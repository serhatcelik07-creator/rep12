<?php
// MepCenter Claude Hub - ortak çekirdek (veritabanı, ayarlar, yardımcılar)

declare(strict_types=1);

const HUB_VERSION = '1.1.0';
define('HUB_ROOT', dirname(__DIR__));

function hub_config(): array
{
    static $cfg = null;
    if ($cfg === null) {
        $file = HUB_ROOT . '/config.php';
        if (!is_file($file)) {
            throw new RuntimeException('config.php yok. Önce install.php çalıştırın.');
        }
        $cfg = require $file;
        $cfg += [
            'max_upload_mb' => 20,
            'allowed_ips' => [],
            'session_active_minutes' => 30,
            'upload_dir' => HUB_ROOT . '/data/uploads',
            'timezone' => 'Europe/Istanbul',
        ];
        date_default_timezone_set($cfg['timezone']);
    }
    return $cfg;
}

function db(): PDO
{
    static $pdo = null;
    if ($pdo === null) {
        $c = hub_config()['db'];
        $dsn = sprintf('mysql:host=%s;dbname=%s;charset=%s', $c['host'], $c['name'], $c['charset'] ?? 'utf8mb4');
        $pdo = new PDO($dsn, $c['user'], $c['pass'], [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]);
        $pdo->exec("SET time_zone = '" . date('P') . "'");
    }
    return $pdo;
}

function q(string $sql, array $params = []): PDOStatement
{
    $st = db()->prepare($sql);
    $st->execute($params);
    return $st;
}

function setting_get(string $k, ?string $default = null): ?string
{
    $v = q('SELECT v FROM hub_settings WHERE k = ?', [$k])->fetchColumn();
    return $v === false ? $default : $v;
}

function setting_set(string $k, string $v): void
{
    q('INSERT INTO hub_settings (k, v) VALUES (?, ?) ON DUPLICATE KEY UPDATE v = VALUES(v)', [$k, $v]);
}

function client_ip(): string
{
    return $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
}

function ip_allowed(): bool
{
    $list = hub_config()['allowed_ips'];
    return !$list || in_array(client_ip(), $list, true);
}

function h(?string $s): string
{
    return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8');
}

function new_token(): string
{
    return 'mch_' . bin2hex(random_bytes(24));
}

function token_hash(string $token): string
{
    return hash('sha256', $token);
}

function str_cut(string $s, int $max): string
{
    return mb_strlen($s) > $max ? mb_substr($s, 0, $max) . '…' : $s;
}

/** Bir oturumun alabileceği mesajlar için WHERE parçası (m = hub_messages) */
function inbox_where(array $session, array $agent): array
{
    $sql = "(m.to_type = 'all'
            OR (m.to_type = 'agent' AND m.to_value = :agent)
            OR (m.to_type = 'session' AND m.to_value = :sid)
            OR (m.to_type = 'machine' AND m.to_value = :machine)
            OR (m.to_type = 'project' AND (m.to_value = :project OR m.to_value = :pcode)))
            AND (m.from_session_id IS NULL OR m.from_session_id <> :sid2)
            AND m.created_at >= :started";
    return [$sql, [
        ':agent' => $agent['name'],
        ':sid' => (string)$session['id'],
        ':machine' => (string)$session['machine'],
        ':project' => (string)$session['project'],
        ':pcode' => (string)($session['project_code'] ?? ''),
        ':sid2' => $session['id'],
        // Yeni açılan oturum son 3 günün mesajlarını görür, daha eskisini değil
        ':started' => date('Y-m-d H:i:s', strtotime($session['started_at']) - 3 * 86400),
    ]];
}

function active_sessions(?int $excludeId = null): array
{
    $min = (int)hub_config()['session_active_minutes'];
    return q(
        "SELECT s.id, a.name AS agent, a.type AS agent_type, s.machine, s.project, s.project_code, s.cwd,
                s.status_text, s.started_at, s.last_seen_at,
                TIMESTAMPDIFF(SECOND, s.last_seen_at, NOW()) AS idle_sec
           FROM hub_sessions s JOIN hub_agents a ON a.id = s.agent_id
          WHERE s.ended_at IS NULL AND s.last_seen_at >= (NOW() - INTERVAL $min MINUTE)
            AND (? IS NULL OR s.id <> ?)
          ORDER BY s.last_seen_at DESC",
        [$excludeId, $excludeId]
    )->fetchAll();
}

/** Proje kodu biçimi: harf/rakamla başlar; harf, rakam, . _ - / içerebilir (en fazla 60) */
function valid_project_code(string $code): bool
{
    return (bool)preg_match('~^[A-Za-z0-9][A-Za-z0-9._/-]{0,59}$~', $code);
}
