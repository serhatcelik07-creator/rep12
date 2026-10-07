"""Akaryakıt istasyonu yerleşim planı + LPG tankı katodik koruma TASLAK DXF üretici.

Kaynak: elle çizilmiş kroki + saha fotoğrafları (Shell "Tek Tank / Tek Dispenser" LPG tesisatı).
Birim: metre (1 çizim birimi = 1 m). Krokide ölçek yok; kroki ~50 px = 1 m kabul edilerek
yerleşim ölçeklendi. Tüm ölçüler sahada TEYİT EDİLMELİDİR.

Kullanım:  python3 plan_uret.py   ->  istasyon_lpg_kk_taslak.dxf (+ önizleme .png)
"""
import math
import os
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
DXF_PATH = os.path.join(OUT_DIR, "istasyon_lpg_kk_taslak.dxf")
PNG_PATH = os.path.join(OUT_DIR, "istasyon_lpg_kk_taslak.png")

PX_PER_M = 50.0
SKETCH_H = 1850.0


def P(px, py):
    """Kroki pikselini metreye çevir (y yukarı)."""
    return (px / PX_PER_M, (SKETCH_H - py) / PX_PER_M)


# --------------------------------------------------------------------------- tasarım verisi
# Saha plakası (Shell & Turcas "Tek Tank / Tek Dispenser Tesisat Şeması") malzeme listesinden okunanlar:
#   Poz 25: 1 ad. LPG Stok Tankı, 10M3, Shell & Turcas standartlarında (şemada Ø2350 ölçüsü)
#   Poz 24: 2 ad. 10 Lb Magnezyum Anot, TSE belgeli  (tank)
#   Poz 17: 2 ad. 3,5 Lb Magnezyum Anot, TSE belgeli (dispenser tarafı)
#   Poz 13: 6 ad. İzole Flanş Kiti (YUY-SAN, PN40); hatlar SCH80 dikişsiz çelik çekme boru 1" ve 1 1/2"
# Hesapta 10 m³ tank için tipik Ø1.60 x 5.40 m kullanıldı (Ø2350'ye göre daha büyük yüzey -> emniyetli taraf).
TANK_V = 10.0
TANK_D = 1.60
TANK_L = 5.40
SOIL_RHO = 30.0          # Ω·m  (zemin özdirenci - SAHADA WENNER İLE ÖLÇÜLECEK)
I_BARE = 20.0            # mA/m²  çıplak çelik akım yoğunluğu (zemin)
COAT_BREAK = 0.10        # ömür sonu kaplama hasar oranı
SAFETY = 1.3
LIFE_Y = 20
MG_CAP = 1230.0          # Ah/kg (pratik, verim dahil)
MG_UTIL = 0.85
DRIVE_V = 1.75 - 0.85    # yüksek potansiyelli Mg (-1.75 V CSE) - koruma kriteri (-0.85 V CSE)
# hazır dolgulu Mg anot tipleri: (kg, dolgu boyu m, dolgu çapı m)
MG_TIP = {"10 Lb": (4.5, 0.60, 0.15), "3,5 Lb": (1.6, 0.40, 0.10)}
N_ANODE_TANK = 4         # 10 Lb (plakada 2 ad. -> 20 yıl için sınırda, 4 ad. önerildi)
N_ANODE_DISP = 2         # 3,5 Lb (plakadaki gibi)
PIPE_DN_OD = 0.0422      # 1 1/4" ~ 1"-1 1/2" ortalama dış çap (m)


def anot_r(tip):
    _, ln, d = MG_TIP[tip]
    return SOIL_RHO / (2 * math.pi * ln) * (math.log(8 * ln / d) - 1)  # Dwight


