"""Klavye olaylarinda ne yapilacagina karar veren saf mantik.

Platforma ozgu hicbir sey icermez; tus kodlari Windows'ta VK, Mac'te sanal
tus kodudur. Yakalama modulleri (windows/yakala.py, mac/yakala.py) bu
kararlari uygular.
"""

from cekirdek import tuslar

# yakalama modulunun uygulayacagi eylemler
GECIR = "gecir"            # yerel bilgisayarda normal islensin
YUT = "yut"                # hicbir yere gitmesin
GONDER = "gonder"          # yerelde islenmesin, uzak bilgisayara gonderilsin
UZAGA_GEC = "uzaga_gec"
GERI_DON = "geri_don"
YAKALANDI = "yakalandi"    # ayarlarda yeni kisayol secildi
KULLANILAMAZ = "kullanilamaz"  # gecis tusuna basildi ama baglanti/lisans yok


class Kisayol:
    def __init__(self, vk, degistiriciler=()):
        self.vk = int(vk)
        self.degistiriciler = frozenset(degistiriciler)

    @classmethod
    def sozlukten(cls, veri):
        return cls(veri["vk"], veri.get("degistiriciler", ()))

    def sozluk(self):
        return {"vk": self.vk, "degistiriciler": sorted(self.degistiriciler)}

    def eslesir(self, vk, basili_degistiriciler):
        # Degistiricisiz kisayol (or. tek basina ↓) sadece baska tus basili
        # degilken calisir; Shift+↓ gibi kombinasyonlar normal islemeye devam eder.
        return vk == self.vk and basili_degistiriciler == self.degistiriciler

    def metin(self, platform):
        adlar = tuslar.DEGISTIRICI_ADLARI[platform]
        parcalar = [adlar[d] for d in tuslar.DEGISTIRICI_SIRASI if d in self.degistiriciler]
        parcalar.append(tuslar.TUS_ADLARI[platform].get(self.vk, f"#{self.vk}"))
        return (" + " if platform == "windows" else "").join(parcalar)

    def __eq__(self, diger):
        return isinstance(diger, Kisayol) and (self.vk, self.degistiriciler) == (diger.vk, diger.degistiriciler)

    def __hash__(self):
        return hash((self.vk, self.degistiriciler))

    def __repr__(self):
        return f"Kisayol({self.vk}, {sorted(self.degistiriciler)})"


class KlavyeKarari:
    def __init__(self, git, don, platform):
        self.degistirici = tuslar.DEGISTIRICILER[platform]
        self.git = git
        self.don = don
        self.uzakta = False
        self.basili = set()       # fiziksel olarak basili VK kodlari
        self.yutulacak = set()    # birakilana kadar hicbir yere gitmeyecek tuslar
        self.uzak_basili = set()   # basilma olayi uzak bilgisayara gonderilmis tuslar
        self.yakalama = False

    def _basili_degistiriciler(self, haric):
        return frozenset(filter(None, (self.degistirici.get(v) for v in self.basili if v != haric)))

    def yakalamaya_basla(self):
        self.yakalama = True

    def geri_al(self):
        """Baglanti koptugunda motor cagirir."""
        self.uzakta = False
        self.uzak_basili.clear()

    def olay(self, vk, basildi, bagli=True, kullanilabilir=True):
        """Bir tus olayi icin (eylem, ek) dondurur."""
        degistiriciler = self._basili_degistiriciler(vk)
        if basildi:
            self.basili.add(vk)
        else:
            self.basili.discard(vk)

        if self.yakalama:
            if basildi and vk not in self.degistirici:
                self.yakalama = False
                self.yutulacak.add(vk)
                return YAKALANDI, Kisayol(vk, degistiriciler)
            return GECIR, None

        if vk in self.yutulacak:
            if not basildi:
                self.yutulacak.discard(vk)
            return YUT, None

        if not self.uzakta:
            if basildi and self.git.eslesir(vk, degistiriciler):
                if not (bagli and kullanilabilir):
                    return KULLANILAMAZ, None
                self.yutulacak.add(vk)
                self.uzakta = True
                self.uzak_basili.clear()
                return UZAGA_GEC, None
            return GECIR, None

        if basildi and self.don.eslesir(vk, degistiriciler):
            self.yutulacak.add(vk)
            self.geri_al()
            return GERI_DON, None
        if basildi:
            self.uzak_basili.add(vk)
            return GONDER, None
        if vk in self.uzak_basili:
            self.uzak_basili.discard(vk)
            return GONDER, None
        # Uzaga gecmeden once basilmis bir tusun birakilmasi (or. Ctrl+Alt+M
        # kisayolundaki Ctrl): yerelde islensin ki orada basili kalmasin.
        return GECIR, None
