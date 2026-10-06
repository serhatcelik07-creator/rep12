"""Mac'te uzaktan gelen tus ve fare olaylarini uygular (yonetilen taraf: PC->Mac).

Erisilebilirlik izni gerekir (Sistem Ayarlari > Gizlilik ve Guvenlik > Erisilebilirlik).
"""

import time

import Quartz as Q

from cekirdek import tuslar

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
TIK_PIKSEL = 40  # bir teker tiki (Windows'ta 120 birim) kac piksel kaysin


def izin_var():
    return bool(Q.CGPreflightPostEventAccess())


def izin_iste():
    """Sistem izin penceresini acar (yalnizca ilk seferde gorunur)."""
    Q.CGRequestPostEventAccess()


class Uygulayici:
    def __init__(self):
        self.ayarlar = {"fare_hizi": 1.0, "teker_hizi": 1.0, "teker_ters": False, "ctrl_cmd": False}
        self.kaynak = Q.CGEventSourceCreate(Q.kCGEventSourceStateHIDSystemState)
        self.basili_tuslar = set()
        self.basili_dugmeler = set()
        self.bayraklar = 0
        self.son_tik = (0.0, 0, None)
        self.tik_sayisi = 1
        self._artik = [0.0, 0.0]

    def ayarla(self, ayarlar):
        self.ayarlar.update({k: v for k, v in ayarlar.items() if k in self.ayarlar})

    @staticmethod
    def _post(olay):
        Q.CGEventPost(Q.kCGHIDEventTap, olay)

    # ---- klavye ----
    def tus(self, scan, genis, basildi):
        anahtar = (scan, 1 if genis else 0)
        if self.ayarlar["ctrl_cmd"]:
            # Windows'taki Ctrl+C / Ctrl+V aliskanligi Mac'te Cmd+C / Cmd+V olsun.
            anahtar = tuslar.CTRL_CMD_TAKAS.get(anahtar, anahtar)
        kod = (tuslar.SCAN_MAC_GENIS if anahtar[1] else tuslar.SCAN_MAC).get(anahtar[0])
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
            self._post(olay)
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
        self._post(olay)

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
        hiz = float(self.ayarlar["fare_hizi"])
        dx, dy = dx * hiz, dy * hiz
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
        self._post(olay)

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
        self._post(olay)

    def teker(self, dikey, yatay):
        # Windows'ta 120 = bir tik. Mac'te piksel biriminde kaydiriyoruz.
        carpan = TIK_PIKSEL * float(self.ayarlar["teker_hizi"]) / 120 * (-1 if self.ayarlar["teker_ters"] else 1)
        self._artik[0] += dikey * carpan
        self._artik[1] += -yatay * carpan
        dy, dx = int(self._artik[0]), int(self._artik[1])
        self._artik[0] -= dy
        self._artik[1] -= dx
        if dy == 0 and dx == 0:
            return
        olay = Q.CGEventCreateScrollWheelEvent(self.kaynak, Q.kCGScrollEventUnitPixel, 2, dy, dx)
        Q.CGEventSetFlags(olay, self.bayraklar)
        self._post(olay)

    def hepsini_birak(self):
        for kod in list(self.basili_tuslar):
            olay = Q.CGEventCreateKeyboardEvent(self.kaynak, kod, False)
            if kod in DEGISTIRICI:
                Q.CGEventSetType(olay, Q.kCGEventFlagsChanged)
            Q.CGEventSetFlags(olay, 0)
            self._post(olay)
        self.basili_tuslar.clear()
        self.bayraklar = 0
        for no in list(self.basili_dugmeler):
            self.dugme(no, False)
