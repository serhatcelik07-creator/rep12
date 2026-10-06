<?php
// MepCenter Claude Hub - kimlik doğrulama, oturum ve tüm işlemler.
// api/ (yerel istemciler) ve mcp/ (Claude uzak bağlayıcı) aynı işlemleri kullanır.

declare(strict_types=1);
require_once __DIR__ . '/bootstrap.php';

class HubFail extends RuntimeException
{
}

function header_val(string $name): string
{
    $key = 'HTTP_' . strtoupper(str_replace('-', '_', $name));
    if (!empty($_SERVER[$key])) {
        return (string)$_SERVER[$key];
    }
    if ($name === 'Authorization' && !empty($_SERVER['REDIRECT_HTTP_AUTHORIZATION'])) {
        return (string)$_SERVER['REDIRECT_HTTP_AUTHORIZATION'];
    }
    if (function_exists('getallheaders')) {
        foreach (getallheaders() as $k => $v) {
            if (strcasecmp((string)$k, $name) === 0) {
                return (string)$v;
            }
        }
    }
    return '';
}

/** Token: X-Hub-Token, Authorization: Bearer veya (claude.ai bağlayıcısı için) ?k= parametresi */
function authenticate(): array
{
    $tok = header_val('X-Hub-Token');
    if ($tok === '' && stripos($auth = header_val('Authorization'), 'Bearer ') === 0) {
        $tok = trim(substr($auth, 7));
    }
    if ($tok === '') {
        $tok = (string)($_GET['k'] ?? '');
    }
    if ($tok === '') {
        throw new HubFail('Token gerekli', 401);
    }
    $agent = q('SELECT * FROM hub_agents WHERE token_hash = ?', [token_hash($tok)])->fetch();
    if (!$agent || !$agent['active']) {
        usleep(300000);
        throw new HubFail('Geçersiz veya iptal edilmiş token', 401);
    }
    q('UPDATE hub_agents SET last_seen_at = NOW() WHERE id = ?', [$agent['id']]);
    return $agent;
}

/** Panel kullanıcı adı/şifresini doğrular (15 dakikada 5 hatalı denemeden sonra kilitlenir). */
function check_admin_login(string $user, string $pass): bool
{
    q('DELETE FROM hub_login_attempts WHERE attempted_at < NOW() - INTERVAL 1 DAY');
    $fails = (int)q('SELECT COUNT(*) FROM hub_login_attempts WHERE ip = ? AND attempted_at > NOW() - INTERVAL 15 MINUTE',
                    [client_ip()])->fetchColumn();
    if ($fails >= 5) {
        throw new HubFail('Çok fazla hatalı deneme. 15 dakika sonra tekrar deneyin.', 429);
    }
    if (hash_equals((string)setting_get('admin_user', 'claude'), $user)
        && password_verify($pass, (string)setting_get('admin_pass_hash', ''))) {
        q('DELETE FROM hub_login_attempts WHERE ip = ?', [client_ip()]);
        return true;
    }
    q('INSERT INTO hub_login_attempts (ip) VALUES (?)', [client_ip()]);
    usleep(500000);
    return false;
}

/**
 * Bir bilgisayarı panel kullanıcı adı + şifresiyle kaydeder ve ona özel bağlantı anahtarı döndürür.
 * Aynı adla tekrar kaydolursa eski anahtar geçersiz olur (yeniden kurulum).
 */
function register_machine(string $user, string $pass, string $machine, string $type = 'claude'): array
{
    if (!check_admin_login($user, $pass)) {
        throw new HubFail('Kullanıcı adı veya şifre hatalı (panele girdiğiniz bilgiler).', 401);
    }
    $name = strtolower(trim(preg_replace('/[^A-Za-z0-9._-]+/', '-', $machine), '-')) ?: 'bilgisayar';
    $name = str_cut($name, 90);
    $tok = new_token();
    $exists = q('SELECT id FROM hub_agents WHERE name = ?', [$name])->fetchColumn();
    if ($exists) {
        q('UPDATE hub_agents SET token_hash = ?, token_hint = ?, active = 1 WHERE id = ?', [token_hash($tok), substr($tok, -6), $exists]);
    } else {
        q('INSERT INTO hub_agents (name, type, token_hash, token_hint, note) VALUES (?, ?, ?, ?, ?)',
          [$name, $type, token_hash($tok), substr($tok, -6), 'kurulumla otomatik eklendi']);
    }
    return ['agent' => $name, 'token' => $tok];
}

