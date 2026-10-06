"""Windows dusuk seviye klavye/fare kancalari.

Kararlari karar.py verir; burasi onlari uygular: Mac modunda olaylari yutar,
Mac'e gonderilecekleri kuyruga atar, imleci ekranin ortasinda sabitler.
"""

import ctypes
import queue
import threading

from pynput import keyboard, mouse

import karar
from cekirdek import protokol as p

WM_KEYDOWN, WM_SYSKEYDOWN = 0x100, 0x104
WM_MOUSEMOVE = 0x200
DUGMELER = {0x201: (1, 1), 0x202: (1, 0), 0x204: (2, 1), 0x205: (2, 0), 0x207: (3, 1), 0x208: (3, 0)}
WM_MOUSEWHEEL, WM_XBUTTONDOWN, WM_XBUTTONUP, WM_MOUSEHWHEEL = 0x20A, 0x20B, 0x20C, 0x20E
LLKHF_EXTENDED, LLKHF_INJECTED = 0x01, 0x10 | 0x02
LLMHF_INJECTED = 0x01 | 0x02

user32 = ctypes.windll.user32


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def dpi_farkinda_ol():
    # Olcekli ekranlarda (%125, %150) imlec koordinatlari tutarli olsun.
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        user32.SetProcessDPIAware()


def _isaretli16(deger):
    deger = (deger >> 16) & 0xFFFF
    return deger - 0x10000 if deger & 0x8000 else deger


def _int16(deger):
    return max(-32768, min(32767, int(deger)))


class Motor:
    """olay_bildir(ad, ek) ile arayuze haber verir:
    "mac" / "windows" (gecis), "kullanilamaz", "yakalandi" (Kisayol)."""

    def __init__(self, git, don, olay_bildir, ses_acik=lambda: True):
        self.karar = karar.KlavyeKarari(git, don)
        self.olay_bildir = olay_bildir
        self.ses_acik = ses_acik
        self.kuyruk = queue.Queue()
        self.bagli = False
        self.kullanilabilir = True
        self.merkez = (0, 0)
        self.eski_konum = POINT()
        self.kilit = threading.Lock()
        self._klavye = keyboard.Listener(win32_event_filter=self._klavye_filtresi)
        self._fare = mouse.Listener(win32_event_filter=self._fare_filtresi)

    def baslat(self):
        self._klavye.start()
        self._fare.start()

    def durdur(self):
        self.windowsa_don()
        self._klavye.stop()
        self._fare.stop()

    @property
    def mac_modu(self):
        return self.karar.mac_modu

    def kisayollari_ayarla(self, git, don):
        self.karar.git, self.karar.don = git, don

    def kisayol_yakala(self):
        self.karar.yakalamaya_basla()

    def _gonder(self, tip, a=0, b=0, c=0):
        if self.bagli:
            self.kuyruk.put_nowait((tip, a, b, c))

    def _bip(self, frekans):
        if self.ses_acik():
            import winsound
            threading.Thread(target=winsound.Beep, args=(frekans, 70), daemon=True).start()

    # ---- gecisler ----
    def _maca_gecildi(self):
        with self.kilit:
            user32.GetCursorPos(ctypes.byref(self.eski_konum))
            # Imleci ana ekranin ortasina sabitliyoruz; fare hareketleri buradan
            # olculup Mac'e gonderiliyor, boylece kenara takilma olmuyor.
            self.merkez = (user32.GetSystemMetrics(0) // 2, user32.GetSystemMetrics(1) // 2)
            user32.SetCursorPos(*self.merkez)
            self._gonder(p.MSG_AKTIF, 1)
        self._bip(880)
        self.olay_bildir("mac", None)

    def _windowsa_donuldu(self):
        with self.kilit:
            self._gonder(p.MSG_BIRAK)
            self._gonder(p.MSG_AKTIF, 0)
            user32.SetCursorPos(self.eski_konum.x, self.eski_konum.y)
        self._bip(440)
        self.olay_bildir("windows", None)

    def windowsa_don(self):
        """Baglanti koptugunda veya uygulama kapanirken: klavye Windows'ta kalsin."""
        if self.karar.mac_modu:
            self.karar.windows_moduna_al()
            self._windowsa_donuldu()

    # ---- kancalar ----
    # Windows'un kanca zaman asimi kisadir: burada ag islemi yapilmaz, sadece kuyruga atilir.
    def _klavye_filtresi(self, msg, data):
        if data.flags & LLKHF_INJECTED:
            return True
        basildi = msg in (WM_KEYDOWN, WM_SYSKEYDOWN)
        eylem, ek = self.karar.olay(data.vkCode, basildi, self.bagli, self.kullanilabilir)
        if eylem in (karar.GECIR, karar.KULLANILAMAZ):
            if eylem == karar.KULLANILAMAZ:
                self.olay_bildir("kullanilamaz", None)
            return True
        if eylem == karar.MACA_GEC:
            self._maca_gecildi()
        elif eylem == karar.WINDOWSA_DON:
            self._windowsa_donuldu()
        elif eylem == karar.YAKALANDI:
            self.olay_bildir("yakalandi", ek)
        elif eylem == karar.GONDER:
            # AltGr, Windows'ta sahte bir sol Ctrl uretir (scan kodu 0x21D); onu atla.
            if data.scanCode and not data.scanCode & 0x200:
                self._gonder(p.MSG_TUS, data.scanCode & 0xFF,
                             1 if data.flags & LLKHF_EXTENDED else 0, 1 if basildi else 0)
        self._klavye.suppress_event()

    def _fare_filtresi(self, msg, data):
        if not self.karar.mac_modu or data.flags & LLMHF_INJECTED:
            return True
        if msg == WM_MOUSEMOVE:
            dx, dy = data.pt.x - self.merkez[0], data.pt.y - self.merkez[1]
            if dx or dy:
                self._gonder(p.MSG_HAREKET, _int16(dx), _int16(dy))
        elif msg in DUGMELER:
            self._gonder(p.MSG_DUGME, *DUGMELER[msg])
        elif msg in (WM_XBUTTONDOWN, WM_XBUTTONUP):
            x = (data.mouseData >> 16) & 0xFFFF
            self._gonder(p.MSG_DUGME, 4 if x == 1 else 5, 1 if msg == WM_XBUTTONDOWN else 0)
        elif msg == WM_MOUSEWHEEL:
            self._gonder(p.MSG_TEKER, _isaretli16(data.mouseData), 0)
        elif msg == WM_MOUSEHWHEEL:
            self._gonder(p.MSG_TEKER, 0, _isaretli16(data.mouseData))
        self._fare.suppress_event()
