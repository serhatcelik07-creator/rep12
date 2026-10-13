<?php
declare(strict_types=1);

/**
 * Bot hayatı: her bot ~15 dakikada bir başka bir botla düello yapar (lig puanı, galibiyet/mağlubiyet,
 * seri ve XP gerçek maç kuralıyla değişir) ve botlar dünya sohbetinde kendi dillerinde konuşur.
 *
 * Bilgisayardaki tools/bot_runner.py dakikada bir POST /api/bots_tick.php çağırır (X-Bot-Key = config 'bot_tick_key').
 * Gerekli sütunlar ilk çağrıda kendiliğinden eklenir (users.bot_next_ms, users.bot_lang).
 */
final class BotLife {
  const MATCH_EVERY_MS = 15 * 60 * 1000;  // her bot için maç aralığı
  const JITTER_MS = 3 * 60 * 1000;        // botlar aynı anda oynamasın: ±3 dk
  const MAX_PAIRS_PER_TICK = 30;
  const CHAT_MIN_GAP_S = 75;              // iki bot mesajı arasında en az
  const CHAT_CHANCE = 55;                 // tik başına sohbet olasılığı (%), boşluk dolduysa

  /** @return array özet: oynanan maçlar, yazılan mesajlar */
  public static function tick(): array {
    self::ensureColumns();
    $db = App::$db; $now = App::nowMs();

    // İlk kez görülen botları önümüzdeki 15 dakikaya yay (hepsi aynı dakikada oynamasın)
    $db->prepare('UPDATE users SET bot_next_ms = ? + FLOOR(RAND() * ?) WHERE is_bot = 1 AND bot_next_ms = 0')->execute([$now, self::MATCH_EVERY_MS]);
    self::assignLanguages();

    // Sırası gelen botları lig puanına göre sırala, komşuları eşleştir (yakın seviye)
    $st = $db->prepare('SELECT * FROM users WHERE is_bot = 1 AND is_banned = 0 AND bot_next_ms <= ? ORDER BY bot_next_ms LIMIT ?');
    $st->bindValue(1, $now, PDO::PARAM_INT); $st->bindValue(2, self::MAX_PAIRS_PER_TICK * 2, PDO::PARAM_INT); $st->execute();
    $due = $st->fetchAll();
    usort($due, fn($a, $b) => (int) $a['league_points'] <=> (int) $b['league_points']);
    $matches = [];
    for ($i = 0; $i + 1 < count($due); $i += 2) $matches[] = self::playMatch($due[$i], $due[$i + 1], $now);
    // Tek kalan bir sonraki tike kalır

    $said = self::chat($matches);
    return ['matches' => array_map(fn($m) => "{$m['winner']} {$m['score']} {$m['loser']}", $matches), 'chat' => $said];
  }

  // ---- Maçlar ---------------------------------------------------------------

  /** 3'te 2 düello: her turu beceri farkına göre olasılıkla biri alır. */
  private static function playMatch(array $a, array $b, int $now): array {
    $skA = max(1, (int) $a['bot_skill']); $skB = max(1, (int) $b['bot_skill']);
    $pA = min(.85, max(.15, .5 + ($skA - $skB) * .08));
    $wa = 0; $wb = 0;
    while ($wa < 2 && $wb < 2) { if (mt_rand(1, 1000) <= $pA * 1000) $wa++; else $wb++; }
    self::apply($a, $wa, $wb, $now);
    self::apply($b, $wb, $wa, $now);
    [$win, $lose] = $wa > $wb ? [$a, $b] : [$b, $a];
    return ['winner' => $win['username'], 'loser' => $lose['username'], 'winner_row' => $win, 'loser_row' => $lose,
            'score' => max($wa, $wb) . '-' . min($wa, $wb)];
  }

  /** Lig kuralı (bot_finish ile aynı): kazanınca seri çarpanı, Bronz'da puan kaybı yok. */
  private static function apply(array $bot, int $mine, int $theirs, int $now): void {
    $won = $mine > $theirs; $delta = $mine - $theirs; $streak = (int) $bot['streak'];
    if ($won) { $streak++; $delta = (int) round(max(1, $delta) * self::mult($streak)); }
    else { $streak = 0; if (League::tier((int) $bot['league_points']) <= 2) $delta = 0; }
    $lp = max(0, (int) $bot['league_points'] + $delta);
    $xp = $won ? 100 + 20 * $mine : 25 + 10 * $mine;
    $next = $now + self::MATCH_EVERY_MS + mt_rand(-self::JITTER_MS, self::JITTER_MS);
    App::$db->prepare('UPDATE users SET league_points = ?, duel_wins = duel_wins + ?, duel_losses = duel_losses + ?, streak = ?, best_streak = GREATEST(best_streak, ?), xp = xp + ?, bot_next_ms = ?, last_seen = NOW() WHERE id = ?')
      ->execute([$lp, $won ? 1 : 0, $won ? 0 : 1, $streak, $streak, $xp, $next, $bot['id']]);
  }

