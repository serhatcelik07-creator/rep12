# -*- coding: utf-8 -*-
"""TEMİZ_1.dxf mimari planına mekanik ekipman sembolleri + elektrik güç/gerilim etiketleri + tablolar ekler."""
import json, math, sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezdxf
from ezdxf.enums import TextEntityAlignment, MTextEntityAlignment
from data import *
from cooling import hesapli_odalar, hesapli_dis, geometri, yuk
VRF_ODALAR = hesapli_odalar()
VRF_DIS = hesapli_dis(VRF_ODALAR)
YUK = {(d['kat'], d['no']): yuk(d)[3] / 1000 for d in geometri()}

SRC, OUT = sys.argv[1], sys.argv[2]
ROOMS = json.load(open(sys.argv[3]))
doc = ezdxf.readfile(SRC)
msp = doc.modelspace()

# ---------------------------------------------------------------- stil / katman
if 'MEK_ELK' not in doc.styles:
    doc.styles.add('MEK_ELK', font='arial.ttf')
LAYERS = {
    'MEK-ELK-VRF-IC': 4, 'MEK-ELK-VRF-DIS': 5, 'MEK-ELK-ISITMA': 1, 'MEK-ELK-SIHHI': 140,
    'MEK-ELK-HVL': 3, 'MEK-ELK-KLIMA': 150, 'MEK-ELK-ETIKET': 7, 'MEK-ELK-GUC': 6,
    'MEK-ELK-TABLO': 7, 'MEK-ELK-TABLO-CIZGI': 8, 'MEK-ELK-KAIDE': 8,
}
for n, c in LAYERS.items():
    if n not in doc.layers:
        doc.layers.add(n, color=c)
SYS_LAYER = {'ISITMA': 'MEK-ELK-ISITMA', 'SIHHİ TESİSAT': 'MEK-ELK-SIHHI', 'YAĞMUR SUYU': 'MEK-ELK-SIHHI',
             'HAVALANDIRMA': 'MEK-ELK-HVL', 'KLİMA': 'MEK-ELK-KLIMA'}

def tr(v, d=2):
    return f"{v:.{d}f}".replace('.', ',')

# ---------------------------------------------------------------- bloklar (birim: cm, 1/50)
def blk(name):
    if name in doc.blocks:
        doc.blocks.delete_block(name, safe=False)
    return doc.blocks.new(name)

def rect(b, w, h, cx=0, cy=0, **kw):
    b.add_lwpolyline([(cx-w/2, cy-h/2), (cx+w/2, cy-h/2), (cx+w/2, cy+h/2), (cx-w/2, cy+h/2)], close=True, dxfattribs=kw)

def btext(b, s, h, x=0, y=0):
    b.add_text(s, height=h, dxfattribs={'style': 'MEK_ELK'}).set_placement((x, y), align=TextEntityAlignment.MIDDLE_CENTER)

def pump(b, cx, cy, r=10):
    b.add_circle((cx, cy), r)
    b.add_lwpolyline([(cx-r*0.55, cy+r*0.8), (cx+r, cy), (cx-r*0.55, cy-r*0.8)])

def kaset(name, s):
    b = blk(name)
    rect(b, s, s); i = s*0.62
    rect(b, i, i)
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.add_line((sx*s/2, sy*s/2), (sx*i/2, sy*i/2))
    b.add_circle((0, 0), s*0.1)
kaset('MEK_VRF_KASET_570', 57)
kaset('MEK_VRF_KASET_840', 84)

def vrf_dis(name, w):
    b = blk(name)
    rect(b, w, 77)
    n = 2 if w > 100 else 1
    for k in range(n):
        cx = (-w/4 if n == 2 else 0) + k*w/2
        b.add_circle((cx, 0), 26); b.add_circle((cx, 0), 5)
        for a in (0, 120, 240):
            r = math.radians(a)
            b.add_line((cx+5*math.cos(r), 5*math.sin(r)), (cx+24*math.cos(r+0.5), 24*math.sin(r+0.5)))
vrf_dis('MEK_VRF_DIS_L', 124)
vrf_dis('MEK_VRF_DIS_S', 93)

b = blk('MEK_KAZAN'); rect(b, 50, 35)
b.add_lwpolyline([(-6, -10), (-9, 0), (-3, 6), (-2, 1), (2, 10), (7, 1), (6, -10)], close=True)
btext(b, 'KZ', 7, 0, -13.5)

