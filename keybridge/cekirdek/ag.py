"""Ag: yoneten taraf icin bulma + baglanma, yonetilen taraf icin dinleme.

Iki urunde de ayni kod calisir; yalnizca hangi platformun hangi rolde
oldugu degisir (PC->Mac: Windows yoneten; Mac->PC: Mac yoneten).
"""

import logging
import socket
import threading
import time

from cekirdek import protokol as p
from cekirdek.oturum import Oturum

log = logging.getLogger("keybridge.ag")


# ================================================================ yoneten
class Bulucu(threading.Thread):
    """Aga her 2 saniyede "kim var?" sorar; belirli platformdaki yonetilenleri tutar."""

    ZAMAN_ASIMI = 8  # bu kadar sn cevap vermeyen cihaz listeden duser

    def __init__(self, hedef_platform, degisince=lambda: None):
        super().__init__(daemon=True, name="bulucu")
        self.hedef_platform = hedef_platform
        self.degisince = degisince
        self._cihazlar = {}  # id -> (bilgi, adres, son_gorulme)
        self._kilit = threading.Lock()

    def cihazlar(self):
        with self._kilit:
            simdi = time.monotonic()
            return {k: (b, a) for k, (b, a, t) in self._cihazlar.items() if simdi - t < self.ZAMAN_ASIMI}

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(("", 0))
        s.settimeout(0.5)
        son_soru, onceki = 0.0, set()
        while True:
            if time.monotonic() - son_soru >= 2:
                try:
                    s.sendto(p.KESIF_SORU, ("255.255.255.255", p.KESIF_PORT))
                except OSError:
                    pass  # ag yok (Wi-Fi kapali vb.); tekrar denenecek
                son_soru = time.monotonic()
            try:
                paket, adres = s.recvfrom(2048)
                bilgi = p.kesif_cevabini_coz(paket)
                if bilgi and bilgi.get("platform") == self.hedef_platform:
                    with self._kilit:
                        self._cihazlar[bilgi["id"]] = (bilgi, adres[0], time.monotonic())
            except socket.timeout:
                pass
            except OSError:
                time.sleep(1)
            simdiki = set(self.cihazlar())
            if simdiki != onceki:
                onceki = simdiki
                self.degisince()


class Yoneten(threading.Thread):
    """Secili cihaza baglanir ve oturumu yurutur.

    depo: ben(), get("secili"), eslesmeler(), anahtar_bul/kaydet/sil, uzak_ayarlar()
    durum(ad, ek): "araniyor", "secim", "baglaniyor", "kod", "bagli", "reddedildi", "koptu"
    gelen(tip, a, b, c), pano_geldi(icerik): oturumdan gelenler
    """

    def __init__(self, depo, bulucu, durum, gelen, pano_geldi, pano_onbellegi):
        super().__init__(daemon=True, name="yoneten")
        self.depo = depo
        self.bulucu = bulucu
        self.durum = durum
        self.gelen = gelen
        self.pano_geldi = pano_geldi
        self.pano_onbellegi = pano_onbellegi
        self.oturum = None
        self._yeniden = threading.Event()

    def ayarlari_gonder(self):
        o = self.oturum
        if o:
            o.ayar(self.depo.uzak_ayarlar())

    def yeniden_baglan(self):
        """Secili cihaz degistiginde veya eslesme silindiginde."""
        self._yeniden.set()
        o = self.oturum
        if o:
            o.kapat("yeniden")

    def _hedef(self):
        cihazlar = self.bulucu.cihazlar()
        secili = self.depo.get("secili")
        if secili in cihazlar:
            return cihazlar[secili]
        eslesmeler = self.depo.eslesmeler()
        for kimlik, deger in cihazlar.items():
            if kimlik in eslesmeler:
                return deger
        if len(cihazlar) == 1:
            return next(iter(cihazlar.values()))
        return None

    def run(self):
        hatali = {}
        while True:
            self._yeniden.clear()
            hedef = self._hedef()
            if not hedef:
                self.durum("secim" if len(self.bulucu.cihazlar()) > 1 else "araniyor", None)
                self._yeniden.wait(1)
                continue
            bilgi, adres = hedef
            self.durum("baglaniyor", bilgi)
            try:
                sock = socket.create_connection((adres, bilgi.get("port", p.TCP_PORT)), timeout=5)
            except OSError:
                self._yeniden.wait(2)
                continue
            try:
                p.tcp_ayarla(sock)
                kanal, karsi = p.istemci_el_sikis(
                    sock, self.depo.ben(), bilgi["id"], self.depo.anahtar_bul,
                    lambda kod: self.durum("kod", {"kod": kod, "ad": bilgi.get("ad", "")}),
                    self.depo.anahtar_kaydet)
            except p.EslesmeHatasi as e:
                sock.close()
                self.durum("reddedildi", str(e))
                self._yeniden.wait(5)
                continue
            except Exception as e:
                sock.close()
                log.info("baglanti kurulamadi: %r", e)
                # Kayitli anahtar iki kez ust uste reddedilirse (or. karsi tarafta
                # eslesmeler sifirlandi) unut; bir sonraki denemede yeniden eslesilir.
                if self.depo.anahtar_bul(bilgi["id"]) is not None:
                    hatali[bilgi["id"]] = hatali.get(bilgi["id"], 0) + 1
                    if hatali[bilgi["id"]] >= 2:
                        self.depo.eslesmeyi_sil(bilgi["id"])
                        hatali.pop(bilgi["id"])
                self._yeniden.wait(2)
                continue
            hatali.pop(bilgi["id"], None)
            oturum = Oturum(kanal, self.gelen, self.pano_geldi, self.pano_onbellegi)
            oturum.ayar(self.depo.uzak_ayarlar())
            self.oturum = oturum
            self.durum("bagli", karsi)
            neden = oturum.calistir()
            self.oturum = None
            self.durum("koptu", {"ad": karsi.get("ad", ""), "neden": neden})
            time.sleep(1)


