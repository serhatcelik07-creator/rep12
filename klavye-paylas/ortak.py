"""Windows ve Mac tarafinin ortak kullandigi protokol, sifreleme ve kesif kodu.

Baglanti: Mac dinler (TCP), Windows baglanir. Mac ayrica ayni agdaki
Windows'un onu bulabilmesi icin her saniye UDP yayini yapar.

Tum trafik paylasilan sifreden turetilen anahtarla AES-GCM ile sifrelenir;
sifreyi bilmeyen biri ne tuslari gorebilir ne de Mac'e tus gonderebilir.
"""

import hashlib
import hmac
import os
import socket
import struct

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

TCP_PORT = 24800
KESIF_PORT = 24801
KESIF_IMZA = b"KLAVYE-PAYLAS-1"

# Mesaj tipleri. Her mesaj sabit boyutlu: tip + uc adet int16.
MSG_TUS = 1        # a=scan kodu, b=genisletilmis(0/1), c=basildi(1)/birakildi(0)
MSG_HAREKET = 2    # a=dx, b=dy
MSG_DUGME = 3      # a=dugme (1 sol, 2 sag, 3 orta, 4 X1, 5 X2), b=basildi(1)/birakildi(0)
MSG_TEKER = 4      # a=dikey delta, b=yatay delta (Windows birimi, 120 = bir tik)
MSG_BIRAK = 5      # basili kalan her seyi birak (Windows'a donuldu)
MSG_PING = 6
MSG_AKTIF = 7      # a=1 Mac'e gecildi, 0 Windows'a donuldu

_MSG = struct.Struct("!Bhhh")
_UZUNLUK = struct.Struct("!H")
_TUZ = b"klavye-paylas-v1"


def ana_anahtar(sifre):
    return hashlib.scrypt(sifre.encode("utf-8"), salt=_TUZ, n=2 ** 14, r=8, p=1, dklen=32)


def _turet(anahtar, etiket, nonce_mac, nonce_win):
    return hmac.new(anahtar, etiket + nonce_mac + nonce_win, hashlib.sha256).digest()


def _tam_oku(sock, n):
    veri = b""
    while len(veri) < n:
        parca = sock.recv(n - len(veri))
        if not parca:
            raise ConnectionError("baglanti kapandi")
        veri += parca
    return veri


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
        self.sock.sendall(_UZUNLUK.pack(len(sifreli)) + sifreli)

    def al_ham(self):
        (n,) = _UZUNLUK.unpack(_tam_oku(self.sock, _UZUNLUK.size))
        sifreli = _tam_oku(self.sock, n)
        # Yanlis sifre veya kurcalanmis veri burada InvalidTag hatasi verir.
        veri = self._al.decrypt(self._nonce(self._al_sayac), sifreli, None)
        self._al_sayac += 1
        return veri

    def gonder(self, tip, a=0, b=0, c=0):
        self.gonder_ham(_MSG.pack(tip, a, b, c))

    def al(self):
        return _MSG.unpack(self.al_ham())


def el_sikis_mac(sock, anahtar):
    """Mac tarafi. Basarisiz olursa istisna firlatir."""
    nonce_mac = os.urandom(16)
    sock.sendall(nonce_mac)
    nonce_win = _tam_oku(sock, 16)
    w2m = _turet(anahtar, b"win->mac", nonce_mac, nonce_win)
    m2w = _turet(anahtar, b"mac->win", nonce_mac, nonce_win)
    kanal = SifreliKanal(sock, m2w, w2m)
    if kanal.al_ham() != b"merhaba-mac":
        raise ConnectionError("el sikisma hatali")
    kanal.gonder_ham(b"merhaba-windows")
    return kanal


def el_sikis_windows(sock, anahtar):
    """Windows tarafi. Basarisiz olursa istisna firlatir."""
    nonce_mac = _tam_oku(sock, 16)
    nonce_win = os.urandom(16)
    sock.sendall(nonce_win)
    w2m = _turet(anahtar, b"win->mac", nonce_mac, nonce_win)
    m2w = _turet(anahtar, b"mac->win", nonce_mac, nonce_win)
    kanal = SifreliKanal(sock, w2m, m2w)
    kanal.gonder_ham(b"merhaba-mac")
    # Mac de sifreyi bildigini kanitlamali; yoksa sahte bir cihaza baglaniyoruz.
    if kanal.al_ham() != b"merhaba-windows":
        raise ConnectionError("el sikisma hatali")
    return kanal


def tcp_ayarla(sock):
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
