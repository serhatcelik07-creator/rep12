"""Mac tarafi: Windows'tan gelen klavye ve fare olaylarini Mac'te uygular.

Calistirma:  python3 mac_taraf.py
Ilk calistirmada Sistem Ayarlari > Gizlilik ve Guvenlik > Erisilebilirlik
listesinde Terminal'e (veya python'a) izin vermen gerekir.
"""

import argparse
import getpass
import socket
import threading
import time

import Quartz as Q

import ortak

# Windows scan kodu (set 1) -> Mac sanal tus kodu. Konuma gore eslenir; hangi
# karakterin cikacagini Mac'te secili klavye duzeni (or. Turkce Q) belirler.
NORMAL = {
    0x01: 53, 0x02: 18, 0x03: 19, 0x04: 20, 0x05: 21, 0x06: 23, 0x07: 22,
    0x08: 26, 0x09: 28, 0x0A: 25, 0x0B: 29, 0x0C: 27, 0x0D: 24, 0x0E: 51,
    0x0F: 48, 0x10: 12, 0x11: 13, 0x12: 14, 0x13: 15, 0x14: 17, 0x15: 16,
    0x16: 32, 0x17: 34, 0x18: 31, 0x19: 35, 0x1A: 33, 0x1B: 30, 0x1C: 36,
    0x1D: 59, 0x1E: 0, 0x1F: 1, 0x20: 2, 0x21: 3, 0x22: 5, 0x23: 4,
    0x24: 38, 0x25: 40, 0x26: 37, 0x27: 41, 0x28: 39, 0x29: 50, 0x2A: 56,
    0x2B: 42, 0x2C: 6, 0x2D: 7, 0x2E: 8, 0x2F: 9, 0x30: 11, 0x31: 45,
    0x32: 46, 0x33: 43, 0x34: 47, 0x35: 44, 0x36: 60, 0x37: 67, 0x38: 58,
    0x39: 49, 0x3A: 57, 0x3B: 122, 0x3C: 120, 0x3D: 99, 0x3E: 118,
    0x3F: 96, 0x40: 97, 0x41: 98, 0x42: 100, 0x43: 101, 0x44: 109,
    0x45: 113, 0x46: 107, 0x47: 89, 0x48: 91, 0x49: 92, 0x4A: 78, 0x4B: 86,
    0x4C: 87, 0x4D: 88, 0x4E: 69, 0x4F: 83, 0x50: 84, 0x51: 85, 0x52: 82,
    0x53: 65, 0x56: 10, 0x57: 103, 0x58: 111,
}
GENISLETILMIS = {
    0x1C: 76, 0x1D: 62, 0x45: 71, 0x35: 75, 0x37: 105, 0x38: 61, 0x47: 115, 0x48: 126,
    0x49: 116, 0x4B: 123, 0x4D: 124, 0x4F: 119, 0x50: 125, 0x51: 121,
    0x52: 114, 0x53: 117, 0x5B: 55, 0x5C: 54, 0x5D: 110,
}

SHIFT, CONTROL, OPTION, COMMAND = 0x20000, 0x40000, 0x80000, 0x100000
DEGISTIRICI = {56: SHIFT, 60: SHIFT, 59: CONTROL, 62: CONTROL,
               58: OPTION, 61: OPTION, 55: COMMAND, 54: COMMAND}
# Gercek Mac klavyesi ok/gezinme tuslarinda bu bayraklari da gonderir.
NUMPAD_FN = 0x200000 | 0x800000
FN = 0x800000
OK_TUSLARI = {123, 124, 125, 126}
FN_TUSLARI = {115, 116, 117, 119, 121, 114, 122, 120, 99, 118, 96, 97,
              98, 100, 101, 109, 103, 111, 105, 107}

