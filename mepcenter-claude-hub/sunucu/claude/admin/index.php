<?php
// MepCenter Claude Hub - yönetim paneli (yalnızca site sahibi)

declare(strict_types=1);
require dirname(__DIR__) . '/lib/hub.php';

session_name('claudehub');
session_set_cookie_params([
    'httponly' => true,
    'samesite' => 'Strict',
    'secure' => !empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off',
    'path' => dirname($_SERVER['SCRIPT_NAME']) . '/',
]);
session_start();
header('X-Frame-Options: DENY');
header('X-Content-Type-Options: nosniff');

if (!is_file(HUB_ROOT . '/config.php')) {
    header('Location: ../install.php');
    exit;
}

function csrf(): string
{
    if (empty($_SESSION['csrf'])) {
        $_SESSION['csrf'] = bin2hex(random_bytes(16));
    }
    return '<input type="hidden" name="csrf" value="' . $_SESSION['csrf'] . '">';
}

function check_csrf(): void
{
    if (!hash_equals($_SESSION['csrf'] ?? '', (string)($_POST['csrf'] ?? ''))) {
        http_response_code(400);
        exit('Geçersiz form (CSRF). Sayfayı yenileyip tekrar deneyin.');
    }
}

function redirect(string $qs): void
{
    header('Location: ?' . $qs);
    exit;
}

function flash(?string $set = null): ?string
{
    if ($set !== null) {
        $_SESSION['flash'] = $set;
        return null;
    }
    $f = $_SESSION['flash'] ?? null;
    unset($_SESSION['flash']);
    return $f;
}

function fmt_size(int $b): string
{
    return $b >= 1048576 ? round($b / 1048576, 1) . ' MB' : ($b >= 1024 ? round($b / 1024, 1) . ' KB' : $b . ' B');
}

$p = (string)($_GET['p'] ?? 'dash');

// ---- Giriş / çıkış ---------------------------------------------------------
if ($p === 'logout') {
    session_destroy();
    redirect('');
}

if (empty($_SESSION['admin'])) {
    $err = '';
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        try {
            if (check_admin_login((string)($_POST['user'] ?? ''), (string)($_POST['pass'] ?? ''))) {
                session_regenerate_id(true);
                $_SESSION['admin'] = true;
                redirect('');
            }
            $err = 'Kullanıcı adı veya şifre hatalı.';
        } catch (HubFail $e) {
            $err = $e->getMessage();
        }
    }
    ?><!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Claude Hub</title><link rel="stylesheet" href="style.css"></head><body><main class="narrow">
    <h1>Claude Hub</h1>
    <?php if ($err): ?><p class="err"><?= h($err) ?></p><?php endif; ?>
    <form method="post" class="card">
      <label>Kullanıcı adı <input name="user" autocomplete="username" required autofocus></label>
      <label>Şifre <input name="pass" type="password" autocomplete="current-password" required></label>
      <button>Giriş</button>
    </form>
    <p class="meta">Kullanıcı adı: <b>claude</b>. Şifrenizi unuttuysanız: cPanel Dosya Yöneticisi'nde
      <b>public_html/claude/data/install.lock</b> dosyasını silin, sonra <a href="../install.php">bu sayfadan</a> yeni şifre belirleyin
      (kayıtlar silinmez, giriş kilidi de kalkar).</p>
    </main></body></html><?php
    exit;
}