def kk_hesap(pipe_len):
    a_tank = math.pi * TANK_D * TANK_L + 2 * (math.pi * TANK_D ** 2 / 4) * 1.1
    a_pipe = 2 * math.pi * PIPE_DN_OD * pipe_len          # basma + geri dönüş
    a_tot = a_tank + a_pipe
    i_req = a_tot * I_BARE * COAT_BREAK * SAFETY / 1000.0          # A
    m_req = i_req * 8760 * LIFE_Y / (MG_CAP * MG_UTIL)               # kg
    r10, r35 = anot_r("10 Lb"), anot_r("3,5 Lb")
    i10, i35 = DRIVE_V / r10, DRIVE_V / r35
    i_cap = N_ANODE_TANK * i10 + N_ANODE_DISP * i35
    m_tot = N_ANODE_TANK * MG_TIP["10 Lb"][0] + N_ANODE_DISP * MG_TIP["3,5 Lb"][0]
    life = m_tot * MG_CAP * MG_UTIL / (i_req * 8760)
    life_plaka = (2 * MG_TIP["10 Lb"][0] + 2 * MG_TIP["3,5 Lb"][0]) * MG_CAP * MG_UTIL / (i_req * 8760)
    return dict(a_tank=a_tank, a_pipe=a_pipe, a_tot=a_tot, i_req=i_req, m_req=m_req, r10=r10, r35=r35,
                i10=i10, i35=i35, n=N_ANODE_TANK + N_ANODE_DISP, i_cap=i_cap, m_tot=m_tot, life=life,
                life_plaka=life_plaka)


# --------------------------------------------------------------------------- doküman
doc = ezdxf.new("R2010", setup=True)
doc.units = ezdxf.units.M
doc.header["$INSUNITS"] = 6
doc.header["$MEASUREMENT"] = 1
doc.styles.add("TR", font="arial.ttf")

LAYERS = {
    "SINIR-YOL": (8, "DASHED"),
    "BINA": (7, "Continuous"),
    "KANOPI": (4, "DASHED"),
    "POMPA-ADASI": (3, "Continuous"),
    "LPG-SAHA": (1, "Continuous"),
    "LPG-TANK": (1, "DASHED2"),
    "LPG-HAT": (6, "Continuous"),
    "KK-ANOT": (30, "Continuous"),
    "KK-KABLO": (5, "DASHED2"),
    "KK-OLCUM": (2, "Continuous"),
    "KK-IZOLASYON": (140, "Continuous"),
    "OLCU": (9, "Continuous"),
    "YAZI": (7, "Continuous"),
    "PAFTA": (7, "Continuous"),
    "TEYIT": (11, "Continuous"),
}
for name, (color, lt) in LAYERS.items():
    doc.layers.add(name, color=color, linetype=lt)

msp = doc.modelspace()
doc.header["$LTSCALE"] = 0.5


def pline(pts, layer, closed=False):
    return msp.add_lwpolyline(pts, close=closed, dxfattribs={"layer": layer})


def rect(x, y, w, h, layer):
    return pline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], layer, closed=True)


def text(s, pos, h=0.35, layer="YAZI", align=TextEntityAlignment.MIDDLE_CENTER, rot=0):
    t = msp.add_text(s, height=h, rotation=rot, dxfattribs={"layer": layer, "style": "TR"})
    t.set_placement(pos, align=align)
    return t


def mtext(s, pos, h=0.3, layer="YAZI", width=None):
    m = msp.add_mtext(s, dxfattribs={"layer": layer, "char_height": h, "style": "TR"})
    m.set_location(pos, attachment_point=1)
    if width:
        m.dxf.width = width
    return m


def dim(p1, p2, offset, layer="OLCU", txt="<>"):
    d = msp.add_aligned_dim(p1=p1, p2=p2, distance=offset, text=txt,
                            dxfattribs={"layer": layer},
                            override={"dimtxt": 0.3, "dimasz": 0.25, "dimdec": 2,
                                      "dimexe": 0.15, "dimexo": 0.1, "dimgap": 0.08})
    d.render()


