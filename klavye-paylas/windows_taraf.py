"""Windows tarafi: laptop klavyesini ve faresini Mac'e yonlendirir.

  Asagi ok (↓)  -> klavye ve fare Mac'i kontrol etmeye baslar
  Yukari ok (↑) -> Windows'a geri doner (Mac modundayken ↑ Mac'e gitmez)

Ok tuslari sadece tek basina basilinca gecis yapar; Shift+↓, Ctrl+↑ gibi
kombinasyonlar o an hangi bilgisayar aktifse oraya normal sekilde gider.

Calistirma:  python windows_taraf.py            (Mac'i agda kendisi bulur)
             python windows_taraf.py --mac-ip 192.168.1.20
"""

import argparse
import ctypes
import getpass
import queue
import socket
import threading
import time

from pynput import keyboard, mouse

import ortak

GIT_TUSU = 0x28   # VK_DOWN: Mac'e gec
DON_TUSU = 0x26   # VK_UP:   Windows'a don
DEGISTIRICI_VK = {0x10, 0x11, 0x12, 0x5B, 0x5C, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5}

WM_KEYDOWN, WM_SYSKEYDOWN = 0x100, 0x104
WM_MOUSEMOVE = 0x200
WM_LBUTTONDOWN, WM_LBUTTONUP = 0x201, 0x202
WM_RBUTTONDOWN, WM_RBUTTONUP = 0x204, 0x205
WM_MBUTTONDOWN, WM_MBUTTONUP = 0x207, 0x208
WM_MOUSEWHEEL, WM_XBUTTONDOWN, WM_XBUTTONUP, WM_MOUSEHWHEEL = 0x20A, 0x20B, 0x20C, 0x20E
DUGMELER = {
    WM_LBUTTONDOWN: (1, 1), WM_LBUTTONUP: (1, 0),
    WM_RBUTTONDOWN: (2, 1), WM_RBUTTONUP: (2, 0),
    WM_MBUTTONDOWN: (3, 1), WM_MBUTTONUP: (3, 0),
}
LLKHF_EXTENDED, LLKHF_INJECTED = 0x01, 0x10 | 0x02
LLMHF_INJECTED = 0x01 | 0x02

user32 = ctypes.windll.user32


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def dpi_farkinda_ol():
    # Olcekli ekranlarda (%125, %150) imlec koordinatlari tutarli olsun.
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        user32.SetProcessDPIAware()


def _isaretli16(deger):
    deger = (deger >> 16) & 0xFFFF
    return deger - 0x10000 if deger & 0x8000 else deger


def _int16(deger):
    return max(-32768, min(32767, int(deger)))


