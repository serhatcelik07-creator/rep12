# -*- coding: utf-8 -*-
"""5.TMO_MARDİN_ISITMA_v11 (DWG -> JSON dökümü) ısıtma çizimini mimari altlık üzerine aktarır ve
pencere önündeki radyatörleri dolu duvar bölümlerine taşır (pencereler döşemeye kadar iniyor).

Kullanım:
  python3 build_isitma.py <isitma.json> <mimari_altlık.dxf> <windows.json> <çıktı.dxf> <rapor.json>
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezdxf, ezdxf.path
from ezdxf import bbox
from ezdxf.enums import TextEntityAlignment
from json2dxf import JsonToDxf

JS, BASE, WIN, OUT, REP = sys.argv[1:6]
DX, DY = 81.3837, 6817.7313            # ısıtma DWG -> mimari altlık ofseti
FLOORS = {0: 'ZEMİN KAT', 6000: '1. KAT', 12000: '2. KAT'}
FAC = dict(ALT=1005.0, UST=2557.0, SOL=3357.0, SAG=6809.0)   # zemin kat iç yüz koordinatları
NORMAL = dict(ALT=(0, -1), UST=(0, 1), SOL=(-1, 0), SAG=(1, 0))
RAD_LAYER = 'RAST-IST-RADYATÖR-DİNAMİK BLOK'

data = json.load(open(JS))
doc = ezdxf.readfile(BASE)
msp = doc.modelspace()

# ---------------------------------------------------------------- mimari duvar segmentleri (ışın izleme için)
segs = []
def addseg(e):
    t = e.dxftype()
    if t == 'LINE':
        segs.append((e.dxf.start.x, e.dxf.start.y, e.dxf.end.x, e.dxf.end.y))
    elif t in ('LWPOLYLINE', 'POLYLINE', 'ARC'):
        pts = [(p.x, p.y) for p in ezdxf.path.make_path(e).flattening(2)]
        segs.extend((a[0], a[1], b[0], b[1]) for a, b in zip(pts, pts[1:]))
doors = []
for e in msp:
    L = e.dxf.layer
    if e.dxftype() == 'INSERT':
        if 'DOOR' in L and 'IDEN' not in L:
            try:
                b = bbox.extents([e])
                if b.has_data and b.size.x < 400 and b.size.y < 400:
                    doors.append((b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y))
            except Exception:
                pass
        if any(k in L for k in ('GLAZ', 'ALUMINIUM', 'WINDOW', 'DOOR')):
            try:
                for v in e.virtual_entities():
                    addseg(v)
            except Exception:
                pass
        continue
    if any(k in L for k in ('WALL', 'GLAZ', 'VITRF', 'STRC', 'CERCEVE', 'SHAFT', 'ALUMINIUM', 'MYM_CAM', 'DOOR-FRAM')):
        addseg(e)

def ray(x, y, dx, dy, maxd=1500):
    best = maxd
    for x1, y1, x2, y2 in segs:
        if dx:
            if (y1 - y) * (y2 - y) > 0 or y1 == y2: continue
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1); d = (xi - x) * dx
        else:
            if (x1 - x) * (x2 - x) > 0 or x1 == x2: continue
            yi = y1 + (x - x1) * (y2 - y1) / (x2 - x1); d = (yi - y) * dy
        if 3 < d < best: best = d
    return best

# ---------------------------------------------------------------- pencereler
wins = json.load(open(WIN))
def floor_dx(x):
    return 12000 if x > 14000 else (6000 if x > 8000 else 0)
win_spans = []   # (cephe, floor_dx, a, b)
for w in wins:
    fd = floor_dx(w['x']); x = w['x'] - fd; y = w['y']
    half = w['w'] * 100 / 2
    if abs(y - FAC['ALT']) < 80: win_spans.append(('ALT', fd, w['x'] - half, w['x'] + half))
    elif abs(y - FAC['UST']) < 80: win_spans.append(('UST', fd, w['x'] - half, w['x'] + half))
    elif abs(x - FAC['SOL']) < 90: win_spans.append(('SOL', fd, y - half, y + half))
    elif abs(x - FAC['SAG']) < 90: win_spans.append(('SAG', fd, y - half, y + half))

# ---------------------------------------------------------------- ısıtma çizimini aktar
conv = JsonToDxf(data, doc, DX, DY, prefix='IS_')
def keep(e):
    L = e['layer']
    if L.startswith('Z_MİM'):
        return False
    if L == '0' and e['type'] in ('TEXT', 'MTEXT', 'DIMENSION'):
        return False
    return True
conv.add_entities(keep)

rads, tags, pexs = [], [], []
for h, (ent, js) in conv.map.items():
    L = js['layer']
    if js['type'] == 'INSERT' and L == RAD_LAYER:
        rads.append((h, ent, js))
    elif js['type'] == 'INSERT' and js['name'] == 'RADYATOR_TAG_MRD':
        tags.append((h, ent, js))
    elif js['type'] == 'LWPOLYLINE' and L in ('pex_boru_gidiş', 'pex_boru_dönüş'):
        pexs.append((h, ent, js))

def tagattrs(js):
    return {a.get('tag'): (a['text']['text'] if isinstance(a.get('text'), dict) else '') for a in js.get('attribs', [])}

# radyatör geometrisi
R = []
for h, ent, js in rads:
    b = bbox.extents([ent])
    if not b.has_data:
        continue
    x0, y0, x1, y1 = b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y
    R.append(dict(h=h, ent=ent, js=js, bb=[x0, y0, x1, y1], c=((x0 + x1) / 2, (y0 + y1) / 2),
                  horiz=(x1 - x0) >= (y1 - y0), L=max(x1 - x0, y1 - y0), t=min(x1 - x0, y1 - y0)))

def facade_of(r):
    x0, y0, x1, y1 = r['bb']; fd = floor_dx(r['c'][0])
    cands = []
    if r['horiz']:
        cands += [('ALT', abs(y0 - FAC['ALT'])), ('UST', abs(FAC['UST'] - y1))]
    else:
        cands += [('SOL', abs(x0 - (FAC['SOL'] + fd))), ('SAG', abs((FAC['SAG'] + fd) - x1))]
    f, d = min(cands, key=lambda t: t[1])
    return (f, d) if d < 60 else (None, d)

def overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))

def in_front_of_window(r):
    f, d = facade_of(r)
    if not f:
        return None
    fd = floor_dx(r['c'][0])
    a0, a1 = (r['bb'][0], r['bb'][2]) if f in ('ALT', 'UST') else (r['bb'][1], r['bb'][3])
    for wf, wfd, w0, w1 in win_spans:
        if wf == f and wfd == fd and overlap(a0, a1, w0, w1) > 10:
            return f
    return None

# en yakın etiket ve PE-X uçları
def nearest_tag(r):
    best, bd = None, 1e9
    for h, ent, js in tags:
        p = ent.dxf.insert; d = math.hypot(p.x - r['c'][0], p.y - r['c'][1])
        if d < bd:
            best, bd = (h, ent, js), d
    return best if bd < 250 else None

def pex_ends(r):
    x0, y0, x1, y1 = r['bb']; m = 30
    out = []
    for h, ent, js in pexs:
        pts = list(ent.get_points('xy'))
        for idx in (0, len(pts) - 1):
            px, py = pts[idx]
            if x0 - m <= px <= x1 + m and y0 - m <= py <= y1 + m:
                out.append((ent, idx))
    return out

# ---------------------------------------------------------------- yerleşim
occupied = []   # (x0,y0,x1,y1) yerleşmiş / sabit radyatörler
moving = []
for r in R:
    f = in_front_of_window(r)
    if f:
        r['fac'] = f; moving.append(r)
    else:
        occupied.append(r['bb'])

def near_window(box):
    x0, y0, x1, y1 = box
    fd = floor_dx((x0 + x1) / 2)
    for wf, wfd, w0, w1 in win_spans:
        if wfd != fd:
            continue
        if wf == 'ALT' and y0 < FAC['ALT'] + 70 and overlap(x0, x1, w0 - 5, w1 + 5) > 0: return True
        if wf == 'UST' and y1 > FAC['UST'] - 70 and overlap(x0, x1, w0 - 5, w1 + 5) > 0: return True
        if wf == 'SOL' and x0 < FAC['SOL'] + fd + 70 and overlap(y0, y1, w0 - 5, w1 + 5) > 0: return True
        if wf == 'SAG' and x1 > FAC['SAG'] + fd - 70 and overlap(y0, y1, w0 - 5, w1 + 5) > 0: return True
    return False

def free(box, margin=8):
    x0, y0, x1, y1 = box
    if near_window(box):
        return False
    for o in occupied:
        if not (x1 + margin < o[0] or x0 - margin > o[2] or y1 + margin < o[1] or y0 - margin > o[3]):
            return False
    for d in doors:
        if not (x1 < d[0] - 5 or x0 > d[2] + 5 or y1 < d[1] - 5 or y0 > d[3] + 5):
            return False
    return True

def interval_free_of_windows(f, fd, a, b):
    for wf, wfd, w0, w1 in win_spans:
        if wf == f and wfd == fd and overlap(a, b, w0 - 5, w1 + 5) > 0:
            return False
    return True

# Otomatik yer bulunamayan dar WC holleri için elle konum: (eski merkez) -> (tür, duvar, yeni merkez)
MANUAL = {(11887, 2546): ('yan', 'SAG', 12005, 2490), (17892, 2546): ('yan', 'SAG', 18005, 2490),
          (18297, 2551): ('pier', 'UST', 18100, 2543)}

report = []
for r in sorted(moving, key=lambda r: (r['c'][0], r['c'][1])):
    f = r['fac']; fd = floor_dx(r['c'][0]); nx, ny = NORMAL[f]
    cx, cy = r['c']
    # oda iç sınırları (cepheden 60 cm içeriden ışın)
    px, py = cx - nx * 60, cy - ny * 60
    l, rr, d, u = ray(px, py, -1, 0), ray(px, py, 1, 0), ray(px, py, 0, -1), ray(px, py, 0, 1)
    room = (px - l, py - d, px + rr, py + u)
    g = 8.0   # duvar - radyatör arası boşluk
    Lr, t = r['L'], r['t']
    cands = []
    # (a) aynı cephede pencereler arası dolu duvar
    if f in ('ALT', 'UST'):
        face = FAC[f]
        a = room[0] + 15
        while a + Lr <= room[2] - 15:
            b = a + Lr
            if interval_free_of_windows(f, fd, a, b):
                yc = face + (g + t / 2) * (1 if f == 'ALT' else -1)
                box = (a, yc - t / 2, b, yc + t / 2)
                if free(box):
                    cands.append((abs((a + b) / 2 - cx), 'pier', f, ((a + b) / 2, yc), box))
            a += 5
    else:
        face = FAC[f] + fd
        a = room[1] + 15
        while a + Lr <= room[3] - 15:
            b = a + Lr
            if interval_free_of_windows(f, fd, a, b):
                xc = face + (g + t / 2) * (1 if f == 'SOL' else -1)
                box = (xc - t / 2, a, xc + t / 2, b)
                if free(box):
                    cands.append((abs((a + b) / 2 - cy), 'pier', f, (xc, (a + b) / 2), box))
            a += 5
    # (b) cepheye dik yan duvarlar (cephe köşesine yakın)
    side = []
    if f in ('ALT', 'UST'):
        sgn = 1 if f == 'ALT' else -1
        for wall, xf, nrm in (('SOL', room[0], (-1, 0)), ('SAG', room[2], (1, 0))):
            xc = xf + (g + t / 2) * (1 if wall == 'SOL' else -1)
            for off in range(25, 400, 10):
                s0 = FAC[f] + sgn * off; s1 = s0 + sgn * Lr
                box = (xc - t / 2, min(s0, s1), xc + t / 2, max(s0, s1))
                if box[1] < room[1] + 10 or box[3] > room[3] - 10:
                    break
                if free(box):
                    side.append((1000 + off + abs(xc - cx) * 0.2, 'yan', wall, (xc, (s0 + s1) / 2), box)); break
    else:
        sgn = 1 if f == 'SOL' else -1
        for wall, yf in (('ALT', room[1]), ('UST', room[3])):
            yc = yf + (g + t / 2) * (1 if wall == 'ALT' else -1)
            for off in range(25, 400, 10):
                s0 = FAC[f] + fd + sgn * off; s1 = s0 + sgn * Lr
                box = (min(s0, s1), yc - t / 2, max(s0, s1), yc + t / 2)
                if box[0] < room[0] + 10 or box[2] > room[2] - 10:
                    break
                if free(box):
                    side.append((1000 + off + abs(yc - cy) * 0.2, 'yan', wall, ((s0 + s1) / 2, yc), box)); break
    cands += side
    for (mx_, my_), (mkind, mwall, mcx, mcy) in MANUAL.items():   # elle verilen konumlar
        if abs(mx_ - cx) < 30 and abs(my_ - cy) < 30:
            if mwall in ('SOL', 'SAG') and f in ('ALT', 'UST') or mwall in ('ALT', 'UST') and f in ('SOL', 'SAG'):
                box = (mcx - t / 2, mcy - Lr / 2, mcx + t / 2, mcy + Lr / 2) if mwall in ('SOL', 'SAG') else (mcx - Lr / 2, mcy - t / 2, mcx + Lr / 2, mcy + t / 2)
            else:
                box = (mcx - Lr / 2, mcy - t / 2, mcx + Lr / 2, mcy + t / 2) if f in ('ALT', 'UST') else (mcx - t / 2, mcy - Lr / 2, mcx + t / 2, mcy + Lr / 2)
            cands = [(-1, mkind, mwall, (mcx, mcy), box)]
    if not cands:   # (c) karşı duvar (cephenin tersi)
        if f in ('ALT', 'UST'):
            back = room[3] if f == 'ALT' else room[1]
            yc = back + (g + t / 2) * (-1 if f == 'ALT' else 1)
            a = room[0] + 15
            while a + Lr <= room[2] - 15:
                box = (a, yc - t / 2, a + Lr, yc + t / 2)
                if free(box):
                    cands.append((2000 + abs(a + Lr / 2 - cx), 'yan', 'UST' if f == 'ALT' else 'ALT', (a + Lr / 2, yc), box)); break
                a += 5
        else:
            back = room[2] if f == 'SOL' else room[0]
            xc = back + (g + t / 2) * (-1 if f == 'SOL' else 1)
            a = room[1] + 15
            while a + Lr <= room[3] - 15:
                box = (xc - t / 2, a, xc + t / 2, a + Lr)
                if free(box):
                    cands.append((2000 + abs(a + Lr / 2 - cy), 'yan', 'SAG' if f == 'SOL' else 'SOL', (xc, a + Lr / 2), box)); break
                a += 5
    if not cands:
        report.append(dict(tag=None, durum='YER BULUNAMADI', c=r['c'])); occupied.append(r['bb']); continue
    cands.sort(key=lambda c: c[0])
    _, kind, wall, (ncx, ncy), box = cands[0]
    # yeni duvar normali
    nn = NORMAL[wall] if kind == 'yan' else NORMAL[f]
    delta = math.atan2(nn[1], nn[0]) - math.atan2(ny, nx)
    cd, sd = math.cos(delta), math.sin(delta)
    def T(p):
        qx, qy = p[0] - cx, p[1] - cy
        return (ncx + qx * cd - qy * sd, ncy + qx * sd + qy * cd)
    ent = r['ent']
    ins = ent.dxf.insert
    ent.dxf.insert = T((ins.x, ins.y))
    ent.dxf.rotation = (ent.dxf.rotation + math.degrees(delta)) % 360
    occupied.append(box)
    # etiket
    tg = nearest_tag(r); tinfo = {}
    if tg:
        th, tent, tjs = tg; tinfo = tagattrs(tjs)
        mx, my = ncx - cx, ncy - cy
        if kind == 'yan':   # etiketi radyatörün oda tarafına al
            mx += -nn[0] * (40 if nn[0] < 0 else 170)
            my += -nn[1] * (30 if nn[1] < 0 else 60)
        tent.dxf.insert = (tent.dxf.insert.x + mx, tent.dxf.insert.y + my)
        for te in conv.attr_map.get(th, []):
            te.translate(mx, my, 0)
    # PE-X boruları: ucu yeni bağlantı noktasına uzat (cephe boyunca + duvar boyunca)
    for pl, idx in pex_ends(r):
        pts = [tuple(p) for p in pl.get_points('xyseb')]
        ox, oy = pts[idx][0], pts[idx][1]
        nxp, nyp = T((ox, oy))
        mid = (nxp, oy) if f in ('ALT', 'UST') else (ox, nyp)
        add = [(mid[0], mid[1], 0, 0, 0), (nxp, nyp, 0, 0, 0)]
        if idx == 0:
            pts = list(reversed(add)) + pts
        else:
            pts = pts + add
        pl.set_points(pts, format='xyseb')
    report.append(dict(mahal=tinfo.get('MAHAL_NO'), radyator=tinfo.get('RADYATOR'), guc=tinfo.get('RAD_GUC'),
                       koll=tinfo.get('KOLL_NO'), kat=FLOORS[fd], cephe=f, yeni=('pencere arası duvar' if kind == 'pier' else f'yan duvar ({wall})'),
                       eski=[round(v) for v in r['c']], yeni_konum=[round(ncx), round(ncy)]))

# ---------------------------------------------------------------- pafta adları + revizyon notu
for e in msp.query('INSERT'):
    for a in e.attribs:
        if a.dxf.tag == 'PAFTA_ADI' and a.dxf.text in ('ZEMİN KAT PLANI', '1. KAT PLANI', '2. KAT PLANI'):
            a.dxf.text = a.dxf.text.replace('PLANI', 'ISITMA TESİSATI PLANI')
if 'ISIT-REV' not in doc.layers:
    doc.layers.add('ISIT-REV', color=1)
for fd, ad in FLOORS.items():
    t = msp.add_text(f'REV-1: Döşemeye kadar inen pencerelerin önündeki radyatörler pencere arası dolu duvarlara / yan duvarlara taşınmıştır.',
                     height=10, dxfattribs={'layer': 'ISIT-REV', 'style': 'Standard'})
    t.set_placement((2450 + fd, 960), align=TextEntityAlignment.LEFT)

doc.saveas(OUT)
json.dump(report, open(REP, 'w'), ensure_ascii=False, indent=1)
print('radyatör', len(R), 'taşınan', len([x for x in report if x.get('yeni')]), 'bulunamayan', len([x for x in report if x.get('durum')]))