# --------------------------------------------------------------------------- yerleşim (krokiden)
# Yol / parsel sınırı (sağ ve alt)
pline([P(1595, 62), P(1915, 20)], "SINIR-YOL")
pline([P(1645, 75), P(1660, 260), P(1790, 600), P(1885, 830)], "SINIR-YOL")
pline([P(1590, 155), P(1700, 380), P(1800, 640), P(1870, 820)], "SINIR-YOL")
pline([P(1888, 845), P(1885, 1300), P(1878, 1765)], "SINIR-YOL")
pline([P(680, 1800), P(900, 1780), P(1250, 1805), P(1500, 1830), P(1800, 1845)], "SINIR-YOL")
pline([P(1735, 1830), P(1880, 1750)], "SINIR-YOL")
text("YOL / PARSEL SINIRI (teyit)", P(1940, 1300), 0.45, "SINIR-YOL", rot=90)
text("YOL / PARSEL SINIRI (teyit)", P(1200, 1835), 0.45, "SINIR-YOL")

# Satış binası (üst sol)
bina1 = [P(185, 463), P(915, 410), P(915, 285), P(870, 252), P(600, 280), P(385, 355)]
pline(bina1, "BINA", closed=True)
text("SATIŞ BİNASI / MARKET (teyit)", P(600, 395), 0.5, "BINA")
# Üstteki eleman (krokide tam anlaşılamadı)
pline([P(750, 175), P(820, 165), P(860, 160), P(910, 90), P(975, 300), P(915, 330), P(820, 330)],
      "TEYIT", closed=True)
text("EK YAPI / ELEMAN ?", P(870, 230), 0.35, "TEYIT")

# Alt sol mevcut yapı
bina2 = [P(20, 1510), P(165, 1505), P(310, 1470), P(480, 1505), P(890, 1545), P(1165, 1515),
         P(1180, 1655), P(880, 1670), P(870, 1730), P(530, 1685), P(250, 1695), P(20, 1645)]
pline(bina2, "BINA", closed=True)
pline([P(480, 1505), P(480, 1665)], "BINA")
pline([P(890, 1545), P(878, 1725)], "BINA")
text("MEVCUT YAPI (yıkama/servis? - teyit)", P(560, 1600), 0.45, "BINA")
dim(P(890, 1545), P(1165, 1515), 0.6, txt="7.00 (kroki)")

# Sağdaki eleman ("Ara..." notu)
rect(*P(1715, 1235), (1820 - 1715) / PX_PER_M, (1235 - 975) / PX_PER_M, "TEYIT")
pline([P(1705, 1020), P(1840, 1020)], "TEYIT")
text("HAVA-SU / GİRİŞ ? ('Ara...' notu)", P(1770, 940), 0.3, "TEYIT")

# Pompa adaları (gerçekçi ölçü: 6.0 x 1.5 m), kroki merkezlerinde
ISL_W, ISL_H = 6.0, 1.5
adalar = [("ADA-1  BENZİN/MOTORİN", P(430, 628)),
          ("ADA-2  BENZİN/MOTORİN", P(1022, 650)),
          ("ADA-3  BENZİN/MOTORİN", P(487, 1122)),
          ("ADA-4  LPG DİSPENSERİ", P(992, 1130))]
for name, (cx, cy) in adalar:
    rect(cx - ISL_W / 2, cy - ISL_H / 2, ISL_W, ISL_H, "POMPA-ADASI")
    # dispenser gövdeleri
    for dx in (-1.6, 1.6):
        rect(cx + dx - 0.5, cy - 0.3, 1.0, 0.6, "POMPA-ADASI")
    text(name, (cx, cy + 1.1), 0.35, "POMPA-ADASI")
lpg_cx, lpg_cy = adalar[3][1]

# Kanopi
kx0, ky0 = min(a[1][0] for a in adalar) - ISL_W / 2 - 2, min(a[1][1] for a in adalar) - 2.5
kx1, ky1 = max(a[1][0] for a in adalar) + ISL_W / 2 + 2, max(a[1][1] for a in adalar) + 4
rect(kx0, ky0, kx1 - kx0, ky1 - ky0, "KANOPI")
text("KANOPİ İZDÜŞÜMÜ", ((kx0 + kx1) / 2, ky1 - 0.6), 0.4, "KANOPI")

