import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cekirdek import karar as k  # noqa: E402

ASAGI, YUKARI, SOL_SHIFT, SOL_CTRL, SOL_ALT, A, M = 0x28, 0x26, 0xA0, 0xA2, 0xA4, 0x41, 0x4D


def bas(kk, vk, **kw):
    return kk.olay(vk, True, **kw)[0]


def birak(kk, vk, **kw):
    return kk.olay(vk, False, **kw)[0]


class KararTesti(unittest.TestCase):
    def setUp(self):
        self.kk = k.KlavyeKarari(k.Kisayol(ASAGI), k.Kisayol(YUKARI), "windows")

    def test_varsayilan_gecis(self):
        kk = self.kk
        self.assertEqual(bas(kk, ASAGI), k.UZAGA_GEC)
        # Gecis tusunun tekrar ve birakma olaylari hicbir yere gitmez.
        self.assertEqual(bas(kk, ASAGI), k.YUT)
        self.assertEqual(birak(kk, ASAGI), k.YUT)
        # Mac modunda ↓ ve harfler Mac'e gider.
        self.assertEqual(bas(kk, ASAGI), k.GONDER)
        self.assertEqual(birak(kk, ASAGI), k.GONDER)
        self.assertEqual(bas(kk, A), k.GONDER)
        self.assertEqual(birak(kk, A), k.GONDER)
        # ↑ Windows'a dondurur, Mac'e gitmez.
        self.assertEqual(bas(kk, YUKARI), k.GERI_DON)
        self.assertEqual(birak(kk, YUKARI), k.YUT)
        self.assertEqual(bas(kk, YUKARI), k.GECIR)

    def test_degistiriciyle_gecis_olmaz(self):
        kk = self.kk
        self.assertEqual(bas(kk, SOL_SHIFT), k.GECIR)
        self.assertEqual(bas(kk, ASAGI), k.GECIR)  # Shift+↓ Windows'ta metin secer
        birak(kk, ASAGI)
        birak(kk, SOL_SHIFT)
        self.assertEqual(bas(kk, ASAGI), k.UZAGA_GEC)
        birak(kk, ASAGI)
        self.assertEqual(bas(kk, SOL_SHIFT), k.GONDER)
        self.assertEqual(bas(kk, YUKARI), k.GONDER)  # Shift+↑ Mac'te secim yapar
        birak(kk, YUKARI)
        birak(kk, SOL_SHIFT)
        self.assertEqual(bas(kk, YUKARI), k.GERI_DON)

    def test_baglanti_yoksa_tus_normal_calisir(self):
        self.assertEqual(bas(self.kk, ASAGI, bagli=False), k.KULLANILAMAZ)
        self.assertFalse(self.kk.uzakta)
        self.assertEqual(bas(self.kk, ASAGI, kullanilabilir=False), k.KULLANILAMAZ)

    def test_kombinasyon_kisayolu(self):
        kk = k.KlavyeKarari(k.Kisayol(M, {"ctrl", "alt"}), k.Kisayol(M, {"ctrl", "shift"}), "windows")
        self.assertEqual(bas(kk, M), k.GECIR)
        birak(kk, M)
        bas(kk, SOL_CTRL)
        bas(kk, SOL_ALT)
        self.assertEqual(bas(kk, M), k.UZAGA_GEC)
        # Mac'e gecmeden once basilan Ctrl/Alt'in birakilmasi Windows'a gider.
        self.assertEqual(birak(kk, M), k.YUT)
        self.assertEqual(birak(kk, SOL_ALT), k.GECIR)
        self.assertEqual(birak(kk, SOL_CTRL), k.GECIR)
        self.assertEqual(bas(kk, SOL_CTRL), k.GONDER)
        bas(kk, SOL_SHIFT)
        self.assertEqual(bas(kk, M), k.GERI_DON)

    def test_yakalama(self):
        kk = self.kk
        kk.yakalamaya_basla()
        self.assertEqual(bas(kk, SOL_CTRL), k.GECIR)
        eylem, kisayol = kk.olay(0x71, True)
        self.assertEqual(eylem, k.YAKALANDI)
        self.assertEqual(kisayol, k.Kisayol(0x71, {"ctrl"}))
        self.assertEqual(kisayol.metin("windows"), "Ctrl + F2")
        self.assertEqual(birak(kk, 0x71), k.YUT)

    def test_kopunca_windowsa_doner(self):
        bas(self.kk, ASAGI)
        self.kk.geri_al()
        birak(self.kk, ASAGI)
        self.assertEqual(bas(self.kk, A), k.GECIR)

    def test_sozluk(self):
        ks = k.Kisayol(M, {"ctrl", "alt"})
        self.assertEqual(k.Kisayol.sozlukten(ks.sozluk()), ks)
        self.assertEqual(ks.metin("windows"), "Ctrl + Alt + M")
        self.assertEqual(k.Kisayol(ASAGI).metin("windows"), "↓")
        self.assertEqual(k.Kisayol(46, {"win", "alt"}).metin("mac"), "⌥⌘M")

    def test_mac_kisayollari(self):
        kk = k.KlavyeKarari(k.Kisayol(125), k.Kisayol(126), "mac")
        self.assertEqual(bas(kk, 56), k.GECIR)          # sol Shift
        self.assertEqual(bas(kk, 125), k.GECIR)         # Shift+↓ gecis yapmaz
        birak(kk, 125)
        birak(kk, 56)
        self.assertEqual(bas(kk, 125), k.UZAGA_GEC)
        birak(kk, 125)
        self.assertEqual(bas(kk, 126), k.GERI_DON)


if __name__ == "__main__":
    unittest.main()
