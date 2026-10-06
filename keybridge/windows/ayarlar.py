"""Windows'ta ayar dosyasinin yeri ve eslesme anahtarlarinin korunmasi.

Ayarlar: %APPDATA%\\KeyBridge\\<urun>\\ayarlar.json
Gelen dosyalar: %LOCALAPPDATA%\\KeyBridge\\<urun>\\Pano
Eslesme anahtarlari Windows DPAPI ile korunur (yalnizca bu kullanici acabilir).
"""

import ctypes
import os
import socket
from ctypes import wintypes

from cekirdek.depo import Depo, varsayilanlar


def onbellek(urun):
    temel = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    yol = os.path.join(temel, "KeyBridge", urun, "Pano")
    os.makedirs(yol, exist_ok=True)
    return yol


class _BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]


def _dpapi(veri, koru):
    try:
        crypt32, kernel32 = ctypes.windll.crypt32, ctypes.windll.kernel32
    except AttributeError:  # Windows disi (testler): korumasiz
        return veri
    tampon = ctypes.create_string_buffer(veri, len(veri))
    giris = _BLOB(len(veri), ctypes.cast(tampon, ctypes.POINTER(ctypes.c_char)))
    cikis = _BLOB()
    islev = crypt32.CryptProtectData if koru else crypt32.CryptUnprotectData
    if not islev(ctypes.byref(giris), None, None, None, None, 0, ctypes.byref(cikis)):
        raise OSError("DPAPI hatasi")
    try:
        return ctypes.string_at(cikis.pbData, cikis.cbData)
    finally:
        kernel32.LocalFree(cikis.pbData)


def _ad():
    return os.environ.get("COMPUTERNAME") or socket.gethostname()


def ayarlar(urun, yol=None):
    temel = os.environ.get("APPDATA") or os.path.expanduser("~")
    yol = yol or os.path.join(temel, "KeyBridge", urun, "ayarlar.json")
    return Depo(yol, varsayilanlar("windows"), _ad,
                koru=lambda b: _dpapi(b, True), coz=lambda b: _dpapi(b, False))