# --------------------------------------------------------------------------- LPG tank sahası
# Kroki: üst 6 m, sağ 4 m, sağ-alt köşe 1.2 m pah. (kroki "3 m" alt notu teyit edilecek)
sx, sy_top = P(1315, 1300)
S_W, S_RIGHT, CH = 6.0, 4.0, 1.2
ch = CH / math.sqrt(2)
S_H = S_RIGHT + ch
saha = [(sx, sy_top), (sx + S_W, sy_top), (sx + S_W, sy_top - S_RIGHT),
        (sx + S_W - ch, sy_top - S_H), (sx, sy_top - S_H)]
pline(saha, "LPG-SAHA", closed=True)
# tel çit iç çizgisi (0.15 m)
off = 0.15
pline([(sx + off, sy_top - off), (sx + S_W - off, sy_top - off), (sx + S_W - off, sy_top - S_RIGHT),
       (sx + S_W - ch, sy_top - S_H + off), (sx + off, sy_top - S_H + off)], "LPG-SAHA", closed=True)
text("LPG TANK SAHASI (tel çitli, çarpma bariyerli)", (sx + S_W / 2, sy_top + 1.3), 0.35, "LPG-SAHA")
dim((sx, sy_top), (sx + S_W, sy_top), 0.4, txt="6.00")
dim((sx + S_W, sy_top), (sx + S_W, sy_top - S_RIGHT), -0.5, txt="4.00")
dim((sx + S_W, sy_top - S_RIGHT), (sx + S_W - ch, sy_top - S_H), -0.4, txt="1.20")
dim((sx, sy_top - S_H), (sx + S_W - ch, sy_top - S_H), -0.9, txt=f"{S_W - ch:.2f}")
# çarpma bariyerleri (U boru)
for i in range(4):
    bx = sx + 0.6 + i * 1.4
    pline([(bx, sy_top - S_H - 0.6), (bx + 0.8, sy_top - S_H - 0.6)], "LPG-SAHA")

# Tank (yeraltı, yatay)
tcx, tcy = sx + S_W / 2, sy_top - S_H / 2 - 0.2
t0, t1 = tcx - TANK_L / 2, tcx + TANK_L / 2
r = TANK_D / 2
pline([(t0 + r, tcy - r), (t1 - r, tcy - r)], "LPG-TANK")
pline([(t0 + r, tcy + r), (t1 - r, tcy + r)], "LPG-TANK")
msp.add_arc((t0 + r, tcy), r, 90, 270, dxfattribs={"layer": "LPG-TANK"})
msp.add_arc((t1 - r, tcy), r, 270, 90, dxfattribs={"layer": "LPG-TANK"})
msp.add_circle((tcx + 0.6, tcy), 0.3, dxfattribs={"layer": "LPG-SAHA"})  # menhol / armatür grubu
text("LPG TANKI 10 m³", (tcx - 1.2, tcy), 0.22, "LPG-TANK")
text("Tank: 10 m³ (plaka poz 25), hesapta Ø1.60 x L5.40 m kabul - etiketten teyit", (sx + S_W / 2, sy_top - S_H - 1.5), 0.25, "LPG-TANK")
text("MENHOL", (tcx + 0.6, tcy + 0.45), 0.18, "LPG-SAHA")
# Kademeli pompa
rect(sx + 0.4, sy_top - 1.1, 1.2, 0.5, "LPG-SAHA")
text("KADEMELİ POMPA", (sx + 1.0, sy_top - 0.4), 0.18, "LPG-SAHA")