b = blk('MEK_PANEL'); rect(b, 30, 20); b.add_line((-15, -10), (15, 10)); btext(b, 'KP', 6, 6, -5)

b = blk('MEK_POMPA'); pump(b, 0, 0, 10)
b = blk('MEK_POMPA2'); pump(b, -12, 0, 10); pump(b, 12, 0, 10); b.add_line((-22, 14), (22, 14)); b.add_line((-12, 10), (-12, 14)); b.add_line((12, 10), (12, 14))

b = blk('MEK_BOYLER'); b.add_circle((0, 0), 30); b.add_circle((0, 0), 25)
b.add_lwpolyline([(-15, -12), (-9, 12), (-3, -12), (3, 12), (9, -12), (15, 12)])

b = blk('MEK_GAZ'); rect(b, 18, 18); b.add_circle((0, 0), 6); btext(b, 'G', 6)

b = blk('MEK_FAN'); rect(b, 40, 28); b.add_circle((0, 0), 11)
for a in (45, 135, 225, 315):
    r = math.radians(a); b.add_line((0, 0), (11*math.cos(r), 11*math.sin(r)))
b.add_line((-20, -14), (-14, 0)); b.add_line((-14, 0), (-20, 14))   # akış yönü oku

b = blk('MEK_HIDROFOR'); b.add_circle((-14, 0), 18); btext(b, 'HT', 7, -14, 0)
pump(b, 16, 9, 8); pump(b, 16, -9, 8); b.add_line((4, 9), (8, 9)); b.add_line((4, -9), (8, -9))

b = blk('MEK_DALGIC'); rect(b, 32, 32); pump(b, 0, 2, 9)
b.add_lwpolyline([(-14, -11), (-10, -9), (-6, -11), (-2, -9), (2, -11), (6, -9), (10, -11), (14, -9)])

b = blk('MEK_DAVLUMBAZ'); rect(b, 70, 45); rect(b, 50, 28)
for sx in (-1, 1):
    for sy in (-1, 1):
        b.add_line((sx*35, sy*22.5), (sx*25, sy*14))
b.add_circle((0, 0), 7)

b = blk('MEK_KUMANDA'); rect(b, 16, 11); rect(b, 9, 5, 0, 1)

b = blk('MEK_SPLIT'); rect(b, 80, 20)
for y in (-4, 0, 4):
    b.add_line((-34, y), (34, y))
b = blk('MEK_SPLIT_DIS'); rect(b, 80, 30); b.add_circle((-12, 0), 12); b.add_circle((-12, 0), 3)
for x in (8, 14, 20, 26, 32):
    b.add_line((x, -12), (x, 12))

SYM = {'KAZAN': ('MEK_KAZAN', 50, 35), 'PANEL': ('MEK_PANEL', 30, 20), 'POMPA': ('MEK_POMPA', 20, 20),
       'POMPA2': ('MEK_POMPA2', 44, 30), 'BOYLER': ('MEK_BOYLER', 60, 60), 'GAZ': ('MEK_GAZ', 18, 18),
       'FAN': ('MEK_FAN', 40, 28), 'HIDROFOR': ('MEK_HIDROFOR', 66, 38), 'DALGIC': ('MEK_DALGIC', 32, 32),
       'DAVLUMBAZ': ('MEK_DAVLUMBAZ', 70, 45), 'KUMANDA': ('MEK_KUMANDA', 16, 11), 'SPLIT': ('MEK_SPLIT', 80, 20)}

# ---------------------------------------------------------------- yardımcı çizimler
def text(x, y, s, h, layer, align=TextEntityAlignment.LEFT, color=None):
    a = {'style': 'MEK_ELK', 'layer': layer}
    if color is not None:
        a['color'] = color
    t = msp.add_text(s, height=h, dxfattribs=a)
    t.set_placement((x, y), align=align)
    return t

def tagbox(x, y, s, layer, h=8.5):
    """Etiket balonu: yuvarlatılmış köşeli çerçeve içinde cihaz kodu (x,y sol-alt)."""
    w = len(s)*h*0.68 + 8
    text(x + w/2, y + h*0.85, s, h, 'MEK-ELK-ETIKET', TextEntityAlignment.MIDDLE_CENTER)
    msp.add_lwpolyline([(x, y), (x+w, y), (x+w, y+h*1.7), (x, y+h*1.7)], close=True,
                       dxfattribs={'layer': layer})
    return w

