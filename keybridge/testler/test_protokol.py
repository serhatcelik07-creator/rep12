import os
import socket
import sys
import threading
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cekirdek import protokol as p  # noqa: E402


class Depo:
    def __init__(self):
        self.anahtarlar = {}

    def bul(self, kimlik):
        return self.anahtarlar.get(kimlik)

    def kaydet(self, kimlik, ad, anahtar):
        self.anahtarlar[kimlik] = anahtar


def calistir(win_depo, mac_depo, izin=True, hedef="mac-1"):
    a, b = socket.socketpair()
    a.settimeout(5)
    b.settimeout(5)
    sonuc = {"kodlar": []}

    def mac():
        try:
            def onay(ad, kod):
                sonuc["kodlar"].append(kod)
                sonuc["win_ad"] = ad
                return izin
            kanal, win = p.sunucu_el_sikis(a, {"id": "mac-1", "ad": "Mac mini"}, mac_depo.bul, onay, mac_depo.kaydet)
            sonuc["mac_aldi"] = [kanal.al(), kanal.al()]
            kanal.gonder(p.MSG_PING)
        except Exception as e:
            sonuc["mac_hata"] = e
            a.close()

    t = threading.Thread(target=mac)
    t.start()
    try:
        kanal, mac_bilgi = p.istemci_el_sikis(b, {"id": "win-1", "ad": "LAPTOP"}, hedef, win_depo.bul,
                                              sonuc["kodlar"].append, win_depo.kaydet)
        kanal.gonder(p.MSG_TUS, 0x1E, 0, 1)
        kanal.ayar_gonder({"hiz": 1.5, "ctrl_cmd": True})
        sonuc["win_aldi"] = kanal.al()
        sonuc["mac_ad"] = mac_bilgi["ad"]
    except Exception as e:
        sonuc["win_hata"] = e
        b.close()
    t.join()
    a.close()
    b.close()
    return sonuc


class ProtokolTesti(unittest.TestCase):
    def test_ilk_eslestirme_ve_sonraki_baglanti(self):
        win, mac = Depo(), Depo()
        s = calistir(win, mac)
        self.assertNotIn("win_hata", s)
        self.assertNotIn("mac_hata", s)
        # Mac'teki onay kodu ile Windows'ta gosterilen kod ayni olmali.
        self.assertEqual(len(s["kodlar"]), 2)
        self.assertEqual(s["kodlar"][0], s["kodlar"][1])
        self.assertEqual(len(s["kodlar"][0]), 6)
        self.assertEqual(s["mac_aldi"], [(p.MSG_TUS, 0x1E, 0, 1), (p.MSG_AYAR, {"hiz": 1.5, "ctrl_cmd": True}, 0, 0)])
        self.assertEqual(s["win_aldi"], (p.MSG_PING, 0, 0, 0))
        self.assertEqual(win.anahtarlar["mac-1"], mac.anahtarlar["win-1"])

        # Ikinci baglantida onay sorulmamali.
        s2 = calistir(win, mac)
        self.assertNotIn("win_hata", s2)
        self.assertEqual(s2["kodlar"], [])
        self.assertEqual(s2["mac_aldi"][0], (p.MSG_TUS, 0x1E, 0, 1))

    def test_reddedilen_eslestirme(self):
        win, mac = Depo(), Depo()
        s = calistir(win, mac, izin=False)
        self.assertIsInstance(s["win_hata"], p.EslesmeHatasi)
        self.assertEqual(win.anahtarlar, {})
        self.assertEqual(mac.anahtarlar, {})

    def test_yanlis_anahtar_baglanamaz(self):
        win, mac = Depo(), Depo()
        win.anahtarlar["mac-1"] = os.urandom(32)
        mac.anahtarlar["win-1"] = os.urandom(32)
        s = calistir(win, mac)
        self.assertIn("win_hata", s)
        self.assertIn("mac_hata", s)

    def test_mac_eslesmeyi_unuttuysa_yeniden_eslesir(self):
        win, mac = Depo(), Depo()
        win.anahtarlar["mac-1"] = os.urandom(32)
        s = calistir(win, mac)
        self.assertNotIn("win_hata", s)
        self.assertEqual(len(s["kodlar"]), 2)
        self.assertEqual(win.anahtarlar["mac-1"], mac.anahtarlar["win-1"])

    def test_baska_mac_reddedilir(self):
        s = calistir(Depo(), Depo(), hedef="baska-mac")
        self.assertIsInstance(s["win_hata"], p.EslesmeHatasi)

    def test_kesif(self):
        bilgi = p.kesif_cevabini_coz(p.kesif_cevabi("mac-1", "Serhat'ın Mac mini"))
        self.assertEqual(bilgi["ad"], "Serhat'ın Mac mini")
        self.assertIsNone(p.kesif_cevabini_coz(b"KB2!bozuk"))
        self.assertIsNone(p.kesif_cevabini_coz(b"baska"))


if __name__ == "__main__":
    unittest.main()
