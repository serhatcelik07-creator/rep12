"""ZİVER PETROL A.Ş. - Akaryakıt + LPG istasyonu
LPG tankı ve hatları KATODİK KORUMA PROJESİ (vaziyet, uygulama planı, kesit, perspektif,
izometrik şema, detaylar, hesap, antet) DXF üretici.

Altlık: kaynak/TASLAK3.dxf (kullanıcının düzenlediği yerleşim).  Birim: metre, 1 birim = 1 m.
Pafta ölçeği 1/50: en küçük yazı 2.0 mm (0.100 m), en büyük yazı 2.55 mm (0.1275 m).
Pafta yüksekliği TASLAK3 ile aynı tutuldu (y = -0.71 ... 37.30), pafta sağa doğru genişletildi.

Kullanım: python3 proje_uret.py [--png]
"""
import math
import os
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment as TA

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "kaynak", "TASLAK3.dxf")
OUT = os.path.join(HERE, "ZIVER_PETROL_LPG_KK_PROJE.dxf")
PNG = os.path.join(HERE, "ZIVER_PETROL_LPG_KK_PROJE.png")

H1, H2, H3 = 0.100, 0.110, 0.1275          # 2.0 / 2.2 / 2.55 mm @ 1/50
C30, S30 = math.cos(math.radians(30)), 0.5

# ============================================================================ proje verisi
ISVEREN = "ZİVER PETROL A.Ş."
ADRES = "Yenimahalle Mah. Hekimsuyu Cad. No:19/A  Gaziosmanpaşa / İSTANBUL"
FIRMA = "SMA MÜHENDİSLİK"
BURO_TESCIL = "34341110000786"
MUHENDIS = "ABDULLAH SUPHİ AYDIN"
EMO_SICIL = "34 34 5644"
TARIH = "10.2026"

# Tank (saha plakası poz 25: 10 m³) - hesapta Ø1.60 x 5.40 m (2:1 bombeli) kabul
TANK_V, TANK_D, TANK_L = 10.0, 1.60, 5.40
# Mevcut anotlar (saha plakası): poz 24: 2 x 10 Lb, poz 17: 2 x 3,5 Lb
ANOT = {"10 Lb": dict(kg=4.5, L=0.50, d=0.14, ing=(0.076, 0.356)),
        "3,5 Lb": dict(kg=1.6, L=0.35, d=0.10, ing=(0.051, 0.229))}
SOIL_RHO = 30.0       # Ω·m  kabul (sahada Wenner ile ölçülecek)
I_BARE = 20.0         # mA/m² çıplak çelik
COAT_EFF = 0.95       # ortalama kaplama verimi (fabrika PU/epoksi kaplama)
SAFETY = 1.25
LIFE_Y = 20
MG_CAP, MG_UTIL = 1230.0, 0.85
E_MG, E_KRIT = -1.75, -0.85
PIPE_OD = 0.0422      # 1" - 1 1/2" ortalama

# ============================================================================ doküman
src = ezdxf.readfile(SRC)


def src_pts(h):
    return [(float(p[0]), float(p[1])) for p in src.entitydb[h].get_points("xy")]


def src_circle(h):
    e = src.entitydb[h]
    return float(e.dxf.center.x), float(e.dxf.center.y), float(e.dxf.radius)


doc = ezdxf.new("R2010", setup=True)
doc.units = ezdxf.units.M
doc.header["$INSUNITS"] = 6
doc.header["$MEASUREMENT"] = 1
doc.header["$LTSCALE"] = 0.2
doc.header["$LWDISPLAY"] = 1
doc.header["$TEXTSIZE"] = H1
doc.styles.add("ARIAL", font="arial.ttf")
doc.header["$TEXTSTYLE"] = "ARIAL"

LAY = {
    "PAFTA": (7, "Continuous", 70), "ANTET": (7, "Continuous", 35), "ANTET-INCE": (8, "Continuous", 18),
    "ANTET-LOGO": (1, "Continuous", 50),
    "YOL": (8, "DASHED", 25), "BINA": (7, "Continuous", 50), "BINA-TARAMA": (8, "Continuous", 9),
    "KANOPI": (4, "DASHDOT", 25), "KOLON": (7, "Continuous", 35),
    "ADA": (3, "Continuous", 35), "ADA-TARAMA": (8, "Continuous", 9), "DISPENSER": (2, "Continuous", 35),
    "LPG-SAHA": (1, "Continuous", 35), "CIT": (1, "Continuous", 25), "SAHA-TARAMA": (9, "Continuous", 9),
    "BARIYER": (2, "Continuous", 25), "YANGIN": (1, "Continuous", 25),
    "LPG-TANK": (1, "DASHED2", 35), "EKSEN": (8, "CENTER2", 13), "GIZLI": (8, "DASHED2", 13),
    "LPG-HAT": (6, "Continuous", 50),
    "KK-ANOT": (30, "Continuous", 35), "KK-KABLO": (5, "DASHED2", 25), "KK-OLCUM": (2, "Continuous", 35),
    "KK-IZOLASYON": (140, "Continuous", 35), "KESIT-HATTI": (1, "DASHDOT", 50),
    "OLCU": (8, "Continuous", 13), "YAZI": (7, "Continuous", 18), "BASLIK": (7, "Continuous", 35),
    "BALON": (7, "Continuous", 18),
    "KESIT": (7, "Continuous", 50), "KESIT-INCE": (8, "Continuous", 18), "KESIT-TARAMA": (8, "Continuous", 9),
    "DETAY": (7, "Continuous", 35), "DETAY-INCE": (8, "Continuous", 18), "DETAY-TARAMA": (8, "Continuous", 9),
    "PERSPEKTIF": (7, "Continuous", 35), "PERSPEKTIF-INCE": (8, "Continuous", 13),
    "IZO": (7, "Continuous", 25), "IZO-HAT": (6, "Continuous", 50), "IZO-VANA": (3, "Continuous", 25),
    "TABLO": (7, "Continuous", 25), "TABLO-INCE": (8, "Continuous", 13),
}
for n, (c, lt, lw) in LAY.items():
    doc.layers.add(n, color=c, linetype=lt, lineweight=lw)

for name, lfac, dec in (("KK50", 100, 0), ("KK25", 50, 0), ("KK10", 200, 0), ("KK5", 100, 0)):
    ds = doc.dimstyles.new(name)
    ds.dxf.dimtxt, ds.dxf.dimasz, ds.dxf.dimexe, ds.dxf.dimexo = H1, 0.07, 0.06, 0.05
    ds.dxf.dimgap, ds.dxf.dimtad, ds.dxf.dimdec, ds.dxf.dimlfac = 0.03, 1, dec, lfac
    ds.dxf.dimtxsty, ds.dxf.dimclrd, ds.dxf.dimclre, ds.dxf.dimclrt = "ARIAL", 8, 8, 7
    ds.dxf.dimtix, ds.dxf.dimzin = 0, 8
    ds.set_arrows(blk=ezdxf.ARROWS.architectural_tick)

msp = doc.modelspace()


# ============================================================================ yardımcılar
def pl(pts, layer, closed=False, fmt="xy", **kw):
    att = {"layer": layer}
    att.update(kw)
    return msp.add_lwpolyline(pts, format=fmt, close=closed, dxfattribs=att)