/** Oturumu bul/oluştur. Başlık yoksa (claude.ai web) makine adı "web" olur. */
function touch_session(array $agent, string $defaultMachine = 'bilinmeyen'): array
{
    $machine = str_cut(trim(rawurldecode(header_val('X-Hub-Machine'))) ?: $defaultMachine, 100);
    $project = str_cut(trim(rawurldecode(header_val('X-Hub-Project'))), 190);
    $cwd = str_cut(trim(rawurldecode(header_val('X-Hub-Cwd'))), 500);
    $key = trim(rawurldecode(header_val('X-Hub-Client-Key'))) ?: ($machine . '|' . $cwd);
    $key = substr(hash('sha256', $key), 0, 40);

    $upd = q(
        'UPDATE hub_sessions SET last_seen_at = NOW(), machine = ?, project = ?, cwd = ?,
                started_at = IF(ended_at IS NULL, started_at, NOW()), ended_at = NULL
          WHERE agent_id = ? AND client_key = ?',
        [$machine, $project, $cwd, $agent['id'], $key]
    );
    if ($upd->rowCount() === 0 && !q('SELECT 1 FROM hub_sessions WHERE agent_id = ? AND client_key = ?', [$agent['id'], $key])->fetchColumn()) {
        // INSERT IGNORE: aynı anda gelen iki ilk istek çakışırsa hata vermesin
        q('INSERT IGNORE INTO hub_sessions (agent_id, client_key, machine, project, cwd) VALUES (?, ?, ?, ?, ?)',
          [$agent['id'], $key, $machine, $project, $cwd]);
    }
    return q('SELECT * FROM hub_sessions WHERE agent_id = ? AND client_key = ?', [$agent['id'], $key])->fetch();
}

function session_label(array $agent, array $s): string
{
    return $agent['name'] . '@' . $s['machine'] . ($s['project'] !== '' ? ' [' . $s['project'] . ']' : '');
}

function agent_instructions(): string
{
    $custom = setting_get('agent_instructions');
    return $custom !== null && trim($custom) !== '' ? $custom : (string)file_get_contents(__DIR__ . '/talimat.md');
}

function fetch_inbox(array $session, array $agent, bool $unreadOnly, int $limit, bool $mark): array
{
    [$where, $params] = inbox_where($session, $agent);
    $params[':me'] = $session['id'];
    $rows = q(
        "SELECT m.id, m.from_session_id, m.from_label, m.to_type, m.to_value, m.topic, m.body, m.created_at,
                (r.message_id IS NOT NULL) AS is_read
           FROM hub_messages m
      LEFT JOIN hub_message_reads r ON r.message_id = m.id AND r.session_id = :me
          WHERE $where " . ($unreadOnly ? 'AND r.message_id IS NULL' : '') . "
       ORDER BY m.id DESC LIMIT " . max(1, min($limit, 200)),
        $params
    )->fetchAll();
    if ($mark && $rows) {
        $ins = db()->prepare('INSERT IGNORE INTO hub_message_reads (message_id, session_id) VALUES (?, ?)');
        foreach ($rows as $r) {
            $ins->execute([$r['id'], $session['id']]);
        }
    }
    foreach ($rows as &$r) {
        $r['is_read'] = (bool)$r['is_read'];
    }
    return array_reverse($rows);
}

