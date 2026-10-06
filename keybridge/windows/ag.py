"""Mac'i bulma ve baglanti dongusu (Windows tarafi)."""

import queue
import socket
import threading
import time

from cekirdek import protokol as p


class MacBulucu(threading.Thread):
    """Aga her 2 saniyede "kim var?" sorar; cevap veren Mac'leri tutar."""

    ZAMAN_ASIMI = 8  # bu kadar sn cevap vermeyen Mac listeden duser

    def __init__(self, degisince):
        super().__init__(daemon=True)
        self.degisince = degisince
        self._macler = {}  # id -> (bilgi, adres, son_gorulme)
        self._kilit = threading.Lock()

    def macler(self):
        with self._kilit:
            simdi = time.monotonic()
            return {k: (b, a) for k, (b, a, t) in self._macler.items() if simdi - t < self.ZAMAN_ASIMI}

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(("", 0))
        s.settimeout(0.5)
        son_soru = 0.0
        onceki = set()
        while True:
            if time.monotonic() - son_soru >= 2:
                try:
                    s.sendto(p.KESIF_SORU, ("255.255.255.255", p.KESIF_PORT))
                except OSError:
                    pass  # ag yok (Wi-Fi kapali vb.); tekrar denenecek
                son_soru = time.monotonic()
            try:
                paket, adres = s.recvfrom(1024)
                bilgi = p.kesif_cevabini_coz(paket)
                if bilgi:
                    with self._kilit:
                        self._macler[bilgi["id"]] = (bilgi, adres[0], time.monotonic())
            except socket.timeout:
                pass
            except OSError:
                time.sleep(1)
            simdiki = set(self.macler())
            if simdiki != onceki:
                onceki = simdiki
                self.degisince()


class Baglanti(threading.Thread):
    """Secili Mac'e baglanir, motorun kuyrugundaki olaylari gonderir.

    durum(ad, ek) ile arayuze haber verir: "araniyor", "baglaniyor",
    "kod" (eslestirme kodu), "bagli" (mac bilgisi), "reddedildi", "koptu".
    """

    def __init__(self, ayarlar, bulucu, motor, durum):
        super().__init__(daemon=True)
        self.ayarlar = ayarlar
        self.bulucu = bulucu
        self.motor = motor
        self.durum = durum
        self.kanal = None
        self._kilit = threading.Lock()
        self._yeniden = threading.Event()

    def ayarlari_gonder(self):
        with self._kilit:
            if self.kanal:
                try:
                    self.kanal.ayar_gonder(self.ayarlar.mac_ayarlari())
                except OSError:
                    pass

    def yeniden_baglan(self):
        """Secili Mac degistiginde mevcut baglantiyi birakir."""
        self._yeniden.set()
        with self._kilit:
            if self.kanal:
                try:
                    self.kanal.sock.close()
                except OSError:
                    pass

    def _hedef(self):
        macler = self.bulucu.macler()
        secili = self.ayarlar.get("secili_mac")
        if secili in macler:
            return macler[secili]
        # Secim yoksa: once daha once eslesilmis bir Mac, yoksa tek Mac varsa o.
        eslesmeler = self.ayarlar.eslesmeler()
        for kimlik, deger in macler.items():
            if kimlik in eslesmeler:
                return deger
        if len(macler) == 1 and secili is None:
            return next(iter(macler.values()))
        return None

    def run(self):
        hatali_dogrulama = {}
        while True:
            self._yeniden.clear()
            hedef = self._hedef()
            if not hedef:
                self.durum("araniyor", None)
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
                kanal, mac = p.istemci_el_sikis(
                    sock, self.ayarlar.ben(), bilgi["id"], self.ayarlar.anahtar_bul,
                    lambda kod: self.durum("kod", kod), self.ayarlar.anahtar_kaydet)
            except p.EslesmeHatasi as e:
                sock.close()
                self.durum("reddedildi", str(e))
                self._yeniden.wait(5)
                continue
            except Exception:
                sock.close()
                # Kayitli anahtar iki kez ust uste reddedilirse (or. Mac'te eslesmeler
                # sifirlandi) anahtari unut; bir sonraki denemede yeniden eslesilir.
                if self.ayarlar.anahtar_bul(bilgi["id"]) is not None:
                    hatali_dogrulama[bilgi["id"]] = hatali_dogrulama.get(bilgi["id"], 0) + 1
                    if hatali_dogrulama[bilgi["id"]] >= 2:
                        self.ayarlar.eslesmeyi_sil(bilgi["id"])
                        hatali_dogrulama.pop(bilgi["id"])
                self._yeniden.wait(2)
                continue
            hatali_dogrulama.pop(bilgi["id"], None)
            self._oturum(sock, kanal, mac)

    def _oturum(self, sock, kanal, mac):
        while not self.motor.kuyruk.empty():
            self.motor.kuyruk.get_nowait()
        sock.settimeout(5)
        with self._kilit:
            self.kanal = kanal
        self.ayarlari_gonder()
        self.motor.bagli = True
        self.durum("bagli", mac)
        okuyucu = threading.Thread(target=self._okuyucu, args=(kanal,), daemon=True)
        okuyucu.start()
        try:
            # Fare surekli hareket etse bile her saniye ping at; Mac'in cevaplari
            # okuyucuyu canli tutar, 5 sn cevap yoksa baglanti olmus sayilir.
            son_ping = 0.0
            while okuyucu.is_alive() and not self._yeniden.is_set():
                try:
                    mesaj = self.motor.kuyruk.get(timeout=0.5)
                    with self._kilit:
                        kanal.gonder(*mesaj)
                except queue.Empty:
                    pass
                if time.monotonic() - son_ping >= 1:
                    with self._kilit:
                        kanal.gonder(p.MSG_PING)
                    son_ping = time.monotonic()
        except Exception:
            pass
        # Baglanti koptu: klavye Windows'ta kalsin ki kullanici kilitlenmesin.
        self.motor.bagli = False
        self.motor.windowsa_don()
        with self._kilit:
            self.kanal = None
        sock.close()
        self.durum("koptu", mac)
        time.sleep(1)

    @staticmethod
    def _okuyucu(kanal):
        try:
            while True:
                kanal.al()
        except Exception:
            pass
