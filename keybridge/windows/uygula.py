"""Windows'ta uzaktan gelen tus ve fare olaylarini uygular (yonetilen taraf: Mac->PC).

SendInput ile scan kodu gonderilir; hangi karakterin cikacagini Windows'taki
klavye duzeni belirler.

Not: Windows, yonetici olarak calisan pencerelere normal bir uygulamanin tus
gondermesine izin vermez (UIPI) ve Ctrl+Alt+Del hicbir zaman taklit edilemez.
"""

import ctypes
from ctypes import wintypes

from cekirdek import tuslar

INPUT_MOUSE, INPUT_KEYBOARD = 0, 1
KEYEVENTF_EXTENDEDKEY, KEYEVENTF_KEYUP, KEYEVENTF_SCANCODE = 0x1, 0x2, 0x8
MOUSEEVENTF_MOVE = 0x1
MOUSEEVENTF_WHEEL, MOUSEEVENTF_HWHEEL = 0x800, 0x1000
DUGME_BAYRAK = {1: (0x2, 0x4, 0), 2: (0x8, 0x10, 0), 3: (0x20, 0x40, 0), 4: (0x80, 0x100, 1), 5: (0x80, 0x100, 2)}

ULONG_PTR = ctypes.c_size_t


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD), ("wParamH", wintypes.WORD)]


class _GIRDI(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _GIRDI)]


_SendInput = ctypes.windll.user32.SendInput
_SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
_SendInput.restype = wintypes.UINT


def _gonder(*girdiler):
    dizi = (INPUT * len(girdiler))(*girdiler)
    _SendInput(len(girdiler), dizi, ctypes.sizeof(INPUT))


def _tus(scan, genis, basildi):
    bayrak = KEYEVENTF_SCANCODE | (KEYEVENTF_EXTENDEDKEY if genis else 0) | (0 if basildi else KEYEVENTF_KEYUP)
    g = INPUT(type=INPUT_KEYBOARD)
    g.ki = KEYBDINPUT(0, scan, bayrak, 0, 0)
    return g


def _fare(bayrak, dx=0, dy=0, veri=0):
    g = INPUT(type=INPUT_MOUSE)
    g.mi = MOUSEINPUT(dx, dy, ctypes.c_uint32(veri).value, bayrak, 0, 0)
    return g


class Uygulayici:
    def __init__(self):
        self.ayarlar = {"fare_hizi": 1.0, "teker_hizi": 1.0, "teker_ters": False, "ctrl_cmd": False}
        self.basili_tuslar = set()
        self.basili_dugmeler = set()
        self._artik = [0.0, 0.0]

    def ayarla(self, ayarlar):
        self.ayarlar.update({k: v for k, v in ayarlar.items() if k in self.ayarlar})

    def tus(self, scan, genis, basildi):
        anahtar = (scan, 1 if genis else 0)
        if self.ayarlar["ctrl_cmd"]:
            anahtar = tuslar.CTRL_CMD_TAKAS.get(anahtar, anahtar)
        if basildi:
            self.basili_tuslar.add(anahtar)
        else:
            self.basili_tuslar.discard(anahtar)
        _gonder(_tus(anahtar[0], anahtar[1], basildi))

    def hareket(self, dx, dy):
        # Kesirli kismi biriktir ki dusuk hizlarda yavas hareketler kaybolmasin.
        hiz = float(self.ayarlar["fare_hizi"])
        self._artik[0] += dx * hiz
        self._artik[1] += dy * hiz
        ix, iy = int(self._artik[0]), int(self._artik[1])
        self._artik[0] -= ix
        self._artik[1] -= iy
        if ix or iy:
            _gonder(_fare(MOUSEEVENTF_MOVE, ix, iy))

    def dugme(self, no, basildi):
        if no not in DUGME_BAYRAK:
            return
        asagi, yukari, x = DUGME_BAYRAK[no]
        if basildi:
            self.basili_dugmeler.add(no)
        else:
            self.basili_dugmeler.discard(no)
        _gonder(_fare(asagi if basildi else yukari, veri=x))

    def teker(self, dikey, yatay):
        carpan = float(self.ayarlar["teker_hizi"]) * (-1 if self.ayarlar["teker_ters"] else 1)
        if dikey:
            _gonder(_fare(MOUSEEVENTF_WHEEL, veri=int(dikey * carpan)))
        if yatay:
            _gonder(_fare(MOUSEEVENTF_HWHEEL, veri=int(yatay * carpan)))

    def hepsini_birak(self):
        for scan, genis in list(self.basili_tuslar):
            _gonder(_tus(scan, genis, False))
        self.basili_tuslar.clear()
        for no in list(self.basili_dugmeler):
            self.dugme(no, False)
