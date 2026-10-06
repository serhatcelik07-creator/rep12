#!/usr/bin/env python3
"""MepCenter Claude Hub - bilgisayar kurulumu (macOS / Windows / Linux).

Ne yapar:
  1. Dosyaları ~/.mepcenter/ klasörüne kopyalar; panel kullanıcı adı/şifresiyle bilgisayarı hub'a kaydeder
     (Claude kullanımı her zaman sizin Claude aboneliğinizden düşer; API anahtarı gerekmez)
  2. Sunucuya bağlanmayı dener
  3. Claude Code'a hook'ları ekler (~/.claude/settings.json, yedek alınarak)
  4. Claude Code'a "mepcenter" MCP sunucusunu ekler (claude mcp add --scope user)
  5. İsterseniz Claude Desktop'a da MCP sunucusunu ekler
  6. ~/.claude/CLAUDE.md dosyasına kısa bir hub notu ekler
  7. İsterseniz KÖPRÜ AJANINI kurar: bilgisayar açılınca başlar, 7/24 hub'a bağlı kalır ve
     panelden yazdıklarınızı bu bilgisayardaki Claude Code'a iletir

Kullanım:  python3 kur.py            (Windows: py kur.py)
Kaldırma:  python3 kur.py --kaldir
"""

import getpass
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
DEST = os.path.join(HOME, ".mepcenter")
CLAUDE_DIR = os.path.join(HOME, ".claude")
SETTINGS = os.path.join(CLAUDE_DIR, "settings.json")
CLAUDE_MD = os.path.join(CLAUDE_DIR, "CLAUDE.md")
FILES = ["hub_client.py", "mepcenter_mcp.py", "mepcenter_hook.py", "hub_dinle.py", "hub_kopru.py"]
LAUNCH_AGENT = os.path.join(HOME, "Library", "LaunchAgents", "com.mepcenter.kopru.plist")
WIN_STARTUP = os.path.join(os.environ.get("APPDATA", HOME), "Microsoft", "Windows", "Start Menu", "Programs",
                           "Startup", "mepcenter-kopru.vbs")
SYSTEMD_UNIT = os.path.join(HOME, ".config", "systemd", "user", "mepcenter-kopru.service")
MARK_START = "<!-- mepcenter-hub:start -->"
MARK_END = "<!-- mepcenter-hub:end -->"

CLAUDE_MD_BLOCK = f"""{MARK_START}
## MepCenter Claude Hub
Bu bilgisayardaki Claude, kullanıcının diğer bilgisayarlarındaki ve claude.ai'deki Claude'larla
`mepcenter` MCP araçları üzerinden ortak çalışır (sunucu: mepcenter.com.tr/claude).
- Kullanıcı bir görev kodu söylerse ("kod matwar", "matwar görevine bak") hemen `hub_set_project` çağır,
  gelen özeti oku, nerede kalındığını kısaca söyle ve devam et.
- Anlamlı her aşamadan sonra `hub_project_update` ile görevin "son durum" notunu yeniden yaz;
  önemli kararları `hub_log` (kind=decision) ile kaydet.
- Kullanıcı "dinle" / "beklemede kal" derse: `python3 ~/.mepcenter/hub_dinle.py` komutunu ARKA PLANDA çalıştır;
  komut bittiğinde gelen mesajı yanıtla (`hub_send`, panelden geldiyse to="admin") ve dinleyiciyi yeniden başlat.
- Şifre, token, API anahtarı gibi gizli bilgileri asla hub'a yazma.
{MARK_END}"""


def ask(prompt, default=""):
    v = input(f"{prompt}{' [' + default + ']' if default else ''}: ").strip()
    return v or default


def yes(prompt, default=True):
    v = input(f"{prompt} [{'E/h' if default else 'e/H'}]: ").strip().lower()
    return default if not v else v in ("e", "evet", "y", "yes")


def py_cmd():
    """Hook komutlarında kullanılacak Python yolu (ileri eğik çizgiyle; Windows'ta Git Bash uyumlu)."""
    return sys.executable.replace("\\", "/")


