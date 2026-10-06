#!/usr/bin/env python3
"""MepCenter Claude Hub - yerel MCP köprüsü (stdio), Claude Code ve Claude Desktop için.

Araç listesi ve talimat sunucudan alınır (tek kaynak: sunucu/claude/lib/tools.php).
Yerel dosya sistemine erişmesi gereken iki araç burada çalışır: hub_upload, hub_download.
Yalnızca Python standart kütüphanesi kullanır.
"""

import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hub_client import HubError, api, load_config, project_dir  # noqa: E402

SERVER_INFO = {"name": "mepcenter-hub", "version": "1.1.0"}
SUPPORTED = ["2024-11-05", "2025-03-26", "2025-06-18"]

LOCAL_TOOLS = [
    {
        "name": "hub_upload",
        "description": "Yerel bir dosyayı hub'a yükler (bağlı olunan görev koduna). Diğer makinelerdeki Claude'lar görebilir/indirebilir.",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "note": {"type": "string"}},
                        "required": ["path"]},
    },
    {
        "name": "hub_download",
        "description": "Hub'daki bir dosyayı bu bilgisayara indirir (id: hub_files'tan). dest verilmezse "
                       "proje klasöründe dosyanın orijinal yoluna kaydeder; var olan dosyanın üzerine yazmak için overwrite=true.",
        "inputSchema": {"type": "object", "properties": {"id": {"type": "integer"}, "dest": {"type": "string"},
                                                         "overwrite": {"type": "boolean"}},
                        "required": ["id"]},
    },
]

_remote_tools = None
_instructions = None


def remote_tools():
    global _remote_tools, _instructions
    if _remote_tools is None:
        res = api("tools", timeout=10)
        _remote_tools = res["tools"]
        _instructions = res.get("instructions")
    return _remote_tools


def local_tool(name, a):
    cwd = project_dir()
    if name == "hub_upload":
        path = os.path.abspath(os.path.join(cwd, os.path.expanduser(a["path"])))
        with open(path, "rb") as f:
            data = f.read()
        try:
            inside = os.path.commonpath([path, cwd]) == cwd
        except ValueError:
            inside = False
        rel = os.path.relpath(path, cwd) if inside else os.path.basename(path)
        res = api("upload", {"name": os.path.basename(path), "rel_path": rel.replace("\\", "/"), "note": a.get("note", ""),
                             "content_b64": base64.b64encode(data).decode("ascii")}, cwd=cwd, timeout=180)
        return json.dumps(res, ensure_ascii=False)
    if name == "hub_download":
        res = api("file_get", params={"id": a["id"]}, cwd=cwd, timeout=180)
        dest = a.get("dest") or res.get("rel_path") or res["name"]
        dest = os.path.abspath(os.path.join(cwd, os.path.expanduser(dest)))
        if os.path.exists(dest) and not a.get("overwrite"):
            return f"Hata: {dest} zaten var. Üzerine yazmak için overwrite=true ya da başka bir dest ver."
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(base64.b64decode(res["content_b64"]))
        return json.dumps({"ok": True, "saved_to": dest, "size": res["size"]}, ensure_ascii=False)
    return None


def handle(msg):
    method = msg.get("method")
    mid = msg.get("id")
    if "id" not in msg:
        return None
    if method == "initialize":
        want = (msg.get("params") or {}).get("protocolVersion")
        try:
            remote_tools()
        except HubError:
            pass
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": want if want in SUPPORTED else SUPPORTED[-1],
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": SERVER_INFO,
            "instructions": _instructions or "MepCenter Hub: kullanıcının tüm Claude oturumlarının ortak hafızası. "
                                             "Görev kodu söylenince hub_set_project çağır.",
        }}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if method == "tools/list":
        try:
            tools = remote_tools()
        except HubError:
            tools = []
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": tools + LOCAL_TOOLS}}
    if method == "tools/call":
        p = msg.get("params") or {}
        name, args = p.get("name"), p.get("arguments") or {}
        try:
            text = local_tool(name, args)
            if text is None:
                text = api("tool_call", {"name": name, "arguments": args}, timeout=70)["text"]
            err = text.startswith("Hata:")
        except (HubError, OSError, KeyError, ValueError) as e:
            text, err = f"Hata: {e}", True
        return {"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": text}], "isError": err}}
    if method in ("resources/list", "prompts/list"):
        key = method.split("/")[0]
        return {"jsonrpc": "2.0", "id": mid, "result": {key: []}}
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Desteklenmeyen metot: {method}"}}


def main():
    stdin = open(sys.stdin.fileno(), "r", encoding="utf-8", newline="\n", closefd=False)
    stdout = open(sys.stdout.fileno(), "w", encoding="utf-8", newline="\n", closefd=False)
    load_config()
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        batch = isinstance(msg, list)
        replies = [r for r in (handle(m) for m in (msg if batch else [msg])) if r is not None]
        if replies:
            stdout.write(json.dumps(replies if batch else replies[0], ensure_ascii=False) + "\n")
            stdout.flush()


if __name__ == "__main__":
    main()