def guc_txt(e):
    kod, sist, ad, oz, mah, kat, adet, cal, kw, v, faz = e[:11]
    if kw == 0:
        return 'elektrik bağlantısı yok'
    fz = '230V 1~' if faz == 1 else '400V 3~'
    if adet > 1:
        yd = f" ({cal}+{adet-cal})" if cal < adet else ''
        return f"{adet}x{tr(kw)} kW{yd} {fz}"
    return f"{tr(kw)} kW {fz}"

# ---------------------------------------------------------------- ekipmanlar
placed_boxes = []
for e in EKIPMAN:
    kod, sist, ad, oz, mah, kat, adet, cal, kw, v, faz, cos, pano, sym, pos, src = e
    layer = SYS_LAYER[sist]
    bname, w, h = SYM[sym]
    x, y = pos
    msp.add_blockref(bname, (x, y), dxfattribs={'layer': layer})
    # etiket: sembolün üstünde kod balonu, altında güç bilgisi
    tw = tagbox(x - w/2, y + h/2 + 3, kod, layer)
    g = guc_txt(e)
    if ' 230V' in g or ' 400V' in g:
        i = g.rfind(' ', 0, g.find('V ') - 2)
        text(x - w/2, y - h/2 - 9, g[:i], 6.5, 'MEK-ELK-GUC')
        text(x - w/2, y - h/2 - 18, g[i+1:], 6.5, 'MEK-ELK-GUC')
    else:
        text(x - w/2, y - h/2 - 9, g, 6.5, 'MEK-ELK-GUC')

# Split klima dış üniteleri (server)
for i, (x, y) in enumerate(SPLIT_DIS_KONUM):
    msp.add_blockref('MEK_SPLIT_DIS', (x, y), dxfattribs={'layer': 'MEK-ELK-KLIMA'})
    tagbox(x - 40, y + 18, f'SPLT-1/{"D" if i==0 else "D (YEDEK)"}', 'MEK-ELK-KLIMA', 7)
text(3380, 818, 'SPLT-1 dış üniteler (dış cephe konsolu) - besleme iç ünite üzerinden', 6.5, 'MEK-ELK-GUC')

# Yağmur suyu deposu (gömülü) - gösterim
x0, y0, x1, y1 = YAGMUR_DEPO
msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={'layer': 'MEK-ELK-SIHHI', 'linetype': 'DASHED' if 'DASHED' in doc.linetypes else 'CONTINUOUS'})
text((x0+x1)/2, y1 - 14, 'YAĞMUR SUYU DEPOSU 12 m³ (GÖMÜLÜ)', 7, 'MEK-ELK-ETIKET', TextEntityAlignment.MIDDLE_CENTER)
msp.add_lwpolyline([(3920, 2760), (4060, 2760), (4060, 2880), (3920, 2880)], close=True, dxfattribs={'layer': 'MEK-ELK-SIHHI'})
text(3990, 2866, 'MANEVRA ODASI', 6.5, 'MEK-ELK-ETIKET', TextEntityAlignment.MIDDLE_CENTER)

# VRF dış üniteler + beton kaide
kx0 = min(p[0] for p in VRF_DIS_KONUM.values()) - 110; kx1 = max(p[0] for p in VRF_DIS_KONUM.values()) + 100
ky = list(VRF_DIS_KONUM.values())[0][1]
msp.add_lwpolyline([(kx0, ky-75), (kx1, ky-75), (kx1, ky+75), (kx0, ky+75)], close=True, dxfattribs={'layer': 'MEK-ELK-KAIDE'})
text(kx0 + 5, ky + 82, 'VRF DIŞ ÜNİTELER - 10 cm BETON KAİDE + ÇELİK KAFES (KAİDE, ÜNİTE EBADINDAN 50 cm BÜYÜK)', 7, 'MEK-ELK-ETIKET')
for d in VRF_DIS:
    sistem, mod, hp, qk, ek, olc, katlar = d
    x, y = VRF_DIS_KONUM[mod]
    big = hp >= 12
    msp.add_blockref('MEK_VRF_DIS_L' if big else 'MEK_VRF_DIS_S', (x, y), dxfattribs={'layer': 'MEK-ELK-VRF-DIS'})
    w = 124 if big else 93
    tagbox(x - w/2, y + 42, mod, 'MEK-ELK-VRF-DIS', 8)
    text(x + w/2 - 52, y + 46, f'{hp} HP / {tr(qk,1)} kW', 6.5, 'MEK-ELK-ETIKET')
    text(x - w/2, y - 52, f'{tr(ek)} kW 400V 3N~', 6.5, 'MEK-ELK-GUC')