def hook_cmd(event):
    return f'"{py_cmd()}" "{os.path.join(DEST, "mepcenter_hook.py").replace(chr(92), "/")}" {event}'


def backup(path):
    if os.path.exists(path):
        b = f"{path}.yedek-{time.strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(path, b)
        return b
    return None


def find_claude():
    """claude komutunu PATH'te ve bilinen kurulum klasörlerinde arar."""
    found = shutil.which("claude")
    if found:
        return found
    cands = [os.path.join(HOME, ".local", "bin", "claude"), os.path.join(HOME, ".claude", "local", "claude"),
             "/opt/homebrew/bin/claude", "/usr/local/bin/claude"]
    if os.name == "nt":
        appdata = os.environ.get("APPDATA", "")
        local = os.environ.get("LOCALAPPDATA", "")
        cands = [os.path.join(HOME, ".local", "bin", "claude.exe"), os.path.join(appdata, "npm", "claude.cmd"),
                 os.path.join(local, "Programs", "claude", "claude.exe"), os.path.join(local, "AnthropicClaude", "claude.exe")]
    for c in cands:
        if c and os.path.isfile(c):
            return c
    return ""


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def strip_our_hooks(settings):
    hooks = settings.get("hooks") or {}
    for ev in list(hooks):
        groups = []
        for g in hooks[ev]:
            g["hooks"] = [h for h in g.get("hooks", []) if "mepcenter_hook.py" not in h.get("command", "")]
            if g["hooks"]:
                groups.append(g)
        if groups:
            hooks[ev] = groups
        else:
            del hooks[ev]
    if hooks:
        settings["hooks"] = hooks
    else:
        settings.pop("hooks", None)


def install_hooks():
    settings = load_json(SETTINGS)
    b = backup(SETTINGS)
    strip_our_hooks(settings)
    hooks = settings.setdefault("hooks", {})

    def add(event, arg, matcher=None, timeout=30):
        group = {"hooks": [{"type": "command", "command": hook_cmd(arg), "timeout": timeout}]}
        if matcher:
            group["matcher"] = matcher
        hooks.setdefault(event, []).append(group)

    add("SessionStart", "start", timeout=20)
    add("UserPromptSubmit", "prompt", timeout=30)
    add("Stop", "stop", timeout=90)
    add("PostToolUse", "file", matcher="Write|Edit|MultiEdit|NotebookEdit", timeout=60)
    add("PreCompact", "precompact", timeout=120)
    add("SessionEnd", "end", timeout=120)
    save_json(SETTINGS, settings)
    print(f"  ✓ Hook'lar eklendi: {SETTINGS}" + (f" (yedek: {os.path.basename(b)})" if b else ""))


def install_mcp_claude_code():
    claude = find_claude()
    cmd_add = ["mcp", "add", "--scope", "user", "mepcenter", "--", sys.executable, os.path.join(DEST, "mepcenter_mcp.py")]
    if not claude:
        print("  ! 'claude' komutu bulunamadı. Claude Code kurulduktan sonra şunu çalıştırın:")
        print("    claude " + " ".join(f'"{c}"' if " " in c else c for c in cmd_add))
        return
    subprocess.run([claude, "mcp", "remove", "--scope", "user", "mepcenter"], capture_output=True)
    r = subprocess.run([claude] + cmd_add, capture_output=True, text=True)
    if r.returncode == 0:
        print("  ✓ Claude Code'a 'mepcenter' MCP sunucusu eklendi")
    else:
        print("  ! MCP eklenemedi:", (r.stderr or r.stdout).strip())


def desktop_config_path():
    if sys.platform == "darwin":
        return os.path.join(HOME, "Library", "Application Support", "Claude", "claude_desktop_config.json")
    if os.name == "nt":
        return os.path.join(os.environ.get("APPDATA", HOME), "Claude", "claude_desktop_config.json")
    return os.path.join(HOME, ".config", "Claude", "claude_desktop_config.json")


