"""Ortak pano: metin, resim ve dosyalarin iki bilgisayar arasinda aktarimi.

Kural (Synergy'deki gibi): kontrol bir bilgisayardan otekine gecerken,
terk edilen bilgisayarin panosu degistiyse otekine gonderilir. Boylece bir
tarafta Kopyala, oteki tarafta Yapistir calisir; surekli trafik olmaz.

Pano icerigi platformdan bagimsiz bir sozluktur:
  {"tur": "metin", "metin": str}
  {"tur": "resim", "png": bytes}
  {"tur": "dosyalar", "yollar": [mutlak yol, ...]}
Dosyalar alan tarafta onbellek klasorune yazilir ve oradaki yollar panoya
konur; kullanici Finder/Gezgin'de Yapistir deyince oradan kopyalanir.
"""

import json
import os
import shutil
import time

from cekirdek import protokol as p

PARCA = 32 * 1024
BELLEK_SINIRI = 64 * 1024 * 1024        # metin/resim icin
VARSAYILAN_DOSYA_SINIRI = 2 * 1024 ** 3  # dosya aktarimi icin (2 GB)


class AktarimHatasi(Exception):
    pass


# ---------------------------------------------------------------- gonderme
def _dosya_listesi(yollar):
    """Ust duzey yollari (klasorler dahil) goreli bir listeye acar."""
    girdiler, kaynaklar, ustler = [], [], []
    for yol in yollar:
        yol = os.path.abspath(yol)
        ad = os.path.basename(yol.rstrip("\\/")) or "dosya"
        ustler.append(ad)
        if os.path.isdir(yol):
            girdiler.append({"yol": ad, "klasor": True})
            for kok, klasorler, dosyalar in os.walk(yol):
                klasorler.sort()
                goreli_kok = os.path.relpath(kok, os.path.dirname(yol))
                for k in klasorler:
                    girdiler.append({"yol": _birlestir(goreli_kok, k), "klasor": True})
                for d in sorted(dosyalar):
                    tam = os.path.join(kok, d)
                    if os.path.isfile(tam) and not os.path.islink(tam):
                        girdiler.append({"yol": _birlestir(goreli_kok, d), "boyut": os.path.getsize(tam)})
                        kaynaklar.append(tam)
        elif os.path.isfile(yol):
            girdiler.append({"yol": ad, "boyut": os.path.getsize(yol)})
            kaynaklar.append(yol)
    return girdiler, kaynaklar, ustler


def _birlestir(kok, ad):
    parcalar = [] if kok in (".", "") else kok.replace("\\", "/").split("/")
    return "/".join(parcalar + [ad])


def aktarim_mesajlari(no, icerik, dosya_siniri=VARSAYILAN_DOSYA_SINIRI):
    """Bir pano icerigini kanal uzerinden gonderilecek ham mesajlara cevirir (uretec)."""
    tur = icerik["tur"]
    if tur in ("metin", "resim"):
        veri = icerik["metin"].encode("utf-8") if tur == "metin" else icerik["png"]
        if len(veri) > BELLEK_SINIRI:
            return
        yield p.json_mesaji(p.MSG_PANO_BASLA, {"no": no, "tur": tur, "boyut": len(veri)})
        for i in range(0, len(veri), PARCA):
            yield p.parca_mesaji(no, veri[i:i + PARCA])
        yield p.bitti_mesaji(no)
        return
    if tur != "dosyalar":
        return
    girdiler, kaynaklar, ustler = _dosya_listesi(icerik["yollar"])
    toplam = sum(g.get("boyut", 0) for g in girdiler)
    if not girdiler or toplam > dosya_siniri:
        return
    yield p.json_mesaji(p.MSG_PANO_BASLA, {"no": no, "tur": "dosyalar", "boyut": toplam,
                                           "girdiler": girdiler, "ustler": ustler})
    for kaynak in kaynaklar:
        with open(kaynak, "rb") as f:
            while True:
                parca = f.read(PARCA)
                if not parca:
                    break
                yield p.parca_mesaji(no, parca)
    yield p.bitti_mesaji(no)


# ---------------------------------------------------------------- alma
def _guvenli_yol(kok, goreli):
    """Karsi tarafin gonderdigi yolun onbellek klasorunun disina cikmamasini saglar."""
    goreli = goreli.replace("\\", "/")
    parcalar = [x for x in goreli.split("/") if x not in ("", ".")]
    if goreli.startswith("/") or not parcalar or any(x == ".." or ":" in x for x in parcalar):
        raise AktarimHatasi(f"gecersiz yol: {goreli!r}")
    tam = os.path.abspath(os.path.join(kok, *parcalar))
    if os.path.commonpath([tam, os.path.abspath(kok)]) != os.path.abspath(kok):
        raise AktarimHatasi(f"gecersiz yol: {goreli!r}")
    return tam