DUGME_OLAY = {
    1: (Q.kCGEventLeftMouseDown, Q.kCGEventLeftMouseUp, Q.kCGMouseButtonLeft),
    2: (Q.kCGEventRightMouseDown, Q.kCGEventRightMouseUp, Q.kCGMouseButtonRight),
    3: (Q.kCGEventOtherMouseDown, Q.kCGEventOtherMouseUp, Q.kCGMouseButtonCenter),
    4: (Q.kCGEventOtherMouseDown, Q.kCGEventOtherMouseUp, 3),
    5: (Q.kCGEventOtherMouseDown, Q.kCGEventOtherMouseUp, 4),
}
CIFT_TIK_SURE = 0.4


class Uygulayici:
    def __init__(self, hiz, teker_hiz, ctrl_cmd):
        self.hiz = hiz
        self.teker_hiz = teker_hiz
        self.kaynak = Q.CGEventSourceCreate(Q.kCGEventSourceStateHIDSystemState)
        self.basili_tuslar = set()
        self.basili_dugmeler = set()
        self.bayraklar = 0
        self.son_tik = (0.0, 0, None)  # zaman, dugme, konum
        self.tik_sayisi = 1
        self.esle = dict(NORMAL), dict(GENISLETILMIS)
        if ctrl_cmd:
            # Windows'taki Ctrl+C / Ctrl+V aliskanligi Mac'te Cmd+C / Cmd+V olsun.
            normal, genis = self.esle
            normal[0x1D], genis[0x1D], genis[0x5B], genis[0x5C] = 55, 54, 59, 62

    # ---- klavye ----
    def tus(self, scan, genis, basildi):
        kod = self.esle[1 if genis else 0].get(scan)
        if kod is None:
            return
        if kod in DEGISTIRICI:
            if basildi:
                self.basili_tuslar.add(kod)
            else:
                self.basili_tuslar.discard(kod)
            self._bayraklari_hesapla()
            olay = Q.CGEventCreateKeyboardEvent(self.kaynak, kod, bool(basildi))
            Q.CGEventSetType(olay, Q.kCGEventFlagsChanged)
            Q.CGEventSetFlags(olay, self.bayraklar)
            Q.CGEventPost(Q.kCGHIDEventTap, olay)
            return
        tekrar = basildi and kod in self.basili_tuslar
        if basildi:
            self.basili_tuslar.add(kod)
        else:
            self.basili_tuslar.discard(kod)
        olay = Q.CGEventCreateKeyboardEvent(self.kaynak, kod, bool(basildi))
        ek = NUMPAD_FN if kod in OK_TUSLARI else FN if kod in FN_TUSLARI else 0
        Q.CGEventSetFlags(olay, self.bayraklar | ek)
        if tekrar:
            Q.CGEventSetIntegerValueField(olay, Q.kCGKeyboardEventAutorepeat, 1)
        Q.CGEventPost(Q.kCGHIDEventTap, olay)

    def _bayraklari_hesapla(self):
        self.bayraklar = 0
        for kod in self.basili_tuslar:
            self.bayraklar |= DEGISTIRICI.get(kod, 0)

    # ---- fare ----
    @staticmethod
    def _konum():
        return Q.CGEventGetLocation(Q.CGEventCreate(None))

    @staticmethod
    def _ekranda_tut(eski, x, y):
        hata, ekranlar, adet = Q.CGGetActiveDisplayList(16, None, None)
        sinirlar = [Q.CGDisplayBounds(e) for e in ekranlar[:adet]]
        if not sinirlar:
            return x, y
        for s in sinirlar:
            if Q.CGRectContainsPoint(s, (x, y)):
                return x, y
        # Ekran disina tasti: imlecin su an bulundugu ekranin kenarinda tut.
        hedef = next((s for s in sinirlar if Q.CGRectContainsPoint(s, eski)), sinirlar[0])
        x0, y0 = hedef.origin.x, hedef.origin.y
        x1, y1 = x0 + hedef.size.width - 1, y0 + hedef.size.height - 1
        return min(max(x, x0), x1), min(max(y, y0), y1)

    def hareket(self, dx, dy):
        dx, dy = dx * self.hiz, dy * self.hiz
        eski = self._konum()
        x, y = self._ekranda_tut(eski, eski.x + dx, eski.y + dy)
        if 1 in self.basili_dugmeler:
            tip, dugme = Q.kCGEventLeftMouseDragged, Q.kCGMouseButtonLeft
        elif 2 in self.basili_dugmeler:
            tip, dugme = Q.kCGEventRightMouseDragged, Q.kCGMouseButtonRight
        elif self.basili_dugmeler:
            tip, dugme = Q.kCGEventOtherMouseDragged, Q.kCGMouseButtonCenter
        else:
            tip, dugme = Q.kCGEventMouseMoved, Q.kCGMouseButtonLeft
        olay = Q.CGEventCreateMouseEvent(self.kaynak, tip, (x, y), dugme)
        Q.CGEventSetIntegerValueField(olay, Q.kCGMouseEventDeltaX, int(dx))
        Q.CGEventSetIntegerValueField(olay, Q.kCGMouseEventDeltaY, int(dy))
        Q.CGEventSetFlags(olay, self.bayraklar)
        Q.CGEventPost(Q.kCGHIDEventTap, olay)

    def dugme(self, no, basildi):
        if no not in DUGME_OLAY:
            return
        asagi, yukari, mac_dugme = DUGME_OLAY[no]
        konum = self._konum()
        if basildi:
            simdi = time.monotonic()
            zaman, son_no, son_konum = self.son_tik
            yakin = son_konum is not None and abs(son_konum.x - konum.x) < 5 and abs(son_konum.y - konum.y) < 5
            if son_no == no and simdi - zaman < CIFT_TIK_SURE and yakin:
                self.tik_sayisi += 1
            else:
                self.tik_sayisi = 1
            self.son_tik = (simdi, no, konum)
            self.basili_dugmeler.add(no)
        else:
            self.basili_dugmeler.discard(no)
        olay = Q.CGEventCreateMouseEvent(self.kaynak, asagi if basildi else yukari, konum, mac_dugme)
        Q.CGEventSetIntegerValueField(olay, Q.kCGMouseEventClickState, self.tik_sayisi)
        Q.CGEventSetFlags(olay, self.bayraklar)
        Q.CGEventPost(Q.kCGHIDEventTap, olay)

    def teker(self, dikey, yatay):
        # Windows'ta 120 = bir tik. Mac'te piksel biriminde kaydiriyoruz.
        dy = int(round(dikey / 120 * self.teker_hiz))
        dx = int(round(-yatay / 120 * self.teker_hiz))
        if dy == 0 and dx == 0:
            return
        olay = Q.CGEventCreateScrollWheelEvent(self.kaynak, Q.kCGScrollEventUnitPixel, 2, dy, dx)
        Q.CGEventSetFlags(olay, self.bayraklar)
        Q.CGEventPost(Q.kCGHIDEventTap, olay)

    def hepsini_birak(self):
        for kod in list(self.basili_tuslar):
            olay = Q.CGEventCreateKeyboardEvent(self.kaynak, kod, False)
            if kod in DEGISTIRICI:
                Q.CGEventSetType(olay, Q.kCGEventFlagsChanged)
            Q.CGEventSetFlags(olay, 0)
            Q.CGEventPost(Q.kCGHIDEventTap, olay)
        self.basili_tuslar.clear()
        self.bayraklar = 0
        for no in list(self.basili_dugmeler):
            self.dugme(no, False)