// ---- İşlemler (POST) -------------------------------------------------------
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    check_csrf();
    $a = (string)($_POST['a'] ?? '');
    switch ($a) {
        case 'agent_create':
            $name = trim((string)$_POST['name']);
            $type = preg_replace('/[^a-z0-9_-]/', '', strtolower((string)($_POST['type'] ?? 'claude'))) ?: 'claude';
            if ($name === '') {
                flash('Ajan adı gerekli.');
                redirect('p=agents');
            }
            $tok = new_token();
            try {
                q('INSERT INTO hub_agents (name, type, token_hash, token_hint, note) VALUES (?, ?, ?, ?, ?)',
                  [str_cut($name, 100), $type, token_hash($tok), substr($tok, -6), str_cut(trim((string)($_POST['note'] ?? '')), 250)]);
                $_SESSION['new_token'] = [$name, $tok];
            } catch (PDOException $e) {
                flash('Bu isimde bir ajan zaten var.');
            }
            redirect('p=agents');
        case 'web_link': // claude.ai / Cowork bağlayıcısı için hazır adres
            $tok = new_token();
            $id = q("SELECT id FROM hub_agents WHERE name = 'claude-web'")->fetchColumn();
            if ($id) {
                q('UPDATE hub_agents SET token_hash = ?, token_hint = ?, active = 1 WHERE id = ?', [token_hash($tok), substr($tok, -6), $id]);
            } else {
                q("INSERT INTO hub_agents (name, type, token_hash, token_hint, note) VALUES ('claude-web', 'claude', ?, ?, 'claude.ai / Cowork bağlayıcısı')",
                  [token_hash($tok), substr($tok, -6)]);
            }
            $base = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off' ? 'https' : 'http') . '://' . ($_SERVER['HTTP_HOST'] ?? '')
                  . rtrim(dirname(dirname($_SERVER['SCRIPT_NAME'])), '/') . '/';
            $_SESSION['web_link'] = $base . 'mcp/?k=' . $tok;
            redirect('p=agents');
        case 'agent_toggle':
            q('UPDATE hub_agents SET active = 1 - active WHERE id = ?', [(int)$_POST['id']]);
            redirect('p=agents');
        case 'agent_rotate':
            $tok = new_token();
            $name = q('SELECT name FROM hub_agents WHERE id = ?', [(int)$_POST['id']])->fetchColumn();
            q('UPDATE hub_agents SET token_hash = ?, token_hint = ? WHERE id = ?', [token_hash($tok), substr($tok, -6), (int)$_POST['id']]);
            $_SESSION['new_token'] = [$name, $tok];
            redirect('p=agents');
        case 'agent_delete':
            q('DELETE FROM hub_agents WHERE id = ?', [(int)$_POST['id']]);
            flash('Ajan ve oturumları silindi.');
            redirect('p=agents');
        case 'send':
            $to = trim((string)($_POST['to'] ?? 'all'));
            [$type, $val] = array_pad(explode(':', $to, 2), 2, '');
            if (!in_array($type, ['all', 'agent', 'session', 'machine', 'project'], true)) {
                $type = 'all';
            }
            if (trim((string)$_POST['body']) !== '') {
                q('INSERT INTO hub_messages (from_session_id, from_label, to_type, to_value, topic, body) VALUES (NULL, ?, ?, ?, ?, ?)',
                  ['Yönetici (panel)', $type, $type === 'all' ? '' : $val, str_cut((string)($_POST['topic'] ?? ''), 190), trim((string)$_POST['body'])]);
                flash('Mesaj gönderildi.');
            }
            redirect('p=messages');
        case 'msg_delete':
            q('DELETE FROM hub_messages WHERE id = ?', [(int)$_POST['id']]);
            redirect('p=messages');
        case 'topic_delete':
            q('DELETE FROM hub_topics WHERE id = ?', [(int)$_POST['id']]);
            redirect('p=topics');
        case 'file_delete':
            $f = q('SELECT stored_name FROM hub_files WHERE id = ?', [(int)$_POST['id']])->fetch();
            if ($f) {
                @unlink(hub_config()['upload_dir'] . '/' . $f['stored_name']);
                q('DELETE FROM hub_files WHERE id = ?', [(int)$_POST['id']]);
            }
            redirect('p=files');
        case 'session_end':
            q('UPDATE hub_sessions SET ended_at = NOW() WHERE id = ?', [(int)$_POST['id']]);
            redirect('');
        case 'kv_set':
            q('INSERT INTO hub_kv (ns, k, v, updated_by) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE v = VALUES(v), updated_by = VALUES(updated_by)',
              [trim((string)$_POST['ns']) ?: 'default', trim((string)$_POST['key']), (string)$_POST['value'], 'Yönetici (panel)']);
            redirect('p=kv&ns=' . urlencode(trim((string)$_POST['ns']) ?: 'default'));
        case 'kv_del':
            q('DELETE FROM hub_kv WHERE ns = ? AND k = ?', [(string)$_POST['ns'], (string)$_POST['key']]);
            redirect('p=kv&ns=' . urlencode((string)$_POST['ns']));
        case 'chat_send': // Panelden bir oturuma / herkese mesaj
            $sid = (string)($_POST['s'] ?? 'all');
            $body = trim((string)($_POST['body'] ?? ''));
            if ($body !== '') {
                q('INSERT INTO hub_messages (from_session_id, from_label, to_type, to_value, topic, body) VALUES (NULL, ?, ?, ?, ?, ?)',
                  ['Yönetici (panel)', $sid === 'all' ? 'all' : 'session', $sid === 'all' ? '' : (string)(int)$sid, 'panel sohbet', $body]);
            }
            if (!empty($_POST['ajax'])) {
                header('Content-Type: application/json');
                exit('{"ok":true}');
            }
            redirect('p=chat&s=' . urlencode($sid));
        case 'project_save':
            $code = trim((string)$_POST['code']);
            if (valid_project_code($code)) {
                q('INSERT IGNORE INTO hub_projects (code) VALUES (?)', [$code]);
                q('UPDATE hub_projects SET name = ?, note = ? WHERE code = ?', [str_cut(trim((string)$_POST['name']), 190), (string)$_POST['note'], $code]);
                $sum = trim((string)($_POST['summary'] ?? ''));
                $old = (string)q('SELECT summary FROM hub_projects WHERE code = ?', [$code])->fetchColumn();
                if ($sum !== trim($old)) {
                    q('UPDATE hub_projects SET summary = ?, summary_by = ?, summary_at = NOW() WHERE code = ?', [$sum, 'Yönetici (panel)', $code]);
                    q('INSERT INTO hub_topics (session_id, project_code, kind, title, content) VALUES (NULL, ?, ?, ?, ?)',
                      [$code, 'status', 'Son durum güncellendi (panel)', $sum]);
                }
                flash('Görev kaydedildi.');
            } else {
                flash('Geçersiz görev kodu.');
            }
            redirect('p=projects&code=' . urlencode($code));
        case 'project_delete':
            q('DELETE FROM hub_projects WHERE code = ?', [(string)$_POST['code']]);
            flash('Görev kaydı silindi (konuşma kayıtları ve dosyalar duruyor).');
            redirect('p=projects');
        case 'instructions_save':
            setting_set('agent_instructions', (string)$_POST['text']);
            flash(trim((string)$_POST['text']) === '' ? 'Varsayılan talimata dönüldü.' : 'Talimat kaydedildi. Claude\'lar yeni bağlantıda bunu alır.');
            redirect('p=settings');
        case 'password':
            if (!password_verify((string)$_POST['old'], (string)setting_get('admin_pass_hash', ''))) {
                flash('Mevcut şifre hatalı.');
            } elseif (strlen((string)$_POST['new']) < 10) {
                flash('Yeni şifre en az 10 karakter olmalı.');
            } else {
                setting_set('admin_pass_hash', password_hash((string)$_POST['new'], PASSWORD_DEFAULT));
                flash('Şifre değiştirildi.');
            }
            redirect('p=settings');
    }
    redirect('');
}

