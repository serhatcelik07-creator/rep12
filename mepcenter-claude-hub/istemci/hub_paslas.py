#!/usr/bin/env python3
"""MepCenter Claude Hub - PASLAŞMA (kaynak kodu buluta gönder, buluttan gelen yamayı uygula ve test et).

Claude token'ı harcamaz: işi bulut oturumu yapar, bu bilgisayar yalnızca dosya taşır ve derler/test eder.

Kullanım:
  python3 hub_paslas.py gonder --kod pofuduk            kaynak klasörü tek zip olarak hub'a gönderir
  python3 hub_paslas.py al --kod pofuduk                buluttaki son yamayı kaynağa uygular, derleme kopyasında
                                                        flutter analyze + flutter test çalıştırır, sonucu hub'a yazar
  python3 hub_paslas.py al --kod pofuduk --test-yok     yalnızca uygula
  python3 hub_paslas.py geri --kod pofuduk              son uygulanan yamayı geri alır (yedekten)
  python3 hub_paslas.py temizle --kod pofuduk           hub'daki bu göreve ait aktarım dosyalarını siler

Dosya paylaşma protokolü: asıllar bu bilgisayarda durur, hub yalnızca aktarım alanıdır (paslas/<kod>/).
İşi biten aktarım dosyaları silinir; unutulanları sunucu birkaç gün sonra kendisi siler.
Seçenekler:
  --kaynak YOL    kaynak klasör (varsayılan: <kod> için bilinen yollar, örn. /Volumes/*/center_pdf, G:\\center_pdf)
  --derleme YOL   derleme kopyası (varsayılan: ~/dev/<klasör adı>, Windows'ta C:\\dev\\<klasör adı>)
  --zorla         kaynakta yamadan sonra değişmiş dosya olsa da uygula (önce yedek alınır)
"""

import argparse
import base64
import glob
import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hub_client import HubError, api, load_config  # noqa: E402

PART_MB = 8  # hub yükleme sınırının altında kalsın (base64 + JSON şişmesi)
SKIP_DIRS = {".git", ".dart_tool", "build", ".idea", ".vs", ".vscode", "Pods", "ephemeral", "node_modules",
             "__pycache__", ".gradle", ".paslas_yedek", "wp", "$RECYCLE.BIN", "System Volume Information"}
SKIP_EXT = {".msix", ".exe", ".dll", ".zip", ".pfx", ".p12", ".pem", ".key", ".so", ".dylib", ".appx", ".dmg"}
SKIP_NAMES = {"config.php", "satis_api.php", ".env", "local.properties", ".ds_store", "thumbs.db", "desktop.ini"}
MAX_FILE_MB = 5
KNOWN = {"pofuduk": ["/Volumes/*/center_pdf", "G:\\center_pdf", "~/dev/center_pdf", "C:\\dev\\center_pdf"]}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def find_source(code, given):
    if given:
        return os.path.abspath(os.path.expanduser(given))
    for pat in KNOWN.get(code, []):
        for p in sorted(glob.glob(os.path.expanduser(pat))):
            if os.path.isfile(os.path.join(p, "pubspec.yaml")) or os.path.isdir(p):
                return p
    sys.exit(f"Kaynak klasör bulunamadı; --kaynak ile verin.")


def skip_file(rel, size):
    name = rel.rsplit("/", 1)[-1].lower()
    return (name in SKIP_NAMES or name.startswith("_gizli") or name.startswith("~$")
            or os.path.splitext(name)[1] in SKIP_EXT or size > MAX_FILE_MB * 1048576)


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root).replace("\\", "/")
            try:
                size = os.path.getsize(path)
            except OSError:
                continue
            if not skip_file(rel, size):
                yield rel, path


def upload_blob(data, rel_path, code, note):
    step = int(PART_MB * 1048576)
    parts = [data[i:i + step] for i in range(0, len(data), step)] or [b""]
    ids = []
    for n, chunk in enumerate(parts, 1):
        name = rel_path.rsplit("/", 1)[-1] + (f".part{n}of{len(parts)}" if len(parts) > 1 else "")
        rel = rel_path + (f".part{n}of{len(parts)}" if len(parts) > 1 else "")
        res = api("upload", {"name": name, "rel_path": rel, "code": code, "note": note,
                             "content_b64": base64.b64encode(chunk).decode("ascii")}, timeout=600)
        ids.append(res["id"])
        print(f"  ✓ {rel} ({len(chunk) // 1024} KB)")
    return ids


def transfer_files(code, prefix=""):
    files = api("files", params={"q": f"paslas/{code}/{prefix}", "code": code, "limit": 300})["files"]
    return [f for f in files if f["rel_path"].startswith(f"paslas/{code}/{prefix}")]


