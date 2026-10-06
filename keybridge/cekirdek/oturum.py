"""Kurulmus bir baglanti uzerinde iki yonlu oturum.

Tek bir gonderici is parcacigi kanala yazar: once tus/fare olaylari, onlar
yokken pano aktariminin parcalari. Boylece buyuk bir dosya aktarilirken bile
klavye ve fare gecikmez. Iki taraf da her saniye ping atar; 5 sn hicbir sey
gelmezse baglanti olmus sayilir.
"""

import collections
import itertools
import queue
import threading
import time

from cekirdek import pano as pano_mod
from cekirdek import protokol as p

PING_ARALIGI = 1.0
ZAMAN_ASIMI = 5.0


class Oturum:
    def __init__(self, kanal, gelen, pano_geldi, pano_onbellegi, dosya_siniri=pano_mod.VARSAYILAN_DOSYA_SINIRI):
        """gelen(tip, a, b, c): tus/fare/ayar/aktif mesajlari icin;
        pano_geldi(icerik): bir pano aktarimi tamamlaninca."""
        self.kanal = kanal
        self.gelen = gelen
        self.pano_geldi = pano_geldi
        self.dosya_siniri = dosya_siniri
        self._alici = pano_mod.PanoAlici(pano_onbellegi, dosya_siniri)
        self._kuyruk = queue.Queue()
        self._aktarimlar = collections.deque()
        self._no = itertools.count(1)
        self._bitti = threading.Event()
        self.neden = None

    # ---- disaridan cagrilanlar (herhangi bir is parcacigindan) ----
    def olay(self, tip, a=0, b=0, c=0):
        self._kuyruk.put_nowait(p.sabit_mesaj(tip, a, b, c))

    def ayar(self, ayarlar):
        self._kuyruk.put_nowait(p.json_mesaji(p.MSG_AYAR, ayarlar))

    def pano_gonder(self, icerik):
        # Yeni kopyalanan icerik eskisinin yerini alir; yarim kalan aktarim iptal edilir.
        self._aktarimlar.clear()
        self._aktarimlar.append(pano_mod.aktarim_mesajlari(next(self._no), icerik, self.dosya_siniri))

    def kapat(self, neden=None):
        if not self._bitti.is_set():
            self.neden = self.neden or neden
            self._bitti.set()
            try:
                self.kanal.sock.close()
            except OSError:
                pass

    @property
    def acik(self):
        return not self._bitti.is_set()

    # ---- calistirma ----
    def calistir(self):
        """Baglanti kopana kadar bloklar."""
        self.kanal.sock.settimeout(ZAMAN_ASIMI)
        okuyucu = threading.Thread(target=self._oku, daemon=True)
        okuyucu.start()
        try:
            self._gonder_dongusu()
        except Exception as e:
            self.kapat(str(e) or type(e).__name__)
        finally:
            self.kapat()
            self._alici.iptal()
        okuyucu.join(1)
        return self.neden

    def _gonder_dongusu(self):
        son_ping = 0.0
        while not self._bitti.is_set():
            aktarim = self._aktarimlar[0] if self._aktarimlar else None
            try:
                mesaj = self._kuyruk.get(timeout=0 if aktarim else 0.25)
            except queue.Empty:
                mesaj = None
                if aktarim:
                    mesaj = next(aktarim, None)
                    if mesaj is None and self._aktarimlar and self._aktarimlar[0] is aktarim:
                        self._aktarimlar.popleft()
            if mesaj is not None:
                self.kanal.gonder_ham(mesaj)
            if time.monotonic() - son_ping >= PING_ARALIGI:
                self.kanal.gonder(p.MSG_PING)
                son_ping = time.monotonic()

    def _oku(self):
        try:
            while not self._bitti.is_set():
                tip, a, b, c = self.kanal.al()
                if tip == p.MSG_PING:
                    continue
                if tip == p.MSG_PANO_BASLA:
                    try:
                        self._alici.basla(a)
                    except (pano_mod.AktarimHatasi, OSError, KeyError, ValueError):
                        self._alici.iptal()
                elif tip == p.MSG_PANO_PARCA:
                    try:
                        self._alici.parca(a, b)
                    except OSError:
                        self._alici.iptal()
                elif tip == p.MSG_PANO_BITTI:
                    icerik = self._alici.bitti(a)
                    if icerik:
                        self._guvenli(self.pano_geldi, icerik)
                else:
                    self._guvenli(self.gelen, tip, a, b, c)
        except Exception as e:
            self.kapat(str(e) or type(e).__name__)

    @staticmethod
    def _guvenli(islev, *args):
        # Tek bir olaydaki hata (or. Mac'te izin yok) baglantiyi dusurmesin.
        try:
            islev(*args)
        except Exception:
            pass