# ================================================================ yonetilen
class KesifCevaplayici(threading.Thread):
    def __init__(self, ben, platform, port=p.TCP_PORT):
        super().__init__(daemon=True, name="kesif")
        self.ben, self.platform, self.port = ben, platform, port

    def run(self):
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("", p.KESIF_PORT))
                while True:
                    paket, adres = s.recvfrom(64)
                    if paket.startswith(p.KESIF_SORU):
                        ben = self.ben()
                        s.sendto(p.kesif_cevabi(ben["id"], ben["ad"], self.platform, self.port), adres)
            except OSError as e:
                log.warning("kesif hatasi: %r", e)
                time.sleep(3)


class Yonetilen(threading.Thread):
    """Gelen baglantilari kabul eder; ayni anda tek bir yoneten.

    depo: ben(), anahtar_bul/kaydet
    onay_iste(ad, kod) -> bool: eslestirmede kullaniciya sorar
    durum(ad, ek): "bekliyor", "bagli", "koptu", "reddedildi"
    gelen(tip, a, b, c), pano_geldi(icerik)
    """

    def __init__(self, depo, platform, onay_iste, durum, gelen, pano_geldi, pano_onbellegi, port=p.TCP_PORT):
        super().__init__(daemon=True, name="yonetilen")
        self.depo = depo
        self.platform = platform
        self.onay_iste = onay_iste
        self.durum = durum
        self.gelen = gelen
        self.pano_geldi = pano_geldi
        self.pano_onbellegi = pano_onbellegi
        self.port = port
        self.oturum = None
        self._kilit = threading.Lock()

    def run(self):
        KesifCevaplayici(self.depo.ben, self.platform, self.port).start()
        while True:
            try:
                sunucu = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sunucu.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sunucu.bind(("0.0.0.0", self.port))
                sunucu.listen(4)
                break
            except OSError as e:
                log.warning("port %s acilamadi: %r", self.port, e)
                time.sleep(3)
        self.durum("bekliyor", None)
        while True:
            sock, adres = sunucu.accept()
            threading.Thread(target=self._isle, args=(sock, adres), daemon=True).start()

    def _isle(self, sock, adres):
        try:
            p.tcp_ayarla(sock)
            sock.settimeout(10)
            kanal, karsi = p.sunucu_el_sikis(sock, self.depo.ben(), self.depo.anahtar_bul,
                                             self.onay_iste, self.depo.anahtar_kaydet)
        except p.EslesmeHatasi as e:
            self.durum("reddedildi", str(e))
            sock.close()
            return
        except Exception as e:
            log.info("%s el sikismasi basarisiz: %r", adres[0], e)
            sock.close()
            return
        oturum = Oturum(kanal, self.gelen, self.pano_geldi, self.pano_onbellegi)
        with self._kilit:
            # Yeni baglanti eskisinin yerini alir (or. yoneten yeniden baslatildi).
            if self.oturum:
                self.oturum.kapat("yeni baglanti")
            self.oturum = oturum
        self.durum("bagli", karsi)
        neden = oturum.calistir()
        with self._kilit:
            if self.oturum is oturum:
                self.oturum = None
                self.durum("koptu", {"ad": karsi.get("ad", ""), "neden": neden})
