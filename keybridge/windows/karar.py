"""Klavye olaylarinda ne yapilacagina karar veren saf mantik.

Windows'a ozgu hicbir sey icermez; bu sayede her platformda test edilebilir.
motor.py bu kararlari Windows kancalarina uygular.
"""

DEGISTIRICILER = {
    "ctrl": frozenset({0x11, 0xA2, 0xA3}),
    "shift": frozenset({0x10, 0xA0, 0xA1}),
    "alt": frozenset({0x12, 0xA4, 0xA5}),
    "win": frozenset({0x5B, 0x5C}),
}
_SIRA = ("ctrl", "alt", "shift", "win")
_ADLAR = {"ctrl": "Ctrl", "alt": "Alt", "shift": "Shift", "win": "Win"}

VK_ADLARI = {
    0x08: "Backspace", 0x09: "Tab", 0x0D: "Enter", 0x13: "Pause", 0x14: "Caps Lock",
    0x1B: "Esc", 0x20: "Boşluk", 0x21: "Page Up", 0x22: "Page Down", 0x23: "End",
    0x24: "Home", 0x25: "←", 0x26: "↑", 0x27: "→", 0x28: "↓", 0x2C: "Print Screen",
    0x2D: "Insert", 0x2E: "Delete", 0x5D: "Menü", 0x90: "Num Lock", 0x91: "Scroll Lock",
    0x60: "Num 0", 0x61: "Num 1", 0x62: "Num 2", 0x63: "Num 3", 0x64: "Num 4",
    0x65: "Num 5", 0x66: "Num 6", 0x67: "Num 7", 0x68: "Num 8", 0x69: "Num 9",
    0x6A: "Num *", 0x6B: "Num +", 0x6D: "Num -", 0x6E: "Num .", 0x6F: "Num /",
}
VK_ADLARI.update({0x30 + i: str(i) for i in range(10)})
VK_ADLARI.update({0x41 + i: chr(0x41 + i) for i in range(26)})
VK_ADLARI.update({0x70 + i: f"F{i + 1}" for i in range(24)})

# motor.py'nin uygulayacagi eylemler
GECIR = "gecir"            # Windows'a normal sekilde gitsin
YUT = "yut"                # hicbir yere gitmesin
GONDER = "gonder"          # Windows'a gitmesin, Mac'e gonderilsin
MACA_GEC = "maca_gec"
WINDOWSA_DON = "windowsa_don"
YAKALANDI = "yakalandi"    # ayarlarda yeni kisayol secildi
KULLANILAMAZ = "kullanilamaz"  # gecis tusuna basildi ama baglanti/lisans yok


def degistirici_adi(vk):
    for ad, kodlar in DEGISTIRICILER.items():
        if vk in kodlar:
            return ad
    return None


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

    def metin(self):
        parcalar = [_ADLAR[d] for d in _SIRA if d in self.degistiriciler]
        parcalar.append(VK_ADLARI.get(self.vk, f"Tuş {self.vk:#04x}"))
        return " + ".join(parcalar)

    def __eq__(self, diger):
        return isinstance(diger, Kisayol) and (self.vk, self.degistiriciler) == (diger.vk, diger.degistiriciler)

    def __hash__(self):
        return hash((self.vk, self.degistiriciler))

    def __repr__(self):
        return f"Kisayol({self.metin()!r})"


class KlavyeKarari:
    def __init__(self, git, don):
        self.git = git
        self.don = don
        self.mac_modu = False
        self.basili = set()       # fiziksel olarak basili VK kodlari
        self.yutulacak = set()    # birakilana kadar hicbir yere gitmeyecek tuslar
        self.mac_basili = set()   # basilma olayi Mac'e gonderilmis tuslar
        self.yakalama = False

    def _basili_degistiriciler(self, haric):
        return frozenset(filter(None, (degistirici_adi(v) for v in self.basili if v != haric)))

    def yakalamaya_basla(self):
        self.yakalama = True

    def windows_moduna_al(self):
        """Baglanti koptugunda motor cagirir."""
        self.mac_modu = False
        self.mac_basili.clear()

    def olay(self, vk, basildi, bagli=True, kullanilabilir=True):
        """Bir tus olayi icin (eylem, ek) dondurur."""
        degistiriciler = self._basili_degistiriciler(vk)
        if basildi:
            self.basili.add(vk)
        else:
            self.basili.discard(vk)

        if self.yakalama:
            if basildi and degistirici_adi(vk) is None:
                self.yakalama = False
                self.yutulacak.add(vk)
                return YAKALANDI, Kisayol(vk, degistiriciler)
            return GECIR, None

        if vk in self.yutulacak:
            if not basildi:
                self.yutulacak.discard(vk)
            return YUT, None

        if not self.mac_modu:
            if basildi and self.git.eslesir(vk, degistiriciler):
                if not (bagli and kullanilabilir):
                    return KULLANILAMAZ, None
                self.yutulacak.add(vk)
                self.mac_modu = True
                self.mac_basili.clear()
                return MACA_GEC, None
            return GECIR, None

        if basildi and self.don.eslesir(vk, degistiriciler):
            self.yutulacak.add(vk)
            self.windows_moduna_al()
            return WINDOWSA_DON, None
        if basildi:
            self.mac_basili.add(vk)
            return GONDER, None
        if vk in self.mac_basili:
            self.mac_basili.discard(vk)
            return GONDER, None
        # Mac'e gecmeden once basilmis bir tusun birakilmasi (or. Ctrl+Alt+M
        # kisayolundaki Ctrl): Windows'a gitsin ki orada basili kalmasin.
        return GECIR, None