# LPG hatları (emiş, basma, geri dönüş, by-pass) -> dispensere
menhol = (tcx + 0.6, tcy)
pompa = (sx + 1.0, sy_top - 0.85)
pline([menhol, (menhol[0], sy_top - 0.85), pompa], "LPG-HAT")
izf_tank = (sx - 0.05, sy_top - 0.85)
disp = (lpg_cx + 1.6, lpg_cy)
hat = [pompa, izf_tank, (izf_tank[0] - 1.0, izf_tank[1]), (disp[0] + 1.5, disp[1] - 1.5), (disp[0], disp[1] - 0.3)]
pline(hat, "LPG-HAT")
pline([(p[0], p[1] - 0.15) for p in hat], "LPG-HAT")
lbl = (hat[2][0] - 9.5, hat[2][1] - 2.2)
pline([((hat[2][0] + hat[3][0]) / 2, (hat[2][1] + hat[3][1]) / 2), (lbl[0] + 7.6, lbl[1] + 0.2)], "LPG-HAT")
mtext("LPG HATLARI: BASMA + GERİ DÖNÜŞ\\PSCH80 dikişsiz çelik, toprak altı, kaplamalı", (lbl[0], lbl[1] + 0.6), 0.22, "LPG-HAT")
pipe_len = sum(math.dist(hat[i], hat[i + 1]) for i in range(len(hat) - 1)) + 2 * math.dist(menhol, pompa)
dist_disp = math.dist((sx, sy_top - S_H / 2), (lpg_cx + ISL_W / 2, lpg_cy))
pline([(lpg_cx + ISL_W / 2, lpg_cy - ISL_H / 2), (sx, sy_top)], "OLCU")
text(f"dispenser-tank sahası ≈ {math.dist((lpg_cx + ISL_W / 2, lpg_cy - ISL_H / 2), (sx, sy_top)):.1f} m "
     "(krokide 5+5 m) - mesafeler TEYİT", (sx - 1.0, sy_top + 2.2), 0.22, "OLCU",
     align=TextEntityAlignment.MIDDLE_LEFT)

# --------------------------------------------------------------------------- KATODİK KORUMA
# İzolasyon flanşları
def izf(pt, label):
    x, y = pt
    pline([(x - 0.05, y - 0.25), (x - 0.05, y + 0.25)], "KK-IZOLASYON")
    pline([(x + 0.05, y - 0.25), (x + 0.05, y + 0.25)], "KK-IZOLASYON")
    text(label, (x, y + 0.45), 0.18, "KK-IZOLASYON")


izf((menhol[0], tcy + 0.45), "İF-1")
izf(izf_tank, "İF-2")
izf((disp[0], disp[1] - 0.6), "İF-3")

# Anotlar: tankın iki uzun kenarına 2'şer adet 10 Lb, tank yüzeyinden ~0.8 m
anotlar = []
for i, ax in enumerate((t0 + 1.6, t1 - 1.0)):
    anotlar.append((f"MA-{i * 2 + 1}", (ax, tcy + r + 0.8)))
    anotlar.append((f"MA-{i * 2 + 2}", (ax, tcy - r - 0.8)))
# dispenser tarafı: 2 adet 3,5 Lb, dispenser altındaki hat girişinin iki yanına
mid = ((hat[2][0] + hat[3][0]) / 2, (hat[2][1] + hat[3][1]) / 2 - 1.0)
anotlar.append(("MA-5", (disp[0] + 1.2, disp[1] - 1.3)))
anotlar.append(("MA-6", (disp[0] - 1.0, disp[1] - 1.3)))
for name, (ax, ay) in anotlar:
    msp.add_circle((ax, ay), 0.10, dxfattribs={"layer": "KK-ANOT"})
    msp.add_circle((ax, ay), 0.20, dxfattribs={"layer": "KK-ANOT"})
    hatch = msp.add_hatch(color=30, dxfattribs={"layer": "KK-ANOT"})
    hatch.paths.add_polyline_path([(ax + 0.10 * math.cos(a / 8 * math.pi), ay + 0.10 * math.sin(a / 8 * math.pi))
                                   for a in range(16)], is_closed=True)
    text(name + (" (10 Lb)" if int(name[3:]) <= 4 else " (3,5 Lb)"),
         (ax, ay + (0.38 if name in ("MA-1", "MA-3") else -0.38)), 0.17, "KK-ANOT")

# Ölçüm kutuları
OK1 = (sx - 0.6, sy_top - S_H + 0.5)
OK2 = (disp[0] + 0.1, disp[1] - 2.3)
for nm, (ox, oy) in (("ÖK-1", OK1), ("ÖK-2", OK2)):
    rect(ox - 0.2, oy - 0.15, 0.4, 0.3, "KK-OLCUM")
    pline([(ox - 0.2, oy - 0.15), (ox + 0.2, oy + 0.15)], "KK-OLCUM")
    text(nm, (ox, oy - 0.4), 0.2, "KK-OLCUM")