/** Bir görev hakkında her şeyi tek bir Markdown metni olarak toplar. */
function project_brief_md(string $code, ?int $mySessionId = null, int $convLimit = 15): string
{
    $p = q('SELECT * FROM hub_projects WHERE code = ?', [$code])->fetch();
    $min = (int)hub_config()['session_active_minutes'];
    $L = ["# Görev: $code" . ($p && $p['name'] !== '' ? ' — ' . $p['name'] : '')];
    if (!$p) {
        $L[] = '_Bu kodla daha önce kayıt yok; yeni görev olarak açıldı._';
    }
    if ($p && trim((string)$p['summary']) !== '') {
        $L[] = "\n## Son durum (güncelleyen: {$p['summary_by']}, {$p['summary_at']})\n" . $p['summary'];
    } elseif ($p) {
        $L[] = "\n## Son durum\n_Henüz yazılmamış. Çalıştıkça hub_project_update ile yaz._";
    }

    $act = q("SELECT s.id, a.name AS agent, s.machine, s.status_text, s.last_seen_at
                FROM hub_sessions s JOIN hub_agents a ON a.id = s.agent_id
               WHERE s.project_code = ? AND s.ended_at IS NULL AND (? IS NULL OR s.id <> ?)
                 AND s.last_seen_at >= NOW() - INTERVAL $min MINUTE", [$code, $mySessionId, $mySessionId])->fetchAll();
    if ($act) {
        $L[] = "\n## Şu an bu görevde çalışan diğer oturumlar";
        foreach ($act as $a) {
            $L[] = "- #{$a['id']} {$a['agent']}@{$a['machine']} (son: " . substr($a['last_seen_at'], 11, 5) . '): '
                 . str_cut((string)$a['status_text'] ?: 'durum yok', 300);
        }
    }

    $notes = q("SELECT id, kind, title, content, created_at FROM hub_topics
                 WHERE project_code = ? AND kind NOT IN ('conversation', 'transcript')
                 ORDER BY id DESC LIMIT 25", [$code])->fetchAll();
    if ($notes) {
        $L[] = "\n## Kararlar ve notlar (yeniden eskiye)";
        foreach ($notes as $n) {
            $L[] = "- [#{$n['id']} {$n['kind']} " . substr($n['created_at'], 0, 16) . '] **' . ($n['title'] ?: '-') . '** — '
                 . str_cut(preg_replace('/\s+/', ' ', $n['content']), 600);
        }
    }

    $conv = q("SELECT t.id, t.title, t.created_at, LEFT(t.content, 1200) AS content, s.machine
                 FROM hub_topics t LEFT JOIN hub_sessions s ON s.id = t.session_id
                WHERE t.project_code = ? AND t.kind = 'conversation'
                ORDER BY t.id DESC LIMIT " . max(1, min($convLimit, 100)), [$code])->fetchAll();
    if ($conv) {
        $total = (int)q("SELECT COUNT(*) FROM hub_topics WHERE project_code = ? AND kind = 'conversation'", [$code])->fetchColumn();
        $L[] = "\n## Son konuşmalar (toplam $total kayıt; tamamı için hub_topics / hub_topic)";
        foreach (array_reverse($conv) as $c) {
            $L[] = "\n### #{$c['id']} · {$c['machine']} · " . substr($c['created_at'], 0, 16) . "\n" . str_cut($c['content'], 1200);
        }
    }

    $files = q("SELECT f.id, f.rel_path, f.size, f.created_at, s.machine
                  FROM hub_files f LEFT JOIN hub_sessions s ON s.id = f.session_id
                 WHERE f.project_code = ? AND f.id IN (SELECT MAX(id) FROM hub_files WHERE project_code = ? GROUP BY rel_path)
                 ORDER BY f.id DESC LIMIT 60", [$code, $code])->fetchAll();
    if ($files) {
        $L[] = "\n## Dosyalar (her yolun son sürümü)";
        foreach ($files as $f) {
            $L[] = "- #{$f['id']} `{$f['rel_path']}` (" . round($f['size'] / 1024, 1) . ' KB, ' . ($f['machine'] ?: 'panel') . ', ' . substr($f['created_at'], 0, 16) . ')';
        }
    }

    $kv = q('SELECT k, LEFT(v, 200) AS v FROM hub_kv WHERE ns = ? ORDER BY k LIMIT 50', [$code])->fetchAll();
    if ($kv) {
        $L[] = "\n## Ortak veri (ns = $code)";
        foreach ($kv as $row) {
            $L[] = "- {$row['k']}: " . str_cut(preg_replace('/\s+/', ' ', $row['v']), 200);
        }
    }
    return implode("\n", $L);
}

/** Dosyayı diske yazar ve kaydını açar. Aynı kaynaktan aynı yol + aynı içerik tekrar gelirse yeni kayıt açmaz. */
function store_file(string $data, string $name, string $relPath, string $code, ?int $sessionId, string $note = ''): array
{
    if (strlen($data) > (int)hub_config()['max_upload_mb'] * 1048576) {
        throw new HubFail('Dosya çok büyük (sınır ' . hub_config()['max_upload_mb'] . ' MB)', 413);
    }
    $name = basename(str_replace('\\', '/', $name));
    $sha = hash('sha256', $data);
    $rel = str_cut(str_replace('\\', '/', $relPath ?: $name), 490);
    $dup = q('SELECT id FROM hub_files WHERE rel_path = ? AND sha256 = ? AND session_id <=> ? AND project_code <=> ? LIMIT 1',
             [$rel, $sha, $sessionId, $code === '' ? null : $code])->fetchColumn();
    if ($dup) {
        return ['id' => (int)$dup, 'duplicate' => true];
    }
    $dir = hub_config()['upload_dir'];
    if (!is_dir($dir) && !mkdir($dir, 0750, true)) {
        throw new HubFail('Yükleme klasörü oluşturulamadı', 500);
    }
    $stored = bin2hex(random_bytes(20));
    if (file_put_contents("$dir/$stored", $data) === false) {
        throw new HubFail('Dosya kaydedilemedi', 500);
    }
    q('INSERT INTO hub_files (session_id, project_code, orig_name, rel_path, stored_name, size, sha256, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
      [$sessionId, $code === '' ? null : $code, str_cut($name, 250), $rel, $stored, strlen($data), $sha, str_cut($note, 250)]);
    return ['id' => (int)db()->lastInsertId()];
}

function arg_str(array $a, string $k, string $default = ''): string
{
    return isset($a[$k]) && $a[$k] !== null ? trim((string)$a[$k]) : $default;
}

/**
 * Tüm hub işlemleri. $a = argümanlar. Sonuç dizi döner; hata durumunda HubFail fırlatır.
 * $session referansla alınır çünkü project_set oturumu değiştirir.
 */
function hub_action(string $r, array $agent, array &$session, array $a): array
{
    $me = session_label($agent, $session);
    $code = (string)($session['project_code'] ?? '');

    switch ($r) {
        case 'ping':
            return ['agent' => $agent['name'], 'agent_type' => $agent['type'], 'session' => $session, 'version' => HUB_VERSION];

        case 'instructions':
            return ['text' => agent_instructions()];

        case 'status':
            q('UPDATE hub_sessions SET status_text = ? WHERE id = ?', [str_cut(arg_str($a, 'status'), 2000), $session['id']]);
            return [];

        case 'end':
            q('UPDATE hub_sessions SET ended_at = NOW() WHERE id = ?', [$session['id']]);
            return [];

        case 'sessions':
            return ['me' => (int)$session['id'], 'sessions' => active_sessions()];

        case 'send':
            $body = arg_str($a, 'body');
            if ($body === '') {
                throw new HubFail('body boş olamaz');
            }
            [$type, $val] = array_pad(explode(':', arg_str($a, 'to', 'all') ?: 'all', 2), 2, '');
            if ($type === 'all') {
                $val = '';
            } elseif ($type === 'admin') {
                $val = '';
            } elseif (!in_array($type, ['agent', 'session', 'machine', 'project'], true) || $val === '') {
                throw new HubFail('to şu biçimlerden biri olmalı: all, admin, agent:AD, session:ID, machine:AD, project:KOD');
            }
            q('INSERT INTO hub_messages (from_session_id, from_label, to_type, to_value, topic, body) VALUES (?, ?, ?, ?, ?, ?)',
              [$session['id'], $me, $type, $val, str_cut(arg_str($a, 'topic'), 190), $body]);
            return ['id' => (int)db()->lastInsertId()];

        case 'inbox':
            $unread = arg_str($a, 'unread', '1') !== '0';
            $mark = arg_str($a, 'mark', '1') !== '0';
            return ['messages' => fetch_inbox($session, $agent, $unread, (int)($a['limit'] ?? 50), $mark)];

        case 'wait': // Dinleme modu: yeni mesaj gelene kadar bekle (en fazla ~25 sn), gelince döndür
            $deadline = time() + max(1, min((int)($a['timeout'] ?? 25), 50));
            @set_time_limit(70);
            do {
                $msgs = fetch_inbox($session, $agent, true, 20, true);
                if ($msgs) {
                    return ['messages' => $msgs];
                }
                q('UPDATE hub_sessions SET last_seen_at = NOW() WHERE id = ?', [$session['id']]);
                sleep(2);
            } while (time() < $deadline);
            return ['messages' => []];

        case 'context': // Hook'lar için düz metin: diğer oturumlar + okunmamış mesajlar
            $lines = [];
            $others = arg_str($a, 'sessions', '1') === '0' ? [] : active_sessions((int)$session['id']);
            if ($others) {
                $lines[] = 'Şu an aktif diğer Claude oturumları:';
                foreach ($others as $o) {
                    $lines[] = sprintf('- #%d %s@%s [%s%s] (son: %s): %s', $o['id'], $o['agent'], $o['machine'],
                        $o['project'] ?: '-', $o['project_code'] ? ', görev ' . $o['project_code'] : '',
                        substr($o['last_seen_at'], 11, 5), str_cut((string)$o['status_text'] ?: 'durum yok', 300));
                }
            }
            $msgs = fetch_inbox($session, $agent, true, 20, true);
            if ($msgs) {
                $lines[] = 'Sana gelen okunmamış hub mesajları:';
                foreach ($msgs as $m) {
                    $lines[] = sprintf('- [#%d %s] %s%s: %s', $m['id'], substr($m['created_at'], 0, 16), $m['from_label'],
                        $m['topic'] !== '' ? ' (' . $m['topic'] . ')' : '', str_cut($m['body'], 1500));
                }
            }
            return ['session_id' => (int)$session['id'], 'project_code' => $code ?: null, 'text' => implode("\n", $lines)];

        case 'project_set': // Oturumu bir göreve bağla ve görevin tüm özetini döndür
            $new = arg_str($a, 'code');
            if ($new !== '' && !valid_project_code($new)) {
                throw new HubFail('Geçersiz görev kodu. Harf/rakam ile başlamalı; harf, rakam, . _ - / içerebilir (en fazla 60).');
            }
            q('UPDATE hub_sessions SET project_code = ? WHERE id = ?', [$new === '' ? null : $new, $session['id']]);
            $session['project_code'] = $new === '' ? null : $new;
            if ($new === '') {
                return ['code' => null];
            }
            $existed = (bool)q('SELECT 1 FROM hub_projects WHERE code = ?', [$new])->fetchColumn();
            $brief = project_brief_md($new, (int)$session['id']);
            if (!$existed) {
                q('INSERT IGNORE INTO hub_projects (code, name) VALUES (?, ?)', [$new, str_cut(arg_str($a, 'name'), 190)]);
            }
            return ['code' => $new, 'new_project' => !$existed, 'brief' => $brief];

        case 'project_brief':
            $c = arg_str($a, 'code') ?: $code;
            if ($c === '') {
                throw new HubFail('Görev kodu belirtilmedi (önce hub_set_project ya da code parametresi).');
            }
            return ['code' => $c, 'brief' => project_brief_md($c, (int)$session['id'], (int)($a['conversations'] ?? 15))];

        case 'project_update': // Görevin "son durum" notunu ve/veya adını güncelle
            $c = arg_str($a, 'code') ?: $code;
            if ($c === '' || !valid_project_code($c)) {
                throw new HubFail('Geçerli bir görev kodu gerekli.');
            }
            q('INSERT IGNORE INTO hub_projects (code) VALUES (?)', [$c]);
            if (($name = arg_str($a, 'name')) !== '') {
                q('UPDATE hub_projects SET name = ? WHERE code = ?', [str_cut($name, 190), $c]);
            }
            if (($sum = arg_str($a, 'summary')) !== '') {
                q('UPDATE hub_projects SET summary = ?, summary_by = ?, summary_at = NOW() WHERE code = ?',
                  [str_cut($sum, 100000), $me, $c]);
                // Eski sürüm kaybolmasın diye geçmişe de yaz
                q('INSERT INTO hub_topics (session_id, project_code, kind, title, content) VALUES (?, ?, ?, ?, ?)',
                  [$session['id'], $c, 'status', 'Son durum güncellendi', str_cut($sum, 100000)]);
            }
            return ['code' => $c];

        case 'projects':
            return ['projects' => q("SELECT p.code, p.name, p.summary_at, p.created_at,
                    (SELECT COUNT(*) FROM hub_topics t WHERE t.project_code = p.code) AS records,
                    (SELECT COUNT(*) FROM hub_files f WHERE f.project_code = p.code) AS files,
                    (SELECT MAX(t.created_at) FROM hub_topics t WHERE t.project_code = p.code) AS last_activity
                    FROM hub_projects p ORDER BY last_activity DESC, p.created_at DESC")->fetchAll()];

        case 'topic_add':
            $content = (string)($a['content'] ?? '');
            if (trim($content) === '') {
                throw new HubFail('content boş olamaz');
            }
            $kind = preg_replace('/[^a-z_]/', '', arg_str($a, 'kind', 'note')) ?: 'note';
            $c = arg_str($a, 'code') ?: $code;
            q('INSERT INTO hub_topics (session_id, project_code, kind, title, content) VALUES (?, ?, ?, ?, ?)',
              [$session['id'], $c === '' ? null : $c, $kind, str_cut(arg_str($a, 'title'), 250), str_cut($content, 2000000)]);
            return ['id' => (int)db()->lastInsertId()];

        case 'topics':
            $where = ['1=1'];
            $p = [];
            if (($qs = arg_str($a, 'q')) !== '') {
                $where[] = '(t.title LIKE ? OR t.content LIKE ?)';
                array_push($p, "%$qs%", "%$qs%");
            }
            foreach (['machine' => 's.machine', 'project' => 's.project', 'kind' => 't.kind', 'code' => 't.project_code'] as $k => $col) {
                if (($v = arg_str($a, $k)) !== '') {
                    $where[] = "$col = ?";
                    $p[] = $v;
                }
            }
            if (($sid = (int)($a['session'] ?? 0)) > 0) {
                $where[] = 't.session_id = ?';
                $p[] = $sid;
            }
            $limit = max(1, min((int)($a['limit'] ?? 20), 200));
            $offset = max(0, (int)($a['offset'] ?? 0));
            return ['topics' => q("SELECT t.id, t.project_code, t.kind, t.title, LEFT(t.content, 500) AS preview,
                                          LENGTH(t.content) AS length, t.created_at, t.session_id, s.machine, s.project, a.name AS agent
                                     FROM hub_topics t
                                LEFT JOIN hub_sessions s ON s.id = t.session_id
                                LEFT JOIN hub_agents a ON a.id = s.agent_id
                                    WHERE " . implode(' AND ', $where) . " ORDER BY t.id DESC LIMIT $limit OFFSET $offset", $p)->fetchAll()];

        case 'topic':
            $row = q('SELECT t.*, s.machine, s.project FROM hub_topics t LEFT JOIN hub_sessions s ON s.id = t.session_id WHERE t.id = ?',
                     [(int)($a['id'] ?? 0)])->fetch();
            if (!$row) {
                throw new HubFail('Bulunamadı', 404);
            }
            // Çok uzun kayıtlar parça parça okunur
            $off = max(0, (int)($a['offset'] ?? 0));
            $len = max(1000, min((int)($a['max_chars'] ?? 60000), 200000));
            $full = $row['content'];
            $row['content'] = mb_substr($full, $off, $len);
            $row['total_chars'] = mb_strlen($full);
            $row['next_offset'] = $off + $len < $row['total_chars'] ? $off + $len : null;
            return ['topic' => $row];

        case 'upload':
            $name = basename(str_replace('\\', '/', arg_str($a, 'name')));
            $b64 = (string)($a['content_b64'] ?? '');
            if ($name === '' || $b64 === '') {
                throw new HubFail('name ve content_b64 gerekli');
            }
            $data = base64_decode($b64, true);
            if ($data === false) {
                throw new HubFail('content_b64 geçersiz');
            }
            if (strlen($data) > (int)hub_config()['max_upload_mb'] * 1048576) {
                throw new HubFail('Dosya çok büyük (sınır ' . hub_config()['max_upload_mb'] . ' MB)', 413);
            }
            $c = arg_str($a, 'code') ?: $code;
            return store_file($data, $name, arg_str($a, 'rel_path', $name), $c, (int)$session['id'], arg_str($a, 'note'));

        case 'files':
            $where = ['1=1'];
            $p = [];
            if (($qs = arg_str($a, 'q')) !== '') {
                $where[] = '(f.orig_name LIKE ? OR f.rel_path LIKE ? OR s.project LIKE ?)';
                array_push($p, "%$qs%", "%$qs%", "%$qs%");
            }
            if (($c = arg_str($a, 'code')) !== '') {
                $where[] = 'f.project_code = ?';
                $p[] = $c;
            }
            $limit = max(1, min((int)($a['limit'] ?? 30), 300));
            return ['files' => q("SELECT f.id, f.project_code, f.orig_name, f.rel_path, f.size, f.note, f.created_at,
                                         s.machine, s.project, a.name AS agent
                                    FROM hub_files f
                               LEFT JOIN hub_sessions s ON s.id = f.session_id
                               LEFT JOIN hub_agents a ON a.id = s.agent_id
                                   WHERE " . implode(' AND ', $where) . " ORDER BY f.id DESC LIMIT $limit", $p)->fetchAll()];

        case 'file_get': // İçerik: format=text (metin dosyaları) veya base64
            $f = q('SELECT * FROM hub_files WHERE id = ?', [(int)($a['id'] ?? 0)])->fetch();
            $path = $f ? hub_config()['upload_dir'] . '/' . $f['stored_name'] : '';
            if (!$f || !is_file($path)) {
                throw new HubFail('Bulunamadı', 404);
            }
            $data = (string)file_get_contents($path);
            $info = ['id' => (int)$f['id'], 'name' => $f['orig_name'], 'rel_path' => $f['rel_path'],
                     'project_code' => $f['project_code'], 'size' => (int)$f['size']];
            if (arg_str($a, 'format') === 'text') {
                if (!mb_check_encoding($data, 'UTF-8') || strpos($data, "\0") !== false) {
                    throw new HubFail('Bu dosya metin değil (ikili dosya).');
                }
                $info['text'] = str_cut($data, 300000);
            } else {
                $info['content_b64'] = base64_encode($data);
            }
            return $info;

        case 'kv_set':
            $k = str_cut(arg_str($a, 'key'), 190);
            if ($k === '') {
                throw new HubFail('key gerekli');
            }
            q('INSERT INTO hub_kv (ns, k, v, updated_by) VALUES (?, ?, ?, ?)
               ON DUPLICATE KEY UPDATE v = VALUES(v), updated_by = VALUES(updated_by)',
              [str_cut(arg_str($a, 'ns') ?: ($code ?: 'default'), 100), $k, (string)($a['value'] ?? ''), $me]);
            return [];

        case 'kv_get':
            $row = q('SELECT ns, k AS `key`, v AS value, updated_by, updated_at FROM hub_kv WHERE ns = ? AND k = ?',
                     [arg_str($a, 'ns') ?: ($code ?: 'default'), arg_str($a, 'key')])->fetch();
            if (!$row) {
                throw new HubFail('Bulunamadı', 404);
            }
            return ['item' => $row];

        case 'kv_list':
            $ns = arg_str($a, 'ns');
            return ['items' => $ns === ''
                ? q('SELECT ns, COUNT(*) AS keys_count, MAX(updated_at) AS updated_at FROM hub_kv GROUP BY ns ORDER BY ns')->fetchAll()
                : q('SELECT k AS `key`, LEFT(v, 300) AS preview, updated_by, updated_at FROM hub_kv WHERE ns = ? ORDER BY k', [$ns])->fetchAll()];

        case 'kv_del':
            q('DELETE FROM hub_kv WHERE ns = ? AND k = ?', [arg_str($a, 'ns') ?: ($code ?: 'default'), arg_str($a, 'key')]);
            return [];
    }
    throw new HubFail('Bilinmeyen komut: ' . $r, 404);
}