def kesif_yayini(port, dur):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    paket = ortak.KESIF_IMZA + port.to_bytes(2, "big") + socket.gethostname().encode()[:60]
    while not dur.is_set():
        try:
            s.sendto(paket, ("255.255.255.255", ortak.KESIF_PORT))
        except OSError:
            pass  # ag gecici olarak yoksa (Wi-Fi kopmasi vb.) sessizce tekrar dene
        dur.wait(1.0)


def baglantiyi_isle(sock, adres, anahtar, uyg):
    ortak.tcp_ayarla(sock)
    sock.settimeout(10)
    try:
        kanal = ortak.el_sikis_mac(sock, anahtar)
    except Exception:
        print(f"[!] {adres[0]} baglanmayi denedi ama sifre uyusmadi.")
        return
    print(f"[+] Windows baglandi: {adres[0]}")
    # Windows her saniye ping atar; 5 sn ses yoksa baglantiyi olu say.
    sock.settimeout(5)
    hatalar = set()
    try:
        while True:
            tip, a, b, c = kanal.al()
            try:
                olayi_uygula(kanal, uyg, tip, a, b, c)
            except Exception as e:
                # Tek bir olaydaki hata baglantiyi dusurmesin; her hatayi bir kez yaz.
                if (tip, type(e)) not in hatalar:
                    hatalar.add((tip, type(e)))
                    print(f"[!] Olay {tip} uygulanamadi: {e!r}")
    except Exception as e:
        print(f"[-] Baglanti koptu: {e!r}")
    finally:
        uyg.hepsini_birak()