def install_mcp_desktop():
    path = desktop_config_path()
    if not os.path.isdir(os.path.dirname(path)):
        return
    if not yes("Claude Desktop uygulamasına da eklensin mi?"):
        return
    cfg = load_json(path)
    b = backup(path)
    cfg.setdefault("mcpServers", {})["mepcenter"] = {
        "command": sys.executable, "args": [os.path.join(DEST, "mepcenter_mcp.py")]}
    save_json(path, cfg)
    print(f"  ✓ Claude Desktop'a eklendi (uygulamayı yeniden başlatın)" + (f" (yedek: {os.path.basename(b)})" if b else ""))


def install_claude_md():
    os.makedirs(CLAUDE_DIR, exist_ok=True)
    text = ""
    if os.path.exists(CLAUDE_MD):
        with open(CLAUDE_MD, "r", encoding="utf-8") as f:
            text = f.read()
    if MARK_START in text:
        s, e = text.index(MARK_START), text.index(MARK_END) + len(MARK_END)
        text = text[:s] + CLAUDE_MD_BLOCK + text[e:]
    else:
        text = (text.rstrip() + "\n\n" if text.strip() else "") + CLAUDE_MD_BLOCK + "\n"
    with open(CLAUDE_MD, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  ✓ Hub notu eklendi: {CLAUDE_MD}")


def install_kopru(cfg, cfg_path):
    print("\nKÖPRÜ AJANI: bilgisayar açılınca başlar, 7/24 hub'a bağlı kalır; panelin Sohbet sayfasından bu")
    print("bilgisayarın 'kopru' oturumuna yazdığınız işleri buradaki Claude Code'a yaptırır ve cevabı panele yazar.")
    if not yes("Köprü ajanı kurulsun mu?"):
        return
    k = cfg.setdefault("kopru", {})
    claude = find_claude() or k.get("claude_path", "")
    if not claude:
        print("  ! Bu bilgisayarda Claude Code (claude komutu) bulunamadı. Claude Code'u kurduktan sonra bu kurulumu")
        print("    tekrar çalıştırın; köprü o zaman çalışır. (Şimdilik Enter'a basabilirsiniz.)")
        claude = ask("claude komutunun tam yolu (bilmiyorsanız Enter)", "")
    k["claude_path"] = claude
    k["workdir"] = ask("Claude hangi klasörde çalışsın", k.get("workdir") or os.path.join(HOME))
    print("İzin modu: 1) Dosya okur/düzenler, komut çalıştırmaz (önerilen)  2) Sadece okur  3) Her şeye izinli (riskli)")
    choice = ask("Seçim", {"default": "2", "bypassPermissions": "3"}.get(k.get("permission_mode"), "1"))
    k["permission_mode"] = {"2": "default", "3": "bypassPermissions"}.get(choice, "acceptEdits")
    k["prevent_sleep"] = yes("Köprü çalışırken bilgisayar uykuya geçmesin mi? (7/24 erişim için önerilir)", True)
    save_json(cfg_path, cfg)

    stop_running_kopru()  # eski sürüm çalışıyorsa durdur; yenisi aşağıda başlatılır
    py = sys.executable
    script = os.path.join(DEST, "hub_kopru.py")
    logf = os.path.join(DEST, "kopru.log")
    if sys.platform == "darwin":
        path_env = ":".join(dict.fromkeys(filter(None, [os.path.dirname(claude) if claude else "",
                                                        os.path.dirname(py), "/opt/homebrew/bin", "/usr/local/bin",
                                                        "/usr/bin", "/bin", "/usr/sbin", "/sbin"])))
        plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.mepcenter.kopru</string>
  <key>ProgramArguments</key><array><string>{py}</string><string>{script}</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>30</integer>
  <key>StandardOutPath</key><string>{logf}</string>
  <key>StandardErrorPath</key><string>{logf}</string>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>{path_env}</string>
    <key>HOME</key><string>{HOME}</string>
    <key>LANG</key><string>tr_TR.UTF-8</string>
  </dict>
</dict></plist>
"""
        os.makedirs(os.path.dirname(LAUNCH_AGENT), exist_ok=True)
        subprocess.run(["launchctl", "unload", LAUNCH_AGENT], capture_output=True)
        with open(LAUNCH_AGENT, "w", encoding="utf-8") as f:
            f.write(plist)
        subprocess.run(["launchctl", "load", "-w", LAUNCH_AGENT], capture_output=True)
        print(f"  ✓ Köprü kuruldu ve başlatıldı (LaunchAgent). Günlük: {logf}")
    elif os.name == "nt":
        pyw = py  # pencere, aşağıdaki Run(..., 0) ile gizlenir
        # Pencere açmadan çalıştır, çıktıyı günlüğe yaz
        vbs = (f'Set sh = CreateObject("WScript.Shell")\r\n'
               f'sh.Run "cmd /c """"{pyw}"" ""{script}"" >> ""{logf}"" 2>&1""", 0, False\r\n')
        os.makedirs(os.path.dirname(WIN_STARTUP), exist_ok=True)
        with open(WIN_STARTUP, "w", encoding="utf-8") as f:
            f.write(vbs)
        subprocess.Popen(["wscript", WIN_STARTUP])
        print(f"  ✓ Köprü kuruldu (Başlangıç klasörü) ve başlatıldı. Günlük: {logf}")
    else:
        unit = f"""[Unit]
Description=MepCenter Claude Hub kopru ajani
After=network-online.target

[Service]
ExecStart={py} {script}
Restart=always
RestartSec=30
Environment=PATH={os.path.dirname(claude) if claude else ''}:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=default.target
"""
        os.makedirs(os.path.dirname(SYSTEMD_UNIT), exist_ok=True)
        with open(SYSTEMD_UNIT, "w", encoding="utf-8") as f:
            f.write(unit)
        subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)
        subprocess.run(["systemctl", "--user", "enable", "--now", "mepcenter-kopru"], capture_output=True)
        print("  ✓ Köprü kuruldu (systemd --user). Durum: systemctl --user status mepcenter-kopru")