# Kalıcı referans elektrot
RE = (tcx + 0.3, tcy - r - 0.35)
msp.add_circle(RE, 0.12, dxfattribs={"layer": "KK-OLCUM"})
text("RE", (RE[0] + 0.3, RE[1]), 0.16, "KK-OLCUM")

# Kablolar: tank anotları -> ÖK-1 ; tank bağlantısı ; RE -> ÖK-1 ; MA-5/6 + hat -> ÖK-2
for name, (ax_, ay_) in anotlar[:4]:
    pline([(ax_, ay_), (sx + 0.3, ay_), (sx + 0.3, OK1[1]), (OK1[0] + 0.2, OK1[1])], "KK-KABLO")
pline([(t0 + 0.3, tcy - r), (t0 + 0.3, OK1[1] + 0.05), (OK1[0] + 0.2, OK1[1] + 0.05)], "KK-KABLO")
pline([RE, (RE[0], OK1[1] - 0.05), (OK1[0] + 0.2, OK1[1] - 0.05)], "KK-KABLO")
for name, (ax_, ay_) in anotlar[4:]:
    pline([(ax_, ay_), (ax_, OK2[1]), (OK2[0] + (0.2 if ax_ > OK2[0] else -0.2), OK2[1])], "KK-KABLO")
pline([(OK2[0], OK2[1] + 0.15), (OK2[0], disp[1] - 0.45)], "KK-KABLO")  # hat bağlantısı

# --------------------------------------------------------------------------- lejant, notlar, hesap
H = kk_hesap(pipe_len)
LX, LY = 42.0, 37.0
lejant = [
    ("SINIR-YOL", "Yol / parsel sınırı"), ("BINA", "Bina / yapı"), ("KANOPI", "Kanopi izdüşümü"),
    ("POMPA-ADASI", "Pompa adası / dispenser"), ("LPG-SAHA", "LPG tank sahası, çit"),
    ("LPG-TANK", "LPG tankı (yeraltı)"), ("LPG-HAT", "LPG hattı"),
    ("KK-ANOT", "Mg anot (MA)"), ("KK-KABLO", "KK kablosu (NYY 1x10 mm²)"),
    ("KK-OLCUM", "Ölçüm kutusu (ÖK) / referans elektrot"), ("KK-IZOLASYON", "İzolasyon flanşı (İF)"),
    ("TEYIT", "Krokiden okunamayan / teyit edilecek"),
]
text("LEJANT", (LX, LY), 0.5, align=TextEntityAlignment.LEFT)
for i, (ly, desc) in enumerate(lejant):
    y = LY - 1.0 - i * 0.6
    pline([(LX, y), (LX + 1.5, y)], ly)
    text(desc, (LX + 2.0, y), 0.28, align=TextEntityAlignment.MIDDLE_LEFT)

