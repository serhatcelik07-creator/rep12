"""Microsoft Store lisansi (PC->Mac Windows uygulamasi): 15 gunluk deneme, sonra satin alma.

Deneme suresi ve fiyat Partner Center'da ayarlanir (Fiyatlandirma ve
kullanilabilirlik > Ucretsiz deneme: 15 gun). Uygulama yalnizca Store'dan
lisans durumunu okur; satin alma icin Store sayfasini acar. Odeme, iade ve
vergi Store tarafindan yapilir.
"""

import ctypes
import datetime as dt
import threading
import webbrowser

from cekirdek.metinler import T

# Partner Center > Urun kimligi > "Store ID" (12 karakter, or. 9NBLGGH4R315).
STORE_ID = "9XXXXXXXXXXX"

TAM = "tam"
DENEME = "deneme"
BITTI = "bitti"
GELISTIRICI = "gelistirici"

try:
    from _paket_bilgisi import STORE_SURUMU  # Store derlemesinde paketleme betigi uretir
except ImportError:
    STORE_SURUMU = False


def degerlendir(etkin, deneme, bitis, simdi=None):
    """Store'dan okunan degerlerden (tur, kalan_gun) uretir."""
    simdi = simdi or dt.datetime.now(dt.timezone.utc)
    if not etkin:
        return BITTI, 0
    if not deneme:
        return TAM, None
    if bitis is None:
        return DENEME, None
    if bitis.tzinfo is None:
        bitis = bitis.replace(tzinfo=dt.timezone.utc)
    kalan = (bitis - simdi).total_seconds()
    if kalan <= 0:
        return BITTI, 0
    return DENEME, int(-(-kalan // 86400))  # yukari yuvarla: 1 saat kaldiysa "1 gun"


def _paketli_mi():
    """Uygulama Store/MSIX paketi icinden mi calisiyor?"""
    try:
        uzunluk = ctypes.c_uint32(0)
        hata = ctypes.windll.kernel32.GetCurrentPackageFullName(ctypes.byref(uzunluk), None)
    except (AttributeError, OSError):
        return False
    return hata != 15700  # APPMODEL_ERROR_NO_PACKAGE


def _storedan_oku():
    import asyncio
    from winrt.windows.services.store import StoreContext

    async def oku():
        lisans = await StoreContext.get_default().get_app_license_async()
        return lisans.is_active, lisans.is_trial, lisans.expiration_date

    return asyncio.run(oku())


class Lisans:
    """Lisans durumunu tutar; ayarlar dosyasinda son bilinen durumu saklar."""

    def __init__(self, ayarlar, degisince=lambda: None):
        self.ayarlar = ayarlar
        self.degisince = degisince
        self.tur, self.kalan_gun = GELISTIRICI, None
        onbellek = ayarlar.get("lisans_onbellek")
        if STORE_SURUMU and onbellek:
            self.tur, self.kalan_gun = onbellek["tur"], onbellek.get("kalan_gun")

    @property
    def kullanilabilir(self):
        return self.tur != BITTI

    def yenile_arkaplanda(self):
        threading.Thread(target=self.yenile, daemon=True).start()

    def yenile(self):
        if not STORE_SURUMU:
            tur, kalan = GELISTIRICI, None
        elif not _paketli_mi():
            # Store derlemesi paketin disindan calistirilmis: lisans dogrulanamaz.
            tur, kalan = BITTI, 0
        else:
            try:
                tur, kalan = degerlendir(*_storedan_oku())
            except Exception:
                # Store'a ulasilamadi (cevrimdisi vb.): son bilinen durumla devam et.
                return
            self.ayarlar.set("lisans_onbellek", {"tur": tur, "kalan_gun": kalan,
                                                 "zaman": dt.datetime.now().isoformat(timespec="seconds")})
        if (tur, kalan) != (self.tur, self.kalan_gun):
            self.tur, self.kalan_gun = tur, kalan
            self.degisince()

    def metin(self):
        if self.tur == TAM:
            return T("lisans_tam")
        if self.tur == DENEME:
            return T("lisans_deneme", gun=self.kalan_gun) if self.kalan_gun else T("lisans_deneme_suresiz")
        if self.tur == BITTI:
            return T("lisans_bitti")
        return T("lisans_gelistirici")

    @staticmethod
    def satin_al():
        webbrowser.open(f"ms-windows-store://pdp/?productid={STORE_ID}")