def stop_running_kopru():
    pid_file = os.path.join(DEST, "kopru.pid")
    try:
        with open(pid_file) as f:
            pid = int(f.read().strip())
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
        else:
            os.kill(pid, 15)
        os.remove(pid_file)
        time.sleep(1)
        print("  ✓ Çalışan eski köprü durduruldu")
    except (OSError, ValueError):
        pass


def uninstall_kopru():
    stop_running_kopru()
    if os.path.exists(LAUNCH_AGENT):
        subprocess.run(["launchctl", "unload", LAUNCH_AGENT], capture_output=True)
        os.remove(LAUNCH_AGENT)
        print("  ✓ Köprü (LaunchAgent) kaldırıldı")
    if os.path.exists(WIN_STARTUP):
        os.remove(WIN_STARTUP)
        print("  ✓ Köprü (Başlangıç) kaldırıldı")
    if os.path.exists(SYSTEMD_UNIT):
        subprocess.run(["systemctl", "--user", "disable", "--now", "mepcenter-kopru"], capture_output=True)
        os.remove(SYSTEMD_UNIT)
        print("  ✓ Köprü (systemd) kaldırıldı")


def uninstall():
    uninstall_kopru()
    settings = load_json(SETTINGS)
    if settings:
        backup(SETTINGS)
        strip_our_hooks(settings)
        save_json(SETTINGS, settings)
        print("  ✓ Hook'lar kaldırıldı")
    if find_claude():
        subprocess.run([find_claude(), "mcp", "remove", "--scope", "user", "mepcenter"], capture_output=True)
        print("  ✓ MCP sunucusu kaldırıldı")
    path = desktop_config_path()
    cfg = load_json(path)
    if "mepcenter" in (cfg.get("mcpServers") or {}):
        backup(path)
        del cfg["mcpServers"]["mepcenter"]
        save_json(path, cfg)
        print("  ✓ Claude Desktop'tan kaldırıldı")
    if os.path.exists(CLAUDE_MD):
        with open(CLAUDE_MD, "r", encoding="utf-8") as f:
            text = f.read()
        if MARK_START in text:
            s, e = text.index(MARK_START), text.index(MARK_END) + len(MARK_END)
            with open(CLAUDE_MD, "w", encoding="utf-8") as f:
                f.write((text[:s] + text[e:]).strip() + "\n")
            print("  ✓ CLAUDE.md notu kaldırıldı")
    print(f"Ayarlar ve token {DEST} klasöründe duruyor; istemezseniz bu klasörü silin.")


