<?php
// /claude adresine gelen tarayıcıyı panele, kurulum yapılmadıysa kuruluma yönlendir
header('Location: ' . (is_file(__DIR__ . '/config.php') ? 'admin/' : 'install.php'));
