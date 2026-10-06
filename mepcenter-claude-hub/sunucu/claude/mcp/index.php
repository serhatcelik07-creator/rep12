<?php
// MepCenter Claude Hub - uzak MCP sunucusu (Streamable HTTP, yalnızca JSON yanıt)
//
// claude.ai (web/mobil), Claude Desktop ve Cowork için "Custom Connector" adresi:
//   https://mepcenter.com.tr/claude/mcp/?k=AJAN_TOKENI
// Claude Code için:  claude mcp add --transport http mepcenter https://mepcenter.com.tr/claude/mcp/ \
//                       --header "Authorization: Bearer AJAN_TOKENI"

declare(strict_types=1);
require dirname(__DIR__) . '/lib/hub.php';
require dirname(__DIR__) . '/lib/tools.php';

const MCP_VERSIONS = ['2024-11-05', '2025-03-26', '2025-06-18'];

header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

function rpc_out($payload, int $code = 200): void
{
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_INVALID_UTF8_SUBSTITUTE);
    exit;
}

function rpc_error($id, int $code, string $msg): array
{
    return ['jsonrpc' => '2.0', 'id' => $id, 'error' => ['code' => $code, 'message' => $msg]];
}

$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
if ($method === 'GET') {
    // Sunucudan istemciye SSE akışı desteklenmiyor
    header('Allow: POST');
    rpc_out(['error' => 'Bu MCP uç noktası yalnızca POST kabul eder.'], 405);
}
if ($method === 'DELETE') {
    http_response_code(204);
    exit;
}
if ($method !== 'POST') {
    rpc_out(['error' => 'Desteklenmeyen metot'], 405);
}

try {
    if (!ip_allowed()) {
        throw new HubFail('Bu IP adresine izin verilmiyor', 403);
    }
    $agent = authenticate();
} catch (HubFail $e) {
    header('WWW-Authenticate: Bearer');
    rpc_out(rpc_error(null, -32001, $e->getMessage()), 401);
}

$req = json_decode((string)file_get_contents('php://input'), true);
if (!is_array($req)) {
    rpc_out(rpc_error(null, -32700, 'Geçersiz JSON'), 400);
}

$session = null;
$handle = function (array $m) use ($agent, &$session): ?array {
    $id = $m['id'] ?? null;
    $name = (string)($m['method'] ?? '');
    if (!array_key_exists('id', $m)) {
        return null; // bildirim
    }
    try {
        switch ($name) {
            case 'initialize':
                $want = (string)($m['params']['protocolVersion'] ?? '');
                return ['jsonrpc' => '2.0', 'id' => $id, 'result' => [
                    'protocolVersion' => in_array($want, MCP_VERSIONS, true) ? $want : end(MCP_VERSIONS),
                    'capabilities' => ['tools' => ['listChanged' => false]],
                    'serverInfo' => ['name' => 'mepcenter-hub', 'version' => HUB_VERSION],
                    'instructions' => agent_instructions(),
                ]];
            case 'ping':
                return ['jsonrpc' => '2.0', 'id' => $id, 'result' => new stdClass()];
            case 'tools/list':
                return ['jsonrpc' => '2.0', 'id' => $id, 'result' => ['tools' => hub_tools_list()]];
            case 'tools/call':
                if ($session === null) {
                    $session = touch_session($agent, 'web');
                }
                $p = $m['params'] ?? [];
                try {
                    $text = hub_tool_call((string)($p['name'] ?? ''), (array)($p['arguments'] ?? []), $agent, $session);
                    $isError = false;
                } catch (HubFail $e) {
                    $text = 'Hata: ' . $e->getMessage();
                    $isError = true;
                }
                return ['jsonrpc' => '2.0', 'id' => $id, 'result' => [
                    'content' => [['type' => 'text', 'text' => $text]], 'isError' => $isError]];
            case 'resources/list':
                return ['jsonrpc' => '2.0', 'id' => $id, 'result' => ['resources' => []]];
            case 'prompts/list':
                return ['jsonrpc' => '2.0', 'id' => $id, 'result' => ['prompts' => []]];
        }
        return rpc_error($id, -32601, "Desteklenmeyen metot: $name");
    } catch (Throwable $e) {
        error_log('[claude-hub mcp] ' . $e);
        return rpc_error($id, -32603, 'Sunucu hatası');
    }
};

if (isset($req[0])) { // toplu istek
    $replies = array_values(array_filter(array_map($handle, $req)));
    if (!$replies) {
        http_response_code(202);
        exit;
    }
    rpc_out($replies);
}
$reply = $handle($req);
if ($reply === null) {
    http_response_code(202);
    exit;
}
rpc_out($reply);