// ---- Sohbet akışı (JSON, panel tarafından yoklanır) -------------------------
function chat_thread(string $sid, int $after = 0): array
{
    if ($sid === 'all') {
        return q("SELECT m.id, m.from_label, m.from_session_id, m.to_type, m.to_value, m.body, m.created_at FROM hub_messages m
                   WHERE m.id > ? AND ((m.from_session_id IS NULL AND m.to_type = 'all') OR m.to_type = 'admin')
                   ORDER BY m.id DESC LIMIT 200", [$after])->fetchAll();
    }
    return q("SELECT m.id, m.from_label, m.from_session_id, m.to_type, m.to_value, m.body, m.created_at FROM hub_messages m
               WHERE m.id > ? AND ((m.from_session_id IS NULL AND m.to_type = 'session' AND m.to_value = ?)
                     OR (m.from_session_id = ? AND m.to_type = 'admin'))
               ORDER BY m.id DESC LIMIT 200", [$after, $sid, (int)$sid])->fetchAll();
}

if ($p === 'chat_json') {
    header('Content-Type: application/json; charset=utf-8');
    $rows = array_reverse(chat_thread((string)($_GET['s'] ?? 'all'), (int)($_GET['after'] ?? 0)));
    echo json_encode(['messages' => $rows, 'sessions' => active_sessions()], JSON_UNESCAPED_UNICODE | JSON_INVALID_UTF8_SUBSTITUTE);
    exit;
}

// ---- Dosya indirme ---------------------------------------------------------
if ($p === 'download') {
    $f = q('SELECT * FROM hub_files WHERE id = ?', [(int)($_GET['id'] ?? 0)])->fetch();
    $path = $f ? hub_config()['upload_dir'] . '/' . $f['stored_name'] : '';
    if (!$f || !is_file($path)) {
        http_response_code(404);
        exit('Bulunamadı');
    }
    header('Content-Type: application/octet-stream');
    header('Content-Length: ' . filesize($path));
    header("Content-Disposition: attachment; filename*=UTF-8''" . rawurlencode($f['orig_name']));
    readfile($path);
    exit;
}

// ---- Sayfalar --------------------------------------------------------------
$nav = ['dash' => 'Oturumlar', 'chat' => 'Sohbet', 'projects' => 'Görevler', 'messages' => 'Tüm mesajlar',
        'topics' => 'Kayıtlar', 'files' => 'Dosyalar',
        'kv' => 'Ortak veri', 'agents' => 'Bilgisayarlar', 'settings' => 'Ayarlar'];
$flash = flash();
?><!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Claude Hub</title><link rel="stylesheet" href="style.css">
<?php if ($p === 'dash' || $p === 'messages'): ?><meta http-equiv="refresh" content="30"><?php endif; ?>
</head><body>
<header><b>Claude Hub</b>
<nav><?php foreach ($nav as $k => $v): ?><a href="?p=<?= $k ?>" class="<?= $p === $k ? 'on' : '' ?>"><?= h($v) ?></a><?php endforeach; ?>
<a href="?p=logout">Çıkış</a></nav></header>
<main>
<?php if ($flash): ?><p class="ok"><?= h($flash) ?></p><?php endif; ?>

<?php if ($p === 'dash'):
    $active = active_sessions();
    $recent = q("SELECT s.*, a.name AS agent FROM hub_sessions s JOIN hub_agents a ON a.id = s.agent_id
                 ORDER BY s.last_seen_at DESC LIMIT 30")->fetchAll();
    $activeIds = array_column($active, 'id');
    $stats = q("SELECT (SELECT COUNT(*) FROM hub_messages) m, (SELECT COUNT(*) FROM hub_topics) t,
                       (SELECT COUNT(*) FROM hub_files) f, (SELECT COUNT(*) FROM hub_agents WHERE active=1) a")->fetch(); ?>
  <div class="stats">
    <div><b><?= count($active) ?></b>aktif oturum</div><div><b><?= $stats['a'] ?></b>ajan</div>
    <div><b><?= $stats['m'] ?></b>mesaj</div><div><b><?= $stats['t'] ?></b>konuşma kaydı</div><div><b><?= $stats['f'] ?></b>dosya</div>
  </div>
  <h2>Oturumlar</h2>
  <div class="scroll"><table>
    <tr><th>#</th><th>Durum</th><th>Ajan</th><th>Makine</th><th>Klasör</th><th>Görev</th><th>Ne yapıyor</th><th>Son görülme</th><th></th></tr>
    <?php foreach ($recent as $s): $on = in_array($s['id'], $activeIds); ?>
    <tr class="<?= $on ? '' : 'dim' ?>">
      <td><?= $s['id'] ?></td><td><span class="dot <?= $on ? 'on' : '' ?>"></span><?= $on ? 'aktif' : ($s['ended_at'] ? 'kapandı' : 'sessiz') ?></td>
      <td><?= h($s['agent']) ?></td><td><?= h($s['machine']) ?></td>
      <td title="<?= h($s['cwd']) ?>"><?= h($s['project']) ?></td>
      <td><?php if ($s['project_code']): ?><a href="?p=projects&code=<?= urlencode($s['project_code']) ?>"><?= h($s['project_code']) ?></a><?php endif; ?></td>
      <td><?= nl2br(h(str_cut((string)$s['status_text'], 300))) ?></td>
      <td><?= h($s['last_seen_at']) ?></td>
      <td><a href="?p=chat&s=<?= $s['id'] ?>">sohbet</a> · <a href="?p=topics&session=<?= $s['id'] ?>">kayıtlar</a>
        <?php if ($on): ?><form method="post" class="inline"><?= csrf() ?><input type="hidden" name="a" value="session_end"><input type="hidden" name="id" value="<?= $s['id'] ?>"><button class="link">kapat</button></form><?php endif; ?></td>
    </tr>
    <?php endforeach; ?>
  </table></div>

<?php elseif ($p === 'chat'):
    $sel = (string)($_GET['s'] ?? 'all');
    $act = active_sessions(); ?>
  <div class="chat">
    <aside>
      <a class="sess <?= $sel === 'all' ? 'on' : '' ?>" href="?p=chat&s=all"><b>Herkes</b><small>tüm aktif Claude'lara</small></a>
      <div id="sesslist"><?php foreach ($act as $a): ?>
        <a class="sess <?= $sel === (string)$a['id'] ? 'on' : '' ?>" href="?p=chat&s=<?= $a['id'] ?>"><b><span class="dot on"></span>#<?= $a['id'] ?> <?= h($a['agent'] . '@' . $a['machine']) ?></b>
          <small><?= $a['project'] === 'kopru' ? '🔌 köprü ajanı (7/24) — yazdığınız işi bu bilgisayardaki Claude yapar' : h(($a['project_code'] ? $a['project_code'] . ' · ' : '') . $a['project']) ?></small>
          <small><?= h(str_cut((string)$a['status_text'], 90)) ?></small></a>
      <?php endforeach; ?></div>
      <?php if (!$act): ?><p class="meta">Şu an aktif oturum yok.</p><?php endif; ?>
    </aside>
    <section>
      <div id="thread" class="thread"></div>
      <form id="chatform" method="post" class="chatform"><?= csrf() ?><input type="hidden" name="a" value="chat_send"><input type="hidden" name="s" value="<?= h($sel) ?>">
        <textarea name="body" id="chatbody" rows="2" placeholder="Mesaj yaz… (Enter gönderir, Shift+Enter yeni satır)" required></textarea><button>Gönder</button></form>
      <p class="meta">Claude mesajı bir sonraki adımında (ya da "dinleme modu"ndaysa birkaç saniye içinde) görür ve cevabını buraya yazar.</p>
    </section>
  </div>
  <script>
  (function(){
    const sel = <?= json_encode($sel) ?>; let last = 0; const th = document.getElementById('thread');
    function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
    function add(m){
      const mine = m.from_session_id === null;
      const el = document.createElement('div'); el.className = 'bubble ' + (mine ? 'me' : 'them');
      el.innerHTML = '<div class="meta">' + esc(mine ? 'Sen' + (m.to_type==='all' ? ' → herkes' : '') : m.from_label) + ' · ' + esc(m.created_at.substr(11,5)) + '</div>' + esc(m.body).replace(/\n/g,'<br>');
      th.appendChild(el); last = Math.max(last, m.id);
    }
    async function poll(){
      try{
        const r = await fetch('?p=chat_json&s=' + encodeURIComponent(sel) + '&after=' + last, {credentials:'same-origin'});
        const j = await r.json(); const atBottom = th.scrollHeight - th.scrollTop - th.clientHeight < 60;
        j.messages.forEach(add); if (j.messages.length && atBottom) th.scrollTop = th.scrollHeight;
      }catch(e){}
    }
    const f = document.getElementById('chatform'), b = document.getElementById('chatbody');
    f.addEventListener('submit', async e => { e.preventDefault(); if(!b.value.trim()) return;
      const fd = new FormData(f); fd.append('ajax','1'); b.value=''; await fetch('', {method:'POST', body:fd, credentials:'same-origin'}); poll(); });
    b.addEventListener('keydown', e => { if (e.key==='Enter' && !e.shiftKey){ e.preventDefault(); f.requestSubmit(); } });
    poll().then(()=>{ th.scrollTop = th.scrollHeight; }); setInterval(poll, 4000);
  })();
  </script>

<?php elseif ($p === 'projects'):
    $code = trim((string)($_GET['code'] ?? ''));
    if ($code !== ''):
        $pr = q('SELECT * FROM hub_projects WHERE code = ?', [$code])->fetch() ?: ['code' => $code, 'name' => '', 'summary' => '', 'note' => '', 'summary_by' => '', 'summary_at' => ''];
        $cnt = q("SELECT kind, COUNT(*) c FROM hub_topics WHERE project_code = ? GROUP BY kind", [$code])->fetchAll(PDO::FETCH_KEY_PAIR); ?>
    <p><a href="?p=projects">← Görevler</a></p>
    <h2>Görev: <?= h($code) ?> <?= $pr['name'] ? '— ' . h($pr['name']) : '' ?></h2>
    <p class="meta"><?php foreach ($cnt as $k => $c): ?><a class="chip" href="?p=topics&code=<?= urlencode($code) ?>&kind=<?= urlencode($k) ?>"><?= h($k) ?>: <?= $c ?></a> <?php endforeach; ?>
      <a class="chip" href="?p=topics&code=<?= urlencode($code) ?>">tüm kayıtlar →</a></p>
    <form method="post" class="card"><?= csrf() ?><input type="hidden" name="a" value="project_save"><input type="hidden" name="code" value="<?= h($code) ?>">
      <label>Görev adı <input name="name" value="<?= h($pr['name']) ?>"></label>
      <label>Son durum (Claude'lar devam ederken önce bunu okur)<?= $pr['summary_at'] ? ' — son güncelleyen: ' . h($pr['summary_by']) . ', ' . h($pr['summary_at']) : '' ?>
        <textarea name="summary" rows="12"><?= h((string)$pr['summary']) ?></textarea></label>
      <label>Kendi notun (yalnızca panelde) <textarea name="note" rows="2"><?= h((string)$pr['note']) ?></textarea></label>
      <button>Kaydet</button></form>
    <h2>Claude'un göreceği tam özet</h2>
    <pre class="content"><?= h(project_brief_md($code, null, 10)) ?></pre>
    <form method="post"><?= csrf() ?><input type="hidden" name="a" value="project_delete"><input type="hidden" name="code" value="<?= h($code) ?>"><button class="link danger" onclick="return confirm('Görev kaydı silinsin mi? (Konuşmalar ve dosyalar silinmez)')">görev kaydını sil</button></form>
  <?php else:
        $rows = q("SELECT p.code, p.name, p.summary_at, p.created_at,
                          (SELECT COUNT(*) FROM hub_topics t WHERE t.project_code = p.code) AS records,
                          (SELECT COUNT(*) FROM hub_files f WHERE f.project_code = p.code) AS files,
                          (SELECT COUNT(*) FROM hub_sessions s WHERE s.project_code = p.code AND s.ended_at IS NULL
                              AND s.last_seen_at >= NOW() - INTERVAL " . (int)hub_config()['session_active_minutes'] . " MINUTE) AS live,
                          (SELECT MAX(t.created_at) FROM hub_topics t WHERE t.project_code = p.code) AS last_activity
                     FROM hub_projects p ORDER BY last_activity DESC, p.created_at DESC")->fetchAll(); ?>
    <h2>Görevler</h2>
    <p class="meta">Herhangi bir Claude'a "<b>kod matwar</b>" ya da "<b>matwar görevine bak</b>" dediğinizde o Claude buradaki görevin son durumunu, kararlarını, konuşmalarını ve dosyalarını okuyup devam eder.</p>
    <form class="search" method="get"><input type="hidden" name="p" value="projects"><input name="code" placeholder="yeni görev kodu, örn. matwar" pattern="[A-Za-z0-9][A-Za-z0-9._/-]{0,59}"><button>Aç / oluştur</button></form>
    <div class="scroll"><table><tr><th>Kod</th><th>Ad</th><th>Aktif oturum</th><th>Kayıt</th><th>Dosya</th><th>Son durum güncellemesi</th><th>Son hareket</th></tr>
    <?php foreach ($rows as $r): ?>
      <tr><td><a href="?p=projects&code=<?= urlencode($r['code']) ?>"><b><?= h($r['code']) ?></b></a></td><td><?= h($r['name']) ?></td>
        <td><?= $r['live'] ? '<span class="dot on"></span>' . $r['live'] : '-' ?></td><td><?= $r['records'] ?></td><td><?= $r['files'] ?></td>
        <td><?= h($r['summary_at'] ?? '-') ?></td><td><?= h($r['last_activity'] ?? '-') ?></td></tr>
    <?php endforeach; ?></table></div>
  <?php endif; ?>

<?php elseif ($p === 'messages'):
    $rows = q('SELECT * FROM hub_messages ORDER BY id DESC LIMIT 200')->fetchAll(); ?>
  <h2>Claude'lara mesaj gönder</h2>
  <form method="post" class="card">
    <?= csrf() ?><input type="hidden" name="a" value="send">
    <label>Kime <input name="to" value="all" placeholder="all | agent:mac-claude | machine:MacBook | project:matwar | session:12"></label>
    <label>Konu <input name="topic"></label>
    <label>Mesaj <textarea name="body" rows="3" required></textarea></label>
    <button>Gönder</button>
  </form>
  <h2>Son mesajlar</h2>
  <?php foreach ($rows as $m): ?>
    <div class="msg"><div class="meta">#<?= $m['id'] ?> · <?= h($m['created_at']) ?> · <b><?= h($m['from_label']) ?></b> → <?= h($m['to_type'] . ($m['to_value'] !== '' ? ':' . $m['to_value'] : '')) ?>
      <?= $m['topic'] !== '' ? ' · <i>' . h($m['topic']) . '</i>' : '' ?>
      <form method="post" class="inline"><?= csrf() ?><input type="hidden" name="a" value="msg_delete"><input type="hidden" name="id" value="<?= $m['id'] ?>"><button class="link danger" onclick="return confirm('Silinsin mi?')">sil</button></form></div>
      <div class="body"><?= nl2br(h($m['body'])) ?></div></div>
  <?php endforeach; ?>

<?php elseif ($p === 'topics'):
    if (!empty($_GET['id'])):
        $t = q('SELECT t.*, s.machine, s.project, a.name AS agent FROM hub_topics t LEFT JOIN hub_sessions s ON s.id = t.session_id LEFT JOIN hub_agents a ON a.id = s.agent_id WHERE t.id = ?', [(int)$_GET['id']])->fetch();
        if ($t): ?>
      <p><a href="?p=topics">← Konuşmalar</a></p>
      <h2><?= h($t['title'] ?: '(başlıksız)') ?></h2>
      <p class="meta"><?= h($t['kind']) ?> · görev: <?= h($t['project_code'] ?? '-') ?> · <?= h($t['agent'] . '@' . $t['machine']) ?> · <?= h($t['project']) ?> · <?= h($t['created_at']) ?></p>
      <pre class="content"><?= h($t['content']) ?></pre>
    <?php endif;
    else:
        $qs = trim((string)($_GET['q'] ?? ''));
        $sid = (int)($_GET['session'] ?? 0);
        $fcode = trim((string)($_GET['code'] ?? ''));
        $where = ['1=1'];
        $prm = [];
        if ($qs !== '') { $where[] = '(t.title LIKE ? OR t.content LIKE ?)'; $prm[] = "%$qs%"; $prm[] = "%$qs%"; }
        if ($sid) { $where[] = 't.session_id = ?'; $prm[] = $sid; }
        if ($fcode !== '') { $where[] = 't.project_code = ?'; $prm[] = $fcode; }
        if (($fkind = trim((string)($_GET['kind'] ?? ''))) !== '') { $where[] = 't.kind = ?'; $prm[] = $fkind; }
        $rows = q('SELECT t.id, t.project_code, t.kind, t.title, LEFT(t.content, 400) AS preview, t.created_at, s.machine, s.project, a.name AS agent
                     FROM hub_topics t LEFT JOIN hub_sessions s ON s.id = t.session_id LEFT JOIN hub_agents a ON a.id = s.agent_id
                    WHERE ' . implode(' AND ', $where) . ' ORDER BY t.id DESC LIMIT 200', $prm)->fetchAll(); ?>
      <form class="search"><input type="hidden" name="p" value="topics"><input name="q" value="<?= h($qs) ?>" placeholder="Kayıtlarda ara…"><input name="code" value="<?= h($fcode) ?>" placeholder="görev kodu" style="max-width:160px"><button>Ara</button></form>
      <?php foreach ($rows as $t): ?>
        <div class="msg"><div class="meta">#<?= $t['id'] ?> · <?= h($t['created_at']) ?> · <?= h($t['kind']) ?><?= $t['project_code'] ? ' · <a href="?p=projects&code=' . urlencode($t['project_code']) . '">' . h($t['project_code']) . '</a>' : '' ?> · <b><?= h($t['agent'] . '@' . $t['machine']) ?></b> · <?= h($t['project']) ?>
          <form method="post" class="inline"><?= csrf() ?><input type="hidden" name="a" value="topic_delete"><input type="hidden" name="id" value="<?= $t['id'] ?>"><button class="link danger" onclick="return confirm('Silinsin mi?')">sil</button></form></div>
          <a href="?p=topics&id=<?= $t['id'] ?>"><b><?= h($t['title'] ?: '(başlıksız)') ?></b></a>
          <div class="body small"><?= nl2br(h(str_cut($t['preview'], 400))) ?></div></div>
      <?php endforeach;
    endif; ?>

<?php elseif ($p === 'files'):
    $rows = q('SELECT f.*, s.machine, s.project, a.name AS agent FROM hub_files f LEFT JOIN hub_sessions s ON s.id = f.session_id LEFT JOIN hub_agents a ON a.id = s.agent_id ORDER BY f.id DESC LIMIT 300')->fetchAll(); ?>
  <h2>Yüklenen dosyalar</h2>
  <div class="scroll"><table><tr><th>#</th><th>Dosya</th><th>Görev · klasör / yol</th><th>Kaynak</th><th>Boyut</th><th>Tarih</th><th></th></tr>
  <?php foreach ($rows as $f): ?>
    <tr><td><?= $f['id'] ?></td><td><a href="?p=download&id=<?= $f['id'] ?>"><?= h($f['orig_name']) ?></a><?= $f['note'] ? '<br><small>' . h($f['note']) . '</small>' : '' ?></td>
      <td><?= h(($f['project_code'] ? $f['project_code'] . ' · ' : '') . $f['project']) ?><br><small><?= h($f['rel_path']) ?></small></td><td><?= h($f['agent'] . '@' . $f['machine']) ?></td>
      <td><?= fmt_size((int)$f['size']) ?></td><td><?= h($f['created_at']) ?></td>
      <td><form method="post" class="inline"><?= csrf() ?><input type="hidden" name="a" value="file_delete"><input type="hidden" name="id" value="<?= $f['id'] ?>"><button class="link danger" onclick="return confirm('Silinsin mi?')">sil</button></form></td></tr>
  <?php endforeach; ?></table></div>

<?php elseif ($p === 'kv'):
    $ns = (string)($_GET['ns'] ?? '');
    $spaces = q('SELECT ns, COUNT(*) c FROM hub_kv GROUP BY ns ORDER BY ns')->fetchAll(); ?>
  <h2>Ortak veri (anahtar / değer)</h2>
  <p class="meta">Claude'lar <code>hub_kv_set</code> / <code>hub_kv_get</code> araçlarıyla buraya ortak veri yazıp okuyabilir.</p>
  <p><?php foreach ($spaces as $s): ?><a class="chip <?= $ns === $s['ns'] ? 'on' : '' ?>" href="?p=kv&ns=<?= urlencode($s['ns']) ?>"><?= h($s['ns']) ?> (<?= $s['c'] ?>)</a> <?php endforeach; ?></p>
  <?php if ($ns !== ''): $items = q('SELECT * FROM hub_kv WHERE ns = ? ORDER BY k', [$ns])->fetchAll(); ?>
    <div class="scroll"><table><tr><th>Anahtar</th><th>Değer</th><th>Son yazan</th><th></th></tr>
    <?php foreach ($items as $it): ?>
      <tr><td><?= h($it['k']) ?></td><td><pre class="small"><?= h(str_cut($it['v'], 2000)) ?></pre></td><td><?= h($it['updated_by']) ?><br><small><?= h($it['updated_at']) ?></small></td>
        <td><form method="post" class="inline"><?= csrf() ?><input type="hidden" name="a" value="kv_del"><input type="hidden" name="ns" value="<?= h($ns) ?>"><input type="hidden" name="key" value="<?= h($it['k']) ?>"><button class="link danger" onclick="return confirm('Silinsin mi?')">sil</button></form></td></tr>
    <?php endforeach; ?></table></div>
  <?php endif; ?>
  <form method="post" class="card"><?= csrf() ?><input type="hidden" name="a" value="kv_set">
    <label>Alan (namespace) <input name="ns" value="<?= h($ns ?: 'default') ?>"></label>
    <label>Anahtar <input name="key" required></label>
    <label>Değer <textarea name="value" rows="3"></textarea></label>
    <button>Kaydet</button></form>

<?php elseif ($p === 'agents'):
    $agents = q('SELECT a.*, (SELECT COUNT(*) FROM hub_sessions s WHERE s.agent_id = a.id) AS sess FROM hub_agents a ORDER BY a.last_seen_at DESC, a.id')->fetchAll();
    $nt = $_SESSION['new_token'] ?? null;
    $wl = $_SESSION['web_link'] ?? null;
    unset($_SESSION['new_token'], $_SESSION['web_link']); ?>
  <h2>Bilgisayar nasıl eklenir?</h2>
  <div class="card">
    <p>O bilgisayarda <b>kur.py</b> programını çalıştırın. Program sizden yalnızca bu panelin kullanıcı adını (<b>claude</b>) ve şifresini ister;
      bilgisayar kendini otomatik olarak aşağıdaki listeye ekler. Burada ayrıca bir şey yapmanız gerekmez.</p>
    <p class="meta">Claude'un kullanımı her zaman sizin Claude aboneliğinizden düşer; bu sistem ek ücret veya API anahtarı kullanmaz.</p>
  </div>

  <h2>Bağlı bilgisayarlar</h2>
  <div class="scroll"><table><tr><th>Ad</th><th>Durum</th><th>Son görülme</th><th>Oturum</th><th></th></tr>
  <?php foreach ($agents as $ag): ?>
    <tr class="<?= $ag['active'] ? '' : 'dim' ?>"><td><b><?= h($ag['name']) ?></b><?= $ag['note'] ? '<br><small>' . h($ag['note']) . '</small>' : '' ?></td>
      <td><?= $ag['active'] ? 'bağlanabilir' : 'engellendi' ?></td>
      <td><?= h($ag['last_seen_at'] ?? '-') ?></td><td><?= $ag['sess'] ?></td>
      <td>
        <form method="post" class="inline"><?= csrf() ?><input type="hidden" name="a" value="agent_toggle"><input type="hidden" name="id" value="<?= $ag['id'] ?>"><button class="link"><?= $ag['active'] ? 'engelle' : 'izin ver' ?></button></form>
        <form method="post" class="inline"><?= csrf() ?><input type="hidden" name="a" value="agent_delete"><input type="hidden" name="id" value="<?= $ag['id'] ?>"><button class="link danger" onclick="return confirm('Bu bilgisayar ve oturum kayıtları silinsin mi? (Konuşma kayıtları kalır)')">sil</button></form>
      </td></tr>
  <?php endforeach; ?>
  <?php if (!$agents): ?><tr><td colspan="5" class="meta">Henüz bilgisayar yok. Bir bilgisayarda kur.py çalıştırın.</td></tr><?php endif; ?>
  </table></div>
  <p class="meta">Bir bilgisayar kaybolur ya da çalınırsa "engelle" deyin; o bilgisayar artık bağlanamaz.</p>

  <h2>claude.ai (web / mobil) ve Cowork</h2>
  <div class="card">
    <?php if ($wl): ?>
      <p><b>Bağlantı adresiniz</b> (yalnızca şimdi gösterilir, kopyalayın):</p>
      <pre class="token"><?= h($wl) ?></pre>
      <p class="meta">claude.ai → Ayarlar → Connectors → <b>Add custom connector</b> → Ad: <i>MepCenter Hub</i>, URL: yukarıdaki adres.
        Bu adresi kimseyle paylaşmayın; yeni adres oluşturursanız eskisi çalışmaz.</p>
    <?php else: ?>
      <p>claude.ai sitesinde, telefonda veya Cowork'te de "kod matwar" diyebilmek için bir kez bağlantı adresi oluşturup claude.ai ayarlarına ekleyin.</p>
    <?php endif; ?>
    <form method="post"><?= csrf() ?><input type="hidden" name="a" value="web_link">
      <button onclick="return <?= $wl ? 'true' : "confirm('Daha önce oluşturduysanız eski adres çalışmayı bırakır. Devam?')" ?>">Bağlantı adresi oluştur</button></form>
  </div>

  <details<?= $nt ? ' open' : '' ?>><summary class="meta">Gelişmiş: elle anahtar oluştur (normalde gerekmez)</summary>
    <?php if ($nt): ?>
      <div class="card warn"><b><?= h($nt[0]) ?></b> için anahtar (yalnızca şimdi gösterilir):<pre class="token"><?= h($nt[1]) ?></pre></div>
    <?php endif; ?>
    <form method="post" class="card"><?= csrf() ?><input type="hidden" name="a" value="agent_create">
      <label>Ad <input name="name" required></label>
      <label>Tür <select name="type"><option value="claude">claude</option><option value="other">diğer ajan</option></select></label>
      <label>Not <input name="note"></label>
      <button>Oluştur</button></form>
  </details>

<?php elseif ($p === 'settings'): ?>
  <h2>Panel şifresini değiştir</h2>
  <form method="post" class="card"><?= csrf() ?><input type="hidden" name="a" value="password">
    <label>Mevcut şifre <input type="password" name="old" required></label>
    <label>Yeni şifre (en az 10 karakter) <input type="password" name="new" minlength="10" required></label>
    <button>Değiştir</button></form>
  <h2>Claude ajanları için talimat</h2>
  <p class="meta">Her Claude hub'a bağlandığında bu talimatı alır (görev kodu söylenince ne yapacağı, neyi kaydedeceği vb.). Boş bırakırsanız varsayılan talimat kullanılır.</p>
  <form method="post" class="card"><?= csrf() ?><input type="hidden" name="a" value="instructions_save">
    <textarea name="text" rows="18"><?= h(agent_instructions()) ?></textarea>
    <button>Talimatı kaydet</button></form>
  <h2>Bilgi</h2>
  <?php $base = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off' ? 'https' : 'http') . '://' . ($_SERVER['HTTP_HOST'] ?? '') . rtrim(dirname(dirname($_SERVER['SCRIPT_NAME'])), '/') . '/'; ?>
  <p class="meta">Sürüm <?= HUB_VERSION ?> · Hub adresi: <code><?= h($base) ?></code> · Claude bağlayıcı (MCP) adresi: <code><?= h($base) ?>mcp/?k=AJAN_TOKENI</code>
  · Yükleme sınırı: <?= (int)hub_config()['max_upload_mb'] ?> MB (PHP post_max_size: <?= h(ini_get('post_max_size')) ?>)</p>
<?php endif; ?>
</main></body></html>
