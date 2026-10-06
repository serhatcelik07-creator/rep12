"""Iki urunun (PC->Mac ve Mac->PC) ortak kullandigi protokol.

Roller: klavyesi kullanilan bilgisayar "yoneten" (istemci), kontrol edilen
bilgisayar "yonetilen" (sunucu).

Akis:
  1. Kesif: yoneten yerel aga UDP yayini ile "kim var?" sorar, yonetilen
     kendi adiyla cevap verir.
  2. Yoneten TCP ile baglanir. Iki taraf gecici X25519 anahtarlariyla ortak
     sir uretir; tum trafik AES-GCM ile sifrelenir.
  3. Ilk baglantida eslestirme: iki ekranda ayni 6 haneli kod gorunur,
     yonetilen bilgisayarda "Izin ver" denince kalici bir eslesme anahtari
     uretilip yonetene gonderilir. Sonraki baglantilarda sorulmaz.

Sifre yok: kullanici kontrol edilecek bilgisayarda bir kere onay verir.
"""

import base64
import hashlib
import json
import os
import socket
import struct

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

UYGULAMA_ADI = "KeyBridge"
SURUM = "1.0.0"
PROTOKOL = 2

TCP_PORT = 24800
KESIF_PORT = 24801
KESIF_SORU = b"KB2?"
KESIF_CEVAP = b"KB2!"

# Sabit boyutlu mesajlar: tip + uc adet int16.
MSG_TUS = 1        # a=scan kodu, b=genisletilmis(0/1), c=basildi(1)/birakildi(0)
MSG_HAREKET = 2    # a=dx, b=dy
MSG_DUGME = 3      # a=dugme (1 sol, 2 sag, 3 orta, 4 X1, 5 X2), b=basildi(1)/birakildi(0)
MSG_TEKER = 4      # a=dikey delta, b=yatay delta (Windows birimi, 120 = bir tik)
MSG_BIRAK = 5      # basili kalan her seyi birak
MSG_PING = 6
MSG_AKTIF = 7      # a=1 kontrol uzak bilgisayara gecti, 0 geri dondu
# Degisken boyutlu mesajlar
MSG_AYAR = 8         # JSON: yoneten taraftaki ayarlar (fare hizi, Ctrl/Cmd vb.)
MSG_PANO_BASLA = 9   # JSON: pano aktarimi basliyor (tur, boyut, dosya listesi)
MSG_PANO_PARCA = 10  # 4 bayt aktarim no + veri
MSG_PANO_BITTI = 11  # 4 bayt aktarim no
_JSON_MESAJLAR = (MSG_AYAR, MSG_PANO_BASLA)

_MSG = struct.Struct("!Bhhh")
_UZUNLUK = struct.Struct("!H")
_MERHABA_MAC = b"merhaba-mac"
_MERHABA_WIN = b"merhaba-windows"
ONAY_SURESI = 120  # kullanicinin "Izin ver"e basmasi icin taninan sure (sn)


class EslesmeHatasi(Exception):
    """Eslesme reddedildi ya da anahtarlar uyusmadi."""


# ---------------------------------------------------------------- kesif
def kesif_cevabi(kimlik, ad, platform, port=TCP_PORT):
    """Yonetilen taraf (klavyesi kullanilacak olmayan bilgisayar) kendini tanitir."""
    bilgi = {"id": kimlik, "ad": ad, "platform": platform, "port": port, "v": PROTOKOL}
    return KESIF_CEVAP + json.dumps(bilgi, ensure_ascii=False).encode("utf-8")


def kesif_cevabini_coz(paket):
    if not paket.startswith(KESIF_CEVAP):
        return None
    try:
        bilgi = json.loads(paket[len(KESIF_CEVAP):].decode("utf-8"))
    except ValueError:
        return None
    if not isinstance(bilgi, dict) or bilgi.get("v") != PROTOKOL or "id" not in bilgi:
        return None
    return bilgi


# ---------------------------------------------------------------- cerceve
def _tam_oku(sock, n):
    veri = b""
    while len(veri) < n:
        parca = sock.recv(n - len(veri))
        if not parca:
            raise ConnectionError("baglanti kapandi")
        veri += parca
    return veri


def _cerceve_gonder(sock, veri):
    sock.sendall(_UZUNLUK.pack(len(veri)) + veri)


def _cerceve_al(sock):
    (n,) = _UZUNLUK.unpack(_tam_oku(sock, _UZUNLUK.size))
    return _tam_oku(sock, n)