# ---------------------------------------------------------------- VRF iç üniteler
def room_lookup(kat, no):
    for r in ROOMS:
        if r['kat'] == kat and r['no'] == no:
            return r
    raise KeyError((kat, no))

def overlap(a, b):
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])

ic_list = []   # (kat, no, mahal, alan, kap, sistem, x, y)
for kat, no, ad, alan, kaps, sistem, ovr in VRF_ODALAR:
    r = room_lookup(kat, no)
    bx0, by0, bx1, by1 = ovr or r['bb']
    tx, ty = r['tag']
    tagz = (tx - 20, ty - 70, tx + 300, ty + 30)
    w, h = bx1 - bx0, by1 - by0
    cx, cy = (bx0 + bx1)/2, (by0 + by1)/2
    n = len(kaps)
    if n == 1:
        cands = [(cx, cy), (cx, cy + h/4), (cx, cy - h/4), (cx - w/4, cy), (cx + w/4, cy),
                 (cx, cy + h/3), (cx, cy - h/3)]
        base = [[c] for c in cands]
    else:
        if w >= h:
            base = [[(bx0 + w/4, cy + dy), (bx0 + 3*w/4, cy + dy)] for dy in (0, h/5, -h/5, h/3.2, -h/3.2)]
        else:
            base = [[(cx + dx, by0 + h/4), (cx + dx, by0 + 3*h/4)] for dx in (0, w/5, -w/5)]
    chosen = base[0]
    for opt in base:
        ok = True
        for (ux, uy) in opt:
            ub = (ux - 32, uy - 58, ux + 45, uy + 32)
            inside = ub[0] > bx0 + 5 and ub[2] < bx1 - 5 and ub[1] > by0 + 5 and ub[3] < by1 - 5
            if overlap(ub, tagz) or not inside:
                ok = False
        if ok:
            chosen = opt; break
    chosen = [(c[0], c[1], 'B') for c in chosen]
    if (kat, no) in VRF_POS:
        chosen = VRF_POS[(kat, no)]
    for kap, (ux, uy, side) in zip(kaps, chosen):
        tip, tipad, qh, ekw, olc = VRF_TIP[kap]
        msp.add_blockref('MEK_VRF_KASET_840' if kap >= 7 else 'MEK_VRF_KASET_570', (ux, uy), dxfattribs={'layer': 'MEK-ELK-VRF-IC'})
        if side == 'R':
            text(ux + 33, uy + 12, f'{sistem} {tip}', 6.5, 'MEK-ELK-ETIKET')
            text(ux + 33, uy + 1, f'{tr(kap,1)} kW soğ.', 6.5, 'MEK-ELK-ETIKET')
            text(ux + 33, uy - 10, f'{tr(ekw)} kW 230V 1~', 6.5, 'MEK-ELK-GUC')
        else:
            text(ux - 28.5, uy + 33, f'{sistem} {tip}', 6.5, 'MEK-ELK-ETIKET')
            text(ux - 28.5, uy - 39, f'{tr(kap,1)} kW soğ.', 6.5, 'MEK-ELK-ETIKET')
            text(ux - 28.5, uy - 49, f'{tr(ekw)} kW 230V 1~', 6.5, 'MEK-ELK-GUC')
        ic_list.append((kat, no, ad, alan, kap, sistem, ux, uy))

