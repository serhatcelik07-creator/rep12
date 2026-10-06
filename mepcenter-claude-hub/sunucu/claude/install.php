<?php
// MepCenter Claude Hub - kurulum ve panel şifresi sıfırlama.
// İlk kurulum: veritabanı şifresi + panel şifresi sorulur.
// Şifre unutulursa: data/install.lock dosyasını silip bu sayfayı açın; yalnızca yeni panel şifresi sorulur.

declare(strict_types=1);
require __DIR__ . '/lib/bootstrap.php';

$lock = HUB_ROOT . '/data/install.lock';
$cfgFile = HUB_ROOT . '/config.php';
$err = '';
$done = false;
$configText = null;
$adminUser = 'claude';

if (is_file($lock)) {
    http_response_code(403);
    exit('<meta charset="utf-8"><p style="font:16px system-ui;padding:24px">Kurulum zaten yapılmış. '
        . '<a href="admin/">Panele git</a>.<br><br>Panel şifresini unuttuysanız: cPanel Dosya Yöneticisi\'nde '
        . '<b>public_html/claude/data/install.lock</b> dosyasını silin ve bu sayfayı yenileyin.</p>');
}

// config.php varsa ve veritabanına bağlanılabiliyorsa: yalnızca şifre sıfırlama
$resetMode = false;
if (is_file($cfgFile)) {
    try {
        db()->query('SELECT 1');
        $resetMode = true;
    } catch (Throwable $e) {
        $resetMode = false;
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $adminPass = (string)($_POST['admin_pass'] ?? '');
    try {
        if (strlen($adminPass) < 10) {
            throw new RuntimeException('Panel şifresi en az 10 karakter olmalı.');
        }
        if ($adminPass !== (string)($_POST['admin_pass2'] ?? '')) {
            throw new RuntimeException('İki şifre aynı değil.');
        }
        if ($resetMode) {
            $pdo = db();
        } else {
            $dbHost = trim($_POST['db_host'] ?? 'localhost') ?: 'localhost';
            $dbName = trim($_POST['db_name'] ?? '') ?: 'mepcente_claude';
            $dbUser = trim($_POST['db_user'] ?? '') ?: 'mepcente_claude';
            $dbPass = (string)($_POST['db_pass'] ?? '');
            try {
                $pdo = new PDO("mysql:host=$dbHost;dbname=$dbName;charset=utf8mb4", $dbUser, $dbPass,
                               [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
            } catch (PDOException $e) {
                throw new RuntimeException('Veritabanına bağlanılamadı. cPanel > MySQL Veritabanları\'ndaki veritabanı adı, '
                    . 'kullanıcı ve şifreyi kontrol edin (kullanıcı veritabanına "tüm yetkiler" ile eklenmiş olmalı). '
                    . 'Teknik ayrıntı: ' . $e->getMessage());
            }
            $configText = "<?php\nreturn " . var_export([
                'db' => ['host' => $dbHost, 'name' => $dbName, 'user' => $dbUser, 'pass' => $dbPass, 'charset' => 'utf8mb4'],
                'max_upload_mb' => 20,
                'allowed_ips' => [],
                'session_active_minutes' => 30,
                'timezone' => 'Europe/Istanbul',
            ], true) . ";\n";
        }

        // Tablolar (zaten varsa dokunulmaz)
        $sql = (string)file_get_contents(HUB_ROOT . '/lib/schema.sql');
        foreach (array_filter(array_map('trim', explode(';', $sql))) as $stmt) {
            if (!preg_match('/^\s*(--.*\n\s*)*$/', $stmt)) {
                $pdo->exec($stmt);
            }
        }
        $up = $pdo->prepare('INSERT INTO hub_settings (k, v) VALUES (?, ?) ON DUPLICATE KEY UPDATE v = VALUES(v)');
        $up->execute(['admin_user', $adminUser]);
        $up->execute(['admin_pass_hash', password_hash($adminPass, PASSWORD_DEFAULT)]);
        $pdo->exec('DELETE FROM hub_login_attempts'); // 15 dakikalık giriş kilidini kaldır

        if ($configText !== null) {
            if (!is_dir(HUB_ROOT . '/data/uploads')) {
                @mkdir(HUB_ROOT . '/data/uploads', 0750, true);
            }
            if (@file_put_contents($cfgFile, $configText) !== false) {
                @chmod($cfgFile, 0640);
                $configText = null;
            }
        }
        if ($configText === null) {
            file_put_contents($lock, date('c'));
        }
        $done = true;
    } catch (Throwable $e) {
        $err = $e->getMessage();
    }
}
?><!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Claude Hub Kurulum</title>
<link rel="stylesheet" href="admin/style.css"></head>
<body><main class="narrow">
<h1><?= $resetMode ? 'Panel şifresini yenile' : 'Claude Hub kurulumu' ?></h1>
<?php if ($err): ?><p class="err"><?= h($err) ?></p><?php endif; ?>

<?php if ($done): ?>
  <?php if ($configText): ?>
    <p class="err">Ayar dosyası yazılamadı. Aşağıdaki metni cPanel Dosya Yöneticisi'nde <b>public_html/claude/config.php</b>
      adında yeni bir dosya oluşturup içine yapıştırın, sonra bu sayfayı tekrar açın:</p>
    <pre><?= h($configText) ?></pre>
  <?php else: ?>
    <p class="ok">Tamam! Artık panele girebilirsiniz.</p>
    <div class="card">
      <p>Kullanıcı adı: <b>claude</b><br>Şifre: <b>az önce yazdığınız şifre</b></p>
      <a class="btn" href="admin/">Panele git →</a>
    </div>
  <?php endif; ?>
<?php else: ?>
<form method="post" class="card">
  <?php if (!$resetMode): ?>
    <h2>1. Veritabanı şifresi</h2>
    <p class="meta">cPanel &gt; MySQL Veritabanları'nda <b>mepcente_claude</b> kullanıcısını oluştururken verdiğiniz şifre.</p>
    <label>Veritabanı şifresi <input name="db_pass" type="password" required></label>
    <details><summary class="meta">Veritabanı adı / kullanıcı farklıysa tıklayın</summary>
      <label>Sunucu <input name="db_host" value="localhost"></label>
      <label>Veritabanı adı <input name="db_name" value="mepcente_claude"></label>
      <label>Kullanıcı adı <input name="db_user" value="mepcente_claude"></label>
    </details>
    <h2>2. Panel şifresi</h2>
  <?php else: ?>
    <p class="meta">Kurulum zaten yapılmış; sadece yeni bir panel şifresi belirleyin. Hiçbir kayıt silinmez.</p>
  <?php endif; ?>
  <p>Panele giriş kullanıcı adı: <b>claude</b></p>
  <label>Yeni panel şifresi (en az 10 karakter) <input name="admin_pass" type="password" minlength="10" required autocomplete="new-password"></label>
  <label>Şifre tekrar <input name="admin_pass2" type="password" minlength="10" required autocomplete="new-password"></label>
  <p class="meta">Bu şifreyi bir yere not edin.</p>
  <button type="submit"><?= $resetMode ? 'Şifreyi kaydet' : 'Kur' ?></button>
</form>
<?php endif; ?>
</main></body></html>