class SifreliKanal:
    """Bir TCP soketi uzerinde sirali, sifreli mesajlasma."""

    def __init__(self, sock, gonder_anahtari, al_anahtari):
        self.sock = sock
        self._gonder = AESGCM(gonder_anahtari)
        self._al = AESGCM(al_anahtari)
        self._gonder_sayac = 0
        self._al_sayac = 0

    @staticmethod
    def _nonce(sayac):
        return b"\x00\x00\x00\x00" + sayac.to_bytes(8, "big")

    def gonder_ham(self, veri):
        sifreli = self._gonder.encrypt(self._nonce(self._gonder_sayac), veri, None)
        self._gonder_sayac += 1
        _cerceve_gonder(self.sock, sifreli)

    def al_ham(self):
        # Kurcalanmis veya yanlis anahtarla sifrelenmis veri burada InvalidTag verir.
        veri = self._al.decrypt(self._nonce(self._al_sayac), _cerceve_al(self.sock), None)
        self._al_sayac += 1
        return veri

    def gonder(self, tip, a=0, b=0, c=0):
        self.gonder_ham(sabit_mesaj(tip, a, b, c))

    def ayar_gonder(self, ayarlar):
        self.gonder_ham(json_mesaji(MSG_AYAR, ayarlar))

    def al(self):
        """Her zaman dort ogeli demet dondurur:
        sabit mesajlar (tip, a, b, c); JSON mesajlari (tip, sozluk, 0, 0);
        MSG_PANO_PARCA (tip, no, veri, 0); MSG_PANO_BITTI (tip, no, 0, 0)."""
        veri = self.al_ham()
        tip = veri[0]
        if tip in _JSON_MESAJLAR:
            return tip, json.loads(veri[1:].decode("utf-8")), 0, 0
        if tip == MSG_PANO_PARCA:
            return tip, int.from_bytes(veri[1:5], "big"), veri[5:], 0
        if tip == MSG_PANO_BITTI:
            return tip, int.from_bytes(veri[1:5], "big"), 0, 0
        return _MSG.unpack(veri)


def sabit_mesaj(tip, a=0, b=0, c=0):
    return _MSG.pack(tip, a, b, c)


def json_mesaji(tip, veri):
    return bytes([tip]) + json.dumps(veri, ensure_ascii=False).encode("utf-8")


def parca_mesaji(no, veri):
    return bytes([MSG_PANO_PARCA]) + no.to_bytes(4, "big") + veri


def bitti_mesaji(no):
    return bytes([MSG_PANO_BITTI]) + no.to_bytes(4, "big")


# ---------------------------------------------------------------- el sikisma
def _b64(veri):
    return base64.b64encode(veri).decode("ascii")


def _b64_coz(metin):
    return base64.b64decode(metin.encode("ascii"))


def _yeni_anahtar_cifti():
    gizli = X25519PrivateKey.generate()
    acik = gizli.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return gizli, acik


def _turet(ikm, tuz, etiket, uzunluk=32):
    return HKDF(algorithm=hashes.SHA256(), length=uzunluk, salt=tuz, info=etiket).derive(ikm)


def _oturum_anahtarlari(ortak_sir, eslesme_anahtari, ozet):
    ikm = ortak_sir + (eslesme_anahtari or b"")
    return _turet(ikm, ozet, b"kb2 win->mac"), _turet(ikm, ozet, b"kb2 mac->win")


def eslestirme_kodu(ortak_sir, ozet):
    """Iki ekranda gosterilen 6 haneli kod. Araya giren biri ayni kodu uretemez."""
    sayi = int.from_bytes(_turet(ortak_sir, ozet, b"kb2 kod", 4), "big") % 1_000_000
    return f"{sayi:06d}"


def kodu_bicimle(kod):
    return f"{kod[:3]} {kod[3:]}"


