"""Yoneten ve yonetilen ayni makinede: eslesme, olaylar, pano ve dosya aktarimi."""

import os
import socket
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cekirdek import ag, pano  # noqa: E402
from cekirdek import protokol as p  # noqa: E402


def bos_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class Depo:
    def __init__(self, kimlik, ad):
        self._ben = {"id": kimlik, "ad": ad}
        self.anahtarlar = {}

    def ben(self):
        return self._ben

    def get(self, anahtar):
        return None

    def eslesmeler(self):
        return {k: "" for k in self.anahtarlar}

    def anahtar_bul(self, k):
        return self.anahtarlar.get(k)

    def anahtar_kaydet(self, k, ad, anahtar):
        self.anahtarlar[k] = anahtar

    def eslesmeyi_sil(self, k):
        self.anahtarlar.pop(k, None)

    def uzak_ayarlar(self):
        return {"fare_hizi": 2.0}


class SahteBulucu:
    def __init__(self, port):
        self.port = port

    def cihazlar(self):
        return {"mac-1": ({"id": "mac-1", "ad": "Mac", "port": self.port, "v": 2}, "127.0.0.1")}


class Bekleyici:
    def __init__(self):
        self.olaylar = []
        self.kosul = threading.Condition()

    def ekle(self, *x):
        with self.kosul:
            self.olaylar.append(x)
            self.kosul.notify_all()

    def bekle(self, kosul, sure=10):
        with self.kosul:
            return self.kosul.wait_for(lambda: any(kosul(o) for o in self.olaylar), sure)


class UctanUcaTest(unittest.TestCase):
    def test_tam_akis(self):
        port = bos_port()
        tmp = tempfile.mkdtemp()
        onaylar, y_durum, s_durum, s_gelen, s_pano, y_pano = (Bekleyici() for _ in range(6))

        def onay(ad, kod):
            onaylar.ekle(ad, kod)
            return True

        yonetilen = ag.Yonetilen(Depo("mac-1", "Mac"), "mac", onay, s_durum.ekle, s_gelen.ekle,
                                 s_pano.ekle, os.path.join(tmp, "mac"), port=port)
        yonetilen.start()
        self.assertTrue(s_durum.bekle(lambda o: o[0] == "bekliyor"))

        yoneten = ag.Yoneten(Depo("win-1", "LAPTOP"), SahteBulucu(port), y_durum.ekle,
                             lambda *a: None, y_pano.ekle, os.path.join(tmp, "win"))
        yoneten.start()
        self.assertTrue(y_durum.bekle(lambda o: o[0] == "bagli"))
        kod_win = next(o[1]["kod"] for o in y_durum.olaylar if o[0] == "kod")
        self.assertEqual(onaylar.olaylar[0], ("LAPTOP", kod_win))

        # Baglaninca ayarlar gider, sonra tus olaylari.
        self.assertTrue(s_gelen.bekle(lambda o: o[0] == p.MSG_AYAR and o[1] == {"fare_hizi": 2.0}))
        yoneten.oturum.olay(p.MSG_TUS, 0x1E, 0, 1)
        self.assertTrue(s_gelen.bekle(lambda o: o == (p.MSG_TUS, 0x1E, 0, 1)))

        # Pano: yoneten -> yonetilen (metin) ve yonetilen -> yoneten (dosyalar + klasor).
        yoneten.oturum.pano_gonder({"tur": "metin", "metin": "merhaba ğüşı"})
        self.assertTrue(s_pano.bekle(lambda o: o[0] == {"tur": "metin", "metin": "merhaba ğüşı"}))

        kaynak = os.path.join(tmp, "kaynak")
        os.makedirs(os.path.join(kaynak, "klasor", "alt"))
        buyuk = os.urandom(300_000)
        with open(os.path.join(kaynak, "klasor", "alt", "buyuk.bin"), "wb") as f:
            f.write(buyuk)
        with open(os.path.join(kaynak, "klasor", "bos.txt"), "wb"):
            pass
        with open(os.path.join(kaynak, "not.txt"), "w", encoding="utf-8") as f:
            f.write("selam")
        yonetilen.oturum.pano_gonder({"tur": "dosyalar", "yollar": [os.path.join(kaynak, "klasor"),
                                                                    os.path.join(kaynak, "not.txt")]})
        # Aktarim surerken tus olaylari gecikmeden gitmeli.
        yoneten.oturum.olay(p.MSG_TUS, 0x30, 0, 1)
        self.assertTrue(s_gelen.bekle(lambda o: o == (p.MSG_TUS, 0x30, 0, 1)))
        self.assertTrue(y_pano.bekle(lambda o: o[0]["tur"] == "dosyalar"))
        yollar = y_pano.olaylar[-1][0]["yollar"]
        self.assertEqual([os.path.basename(y) for y in yollar], ["klasor", "not.txt"])
        with open(os.path.join(yollar[0], "alt", "buyuk.bin"), "rb") as f:
            self.assertEqual(f.read(), buyuk)
        self.assertTrue(os.path.isfile(os.path.join(yollar[0], "bos.txt")))
        with open(yollar[1], encoding="utf-8") as f:
            self.assertEqual(f.read(), "selam")

        # Yonetilen kapaninca yoneten kopmayi fark eder.
        yonetilen.oturum.kapat("test")
        self.assertTrue(y_durum.bekle(lambda o: o[0] == "koptu"))
        # ... ve kayitli anahtarla onay sormadan yeniden baglanir.
        y_durum.olaylar.clear()
        self.assertTrue(y_durum.bekle(lambda o: o[0] == "bagli"))
        self.assertEqual(len(onaylar.olaylar), 1)


class PanoGuvenlikTesti(unittest.TestCase):
    def test_yol_disari_cikamaz(self):
        alici = pano.PanoAlici(tempfile.mkdtemp())
        for kotu in ("../disari.txt", "/etc/passwd", "a/../../b", "C:/Windows/x"):
            with self.assertRaises(pano.AktarimHatasi):
                alici.basla({"no": 1, "tur": "dosyalar", "boyut": 1,
                             "girdiler": [{"yol": kotu, "boyut": 1}], "ustler": [kotu]})

    def test_sinir(self):
        alici = pano.PanoAlici(tempfile.mkdtemp(), dosya_siniri=10)
        with self.assertRaises(pano.AktarimHatasi):
            alici.basla({"no": 1, "tur": "dosyalar", "boyut": 11, "girdiler": [], "ustler": []})

    def test_esitleyici_sadece_degisince_gonderir(self):
        class SahtePano:
            def __init__(self):
                self.n, self.icerik, self.yazilan = 0, None, []

            def sayac(self):
                return self.n

            def oku(self):
                return self.icerik

            def yaz(self, icerik):
                self.yazilan.append(icerik)
                self.n += 1

        class SahteOturum:
            def __init__(self):
                self.giden = []

            def pano_gonder(self, icerik):
                self.giden.append(icerik)

        sp, so = SahtePano(), SahteOturum()
        e = pano.PanoEsitleyici(sp)
        e.gerekirse_gonder(so)
        self.assertEqual(so.giden, [])
        sp.icerik, sp.n = {"tur": "metin", "metin": "a"}, 1
        e.gerekirse_gonder(so)
        e.gerekirse_gonder(so)
        self.assertEqual(len(so.giden), 1)
        # Karsidan gelen icerik yazilinca geri gonderilmemeli.
        e.geldi({"tur": "metin", "metin": "b"})
        e.gerekirse_gonder(so)
        self.assertEqual(len(so.giden), 1)


if __name__ == "__main__":
    unittest.main()