  private static function mult(int $streak): float { return [1 => 1.25, 2 => 1.5, 3 => 2.0, 4 => 2.5][$streak] ?? ($streak <= 0 ? 1.0 : 3.0); }

  // ---- Sohbet ---------------------------------------------------------------

  /** Botlar ara sıra dünya sohbetine yazar: maç sonrası övünme/yakınma, selam, meydan okuma, matematik sohbeti. */
  private static function chat(array $matches): array {
    $db = App::$db;
    $last = (int) $db->query('SELECT COALESCE(MAX(UNIX_TIMESTAMP(c.created_at)), 0) FROM chat_messages c JOIN users u ON u.id = c.user_id WHERE u.is_bot = 1')->fetchColumn();
    if (time() - $last < self::CHAT_MIN_GAP_S || mt_rand(1, 100) > self::CHAT_CHANCE) return [];

    // Yakında bir insan selam verdiyse bir bot onun dilinde karşılık verir
    $st = $db->query('SELECT c.text, c.username FROM chat_messages c JOIN users u ON u.id = c.user_id WHERE u.is_bot = 0 AND c.created_at > DATE_SUB(NOW(), INTERVAL 3 MINUTE) ORDER BY c.id DESC LIMIT 5');
    foreach ($st->fetchAll() as $m) {
      $lang = BotPhrases::greetingLang((string) $m['text']);
      if ($lang === null) continue;
      $bot = self::randomBot($lang) ?? self::randomBot(null);
      if ($bot && !self::alreadyGreeted((string) $m['username'])) return [self::say($bot, BotPhrases::pick($lang, 'reply', ['name' => $m['username']]))];
    }

    if ($matches && mt_rand(1, 100) <= 60) {
      $m = $matches[array_rand($matches)];
      if (mt_rand(0, 1)) { $bot = $m['winner_row']; $kind = 'won'; $other = $m['loser']; }
      else { $bot = $m['loser_row']; $kind = 'lost'; $other = $m['winner']; }
      $lang = $bot['bot_lang'] ?: 'en';
      return [self::say($bot, BotPhrases::pick($lang, $kind, ['opp' => $other, 'score' => $m['score']]))];
    }
    $bot = self::randomBot(null);
    if (!$bot) return [];
    $kind = ['hello', 'challenge', 'math', 'math'][mt_rand(0, 3)];
    return [self::say($bot, BotPhrases::pick($bot['bot_lang'] ?: 'en', $kind, []))];
  }

  private static function alreadyGreeted(string $username): bool {
    $st = App::$db->prepare('SELECT COUNT(*) FROM chat_messages c JOIN users u ON u.id = c.user_id WHERE u.is_bot = 1 AND c.text LIKE ? AND c.created_at > DATE_SUB(NOW(), INTERVAL 10 MINUTE)');
    $st->execute(['%' . $username . '%']);
    return (int) $st->fetchColumn() > 0;
  }

  private static function randomBot(?string $lang): ?array {
    $sql = 'SELECT * FROM users WHERE is_bot = 1 AND is_banned = 0' . ($lang ? ' AND bot_lang = ?' : '') . ' ORDER BY RAND() LIMIT 1';
    $st = App::$db->prepare($sql); $st->execute($lang ? [$lang] : []);
    return $st->fetch() ?: null;
  }

  private static function say(array $bot, string $text): string {
    $text = mb_substr($text, 0, 200);
    App::$db->prepare('INSERT INTO chat_messages (user_id, username, text) VALUES (?, ?, ?)')->execute([$bot['id'], $bot['username'], $text]);
    App::$db->prepare('UPDATE users SET last_seen = NOW() WHERE id = ?')->execute([$bot['id']]);
    return "{$bot['username']}: $text";
  }

  // ---- Kurulum --------------------------------------------------------------

