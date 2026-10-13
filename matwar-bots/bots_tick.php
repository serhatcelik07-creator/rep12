<?php
declare(strict_types=1);
// Bot hayatı tetikleyicisi: bilgisayardaki tools/bot_runner.py dakikada bir çağırır.
// Her çağrıda sırası gelen botlar birbiriyle düello yapar (her bot ~15 dk'da bir) ve botlar sohbette konuşur.
// Kimlik: "X-Bot-Key" başlığı = config 'bot_tick_key'. Anahtar tanımlı değilse uç nokta kapalıdır.
// Hostingde kaynak ~/mathwars/src (index.php.hosting gibi), yerelde ../../src.
$base = is_dir(dirname(__DIR__, 2) . '/mathwars/src') ? dirname(__DIR__, 2) . '/mathwars' : dirname(__DIR__, 2);
require "$base/src/bootstrap.php";
require "$base/src/Season.php";
require "$base/src/BotLife.php";

set_exception_handler(function (Throwable $e) { error_log('[bots_tick] ' . $e); App::fail('server_error', 500); });
App::init("$base/config.php");

$key = (string) (App::$cfg['bot_tick_key'] ?? '');
if ($key === '') App::fail('disabled', 403);
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') App::fail('post_required', 405);
if (!hash_equals($key, (string) ($_SERVER['HTTP_X_BOT_KEY'] ?? ''))) App::fail('unauthorized', 401);

App::ok(BotLife::tick() + ['server_ms' => App::nowMs()]);
