#!/usr/bin/env python3
"""MepCenter Claude Hub - klasör senkronu.

Bir klasördeki (ör. ağ sürücüsü G:\\Projeler\\Matwar) dosyaları hub'a yükler; bir görev koduna bağlar.
Böylece diğer bilgisayarlardaki, claude.ai'deki ve bulut oturumlarındaki Claude'lar bu dosyaları görür.
Yalnızca değişen dosyalar tekrar gönderilir. Sürücünün şifresi bu bilgisayarda kalır, hiçbir yere gönderilmez.

Kullanım:
  python hub_senkron.py "G:\\Projeler\\Matwar" --kod matwar
  python hub_senkron.py "G:\\Projeler\\Matwar" --kod matwar --izle 10     (her 10 dakikada bir tekrar)
  python hub_senkron.py "G:\\Projeler\\Matwar" --kod matwar --deneme      (göndermeden ne gideceğini göster)
Seçenekler:
  --max-mb N     dosya başına üst sınır (varsayılan 20; sunucu sınırını aşamaz)
  --hepsi        hariç tutma listesini (.env, şifre dosyaları, zip, exe…) uygulama
"""

import argparse
import base64
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hub_client import CONFIG_DIR, HubError, api, load_config  # noqa: E402

STATE_FILE = os.path.join(CONFIG_DIR, "senkron_state.json")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".idea", ".vs", "$RECYCLE.BIN",
             "System Volume Information"}


def excluded(rel, patterns):
    import fnmatch
    rel = rel.replace("\\", "/").lower()
    name = rel.rsplit("/", 1)[-1]
    return any(fnmatch.fnmatch(name, p.lower()) or fnmatch.fnmatch(rel, p.lower()) for p in patterns)


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(st):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(STATE_FILE + ".tmp", "w", encoding="utf-8") as f:
        json.dump(st, f)
    os.replace(STATE_FILE + ".tmp", STATE_FILE)


def run_once(root, code, max_mb, use_exclude, dry, cfg):
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        print(f"Klasör bulunamadı: {root}")
        return
    patterns = [p for p in cfg.get("exclude", []) if not p.endswith("/*")] if use_exclude else []
    st = load_state()
    key_prefix = f"{code}|{root}|"
    sent = skipped = big = failed = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root).replace("\\", "/")
            if fn.startswith("~$") or fn.lower() in ("thumbs.db", "desktop.ini", ".ds_store"):
                continue
            if patterns and excluded(rel, patterns):
                skipped += 1
                continue
            try:
                stt = os.stat(path)
            except OSError:
                continue
            if stt.st_size > max_mb * 1048576:
                big += 1
                print(f"  - çok büyük, atlandı: {rel} ({stt.st_size // 1048576} MB)")
                continue
            sig = f"{stt.st_size}:{int(stt.st_mtime)}"
            if st.get(key_prefix + rel) == sig:
                continue  # değişmemiş
            if dry:
                print(f"  + gönderilecek: {rel}")
                sent += 1
                continue
            try:
                with open(path, "rb") as f:
                    data = f.read()
                api("upload", {"name": fn, "rel_path": f"{os.path.basename(root)}/{rel}", "code": code,
                               "note": "klasör senkronu", "content_b64": base64.b64encode(data).decode("ascii")},
                    cwd=root, cfg=cfg, timeout=300)
                st[key_prefix + rel] = sig
                sent += 1
                print(f"  ✓ {rel}")
                if sent % 20 == 0:
                    save_state(st)
            except (HubError, OSError) as e:
                failed += 1
                print(f"  ! {rel}: {e}")
    if not dry:
        save_state(st)
    print(f"Bitti: {sent} dosya {'gönderilecek' if dry else 'gönderildi'}, {big} çok büyük, "
          f"{skipped} gizli/hariç, {failed} hata. (Değişmeyen dosyalar tekrar gönderilmez.)")


def main():
    ap = argparse.ArgumentParser(description="Bir klasörü MepCenter hub'a gönderir")
    ap.add_argument("klasor", nargs="?")
    ap.add_argument("--kod", help="görev kodu, örn. matwar")
    ap.add_argument("--izle", type=float, default=0, help="her N dakikada bir tekrar et")
    ap.add_argument("--max-mb", type=float, default=20)
    ap.add_argument("--hepsi", action="store_true")
    ap.add_argument("--deneme", action="store_true")
    a = ap.parse_args()
    if not a.klasor:
        a.klasor = input("Gönderilecek klasör (örn. G:\\Projeler\\Matwar): ").strip().strip('"')
    if not a.kod:
        a.kod = input("Görev kodu (örn. matwar): ").strip()
    cfg = load_config()
    if not cfg.get("token"):
        sys.exit("Bu bilgisayar hub'a kayıtlı değil. Önce kur.py çalıştırın.")
    while True:
        print(f"\n{time.strftime('%H:%M')} {a.klasor} -> görev '{a.kod}'")
        run_once(a.klasor, a.kod, a.max_mb, not a.hepsi, a.deneme, cfg)
        if not a.izle:
            break
        time.sleep(a.izle * 60)


if __name__ == "__main__":
    main()