# ---------------------------------------------------------------- tablolar
def table(x, y, cols, rows, rh, th, title=None, title_h=None, header_rows=1, bold_rows=()):
    """cols: [(başlık, genişlik, hizalama 'L'/'C'/'R')]; rows: liste; (x,y) sol-üst."""
    W = sum(c[1] for c in cols)
    cur = y
    if title:
        th2 = title_h or th*1.4
        msp.add_lwpolyline([(x, cur), (x+W, cur), (x+W, cur-rh*1.5), (x, cur-rh*1.5)], close=True, dxfattribs={'layer': 'MEK-ELK-TABLO-CIZGI'})
        text(x + W/2, cur - rh*0.75, title, th2, 'MEK-ELK-TABLO', TextEntityAlignment.MIDDLE_CENTER)
        cur -= rh*1.5
    allrows = [[c[0] for c in cols]] + rows
    top = cur
    for i, row in enumerate(allrows):
        y0 = cur - rh
        cx = x
        hdr = i < header_rows
        for (cname, cw, al), val in zip(cols, row):
            s = '' if val is None else str(val)
            if s:
                if al == 'L' and not hdr:
                    text(cx + 4, y0 + rh/2, s, th, 'MEK-ELK-TABLO', TextEntityAlignment.MIDDLE_LEFT)
                elif al == 'R' and not hdr:
                    text(cx + cw - 4, y0 + rh/2, s, th, 'MEK-ELK-TABLO', TextEntityAlignment.MIDDLE_RIGHT)
                else:
                    text(cx + cw/2, y0 + rh/2, s, th*(0.9 if hdr else 1), 'MEK-ELK-TABLO', TextEntityAlignment.MIDDLE_CENTER)
            cx += cw
        msp.add_line((x, y0), (x+W, y0), dxfattribs={'layer': 'MEK-ELK-TABLO-CIZGI'})
        if hdr or (i in bold_rows):
            msp.add_line((x, y0+1.2), (x+W, y0+1.2), dxfattribs={'layer': 'MEK-ELK-TABLO-CIZGI'})
        cur = y0
    # dikey çizgiler + dış çerçeve
    cx = x
    for c in cols:
        msp.add_line((cx, top), (cx, cur), dxfattribs={'layer': 'MEK-ELK-TABLO-CIZGI'}); cx += c[1]
    msp.add_line((x+W, top), (x+W, cur), dxfattribs={'layer': 'MEK-ELK-TABLO-CIZGI'})
    msp.add_line((x, top), (x+W, top), dxfattribs={'layer': 'MEK-ELK-TABLO-CIZGI'})
    return cur

def faz_s(v, faz):
    return '-' if faz == 0 else ('230V 1~' if faz == 1 else '400V 3~')

# --- satır verileri
rows_all = []
def add_row(kod, sist, ad, mah, kat, adet, cal, kw, gerilim, pano):
    rows_all.append(dict(kod=kod, sist=sist, ad=ad, mah=mah, kat=kat, adet=adet, cal=cal, kw=kw, ger=gerilim, pano=pano))

for e in EKIPMAN:
    kod, sist, ad, oz, mah, kat, adet, cal, kw, v, faz, cos, pano, sym, pos, src = e
    add_row(kod, sist, f'{ad} - {oz}', mah, kat, adet, cal, kw, faz_s(v, faz), pano)
for d in VRF_DIS:
    sistem, mod, hp, qk, ek, olc, katlar = d
    add_row(mod, 'KLİMA (VRF)', f'VRF Dış Ünite {hp} HP, {tr(qk,1)} kW soğutma, tam DC inverter ({katlar})', 'BAHÇE - BETON KAİDE', 'Z', 1, 1, ek, '400V 3N~', 'VRF-P')
from collections import OrderedDict
grp = OrderedDict()
for kat, no, ad, alan, kap, sistem, ux, uy in ic_list:
    k = (kat, sistem, kap)
    grp[k] = grp.get(k, 0) + 1
for (kat, sistem, kap), n in grp.items():
    tip, tipad, qh, ekw, olc = VRF_TIP[kap]
    add_row(tip, 'KLİMA (VRF)', f'{sistem} İç Ünite, {tipad}, {tr(kap,1)} kW soğ. / {tr(qh,1)} kW ısıtma', f'{KAT_AD[kat]} ofis/çalışma mahalleri', kat, n, n, ekw, '230V 1~', f'{kat}KTP')

# --- kat paftalarına mini tablolar
mini_cols = [('KOD', 95, 'C'), ('CİHAZ', 560, 'L'), ('MAHAL', 330, 'L'), ('ADET', 60, 'C'),
             ('BİRİM GÜÇ (kW)', 130, 'R'), ('KURULU GÜÇ (kW)', 135, 'R'), ('GERİLİM', 110, 'C')]
