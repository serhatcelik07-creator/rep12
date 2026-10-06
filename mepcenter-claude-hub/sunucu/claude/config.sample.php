<?php
// Bu dosyayı install.php otomatik olarak config.php adıyla oluşturur.
// Elle kurmak isterseniz config.php olarak kopyalayıp düzenleyin.
return [
    'db' => [
        'host' => 'localhost',
        'name' => 'mepcente_claude',
        'user' => 'mepcente_claude',
        'pass' => 'VERITABANI_SIFRESI',
        'charset' => 'utf8mb4',
    ],
    // Dosya başına en fazla yükleme boyutu (MB)
    'max_upload_mb' => 20,
    // Boş bırakılırsa her IP'den bağlanılabilir (token yine zorunlu).
    // Örnek: ['88.1.2.3', '78.4.5.6']
    'allowed_ips' => [],
    // Bu kadar dakikadır ses vermeyen oturum "aktif değil" sayılır
    'session_active_minutes' => 30,
    'timezone' => 'Europe/Istanbul',
];
