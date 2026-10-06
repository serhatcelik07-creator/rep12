#!/usr/bin/env python3
"""MepCenter Claude Hub - KÖPRÜ AJANI (7/24).

Bilgisayar açılınca başlar, mepcenter.com.tr/claude hub'ına sürekli bağlı kalır.
Panelden (Sohbet sayfasında bu makinenin "köprü" oturumuna) yazdığınız her mesajı
bu bilgisayardaki Claude Code'a iletir (claude -p), cevabı panele geri yazar.
Konuşma sürer: sonraki mesajlar aynı Claude oturumunda devam eder.

Panelden kullanılabilecek komutlar:
  /durum          köprünün durumu (makine, klasör, çalışan iş)
  /yeni           yeni bir Claude konuşması başlat
  /klasor YOL     Claude'un çalışacağı klasörü değiştir
  /iptal          çalışan işi durdur
  /yardim         bu liste

Ayarlar (~/.mepcenter/config.json içindeki "kopru" bölümü):
  workdir          Claude'un çalışacağı klasör (varsayılan: ev klasörü)
  permission_mode  "default" | "acceptEdits" | "bypassPermissions"  (varsayılan: acceptEdits)
  allowed_tools    izin verilen araçlar (permission_mode=default iken önemli)
  accept_from      ["admin"] -> yalnızca panelden gelen mesajlar iş başlatır;
                   ["admin", "claude"] -> diğer Claude'ların mesajları da iş başlatır
  timeout_min      bir işin en uzun süresi (dakika, varsayılan 30)
  prevent_sleep    true -> köprü çalışırken bilgisayarın uykuya geçmesini engelle
  claude_path      claude komutunun tam yolu (kur.py otomatik bulur)
  model            isteğe bağlı model adı
"""

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hub_client import CONFIG_DIR, HubError, api, load_config  # noqa: E402

STATE_FILE = os.path.join(CONFIG_DIR, "kopru_state.json")
KOPRU_DIR = os.path.join(CONFIG_DIR, "kopru")  # hub'da bu makinenin "kopru" oturumu olarak görünür
LOCK_PORT = 47613

DEFAULTS = {
    "workdir": "~",
    "permission_mode": "acceptEdits",
    "allowed_tools": ["Read", "Grep", "Glob", "LS", "WebSearch", "WebFetch", "TodoWrite", "mcp__mepcenter"],
    "accept_from": ["admin"],
    "timeout_min": 30,
    "prevent_sleep": False,
    "claude_path": "",
    "model": "",
}

PROMPT_PREFIX = ("[Bu istek kullanıcının MepCenter panelinden köprü ajanı üzerinden geldi. Kullanıcı şu an bu "
                 "bilgisayarın başında olmayabilir; senin cevabın panele metin olarak iletilecek. Onay gerektiren "
                 "riskli işlemleri yapmadan önce sor; cevabını net ve özet yaz.]\n\n")


def log(*a):
    print(time.strftime("%Y-%m-%d %H:%M:%S"), *a, flush=True)


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(st):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False)


def keep_awake():
    """Bilgisayarın boşta uykuya geçmesini engelle (ekran kapanabilir)."""
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["caffeinate", "-i", "-w", str(os.getpid())])
        elif os.name == "nt":
            import ctypes
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)  # CONTINUOUS | SYSTEM_REQUIRED
    except Exception as e:  # noqa: BLE001
        log("uyku engellenemedi:", e)