class PanoAlici:
    """Gelen pano aktarimini birlestirir. Tamamlaninca icerigi dondurur."""

    def __init__(self, onbellek, dosya_siniri=VARSAYILAN_DOSYA_SINIRI):
        self.onbellek = onbellek
        self.dosya_siniri = dosya_siniri
        self._aktarim = None

    def basla(self, baslik):
        self.iptal()
        tur, boyut = baslik.get("tur"), int(baslik.get("boyut", 0))
        if tur in ("metin", "resim"):
            if boyut > BELLEK_SINIRI:
                raise AktarimHatasi("cok buyuk")
            self._aktarim = {"no": baslik["no"], "tur": tur, "veri": bytearray(), "boyut": boyut}
            return
        if tur != "dosyalar" or boyut > self.dosya_siniri:
            raise AktarimHatasi("desteklenmeyen ya da cok buyuk aktarim")
        klasor = os.path.join(self.onbellek, time.strftime("%Y%m%d-%H%M%S") + f"-{baslik['no']}")
        os.makedirs(klasor, exist_ok=True)
        try:
            dosyalar = []
            for g in baslik["girdiler"]:
                tam = _guvenli_yol(klasor, g["yol"])
                if g.get("klasor"):
                    os.makedirs(tam, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(tam), exist_ok=True)
                    dosyalar.append((tam, int(g["boyut"])))
            ustler = [_guvenli_yol(klasor, u) for u in baslik["ustler"]]
        except Exception:
            shutil.rmtree(klasor, ignore_errors=True)
            raise
        self._aktarim = {"no": baslik["no"], "tur": "dosyalar", "klasor": klasor, "dosyalar": dosyalar,
                         "sira": 0, "acik": None, "kalan": 0, "ustler": ustler}
        self._sonraki_dosya()

    def _sonraki_dosya(self):
        a = self._aktarim
        if a["acik"]:
            a["acik"].close()
            a["acik"] = None
        while a["sira"] < len(a["dosyalar"]):
            yol, boyut = a["dosyalar"][a["sira"]]
            a["sira"] += 1
            a["acik"], a["kalan"] = open(yol, "wb"), boyut
            if boyut:
                return
            a["acik"].close()
            a["acik"] = None

    def parca(self, no, veri):
        a = self._aktarim
        if not a or a["no"] != no:
            return
        if a["tur"] != "dosyalar":
            a["veri"] += veri
            if len(a["veri"]) > a["boyut"]:
                self.iptal()
            return
        while veri:
            if not a["acik"]:
                self.iptal()  # beklenenden fazla veri
                return
            yazilacak = veri[:a["kalan"]]
            a["acik"].write(yazilacak)
            a["kalan"] -= len(yazilacak)
            veri = veri[len(yazilacak):]
            if a["kalan"] == 0:
                self._sonraki_dosya()

    def bitti(self, no):
        a = self._aktarim
        if not a or a["no"] != no:
            return None
        self._aktarim = None
        if a["tur"] == "metin":
            return {"tur": "metin", "metin": bytes(a["veri"]).decode("utf-8", errors="replace")}
        if a["tur"] == "resim":
            return {"tur": "resim", "png": bytes(a["veri"])}
        if a["acik"]:
            a["acik"].close()
        return {"tur": "dosyalar", "yollar": a["ustler"]}

    def iptal(self):
        a, self._aktarim = self._aktarim, None
        if a and a["tur"] == "dosyalar":
            if a["acik"]:
                a["acik"].close()
            shutil.rmtree(a["klasor"], ignore_errors=True)


def onbellegi_temizle(onbellek, gun=1):
    """Eski aktarimlardan kalan dosyalari siler."""
    if not os.path.isdir(onbellek):
        return
    sinir = time.time() - gun * 86400
    for ad in os.listdir(onbellek):
        yol = os.path.join(onbellek, ad)
        try:
            if os.path.getmtime(yol) < sinir:
                shutil.rmtree(yol, ignore_errors=True)
        except OSError:
            pass


# ---------------------------------------------------------------- esitleme
class PanoEsitleyici:
    """Platform panosu ile oturum arasindaki kopru.

    platform_pano nesnesi: sayac() -> int (her degisimde artan sayi),
    oku() -> icerik | None, yaz(icerik).
    """

    def __init__(self, platform_pano, ayar=lambda anahtar: True):
        self.pano = platform_pano
        self.ayar = ayar
        try:
            self._son = self.pano.sayac()
        except Exception:
            self._son = None

    def gerekirse_gonder(self, oturum):
        """Kontrol bu bilgisayardan ayrilirken cagrilir."""
        if not self.ayar("pano"):
            return
        try:
            sayac = self.pano.sayac()
            if sayac == self._son:
                return
            self._son = sayac
            icerik = self.pano.oku()
        except Exception:
            return
        if icerik and (icerik["tur"] != "dosyalar" or self.ayar("dosya")):
            oturum.pano_gonder(icerik)

    def geldi(self, icerik):
        if not self.ayar("pano") or (icerik["tur"] == "dosyalar" and not self.ayar("dosya")):
            return
        try:
            self.pano.yaz(icerik)
            self._son = self.pano.sayac()
        except Exception:
            pass


def json_kopya(veri):
    return json.loads(json.dumps(veri))
