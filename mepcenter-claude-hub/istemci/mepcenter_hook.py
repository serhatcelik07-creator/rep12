#!/usr/bin/env python3
"""MepCenter Claude Hub - Claude Code hook'ları.

Kullanım (settings.json içinden): python mepcenter_hook.py <olay>
  start    SessionStart     : oturumu kaydeder; diğer oturumları ve okunmamış mesajları Claude'a gösterir
  prompt   UserPromptSubmit : "kod matwar" / "proje kodu: matwar" / "matwar görevine bak" yakalanırsa
                              oturumu o göreve bağlar ve görevin tüm özetini Claude'a verir;
                              okunmamış hub mesajlarını Claude'a gösterir
  stop     Stop             : bu turun TAM kaydını (istek, cevaplar, tüm araç çağrıları, kodlar,
                              komut çıktıları) hub'a yazar ve durumu günceller
  file     PostToolUse      : Claude'un yazdığı/düzenlediği dosyayı hub'a yükler
  end      SessionEnd / PreCompact : kalan kaydı yazar, ham konuşma dökümünü (jsonl) yükler

Hook hiçbir zaman Claude'u engellemez: her hata ~/.mepcenter/hook.log'a yazılır, çıkış kodu 0'dır.
"""

import base64
import fnmatch
import gzip
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hub_client import CONFIG_DIR, api, load_config  # noqa: E402

LOG_FILE = os.path.join(CONFIG_DIR, "hook.log")
STATE_FILE = os.path.join(CONFIG_DIR, "state.json")

MAX_FIELD = 60000        # tek bir araç girdisi/çıktısı için üst sınır (karakter)
MAX_CHUNK = 1500000      # tek kayıt için üst sınır

CODE = r"([A-Za-z0-9][A-Za-z0-9._/-]{0,59})"
CODE_PATTERNS = [
    re.compile(r"(?:proje|görev|gorev|project)\s*kod[uü]?\s*[:=]?\s*" + CODE, re.I),
    re.compile(r"\bkod\s*[:=]\s*" + CODE, re.I),
    re.compile(r"^\s*kod\s+" + CODE + r"(?=[\s,.;:!?]|$)", re.I | re.M),
    re.compile(r"\b" + CODE + r"\s+(?:görevine|gorevine|projesine|görevi|projesi)\b", re.I),
    re.compile(r"#(?:görev|gorev|proje)[:\s]+" + CODE, re.I),
]
STOPWORDS = {"bu", "şu", "su", "o", "bir", "yeni", "ne", "nedir", "hangi", "the", "this", "kod", "kodu", "bak", "ile",
             "yaz", "yazar", "ekle", "var", "yok", "nasil", "neden", "icin", "de", "da", "ve", "mi", "olarak", "is",
             "a", "an", "and", "to", "for", "of", "in", "on", "review", "block", "blok", "satir"}

SECRET_PATTERNS = [
    re.compile(r"\b(mch_[a-f0-9]{20,})"),
    re.compile(r"\b(sk-[A-Za-z0-9_-]{20,})"),
    re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,})"),
    re.compile(r"\b(AKIA[0-9A-Z]{16})\b"),
    re.compile(r"\b(xox[abpr]-[A-Za-z0-9-]{10,})"),
    re.compile(r"((?:password|passwd|pwd|şifre|sifre|secret|api[_-]?key|token)\s*[:=]\s*)(['\"]?)([^\s'\"]{4,})", re.I),
]


def redact(text):
    for pat in SECRET_PATTERNS:
        if pat.groups >= 3:
            text = pat.sub(lambda m: m.group(1) + m.group(2) + "***GİZLENDİ***", text)
        else:
            text = pat.sub("***GİZLENDİ***", text)
    return text


def log_error(event, err):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 512 * 1024:
            os.remove(LOG_FILE)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [{event}] {err}\n")
    except OSError:
        pass


def emit(text):
    if text:
        out = open(sys.stdout.fileno(), "w", encoding="utf-8", closefd=False)
        out.write(text + "\n")
        out.flush()


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(st):
    # Eski kayıtları temizle (30 günden eski)
    cutoff = time.time() - 30 * 86400
    st = {k: v for k, v in st.items() if isinstance(v, dict) and v.get("t", 0) > cutoff}
    os.makedirs(CONFIG_DIR, exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f)
    os.replace(tmp, STATE_FILE)


def cut(s, n=MAX_FIELD):
    s = str(s)
    return s if len(s) <= n else s[:n] + f"\n…[{len(s) - n} karakter kesildi]"


def text_of(content):
    if isinstance(content, str):
        return content
    parts = []
    for b in content or []:
        if isinstance(b, dict):
            if b.get("type") == "text":
                parts.append(b.get("text", ""))
            elif b.get("type") == "image":
                parts.append("[görsel]")
    return "\n".join(parts)


