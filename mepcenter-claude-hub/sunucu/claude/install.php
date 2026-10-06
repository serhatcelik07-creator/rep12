<?php
// MepCenter Claude Hub - tek seferlik kurulum sihirbazı.
// Kurulum bitince data/install.lock oluşturulur ve bu sayfa kapanır.

declare(strict_types=1);
require __DIR__ . '/lib/bootstrap.php';

$lock = HUB_ROOT . '/data/install.lock';
$cfgFile = HUB_ROOT . '/config.php';
$msg = '';
$err = '';
$newToken = null;
$configText = null;

if (is_file($lock)) {
    http_response_code(403);
    exit('Kurulum zaten yapılmış. Yeniden kurmak için data/install.lock dosyasını silin.');
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $dbHost = trim($_POST['db_host'] ?? 'localhost');
    $dbName = trim($_POST['db_name'] ?? '');
    $dbUser = trim($_POST['db_user'] ?? '');
    $dbPass = (string)($_POST['db_pass'] ?? '');
    $adminUser = trim($_POST['admin_user'] ?? 'claude');
    $adminPass = (string)($_POST['admin_pass'] ?? '');
    $firstAgent = trim($_POST['first_agent'] ?? '');

    try {
        if (strlen($adminPass) < 10) {
            throw new RuntimeException('Panel şifresi en az 10 karakter olmalı.');
        }
        $pdo = new PDO("mysql:host=$dbHost;dbname=$dbName;charset=utf8mb4", $dbUser, $dbPass, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        ]);
        $sql = file_get_contents(HUB_ROOT . '/lib/schema.sql');
        foreach (array_filter(array_map('trim', explode(';', $sql))) as $stmt) {
            if (preg_match('/^\s*(--.*\n\s*)*$/', $stmt)) {
                continue;
            }
            $pdo->exec($stmt);
        }

        $up = $pdo->prepare('INSERT INTO hub_settings (k, v) VALUES (?, ?) ON DUPLICATE KEY UPDATE v = VALUES(v)');
        $up->execute(['admin_user', $adminUser]);
        $up->execute(['admin_pass_hash', password_hash($adminPass, PASSWORD_DEFAULT)]);

        if ($firstAgent !== '') {
            $newToken = new_token();
            $ins = $pdo->prepare('INSERT INTO hub_agents (name, type, token_hash, token_hint) VALUES (?, ?, ?, ?)');
            $ins->execute([$firstAgent, 'claude', token_hash($newToken), substr($newToken, -6)]);
        }

        $configText = "<?php\nreturn " . var_export([
            'db' => ['host' => $dbHost, 'name' => $dbName, 'user' => $dbUser, 'pass' => $dbPass, 'charset' => 'utf8mb4'],
            'max_upload_mb' => 20,
            'allowed_ips' => [],
            'session_active_minutes' => 30,
            'timezone' => 'Europe/Istanbul',
        ], true) . ";\n";

        if (!is_dir(HUB_ROOT . '/data/uploads')) {
            @mkdir(HUB_ROOT . '/data/uploads', 0750, true);
        }
        if (@file_put_contents($cfgFile, $configText) !== false) {
            $configText = null; // yazıldı, ekranda göstermeye gerek yok
            @chmod($cfgFile, 0640);
        }
        file_put_contents($lock, date('c'));
        $msg = 'Kurulum tamamlandı.';
    } catch (Throwable $e) {
        $err = $e->getMessage();
    }
}
?><!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Claude Hub Kurulum</title>
<link rel="stylesheet" href="admin/style.css"></head>
<body><main class="narrow">
<h1>Claude Hub Kurulumu</h1>
<?php if ($err): ?><p class="err"><?= h($err) ?></p><?php endif; ?>
<?php if ($msg): ?>
  <p class="ok"><?= h($msg) ?></p>
  <?php if ($configText): ?>
    <p class="err">config.php yazılamadı. Aşağıdaki içeriği <code>claude/config.php</code> olarak kaydedin:</p>
    <pre><?= h($configText) ?></pre>
  <?php endif; ?>
  <?php if ($newToken): ?>
    <h2>İlk ajan token'ı</h2>
    <p>Bu token <b>yalnızca bir kez</b> gösterilir. Kopyalayıp o makinenin istemci kurulumunda kullanın:</p>
    <pre class="token"><?= h($newToken) ?></pre>
  <?php endif; ?>
  <p><a class="btn" href="admin/">Yönetim paneline git →</a></p>
<?php else: ?>
<form method="post" class="card">
  <h2>Veritabanı</h2>
  <label>Sunucu <input name="db_host" value="localhost" required></label>
  <label>Veritabanı adı <input name="db_name" value="mepcente_claude" required></label>
  <label>Kullanıcı adı <input name="db_user" value="mepcente_claude" required></label>
  <label>Şifre <input name="db_pass" type="password" required></label>
  <h2>Yönetim paneli girişi</h2>
  <label>Kullanıcı adı <input name="admin_user" value="claude" required></label>
  <label>Şifre (en az 10 karakter) <input name="admin_pass" type="password" minlength="10" required></label>
  <h2>İlk ajan (isteğe bağlı)</h2>
  <label>Ajan adı, örn. <i>mac-claude</i> <input name="first_agent" placeholder="mac-claude"></label>
  <button type="submit">Kur</button>
</form>
<?php endif; ?>
</main></body></html>