def delete_files(ids):
    n = 0
    for i in ids:
        try:
            api("file_delete", {"id": i})
            n += 1
        except HubError as e:
            print(f"  ! {i} silinemedi: {e}")
    return n


def download_latest(code, prefix):
    """prefix ile başlayan en yeni dosyayı (parçalıysa tüm parçalarını) indirir. Dönüş: (ad, veri, kimlikler)."""
    files = transfer_files(code, prefix)
    if not files:
        return None, None, []
    base = files[0]["rel_path"].split(".part")[0]
    group = sorted((f for f in files if f["rel_path"].split(".part")[0] == base), key=lambda f: f["rel_path"])
    want = int(group[0]["rel_path"].rsplit("of", 1)[1]) if ".part" in group[0]["rel_path"] else 1
    seen = {}
    for f in group:  # aynı adla tekrar yüklenmiş parçalar: en yeni olan kalsın
        seen.setdefault(f["rel_path"], f)
    if len(seen) != want:
        sys.exit(f"{base}: {want} parçadan {len(seen)} tanesi hub'da; yükleme bitmemiş olabilir.")
    order = sorted(seen, key=lambda k: int(k.rsplit(".part", 1)[1].split("of")[0]) if ".part" in k else 0)
    data = b"".join(api("download", params={"id": seen[k]["id"]}, raw=True, timeout=600) for k in order)
    return base, data, [f["id"] for f in group]


def report(code, text, title):
    print(text)
    try:
        upload_blob(text.encode("utf-8"), f"paslas/{code}/sonuc-{time.strftime('%Y%m%d-%H%M%S')}.txt", code, title)
        api("topic_add", {"kind": "note", "title": title, "content": text[-6000:], "code": code})
        api("send", {"to": f"project:{code}", "topic": title, "body": text[-3000:]})
    except HubError as e:
        print("Sonuç hub'a yazılamadı:", e)


# --- gonder -----------------------------------------------------------------------------------------------
def cmd_gonder(a):
    root = find_source(a.kod, a.kaynak)
    buf = io.BytesIO()
    manifest = {}
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, path in walk(root):
            with open(path, "rb") as f:
                data = f.read()
            manifest[rel] = sha(data)
            z.writestr(rel, data)
        z.writestr(".paslas.json", json.dumps({"kaynak": root, "makine": load_config()["machine"],
                                               "tarih": time.strftime("%Y-%m-%d %H:%M:%S"), "dosyalar": manifest},
                                              ensure_ascii=False, indent=1))
    data = buf.getvalue()
    print(f"{root}: {len(manifest)} dosya, {len(data) // 1024} KB zip")
    old = [f["id"] for f in transfer_files(a.kod, "kaynak-")]
    if old:
        print(f"  eski kaynak gönderimi siliniyor ({len(old)} dosya)")
        delete_files(old)
    upload_blob(data, f"paslas/{a.kod}/kaynak-{time.strftime('%Y%m%d-%H%M%S')}.zip", a.kod, "paslaşma: kaynak")
    api("send", {"to": f"project:{a.kod}", "topic": "paslaşma: kaynak hazır",
                 "body": f"{load_config()['machine']} kaynağı gönderdi: {len(manifest)} dosya ({root})."})
    print("Bitti. Bulut oturumu kaynağı alabilir.")


# --- al ---------------------------------------------------------------------------------------------------
def cmd_al(a):
    root = find_source(a.kod, a.kaynak)
    base, data, ids = download_latest(a.kod, "yama-")
    if not data:
        sys.exit("Hub'da yama yok.")
    z = zipfile.ZipFile(io.BytesIO(data))
    meta = json.loads(z.read(".yama.json").decode("utf-8"))
    print(f"Yama: {base}\n{meta.get('aciklama', '')}\n")
    conflicts = []
    for rel, info in meta["dosyalar"].items():
        path = os.path.join(root, rel)
        cur = sha(open(path, "rb").read()) if os.path.exists(path) else None
        if cur not in (info.get("eski"), info.get("yeni")):
            conflicts.append(rel)
    if conflicts and not a.zorla:
        sys.exit("Bu dosyalar bulut kaynağı aldıktan sonra burada değişmiş, yama uygulanmadı:\n  "
                 + "\n  ".join(conflicts) + "\nÖnce 'gonder' ile güncel kaynağı yollayın ya da --zorla kullanın.")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup = os.path.join(root, ".paslas_yedek", stamp)
    changed = []
    for rel, info in meta["dosyalar"].items():
        path = os.path.join(root, rel)
        if os.path.exists(path):
            os.makedirs(os.path.dirname(os.path.join(backup, rel)), exist_ok=True)
            shutil.copy2(path, os.path.join(backup, rel))
        if info.get("yeni") is None:  # silinen dosya
            if os.path.exists(path):
                os.remove(path)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(z.read(rel))
        changed.append(rel)
    with open(os.path.join(root, ".paslas_yedek", "son.json"), "w", encoding="utf-8") as f:
        json.dump({"yama": base, "yedek": stamp, "dosyalar": meta["dosyalar"]}, f, ensure_ascii=False)
    print(f"{len(changed)} dosya uygulandı (yedek: {backup}).")
    delete_files(ids)  # protokol: uygulanan yama hub'da kalmaz (geri almak için yerel yedek var)
    if a.test_yok:
        return
    build = mirror(root, a.derleme, changed)
    out = run_checks(build)
    report(a.kod, f"Yama: {base}\nMakine: {load_config()['machine']} ({platform.system()})\n"
                  f"Derleme klasörü: {build}\n\n{out}", f"paslaşma sonucu: {base.rsplit('/', 1)[-1]}")