notlar = (
    "KATODİK KORUMA TASARIM ÖZETİ (TASLAK)\\P"
    "Sistem: Galvanik (kurban) anotlu katodik koruma - yeraltı LPG tankı + toprak altı LPG hatları\\P"
    "Standartlar: TS EN 13636 (yeraltı tank/boru KK), TS EN 12954, TS EN 13509 (ölçüm), TS EN 12068 (kaplama)\\P"
    "Koruma kriteri: Ekoff ≤ -850 mV (Cu/CuSO4), aşırı koruma sınırı -1200 mV (kaplama)\\P"
    "\\P"
    "SAHA PLAKASINDAN: Poz 25 LPG stok tankı 10 m³ | Poz 24 2 ad. 10 Lb Mg anot | Poz 17 2 ad. 3,5 Lb Mg anot\\P"
    "                  Poz 13 6 ad. izole flanş kiti | hatlar SCH80 dikişsiz çelik 1\" ve 1 1/2\"\\P"
    "\\P"
    f"Tank yüzeyi (10 m³, Ø{TANK_D} x {TANK_L} m kabul): {H['a_tank']:.1f} m²\\P"
    f"Hat yüzeyi (2 x ~{pipe_len:.0f} m)  : {H['a_pipe']:.1f} m²\\P"
    f"Toplam yüzey           : {H['a_tot']:.1f} m²\\P"
    f"Akım yoğunluğu         : {I_BARE:.0f} mA/m² x %{COAT_BREAK * 100:.0f} kaplama hasarı x {SAFETY} emniyet\\P"
    f"Gerekli akım           : {H['i_req'] * 1000:.0f} mA\\P"
    f"Zemin özdirenci (kabul): {SOIL_RHO:.0f} Ω·m  (SAHADA ÖLÇÜLECEK)\\P"
    f"Anot direnci (Dwight)  : 10 Lb {H['r10']:.1f} Ω -> {H['i10'] * 1000:.0f} mA | 3,5 Lb {H['r35']:.1f} Ω -> {H['i35'] * 1000:.0f} mA\\P"
    f"Anot sayısı            : {N_ANODE_TANK} x 10 Lb (tank) + {N_ANODE_DISP} x 3,5 Lb (dispenser) = {H['n']} adet\\P"
    f"Toplam kapasite        : {H['i_cap'] * 1000:.0f} mA  (≥ {H['i_req'] * 1000:.0f} mA  OK)\\P"
    f"Gerekli anot kütlesi   : {H['m_req']:.1f} kg / {LIFE_Y} yıl  -> tesis edilen {H['m_tot']:.1f} kg\\P"
    f"Hesaplanan ömür        : ≈ {H['life']:.0f} yıl  (plakadaki 2x10 Lb + 2x3,5 Lb ile ≈ {H['life_plaka']:.0f} yıl)\\P"
    "\\P"
    "NOTLAR\\P"
    "1. Anotlar tank alt seviyesinde, tank yüzeyinden ~0.8-1.5 m mesafede, düşey; ıslatılarak gömülecek.\\P"
    "2. Tank anotları ÖK-1, dispenser anotları ÖK-2 içinde şönt (0.01 Ω) üzerinden tank bağlantısına bağlanacak (akım ölçülebilir).\\P"
    "3. Tank bağlantısı 2 ayrı kablo ile (yedekli), termit/pin kaynağı ile yapılacak; kaynak yeri kaplanacak.\\P"
    "4. İzole flanş kitleri: tank çıkışları (İF-1), saha çıkışı (İF-2), dispenser girişi (İF-3); plakada toplam 6 ad.\\P"
    "5. Tank topraklaması KK'yı kısa devre etmemesi için DC dekuplör (polarizasyon hücresi) üzerinden.\\P"
    "6. Kalıcı Cu/CuSO4 referans elektrot tank yanına; ÖK-1'de ölçüm terminali.\\P"
    "7. Devreye alma: doğal potansiyel, ON/OFF ölçümleri, anot akımları raporlanacak; yılda 1 periyodik ölçüm.\\P"
    "8. Kroki ölçeksizdir; yerleşim ~50 px = 1 m kabulü ile çizildi. TÜM ÖLÇÜLER VE GÜVENLİK MESAFELERİ\\P"
    "    (LPG Piyasası Teknik Düzenlemeler / TS 11939) SAHADA TEYİT EDİLECEKTİR."
)
mtext(notlar, (LX, LY - 9.0), 0.26, width=26.0)

# --------------------------------------------------------------------------- detaylar
DX, DY = 42.0, 6.0
text("DETAY-A: Mg ANOT MONTAJI (ölçeksiz)", (DX, DY + 3.6), 0.35, align=TextEntityAlignment.LEFT)
pline([(DX, DY + 3.0), (DX + 6.0, DY + 3.0)], "PAFTA")                       # zemin
text("zemin kotu", (DX + 6.2, DY + 3.0), 0.2, align=TextEntityAlignment.MIDDLE_LEFT)
rect(DX + 1.0, DY + 0.0, 0.6, 1.5, "KK-ANOT")                                   # dolgu
rect(DX + 1.2, DY + 0.25, 0.2, 1.0, "KK-ANOT")                                  # Mg
pline([(DX + 1.3, DY + 1.5), (DX + 1.3, DY + 2.5), (DX + 4.0, DY + 2.5)], "KK-KABLO")
rect(DX + 4.0, DY + 2.2, 0.8, 0.6, "KK-OLCUM")
text("ÖK", (DX + 4.4, DY + 2.5), 0.2, "KK-OLCUM")
mtext("Mg anot 10 Lb / 3,5 Lb\\Pbentonit-alçı-\\Psodyum sülfat dolgu\\PNYY 1x10 mm² kablo\\Pmin. 0.8 m derinlik",
      (DX + 1.9, DY + 1.4), 0.18)