def istemci_el_sikis(sock, ben, hedef_id, anahtar_bul, kod_goster, anahtar_kaydet):
    """Yoneten taraf (istemci).

    ben: {"id", "ad"}; anahtar_bul(karsi_id) -> bytes | None;
    kod_goster(kod) eslestirmede karsi tarafin onayi beklenirken cagrilir;
    anahtar_kaydet(karsi_id, karsi_ad, anahtar) yeni eslesmeyi saklar.
    Basarida (kanal, karsi_bilgi) dondurur.
    """
    gizli, acik = _yeni_anahtar_cifti()
    kayitli = anahtar_bul(hedef_id)
    merhaba1 = json.dumps({"v": PROTOKOL, "id": ben["id"], "ad": ben["ad"], "pk": _b64(acik),
                           "anahtar_var": kayitli is not None}).encode("utf-8")
    _cerceve_gonder(sock, merhaba1)
    merhaba2 = _cerceve_al(sock)
    mac = json.loads(merhaba2.decode("utf-8"))
    if mac.get("v") != PROTOKOL:
        raise EslesmeHatasi("Karsi taraftaki uygulamanin surumu uyumsuz; iki uygulamayi da guncelleyin.")
    if mac.get("id") != hedef_id:
        raise EslesmeHatasi("Baglanilan cihaz beklenen bilgisayar degil.")
    ortak_sir = gizli.exchange(X25519PublicKey.from_public_bytes(_b64_coz(mac["pk"])))
    ozet = hashlib.sha256(merhaba1 + merhaba2).digest()

    if mac.get("kip") == "dogrula":
        kanal = SifreliKanal(sock, *_oturum_anahtarlari(ortak_sir, kayitli, ozet))
        kanal.gonder_ham(_MERHABA_MAC)
        if kanal.al_ham() != _MERHABA_WIN:
            raise EslesmeHatasi("Eslesme anahtari uyusmadi.")
        return kanal, mac

    # Eslestirme: once gecici anahtarlarla sifreli kanal, sonra karsi tarafta onay.
    kanal = SifreliKanal(sock, *_oturum_anahtarlari(ortak_sir, None, ozet))
    kanal.gonder_ham(_MERHABA_MAC)
    kod_goster(eslestirme_kodu(ortak_sir, ozet))
    eski_sure = sock.gettimeout()
    sock.settimeout(ONAY_SURESI + 10)
    try:
        cevap = json.loads(kanal.al_ham().decode("utf-8"))
    finally:
        sock.settimeout(eski_sure)
    if not cevap.get("izin"):
        raise EslesmeHatasi("Karsi bilgisayarda baglanti izni verilmedi.")
    anahtar_kaydet(mac["id"], mac.get("ad", ""), _b64_coz(cevap["anahtar"]))
    return kanal, mac


def sunucu_el_sikis(sock, ben, anahtar_bul, onay_iste, anahtar_kaydet):
    """Yonetilen taraf (sunucu).

    ben: {"id", "ad"}; anahtar_bul(karsi_id) -> bytes | None;
    onay_iste(karsi_ad, kod) -> bool kullaniciya sorar (bloklayabilir);
    anahtar_kaydet(karsi_id, karsi_ad, anahtar) yeni eslesmeyi saklar.
    Basarida (kanal, karsi_bilgi) dondurur.
    """
    merhaba1 = _cerceve_al(sock)
    win = json.loads(merhaba1.decode("utf-8"))
    if win.get("v") != PROTOKOL:
        raise EslesmeHatasi("Karsi taraftaki uygulamanin surumu uyumsuz.")
    kayitli = anahtar_bul(win["id"]) if win.get("anahtar_var") else None
    kip = "dogrula" if kayitli is not None else "eslestir"
    gizli, acik = _yeni_anahtar_cifti()
    merhaba2 = json.dumps({"v": PROTOKOL, "id": ben["id"], "ad": ben["ad"], "pk": _b64(acik),
                           "kip": kip}).encode("utf-8")
    _cerceve_gonder(sock, merhaba2)
    ortak_sir = gizli.exchange(X25519PublicKey.from_public_bytes(_b64_coz(win["pk"])))
    ozet = hashlib.sha256(merhaba1 + merhaba2).digest()

    w2m, m2w = _oturum_anahtarlari(ortak_sir, kayitli, ozet)
    kanal = SifreliKanal(sock, m2w, w2m)
    if kanal.al_ham() != _MERHABA_MAC:
        raise EslesmeHatasi("Anahtarlar uyusmadi.")
    if kip == "dogrula":
        kanal.gonder_ham(_MERHABA_WIN)
        return kanal, win

    izin = bool(onay_iste(win.get("ad", "?"), eslestirme_kodu(ortak_sir, ozet)))
    if not izin:
        kanal.gonder_ham(json.dumps({"izin": False}).encode("utf-8"))
        raise EslesmeHatasi("Kullanici izin vermedi.")
    anahtar = os.urandom(32)
    anahtar_kaydet(win["id"], win.get("ad", ""), anahtar)
    kanal.gonder_ham(json.dumps({"izin": True, "anahtar": _b64(anahtar)}).encode("utf-8"))
    return kanal, win


def tcp_ayarla(sock):
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
