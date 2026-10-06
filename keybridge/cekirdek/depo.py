"""Ayarlar ve eslesmeler icin JSON deposu (iki platform ortak).

Ayarlarin hepsi yoneten tarafta tutulur; karsi tarafi ilgilendirenler (fare
hizi, Ctrl/Cmd vb.) her baglantida ve her degisiklikte oraya gonderilir.
Yonetilen taraf yalnizca kimligini ve eslesmeleri saklar.
"""

import base64
import json
import os
import threading
import uuid

from cekirdek import tuslar

# Karsi tarafa gonderilen ayarlar
UZAK_AYARLAR = ("fare_hizi", "teker_hizi", "teker_ters", "ctrl_cmd")


def varsayilanlar(platform):
    git, don = tuslar.VARSAYILAN_KISAYOL[platform]
    return {
        "git_tusu": git, "don_tusu": don,
        "fare_hizi": 1.0, "teker_hizi": 1.0, "teker_ters": False, "ctrl_cmd": False,
        "pano": True, "dosya": True, "ses": True, "secili": None,
    }


class Depo:
    def __init__(self, yol, varsayilan, ad_bul, koru=lambda b: b, coz=lambda b: b):
        """koru/coz: eslesme anahtarlarini diske yazmadan once sifreleyen islevler
        (Windows'ta DPAPI). ad_bul(): bu bilgisayarin gorunen adi."""
        self.yol = yol
        self._ad_bul = ad_bul
        self._koru, self._coz = koru, coz
        self._kilit = threading.Lock()
        os.makedirs(os.path.dirname(yol), exist_ok=True)
        try:
            with open(yol, encoding="utf-8") as f:
                self._veri = json.load(f)
        except (OSError, ValueError):
            self._veri = {}
        degisti = False
        for anahtar, deger in varsayilan.items():
            if anahtar not in self._veri:
                self._veri[anahtar] = json.loads(json.dumps(deger))
                degisti = True
        if "kimlik" not in self._veri:
            self._veri["kimlik"] = str(uuid.uuid4())
            degisti = True
        if "eslesmeler" not in self._veri:
            self._veri["eslesmeler"] = {}
            degisti = True
        if degisti:
            self._kaydet()

    def _kaydet(self):
        gecici = self.yol + ".tmp"
        # Eslesme anahtarlari iceriyor: yalnizca bu kullanici okuyabilsin.
        fd = os.open(gecici, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(self._veri, f, ensure_ascii=False, indent=2)
        os.replace(gecici, self.yol)

    def get(self, anahtar, varsayilan=None):
        with self._kilit:
            return self._veri.get(anahtar, varsayilan)

    def set(self, anahtar, deger):
        with self._kilit:
            self._veri[anahtar] = deger
            self._kaydet()

    def ben(self):
        return {"id": self._veri["kimlik"], "ad": self._ad_bul()}

    def uzak_ayarlar(self):
        with self._kilit:
            return {a: self._veri[a] for a in UZAK_AYARLAR if a in self._veri}

    # ---- eslesmeler ----
    def anahtar_bul(self, kimlik):
        with self._kilit:
            kayit = self._veri["eslesmeler"].get(kimlik)
        if not kayit:
            return None
        try:
            return self._coz(base64.b64decode(kayit["anahtar"]))
        except (OSError, ValueError, KeyError):
            return None

    def anahtar_kaydet(self, kimlik, ad, anahtar):
        korunmus = base64.b64encode(self._koru(anahtar)).decode("ascii")
        with self._kilit:
            self._veri["eslesmeler"][kimlik] = {"ad": ad, "anahtar": korunmus}
            self._kaydet()

    def eslesmeyi_sil(self, kimlik):
        with self._kilit:
            self._veri["eslesmeler"].pop(kimlik, None)
            self._kaydet()

    def eslesmeleri_sifirla(self):
        with self._kilit:
            self._veri["eslesmeler"] = {}
            self._kaydet()

    def eslesmeler(self):
        with self._kilit:
            return {k: v["ad"] for k, v in self._veri["eslesmeler"].items()}