def mirror(root, given, changed):
    """exFAT/ağ sürücüsünde derleme yapılmaz: kaynağı yerel derleme kopyasına yansıt."""
    if given:
        build = os.path.abspath(os.path.expanduser(given))
    elif platform.system() == "Windows":
        build = os.path.join("C:\\dev", os.path.basename(root))
    else:
        build = os.path.join(os.path.expanduser("~/dev"), os.path.basename(root))
    if os.path.abspath(build) == os.path.abspath(root):
        return build
    fresh = not os.path.isdir(build)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {"build", ".dart_tool", ".git", ".paslas_yedek", "Pods"}]
        for fn in filenames:
            src = os.path.join(dirpath, fn)
            dst = os.path.join(build, os.path.relpath(src, root))
            try:
                if fresh or not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst) \
                        or os.path.getsize(src) != os.path.getsize(dst):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
            except OSError as e:
                print("kopyalanamadı:", src, e)
    for rel in changed:  # silinen dosyalar
        if not os.path.exists(os.path.join(root, rel)) and os.path.exists(os.path.join(build, rel)):
            os.remove(os.path.join(build, rel))
    return build


def run_checks(build):
    flutter = shutil.which("flutter") or next((p for p in [os.path.expanduser("~/dev/flutter/bin/flutter"),
                                                          "/opt/homebrew/bin/flutter", "C:\\dev\\flutter\\bin\\flutter.bat"]
                                               if os.path.exists(p)), None)
    if not flutter:
        return "flutter bulunamadı (PATH'e ekleyin)."
    res = []
    for args, tail in ((["pub", "get"], 15), (["analyze"], 60), (["test", "--reporter", "compact"], 80)):
        t = time.time()
        p = subprocess.run([flutter] + args, cwd=build, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", shell=platform.system() == "Windows")
        lines = (p.stdout + p.stderr).strip().splitlines()
        res.append(f"$ flutter {' '.join(args)}  → çıkış {p.returncode} ({int(time.time() - t)} sn)\n"
                   + "\n".join(lines[-tail:]))
        if p.returncode != 0 and args[0] == "pub":
            break
    return "\n\n".join(res)


# --- temizle ----------------------------------------------------------------------------------------------
def cmd_temizle(a):
    files = transfer_files(a.kod)
    print(f"Hub'da {len(files)} aktarım dosyası; siliniyor…")
    print(f"{delete_files([f['id'] for f in files])} dosya silindi. Asıllar bu bilgisayarda duruyor.")


# --- geri -------------------------------------------------------------------------------------------------
def cmd_geri(a):
    root = find_source(a.kod, a.kaynak)
    try:
        last = json.load(open(os.path.join(root, ".paslas_yedek", "son.json"), encoding="utf-8"))
    except OSError:
        sys.exit("Geri alınacak yama yok.")
    backup = os.path.join(root, ".paslas_yedek", last["yedek"])
    for rel in last["dosyalar"]:
        src, dst = os.path.join(backup, rel), os.path.join(root, rel)
        if os.path.exists(src):
            shutil.copy2(src, dst)
        elif os.path.exists(dst):
            os.remove(dst)  # yamayla eklenmişti
    os.remove(os.path.join(root, ".paslas_yedek", "son.json"))
    print(f"Geri alındı: {last['yama']}")


def main():
    ap = argparse.ArgumentParser(description="Bulut oturumuyla kaynak/yama paslaşması")
    ap.add_argument("islem", choices=["gonder", "al", "geri", "temizle"])
    ap.add_argument("--kod", required=True)
    ap.add_argument("--kaynak")
    ap.add_argument("--derleme")
    ap.add_argument("--zorla", action="store_true")
    ap.add_argument("--test-yok", action="store_true")
    a = ap.parse_args()
    try:
        {"gonder": cmd_gonder, "al": cmd_al, "geri": cmd_geri, "temizle": cmd_temizle}[a.islem](a)
    except HubError as e:
        sys.exit(f"Hub hatası: {e}")


if __name__ == "__main__":
    main()