for kat in ('Z', '1', '2'):
    dx = KAT_DX[kat]
    rows = []
    tot = 0
    for r in rows_all:
        if r['kat'] != kat:
            continue
        short = r['ad'].split(' - ')[0]
        if r['kod'].startswith('TİP'):
            short = r['ad'].split(' soğ.')[0].replace('İç Ünite, Kaset Tip 4 Yöne Üflemeli,', 'İç Ünite - Kaset') + ' soğ.'
        if len(short) > 58:
            short = short[:56] + '…'
        mah = r['mah'][:32]
        kur = r['adet'] * r['kw']; tot += kur
        rows.append([r['kod'], short, mah, r['adet'], tr(r['kw']), tr(kur), r['ger']])
    rows.append(['', 'TOPLAM KURULU GÜÇ', '', '', '', tr(tot), ''])
    table((5650 if kat == 'Z' else 2440) + dx, 870, mini_cols, rows, 21, 8, title=f'{KAT_AD[kat]} MEKANİK EKİPMAN ELEKTRİK GÜÇLERİ', title_h=11, bold_rows=(len(rows),))

# --- 07 nolu pafta: kat çerçevesini kopyala
src_frame = None
for e in msp.query('INSERT'):
    if e.dxf.name == '*U4' and abs(e.dxf.insert.x - 2310) < 5:
        src_frame = e
DX7 = 26612.547 - 2309.806
fr = src_frame.copy(); msp.add_entity(fr); fr.translate(DX7, 0, 0)
for a in fr.attribs:
    if a.dxf.tag == 'PAFTA_ADI':
        a.dxf.text = 'MEKANİK ELK. GÜÇ TABLOSU'
    if a.dxf.tag == '00':
        a.dxf.text = '07'
X7 = 2309.806 + DX7  # 26612.5

# Tablo-1: tüm ekipman
cols1 = [('NO', 55, 'C'), ('KOD', 110, 'C'), ('SİSTEM', 230, 'L'), ('CİHAZ ADI / TEKNİK ÖZELLİK', 1480, 'L'),
         ('MAHAL', 520, 'L'), ('KAT', 120, 'C'), ('ADET', 70, 'C'), ('ÇALIŞAN', 95, 'C'), ('BİRİM GÜÇ (kW)', 165, 'R'),
         ('KURULU GÜÇ (kW)', 170, 'R'), ('TALEP GÜÇ (kW)', 165, 'R'), ('GERİLİM / FAZ', 190, 'C'), ('PANO', 120, 'C')]
order = ['ISITMA', 'SIHHİ TESİSAT', 'YAĞMUR SUYU', 'HAVALANDIRMA', 'KLİMA', 'KLİMA (VRF)']
rows1 = []; n = 0
sums = OrderedDict((s, [0, 0]) for s in order)
for s in order:
    for r in rows_all:
        if r['sist'] != s:
            continue
        n += 1
        kur = r['adet']*r['kw']; tal = r['cal']*r['kw']
        sums[s][0] += kur; sums[s][1] += tal
        ad = r['ad'] if len(r['ad']) <= 118 else r['ad'][:116] + '…'
        rows1.append([n, r['kod'], s, ad, r['mah'][:42], KAT_AD[r['kat']], r['adet'], r['cal'], tr(r['kw']), tr(kur), tr(tal), r['ger'], r['pano']])
nb = len(rows1)
for s, (k, t) in sums.items():
    rows1.append(['', '', s, f'{s} TOPLAMI', '', '', '', '', '', tr(k), tr(t), '', ''])
TK = sum(v[0] for v in sums.values()); TT = sum(v[1] for v in sums.values())
rows1.append(['', '', '', 'GENEL TOPLAM (MEKANİK)', '', '', '', '', '', tr(TK), tr(TT), '', ''])
yb = table(X7 + 180, 3560, cols1, rows1, 25, 9.5, title='MEKANİK EKİPMAN ELEKTRİK GÜÇ TABLOSU', title_h=16,
           bold_rows=(nb+1, len(rows1)))

