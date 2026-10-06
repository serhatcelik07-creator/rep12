"""MepCenter Claude Hub - ortak istemci (yalnızca Python standart kütüphanesi).

Ayarlar ~/.mepcenter/config.json dosyasından okunur. Ortam değişkenleri
(MEPCENTER_URL, MEPCENTER_TOKEN, MEPCENTER_MACHINE) dosyadakini ezer.
"""

import json
import os
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".mepcenter")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "url": "https://mepcenter.com.tr/claude/",
    "token": "",
    "machine": socket.gethostname(),
    "auto_log": True,         # her cevaptan sonra konuşmanın TAMAMINI (araçlar, kodlar, çıktılar) hub'a yaz
    "auto_upload": True,      # Claude'un yazdığı/düzenlediği dosyaları yükle
    "max_upload_kb": 2048,
    "inject_sessions_on_start": True,
    # Bu kalıplara uyan dosyalar ASLA yüklenmez (gizli bilgi koruması)
    "exclude": [
        ".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "id_rsa*", "id_ed25519*",
        "*secret*", "*password*", "*sifre*", "*credential*", "config.php", ".npmrc", ".pypirc",
        "*.sqlite", "*.db", "*.zip", "*.exe", "*.dll",
        "node_modules/*", ".git/*", "vendor/*", "__pycache__/*", ".venv/*", "venv/*",
    ],
}


class HubError(Exception):
    pass


def load_config():
    cfg = dict(DEFAULTS)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    except FileNotFoundError:
        pass
    for env, key in (("MEPCENTER_URL", "url"), ("MEPCENTER_TOKEN", "token"), ("MEPCENTER_MACHINE", "machine")):
        if os.environ.get(env):
            cfg[key] = os.environ[env]
    url = cfg["url"].rstrip("/")
    if url.endswith("/api") or url.endswith("/mcp"):
        url = url[:-4]
    cfg["url"] = url + "/"
    return cfg


def _ssl_context():
    try:
        import certifi  # varsa (özellikle macOS python.org kurulumlarında işe yarar)
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def project_dir(cwd=None):
    return os.path.abspath(cwd or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def api(r, data=None, params=None, cwd=None, cfg=None, timeout=15, raw=False):
    """Hub API çağrısı. data verilirse POST (JSON), yoksa GET."""
    cfg = cfg or load_config()
    if not cfg.get("token"):
        raise HubError("Bu bilgisayar hub'a kayıtlı değil. kur.py ile kurulum yapın.")
    cwd = project_dir(cwd)
    query = {"r": r}
    query.update({k: v for k, v in (params or {}).items() if v is not None})
    url = cfg["url"] + "api/?" + urllib.parse.urlencode(query)
    headers = {
        "X-Hub-Token": cfg["token"],
        "Authorization": "Bearer " + cfg["token"],
        "X-Hub-Machine": _ascii_header(cfg["machine"]),
        "X-Hub-Project": _ascii_header(os.path.basename(cwd.rstrip("/\\")) or cwd),
        "X-Hub-Cwd": _ascii_header(cwd),
        "X-Hub-Client-Key": _ascii_header(cfg["machine"] + "|" + cwd),
        "User-Agent": "mepcenter-claude-hub/1.0",
        "Accept": "application/json",
    }
    body = None
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as resp:
            payload = resp.read()
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode("utf-8")).get("error", str(e))
        except Exception:
            msg = str(e)
        raise HubError(f"Hub hatası ({e.code}): {msg}")
    except ssl.SSLError as e:
        raise HubError(f"SSL hatası: {e}. macOS'ta 'Install Certificates.command' çalıştırın veya 'pip install certifi'.")
    except (urllib.error.URLError, socket.timeout, OSError) as e:
        raise HubError(f"Hub'a ulaşılamadı: {e}")
    if raw:
        return payload
    try:
        result = json.loads(payload.decode("utf-8"))
    except ValueError:
        raise HubError("Hub geçersiz yanıt döndürdü: " + payload[:200].decode("utf-8", "replace"))
    if not result.get("ok"):
        raise HubError(result.get("error", "bilinmeyen hata"))
    return result


def _ascii_header(value):
    """HTTP başlıkları ASCII olmalı; Türkçe karakterleri yüzde-kodla."""
    value = str(value)
    try:
        value.encode("ascii")
        return value
    except UnicodeEncodeError:
        return urllib.parse.quote(value, safe="/\\:|._- ")


def register(cfg, user, password, machine, timeout=20):
    """Panel kullanıcı adı/şifresiyle bu bilgisayarı kaydeder; bağlantı anahtarını döndürür."""
    url = cfg["url"] + "api/?r=register"
    body = json.dumps({"user": user, "pass": password, "machine": machine}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json; charset=utf-8", "Accept": "application/json",
        "User-Agent": "mepcenter-claude-hub/1.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as resp:
            res = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode("utf-8")).get("error", str(e))
        except Exception:
            msg = str(e)
        raise HubError(_old_server_hint(msg))
    except ssl.SSLError as e:
        raise HubError(f"SSL hatası: {e}. macOS'ta 'Install Certificates.command' çalıştırın veya 'pip install certifi'.")
    except (urllib.error.URLError, socket.timeout, OSError, ValueError) as e:
        raise HubError(f"Hub'a ulaşılamadı ({cfg['url']}): {e}")
    if not res.get("ok"):
        raise HubError(res.get("error", "bilinmeyen hata"))
    return res


def _old_server_hint(msg):
    if "Token gerekli" in msg:
        return ("Sunucudaki dosyalar ESKİ sürüm. Son gönderilen claude.zip'i cPanel'de public_html içinde açıp "
                "eskilerin üzerine yazın, sonra kurulumu tekrar çalıştırın. (Kontrol: tarayıcıda "
                "mepcenter.com.tr/claude/api/?r=register adresi 'POST gerekli' demeli.)")
    return msg