def rect(x0, y0, x1, y1, layer, **kw):
    return pl([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer, True, **kw)


def circ(c, r, layer, **kw):
    att = {"layer": layer}
    att.update(kw)
    return msp.add_circle(c, r, dxfattribs=att)


def T(s, p, h=H1, layer="YAZI", al=TA.MIDDLE_LEFT, rot=0.0, color=None):
    assert H1 - 1e-9 <= h <= H3 + 1e-9
    att = {"layer": layer, "style": "ARIAL"}
    if color is not None:
        att["color"] = color
    t = msp.add_text(s, height=h, rotation=rot, dxfattribs=att)
    t.set_placement(p, align=al)
    return t


def MT(s, p, width, h=H1, layer="YAZI", spacing=1.35):
    m = msp.add_mtext(s, dxfattribs={"layer": layer, "style": "ARIAL", "char_height": h, "width": width})
    m.set_location(p, attachment_point=1)
    m.dxf.line_spacing_factor = spacing
    return m


def hatch(paths, layer, pattern=None, scale=0.04, angle=0.0, color=None, solid=None):
    h = msp.add_hatch(color=color if color is not None else 256, dxfattribs={"layer": layer})
    if solid is not None:
        h.set_solid_fill(color=solid)
    else:
        h.set_pattern_fill(pattern, scale=scale, angle=angle, color=color if color is not None else 256)
    for p in paths:
        if isinstance(p, tuple) and p[0] == "circle":
            ep = h.paths.add_edge_path()
            ep.add_arc(p[1], p[2], 0, 360)
        else:
            h.paths.add_polyline_path(p, is_closed=True)
    return h


def dot(p, layer="BALON", r=0.025):
    hatch([("circle", p, r)], layer, solid=7 if layer in ("BALON", "YAZI") else 256)


def txtw(s, h=H1):
    return len(s) * h * 0.62


def leader(target, elbow, lines, side=1, layer="BALON", tlayer="YAZI", h=H1, mark=True):
    """Kılavuz çizgisi: hedef noktası -> dirsek -> yazı omzu. side=+1 sağ, -1 sol."""
    if isinstance(lines, str):
        lines = [lines]
    w = max(txtw(s, h) for s in lines) + 0.08
    end = (elbow[0] + side * w, elbow[1])
    pl([target, elbow, end], layer)
    if mark:
        dot(target, layer)
    x = elbow[0] + side * 0.04
    al0, al1 = (TA.BOTTOM_LEFT, TA.TOP_LEFT) if side > 0 else (TA.BOTTOM_RIGHT, TA.TOP_RIGHT)
    T(lines[0], (x, elbow[1] + 0.035), h, tlayer, al0)
    for i, s in enumerate(lines[1:]):
        T(s, (x, elbow[1] - 0.035 - i * h * 1.6), h, tlayer, al1)
    return end


def balloon(c, txt, target=None, layer="BALON", r=0.16):
    circ(c, r, layer)
    T(txt, c, H1, "YAZI", TA.MIDDLE_CENTER)
    if target is not None:
        dx, dy = target[0] - c[0], target[1] - c[1]
        d = math.hypot(dx, dy)
        if d > r:
            pl([(c[0] + dx / d * r, c[1] + dy / d * r), target], layer)
            dot(target, layer, 0.02)


def title(s, p, w=None, sub=None):
    """Görünüş başlığı: altı çift çizgili."""
    T(s, p, H3, "BASLIK", TA.BOTTOM_LEFT)
    w = w or txtw(s, H3) + 0.2
    pl([(p[0], p[1] - 0.05), (p[0] + w, p[1] - 0.05)], "BASLIK")
    pl([(p[0], p[1] - 0.09), (p[0] + w, p[1] - 0.09)], "YAZI")
    if sub:
        T(sub, (p[0], p[1] - 0.16), H1, "YAZI", TA.TOP_LEFT)


def dim_al(p1, p2, dist, style="KK50", txt="<>"):
    d = msp.add_aligned_dim(p1=p1, p2=p2, distance=dist, text=txt, dimstyle=style,
                            dxfattribs={"layer": "OLCU"})
    d.render()


def kot(p, label, side=1, layer="KESIT-INCE"):
    x, y = p
    pl([(x, y), (x - 0.06, y + 0.10), (x + 0.06, y + 0.10)], layer, True)
    hatch([[(x, y), (x - 0.06, y + 0.10), (x, y + 0.10)]], layer, solid=256)
    pl([(x - 0.18, y), (x + 0.18 + 0.55 * (side > 0), y)], layer)
    T(label, (x + side * 0.1, y + 0.15), H1, "YAZI", TA.BOTTOM_LEFT if side > 0 else TA.BOTTOM_RIGHT)


def bulge_poly(x0, y0, x1, y1, r):
    """Köşeleri r yarıçaplı yuvarlatılmış dikdörtgen (xyb)."""
    b = math.tan(math.radians(90) / 4)
    return [(x0 + r, y0, 0), (x1 - r, y0, b), (x1, y0 + r, 0), (x1, y1 - r, b), (x1 - r, y1, 0),
            (x0 + r, y1, b), (x0, y1 - r, 0), (x0, y0 + r, b)]


def hull(points):
    pts = sorted(set((round(x, 6), round(y, 6)) for x, y in points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def offset_path(pts, d):
    """Polyline'ı sola d kadar kaydır (miter)."""
    out = []
    n = len(pts)
    for i in range(n):
        if i == 0:
            ax, ay = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
            l = math.hypot(ax, ay)
            nx, ny = -ay / l, ax / l
            out.append((pts[0][0] + nx * d, pts[0][1] + ny * d))
        elif i == n - 1:
            ax, ay = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
            l = math.hypot(ax, ay)
            nx, ny = -ay / l, ax / l
            out.append((pts[-1][0] + nx * d, pts[-1][1] + ny * d))
        else:
            a1 = (pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
            a2 = (pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
            l1, l2 = math.hypot(*a1), math.hypot(*a2)
            n1 = (-a1[1] / l1, a1[0] / l1)
            n2 = (-a2[1] / l2, a2[0] / l2)
            m = (n1[0] + n2[0], n1[1] + n2[1])
            lm = math.hypot(*m)
            m = (m[0] / lm, m[1] / lm)
            k = d / max(0.2, m[0] * n1[0] + m[1] * n1[1])
            out.append((pts[i][0] + m[0] * k, pts[i][1] + m[1] * k))
    return out


def plen(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


# ---------------------------------------------------------------- izometrik izdüşüm
VIEW = (-1.0, -1.0, 1.0)


def iso(p, O, S):
    x, y, z = p
    return (O[0] + (x - y) * C30 * S, O[1] + ((x + y) * S30 + z) * S)


def vis(n):
    return n[0] * VIEW[0] + n[1] * VIEW[1] + n[2] * VIEW[2] > 1e-9


def draw_split(points3, normals, O, S, layer, hidden_layer, closed=True):
    """Halka noktalarını görünür/gizli olarak ayırıp çiz."""
    n = len(points3)
    segs, cur, curv = [], [], None
    rng = range(n + 1) if closed else range(n)
    for k in rng:
        i = k % n
        v = vis(normals[i])
        if curv is None or v == curv:
            cur.append(points3[i])
        else:
            cur.append(points3[i])
            segs.append((curv, cur))
            cur = [points3[i]]
        curv = v
    segs.append((curv, cur))
    for v, s in segs:
        if len(s) > 1:
            pl([iso(p, O, S) for p in s], layer if v else hidden_layer)


def iso_xcyl(O, S, x0, x1, yc, zc, r, layer, thin, hidden, heads=True, shade=True, n=72):
    """x ekseni boyunca silindir (2:1 bombeli kafalı tank veya düz uçlu)."""
    pts = []
    h = r / 2 if heads else 0.0
    steps = 10 if heads else 1
    for k in range(steps + 1):
        t = (math.pi / 2) * k / steps
        rr, dx = r * math.cos(t), h * math.sin(t)
        for xe, sgn in ((x0, -1), (x1, 1)):
            for i in range(n):
                a = 2 * math.pi * i / n
                pts.append((xe + sgn * dx, yc + rr * math.cos(a), zc + rr * math.sin(a)))
    outline = hull([iso(p, O, S) for p in pts])
    pl(outline, layer, True)
    for xe in (x0, x1):
        ring = [(xe, yc + r * math.cos(2 * math.pi * i / n), zc + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
        nor = [(0, math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n)) for i in range(n)]
        if not heads and xe == x0:
            pl([iso(p, O, S) for p in ring], layer, True)   # -x yüzü izleyiciye dönük
        else:
            draw_split(ring, nor, O, S, layer, hidden)
    if shade:
        for deg in (196, 208, 216, 221, 224):
            a = math.radians(deg)
            p0 = (x0, yc + r * math.cos(a), zc + r * math.sin(a))
            p1 = (x1, yc + r * math.cos(a), zc + r * math.sin(a))
            pl([iso(p0, O, S), iso(p1, O, S)], thin)
    return outline


def iso_vcyl(O, S, cx, cy, z0, z1, r, layer, hidden=None, n=48):
    pts, top = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a), z0))
        top.append((cx + r * math.cos(a), cy + r * math.sin(a), z1))
    pl(hull([iso(p, O, S) for p in pts + top]), layer, True)
    pl([iso(p, O, S) for p in top], layer, True)


def iso_box(O, S, x0, y0, z0, dx, dy, dz, layer):
    V = [(x0 + i * dx, y0 + j * dy, z0 + k * dz) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    pl(hull([iso(p, O, S) for p in V]), layer, True)
    c = (x0, y0, z0 + dz)
    for q in ((x0 + dx, y0, z0 + dz), (x0, y0 + dy, z0 + dz), (x0, y0, z0)):
        pl([iso(c, O, S), iso(q, O, S)], layer)


def iso_line(O, S, pts3, layer):
    return pl([iso(p, O, S) for p in pts3], layer)


def iso_dir2(O, S, p, d):
    a, b = iso(p, O, S), iso((p[0] + d[0], p[1] + d[1], p[2] + d[2]), O, S)
    ux, uy = b[0] - a[0], b[1] - a[1]
    l = math.hypot(ux, uy)
    return a, (ux / l, uy / l), (-uy / l, ux / l)


def iso_valve(O, S, p, d, layer="IZO-VANA", a=0.09, b=0.07, kind="vana"):
    c, u, v = iso_dir2(O, S, p, d)
    P = lambda s, t: (c[0] + s * u[0] + t * v[0], c[1] + s * u[1] + t * v[1])
    if kind == "vana":
        pl([P(-a, b), P(a, -b), P(a, b), P(-a, -b)], layer, True)
    elif kind == "cek":
        pl([P(-a, b), P(a, -b), P(a, b), P(-a, -b)], layer, True)
        hatch([[P(-a, b), P(0, 0), P(-a, -b)]], layer, solid=256)
    elif kind == "flans":
        pl([P(-0.03, b), P(-0.03, -b)], layer)
        pl([P(0.03, b), P(0.03, -b)], layer)
    elif kind == "izole":
        pl([P(-0.035, b + 0.02), P(-0.035, -b - 0.02)], "KK-IZOLASYON")
        pl([P(0.035, b + 0.02), P(0.035, -b - 0.02)], "KK-IZOLASYON")
        hatch([[P(-0.035, b), P(0.035, b), P(0.035, -b), P(-0.035, -b)]], "KK-IZOLASYON", solid=256)
    elif kind == "flex":
        pts = [P(-a + 2 * a * i / 8, (b * 0.8) * (1 if i % 2 else -1)) for i in range(9)]
        pl(pts, layer)
    elif kind == "pnomatik":
        pl([P(-a, b), P(a, -b), P(a, b), P(-a, -b)], layer, True)
        pl([P(0, 0), P(0, 2.2 * b)], layer)
        rect(*P(-0.06, 2.2 * b), *P(0.06, 3.4 * b), layer)
    return c


def iso_gauge(O, S, p, layer="IZO-VANA"):
    c = iso(p, O, S)
    pl([c, (c[0], c[1] + 0.18)], layer)
    circ((c[0], c[1] + 0.27), 0.09, layer)
    pl([(c[0], c[1] + 0.27), (c[0] + 0.05, c[1] + 0.32)], layer)


# ============================================================================ 1) VAZİYET + KK UYGULAMA PLANI
for h in ("9A", "9B", "9C", "9D", "9E", "9F"):
    pl(src_pts(h), "YOL")

# Binalar
ust = src_pts("A2")
pl(ust, "BINA", True)
hatch([ust], "BINA-TARAMA", "ANSI31", 0.05)
mk = src_pts("202")
pl(mk, "BINA", True)
pl(src_pts("203"), "BINA")
hatch([mk], "BINA-TARAMA", "ANSI31", 0.05)
pl(src_pts("1FF"), "BINA")
pl(src_pts("A8"), "BINA")
mx0, mx1 = min(p[0] for p in mk), max(p[0] for p in mk)
my0, my1 = min(p[1] for p in mk), max(p[1] for p in mk)
xd = src_pts("203")[0][0]
for s, x in (("MARKET", (mx0 + xd) / 2), ("DEPO", (xd + mx1) / 2)):
    rect(x - txtw(s, H3) / 2 - 0.15, (my0 + my1) / 2 - 0.15, x + txtw(s, H3) / 2 + 0.15, (my0 + my1) / 2 + 0.15,
         "YAZI")
    T(s, (x, (my0 + my1) / 2), H3, "YAZI", TA.MIDDLE_CENTER)

# Akaryakıt tank alanı (mevcut)
ta = src_pts("1EE")
pl(ta, "BINA", True)
pl(offset_path(ta + [ta[0]], -0.15)[:-1], "BINA-TARAMA", True)
for h in ("1EF", "1F0", "1F1", "1F2"):
    cx, cy, r = src_circle(h)
    circ((cx, cy), r, "BINA")
    circ((cx, cy), r - 0.1, "BINA-TARAMA")
    pl([(cx - r + 0.12, cy), (cx + r - 0.12, cy)], "EKSEN")
    pl([(cx, cy - r + 0.12), (cx, cy + r - 0.12)], "EKSEN")
T("AKARYAKIT TANK ALANI (MEVCUT)", ((ta[0][0] + ta[1][0]) / 2, min(p[1] for p in ta) + 0.9), H3, "YAZI",
  TA.MIDDLE_CENTER)

# Araç yıkama
ay = src_pts("B9")
pl(ay, "BINA", True)
pl([(ay[0][0], src_pts("BA")[0][1]), (ay[1][0], src_pts("BA")[0][1])], "BINA")
T("ARAÇ YIKAMA", ((ay[0][0] + ay[1][0]) / 2, (ay[0][1] + ay[2][1]) / 2 - 0.4), H3, "YAZI", TA.MIDDLE_CENTER,
  rot=90)

# Kanopi + kolonlar
kn = src_pts("CC")
pl(kn, "KANOPI", True)
T("KANOPİ İZDÜŞÜMÜ", (kn[3][0] + 0.25, kn[3][1] - 0.3), H2, "YAZI", TA.MIDDLE_LEFT, color=4)

# Pompa adaları
adalar = []
for h, ad, tip in (("BC", "ADA-1", "A"), ("C0", "ADA-2", "A"), ("C4", "ADA-3", "A"), ("C8", "ADA-4", "LPG")):
    p = src_pts(h)
    x0, x1 = min(q[0] for q in p), max(q[0] for q in p)
    y0, y1 = min(q[1] for q in p), max(q[1] for q in p)
    adalar.append((ad, tip, x0, y0, x1, y1))
    r = (y1 - y0) / 2
    bp = [(x0 + r, y0, 0), (x1 - r, y0, 1), (x1 - r, y1, 0), (x0 + r, y1, 1)]
    pl(bp, "ADA", True, fmt="xyb")
    o = 0.10
    ip = [(x0 + r, y0 + o, 0), (x1 - r, y0 + o, 1), (x1 - r, y1 - o, 0), (x0 + r, y1 - o, 1)]
    pl(ip, "ADA", True, fmt="xyb")
    hatch([ip], "ADA-TARAMA", "ANSI37", 0.06)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    disps = [cx] if tip == "LPG" else [cx - 1.6, cx + 1.6]
    for dx in disps:
        rect(dx - 0.55, cy - 0.3, dx + 0.55, cy + 0.3, "DISPENSER")
        rect(dx - 0.45, cy - 0.2, dx + 0.45, cy + 0.2, "DISPENSER")
        T("LPG" if tip == "LPG" else "AKARYAKIT", (dx, cy), H1, "YAZI", TA.MIDDLE_CENTER)
    for bx in (x0 + 0.35, x1 - 0.35):
        for by in (cy - 0.38, cy + 0.38):
            circ((bx, by), 0.09, "BARIYER")
            hatch([("circle", (bx, by), 0.09)], "BARIYER", solid=256)
    lbl = ad + ("  (LPG DİSPENSERİ)" if tip == "LPG" else "  (AKARYAKIT)")
    T(lbl, (cx, y1 + 0.22), H3, "YAZI", TA.BOTTOM_CENTER)
lpg_ada = adalar[3]
LPG_D = ((lpg_ada[2] + lpg_ada[4]) / 2, (lpg_ada[3] + lpg_ada[5]) / 2)

# kanopi kolonları (ada çiftlerinin arasında)
for a, b in ((adalar[0], adalar[2]), (adalar[1], adalar[3])):
    cx = ((a[2] + a[4]) / 2 + (b[2] + b[4]) / 2) / 2
    cy = (a[3] + b[5]) / 2
    rect(cx - 0.25, cy - 0.25, cx + 0.25, cy + 0.25, "KOLON")
    hatch([[(cx - 0.25, cy - 0.25), (cx + 0.25, cy - 0.25), (cx + 0.25, cy + 0.25), (cx - 0.25, cy + 0.25)]],
          "KOLON", "ANSI31", 0.03)
    T("KANOPİ KOLONU", (cx + 0.35, cy), H1, "YAZI", TA.MIDDLE_LEFT, color=8)

# ölçüler: ADA-1
a1 = adalar[0]
dim_al((a1[2], a1[5]), (a1[4], a1[5]), 0.55)
dim_al((a1[2], a1[3]), (a1[2], a1[5]), 0.45)
dim_al((kn[0][0], kn[0][1]), (kn[3][0], kn[3][1]), 0.6)

# ---------------------------------------------------------------- LPG tank sahası
saha = src_pts("CE")
ic = src_pts("CF")
pl(saha, "CIT", True)
pl(ic, "LPG-SAHA", True)
hatch([ic], "SAHA-TARAMA", "GRAVEL", 0.012)
# çit direkleri
for i in range(len(saha)):
    a, b = saha[i], saha[(i + 1) % len(saha)]
    L = math.dist(a, b)
    k = max(1, math.ceil(L / 2.0))
    for j in range(k):
        x, y = a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k
        rect(x - 0.05, y - 0.05, x + 0.05, y + 0.05, "CIT")
        hatch([[(x - 0.05, y - 0.05), (x + 0.05, y - 0.05), (x + 0.05, y + 0.05), (x - 0.05, y + 0.05)]], "CIT",
              solid=256)
SX0, SX1 = min(p[0] for p in saha), max(p[0] for p in saha)
SY0, SY1 = min(p[1] for p in saha), max(p[1] for p in saha)
# kapı (alt kenar, sol)
gx = SX0 + 0.5
pl([(gx, SY0), (gx + 1.0, SY0 - 1.0)], "CIT")
msp.add_arc((gx, SY0), 1.0, 270, 315, dxfattribs={"layer": "CIT"})
leader((gx + 0.5, SY0 - 0.4), (gx - 0.3, SY0 - 1.2), "SAHA GİRİŞ KAPISI (kilitli)", -1)
# çarpma bariyerleri (sol ve alt kenar)
for i in range(1, 4):
    x = SX0 + 0.25 + i * 1.45
    rect(x, SY0 - 0.55, x + 0.9, SY0 - 0.48, "BARIYER")
for i in range(2):
    y = SY0 + 0.5 + i * 1.5
    rect(SX0 - 0.55, y, SX0 - 0.48, y + 0.9, "BARIYER")
# yangın söndürücüler
for (x, y), s in (((SX0 - 0.35, SY1 + 0.35), "YSC 12 kg"), ((SX1 + 0.4, SY1 - 0.5), "YSC 12 kg"),
                  ((SX1 + 0.4, SY0 + 2.3), "YSC 50 kg")):
    circ((x, y), 0.14, "YANGIN")
    hatch([[(x - 0.14, y), (x + 0.14, y), (x, y + 0.14)]], "YANGIN", solid=1)
    T(s, (x + (0.22 if x > SX0 else -0.22), y), H1, "YAZI", TA.MIDDLE_LEFT if x > SX0 else TA.MIDDLE_RIGHT)

# tank (yeraltı)
TX0, TX1 = SX0 + 0.3, SX0 + 0.3 + TANK_L
TYC = (SY0 + SY1) / 2 - 0.15
TR = TANK_D / 2
tb = math.tan(math.radians(180) / 4)
tank_pl = [(TX0 + TR / 2, TYC - TR, 0), (TX1 - TR / 2, TYC - TR, 0.4142), (TX1, TYC, 0.4142),
           (TX1 - TR / 2, TYC + TR, 0), (TX0 + TR / 2, TYC + TR, 0.4142), (TX0, TYC, 0.4142)]
pl(tank_pl, "LPG-TANK", True, fmt="xyb")
pl([(TX0 + TR / 2, TYC - TR), (TX0 + TR / 2, TYC + TR)], "GIZLI")
pl([(TX1 - TR / 2, TYC - TR), (TX1 - TR / 2, TYC + TR)], "GIZLI")
pl([(TX0 - 0.3, TYC), (TX1 + 0.3, TYC)], "EKSEN")
MH = (TX0 + TANK_L * 0.62, TYC)
circ(MH, 0.35, "LPG-SAHA")
circ(MH, 0.28, "LPG-SAHA")
T("LPG TANKI 10 m³ (yeraltı)", (TX0 + 1.55, TYC + 0.12), H3, "YAZI", TA.MIDDLE_CENTER)
T("Ø160 x 540 cm (kabul)", (TX0 + 1.55, TYC - 0.12), H1, "YAZI", TA.MIDDLE_CENTER)
T("MENHOL", (MH[0], MH[1] - 0.48), H1, "YAZI", TA.MIDDLE_CENTER)
# kademeli pompa (saha içi, sol üst)
PX0, PY0 = SX0 + 0.35, SY1 - 0.75
rect(PX0, PY0, PX0 + 1.3, PY0 + 0.45, "LPG-SAHA")
rect(PX0 + 0.9, PY0 + 0.05, PX0 + 1.3, PY0 + 0.40, "LPG-SAHA")
T("KADEMELİ POMPA", (PX0 + 0.05, PY0 + 0.225), H1, "YAZI", TA.MIDDLE_LEFT)
# hatlar: menhol -> pompa (emiş + geri dönüş), pompa -> dispenser (basma + geri dönüş)
yE = PY0 + 0.225
emis = [(MH[0] - 0.08, MH[1] + 0.3), (MH[0] - 0.08, yE + 0.08), (PX0 + 1.3, yE + 0.08)]
donus_s = [(MH[0] + 0.08, MH[1] + 0.3), (MH[0] + 0.08, yE - 0.30), (PX0 - 0.15, yE - 0.30)]
pl(emis, "LPG-HAT")
pl(donus_s, "LPG-HAT")
basma = [(PX0, yE + 0.08), (SX0 - 0.7, yE + 0.08), (LPG_D[0] + 1.25, LPG_D[1] - 1.75),
         (LPG_D[0] + 0.08, LPG_D[1] - 1.75), (LPG_D[0] + 0.08, LPG_D[1] - 0.3)]
donus = [(PX0 - 0.15, yE - 0.30), (SX0 - 0.85, yE - 0.30), (LPG_D[0] + 1.10, LPG_D[1] - 1.95),
         (LPG_D[0] - 0.08, LPG_D[1] - 1.95), (LPG_D[0] - 0.08, LPG_D[1] - 0.3)]
pl(basma, "LPG-HAT")
pl(donus, "LPG-HAT")
mid = ((basma[1][0] + basma[2][0]) / 2, (basma[1][1] + basma[2][1]) / 2)
leader(mid, (mid[0] - 1.6, mid[1] - 1.2),
       ["LPG HATLARI (toprak altı): BASMA + GERİ DÖNÜŞ",
        "SCH80 dikişsiz çelik çekme boru, 2 kat sargılı (min. %50 bindirme)"], -1)
PIPE_LEN = plen(basma) + plen(donus) + plen(emis) + plen(donus_s)

# izole flanşlar (6 ad.)
def izf_plan(p, horiz=True, lab=None, lab_off=(0.0, 0.3)):
    x, y = p
    if horiz:
        pl([(x - 0.05, y - 0.12), (x - 0.05, y + 0.12)], "KK-IZOLASYON")
        pl([(x + 0.05, y - 0.12), (x + 0.05, y + 0.12)], "KK-IZOLASYON")
    else:
        pl([(x - 0.12, y - 0.05), (x + 0.12, y - 0.05)], "KK-IZOLASYON")
        pl([(x - 0.12, y + 0.05), (x + 0.12, y + 0.05)], "KK-IZOLASYON")
    if lab:
        T(lab, (x + lab_off[0], y + lab_off[1]), H1, "YAZI", TA.MIDDLE_CENTER, color=140)


izf_plan((emis[0][0], MH[1] + 0.55), False)
izf_plan((donus_s[0][0], MH[1] + 0.55), False, "İF-1/2", (0.45, 0.0))
izf_plan((SX0 + 0.12, yE + 0.08), True)
izf_plan((SX0 + 0.12, yE - 0.30), True, "İF-3/4", (0.0, -0.22))
izf_plan((basma[-1][0], LPG_D[1] - 0.55), False)
izf_plan((donus[-1][0], LPG_D[1] - 0.55), False, "İF-5/6", (0.55, 0.0))

# anotlar
ANOTLAR = [("MA-1", "10 Lb", (TX0 + 1.0, TYC - TR - 0.8)), ("MA-2", "10 Lb", (TX1 - 0.9, TYC + TR + 0.8)),
           ("MA-3", "3,5 Lb", (LPG_D[0] - 1.2, LPG_D[1] - 1.45)),
           ("MA-4", "3,5 Lb", (LPG_D[0] + 2.0, LPG_D[1] - 1.20))]


def anot_sym(p, name, kind, lab_dir=(0.3, 0.3)):
    circ(p, 0.17, "KK-ANOT")
    circ(p, 0.09, "KK-ANOT")
    hatch([("circle", p, 0.09)], "KK-ANOT", solid=30)
    T(f"{name} ({kind} Mg)", (p[0] + lab_dir[0], p[1] + lab_dir[1]), H1, "YAZI",
      TA.MIDDLE_LEFT if lab_dir[0] >= 0 else TA.MIDDLE_RIGHT, color=30)


anot_sym(ANOTLAR[0][2], "MA-1", "10 Lb", (-0.25, 0.3))
anot_sym(ANOTLAR[1][2], "MA-2", "10 Lb", (0.22, -0.32))
anot_sym(ANOTLAR[2][2], "MA-3", "3,5 Lb", (0.25, -0.28))
anot_sym(ANOTLAR[3][2], "MA-4", "3,5 Lb", (0.25, 0.22))


def ok_sym(p, name, lab_dir=(-0.3, 0.0)):
    x, y = p
    rect(x - 0.2, y - 0.15, x + 0.2, y + 0.15, "KK-OLCUM")
    pl([(x - 0.2, y - 0.15), (x + 0.2, y + 0.15)], "KK-OLCUM")
    hatch([[(x - 0.2, y - 0.15), (x + 0.2, y + 0.15), (x - 0.2, y + 0.15)]], "KK-OLCUM", solid=2)
    T(name, (x + lab_dir[0], y + lab_dir[1]), H3, "YAZI", TA.MIDDLE_RIGHT if lab_dir[0] < 0 else TA.MIDDLE_LEFT,
      color=2)


OK1 = (SX0 - 1.15, SY0 + 0.45)
OK2 = (LPG_D[0] - 2.35, LPG_D[1] - 1.45)
ok_sym(OK1, "ÖK-1")
ok_sym(OK2, "ÖK-2", (-0.3, 0.0))
RE = (TX0 + 2.6, TYC - TR - 0.35)
circ(RE, 0.10, "KK-OLCUM")
pl([(RE[0] - 0.07, RE[1]), (RE[0] + 0.07, RE[1])], "KK-OLCUM")
pl([(RE[0], RE[1] - 0.07), (RE[0], RE[1] + 0.07)], "KK-OLCUM")
T("RE (Cu/CuSO4)", (RE[0] + 0.18, RE[1]), H1, "YAZI", TA.MIDDLE_LEFT, color=2)
# tank kablo bağlantı noktaları (termit)
W1, W2 = (TX0 + 1.7, TYC - TR), (TX0 + 1.9, TYC - TR)
for w in (W1, W2):
    pl([(w[0] - 0.06, w[1] - 0.06), (w[0] + 0.06, w[1] + 0.06)], "KK-OLCUM")
    pl([(w[0] - 0.06, w[1] + 0.06), (w[0] + 0.06, w[1] - 0.06)], "KK-OLCUM")
# kablolar
xin = OK1[0] + 0.2
KAB = []
KAB.append([ANOTLAR[0][2], (ANOTLAR[0][2][0], OK1[1] + 0.08), (xin, OK1[1] + 0.08)])
KAB.append([ANOTLAR[1][2], (ANOTLAR[1][2][0], SY1 - 0.18), (SX0 + 0.2, SY1 - 0.18), (SX0 + 0.2, OK1[1] + 0.12),
            (xin, OK1[1] + 0.12)])
KAB.append([W1, (W1[0], OK1[1] + 0.0), (xin, OK1[1] + 0.0)])
KAB.append([W2, (W2[0], OK1[1] - 0.04), (xin, OK1[1] - 0.04)])
KAB.append([RE, (RE[0], OK1[1] - 0.08), (xin, OK1[1] - 0.08)])
xin2 = OK2[0] + 0.2
KAB.append([ANOTLAR[2][2], (xin2, ANOTLAR[2][2][1])])
KAB.append([ANOTLAR[3][2], (ANOTLAR[3][2][0], OK2[1] + 0.35), (xin2 - 0.1, OK2[1] + 0.35),
            (xin2 - 0.1, OK2[1] + 0.15)])
KAB.append([(donus[-2][0] + 0.3, donus[-2][1]), (donus[-2][0] + 0.3, OK2[1] - 0.6), (OK2[0], OK2[1] - 0.6),
            (OK2[0], OK2[1] - 0.15)])
for k in KAB:
    pl(k, "KK-KABLO")
CABLE_LEN = sum(plen(k) for k in KAB) + len(KAB) * 2.0
leader(((KAB[1][1][0] + KAB[1][2][0]) / 2, KAB[1][2][1]), (SX0 + 1.9, SY1 + 2.0),
       ["KK kabloları: NYY 1x6 mm² (anot), NYY 1x10 mm² (tank/hat)",
        "toprak altı -60 cm, üzerinde kablo ikaz bandı"], 1)

# kesit hattı A-A
KX = TX0 + 3.3
pl([(KX, SY0 - 1.2), (KX, SY1 + 0.75)], "KESIT-HATTI")
for y, s in ((SY0 - 1.2, -1), (SY1 + 0.75, 1)):
    pl([(KX, y), (KX - 0.45, y)], "KESIT")
    hatch([[(KX - 0.45, y), (KX - 0.3, y + 0.06), (KX - 0.3, y - 0.06)]], "KESIT", solid=256)
    circ((KX + 0.25, y + s * 0.05), 0.16, "KESIT")
    T("A", (KX + 0.25, y + s * 0.05), H3, "YAZI", TA.MIDDLE_CENTER)

# saha ölçüleri
dim_al((SX0, SY1), (SX1, SY1), 0.95)
dim_al((SX1, SY0), (SX1, SY1), -0.95)
dim_al((LPG_D[0] + 0.55, LPG_D[1]), (SX0, SY1), 0.5)
leader((SX1 - 0.25, SY0 + 3.2), (SX1 + 1.0, SY0 + 3.7), ["LPG TANK SAHASI", "tel çitli, çakıl kaplama"], 1)

# kuzey oku
NX, NY = -10.6, 34.2
circ((NX, NY), 0.55, "BASLIK")
pl([(NX, NY + 0.75), (NX - 0.25, NY - 0.45), (NX, NY - 0.2), (NX + 0.25, NY - 0.45)], "BASLIK", True)
hatch([[(NX, NY + 0.75), (NX, NY - 0.2), (NX + 0.25, NY - 0.45)]], "BASLIK", solid=256)
T("K", (NX, NY + 0.95), H3, "YAZI", TA.BOTTOM_CENTER)

title("VAZİYET PLANI ve KATODİK KORUMA UYGULAMA PLANI", (-9.6, 36.55),
      sub="Ölçek 1/50  -  Yerleşim mevcut duruma göredir, ölçüler sahada teyit edilecektir.")

# ---------------------------------------------------------------- lejant (sol boşluk)
LX, LY = -11.6, 32.6
title("LEJANT", (LX, LY + 0.45))
lej = []


def lej_row(i, draw, text):
    y = LY - 0.15 - i * 0.42
    draw(LX + 0.45, y)
    T(text, (LX + 1.2, y), H1, "YAZI", TA.MIDDLE_LEFT)


lej_row(0, lambda x, y: anot_sym((x, y), "", "") if False else (circ((x, y), 0.17, "KK-ANOT"),
        circ((x, y), 0.09, "KK-ANOT"), hatch([("circle", (x, y), 0.09)], "KK-ANOT", solid=30)),
        "Magnezyum anot (hazır dolgulu, yüksek potansiyelli)")
lej_row(1, lambda x, y: (rect(x - 0.2, y - 0.15, x + 0.2, y + 0.15, "KK-OLCUM"),
                         hatch([[(x - 0.2, y - 0.15), (x + 0.2, y + 0.15), (x - 0.2, y + 0.15)]], "KK-OLCUM",
                               solid=2)), "Ölçüm (test) kutusu - ÖK")
lej_row(2, lambda x, y: (circ((x, y), 0.10, "KK-OLCUM"), pl([(x - 0.07, y), (x + 0.07, y)], "KK-OLCUM"),
                         pl([(x, y - 0.07), (x, y + 0.07)], "KK-OLCUM")), "Kalıcı Cu/CuSO4 referans elektrot - RE")
lej_row(3, lambda x, y: (pl([(x - 0.05, y - 0.12), (x - 0.05, y + 0.12)], "KK-IZOLASYON"),
                         pl([(x + 0.05, y - 0.12), (x + 0.05, y + 0.12)], "KK-IZOLASYON"),
                         pl([(x - 0.4, y), (x - 0.05, y)], "LPG-HAT"), pl([(x + 0.05, y), (x + 0.4, y)], "LPG-HAT")),
        "İzole flanş kiti - İF")
lej_row(4, lambda x, y: pl([(x - 0.4, y), (x + 0.4, y)], "KK-KABLO"), "Katodik koruma kablosu (toprak altı)")
lej_row(5, lambda x, y: pl([(x - 0.4, y), (x + 0.4, y)], "LPG-HAT"), "LPG hattı (SCH80 dikişsiz çelik)")
lej_row(6, lambda x, y: pl([(x - 0.4, y), (x + 0.4, y)], "LPG-TANK"), "LPG tankı (yeraltı, görünmeyen)")
lej_row(7, lambda x, y: (pl([(x - 0.06, y - 0.06), (x + 0.06, y + 0.06)], "KK-OLCUM"),
                         pl([(x - 0.06, y + 0.06), (x + 0.06, y - 0.06)], "KK-OLCUM")),
        "Tank kablo bağlantısı (termit kaynak / pin brazing)")
lej_row(8, lambda x, y: (pl([(x - 0.4, y), (x + 0.4, y)], "CIT"), rect(x - 0.05, y - 0.05, x + 0.05, y + 0.05, "CIT")),
        "Tel çit ve direk")
lej_row(9, lambda x, y: rect(x - 0.4, y - 0.035, x + 0.4, y + 0.035, "BARIYER"), "Çarpma bariyeri (U boru)")
lej_row(10, lambda x, y: (circ((x, y), 0.14, "YANGIN"),
                          hatch([[(x - 0.14, y), (x + 0.14, y), (x, y + 0.14)]], "YANGIN", solid=1)),
        "Yangın söndürme cihazı (YSC)")
lej_row(11, lambda x, y: pl([(x - 0.4, y), (x + 0.4, y)], "KANOPI"), "Kanopi izdüşümü")
lej_row(12, lambda x, y: (pl([(x - 0.4, y), (x + 0.4, y)], "KESIT-HATTI")), "Kesit hattı")

# ---------------------------------------------------------------- KK malzeme listesi (sol)
def table(x0, ytop, cols, rows, rh=0.30, header_h=0.36, hl=None, tlayer="TABLO"):
    W = sum(c[1] for c in cols)
    y = ytop
    rect(x0, y - header_h, x0 + W, y, tlayer)
    hatch([[(x0, y - header_h), (x0 + W, y - header_h), (x0 + W, y), (x0, y)]], "TABLO-INCE", "ANSI31", 0.02)
    x = x0
    for name, w, al in cols:
        T(name, (x + w / 2, y - header_h / 2), H1, "YAZI", TA.MIDDLE_CENTER)
        x += w
    y -= header_h
    for ri, r in enumerate(rows):
        pl([(x0, y - rh), (x0 + W, y - rh)], "TABLO-INCE")
        x = x0
        for (name, w, al), v in zip(cols, r):
            if al == "C":
                T(str(v), (x + w / 2, y - rh / 2), H1, "YAZI", TA.MIDDLE_CENTER,
                  color=30 if hl and ri in hl else None)
            else:
                T(str(v), (x + 0.08, y - rh / 2), H1, "YAZI", TA.MIDDLE_LEFT, color=30 if hl and ri in hl else None)
            x += w
        y -= rh
    rect(x0, y, x0 + W, ytop, tlayer)
    x = x0
    for name, w, al in cols[:-1]:
        x += w
        pl([(x, y), (x, ytop)], "TABLO-INCE")
    return y


KY = LY - 13 * 0.42 - 0.6
title("KATODİK KORUMA MALZEME LİSTESİ (MEVCUT SİSTEM)", (LX, KY))
kk_rows = [
    ("K1", "Mg anot, yüksek potansiyelli, hazır dolgulu 10 Lb (4,5 kg) - tank", "2 ad.", "MA-1, MA-2 (plaka poz 24)"),
    ("K2", "Mg anot, yüksek potansiyelli, hazır dolgulu 3,5 Lb (1,6 kg) - hat/dispenser", "2 ad.",
     "MA-3, MA-4 (plaka poz 17)"),
    ("K3", "Ölçüm kutusu, IP65, terminal + 0,01 Ω şönt + sökülebilir köprü", "2 ad.", "ÖK-1, ÖK-2"),
    ("K4", "Kalıcı Cu/CuSO4 referans elektrot (ömür ≥ 20 yıl)", "1 ad.", "RE (tank yanı)"),
    ("K5", "İzole flanş kiti PN40 (conta + manşon + pul)", "6 ad.", "İF-1...İF-6 (plaka poz 13)"),
    ("K6", "NYY 1x6 mm² anot kablosu / NYY 1x10 mm² yapı kablosu", f"~{math.ceil(CABLE_LEN / 5) * 5} m",
     "Toprak altı -60 cm"),
    ("K7", "Termit kaynak / pin brazing bağlantı + kaplama tamir seti", "3 ad.", "Tank (2), hat (1)"),
    ("K8", "Kablo ikaz bandı (sarı, 'DİKKAT KATODİK KORUMA KABLOSU')", f"~{math.ceil(CABLE_LEN / 2 / 5) * 5} m",
     "-30 cm"),
]
ky_end = table(LX, KY - 0.25, [("POZ", 0.55, "C"), ("MALZEME", 7.6, "L"), ("MİKTAR", 1.1, "C"),
                                ("YERİ / AÇIKLAMA", 4.3, "L")], kk_rows)

# ---------------------------------------------------------------- genel notlar (sol)
NY0 = ky_end - 0.65
title("GENEL NOTLAR", (LX, NY0))
notlar = (
    "1. Mevcut LPG tesisatı (tank, hatlar, dispenser ve katodik koruma) yetkili firma (İPRAGAZ) tarafından tesis "
    "edilmiştir. Bu proje mevcut katodik koruma sisteminin belgelenmesi amacıyla hazırlanmıştır.\\P"
    "2. Sistem galvanik (kurban) anotlu katodik korumadır; harici akım kaynağı yoktur.\\P"
    "3. Uygulanan standartlar: TS EN 12954, TS EN 13636 (yeraltı metal tank ve boruların KK), TS EN 13509 "
    "(ölçüm teknikleri), TS EN 12068 (dış kaplamalar), LPG Piyasası Teknik Düzenleme Yönetmeliği.\\P"
    "4. Koruma kriteri: IR'siz (kesik akım) potansiyel Eoff ≤ -850 mV (Cu/CuSO4). Kaplama hasarını önlemek "
    "için Eoff ≥ -1200 mV olmalıdır.\\P"
    "5. Tank, hat ve dispenser bağlantıları izole flanş kitleri (İF-1...İF-6) ile tesisatın diğer kısımlarından "
    "elektriksel olarak ayrılmıştır. İzolasyon direnci devreye almada ölçülecektir.\\P"
    "6. Topraklama ile KK sistemi arasında doğrudan bağlantı yapılmayacak; gerekirse DC dekuplör kullanılacaktır.\\P"
    "7. Ölçümler yılda en az bir kez yapılıp kayıt altına alınacaktır: tank/zemin potansiyeli (ON/OFF), anot "
    "akımları (şönt üzerinden), izole flanş kontrolü.\\P"
    "8. Ölçüler mevcut duruma göre yaklaşık olup tank boyutları tank etiketinden teyit edilecektir. Zemin "
    "özdirenci (Wenner) sahada ölçülecektir."
)
MT(notlar, (LX, NY0 - 0.25), 13.6, H1)

# ============================================================================ 2) İZOMETRİK TESİSAT ŞEMASI
IS = 1.45
O = (48.4, 18.9)
title("İZOMETRİK TESİSAT ŞEMASI", (40.4, 36.55),
      sub="Saha plakasındaki 'Tek Tank / Tek Dispenser Tesisat Şeması'ndan uyarlanmıştır (ölçeksiz).")
GZ = 1.4   # zemin kotu (şema koordinatı)
# tank
iso_xcyl(O, IS, 0.4, 4.6, 0.0, 0.0, 0.8, "IZO", "PERSPEKTIF-INCE", "GIZLI")
iso_vcyl(O, IS, 2.5, 0.0, 0.8, 1.5, 0.45, "IZO")
# hat noktaları
EM = [(2.3, 0.15, 1.5), (2.3, 0.15, 1.85), (2.3, 2.5, 1.85), (2.55, 2.5, 1.85)]
PUMP = (2.55, 3.6)
BAS = [(4.3, 2.5, 1.85), (4.8, 2.5, 1.85), (4.8, 4.2, 1.85), (4.8, 4.2, 0.9), (4.8, 8.6, 0.9), (4.8, 8.6, 1.45)]
BYP = [(4.8, 2.5, 1.85), (4.8, 0.55, 1.85), (2.75, 0.55, 1.85), (2.75, 0.25, 1.5)]
DON = [(5.25, 8.6, 1.45), (5.25, 8.6, 0.75), (5.25, 3.9, 0.75), (5.25, 3.9, 2.15), (5.25, -0.25, 2.15),
       (2.55, -0.25, 2.15), (2.55, -0.25, 1.5)]
VENT = [(2.15, -0.15, 1.5), (2.15, -0.15, 3.7)]
for path in (EM, BAS, BYP, DON):
    iso_line(O, IS, path, "IZO-HAT")
iso_line(O, IS, VENT, "IZO")
# zemin geçiş işaretleri
for p in ((4.8, 4.2, GZ), (5.25, 3.9, GZ), (4.8, 8.6, GZ), (5.25, 8.6, GZ)):
    c = iso(p, O, IS)
    pl([(c[0] - 0.18, c[1]), (c[0] + 0.18, c[1])], "IZO")
    for k in range(3):
        pl([(c[0] - 0.15 + k * 0.12, c[1]), (c[0] - 0.21 + k * 0.12, c[1] - 0.07)], "IZO")
# pompa + motor + kaide
iso_box(O, IS, 2.4, 2.1, 1.3, 2.1, 0.8, 0.2, "PERSPEKTIF-INCE")
iso_xcyl(O, IS, PUMP[0], PUMP[1], 2.5, 1.85, 0.16, "IZO", "PERSPEKTIF-INCE", "GIZLI", heads=False, shade=False, n=36)
iso_box(O, IS, 3.6, 2.28, 1.62, 0.7, 0.44, 0.46, "IZO")
# dispenser
iso_box(O, IS, 4.45, 8.5, GZ, 1.15, 0.75, 0.12, "PERSPEKTIF-INCE")
iso_box(O, IS, 4.55, 8.6, GZ + 0.12, 0.95, 0.55, 1.75, "IZO")
hp = [iso((4.55, 8.85, 2.7), O, IS), iso((4.2, 8.85, 2.2), O, IS), iso((4.05, 8.85, 2.6), O, IS)]
pl(hp, "IZO")
T("LPG DİSPENSERİ", iso((5.0, 8.9, GZ + 2.2), O, IS), H3, "YAZI", TA.BOTTOM_CENTER)
T("KADEMELİ POMPA", iso((3.2, 2.3, 2.45), O, IS), H1, "YAZI", TA.BOTTOM_CENTER)
T("LPG STOK TANKI 10 m³", iso((3.6, -0.9, -1.1), O, IS), H3, "YAZI", TA.TOP_CENTER)
# armatürler (poz no'ları plakadaki listeye göre)
V = {}
V[1] = iso_valve(O, IS, (2.3, 0.15, 1.68), (0, 0, 1), kind="pnomatik")
iso_valve(O, IS, (2.55, -0.25, 1.75), (0, 0, 1), kind="pnomatik")
V[6] = iso_valve(O, IS, (2.3, 1.6, 1.85), (0, 1, 0), kind="flex")
V[12] = iso_valve(O, IS, (4.55, 2.5, 1.85), (1, 0, 0), kind="flex")
V[9] = iso_valve(O, IS, (4.8, 3.0, 1.85), (0, 1, 0), kind="cek")
V[14] = iso_valve(O, IS, (4.8, 3.6, 1.85), (0, 1, 0))
V[11] = iso_valve(O, IS, (4.8, 4.2, 1.6), (0, 0, 1), kind="pnomatik")
V[8] = iso_valve(O, IS, (3.8, 0.55, 1.85), (1, 0, 0))
V[13] = iso_valve(O, IS, (4.8, 4.2, 1.15), (0, 0, 1), kind="izole")
iso_valve(O, IS, (5.25, 3.9, 1.15), (0, 0, 1), kind="izole")
iso_valve(O, IS, (2.3, 0.15, 1.58), (0, 0, 1), kind="izole")
iso_valve(O, IS, (2.55, -0.25, 1.62), (0, 0, 1), kind="izole")
V[18] = iso_valve(O, IS, (4.8, 8.6, 1.2), (0, 0, 1))
iso_valve(O, IS, (5.25, 8.6, 1.2), (0, 0, 1))
iso_valve(O, IS, (4.8, 8.6, 1.05), (0, 0, 1), kind="izole")
iso_valve(O, IS, (5.25, 8.6, 1.05), (0, 0, 1), kind="izole")
V[22] = iso_valve(O, IS, (4.8, 8.6, 1.35), (0, 0, 1), kind="flex")
V[5] = iso_valve(O, IS, (4.8, 6.4, 0.9), (0, 1, 0))
iso_gauge(O, IS, (4.8, 3.9, 1.85))
V[15] = iso((4.8, 3.9, 1.85), O, IS)
iso_gauge(O, IS, (2.75, 0.05, 1.5))
V[2] = iso((2.75, 0.05, 1.5), O, IS)
V[10] = iso_valve(O, IS, (2.15, -0.15, 2.0), (0, 0, 1))
V[3] = iso_valve(O, IS, (2.0, 0.3, 1.5), (1, 0, 0))
pl([iso((1.6, 0.3, 1.5), O, IS), iso((2.0, 0.3, 1.5), O, IS)], "IZO-HAT")
V[4] = iso((1.6, 0.3, 1.5), O, IS)
V[23] = iso((2.15, -0.15, 3.4), O, IS)
V[7] = iso((3.0, 2.5, 1.85), O, IS)
V[16] = hp[1]
V[20] = iso((3.6, 0.55, 1.85), O, IS)
V[21] = iso((5.25, 6.0, 0.75), O, IS)
V[19] = iso((4.8, 2.5, 1.85), O, IS)
V[25] = iso((0.9, -0.55, -0.3), O, IS)
# anotlar + ölçüm kutuları
OKA, OKB = (-1.8, 0.4), (6.6, 7.6)
ANZ = [(1.2, -1.75, -0.3, 0.3, 24), (3.8, 1.75, -0.3, 0.3, 24), (4.0, 9.4, 0.25, 0.6, 17), (6.0, 9.1, 0.25, 0.6, 17)]
for x, y, z0, z1, poz in ANZ:
    iso_vcyl(O, IS, x, y, z0, z1, 0.09 if poz == 24 else 0.07, "KK-ANOT")
    V.setdefault(poz, iso((x, y, (z0 + z1) / 2), O, IS))
for ox, oy in (OKA, OKB):
    iso_box(O, IS, ox, oy, GZ, 0.12, 0.12, 0.9, "KK-OLCUM")
    iso_box(O, IS, ox - 0.1, oy - 0.1, GZ + 0.75, 0.32, 0.32, 0.35, "KK-OLCUM")
for x, y, z0, z1, poz in ANZ[:2]:
    iso_line(O, IS, [(x, y, z1), (x, y, 0.95), (OKA[0] + 0.06, y, 0.95), (OKA[0] + 0.06, OKA[1] + 0.06, 0.95),
                     (OKA[0] + 0.06, OKA[1] + 0.06, GZ)], "KK-KABLO")
iso_line(O, IS, [(0.9, -0.3, 0.75), (0.9, -0.3, 1.0), (OKA[0] + 0.06, -0.3, 1.0), (OKA[0] + 0.06, OKA[1] + 0.06, 1.0)],
         "KK-KABLO")
for x, y, z0, z1, poz in ANZ[2:]:
    iso_line(O, IS, [(x, y, z1), (x, y, 1.0), (OKB[0] + 0.06, y, 1.0), (OKB[0] + 0.06, OKB[1] + 0.06, 1.0),
                     (OKB[0] + 0.06, OKB[1] + 0.06, GZ)], "KK-KABLO")
T("ÖK-1", iso((OKA[0], OKA[1], GZ + 1.25), O, IS), H2, "YAZI", TA.BOTTOM_CENTER, color=2)
T("ÖK-2", iso((OKB[0], OKB[1], GZ + 1.25), O, IS), H2, "YAZI", TA.BOTTOM_CENTER, color=2)
T("BASMA HATTI (toprak altı)", iso((4.8, 6.6, 0.95), O, IS), H1, "YAZI", TA.BOTTOM_LEFT, rot=-30, color=6)
T("GERİ DÖNÜŞ HATTI (toprak altı)", iso((5.25, 4.6, 0.7), O, IS), H1, "YAZI", TA.TOP_LEFT, rot=-30, color=6)
T("BY-PASS HATTI", iso((4.7, 1.5, 1.9), O, IS), H1, "YAZI", TA.BOTTOM_RIGHT, rot=30, color=6)
T("EMİŞ HATTI", iso((2.35, 1.1, 1.9), O, IS), H1, "YAZI", TA.BOTTOM_LEFT, rot=-30, color=6)


def balloon_columns(items, xcol, side):
    """Balonları dikey sütunda, hedeflerin yükseklik sırasına göre diz."""
    items = sorted(items, key=lambda kv: -kv[1][1])
    n = len(items)
    ymid = sum(p[1] for _, p in items) / n
    gap = 0.62
    ys = [ymid + (n - 1) / 2 * gap - i * gap for i in range(n)]
    for (k, p), y in zip(items, ys):
        c = (xcol, y)
        circ(c, 0.17, "BALON")
        T(str(k), c, H1, "YAZI", TA.MIDDLE_CENTER)
        ex = xcol - side * 0.17
        pl([(ex, y), (ex - side * 0.35, y), p], "BALON")
        dot(p, "BALON", 0.02)


left = [(k, p) for k, p in V.items() if p[0] < 47.6]
right = [(k, p) for k, p in V.items() if p[0] >= 47.6]
balloon_columns(left, 41.2, -1)
balloon_columns(right, 56.2, 1)
T("Numaralar tesisat malzeme listesindeki poz numaralarıdır. Tüm toprak altı hatlar SCH80 dikişsiz çelik, "
  "2 kat sargılıdır.", (40.4, 16.25), H1, "YAZI", TA.BOTTOM_LEFT, color=8)

# ---------------------------------------------------------------- tesisat malzeme listesi (plaka)
PLAKA = [
    (1, 4, "DN25", "OMAL", "PN40", "Tam geçişli, pnömatik aktüatörlü vana"),
    (2, 1, "-", "PAKKENS", "PN40", "Tank manometresi Q63, 0-25 bar gliserinli"),
    (3, 1, "-", "REGO", "300#", "Dolum valfi (REGO 7579C / OMEGA VRN 20)"),
    (4, 1, "-", "ÖZEL", "-", "Dolum hattı by-pass adaptörü"),
    (5, "-", "DN15 (1/2\")", "MHA", "PN500", "Termal tahliye valfi"),
    (6, 1, "-", "AYVAZ", "PN40", "Metal örgülü esnek bağlantı (30 cm)"),
    (7, 1, "-", "-", "-", "Harici kademeli pompa"),
    (8, 1, "-", "CORKEN", "300#", "CORKEN B166 by-pass valfi"),
    (9, 1, "-", "-", "PN40", "Çek valf"),
    (10, 5, "-", "REGO", "300#", "Emniyet valfi - REGO 3129"),
    (11, 2, "DN32", "OMAL", "PN40", "Tam geçişli, pnömatik aktüatörlü vana"),
    (12, 2, "DN32", "AYVAZ", "PN40", "Metal örgülü esnek bağlantı (30 cm)"),
    (13, 6, "-", "YUY-SAN", "PN40", "İzole flanş kiti"),
    (14, 2, "DN32", "-", "PN40", "Tam geçişli küresel gaz-fazı vanası (TSE 9809)"),
    (15, 2, "1/2\"", "PAKKENS", "PN40", "Q100 0-25 bar gliserinli manometre"),
    (16, 2, "3/4\"", "-", "PN40", "R1 esnek bağlantı hortumu"),
    (17, 2, "-", "TSE belgeli", "-", "3,5 Lb magnezyum anot"),
    (18, 2, "DN25", "-", "PN40", "Tam geçişli küresel gaz-fazı vanası (TSE 9809)"),
    (19, 1, "-", "-", "SCH80", "Redüksiyon"),
    (20, "-", "1\"", "-", "SCH80", "Dikişsiz çelik çekme boru"),
    (21, "-", "1 1/2\"", "-", "SCH80", "Dikişsiz çelik çekme boru"),
    (22, 1, "DN25", "AYVAZ", "PN40", "Metal örgülü esnek bağlantı (30 cm)"),
    (23, 1, "2\"", "-", "-", "Emniyet ventili bacası (min. 1 m)"),
    (24, 2, "-", "TSE belgeli", "-", "10 Lb magnezyum anot"),
    (25, 1, "10 m³", "-", "-", "LPG stok tankı (yeraltı)"),
]
title("TESİSAT MALZEME LİSTESİ (saha plakasından)", (40.4, 15.15))
table(40.4, 14.85, [("POZ", 0.55, "C"), ("ADET", 0.6, "C"), ("EBAT", 1.15, "C"), ("MARKA", 1.35, "C"),
                    ("SINIFI", 0.85, "C"), ("AÇIKLAMA", 4.9, "L")],
      [tuple(str(v) for v in r) for r in PLAKA], rh=0.33, hl={12, 16, 23})
T("Turuncu satırlar katodik koruma ile ilgili kalemlerdir. Okunamayan ebatlar '-' ile gösterilmiştir.",
  (40.4, 0.05), H1, "YAZI", TA.BOTTOM_LEFT, color=8)

# ============================================================================ 3) PERSPEKTİF GÖRÜNÜŞ
PO, PS = (65.0, 31.2), 1.3
title("PERSPEKTİF GÖRÜNÜŞ - LPG TANKI ve KATODİK KORUMA", (58.6, 36.55),
      sub="İzometrik, temsilidir. Tank zemin altındadır; görünürlük için toprak gösterilmemiştir.")
TZ = -1.6
lp = lambda p3: iso(p3, PO, PS)
# beton ankraj plağı
iso_box(PO, PS, -0.1, -1.1, -2.95, 5.6, 2.2, 0.25, "PERSPEKTIF-INCE")
# tank + kayışlar
iso_xcyl(PO, PS, 0.4, 5.0, 0.0, TZ, 0.8, "PERSPEKTIF", "PERSPEKTIF-INCE", "GIZLI")
for xs in (1.3, 4.1):
    ring = [(xs, 0.83 * math.cos(math.radians(a)), TZ + 0.83 * math.sin(math.radians(a))) for a in range(-15, 46, 5)]
    pl([lp(p) for p in [(xs, 1.0, -2.7)] + ring], "PERSPEKTIF-INCE")
    ring2 = [(xs, 0.83 * math.cos(math.radians(a)), TZ + 0.83 * math.sin(math.radians(a))) for a in range(45, 196, 5)]
    pl([lp(p) for p in ring2 + [(xs, -1.0, -2.7)]], "PERSPEKTIF-INCE")
# menhol + zemin plakası
MXp = 3.35
iso_vcyl(PO, PS, MXp, 0.0, TZ + 0.8, 0.0, 0.35, "PERSPEKTIF")
iso_box(PO, PS, MXp - 0.75, -0.75, -0.1, 1.5, 1.5, 0.1, "PERSPEKTIF-INCE")
iso_vcyl(PO, PS, MXp, 0.0, 0.0, 0.12, 0.45, "PERSPEKTIF")
T("ZEMİN ±0.00", lp((MXp - 0.75, -0.75, -0.1)), H1, "YAZI", TA.TOP_RIGHT, color=8)
for dy in (-0.12, 0.12):
    iso_line(PO, PS, [(MXp - 0.15, dy, 0.12), (MXp - 0.15, dy, 0.4), (MXp - 1.7, dy, 0.4)], "IZO-HAT")
    iso_valve(PO, PS, (MXp - 0.15, dy, 0.28), (0, 0, 1), kind="izole")
# anotlar + kablolar -> ÖK-1 (sol ön)
OKp = (-0.9, -1.9)
PAN = [("MA-1", 1.0, -1.6), ("MA-2", 4.3, 1.6)]
for nm, x, y in PAN:
    iso_vcyl(PO, PS, x, y, TZ - 0.25, TZ + 0.25, 0.08, "KK-ANOT")
iso_line(PO, PS, [(1.0, -1.6, TZ + 0.25), (1.0, -1.6, -0.6), (OKp[0] + 0.06, -1.6, -0.6),
                  (OKp[0] + 0.06, OKp[1] + 0.06, -0.6), (OKp[0] + 0.06, OKp[1] + 0.06, 0)], "KK-KABLO")
iso_line(PO, PS, [(4.3, 1.6, TZ + 0.25), (4.3, 1.6, -0.6), (-0.4, 1.6, -0.6), (-0.4, -1.75, -0.6),
                  (OKp[0] + 0.06, -1.75, -0.6)], "KK-KABLO")
iso_vcyl(PO, PS, 2.6, -1.15, TZ - 0.1, TZ + 0.1, 0.04, "KK-OLCUM")
iso_line(PO, PS, [(2.6, -1.15, TZ + 0.1), (2.6, -1.15, -0.7), (OKp[0] + 0.06, -1.15, -0.7),
                  (OKp[0] + 0.06, OKp[1] + 0.06, -0.7)], "KK-KABLO")
WP = (1.9, -0.55, TZ + 0.58)
iso_line(PO, PS, [WP, (1.9, -0.55, -0.65), (OKp[0] + 0.06, -0.55, -0.65), (OKp[0] + 0.06, OKp[1] + 0.06, -0.65)],
         "KK-KABLO")
iso_box(PO, PS, OKp[0], OKp[1], 0.0, 0.12, 0.12, 0.95, "KK-OLCUM")
iso_box(PO, PS, OKp[0] - 0.1, OKp[1] - 0.1, 0.8, 0.32, 0.32, 0.38, "KK-OLCUM")
iso_box(PO, PS, OKp[0] - 0.3, OKp[1] - 0.3, -0.1, 0.72, 0.72, 0.1, "PERSPEKTIF-INCE")


def pl_lead(p3, dx, dy, txt, side):
    a = lp(p3)
    leader(a, (a[0] + dx, a[1] + dy), txt, side)


pl_lead((2.2, 0.0, TZ + 0.8), -1.2, 1.4, ["LPG STOK TANKI 10 m³", "fabrika kaplamalı (PU/epoksi)"], -1)
pl_lead((1.0, -1.6, TZ), -1.6, -0.9, ["MA-1  Mg anot 10 Lb", "tank ekseni kotunda, ~0,8 m mesafede"], -1)
pl_lead((4.3, 1.6, TZ), -1.2, 2.6, ["MA-2  Mg anot 10 Lb", "çapraz yerleşim (homojen akım)"], -1)
pl_lead((OKp[0], OKp[1], 1.0), -0.9, 0.9, ["ÖK-1 ölçüm kutusu", "(şönt + köprü + RE terminali)"], -1)
pl_lead(WP, 1.6, -2.2, ["Tank kablo bağlantısı (2 ad.)", "termit kaynak + kaplama tamiri"], 1)
pl_lead((2.6, -1.15, TZ), 2.0, -1.4, ["RE kalıcı Cu/CuSO4 referans elektrot"], 1)
pl_lead((MXp, 0.0, 0.12), 1.2, 1.0, ["Menhol / armatür grubu", "İF-1/2 izole flanşlar"], 1)
pl_lead((4.1, 0.55, TZ + 0.62), 2.2, 0.0, ["Ankraj kayışı", "(tank ile arası izolasyon pedli)"], 1)
pl_lead((5.3, 1.0, -2.83), 1.3, -0.5, ["Beton ankraj plağı", "üzerinde 30 cm elenmiş kum yatak"], 1)

# ============================================================================ 4) KESİT A-A (1/25)
KS = 2.0
KC = (67.2, 21.9)          # zemin kotu ±0.00 ve tank ekseni x


def K(x, z):
    return (KC[0] + KS * x, KC[1] + KS * z)


title("KESİT A-A  (Ölçek 1/25)", (58.6, 24.95), sub="Tank sahası enine kesiti - anotlar kesit düzlemine izdüşürülmüştür.")
XL, XR, ZB = -3.0, 3.0, -3.3


def xe(z):
    return 1.1 + (z + 2.95) * (0.8 / 2.85)


exc = [(-1.1, -2.95), (1.1, -2.95), (1.9, -0.1), (-1.9, -0.1)]
pl([K(*p) for p in exc], "KESIT-INCE", True)
# zemin + çakıl
pl([K(XL, 0), K(XR, 0)], "KESIT")
pl([K(XL, -0.1), K(XR, -0.1)], "KESIT-INCE")
hatch([[K(XL, 0), K(XR, 0), K(XR, -0.1), K(XL, -0.1)]], "KESIT-TARAMA", "GRAVEL", 0.015)
# doğal zemin taraması (kazı ve anotlar hariç)
ANX = 1.6
bag = lambda x: [K(x - 0.07, -1.85), K(x + 0.07, -1.85), K(x + 0.07, -1.35), K(x - 0.07, -1.35)]
hatch([[K(XL, -0.1), K(XR, -0.1), K(XR, ZB), K(XL, ZB)], [K(*p) for p in exc], bag(-ANX), bag(ANX)],
      "KESIT-TARAMA", "EARTH", 0.08)
# beton plak
slab = [K(-1.1, -2.95), K(1.1, -2.95), K(1.1, -2.70), K(-1.1, -2.70)]
pl(slab, "KESIT", True)
hatch([slab], "KESIT-TARAMA", "AR-CONC", 0.006)
# kum
sand = [K(-xe(-2.7) + 0.0, -2.7), K(xe(-2.7), -2.7), K(1.9, -0.1), K(-1.9, -0.1)]
hatch([sand, ("circle", K(0, -1.6), KS * 0.8)], "KESIT-TARAMA", "AR-SAND", 0.008)
# tank
circ(K(0, -1.6), KS * 0.8, "KESIT")
circ(K(0, -1.6), KS * 0.79, "KESIT-INCE")
circ(K(0, -1.6), KS * 0.815, "KESIT-INCE")
pl([K(-1.0, -1.6), K(1.0, -1.6)], "EKSEN")
pl([K(0, -0.65), K(0, -2.55)], "EKSEN")
# ankraj kayışı
Cc, rs = (0.0, -1.6), 0.83


def tangent(A, left=True):
    dx, dy = A[0] - Cc[0], A[1] - Cc[1]
    d = math.hypot(dx, dy)
    al = math.acos(rs / d)
    b = math.atan2(dy, dx)
    cands = [(Cc[0] + rs * math.cos(b + s * al), Cc[1] + rs * math.sin(b + s * al)) for s in (1, -1)]
    return min(cands, key=lambda p: p[0]) if left else max(cands, key=lambda p: p[0])


A_, B_ = (-0.95, -2.7), (0.95, -2.7)
TL, TRt = tangent(A_, True), tangent(B_, False)
thL = math.atan2(TL[1] - Cc[1], TL[0] - Cc[0])
thR = math.atan2(TRt[1] - Cc[1], TRt[0] - Cc[0])
dth = (thL - thR) % (2 * math.pi)
pl([(*K(*A_), 0), (*K(*TL), -math.tan(dth / 4)), (*K(*TRt), 0), (*K(*B_), 0)], "KESIT-INCE", fmt="xyb")
for x in (-0.95, 0.95):
    rect(*K(x - 0.03, -2.78), *K(x + 0.03, -2.70), "KESIT")
# anotlar
for x in (-ANX, ANX):
    pl(bag(x), "KK-ANOT", True)
    rect(*K(x - 0.038, -1.78), *K(x + 0.038, -1.42), "KK-ANOT")
    hatch([[K(x - 0.038, -1.78), K(x + 0.038, -1.78), K(x + 0.038, -1.42), K(x - 0.038, -1.42)]], "KK-ANOT",
          "ANSI31", 0.02)
# referans elektrot
REx = 1.12
rect(*K(REx - 0.03, -1.70), *K(REx + 0.03, -1.50), "KK-OLCUM")
# ölçüm kutusu direği
PXk = -2.6
rect(*K(PXk - 0.03, 0), *K(PXk + 0.03, 0.95), "KK-OLCUM")
rect(*K(PXk - 0.15, 0.80), *K(PXk + 0.15, 1.15), "KK-OLCUM")
hatch([[K(PXk - 0.15, 0.8), K(PXk + 0.15, 0.8), K(PXk + 0.15, 1.15), K(PXk - 0.15, 1.15)]], "KK-OLCUM",
      "ANSI37", 0.03)
rect(*K(PXk - 0.12, -0.6), *K(PXk + 0.12, 0), "KESIT-INCE")
# kablolar
TW = (0.8 * math.cos(math.radians(118)), -1.6 + 0.8 * math.sin(math.radians(118)))
cab = [[K(-ANX, -1.35), K(-ANX, -0.55), K(PXk + 0.02, -0.55)],
       [K(ANX, -1.35), K(ANX, -0.60), K(PXk + 0.02, -0.60)],
       [K(*TW), K(TW[0], -0.50), K(PXk + 0.02, -0.50)],
       [K(REx, -1.50), K(REx, -0.65), K(PXk + 0.02, -0.65)]]
for c in cab:
    pl(c, "KK-KABLO")
pl([K(PXk + 0.02, -0.65), K(PXk + 0.02, 0.85)], "KK-KABLO")
pl([K(-2.4, -0.3), K(2.0, -0.3)], "KK-KABLO", color=2)
# kotlar
for z, s in ((0.0, "±0.00"), (-0.80, "-0.80"), (-1.60, "-1.60"), (-2.40, "-2.40"), (-2.70, "-2.70"),
             (-2.95, "-2.95")):
    kot(K(2.35, z), s)
# ölçüler
dim_al(K(0.35, 0), K(0.35, -0.8), 0.0001 + 0.0, "KK25")
dim_al(K(-0.35, -0.8), K(-0.35, -2.4), 0.0001, "KK25")
dim_al(K(0.0, -2.4), K(0.0, -2.7), -0.25, "KK25")
dim_al(K(0.8, -1.6), K(ANX, -1.6), -1.1, "KK25")
dim_al(K(ANX + 0.07, -1.35), K(ANX + 0.07, -1.85), -0.35, "KK25")
dim_al(K(-2.6, 0.0), K(-2.6, -0.55), 0.55, "KK25")
# etiketler (sol / sağ kenar boşluğunda)
LXk, RXk = K(-3.15, 0)[0], K(3.15, 0)[0]
for tgt, z, txt in (((PXk, 1.0), 1.0, ["ÖK-1 ölçüm kutusu (direk üstü)"]),
                    ((-2.9, -0.05), 0.35, ["Çakıl kaplama 10 cm"]),
                    ((-2.2, -0.3), -0.3, ["Kablo ikaz bandı (-30 cm)"]),
                    ((-ANX, -1.6), -1.6, ["MA-1  Mg anot 10 Lb", "doğal zemine, ıslatılarak"]),
                    ((-0.636, -2.134), -2.3, ["Ankraj kayışı + izolasyon pedi"]),
                    ((-0.6, -2.85), -2.85, ["Beton ankraj plağı"])):
    leader(K(*tgt), (LXk, K(0, z)[1]), txt, -1)
for tgt, z, txt in (((REx, -1.6), -1.0, ["RE  Cu/CuSO4 referans elektrot"]),
                    ((ANX, -1.6), -1.3 - 0.0, ["MA-2  Mg anot 10 Lb"]),
                    ((0.3, -2.55), -2.55, ["Elenmiş kum yatak / dolgu"])):
    leader(K(*tgt), (RXk, K(0, z)[1]), txt, 1)
leader(K(0.35, -1.25), (K(1.25, 0)[0], K(0, 1.05)[1]), ["LPG TANKI Ø160 cm (10 m³)", "fabrika kaplamalı"], 1)
leader(K(*TW), (K(0.9, 0)[0], K(0, 0.55)[1]), ["Termit kaynak bağlantısı (tank)"], 1)

# ============================================================================ 5) ANOT DETAYLARI (1/5)
DS = 10.0
title("DETAY-1: HAZIR DOLGULU Mg ANOT  (Ölçek 1/5)", (58.6, 11.55),
      sub="Ölçüler mm'dir, üretici kataloğuna göre teyit edilecektir.")


def anot_detay(cx, by, spec, name):
    L, d = spec["L"] * DS, spec["d"] * DS
    iw, il = spec["ing"][0] * DS, spec["ing"][1] * DS
    x0, x1 = cx - d / 2, cx + d / 2
    bagp = [(x0, by), (x1, by), (x1, by + L), (cx + d * 0.15, by + L + 0.2), (cx - d * 0.15, by + L + 0.2),
            (x0, by + L)]
    pl(bagp, "DETAY", True)
    iy0 = by + (L - il) / 2
    ing = [(cx - iw / 2, iy0), (cx + iw / 2, iy0), (cx + iw / 2, iy0 + il), (cx - iw / 2, iy0 + il)]
    hatch([bagp, ing], "DETAY-TARAMA", "DOTS", 0.03)
    pl(ing, "KK-ANOT", True)
    hatch([ing], "KK-ANOT", "ANSI31", 0.04)
    pl([(cx, iy0 - 0.15), (cx, iy0 + il + 0.15)], "DETAY")
    tie = by + L + 0.2
    pl([(cx - 0.12, tie), (cx + 0.12, tie)], "DETAY")
    cab = [(cx, iy0 + il + 0.15), (cx, tie + 0.6), (cx + 0.4, tie + 1.0), (cx + 1.0, tie + 1.0)]
    pl(cab, "KK-KABLO")
    for p1, p2, dd in (((x0, by), (x0, by + L), 0.45), ((x0, by), (x1, by), -0.4),
                       ((cx + iw / 2, iy0), (cx + iw / 2, iy0 + il), -(d / 2 - iw / 2) - 0.35)):
        msp.add_aligned_dim(p1=p1, p2=p2, distance=dd, dimstyle="KK5", dxfattribs={"layer": "OLCU"}).render()
    T(name, (cx, by - 0.75), H3, "YAZI", TA.TOP_CENTER)
    return dict(cx=cx, by=by, L=L, d=d, iy0=iy0, il=il, iw=iw, tie=tie, cab=cab)


A1 = anot_detay(61.3, 1.2, ANOT["10 Lb"], "Mg ANOT 10 Lb (MA-1, MA-2)")
A2 = anot_detay(65.4, 1.2, ANOT["3,5 Lb"], "Mg ANOT 3,5 Lb (MA-3, MA-4)")
c = A2
lab = [((c["cab"][-1][0], c["cab"][-1][1]), ["NYY 1x6 mm² anot kablosu,", "fabrika çıkışlı min. 3 m"]),
       ((c["cx"] + 0.12, c["tie"]), ["Torba bağı"]),
       ((c["cx"], c["iy0"] + c["il"] + 0.08), ["Kablo-çekirdek bağlantısı", "gümüş lehim + epoksi izolasyon"]),
       ((c["cx"] + c["d"] / 2 - 0.12, c["by"] + c["L"] - 0.4), ["Hazır dolgu: %75 alçı + %20 bentonit",
                                                               "+ %5 sodyum sülfat"]),
       ((c["cx"] + c["iw"] / 2 - 0.08, c["iy0"] + c["il"] * 0.55), ["Mg alaşım külçe, yüksek potansiyelli",
                                                                    "(Ecorr ≤ -1,70 V Cu/CuSO4)"]),
       ((c["cx"], c["iy0"] - 0.1), ["Çelik çekirdek (galvanizli)"]),
       ((c["cx"] + c["d"] / 2, c["by"] + 0.25), ["Pamuklu / kağıt torba"])]
for i, (tgt, txt) in enumerate(lab):
    leader(tgt, (67.6, 7.0 - i * 0.92), txt, 1)
an_rows = []
for k, s_ in ANOT.items():
    an_rows.append((k, f"{s_['kg']} kg", f"Ø{s_['d'] * 1000:.0f}x{s_['L'] * 1000:.0f}",
                    f"{s_['ing'][0] * 1000:.0f}x{s_['ing'][0] * 1000:.0f}x{s_['ing'][1] * 1000:.0f}",
                    "2", "Tank" if k == "10 Lb" else "Hat / dispenser"))
table(71.1, 11.05, [("ANOT", 0.8, "C"), ("NET", 0.75, "C"), ("TORBA mm", 1.15, "C"), ("KÜLÇE mm", 1.35, "C"),
                    ("ADET", 0.55, "C"), ("YERİ", 1.4, "C")], an_rows)

# ============================================================================ 6) DETAYLAR (sağ sütun)
CX0 = 78.6
# ---- DETAY-2: ölçüm kutusu bağlantı şeması
title("DETAY-2: ÖLÇÜM KUTUSU ÖK-1 BAĞLANTI ŞEMASI", (CX0, 36.55), sub="Ölçeksiz. ÖK-2 aynı düzende (MA-3, MA-4, hat).")
bx0, by0, bx1, by1 = CX0 + 0.3, 30.4, CX0 + 7.7, 35.4
pl(bulge_poly(bx0, by0, bx1, by1, 0.15), "KK-OLCUM", True, fmt="xyb")
pl(bulge_poly(bx0 + 0.12, by0 + 0.12, bx1 - 0.12, by1 - 0.12, 0.1), "KK-OLCUM", True, fmt="xyb")
T("IP65 POLYESTER KUTU - kilitli kapak", ((bx0 + bx1) / 2, by1 - 0.35), H1, "YAZI", TA.MIDDLE_CENTER, color=2)
busy = by1 - 0.9
rect(bx0 + 0.6, busy - 0.06, bx1 - 0.6, busy + 0.06, "DETAY")
hatch([[(bx0 + 0.6, busy - 0.06), (bx1 - 0.6, busy - 0.06), (bx1 - 0.6, busy + 0.06), (bx0 + 0.6, busy + 0.06)]],
      "DETAY", solid=256)
T("YAPI (TANK) BARASI - bakır", ((bx0 + bx1) / 2, busy + 0.2), H1, "YAZI", TA.BOTTOM_CENTER)


def zigzag(x, y0, y1, w=0.08, n=6):
    pts = [(x, y0)]
    for i in range(n):
        pts.append((x + (w if i % 2 == 0 else -w), y0 + (y1 - y0) * (i + 0.5) / n))
    pts.append((x, y1))
    pl(pts, "DETAY")


terms = [("T1", "Tank kablosu 1"), ("T2", "Tank kablosu 2"), ("MA-1", "Anot 10 Lb"), ("MA-2", "Anot 10 Lb"),
         ("RE", "Referans elektrot")]
tx_list = [bx0 + 1.0 + i * 1.4 for i in range(len(terms))]
ty = by0 + 1.25
for (tn, desc), x in zip(terms, tx_list):
    circ((x, ty), 0.12, "DETAY")
    pl([(x - 0.08, ty - 0.08), (x + 0.08, ty + 0.08)], "DETAY")
    T(tn, (x, ty - 0.22), H1, "YAZI", TA.TOP_CENTER)
    pl([(x, ty - 0.12), (x, by0 - 0.6)], "KK-KABLO")
    T(desc, (x, by0 - 0.7), H1, "YAZI", TA.TOP_CENTER, color=8)
    if tn.startswith("T"):
        pl([(x, ty + 0.12), (x, busy - 0.06)], "DETAY")
    elif tn.startswith("MA"):
        pl([(x, ty + 0.12), (x, ty + 0.5)], "DETAY")
        zigzag(x, ty + 0.5, ty + 1.3)
        T("şönt 0,01 Ω", (x + 0.15, ty + 0.9), H1, "YAZI", TA.MIDDLE_LEFT)
        pl([(x, ty + 1.3), (x, ty + 1.55)], "DETAY")
        pl([(x, ty + 1.55), (x + 0.18, ty + 1.85)], "DETAY")
        circ((x, ty + 1.55), 0.03, "DETAY")
        circ((x, ty + 2.0), 0.03, "DETAY")
        pl([(x, ty + 2.0), (x, busy - 0.06)], "DETAY")
        T("köprü", (x - 0.12, ty + 1.78), H1, "YAZI", TA.MIDDLE_RIGHT)
    else:
        pl([(x, ty + 0.12), (x, ty + 0.8)], "DETAY")
        circ((x, ty + 0.9), 0.1, "DETAY")
        T("ölçüm", (x, ty + 1.1), H1, "YAZI", TA.BOTTOM_CENTER)

# ---- DETAY-3: izole flanş
title("DETAY-3: İZOLE FLANŞ KİTİ (Ölçek 1/2,5)", (CX0 + 9.4, 36.55), sub="DN32 PN40 - İF-1...İF-6")
FS = 20.0
fx, fy = CX0 + 12.3, 32.4
OD, th, gk, pod = 0.140 * FS, 0.020 * FS, 0.006 * FS, 0.0424 * FS
for s in (-1, 1):
    xa = fx + s * gk / 2
    xb = xa + s * th
    for side in (-1, 1):
        y0, y1 = fy + side * pod / 2, fy + side * OD / 2
        pts = [(xa, y0), (xb, y0), (xb, y1), (xa, y1)]
        pl(pts, "DETAY", True)
        hatch([pts], "DETAY-TARAMA", "ANSI31", 0.03, angle=0 if s < 0 else 90)
    pl([(xb, fy + pod / 2), (xb + s * 1.9, fy + pod / 2)], "DETAY")
    pl([(xb, fy - pod / 2), (xb + s * 1.9, fy - pod / 2)], "DETAY")
    pl([(xb + s * 1.9, fy + pod / 2 + 0.08), (xb + s * 1.82, fy), (xb + s * 1.9, fy - pod / 2 - 0.08)], "DETAY-INCE")
g = [(fx - gk / 2, fy + pod / 2), (fx + gk / 2, fy + pod / 2), (fx + gk / 2, fy + OD / 2 - 0.02),
     (fx - gk / 2, fy + OD / 2 - 0.02)]
for sgn in (1, -1):
    gg = [(x, fy + sgn * (y - fy)) for x, y in g]
    pl(gg, "KK-IZOLASYON", True)
    hatch([gg], "KK-IZOLASYON", solid=140)
# cıvatalar
for sgn in (1, -1):
    by = fy + sgn * (0.110 * FS / 2)
    L2 = gk / 2 + th + 0.45
    pl([(fx - L2, by - 0.12), (fx + L2, by - 0.12)], "DETAY")
    pl([(fx - L2, by + 0.12), (fx + L2, by + 0.12)], "DETAY")
    rect(fx - gk / 2 - th, by - 0.16, fx + gk / 2 + th, by + 0.16, "KK-IZOLASYON")
    for s_ in (-1, 1):
        x0w = fx + s_ * (gk / 2 + th)
        wp = [(x0w, by - 0.36), (x0w + s_ * 0.08, by - 0.36), (x0w + s_ * 0.08, by + 0.36), (x0w, by + 0.36)]
        pl(wp, "KK-IZOLASYON", True)
        hatch([wp], "KK-IZOLASYON", solid=140)
        rect(x0w + s_ * 0.08, by - 0.36, x0w + s_ * 0.14, by + 0.36, "DETAY")
        rect(x0w + s_ * 0.14, by - 0.28, x0w + s_ * 0.40, by + 0.28, "DETAY")
pl([(fx - 2.4, fy), (fx + 2.4, fy)], "EKSEN")
bt = fy + 0.110 * FS / 2
rgt = [((fx, fy + pod / 2 + 0.25), ["İzolasyon contası (fiber / neopren)"]),
       ((fx + 0.05, bt + 0.14), ["İzolasyon manşonu (G-10)"]),
       ((fx + gk / 2 + th + 0.04, bt + 0.3), ["İzolasyon pulu (G-10)"]),
       ((fx + gk / 2 + th + 0.3, bt + 0.2), ["Çelik pul + somun + cıvata"])]
for i, (tgt, txt) in enumerate(rgt):
    leader(tgt, (fx + 2.0, fy + 2.6 - i * 0.55), txt, 1)
for i, (tgt, txt) in enumerate((((fx - gk / 2 - th / 2, fy - OD / 2 + 0.3), ["Flanş PN40"]),
                                ((fx - 1.6, fy - pod / 2), ["SCH80 boru"]))):
    leader(tgt, (fx - 1.9, fy - 1.9 - i * 0.55), txt, -1)

# ---- DETAY-4: termit kaynak bağlantısı
title("DETAY-4: TANK KABLO BAĞLANTISI (Ölçek 1/5)", (CX0, 28.3), sub="Termit kaynak / pin brazing")
wx, wy = CX0 + 2.6, 24.6
pl([(wx - 2.0, wy), (wx + 2.0, wy)], "DETAY")
pl([(wx - 2.0, wy - 0.1), (wx + 2.0, wy - 0.1)], "DETAY")
hatch([[(wx - 2.0, wy - 0.1), (wx + 2.0, wy - 0.1), (wx + 2.0, wy), (wx - 2.0, wy)]], "DETAY-TARAMA", "ANSI31", 0.02)
pl([(wx - 2.0, wy + 0.05), (wx - 0.55, wy + 0.05)], "DETAY-INCE")
pl([(wx + 0.55, wy + 0.05), (wx + 2.0, wy + 0.05)], "DETAY-INCE")
msp.add_arc((wx, wy), 0.55, 0, 180, dxfattribs={"layer": "DETAY"})
pl([(wx - 0.18, wy), (wx - 0.12, wy + 0.12), (wx + 0.12, wy + 0.12), (wx + 0.18, wy)], "DETAY", True)
hatch([[(wx - 0.18, wy), (wx - 0.12, wy + 0.12), (wx + 0.12, wy + 0.12), (wx + 0.18, wy)]], "DETAY", solid=256)
pl([(wx, wy + 0.12), (wx + 0.2, wy + 0.3), (wx + 0.9, wy + 0.3), (wx + 1.3, wy + 0.8), (wx + 2.0, wy + 0.8)],
   "KK-KABLO")
for tgt, el, txt, sd in (((wx - 1.5, wy - 0.05), (wx - 1.2, wy - 0.75), ["Tank cidarı (çelik)"], -1),
                         ((wx - 1.2, wy + 0.05), (wx - 1.0, wy + 0.65), ["Fabrika kaplaması"], -1),
                         ((wx, wy + 0.06), (wx - 0.35, wy - 0.9), ["Termit kaynak"], 1),
                         ((wx - 0.3, wy + 0.47), (wx - 0.9, wy + 1.15), ["Epoksi kaplama tamir başlığı"], -1),
                         ((wx + 1.6, wy + 0.8), (wx + 1.9, wy + 1.25), ["NYY 1x10 mm²"], 1)):
    leader(tgt, el, txt, sd)

# ---- DETAY-5: referans elektrot
title("DETAY-5: KALICI REFERANS ELEKTROT (Ölçek 1/10)", (CX0 + 9.4, 28.3), sub="Cu/CuSO4, tank yanına, tank ekseni kotunda")
rx, ry = CX0 + 11.4, 23.4
rb = [(rx - 0.38, ry), (rx + 0.38, ry), (rx + 0.38, ry + 1.5), (rx - 0.38, ry + 1.5)]
re = [(rx - 0.13, ry + 0.25), (rx + 0.13, ry + 0.25), (rx + 0.13, ry + 1.25), (rx - 0.13, ry + 1.25)]
pl(rb, "DETAY", True)
hatch([rb, re], "DETAY-TARAMA", "DOTS", 0.03)
pl(re, "KK-OLCUM", True)
rect(rx - 0.1, ry + 0.25, rx + 0.1, ry + 0.4, "KK-OLCUM")
hatch([[(rx - 0.1, ry + 0.25), (rx + 0.1, ry + 0.25), (rx + 0.1, ry + 0.4), (rx - 0.1, ry + 0.4)]], "KK-OLCUM",
      solid=8)
pl([(rx, ry + 0.4), (rx, ry + 1.2)], "DETAY")
pl([(rx, ry + 1.25), (rx, ry + 2.1), (rx + 0.5, ry + 2.5), (rx + 1.2, ry + 2.5)], "KK-KABLO")
msp.add_aligned_dim(p1=(rx - 0.38, ry), p2=(rx - 0.38, ry + 1.5), distance=0.3, dimstyle="KK10",
                    dxfattribs={"layer": "OLCU"}).render()
msp.add_aligned_dim(p1=(rx - 0.38, ry), p2=(rx + 0.38, ry), distance=-0.3, dimstyle="KK10",
                    dxfattribs={"layer": "OLCU"}).render()
for i, (tgt, txt) in enumerate((((rx, ry + 0.32), ["Seramik gözenekli uç"]),
                                ((rx + 0.05, ry + 0.8), ["Cu çubuk + CuSO4 doygun çözelti"]),
                                ((rx + 0.3, ry + 1.1), ["Özel dolgu (jips + bentonit)"]),
                                ((rx + 0.9, ry + 2.5), ["Kablo 1x6 mm² (ÖK-1 RE terminaline)"]))):
    leader(tgt, (rx + 1.1, ry + 0.25 + i * 0.5 - (0.3 if i == 3 else 0)), txt, 1) if i < 3 else \
        leader(tgt, (rx + 1.4, ry + 2.9), txt, 1)

# ============================================================================ 7) HESAP
A_TANK = math.pi * TANK_D * (TANK_L - TANK_D / 2) + 2 * (math.pi * TANK_D ** 2 / 4) * 1.38
A_PIPE = math.pi * PIPE_OD * PIPE_LEN
A_TOT = A_TANK + A_PIPE
I_D = I_BARE * (1 - COAT_EFF) * SAFETY
I_REQ = A_TOT * I_D / 1000


def r_anot(s):
    return SOIL_RHO / (2 * math.pi * s["L"]) * (math.log(8 * s["L"] / s["d"]) - 1)


R10, R35 = r_anot(ANOT["10 Lb"]), r_anot(ANOT["3,5 Lb"])
DV = abs(E_MG - E_KRIT)
I10, I35 = DV / R10, DV / R35
I_CAP = 2 * I10 + 2 * I35
M_TOT = 2 * ANOT["10 Lb"]["kg"] + 2 * ANOT["3,5 Lb"]["kg"]
M_REQ = I_REQ * 8760 * LIFE_Y / (MG_CAP * MG_UTIL)
LIFE = M_TOT * MG_CAP * MG_UTIL / (I_REQ * 8760)

HX, HY = CX0, 21.0
title("KATODİK KORUMA HESABI (MEVCUT SİSTEM KONTROLÜ)", (HX, HY))
hrows = [
    ("Korunan yapı", "LPG tankı 10 m³ + toprak altı LPG hatları"),
    ("Tank yüzeyi (Ø1,60 x 5,40 m, 2:1 bombeli)", f"At = {A_TANK:.1f} m²"),
    (f"Hat yüzeyi (~{PIPE_LEN:.0f} m, ort. Ø{PIPE_OD * 1000:.0f} mm)", f"Ah = {A_PIPE:.1f} m²"),
    ("Toplam yüzey", f"A = {A_TOT:.1f} m²"),
    ("Çıplak çelik akım yoğunluğu (zemin)", f"ib = {I_BARE:.0f} mA/m²"),
    ("Ortalama kaplama verimi / emniyet katsayısı", f"%{COAT_EFF * 100:.0f}  /  {SAFETY}"),
    ("Tasarım akım yoğunluğu  i = ib x (1-η) x k", f"i = {I_D:.2f} mA/m²"),
    ("Gerekli koruma akımı  I = A x i", f"I = {I_REQ * 1000:.0f} mA"),
    ("Zemin özdirenci (kabul, sahada ölçülecek)", f"ρ = {SOIL_RHO:.0f} Ω·m"),
    ("Anot direnci (Dwight)  R = ρ/(2πL)·[ln(8L/d) - 1]", f"10 Lb: {R10:.1f} Ω  /  3,5 Lb: {R35:.1f} Ω"),
    (f"Sürücü gerilim  ΔE = |{E_MG}| - |{E_KRIT}|", f"ΔE = {DV:.2f} V"),
    ("Anot çıkış akımı  Ia = ΔE / R", f"10 Lb: {I10 * 1000:.0f} mA  /  3,5 Lb: {I35 * 1000:.0f} mA"),
    ("Toplam anot kapasitesi (2 x 10 Lb + 2 x 3,5 Lb)", f"{I_CAP * 1000:.0f} mA  ≥  {I_REQ * 1000:.0f} mA  UYGUN"),
    (f"Gerekli anot kütlesi ({LIFE_Y} yıl, Q={MG_CAP:.0f} Ah/kg, u={MG_UTIL})", f"{M_REQ:.1f} kg  ≤  {M_TOT:.1f} kg  UYGUN"),
    ("Hesaplanan anot ömrü  t = M·Q·u / (I·8760)", f"t ≈ {LIFE:.0f} yıl  ≥  {LIFE_Y} yıl  UYGUN"),
]
table(HX, HY - 0.25, [("PARAMETRE", 10.2, "L"), ("DEĞER", 7.9, "L")], hrows, rh=0.30, hl={12, 13, 14})
T("Sonuç: Mevcut 4 adet Mg anot ile tank ve hatlar için gerekli koruma akımı ve 20 yıllık ömür sağlanmaktadır.",
  (HX, HY - 0.25 - 0.36 - 15 * 0.30 - 0.25), H1, "YAZI", TA.TOP_LEFT, color=3)
T("Devreye alma ve periyodik ölçümlerde Eoff ≤ -850 mV sağlanamazsa ilave anot tesis edilecektir.",
  (HX, HY - 0.25 - 0.36 - 15 * 0.30 - 0.48), H1, "YAZI", TA.TOP_LEFT, color=3)

# ============================================================================ 8) PAFTA + ANTET
FX0, FY0, FY1 = -12.26, -0.71, 37.30
FX1 = 97.6
rect(FX0, FY0, FX1, FY1, "PAFTA")
# bölüm ayraçları
for x in (39.9, 58.2, 78.2):
    pl([(x, FY0), (x, FY1)], "ANTET-INCE")
pl([(39.9, 15.75), (58.2, 15.75)], "ANTET-INCE")
pl([(58.2, 25.65), (78.2, 25.65)], "ANTET-INCE")
pl([(58.2, 12.2), (78.2, 12.2)], "ANTET-INCE")
pl([(78.2, 29.0), (FX1, 29.0)], "ANTET-INCE")
pl([(78.2, 21.65), (FX1, 21.65)], "ANTET-INCE")
pl([(87.2, 29.0), (87.2, FY1)], "ANTET-INCE")
pl([(87.2, 21.65), (87.2, 29.0)], "ANTET-INCE")

# ---------------------------------------------------------------- ölçüm formu (antet üstü)
title("DEVREYE ALMA / PERİYODİK ÖLÇÜM FORMU", (CX0, 13.05))
olc = [
    ("ÖK-1 / T1", "Tank-zemin potansiyeli Eon / Eoff", "Eoff ≤ -850 mV", "", ""),
    ("ÖK-1 / MA-1", "Anot akımı (şönt mV / 0,01 Ω)", "> 0 mA", "", ""),
    ("ÖK-1 / MA-2", "Anot akımı (şönt mV / 0,01 Ω)", "> 0 mA", "", ""),
    ("ÖK-2 / Hat", "Hat-zemin potansiyeli Eon / Eoff", "Eoff ≤ -850 mV", "", ""),
    ("ÖK-2 / MA-3, MA-4", "Anot akımları", "> 0 mA", "", ""),
    ("İF-1 ... İF-6", "İzolasyon kontrolü (potansiyel farkı)", "Yalıtım var", "", ""),
    ("Tank sahası", "Zemin özdirenci (Wenner)", "Ω·m", "", ""),
]
table(CX0, 12.75, [("ÖLÇÜM NOKTASI", 3.3, "L"), ("ÖLÇÜM", 6.4, "L"), ("KRİTER", 3.0, "C"),
                   ("ÖLÇÜLEN", 2.8, "C"), ("TARİH / İMZA", 3.6, "C")], olc, rh=0.30)

# ---------------------------------------------------------------- antet
AX0, AX1, AY0 = 78.2, FX1, FY0
yb = [AY0, AY0 + 1.0]                     # alt bilgi satırı
yb += [yb[-1] + 0.38, yb[-1] + 0.76, yb[-1] + 1.11]   # revizyon 2 satır + başlık
yb += [yb[-1] + 2.3, yb[-1] + 2.7]        # firma bloğu + başlık
yb += [yb[-1] + 0.55, yb[-1] + 1.10, yb[-1] + 1.80, yb[-1] + 2.55, yb[-1] + 3.40]
AY1 = yb[-1]
rect(AX0, AY0, AX1, AY1, "ANTET")
for y in yb[1:-1]:
    pl([(AX0, y), (AX1, y)], "ANTET" if y not in (yb[2], yb[3]) else "ANTET-INCE")
(y_alt, y_r1, y_r2, y_rl, y_fb, y_fh, y_lpg, y_adr, y_isv, y_ic, y_pr) = yb[1:]
# proje / içerik
T("PROJE", (AX0 + 0.2, y_pr - 0.22), H1, "YAZI", TA.MIDDLE_LEFT, color=8)
T("AKARYAKIT VE LPG İKMAL İSTASYONU - LPG TANKI VE HATLARI KATODİK KORUMA PROJESİ",
  (AX0 + 0.2, y_ic + 0.3), H3, "YAZI", TA.MIDDLE_LEFT)
T("PAFTA İÇERİĞİ", (AX0 + 0.2, y_ic - 0.2), H1, "YAZI", TA.MIDDLE_LEFT, color=8)
T("Vaziyet ve KK uygulama planı, kesit A-A, perspektif, izometrik tesisat şeması, detaylar, hesap",
  (AX0 + 0.2, y_isv + 0.25), H2, "YAZI", TA.MIDDLE_LEFT)
LBLW = 3.6
pl([(AX0 + LBLW, y_fh), (AX0 + LBLW, y_isv)], "ANTET")
for (y0, y1), lab, val, hh in (((y_adr, y_isv), "İŞVEREN / MAL SAHİBİ", ISVEREN, H3),
                               ((y_lpg, y_adr), "ADRES", ADRES, H2),
                               ((y_fh, y_lpg), "LPG TESİSATI", "Yetkili firma (İPRAGAZ) tarafından tesis edilmiştir",
                                H2)):
    T(lab, (AX0 + 0.2, (y0 + y1) / 2), H1, "YAZI", TA.MIDDLE_LEFT, color=8)
    T(val, (AX0 + LBLW + 0.2, (y0 + y1) / 2), hh, "YAZI", TA.MIDDLE_LEFT)
# çizen firma / müellif / onay
XC1, XC2 = AX0 + 6.6, AX0 + 13.6
for x in (XC1, XC2):
    pl([(x, y_rl), (x, y_fh)], "ANTET")
T("ÇİZEN FİRMA", (AX0 + 0.2, (y_fb + y_fh) / 2), H1, "YAZI", TA.MIDDLE_LEFT, color=8)
T("PROJE MÜELLİFİ", (XC1 + 0.2, (y_fb + y_fh) / 2), H1, "YAZI", TA.MIDDLE_LEFT, color=8)
T("ONAY", (XC2 + 0.2, (y_fb + y_fh) / 2), H1, "YAZI", TA.MIDDLE_LEFT, color=8)
lg = (AX0 + 0.35, y_rl + 0.3, XC1 - 0.35, y_fb - 0.3)
rect(*lg, "ANTET-LOGO")
rect(lg[0] + 0.08, lg[1] + 0.08, lg[2] - 0.08, lg[3] - 0.08, "ANTET-INCE")
lcx, lcy = (lg[0] + lg[2]) / 2, (lg[1] + lg[3]) / 2
T(FIRMA, (lcx, lcy + 0.28), H3, "YAZI", TA.MIDDLE_CENTER)
pl([(lcx - 1.35, lcy + 0.05), (lcx + 1.35, lcy + 0.05)], "ANTET-LOGO")
T(f"BÜRO TESCİL NO: {BURO_TESCIL}", (lcx, lcy - 0.2), H1, "YAZI", TA.MIDDLE_CENTER)
T(MUHENDIS, (XC1 + 0.2, y_fb - 0.45), H3, "YAZI", TA.MIDDLE_LEFT)
T(f"EMO SİCİL NO: {EMO_SICIL}", (XC1 + 0.2, y_fb - 0.85), H2, "YAZI", TA.MIDDLE_LEFT)
T(f"BÜRO TESCİL NO: {BURO_TESCIL}", (XC1 + 0.2, y_fb - 1.2), H2, "YAZI", TA.MIDDLE_LEFT)
T("İMZA:", (XC1 + 0.2, y_rl + 0.35), H1, "YAZI", TA.MIDDLE_LEFT, color=8)
pl([(XC1 + 1.0, y_rl + 0.28), (XC2 - 0.4, y_rl + 0.28)], "ANTET-INCE")
# revizyonlar
T("REVİZYONLAR", (AX0 + 0.2, (y_r2 + y_rl) / 2), H1, "YAZI", TA.MIDDLE_LEFT, color=8)
rv = [0.0, 1.0, 3.0, 13.6, 16.3, AX1 - AX0]
for x in rv[1:-1]:
    pl([(AX0 + x, y_alt), (AX0 + x, y_r2)], "ANTET-INCE")
for (a, b), s1, s2 in zip(zip(rv, rv[1:]), ("REV", "TARİH", "AÇIKLAMA", "ÇİZEN", "KONTROL"),
                          ("00", TARIH, "İlk yayın", "SMA", "A.S.A.")):
    T(s1, (AX0 + (a + b) / 2, (y_r1 + y_r2) / 2), H1, "YAZI", TA.MIDDLE_CENTER, color=8)
    T(s2, (AX0 + (a + b) / 2, (y_alt + y_r1) / 2), H1, "YAZI", TA.MIDDLE_CENTER)
# alt bilgi
bc_ = [0.0, 4.4, 8.0, 11.6, 14.8, AX1 - AX0]
for x in bc_[1:-1]:
    pl([(AX0 + x, AY0), (AX0 + x, y_alt)], "ANTET")
for (a, b), lab, val in zip(zip(bc_, bc_[1:]), ("ÖLÇEK", "TARİH", "PAFTA NO", "REVİZYON", "PAFTA"),
                            ("1/50 (aksi belirtilmedikçe)", TARIH, "KK-01", "00", "1 / 1")):
    T(lab, (AX0 + a + 0.15, y_alt - 0.18), H1, "YAZI", TA.MIDDLE_LEFT, color=8)
    T(val, (AX0 + (a + b) / 2, AY0 + 0.35), H3, "YAZI", TA.MIDDLE_CENTER)

# ============================================================================ kayıt
_lts = {lt.dxf.name.lower() for lt in doc.linetypes}
assert all(l.dxf.linetype.lower() in _lts for l in doc.layers), "tanımsız çizgi tipi"
for e in msp.query("TEXT"):
    assert H1 - 1e-6 <= e.dxf.height <= H3 + 1e-6, e.dxf.text
for e in msp.query("MTEXT"):
    assert H1 - 1e-6 <= e.dxf.char_height <= H3 + 1e-6
doc.encoding = "cp1254"
doc.saveas(OUT)
print("DXF:", OUT)
print(f"A={A_TOT:.1f} m2  I={I_REQ * 1000:.0f} mA  cap={I_CAP * 1000:.0f} mA  life={LIFE:.0f} y  "
      f"pipe={PIPE_LEN:.1f} m  cable={CABLE_LEN:.0f} m")

if "--png" in sys.argv:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy, LineweightPolicy

    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR,
                        lineweight_policy=LineweightPolicy.ABSOLUTE, lineweight_scaling=0.6)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(msp)
    fig.set_size_inches(110 / 2.54 * 1.0, 38 / 2.54 * 1.0)
    fig.savefig(PNG, dpi=120)
    print("PNG:", PNG)