class Paylasim:
    def __init__(self, sesli):
        self.sesli = sesli
        self.mac_modu = False
        self.bagli = False
        self.kuyruk = queue.Queue()
        self.basili = set()      # fiziksel olarak basili VK kodlari
        self.yutulacak = set()   # gecis tusu; birakilana kadar hicbir yere gitmesin
        self.merkez = (0, 0)
        self.eski_konum = POINT()
        self.kilit = threading.Lock()
        self.klavye = keyboard.Listener(win32_event_filter=self._klavye_filtresi)
        self.fare = mouse.Listener(win32_event_filter=self._fare_filtresi)

    # ---- gecisler ----
    def _gonder(self, tip, a=0, b=0, c=0):
        if self.bagli:
            self.kuyruk.put_nowait((tip, a, b, c))

    def maca_gec(self):
        with self.kilit:
            if self.mac_modu or not self.bagli:
                return
            user32.GetCursorPos(ctypes.byref(self.eski_konum))
            # Imleci ana ekranin ortasina sabitliyoruz; fare hareketleri buradan
            # olculup Mac'e gonderiliyor, boylece kenara takilma olmuyor.
            self.merkez = (user32.GetSystemMetrics(0) // 2, user32.GetSystemMetrics(1) // 2)
            user32.SetCursorPos(*self.merkez)
            self.mac_modu = True
            self._gonder(ortak.MSG_AKTIF, 1)
        print(">>> MAC'i kontrol ediyorsun (geri donmek icin ↑)")
        self._bip(880)

    def windowsa_don(self):
        with self.kilit:
            if not self.mac_modu:
                return
            self.mac_modu = False
            self._gonder(ortak.MSG_BIRAK)
            self._gonder(ortak.MSG_AKTIF, 0)
            user32.SetCursorPos(self.eski_konum.x, self.eski_konum.y)
        print("<<< WINDOWS'u kontrol ediyorsun (Mac'e gecmek icin ↓)")
        self._bip(440)

    def _bip(self, frekans):
        if self.sesli:
            import winsound
            threading.Thread(target=winsound.Beep, args=(frekans, 70), daemon=True).start()

    # ---- kancalar ----
    # Bu fonksiyonlar Windows'un dusuk seviye kancasi icinde calisir: hizli
    # donmeleri gerekir, bu yuzden ag islemi yapmaz, sadece kuyruga atarlar.
    def _klavye_filtresi(self, msg, data):
        if data.flags & LLKHF_INJECTED:
            return True
        vk = data.vkCode
        basildi = msg in (WM_KEYDOWN, WM_SYSKEYDOWN)
        baska_degistirici = any(v in DEGISTIRICI_VK for v in self.basili if v != vk)
        if basildi:
            self.basili.add(vk)
        else:
            self.basili.discard(vk)

        if vk in self.yutulacak:
            if not basildi:
                self.yutulacak.discard(vk)
            self.klavye.suppress_event()

        if not self.mac_modu:
            if basildi and vk == GIT_TUSU and self.bagli and not baska_degistirici:
                self.yutulacak.add(vk)
                self.maca_gec()
                self.klavye.suppress_event()
            return True

        if basildi and vk == DON_TUSU and not baska_degistirici:
            self.yutulacak.add(vk)
            self.windowsa_don()
            self.klavye.suppress_event()
        # AltGr, Windows'ta sahte bir sol Ctrl uretir (scan kodu 0x21D); onu atla.
        if data.scanCode and not data.scanCode & 0x200:
            self._gonder(ortak.MSG_TUS, data.scanCode & 0xFF,
                         1 if data.flags & LLKHF_EXTENDED else 0, 1 if basildi else 0)
        self.klavye.suppress_event()

    def _fare_filtresi(self, msg, data):
        if not self.mac_modu or data.flags & LLMHF_INJECTED:
            return True
        if msg == WM_MOUSEMOVE:
            dx, dy = data.pt.x - self.merkez[0], data.pt.y - self.merkez[1]
            if dx or dy:
                self._gonder(ortak.MSG_HAREKET, _int16(dx), _int16(dy))
        elif msg in DUGMELER:
            self._gonder(ortak.MSG_DUGME, *DUGMELER[msg])
        elif msg in (WM_XBUTTONDOWN, WM_XBUTTONUP):
            x = (data.mouseData >> 16) & 0xFFFF
            self._gonder(ortak.MSG_DUGME, 4 if x == 1 else 5, 1 if msg == WM_XBUTTONDOWN else 0)
        elif msg == WM_MOUSEWHEEL:
            self._gonder(ortak.MSG_TEKER, _isaretli16(data.mouseData), 0)
        elif msg == WM_MOUSEHWHEEL:
            self._gonder(ortak.MSG_TEKER, 0, _isaretli16(data.mouseData))
        self.fare.suppress_event()

    # ---- ag ----
    def _mac_bul(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", ortak.KESIF_PORT))
        s.settimeout(3)
        try:
            while True:
                try:
                    paket, adres = s.recvfrom(256)
                except socket.timeout:
                    print("    Mac araniyor... (Mac'te mac_taraf.py calisiyor mu?)")
                    continue
                if paket.startswith(ortak.KESIF_IMZA):
                    geri = paket[len(ortak.KESIF_IMZA):]
                    port = int.from_bytes(geri[:2], "big")
                    ad = geri[2:].decode(errors="replace")
                    return adres[0], port, ad
        finally:
            s.close()

    def ag_dongusu(self, anahtar, mac_ip, port):
        while True:
            if mac_ip:
                hedef, hedef_port, ad = mac_ip, port, mac_ip
            else:
                hedef, hedef_port, ad = self._mac_bul()
            try:
                sock = socket.create_connection((hedef, hedef_port), timeout=5)
            except OSError as e:
                print(f"[!] {hedef}:{hedef_port} adresine baglanilamadi: {e}")
                time.sleep(2)
                continue
            try:
                ortak.tcp_ayarla(sock)
                kanal = ortak.el_sikis_windows(sock, anahtar)
            except Exception:
                print("[!] Mac'e baglanildi ama sifre uyusmuyor. Iki tarafta ayni sifreyi kullan.")
                sock.close()
                time.sleep(3)
                continue
            print(f"[+] Mac'e baglanildi: {ad} ({hedef}). Mac'e gecmek icin ↓")
            while not self.kuyruk.empty():
                self.kuyruk.get_nowait()
            self.bagli = True
            sock.settimeout(5)
            okuyucu = threading.Thread(target=self._okuyucu, args=(kanal,), daemon=True)
            okuyucu.start()
            sebep = "Mac cevap vermiyor"
            try:
                # Fare surekli hareket etse bile her saniye ping at; Mac'in cevaplari
                # okuyucuyu canli tutar.
                son_ping = 0.0
                while okuyucu.is_alive():
                    try:
                        mesaj = self.kuyruk.get(timeout=0.5)
                        kanal.gonder(*mesaj)
                    except queue.Empty:
                        pass
                    if time.monotonic() - son_ping >= 1:
                        kanal.gonder(ortak.MSG_PING)
                        son_ping = time.monotonic()
            except Exception as e:
                sebep = str(e) or type(e).__name__
            # Baglanti koptu: klavye Windows'ta kalsin ki kullanici kilitlenmesin.
            self.bagli = False
            self.windowsa_don()
            sock.close()
            print(f"[-] Mac baglantisi koptu ({sebep}), yeniden deneniyor...")
            time.sleep(1)

    @staticmethod
    def _okuyucu(kanal):
        # Mac her ping'e cevap verir; 5 sn cevap gelmezse baglanti olmus demektir.
        try:
            while True:
                kanal.al()
        except Exception:
            pass

    def calistir(self, anahtar, mac_ip, port):
        self.klavye.start()
        self.fare.start()
        threading.Thread(target=self.ag_dongusu, args=(anahtar, mac_ip, port), daemon=True).start()
        print("Hazir. Kapatmak icin bu pencerede Ctrl+C (Windows modundayken).")
        try:
            while self.klavye.is_alive() and self.fare.is_alive():
                self.klavye.join(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            self.windowsa_don()
            self.klavye.stop()
            self.fare.stop()


def main():
    p = argparse.ArgumentParser(description="Windows klavye/faresini Mac'te kullan (Windows tarafi)")
    p.add_argument("--sifre", help="Iki tarafta ayni olmali (verilmezse sorulur)")
    p.add_argument("--mac-ip", help="Mac'in IP adresi (verilmezse agda otomatik bulunur)")
    p.add_argument("--port", type=int, default=ortak.TCP_PORT)
    p.add_argument("--sessiz", action="store_true", help="Geciste bip sesi calma")
    args = p.parse_args()

    sifre = args.sifre or getpass.getpass("Sifre (Mac'tekiyle ayni): ")
    if not sifre:
        raise SystemExit("Sifre bos olamaz.")
    dpi_farkinda_ol()
    Paylasim(not args.sessiz).calistir(ortak.ana_anahtar(sifre), args.mac_ip, args.port)


if __name__ == "__main__":
    main()