text("DETAY-B: ÖLÇÜM KUTUSU ÖK-1 BAĞLANTI ŞEMASI", (DX + 11.0, DY + 3.6), 0.35, align=TextEntityAlignment.LEFT)
bx = DX + 11.0
rect(bx, DY - 1.2, 8.0, 4.4, "KK-OLCUM")
pline([(bx + 1.0, DY + 2.6), (bx + 7.0, DY + 2.6)], "KK-OLCUM")
text("TANK BARASI (T1+T2)", (bx + 4.0, DY + 2.85), 0.2, "KK-OLCUM")
for i in range(4):
    x = bx + 1.2 + i * 1.6
    rect(x - 0.15, DY + 1.3, 0.3, 0.8, "KK-OLCUM")
    pline([(x, DY + 2.1), (x, DY + 2.6)], "KK-OLCUM")
    pline([(x, DY + 1.3), (x, DY + 0.3)], "KK-KABLO")
    text(f"MA-{i + 1}", (x, DY + 0.05), 0.18, "KK-ANOT")
    text("şönt", (x + 0.45, DY + 1.7), 0.14, "KK-OLCUM", rot=90)
text("RE terminali", (bx + 4.0, DY - 0.6), 0.2, "KK-OLCUM")

# --------------------------------------------------------------------------- pafta + antet
FX0, FY0, FX1, FY1 = -2.0, -6.0, 72.0, 41.0
rect(FX0, FY0, FX1 - FX0, FY1 - FY0, "PAFTA")
ax0 = FX1 - 22.0
rect(ax0, FY0, 22.0, 5.0, "PAFTA")
for yy in (FY0 + 1.0, FY0 + 2.0, FY0 + 3.5):
    pline([(ax0, yy), (FX1, yy)], "PAFTA")
text("AKARYAKIT + LPG İSTASYONU", (ax0 + 11, FY0 + 4.3), 0.45, "PAFTA")
text("YERLEŞİM PLANI ve LPG TANKI KATODİK KORUMA PROJESİ", (ax0 + 11, FY0 + 2.75), 0.4, "PAFTA")
text("ÖLÇEK: 1/100 (1 birim = 1 m)    PAFTA: KK-01    REV: T0 (TASLAK)", (ax0 + 11, FY0 + 1.5), 0.3, "PAFTA")
text("TARİH: 07.10.2026   ÇİZEN: -   KONTROL: -   ONAY: -", (ax0 + 11, FY0 + 0.5), 0.3, "PAFTA")
# Kuzey oku (kroki yönü bilinmiyor)
nx, ny = 3.0, 36.0
pline([(nx, ny), (nx - 0.5, ny - 1.2), (nx, ny - 0.9), (nx + 0.5, ny - 1.2)], "PAFTA", closed=True)
text("K ? (teyit)", (nx, ny + 0.4), 0.3, "TEYIT")

# AutoCAD tanımsız çizgi tipine başvuran katmanı olan dosyayı açmaz
_lts = {lt.dxf.name.lower() for lt in doc.linetypes}
assert all(l.dxf.linetype.lower() in _lts for l in doc.layers), "tanımsız çizgi tipi"
doc.encoding = "cp1254"  # Türkçe kod sayfası (ANSI_1254)
doc.saveas(DXF_PATH)
print("DXF:", DXF_PATH)
print({k: round(v, 3) for k, v in H.items()}, "boru boyu", round(pipe_len, 1))

if "--png" in sys.argv:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy

    fig = plt.figure(figsize=(30, 19))
    ax = fig.add_axes([0, 0, 1, 1])
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(msp)
    fig.set_size_inches(30, 19)
    fig.savefig(PNG_PATH, dpi=110)
    print("PNG:", PNG_PATH)