def fmt_tool_input(name, inp):
    """Araç girdisini okunur biçimde yaz; kod içeren alanları kod bloğu olarak ver."""
    if not isinstance(inp, dict):
        return "```\n" + cut(inp) + "\n```"
    lines = []
    if name in ("Write",) and "content" in inp:
        lines.append(f"Dosya: `{inp.get('file_path', '')}`\n```\n{cut(inp['content'])}\n```")
    elif name in ("Edit",) and "new_string" in inp:
        lines.append(f"Dosya: `{inp.get('file_path', '')}`" + (" (tümü)" if inp.get("replace_all") else ""))
        lines.append(f"Eski:\n```\n{cut(inp.get('old_string', ''))}\n```\nYeni:\n```\n{cut(inp['new_string'])}\n```")
    elif name == "MultiEdit" and "edits" in inp:
        lines.append(f"Dosya: `{inp.get('file_path', '')}`")
        for i, e in enumerate(inp.get("edits") or [], 1):
            lines.append(f"Değişiklik {i} — Eski:\n```\n{cut(e.get('old_string', ''))}\n```\nYeni:\n```\n{cut(e.get('new_string', ''))}\n```")
    elif name == "Bash" and "command" in inp:
        lines.append(("_" + inp["description"] + "_\n" if inp.get("description") else "") + f"```bash\n{cut(inp['command'])}\n```")
    else:
        lines.append("```json\n" + cut(json.dumps(inp, ensure_ascii=False, indent=1)) + "\n```")
    return "\n".join(lines)


def fmt_tool_result(block):
    c = block.get("content")
    text = text_of(c) if not isinstance(c, str) else c
    flag = " (HATA)" if block.get("is_error") else ""
    return f"Sonuç{flag}:\n```\n{cut(text, 20000)}\n```"


def format_entries(entries):
    """Transcript satırlarını okunur Markdown'a çevirir. (başlık, metin, son istek) döner."""
    out, title, last_prompt = [], "", ""
    for e in entries:
        t = e.get("type")
        if t not in ("user", "assistant") or e.get("isSidechain"):
            continue
        msg = e.get("message") or {}
        content = msg.get("content")
        ts = (e.get("timestamp") or "")[:19].replace("T", " ")
        if t == "user":
            if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        out.append(fmt_tool_result(b))
                continue
            text = text_of(content).strip()
            if not text or e.get("isMeta"):
                continue
            last_prompt = text
            if not title:
                title = " ".join(text.split())[:150]
            out.append(f"\n### 👤 Kullanıcı · {ts}\n{text}")
        else:
            for b in content or []:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text" and b.get("text", "").strip():
                    out.append(f"\n### 🤖 Claude · {ts}\n{b['text'].strip()}")
                elif b.get("type") == "tool_use":
                    out.append(f"\n#### 🔧 {b.get('name')}\n" + fmt_tool_input(b.get("name"), b.get("input")))
    return title, "\n".join(out).strip(), last_prompt


def read_new_entries(path, st_key, st):
    done = int((st.get(st_key) or {}).get("lines", 0))
    entries, n = [], 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for n, line in enumerate(f, 1):
            if n <= done:
                continue
            try:
                entries.append(json.loads(line))
            except ValueError:
                continue
    if n < done:  # dosya yeniden yazılmış (ör. sıkıştırma) - baştan oku
        st[st_key] = {"lines": 0, "t": time.time()}
        return read_new_entries(path, st_key, st)
    return entries, n


def log_transcript(data, cfg, cwd, final=False):
    path = data.get("transcript_path")
    if not cfg.get("auto_log", True) or not path or not os.path.isfile(path):
        return None
    st = load_state()
    key = "tr:" + path
    entries, total = read_new_entries(path, key, st)
    title, body, last_prompt = format_entries(entries)
    if body:
        body = redact(body)
        if len(body) > MAX_CHUNK:
            body = body[:MAX_CHUNK] + "\n…[kayıt çok uzun, kesildi; tam döküm oturum sonunda dosya olarak yüklenir]"
        api("topic_add", {"kind": "conversation", "title": title or "(devam)", "content": body}, cwd=cwd, cfg=cfg, timeout=60)
    st[key] = {"lines": total, "t": time.time()}
    save_state(st)
    return last_prompt