  private static function ensureColumns(): void {
    $cols = array_column(App::$db->query('SHOW COLUMNS FROM users')->fetchAll(PDO::FETCH_ASSOC), 'Field');
    if (!in_array('bot_next_ms', $cols, true)) App::$db->exec('ALTER TABLE users ADD COLUMN bot_next_ms BIGINT UNSIGNED NOT NULL DEFAULT 0');
    if (!in_array('bot_lang', $cols, true)) App::$db->exec("ALTER TABLE users ADD COLUMN bot_lang VARCHAR(5) NOT NULL DEFAULT ''");
  }

  /** Dili henüz atanmamış botlara isimden dil verir (Türkçe isim → tr, İspanyolca → es …), kalanlar çoğunlukla İngilizce. */
  private static function assignLanguages(): void {
    $rows = App::$db->query("SELECT id, username FROM users WHERE is_bot = 1 AND bot_lang = ''")->fetchAll();
    $up = App::$db->prepare('UPDATE users SET bot_lang = ? WHERE id = ?');
    foreach ($rows as $r) $up->execute([BotPhrases::langForName((string) $r['username'], (int) $r['id']), $r['id']]);
  }
}

/** Bot cümleleri. {opp}, {score}, {name} yer tutucuları. Küfür/kişisel bilgi yok; kısa ve oyun içi. */
final class BotPhrases {
  const P = [
    'tr' => [
      'hello' => ['Selam millet 👋', 'Herkese iyi oyunlar!', 'Kim burada? 😄', 'Günaydın savaşçılar ☀️', 'Merhaba, düello var mı?'],
      'challenge' => ['Gold lige çıkmama az kaldı, kim durdurur beni? 💪', 'Bugün seri yapacağım, söz!', 'Çarpmada beni yenen olursa tebrik ederim 😎', 'Turnuvaya giriyorum, görüşürüz arenada!'],
      'math' => ['Kesirler hâlâ en sevmediğim 😅', 'Bölme sorularında hızlanmak lazım', '7×8=56, unutmayın 😂', 'Kafadan toplama çalışıyorum bu ara', 'Geometri soruları çok iyi olmuş'],
      'won' => ['{opp} ile güzel maçtı, {score} aldım 🔥', 'Yine kazandım! {score} 😎', 'GG {opp}, iyi mücadeleydi', 'Seri devam ediyor 💪'],
      'lost' => ['{opp} çok hızlıydı, {score} kaybettim 😤', 'Bu sefer olmadı, rövanş istiyorum {opp}!', 'Son soruda kafam yandı 😅', 'GG {opp}, tebrikler'],
      'reply' => ['Selam {name}! 👋', 'Hoş geldin {name} 😄', 'Selam {name}, iyi oyunlar!', 'Aleyküm selam {name} 🙂'],
    ],
    'en' => [
      'hello' => ['Hey everyone 👋', 'Good luck all!', 'Who is online? 😄', 'Morning warriors ☀️', 'Anyone up for a duel?'],
      'challenge' => ['Almost Gold league, who can stop me? 💪', 'Going for a win streak today!', 'Beat me at multiplication if you can 😎', 'Heading into the tournament, see you in the arena!'],
      'math' => ['Fractions are still my weak spot 😅', 'Need to get faster at division', 'Pro tip: 7×8=56 😂', 'Practicing mental math every day', 'The geometry questions are fun'],
      'won' => ['GG {opp}, took it {score} 🔥', 'Another win! {score} 😎', 'Nice match {opp}, close one', 'Streak keeps going 💪'],
      'lost' => ['{opp} was too fast, lost {score} 😤', 'Rematch {opp}?', 'Brain froze on the last question 😅', 'GG {opp}, well played'],
      'reply' => ['Hi {name}! 👋', 'Welcome {name} 😄', 'Hey {name}, good luck!', 'Hello {name} 🙂'],
    ],
    'es' => [
      'hello' => ['Hola a todos 👋', '¡Suerte a todos!', '¿Quién está conectado? 😄', 'Buenos días guerreros ☀️', '¿Alguien quiere un duelo?'],
      'challenge' => ['Casi llego a Oro, ¿quién me para? 💪', '¡Hoy voy por una racha!', 'Gáname en multiplicación si puedes 😎'],
      'math' => ['Las fracciones me cuestan 😅', 'Tengo que ser más rápido dividiendo', '7×8=56, no lo olviden 😂', 'Las preguntas de geometría están geniales'],
      'won' => ['GG {opp}, gané {score} 🔥', '¡Otra victoria! {score} 😎', 'Buen partido {opp}'],
      'lost' => ['{opp} fue muy rápido, perdí {score} 😤', '¿Revancha {opp}?', 'GG {opp}, bien jugado'],
      'reply' => ['¡Hola {name}! 👋', 'Bienvenido {name} 😄', '¡Suerte {name}!'],
    ],
    'pt' => [
      'hello' => ['Olá pessoal 👋', 'Boa sorte a todos!', 'Alguém pra um duelo?'],
      'challenge' => ['Quase no Ouro, quem me segura? 💪', 'Hoje vou fazer sequência!'],
      'math' => ['Frações ainda são difíceis pra mim 😅', 'Treinando cálculo mental todo dia'],
      'won' => ['GG {opp}, ganhei {score} 🔥', 'Mais uma vitória! {score} 😎'],
      'lost' => ['{opp} foi rápido demais, perdi {score} 😤', 'Revanche {opp}?'],
      'reply' => ['Oi {name}! 👋', 'Bem-vindo {name} 😄'],
    ],
    'de' => [
      'hello' => ['Hallo zusammen 👋', 'Viel Glück allen!', 'Wer hat Lust auf ein Duell?'],
      'challenge' => ['Fast Gold-Liga, wer hält mich auf? 💪', 'Heute hole ich eine Siegesserie!'],
      'math' => ['Brüche sind immer noch schwer 😅', 'Kopfrechnen jeden Tag üben'],
      'won' => ['GG {opp}, {score} gewonnen 🔥', 'Noch ein Sieg! {score} 😎'],
      'lost' => ['{opp} war zu schnell, {score} verloren 😤', 'Revanche {opp}?'],
      'reply' => ['Hallo {name}! 👋', 'Willkommen {name} 😄'],
    ],
    'fr' => [
      'hello' => ['Salut tout le monde 👋', 'Bonne chance à tous !', 'Quelqu’un pour un duel ?'],
      'challenge' => ['Presque en ligue Or, qui m’arrête ? 💪', 'Aujourd’hui je vise une série !'],
      'math' => ['Les fractions, toujours difficile 😅', 'Je m’entraîne au calcul mental'],
      'won' => ['GG {opp}, gagné {score} 🔥', 'Encore une victoire ! {score} 😎'],
      'lost' => ['{opp} trop rapide, perdu {score} 😤', 'Revanche {opp} ?'],
      'reply' => ['Salut {name} ! 👋', 'Bienvenue {name} 😄'],
    ],
    'ru' => [
      'hello' => ['Всем привет 👋', 'Удачи всем!', 'Кто на дуэль?'],
      'challenge' => ['Почти Золото, кто меня остановит? 💪', 'Сегодня иду на серию побед!'],
      'math' => ['Дроби всё ещё сложные 😅', 'Тренирую устный счёт каждый день'],
      'won' => ['GG {opp}, выиграл {score} 🔥', 'Ещё одна победа! {score} 😎'],
      'lost' => ['{opp} был слишком быстрым, проиграл {score} 😤', 'Реванш, {opp}?'],
      'reply' => ['Привет, {name}! 👋', 'Добро пожаловать, {name} 😄'],
    ],
    'ja' => [
      'hello' => ['みなさんこんにちは 👋', 'みんながんばろう！', 'だれか対戦しよう！'],
      'challenge' => ['もうすぐゴールドリーグ！💪', '今日は連勝するぞ！'],
      'math' => ['分数はまだ苦手 😅', '毎日暗算の練習中'],
      'won' => ['GG {opp}、{score}で勝った 🔥', 'また勝った！{score} 😎'],
      'lost' => ['{opp}速すぎ、{score}で負けた 😤', 'リベンジしたい {opp}！'],
      'reply' => ['こんにちは {name}！👋', 'ようこそ {name} 😄'],
    ],
    'ar' => [
      'hello' => ['مرحبا بالجميع 👋', 'بالتوفيق للجميع!', 'من يريد مبارزة؟'],
      'challenge' => ['اقتربت من الدوري الذهبي 💪', 'اليوم سأحقق سلسلة انتصارات!'],
      'math' => ['الكسور ما زالت صعبة 😅', 'أتدرب على الحساب الذهني كل يوم'],
      'won' => ['GG {opp}، فزت {score} 🔥', 'فوز آخر! {score} 😎'],
      'lost' => ['{opp} كان سريعا جدا، خسرت {score} 😤', 'مباراة ثأر يا {opp}؟'],
      'reply' => ['أهلا {name}! 👋', 'مرحبا بك {name} 😄'],
    ],
    'it' => [
      'hello' => ['Ciao a tutti 👋', 'In bocca al lupo a tutti!', 'Qualcuno per un duello?'],
      'challenge' => ['Quasi in lega Oro, chi mi ferma? 💪', 'Oggi punto a una serie di vittorie!'],
      'math' => ['Le frazioni sono ancora difficili 😅', 'Mi alleno con il calcolo mentale'],
      'won' => ['GG {opp}, vinto {score} 🔥', 'Un’altra vittoria! {score} 😎'],
      'lost' => ['{opp} troppo veloce, perso {score} 😤', 'Rivincita {opp}?'],
      'reply' => ['Ciao {name}! 👋', 'Benvenuto {name} 😄'],
    ],
  ];