# Tablo-2: VRF iç ünite seçim tablosu (mahal bazında)
cols2 = [('KAT', 110, 'C'), ('MAHAL NO', 95, 'C'), ('MAHAL ADI', 300, 'L'), ('ALAN (m²)', 110, 'R'), ('SOĞ. YÜKÜ (kW)', 130, 'R'),
         ('ÜNİTE TİPİ', 110, 'C'), ('ADET', 65, 'C'), ('SOĞ. KAP. (kW)', 140, 'R'), ('ISIT. KAP. (kW)', 140, 'R'),
         ('ELK. GÜCÜ (W)', 130, 'R'), ('SİSTEM', 100, 'C')]
rows2 = []
for kat, no, ad, alan, kaps, sistem, ovr in VRF_ODALAR:
    kap = kaps[0]; tip, tipad, qh, ekw, olc = VRF_TIP[kap]
    rows2.append([KAT_AD[kat], no, ad, tr(alan), tr(YUK[(kat, no)]), tip, len(kaps), tr(kap*len(kaps), 1), tr(qh*len(kaps), 1), int(round(ekw*1000*len(kaps))), sistem])
tq = sum(sum(r[4]) for r in VRF_ODALAR)
tn = sum(len(r[4]) for r in VRF_ODALAR)
tw = sum(VRF_TIP[r[4][0]][3]*1000*len(r[4]) for r in VRF_ODALAR)
rows2.append(['', '', 'TOPLAM', '', tr(sum(YUK.values()), 1), '', tn, tr(tq, 1), '', int(tw), ''])
y2top = yb - 90
yb2 = table(X7 + 180, y2top, cols2, rows2, 22, 8.5, title='SOĞUTMA YÜKÜ ÖZETİ VE VRF İÇ ÜNİTE SEÇİM TABLOSU (KASET TİP 4 YÖNE)', title_h=13, bold_rows=(len(rows2),))

# Tablo-3: VRF dış ünite seçim tablosu
cols3 = [('SİSTEM', 110, 'C'), ('MODÜL', 120, 'C'), ('KAPASİTE (HP)', 130, 'C'), ('SOĞUTMA (kW)', 140, 'R'),
         ('ELK. GÜCÜ (kW)', 150, 'R'), ('ÖLÇÜ WxDxH (mm)', 210, 'C'), ('HİZMET ETTİĞİ KATLAR', 260, 'L'), ('İÇ ÜNİTE TOPLAMI (kW)', 210, 'R'), ('KOMB. ORANI', 130, 'R')]
rows3 = []
for sis in ('VRF-1', 'VRF-2'):
    ic = sum(sum(r[4]) for r in VRF_ODALAR if r[5] == sis)
    dis = sum(d[3] for d in VRF_DIS if d[0] == sis)
    first = True
    for d in VRF_DIS:
        if d[0] != sis:
            continue
        rows3.append([sis if first else '', d[1], d[2], tr(d[3], 1), tr(d[4]), d[5], d[6], tr(ic, 1) if first else '', f'%{ic/dis*100:.0f}' if first else ''])
        first = False
rows3.append(['', 'TOPLAM', sum(d[2] for d in VRF_DIS), tr(sum(d[3] for d in VRF_DIS), 1), tr(sum(d[4] for d in VRF_DIS)), '', '', '', ''])
x3 = X7 + 180 + sum(c[1] for c in cols2) + 120
yb3 = table(x3, y2top, cols3, rows3, 24, 9, title='VRF DIŞ ÜNİTE SEÇİM TABLOSU', title_h=13, bold_rows=(len(rows3),))