def olayi_uygula(kanal, uyg, tip, a, b, c):
    if tip == ortak.MSG_TUS:
        uyg.tus(a, b, c)
    elif tip == ortak.MSG_HAREKET:
        uyg.hareket(a, b)
    elif tip == ortak.MSG_DUGME:
        uyg.dugme(a, b)
    elif tip == ortak.MSG_TEKER:
        uyg.teker(a, b)
    elif tip == ortak.MSG_PING:
        kanal.gonder(ortak.MSG_PING)
    elif tip == ortak.MSG_BIRAK:
        uyg.hepsini_birak()
    elif tip == ortak.MSG_AKTIF:
        print(">>> Klavye/fare simdi MAC'te" if a else "<<< Klavye/fare Windows'a dondu")


def main():
    p = argparse.ArgumentParser(description="Windows klavye/faresini Mac'te kullan (Mac tarafi)")
    p.add_argument("--sifre", help="Iki tarafta ayni olmali (verilmezse sorulur)")
    p.add_argument("--port", type=int, default=ortak.TCP_PORT)
    p.add_argument("--hiz", type=float, default=1.0, help="Fare hiz carpani (varsayilan 1.0)")
    p.add_argument("--teker-hiz", type=float, default=40, help="Bir teker tikinda kac piksel kaysin")
    p.add_argument("--ctrl-cmd", action="store_true",
                   help="Windows Ctrl tusu Mac'te Cmd gibi calissin (Ctrl+C = kopyala)")
    args = p.parse_args()

    sifre = args.sifre or getpass.getpass("Sifre (Windows'takiyle ayni): ")
    if not sifre:
        raise SystemExit("Sifre bos olamaz.")
    anahtar = ortak.ana_anahtar(sifre)
    uyg = Uygulayici(args.hiz, args.teker_hiz, args.ctrl_cmd)

    if not Q.CGPreflightPostEventAccess():
        Q.CGRequestPostEventAccess()
        print("[!] Erisilebilirlik izni gerekli: Sistem Ayarlari > Gizlilik ve Guvenlik >"
              " Erisilebilirlik'te Terminal'i acip programi yeniden baslat.")

    dur = threading.Event()
    threading.Thread(target=kesif_yayini, args=(args.port, dur), daemon=True).start()

    sunucu = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sunucu.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sunucu.bind(("0.0.0.0", args.port))
    sunucu.listen(1)
    print(f"Mac hazir, {args.port} portunda Windows bekleniyor. Cikmak icin Ctrl+C.")
    try:
        while True:
            sock, adres = sunucu.accept()
            with sock:
                baglantiyi_isle(sock, adres, anahtar, uyg)
    except KeyboardInterrupt:
        pass
    finally:
        dur.set()
        uyg.hepsini_birak()


if __name__ == "__main__":
    main()