  public static function pick(string $lang, string $kind, array $vars): string {
    $list = self::P[$lang][$kind] ?? self::P['en'][$kind];
    $s = $list[array_rand($list)];
    foreach ($vars as $k => $v) $s = str_replace('{' . $k . '}', (string) $v, $s);
    return $s;
  }

  /** İnsan mesajı bir selamsa hangi dilde olduğu; değilse null. */
  public static function greetingLang(string $text): ?string {
    $t = mb_strtolower($text, 'UTF-8');
    $map = ['tr' => '/(*UCP)\b(selam|merhaba|slm|mrb|günaydın|iyi akşamlar)\b/u', 'es' => '/(*UCP)\b(hola|buenas)\b/u', 'pt' => '/(*UCP)\b(olá|oi)\b/u',
            'de' => '/(*UCP)\b(hallo|servus|moin)\b/u', 'fr' => '/(*UCP)\b(salut|bonjour)\b/u', 'it' => '/(*UCP)\b(ciao)\b/u', 'ru' => '/(привет|здравствуй)/u',
            'ja' => '/(こんにちは|おはよう)/u', 'ar' => '/(مرحبا|السلام)/u', 'en' => '/(*UCP)\b(hi|hello|hey|yo)\b/u'];
    foreach ($map as $lang => $re) if (preg_match($re, $t)) return $lang;
    return null;
  }