# Sembol lejantı
ly = yb3 - 80
text(x3, ly, 'SEMBOL LEJANTI', 13, 'MEK-ELK-TABLO')
leg = [('MEK_VRF_KASET_570', 'VRF iç ünite - kaset tip 4 yöne üflemeli', 'MEK-ELK-VRF-IC'),
       ('MEK_VRF_DIS_L', 'VRF dış ünite (bahçe, beton kaide)', 'MEK-ELK-VRF-DIS'),
       ('MEK_KAZAN', 'Yoğuşmalı duvar tipi doğalgaz kazanı', 'MEK-ELK-ISITMA'),
       ('MEK_POMPA2', 'İkiz sirkülasyon pompası (1 asıl + 1 yedek)', 'MEK-ELK-ISITMA'),
       ('MEK_POMPA', 'Sirkülasyon pompası', 'MEK-ELK-SIHHI'),
       ('MEK_BOYLER', 'Serpantinli boyler', 'MEK-ELK-SIHHI'),
       ('MEK_HIDROFOR', 'Paket hidrofor (2 pompalı)', 'MEK-ELK-SIHHI'),
       ('MEK_DALGIC', 'Dalgıç pompa', 'MEK-ELK-SIHHI'),
       ('MEK_FAN', 'Kanal tipi aspiratör / fan', 'MEK-ELK-HVL'),
       ('MEK_DAVLUMBAZ', 'Davlumbaz aspiratörü', 'MEK-ELK-HVL'),
       ('MEK_SPLIT', 'Split klima iç ünite', 'MEK-ELK-KLIMA'),
       ('MEK_GAZ', 'Gaz kaçak dedektörü + selenoid vana', 'MEK-ELK-ISITMA'),
       ('MEK_PANEL', 'Kaskad kontrol paneli', 'MEK-ELK-ISITMA'),
       ('MEK_KUMANDA', 'VRF merkezi kumanda', 'MEK-ELK-KLIMA')]
yy = ly - 70
for i, (bn, s, lay) in enumerate(leg):
    col = i // 7; row = i % 7
    bx = x3 + 80 + col*720; by = yy - row*95
    msp.add_blockref(bn, (bx, by), dxfattribs={'layer': lay, 'xscale': 0.8 if 'DIS' in bn else 1, 'yscale': 0.8 if 'DIS' in bn else 1})
    text(bx + 90, by, s, 9, 'MEK-ELK-TABLO', TextEntityAlignment.MIDDLE_LEFT)
tagbox(x3 + 1440, yy - 10, 'P-1', 'MEK-ELK-ISITMA')
text(x3 + 1500, yy - 3, 'Cihaz kodu', 9, 'MEK-ELK-TABLO', TextEntityAlignment.MIDDLE_LEFT)
text(x3 + 1440, yy - 60, '0,20 kW 230V 1~', 6.5, 'MEK-ELK-GUC')
text(x3 + 1560, yy - 57, 'Elektrik gücü / gerilim', 9, 'MEK-ELK-TABLO', TextEntityAlignment.MIDDLE_LEFT)

# Notlar
notes = [
    'NOTLAR:',
    '1. Cihaz elektrik güçleri ön seçim değerleridir; satın alınan cihazların katalog elektrik tüketim değerleri esas alınacak, malzeme onayından sonra elektrik projesi revize edilecektir.',
    '2. Isıtma, boyler, sirkülasyon ve hidrofor değerleri TMO Mardin hesap dosyalarından (kazan-boru-pompa, boyler, sirkülasyon, temiz su depo-hidrofor, yağmur suyu) alınmıştır.',
    '3. VRF iç üniteleri mahal bazında soğutma yükü hesabına göre seçilmiştir (Mardin 38,5 °C KT / iç 24 °C; cam güneş+iletim, dış duvar, çatı, insan, aydınlatma, cihaz, infiltrasyon, %10 emniyet). Detay: Excel "Soğutma Yükü" sayfası.',
    '4. VRF dış üniteler üstten hava atışlı olacak, 10 cm beton kaide ve çelik kafes içinde bahçeye konulacaktır. Merkezi kumanda Z-04 Güvenlik-Danışma mahallindedir.',
    '5. Teshin merkezi fanları ex-proof olacak, gaz alarmı ile kazan ve selenoid vana enterlokajı yapılacaktır. Kanal tipi WC fanları aydınlatma/zaman rölesi ile çalışacaktır.',
    '6. Talep gücü: yedek (stand-by) cihazlar hariç çalışan cihaz adedi ile hesaplanmıştır. Pano kodları: MP=Mekanik Pano (Teshin Merkezi), VRF-P=VRF Dış Ünite Panosu, ZKTP/1KTP/2KTP=Kat Tali Panoları.',
]
ny = ly - 70 - 7*95 - 40
for i, s in enumerate(notes):
    text(x3, ny - i*24, s, 9 if i else 11, 'MEK-ELK-TABLO')

doc.saveas(OUT)
print('kurulu', round(TK, 2), 'talep', round(TT, 2), 'ic', tn, 'satir', len(rows_all))
json.dump(dict(ic=ic_list, rows=rows_all), open(OUT + '.json', 'w'), ensure_ascii=False)
