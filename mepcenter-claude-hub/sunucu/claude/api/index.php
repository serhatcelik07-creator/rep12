<?php
// MepCenter Claude Hub - REST API (yerel hook'lar ve istemciler için)
// Kullanım: /claude/api/?r=<komut>   GET parametreleri veya JSON gövde
// Kimlik: "Authorization: Bearer <token>" veya "X-Hub-Token: <token>"
// Oturum: X-Hub-Client-Key, X-Hub-Machine, X-Hub-Project, X-Hub-Cwd başlıkları

declare(strict_types=1);
require dirname(__DIR__) . '/lib/hub.php';
require dirname(__DIR__) . '/lib/tools.php';

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

function out(array $data, int $code = 200): void
{
    http_response_code($code);
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_INVALID_UTF8_SUBSTITUTE);
    exit;
}

try {
    if (!ip_allowed()) {
        throw new HubFail('Bu IP adresine izin verilmiyor', 403);
    }
    $raw = (string)file_get_contents('php://input');
    $body = $raw !== '' ? json_decode($raw, true) : [];
    $args = (is_array($body) ? $body : []) + $_GET;
    unset($args['r'], $args['k']);
    $r = (string)($_GET['r'] ?? 'ping');

    if ($r === 'register') { // Kurulum programı: panel kullanıcı adı/şifresiyle bu bilgisayarı kaydet
        if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
            throw new HubFail('POST gerekli', 405);
        }
        out(['ok' => true] + register_machine((string)($args['user'] ?? ''), (string)($args['pass'] ?? ''),
                                             (string)($args['machine'] ?? '')));
    }

    $agent = authenticate();
    $session = touch_session($agent);

    if ($r === 'tools') { // Yerel MCP köprüsü araç listesini buradan alır
        out(['ok' => true, 'tools' => hub_tools_list(), 'instructions' => agent_instructions()]);
    }
    if ($r === 'tool_call') {
        $text = hub_tool_call((string)($args['name'] ?? ''), (array)($args['arguments'] ?? []), $agent, $session);
        out(['ok' => true, 'text' => $text]);
    }
    if ($r === 'download') { // Ham dosya indirme
        $f = hub_action('file_get', $agent, $session, $args);
        $data = base64_decode($f['content_b64']);
        header('Content-Type: application/octet-stream');
        header('Content-Length: ' . strlen($data));
        header("Content-Disposition: attachment; filename*=UTF-8''" . rawurlencode($f['name']));
        echo $data;
        exit;
    }
    out(['ok' => true] + hub_action($r, $agent, $session, $args));
} catch (HubFail $e) {
    out(['ok' => false, 'error' => $e->getMessage()], $e->getCode() ?: 400);
} catch (Throwable $e) {
    error_log('[claude-hub] ' . $e);
    out(['ok' => false, 'error' => 'Sunucu hatası'], 500);
}