  /** Bot isminden dil tahmini; ipucu yoksa çoğunlukla İngilizce, bir kısmı Türkçe (oyuncuların çoğu TR). */
  public static function langForName(string $name, int $id): string {
    $n = mb_strtolower($name, 'UTF-8');
    if (preg_match('/[çğıöşüİ]/u', $name) || preg_match('/(?<!\p{L})(ali|cem|onur|ece|umut|kerem|bora|burak|zeynep|emre|mert|elif|deniz|can|efe|bozkurt|demir|yağız|arda|selin|ayşe|mehmet|ahmet|kaan|berk|tuna|ozan)(?!\p{L})/u', $n)) return 'tr';
    if (preg_match('/(?<!\p{L})(juan|pedro|pablo|mateo|rico|carlos|diego|lucia|sofia|valentina|javier|alejandro|miguel)(?!\p{L})/u', $n)) return 'es';
    if (preg_match('/(?<!\p{L})(joão|thiago|gabriel|rafael|ana clara|bruno)(?!\p{L})/u', $n)) return 'pt';
    if (preg_match('/(?<!\p{L})(hans|lukas|jonas|lena|felix|klaus|greta)(?!\p{L})/u', $n)) return 'de';
    if (preg_match('/(?<!\p{L})(pierre|louis|chloé|camille|hugo|léa)(?!\p{L})/u', $n)) return 'fr';
    if (preg_match('/(?<!\p{L})(olga|ivan|dmitri|natasha|sasha|boris|vlad)(?!\p{L})/u', $n)) return 'ru';
    if (preg_match('/(?<!\p{L})(kira|yamato|aiko|haruto|sakura|kenji|yuki|hiro)(?!\p{L})/u', $n)) return 'ja';
    if (preg_match('/(?<!\p{L})(omar|ahmed|yusuf|layla|fatima|khalid|hassan)(?!\p{L})/u', $n)) return 'ar';
    if (preg_match('/(?<!\p{L})(marco|giulia|luca|matteo|francesca)(?!\p{L})/u', $n)) return 'it';
    return ['en', 'en', 'en', 'tr', 'tr', 'es'][$id % 6];
  }
}