def main():
    if sys.version_info < (3, 8):
        sys.exit("Python 3.8 veya üstü gerekli.")
    if "--kopru" in sys.argv:  # yalnızca köprü ayarlarını yeniden yap
        cfg_path = os.path.join(DEST, "config.json")
        shutil.copy2(os.path.join(HERE, "hub_kopru.py"), os.path.join(DEST, "hub_kopru.py"))
        install_kopru(load_json(cfg_path), cfg_path)
        return
    if "--kaldir" in sys.argv:
        uninstall()
        return

    print("MepCenter Claude Hub kurulumu\n")
    os.makedirs(DEST, exist_ok=True)
    for f in FILES:
        shutil.copy2(os.path.join(HERE, f), os.path.join(DEST, f))
    print(f"  ✓ Dosyalar kopyalandı: {DEST}")

    cfg_path = os.path.join(DEST, "config.json")
    cfg = load_json(cfg_path)
    cfg["url"] = ask("Hub adresi", cfg.get("url", "https://mepcenter.com.tr/claude/"))
    default_machine = cfg.get("machine") or f"{platform.system().replace('Darwin', 'Mac')}-{socket.gethostname().split('.')[0]}"
    cfg["machine"] = ask("Bu bilgisayarın adı (panelde böyle görünür)", default_machine)
    save_json(cfg_path, cfg)

    sys.path.insert(0, DEST)
    from hub_client import HubError, api, register

    if cfg.get("token") and not yes("Bu bilgisayar daha önce bağlanmış. Bağlantı yenilensin mi?", False):
        pass
    else:
        print("\nPanele girdiğiniz kullanıcı adı ve şifreyi yazın (bilgisayar kendini otomatik kaydeder).")
        while True:
            user = ask("Panel kullanıcı adı", "claude")
            pw = getpass.getpass("Panel şifresi (yazarken görünmez; panelden üretilmiş bir token varsa onu da yapıştırabilirsiniz): ").strip()
            if pw.startswith("mch_"):  # panelden elle üretilmiş anahtar
                cfg["token"] = pw
                print("  ✓ Token kaydedildi")
                break
            try:
                res = register(cfg, user, pw, cfg["machine"])
                cfg["token"] = res["token"]
                print(f"  ✓ Bilgisayar kaydedildi: '{res['agent']}'")
                break
            except HubError as e:
                print(f"  ! {e}")
                if not yes("Tekrar denensin mi?", True):
                    sys.exit(1)
    save_json(cfg_path, cfg)
    try:
        os.chmod(cfg_path, 0o600)
    except OSError:
        pass

    try:
        res = api("ping", cwd=HOME)
        print(f"  ✓ Sunucuya bağlanıldı ({res['agent']}, sürüm {res['version']})")
    except HubError as e:
        print(f"  ! Sunucuya bağlanılamadı: {e}")
        if not yes("Yine de kuruluma devam edilsin mi?", False):
            sys.exit(1)

    install_hooks()
    install_mcp_claude_code()
    install_mcp_desktop()
    install_claude_md()
    install_kopru(cfg, cfg_path)
    print("\nKurulum tamam. Açık Claude Code oturumlarını kapatıp yeniden açın.")
    print("Deneme: Claude Code'da  'kod deneme'  yazın; Claude hub'a bağlanıp görevi açmalı ve panelde görünmeli.")


if __name__ == "__main__":
    main()
