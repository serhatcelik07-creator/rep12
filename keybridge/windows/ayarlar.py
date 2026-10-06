"""Windows uygulamasinin ayarlari: %APPDATA%\\KeyBridge\\ayarlar.json

Tum ayarlar Windows'ta tutulur; Mac'i ilgilendirenler (fare hizi, Ctrl/Cmd
vb.) her baglantida ve her degisiklikte Mac'e gonderilir.
Eslesme anahtarlari Windows DPAPI ile korunur (yalnizca bu kullanici acabilir).
"""

import base64
import ctypes
import json
import os
import socket
import threading
import uuid
from ctypes import wintypes

VARSAYILAN = {
    "git_tusu": {"vk": 0x28, "degistiriciler": []},   # ↓
    "don_tusu": {"vk": 0x26, "degistiriciler": []},   # ↑
    "fare_hizi": 1.0,
    "teker_hizi": 1.0,
    "teker_ters": False,
    "ctrl_cmd": False,
    "ses": True,
    "secili_mac": None,
}
# Mac'e gonderilen ayarlar
MAC_AYARLARI = ("fare_hizi", "teker_hizi", "teker_ters", "ctrl_cmd")


def _klasor():
    temel = os.environ.get("APPDATA") or os.path.expanduser("~")
    yol = os.path.join(temel, "KeyBridge")
    os.makedirs(yol, exist_ok=True)
    return yol


class _BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]


def _dpapi(veri, koru):
    try:
        crypt32, kernel32 = ctypes.windll.crypt32, ctypes.windll.kernel32
    except AttributeError:  # Windows disi (testler): korumasiz sakla
        return veri
    giris = _BLOB(len(veri), ctypes.cast(ctypes.create_string_buffer(veri, len(veri)), ctypes.POINTER(ctypes.c_char)))
    cikis = _BLOB()
    islev = crypt32.CryptProtectData if koru else crypt32.CryptUnprotectData
    if not islev(ctypes.byref(giris), None, None, None, None, 0, ctypes.byref(cikis)):
        raise OSError("DPAPI hatasi")
    try:
        return ctypes.string_at(cikis.pbData, cikis.cbData)
    finally:
        kernel32.LocalFree(cikis.pbData)


class Ayarlar:
    def __init__(self, yol=None):
        self.yol = yol or os.path.join(_klasor(), "ayarlar.json")
        self._kilit = threading.Lock()
        try:
            with open(self.yol, encoding="utf-8") as f:
                self._veri = json.load(f)
        except (OSError, ValueError):
            self._veri = {}
        degisti = False
        for anahtar, deger in VARSAYILAN.items():
            if anahtar not in self._veri:
                self._veri[anahtar] = json.loads(json.dumps(deger))
                degisti = True
        if "kimlik" not in self._veri:
            self._veri["kimlik"] = str(uuid.uuid4())
            degisti = True
        self._veri.setdefault("eslesmeler", {})
        if degisti:
            self._kaydet()

    def _kaydet(self):
        gecici = self.yol + ".tmp"
        with open(gecici, "w", encoding="utf-8") as f:
            json.dump(self._veri, f, ensure_ascii=False, indent=2)
        os.replace(gecici, self.yol)

    def get(self, anahtar, varsayilan=None):
        with self._kilit:
            return self._veri.get(anahtar, varsayilan)

    def set(self, anahtar, deger):
        with self._kilit:
            self._veri[anahtar] = deger
            self._kaydet()

    def ben(self):
        ad = os.environ.get("COMPUTERNAME") or socket.gethostname()
        return {"id": self._veri["kimlik"], "ad": ad}

    def mac_ayarlari(self):
        with self._kilit:
            return {a: self._veri[a] for a in MAC_AYARLARI}

    # ---- eslesmeler ----
    def anahtar_bul(self, mac_id):
        with self._kilit:
            kayit = self._veri["eslesmeler"].get(mac_id)
        if not kayit:
            return None
        try:
            return _dpapi(base64.b64decode(kayit["anahtar"]), koru=False)
        except (OSError, ValueError, KeyError):
            return None

    def anahtar_kaydet(self, mac_id, mac_ad, anahtar):
        korunmus = base64.b64encode(_dpapi(anahtar, koru=True)).decode("ascii")
        with self._kilit:
            self._veri["eslesmeler"][mac_id] = {"ad": mac_ad, "anahtar": korunmus}
            self._kaydet()

    def eslesmeyi_sil(self, mac_id):
        with self._kilit:
            self._veri["eslesmeler"].pop(mac_id, None)
            self._kaydet()

    def eslesmeler(self):
        with self._kilit:
            return {k: v["ad"] for k, v in self._veri["eslesmeler"].items()}
