# -*- coding: utf-8 -*-
"""Ofis/çalışma mahalleri soğutma yükü hesabı (ön proje - CLTD/CLF basitleştirilmiş yöntem)."""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import VRF_ODALAR, KAT_DX

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- Tasarım şartları ve katsayılar (Excel'de girdi hücreleri olarak da yer alır)
P = dict(
    t_dis=38.5, t_ic=24.0,              # °C  Mardin yaz dış KT (≈%0,4) / iç tasarım
    U_cam=1.8, SC=0.55, CLF_cam=0.70,   # Low-e çift cam + iç perde
    U_duvar=0.50, U_cati=0.40,          # W/m²K (TS 825 2. bölge sınırları içinde)
    kat_h=4.00, net_h=3.00,             # m  kat yüksekliği (cephe), asma tavan altı net yükseklik
    n_inf=0.5,                          # 1/h infiltrasyon
    aydinlatma=10.0,                    # W/m² LED
    emniyet=1.10,
    dT_cati=22.0,                       # K  çatı arası tavan eşdeğer sıcaklık farkı
)
# Cephe yönleri (kuzey oku: planda sağ-alt, ≈ -53°)
YON = {
    'ALT': ('KD', 37, 470, 10.0),   # (yön, azimut, SHGF max W/m², duvar ΔTeş K)
    'UST': ('GB', 217, 500, 17.0),
    'SAG': ('KB', 307, 520, 15.0),
    'SOL': ('GD', 127, 500, 13.0),
}
# Mahal tipi: (kişi yoğunluğu m²/kişi veya sabit kişi, duyulur W/kişi, gizli W/kişi, cihaz W/m²)
TIP = {
    'OFİS':        (10.0, None, 75, 55, 15.0),
    'MAKAM':       (None, 6,    75, 55, 15.0),
    'SEKRETERYA':  (None, 3,    75, 55, 20.0),
    'KONFERANS':   (2.0,  None, 70, 45, 8.0),
    'MESCİT':      (1.5,  None, 75, 55, 0.0),
    'YEMEKHANE':   (1.5,  None, 80, 80, 5.0),
    'ÇOCUK':       (4.0,  None, 65, 45, 8.0),
    'MİSAFİRHANE': (None, 2,    70, 45, 6.0),
    'DİNLENME':    (3.0,  None, 70, 45, 8.0),
    'GÜVENLİK':    (None, 2,    75, 55, 25.0),
}

def mahal_tipi(ad):
    if 'KONFERANS' in ad: return 'KONFERANS'
    if 'MESCİT' in ad: return 'MESCİT'
    if 'YEMEKHANE' in ad: return 'YEMEKHANE'
    if 'ÇOCUK' in ad: return 'ÇOCUK'
    if 'MİSAFİRHANE' in ad: return 'MİSAFİRHANE'
    if 'DİNLENME' in ad: return 'DİNLENME'
    if 'GÜVENLİK' in ad: return 'GÜVENLİK'
    if 'SEKRETERYA' in ad: return 'SEKRETERYA'
    if 'MÜDÜR' in ad or 'MÜŞAVİR' in ad or 'HUKUK' in ad: return 'MAKAM'
    return 'OFİS'

FAC = dict(ALT=1005, UST=2557, SOL=3357, SAG=6809)   # zemin kat iç yüz koordinatları

def geometri():
    rooms = json.load(open(os.path.join(HERE, 'veri', 'rooms.json')))
    wins = json.load(open(os.path.join(HERE, 'veri', 'windows.json')))
    res = []
    for kat, no, ad, alan, kaps, sis, ovr in VRF_ODALAR:
        r = next(x for x in rooms if x['kat'] == kat and x['no'] == no)
        dx = KAT_DX[kat]
        x0, y0, x1, y1 = ovr or r['bb']
        sides = {}
        if abs(y0 - FAC['ALT']) < 40: sides['ALT'] = (x0, x1)
        if abs(y1 - FAC['UST']) < 30: sides['UST'] = (x0, x1)
        if abs(x0 - (FAC['SOL'] + dx)) < 30: sides['SOL'] = (y0, y1)
        if abs(x1 - (FAC['SAG'] + dx)) < 30: sides['SAG'] = (y0, y1)
        d = dict(kat=kat, no=no, ad=ad, alan=alan, tip=mahal_tipi(ad), sis=sis)
        for s in YON:
            d[f'L_{s}'] = 0.0; d[f'Acam_{s}'] = 0.0; d[f'pen_{s}'] = ''
        for s, (a, b) in sides.items():
            d[f'L_{s}'] = round((b - a) / 100, 2)
            cams = []
            for w in wins:
                if s in ('ALT', 'UST'):
                    yf = FAC[s] + (-7 if s == 'ALT' else 25)
                    if abs(w['y'] - yf) > 90 or not (a - 20 <= w['x'] <= b + 20): continue
                else:
                    xf = FAC[s] + dx + (-5 if s == 'SOL' else 23)
                    if abs(w['x'] - xf) > 90 or not (a - 20 <= w['y'] <= b + 20): continue
                cams.append(w)
            d[f'Acam_{s}'] = round(sum(w['w'] * w['h'] for w in cams), 2)
            d[f'pen_{s}'] = ' + '.join(f"{w['tip']} {int(w['w']*100)}x{int(w['h']*100)}" for w in cams)
        d['cati'] = kat == '2'
        res.append(d)
    return res

def yuk(d, p=P):
    dT = p['t_dis'] - p['t_ic']
    q = {}
    q['cam_gunes'] = sum(d[f'Acam_{s}'] * YON[s][2] * p['SC'] * p['CLF_cam'] for s in YON)
    q['cam_iletim'] = sum(d[f'Acam_{s}'] * p['U_cam'] * dT for s in YON)
    q['duvar'] = sum(max(d[f'L_{s}'] * p['kat_h'] - d[f'Acam_{s}'], 0) * p['U_duvar'] * YON[s][3] for s in YON)
    q['cati'] = d['alan'] * p['U_cati'] * p['dT_cati'] if d['cati'] else 0
    dens, sabit, qs, ql, cih = TIP[d['tip']]
    kisi = sabit if sabit else max(2, math.ceil(d['alan'] / dens))
    d['kisi'] = kisi
    q['insan_d'] = kisi * qs
    q['insan_g'] = kisi * ql
    q['aydinlatma'] = d['alan'] * p['aydinlatma']
    q['cihaz'] = d['alan'] * cih
    q['infiltrasyon'] = 0.335 * p['n_inf'] * d['alan'] * p['net_h'] * dT
    duy = q['cam_gunes'] + q['cam_iletim'] + q['duvar'] + q['cati'] + q['insan_d'] + q['aydinlatma'] + q['cihaz'] + q['infiltrasyon']
    giz = q['insan_g']
    top = (duy + giz) * p['emniyet']
    return q, duy, giz, top

KAP = [2.2, 2.8, 3.6, 4.5, 5.6, 7.1]

def secim(q_kw, alan):
    """Kaset ünite seçimi: ≤5,6 kW tek ünite, üstü / >35 m² mahallerde eşit kapasiteli 2+ ünite."""
    n = max(math.ceil(q_kw / 5.6), 2 if alan > 35 else 1)
    k = next(c for c in KAP if c >= q_kw / n - 1e-9)
    return [k] * n

# VRF dış ünite modülleri: (HP, soğutma kW, elektrik kW, ölçü) — elektrik ≈ 0,42 x kapasite (Edirne TMO VRF tablosu oranı)
MODUL = [(8, 22.4, 9.40, '930x765x1690'), (10, 28.0, 11.25, '930x765x1690'), (12, 33.5, 13.80, '1240x765x1690'),
         (14, 40.0, 16.40, '1240x765x1690'), (16, 45.0, 18.90, '1240x765x1690'), (18, 50.0, 21.00, '1240x765x1690'),
         (20, 56.0, 23.50, '1240x765x1690')]

def dis_unite_sec(ic_kw):
    """İç ünite toplamına göre en küçük dış ünite kombinasyonu (oran %100-%115, en fazla 2 modül)."""
    import itertools
    best = None
    for n in (1, 2):
        for combo in itertools.combinations_with_replacement(MODUL, n):
            S = sum(m[1] for m in combo)
            r = ic_kw / S
            if 1.0 <= r <= 1.15:
                key = (S, n)
                if best is None or key < best[0]:
                    best = (key, combo)
    return list(best[1])

def hesapli_odalar():
    """VRF_ODALAR listesini soğutma yükü hesabına göre seçilen ünitelerle döndürür."""
    G = {(d['kat'], d['no']): d for d in geometri()}
    out = []
    for kat, no, ad, alan, kaps, sis, ovr in VRF_ODALAR:
        d = G[(kat, no)]
        q, duy, giz, top = yuk(d)
        out.append((kat, no, ad, alan, secim(top / 1000, alan), sis, ovr))
    return out

def hesapli_dis(odalar):
    res = []
    for sis, katlar in (('VRF-1', 'Zemin Kat + 1. Kat'), ('VRF-2', '2. Kat')):
        ic = sum(sum(o[4]) for o in odalar if o[5] == sis)
        for i, m in enumerate(sorted(dis_unite_sec(ic), key=lambda m: m[0])):
            res.append((sis, f'{sis}{chr(65+i)}', m[0], m[1], m[2], m[3], katlar))
    return res

if __name__ == '__main__':
    G = geometri()
    tot = 0
    for d in G:
        q, duy, giz, top = yuk(d)
        s = secim(top / 1000, d['alan'])
        tot += top
        cam = sum(d[f'Acam_{x}'] for x in YON)
        print(f"{d['kat']} {d['no']:5s} {d['ad'][:18]:18s} A={d['alan']:5.1f} cam={cam:5.1f} kişi={d['kisi']:2d} "
              f"güneş={q['cam_gunes']:5.0f} duvar={q['duvar']:4.0f} çatı={q['cati']:4.0f} TOP={top/1000:5.2f} kW ({top/d['alan']:3.0f} W/m²) -> {s}  "
              + ' '.join(f"{x}:{d['L_'+x]}/{d['Acam_'+x]}" for x in YON if d['L_'+x]))
    print('toplam', round(tot / 1000, 1))
    O = hesapli_odalar(); print(hesapli_dis(O)); print({s: sum(sum(o[4]) for o in O if o[5]==s) for s in ('VRF-1','VRF-2')})
    json.dump(G, open(os.path.join(HERE, 'veri', 'geo.json'), 'w'), ensure_ascii=False, indent=0)