class Kopru:
    def __init__(self):
        self.cfg = load_config()
        self.k = dict(DEFAULTS)
        self.k.update(self.cfg.get("kopru") or {})
        self.state = load_state()
        self.state.setdefault("workdir", os.path.expanduser(self.k["workdir"]))
        self.claude = self.k["claude_path"] or shutil.which("claude") or ""
        self.proc = None
        self.job_text = ""
        self.job_started = 0.0
        self.queue = []
        self.lock = threading.Lock()
        self.started = time.time()
        os.makedirs(KOPRU_DIR, exist_ok=True)

    # --- hub yardımcıları ---------------------------------------------------
    def call(self, r, data=None, params=None, timeout=20):
        return api(r, data, params, cwd=KOPRU_DIR, cfg=self.cfg, timeout=timeout)

    def reply(self, body, to="admin"):
        try:
            self.call("send", {"to": to, "topic": "köprü", "body": body})
        except HubError as e:
            log("cevap gönderilemedi:", e)

    def status(self, text):
        try:
            self.call("status", {"status": text})
        except HubError:
            pass

    def idle_status(self):
        self.status(f"🟢 Köprü hazır ({self.cfg['machine']}) — klasör: {self.state['workdir']}. Panelden yazın.")

    # --- komutlar -------------------------------------------------------------
    def command(self, text, to):
        parts = text.strip().split(None, 1)
        cmd, rest = parts[0].lower(), (parts[1].strip() if len(parts) > 1 else "")
        if cmd in ("/durum", "/status"):
            job = (f"Çalışan iş ({int(time.time() - self.job_started)} sn): {self.job_text[:200]}"
                   if self.proc else "Çalışan iş yok.")
            self.reply(f"Makine: {self.cfg['machine']} ({platform.system()} {platform.release()})\n"
                       f"Klasör: {self.state['workdir']}\nClaude konuşması: {self.state.get('claude_session') or 'yeni'}\n"
                       f"İzin modu: {self.k['permission_mode']}\n{job}\nKuyruk: {len(self.queue)} mesaj\n"
                       f"Çalışma süresi: {int((time.time() - self.started) / 60)} dk", to)
        elif cmd in ("/yeni", "/new"):
            self.state.pop("claude_session", None)
            save_state(self.state)
            self.reply("Yeni Claude konuşması başlatılacak.", to)
        elif cmd in ("/klasor", "/klasör", "/cd"):
            path = os.path.abspath(os.path.expanduser(rest or "~"))
            if os.path.isdir(path):
                self.state["workdir"] = path
                self.state.pop("claude_session", None)  # klasör değişince konuşma da yenilenir
                save_state(self.state)
                self.idle_status()
                self.reply(f"Klasör: {path} (yeni konuşma)", to)
            else:
                self.reply(f"Klasör bulunamadı: {path}", to)
        elif cmd in ("/iptal", "/cancel"):
            if self.proc:
                self.proc.kill()
                self.reply("Çalışan iş durduruldu.", to)
            else:
                self.reply("Çalışan iş yok.", to)
        else:
            self.reply(__doc__.split("Panelden kullanılabilecek komutlar:")[1].split("Ayarlar")[0].strip(), to)

    # --- Claude çalıştırma ----------------------------------------------------
    def run_claude(self, text, to):
        if not self.claude:
            self.reply("Bu bilgisayarda 'claude' komutu bulunamadı. Claude Code'u kurun veya config.json > "
                       "kopru.claude_path ayarlayın.", to)
            return
        self.job_text, self.job_started = text, time.time()
        self.status(f"⏳ Çalışıyor: {' '.join(text.split())[:150]}")
        self.reply("⏳ Aldım, çalışıyorum…", to)

        def build(resume):
            cmd = [self.claude, "-p", PROMPT_PREFIX + text, "--output-format", "json",
                   "--permission-mode", self.k["permission_mode"]]
            if self.k.get("allowed_tools"):
                cmd += ["--allowedTools", ",".join(self.k["allowed_tools"])]
            if self.k.get("model"):
                cmd += ["--model", self.k["model"]]
            if resume:
                cmd += ["--resume", resume]
            return cmd

        resume = self.state.get("claude_session")
        out, err, code = self._exec(build(resume))
        if code != 0 and resume and "session" in (err + out).lower():
            log("önceki konuşma bulunamadı, yeni konuşma açılıyor")
            out, err, code = self._exec(build(None))

        took = int(time.time() - self.job_started)
        try:
            res = json.loads(out.strip().splitlines()[-1]) if out.strip() else {}
        except ValueError:
            res = {}
        if res.get("session_id"):
            self.state["claude_session"] = res["session_id"]
            save_state(self.state)
        body = res.get("result") or (out.strip() or err.strip() or f"(çıktı yok, çıkış kodu {code})")
        if code == -9:
            body = "⛔ İş durduruldu ya da zaman aşımına uğradı.\n\n" + body
        elif code != 0 or res.get("is_error"):
            body = "⚠️ Claude hata verdi:\n" + body
        cost = f", maliyet ${res['total_cost_usd']:.3f}" if isinstance(res.get("total_cost_usd"), (int, float)) else ""
        self.reply(f"{body[:60000]}\n\n— {self.cfg['machine']} · {took} sn{cost}", to)
        self.job_text = ""

    def _exec(self, cmd):
        log("çalıştırılıyor:", " ".join(cmd[:2]), "…")
        kw = {}
        if os.name == "nt":
            kw["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
        try:
            self.proc = subprocess.Popen(cmd, cwd=self.state["workdir"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace", **kw)
            out, err = self.proc.communicate(timeout=int(self.k["timeout_min"]) * 60)
            code = self.proc.returncode
            if code is not None and code < 0:
                code = -9
        except subprocess.TimeoutExpired:
            self.proc.kill()
            out, err = self.proc.communicate()
            code = -9
        except OSError as e:
            out, err, code = "", str(e), 1
        finally:
            self.proc = None
        return out, err, code

    def worker(self):
        while True:
            with self.lock:
                item = self.queue.pop(0) if self.queue else None
            if item is None:
                time.sleep(0.5)
                continue
            try:
                self.run_claude(*item)
            except Exception as e:  # noqa: BLE001
                log("iş hatası:", e)
                self.reply(f"⚠️ Köprü hatası: {e}", item[1])
            if not self.queue:
                self.idle_status()

    # --- ana döngü --------------------------------------------------------------
    def accepts(self, m):
        if m["from_session_id"] is None:
            return "admin" in self.k["accept_from"] and m["to_type"] == "session"
        return "claude" in self.k["accept_from"] and m["to_type"] == "session"

    def run(self):
        if self.k.get("prevent_sleep"):
            keep_awake()
        threading.Thread(target=self.worker, daemon=True).start()
        backoff = 5
        announced = False
        while True:
            try:
                if not announced:
                    self.idle_status()
                    announced = True
                    log("hub'a bağlandı")
                msgs = self.call("wait", params={"timeout": 25}, timeout=60)["messages"]
                backoff = 5
            except HubError as e:
                log("hub'a ulaşılamadı:", e, f"({backoff} sn sonra tekrar)")
                announced = False
                time.sleep(backoff)
                backoff = min(backoff * 2, 300)
                continue
            for m in msgs:
                text = (m.get("body") or "").strip()
                to = "admin" if m["from_session_id"] is None else f"session:{m['from_session_id']}"
                if text.startswith("/"):
                    if m["to_type"] == "session" or text.split()[0].lower() in ("/durum", "/status"):
                        self.command(text, to)
                elif self.accepts(m):
                    with self.lock:
                        self.queue.append((text, to))
                    if self.proc or len(self.queue) > 1:
                        self.reply(f"Sıraya alındı ({len(self.queue)}. sırada). Çalışan işi durdurmak için /iptal.", to)


def main():
    # Tek kopya: aynı anda yalnızca bir köprü çalışsın
    lock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        lock.bind(("127.0.0.1", LOCK_PORT))
    except OSError:
        log("Köprü zaten çalışıyor, çıkılıyor.")
        return
    cfg = load_config()
    if not cfg.get("token"):
        log("Token yok; önce kur.py ile kurulum yapın.")
        return
    log(f"MepCenter köprü ajanı başlıyor: {cfg['machine']} -> {cfg['url']}")
    with open(os.path.join(CONFIG_DIR, "kopru.pid"), "w") as f:
        f.write(str(os.getpid()))
    Kopru().run()


if __name__ == "__main__":
    main()