def upload_raw_transcript(data, cfg, cwd):
    path = data.get("transcript_path")
    if not cfg.get("auto_log", True) or not path or not os.path.isfile(path):
        return
    with open(path, "rb") as f:
        raw = f.read()
    raw = redact(raw.decode("utf-8", "replace")).encode("utf-8")
    gz = gzip.compress(raw)
    sid = data.get("session_id") or os.path.splitext(os.path.basename(path))[0]
    api("upload", {"name": f"{sid}.jsonl.gz", "rel_path": f".claude-transcripts/{sid}.jsonl.gz",
                   "note": "ham konuşma dökümü", "content_b64": base64.b64encode(gz).decode("ascii")},
        cwd=cwd, cfg=cfg, timeout=120)


def detect_code(prompt):
    for pat in CODE_PATTERNS:
        m = pat.search(prompt)
        if m and m.group(1).lower() not in STOPWORDS:
            return m.group(1).rstrip(".,;:!?")
    return None


def excluded(rel_path, patterns):
    rel = rel_path.replace("\\", "/").lower()
    name = os.path.basename(rel)
    for pat in patterns:
        pat = pat.lower()
        if fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(rel, pat):
            return True
        if pat.endswith("/*") and ("/" + rel).find("/" + pat[:-1]) >= 0:
            return True
    return False


def main():
    event = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        data = json.load(open(sys.stdin.fileno(), "r", encoding="utf-8", closefd=False))
    except Exception:
        data = {}
    cfg = load_config()
    if not cfg.get("token"):
        return
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

    try:
        if event == "start":
            if data.get("source") in (None, "startup", "clear"):
                api("project_set", {"code": ""}, cwd=cwd, cfg=cfg, timeout=6)  # yeni konuşma: görev kodu sıfırlanır
            res = api("context", params={"sessions": "1" if cfg.get("inject_sessions_on_start", True) else "0"},
                      cwd=cwd, cfg=cfg, timeout=6)
            code = res.get("project_code")
            head = (f"[MepCenter Hub] Bu oturum hub'a #{res['session_id']} olarak bağlandı (makine: {cfg['machine']}). "
                    f"Kullanıcının diğer bilgisayarlarındaki ve claude.ai'deki Claude'larla mepcenter MCP araçları "
                    f"(hub_set_project, hub_sessions, hub_send, hub_project_update, hub_log...) üzerinden çalışırsın. ")
            head += (f"Bağlı görev: {code}." if code else
                     "Henüz görev kodu yok: kullanıcı 'kod XXX' / 'XXX görevine bak' deyince hub_set_project ile bağlan.")
            emit(head + ("\n" + res["text"] if res.get("text") else ""))

        elif event == "prompt":
            parts = []
            code = detect_code(data.get("prompt") or "")
            if code:
                text = api("tool_call", {"name": "hub_set_project", "arguments": {"code": code}}, cwd=cwd, cfg=cfg, timeout=20)["text"]
                parts.append(f"[MepCenter Hub] Kullanıcı görev kodu verdi: {code}. Hook oturumu bu göreve bağladı; "
                             f"aşağıdaki özeti oku, kullanıcıya kısaca nerede kalındığını söyle ve devam et.\n\n{text}")
            res = api("context", params={"sessions": "0"}, cwd=cwd, cfg=cfg, timeout=6)
            if res.get("text"):
                parts.append("[MepCenter Hub]\n" + res["text"])
            emit("\n\n".join(parts))

        elif event == "stop":
            last_prompt = log_transcript(data, cfg, cwd)
            if last_prompt:
                api("status", {"status": "Son istek: " + " ".join(last_prompt.split())[:200]}, cwd=cwd, cfg=cfg, timeout=6)

        elif event == "file":
            if not cfg.get("auto_upload", True):
                return
            ti = data.get("tool_input") or {}
            path = ti.get("file_path") or ti.get("notebook_path")
            if not path or not os.path.isfile(path):
                return
            path, root = os.path.abspath(path), os.path.abspath(cwd)
            try:
                inside = os.path.commonpath([path, root]) == root
            except ValueError:  # Windows'ta farklı sürücüler
                inside = False
            rel = os.path.relpath(path, root) if inside else os.path.basename(path)
            if excluded(rel, cfg.get("exclude", [])) or os.path.getsize(path) > int(cfg.get("max_upload_kb", 2048)) * 1024:
                return
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            api("upload", {"name": os.path.basename(path), "rel_path": rel.replace("\\", "/"),
                           "note": "otomatik (" + str(data.get("tool_name", "")) + ")", "content_b64": b64},
                cwd=cwd, cfg=cfg, timeout=60)

        elif event in ("end", "precompact"):
            log_transcript(data, cfg, cwd)
            upload_raw_transcript(data, cfg, cwd)
            if event == "end":
                api("end", {}, cwd=cwd, cfg=cfg, timeout=6)

    except Exception as e:  # hook asla Claude'u durdurmamalı
        log_error(event, e)


if __name__ == "__main__":
    main()
    sys.exit(0)
