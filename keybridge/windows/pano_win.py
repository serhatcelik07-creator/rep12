"""Windows panosu: metin, resim (PNG) ve dosya listesi (Gezgin'de Kopyala/Yapistir)."""

import ctypes
import io
import struct
import time
from ctypes import wintypes

CF_UNICODETEXT, CF_DIB, CF_HDROP = 13, 8, 15
GMEM_MOVEABLE = 0x0002
DROPEFFECT_COPY = 1

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
shell32 = ctypes.WinDLL("shell32", use_last_error=True)

user32.OpenClipboard.argtypes = (wintypes.HWND,)
user32.OpenClipboard.restype = wintypes.BOOL
user32.CloseClipboard.restype = wintypes.BOOL
user32.EmptyClipboard.restype = wintypes.BOOL
user32.GetClipboardData.argtypes = (wintypes.UINT,)
user32.GetClipboardData.restype = wintypes.HANDLE
user32.SetClipboardData.argtypes = (wintypes.UINT, wintypes.HANDLE)
user32.SetClipboardData.restype = wintypes.HANDLE
user32.IsClipboardFormatAvailable.argtypes = (wintypes.UINT,)
user32.IsClipboardFormatAvailable.restype = wintypes.BOOL
user32.GetClipboardSequenceNumber.restype = wintypes.DWORD
user32.RegisterClipboardFormatW.argtypes = (wintypes.LPCWSTR,)
user32.RegisterClipboardFormatW.restype = wintypes.UINT
kernel32.GlobalAlloc.argtypes = (wintypes.UINT, ctypes.c_size_t)
kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
kernel32.GlobalLock.argtypes = (wintypes.HGLOBAL,)
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = (wintypes.HGLOBAL,)
kernel32.GlobalSize.argtypes = (wintypes.HGLOBAL,)
kernel32.GlobalSize.restype = ctypes.c_size_t
kernel32.GlobalFree.argtypes = (wintypes.HGLOBAL,)
shell32.DragQueryFileW.argtypes = (wintypes.HANDLE, wintypes.UINT, wintypes.LPWSTR, wintypes.UINT)
shell32.DragQueryFileW.restype = wintypes.UINT

CF_PNG = user32.RegisterClipboardFormatW("PNG")
CF_DROPEFFECT = user32.RegisterClipboardFormatW("Preferred DropEffect")


class _AcikPano:
    """Pano baska bir uygulamada kisa sure acik olabilir; birkac kez dene."""

    def __enter__(self):
        for _ in range(20):
            if user32.OpenClipboard(None):
                return self
            time.sleep(0.02)
        raise OSError("pano acilamadi")

    def __exit__(self, *_):
        user32.CloseClipboard()


def _oku_bayt(tutamak):
    isaret = kernel32.GlobalLock(tutamak)
    if not isaret:
        return None
    try:
        return ctypes.string_at(isaret, kernel32.GlobalSize(tutamak))
    finally:
        kernel32.GlobalUnlock(tutamak)


def _bellek(veri):
    tutamak = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(veri))
    if not tutamak:
        raise MemoryError
    isaret = kernel32.GlobalLock(tutamak)
    ctypes.memmove(isaret, veri, len(veri))
    kernel32.GlobalUnlock(tutamak)
    return tutamak


def _koy(bicim, veri):
    tutamak = _bellek(veri)
    if not user32.SetClipboardData(bicim, tutamak):
        kernel32.GlobalFree(tutamak)  # basarisizsa bellek bizde kalir


class WindowsPanosu:
    def sayac(self):
        return user32.GetClipboardSequenceNumber()

    def oku(self):
        with _AcikPano():
            if user32.IsClipboardFormatAvailable(CF_HDROP):
                h = user32.GetClipboardData(CF_HDROP)
                adet = shell32.DragQueryFileW(h, 0xFFFFFFFF, None, 0)
                yollar = []
                for i in range(adet):
                    n = shell32.DragQueryFileW(h, i, None, 0) + 1
                    tampon = ctypes.create_unicode_buffer(n)
                    shell32.DragQueryFileW(h, i, tampon, n)
                    yollar.append(tampon.value)
                return {"tur": "dosyalar", "yollar": yollar} if yollar else None
            if CF_PNG and user32.IsClipboardFormatAvailable(CF_PNG):
                veri = _oku_bayt(user32.GetClipboardData(CF_PNG))
                if veri:
                    return {"tur": "resim", "png": veri}
            if user32.IsClipboardFormatAvailable(CF_DIB):
                dib = _oku_bayt(user32.GetClipboardData(CF_DIB))
                if dib:
                    return {"tur": "resim", "png": _dib_png(dib)}
            if user32.IsClipboardFormatAvailable(CF_UNICODETEXT):
                veri = _oku_bayt(user32.GetClipboardData(CF_UNICODETEXT))
                if veri:
                    metin = veri.decode("utf-16-le", errors="replace").split("\x00", 1)[0]
                    return {"tur": "metin", "metin": metin}
        return None

    def yaz(self, icerik):
        tur = icerik["tur"]
        with _AcikPano():
            user32.EmptyClipboard()
            if tur == "metin":
                _koy(CF_UNICODETEXT, icerik["metin"].replace("\r\n", "\n").replace("\n", "\r\n")
                     .encode("utf-16-le") + b"\x00\x00")
            elif tur == "resim":
                _koy(CF_DIB, _png_dib(icerik["png"]))
                if CF_PNG:
                    _koy(CF_PNG, icerik["png"])
            elif tur == "dosyalar":
                # DROPFILES: pFiles=20, pt=(0,0), fNC=0, fWide=1; ardindan cift NUL ile biten yollar.
                yollar = "".join(y + "\x00" for y in icerik["yollar"]) + "\x00"
                _koy(CF_HDROP, struct.pack("<IiiII", 20, 0, 0, 0, 1) + yollar.encode("utf-16-le"))
                _koy(CF_DROPEFFECT, struct.pack("<I", DROPEFFECT_COPY))


def _dib_png(dib):
    from PIL import Image
    # DIB'in basina 14 baytlik BMP dosya basligi ekleyip Pillow'a okut.
    baslik_boyu = struct.unpack_from("<I", dib, 0)[0]
    bit = struct.unpack_from("<H", dib, 14)[0]
    renk = struct.unpack_from("<I", dib, 32)[0] if baslik_boyu >= 36 else 0
    sikistirma = struct.unpack_from("<I", dib, 16)[0]
    maske = 12 if (sikistirma == 3 and baslik_boyu == 40) else 0
    palet = (renk or (1 << bit if bit <= 8 else 0)) * 4
    ofset = 14 + baslik_boyu + maske + palet
    bmp = b"BM" + struct.pack("<IHHI", 14 + len(dib), 0, 0, ofset) + dib
    cikti = io.BytesIO()
    Image.open(io.BytesIO(bmp)).save(cikti, "PNG")
    return cikti.getvalue()


def _png_dib(png):
    from PIL import Image
    cikti = io.BytesIO()
    Image.open(io.BytesIO(png)).convert("RGB").save(cikti, "BMP")
    return cikti.getvalue()[14:]  # BMP dosya basligini at, geriye DIB kalir
