# -*- coding: utf-8 -*-
"""Mekanik ekipman elektrik güç tablosu (Excel, formüllü)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collections import OrderedDict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment
from data import *
from cooling import hesapli_odalar, hesapli_dis, geometri, yuk
VRF_ODALAR = hesapli_odalar()
VRF_DIS = hesapli_dis(VRF_ODALAR)
YUK = {(d['kat'], d['no']): yuk(d)[3] / 1000 for d in geometri()}

OUT = sys.argv[1]
wb = Workbook()
F = 'Arial'
fN = Font(name=F, size=9)
fB = Font(name=F, size=9, bold=True)
fIn = Font(name=F, size=9, color='0000FF')
fLink = Font(name=F, size=9, color='008000')
fT = Font(name=F, size=13, bold=True)
fH = Font(name=F, size=9, bold=True, color='FFFFFF')
hdrFill = PatternFill('solid', start_color='1F4E78')
subFill = PatternFill('solid', start_color='DDEBF7')
totFill = PatternFill('solid', start_color='FCE4D6')
inFill = PatternFill('solid', start_color='FFF2CC')
thin = Side(style='thin', color='808080')
BR = Border(left=thin, right=thin, top=thin, bottom=thin)
CEN = Alignment(horizontal='center', vertical='center', wrap_text=True)
LEFT = Alignment(horizontal='left', vertical='center', wrap_text=True)


def setw(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def header(ws, row, cols):
    for i, c in enumerate(cols, 1):
        cell = ws.cell(row=row, column=i, value=c)
        cell.font = fH; cell.fill = hdrFill; cell.alignment = CEN; cell.border = BR
    ws.row_dimensions[row].height = 36


def title(ws, text, sub, ncol):
    ws['A1'] = text; ws['A1'].font = fT
    ws['A2'] = sub; ws['A2'].font = Font(name=F, size=9, italic=True)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncol)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncol)


def style_row(ws, r, ncol, fill=None, bold=False):
    for c in range(1, ncol + 1):
        cell = ws.cell(row=r, column=c)
        cell.border = BR
        if cell.font is None or cell.font == Font() or cell.font.name != F:
            cell.font = fB if bold else fN
        elif bold:
            cell.font = Font(name=F, size=9, bold=True, color=cell.font.color)
        if fill:
            cell.fill = fill
        if cell.alignment.horizontal is None:
            cell.alignment = LEFT if isinstance(cell.value, str) and not str(cell.value).startswith('=') else CEN


PROJ = 'TMO MARDİN BAŞMÜDÜRLÜĞÜ HİZMET BİNASI — Mekanik Tesisat'

# =============================================================== Ünite Tipleri + Tablolar (lookup)
wsL = wb.active; wsL.title = 'Tablolar'
title(wsL, 'YARDIMCI TABLOLAR', 'VRF iç ünite tipleri (Edirne TMO VRF projesi tip tablosu ile aynı), sigorta ve kablo seçim tabloları', 8)
header(wsL, 4, ['Tip', 'Ünite Tipi', 'Soğutma Kap. (kW)', 'Isıtma Kap. (kW)', 'Elk. Gücü (W)', 'Boyut (mm)'])
tips = sorted(VRF_TIP.items())
for i, (kap, (tip, ad, qh, ekw, olc)) in enumerate(tips):
    r = 5 + i
    vals = [tip, ad, kap, qh, ekw * 1000, olc]
    for c, v in enumerate(vals, 1):
        wsL.cell(row=r, column=c, value=v).font = fIn if c in (3, 4, 5) else fN
    style_row(wsL, r, 6)
TIP_FIRST, TIP_LAST = 5, 5 + len(tips) - 1
TIPR = f'Tablolar!$A${TIP_FIRST}:$A${TIP_LAST}'

wsL['H4'] = 'Sigorta seçimi: In ≥ 1,25 × Ib (C eğrisi, min. 10 A)'; wsL['H4'].font = fB
header_row = 5
for c, h in enumerate(['Alt sınır (A)', 'Sigorta (A)', 'Kablo (mm², Cu)'], 8):
    cell = wsL.cell(row=header_row, column=c, value=h); cell.font = fH; cell.fill = hdrFill; cell.alignment = CEN; cell.border = BR
brk = [(0, 10, '2,5'), (10, 16, '2,5'), (16, 20, '2,5'), (20, 25, '4'), (25, 32, '6'), (32, 40, '10'), (40, 50, '10'), (50, 63, '16'), (63, 80, '25')]
for i, (lo, b, k) in enumerate(brk):
    r = 6 + i
    wsL.cell(row=r, column=8, value=lo).font = fIn
    wsL.cell(row=r, column=9, value=b).font = fIn
    wsL.cell(row=r, column=10, value=k).font = fIn
    for c in (8, 9, 10):
        wsL.cell(row=r, column=c).border = BR; wsL.cell(row=r, column=c).alignment = CEN
BRK_LO = f'Tablolar!$H$6:$H${5 + len(brk)}'
BRK_A = f'Tablolar!$I$6:$I${5 + len(brk)}'
BRK_K = f'Tablolar!$J$6:$J${5 + len(brk)}'
wsL['H17'] = 'Not: Kablo kesitleri ön değerdir; gerilim düşümü ve döşeme koşullarına göre elektrik projesinde kesinleştirilecektir.'
wsL['H17'].font = Font(name=F, size=8, italic=True)
setw(wsL, [10, 28, 14, 14, 13, 14, 3, 13, 12, 14])

# =============================================================== Soğutma Yükü
from cooling import P as CP, YON, TIP as CTIP
wsS = wb.create_sheet('Soğutma Yükü')
title(wsS, 'OFİS VE ÇALIŞMA MAHALLERİ SOĞUTMA YÜKÜ HESABI', PROJ + ' — Ön proje, CLTD/CLF basitleştirilmiş yöntem (ASHRAE), mahal bazında pik yük', 32)
prm = [('Dış tasarım sıcaklığı (KT) [°C]', CP['t_dis'], 'Mardin yaz %0,4 tasarım değeri (≈38,5 °C KT / 20,5 °C YT)'),
       ('İç tasarım sıcaklığı [°C]', CP['t_ic'], '%50 bağıl nem'),
       ('Cam U değeri [W/m²K]', CP['U_cam'], 'Low-e ısıcam'),
       ('Gölgeleme katsayısı SC [-]', CP['SC'], 'Low-e cam + iç perde/stor'),
       ('Cam soğutma yükü faktörü CLF [-]', CP['CLF_cam'], 'İç gölgelemeli, orta ağırlıkta yapı, pik saat'),
       ('Dış duvar U değeri [W/m²K]', CP['U_duvar'], 'TS 825 2. bölge'),
       ('Çatı arası tavan U değeri [W/m²K]', CP['U_cati'], 'Sadece 2. kat mahalleri'),
       ('Çatı eşdeğer sıcaklık farkı [K]', CP['dT_cati'], 'Havalandırmalı kiremit çatı arası'),
       ('Kat yüksekliği (cephe) [m]', CP['kat_h'], 'Kotlar: +1,20 / +5,20 / +9,20'),
       ('Net mahal yüksekliği [m]', CP['net_h'], 'Asma tavan altı'),
       ('İnfiltrasyon [1/h]', CP['n_inf'], ''),
       ('Aydınlatma yükü [W/m²]', CP['aydinlatma'], 'LED armatür'),
       ('Emniyet katsayısı [-]', CP['emniyet'], '')]
wsS['A4'] = 'TASARIM ŞARTLARI VE KATSAYILAR'; wsS['A4'].font = fB
PR = {}
for i, (a, v, n) in enumerate(prm):
    r = 5 + i
    wsS.cell(row=r, column=1, value=a).font = fN
    wsS.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
    c = wsS.cell(row=r, column=4, value=v); c.font = fIn; c.fill = inFill; c.border = BR
    wsS.cell(row=r, column=5, value=n).font = Font(name=F, size=8, italic=True)
    PR[a.split(' [')[0]] = f'$D${r}'
DT = f"({PR['Dış tasarım sıcaklığı (KT)']}-{PR['İç tasarım sıcaklığı']})"
# cephe tablosu
wsS['H4'] = 'CEPHE YÖNLERİ (kuzey oku planda sağ-alt, ≈ -53°)'; wsS['H4'].font = fB
for c, h in enumerate(['Plan cephesi', 'Yön', 'Azimut (°)', 'SHGF maks. (W/m²)', 'Duvar ΔTeş (K)'], 8):
    cell = wsS.cell(row=5, column=c, value=h); cell.font = fH; cell.fill = hdrFill; cell.alignment = CEN; cell.border = BR
YR = {}
plan_ad = {'ALT': 'Alt (giriş)', 'UST': 'Üst', 'SAG': 'Sağ', 'SOL': 'Sol'}
for i, s in enumerate(('ALT', 'UST', 'SAG', 'SOL')):
    r = 6 + i
    yon, az, shgf, dte = YON[s]
    for c, v in enumerate([plan_ad[s], yon, az, shgf, dte], 8):
        cell = wsS.cell(row=r, column=c, value=v); cell.border = BR; cell.alignment = CEN
        cell.font = fIn if c >= 10 else fN
    YR[s] = (f'$K${r}', f'$L${r}')
wsS.cell(row=11, column=8, value='SHGF: 37° K enlemi, Temmuz, saatlik maksimum güneş ısı kazancı faktörü; ΔTeş: orta ağırlıklı duvar CLTD (renk/enlem düzeltmeli).').font = Font(name=F, size=8, italic=True)
# mahal tipleri
wsS['O4'] = 'MAHAL TİPİ İÇ YÜKLERİ'; wsS['O4'].font = fB
for c, h in enumerate(['Mahal tipi', 'Kişi yoğ. (m²/kişi)', 'Sabit kişi', 'Duyulur (W/kişi)', 'Gizli (W/kişi)', 'Cihaz (W/m²)'], 15):
    cell = wsS.cell(row=5, column=c, value=h); cell.font = fH; cell.fill = hdrFill; cell.alignment = CEN; cell.border = BR
TR = {}
for i, (k, (dens, sabit, qs, ql, cih)) in enumerate(CTIP.items()):
    r = 6 + i
    for c, v in enumerate([k, dens, sabit, qs, ql, cih], 15):
        cell = wsS.cell(row=r, column=c, value=v); cell.border = BR; cell.alignment = CEN
        cell.font = fIn if c >= 16 else fN
TT1, TT2 = 6, 6 + len(CTIP) - 1
def tlook(col, r):
    return f'INDEX(${col}${TT1}:${col}${TT2},MATCH($D{r},$O${TT1}:$O${TT2},0))'

H0 = 18
colsS = ['Kat', 'Mahal No', 'Mahal Adı', 'Mahal Tipi', 'Alan (m²)', 'Kişi Sayısı',
         'Dış Duvar KD (m)', 'Cam KD (m²)', 'Dış Duvar GB (m)', 'Cam GB (m²)', 'Dış Duvar KB (m)', 'Cam KB (m²)', 'Dış Duvar GD (m)', 'Cam GD (m²)', 'Çatı Altı (1/0)', 'Pencereler',
         'Q Cam Güneş (W)', 'Q Cam İletim (W)', 'Q Dış Duvar (W)', 'Q Çatı (W)', 'Q İnsan Duyulur (W)', 'Q Aydınlatma (W)', 'Q Cihaz (W)', 'Q İnfiltrasyon (W)',
         'Toplam Duyulur (W)', 'Toplam Gizli (W)', 'TOPLAM SOĞUTMA YÜKÜ (kW) (emniyetli)', 'Birim Yük (W/m²)', 'SHR (-)']
header(wsS, H0, colsS)
G = {(d['kat'], d['no']): d for d in geometri()}
rS0 = H0 + 1
for i, (kat, no, ad, alan, kaps, sis, ovr) in enumerate(VRF_ODALAR):
    r = rS0 + i
    d = G[(kat, no)]; yuk(d)
    dens, sabit, qs, ql, cih = CTIP[d['tip']]
    vals = [KAT_AD[kat], no, ad, d['tip'], alan, d['kisi'],
            d['L_ALT'], d['Acam_ALT'], d['L_UST'], d['Acam_UST'], d['L_SAG'], d['Acam_SAG'], d['L_SOL'], d['Acam_SOL'], 1 if d['cati'] else 0,
            '; '.join(f"{YON[s][0]}: {d['pen_'+s]}" for s in ('ALT', 'UST', 'SAG', 'SOL') if d['pen_'+s]) or 'pencere yok (iç mahal)']
    for c, v in enumerate(vals, 1):
        cell = wsS.cell(row=r, column=c, value=v)
        cell.font = fIn if 5 <= c <= 15 else fN
    sh = lambda s: YR[s][0]; dt = lambda s: YR[s][1]
    wsS.cell(row=r, column=17, value=f"=(H{r}*{sh('ALT')}+J{r}*{sh('UST')}+L{r}*{sh('SAG')}+N{r}*{sh('SOL')})*{PR['Gölgeleme katsayısı SC']}*{PR['Cam soğutma yükü faktörü CLF']}")
    wsS.cell(row=r, column=18, value=f"=(H{r}+J{r}+L{r}+N{r})*{PR['Cam U değeri']}*{DT}")
    kh = PR['Kat yüksekliği (cephe)']
    wsS.cell(row=r, column=19, value=f"=(MAX(G{r}*{kh}-H{r},0)*{dt('ALT')}+MAX(I{r}*{kh}-J{r},0)*{dt('UST')}+MAX(K{r}*{kh}-L{r},0)*{dt('SAG')}+MAX(M{r}*{kh}-N{r},0)*{dt('SOL')})*{PR['Dış duvar U değeri']}")
    wsS.cell(row=r, column=20, value=f"=O{r}*E{r}*{PR['Çatı arası tavan U değeri']}*{PR['Çatı eşdeğer sıcaklık farkı']}")
    wsS.cell(row=r, column=21, value=f"=F{r}*{tlook('R', r)}")
    wsS.cell(row=r, column=22, value=f"=E{r}*{PR['Aydınlatma yükü']}")
    wsS.cell(row=r, column=23, value=f"=E{r}*{tlook('T', r)}")
    wsS.cell(row=r, column=24, value=f"=0.335*{PR['İnfiltrasyon']}*E{r}*{PR['Net mahal yüksekliği']}*{DT}")
    wsS.cell(row=r, column=25, value=f"=SUM(Q{r}:X{r})")
    wsS.cell(row=r, column=26, value=f"=F{r}*{tlook('S', r)}")
    wsS.cell(row=r, column=27, value=f"=(Y{r}+Z{r})*{PR['Emniyet katsayısı']}/1000")
    wsS.cell(row=r, column=28, value=f"=AA{r}*1000/E{r}")
    wsS.cell(row=r, column=29, value=f"=Y{r}/(Y{r}+Z{r})")
    style_row(wsS, r, 29)
    for c in range(17, 27):
        wsS.cell(row=r, column=c).number_format = '#,##0'
    wsS.cell(row=r, column=27).number_format = '0.00'; wsS.cell(row=r, column=27).font = fB
    wsS.cell(row=r, column=28).number_format = '0'
    wsS.cell(row=r, column=29).number_format = '0.00'
rS1 = rS0 + len(VRF_ODALAR) - 1
rst = rS1 + 1
wsS.cell(row=rst, column=3, value='TOPLAM')
wsS.cell(row=rst, column=5, value=f'=SUM(E{rS0}:E{rS1})')
wsS.cell(row=rst, column=6, value=f'=SUM(F{rS0}:F{rS1})')
for c in range(17, 28):
    L = get_column_letter(c)
    wsS.cell(row=rst, column=c, value=f'=SUM({L}{rS0}:{L}{rS1})')
wsS.cell(row=rst, column=28, value=f'=AA{rst}*1000/E{rst}')
style_row(wsS, rst, 29, totFill, True)
for c in range(17, 27):
    wsS.cell(row=rst, column=c).number_format = '#,##0'
wsS.cell(row=rst, column=27).number_format = '0.00'; wsS.cell(row=rst, column=28).number_format = '0'
nts = ['Yöntem: Q güneş = A·SHGF·SC·CLF ; Q iletim = U·A·ΔT ; Q duvar = U·A_net·ΔTeş ; Q insan = n·(qd+qg) ; Q infiltrasyon = 0,335·n·V·ΔT. Toplam = (duyulur + gizli) × emniyet.',
       'Mardin yaz havası kurudur (dış ≈ 8 g/kg < iç 24 °C %50 ≈ 9,3 g/kg); infiltrasyon gizli yükü ihmal edilmiştir.',
       'Dış duvar boyları ve pencere alanları TEMİZ_1.dxf planından (mahal sınırı, P3 160x320, AL1/AL5 140 genişlik şerit pencere — kat başına 3,50 m etkin cam yüksekliği) alınmıştır.',
       'Yük mahal bazında pik (eş zamansız) değerdir; dış ünite seçiminde iç ünite toplamı / dış ünite kombinasyon oranı %100-%115 alınmıştır.',
       'Mavi hücreler girdi olup değiştirildiğinde tüm yükler ve "VRF İç Üniteler" sayfasındaki kapasite kontrolü yeniden hesaplanır.']
for i, s in enumerate(nts):
    wsS.cell(row=rst + 2 + i, column=1, value=s).font = Font(name=F, size=8, italic=True)
wsS.freeze_panes = wsS.cell(row=H0 + 1, column=4)
setw(wsS, [10, 8, 20, 12, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 7, 34, 9, 9, 9, 8, 9, 9, 8, 9, 10, 9, 13, 9, 7])

# =============================================================== VRF İç Üniteler
wsI = wb.create_sheet('VRF İç Üniteler')
title(wsI, 'VRF İÇ ÜNİTE SEÇİM TABLOSU (KASET TİP 4 YÖNE ÜFLEMELİ)', PROJ + ' — Ofis ve çalışma mahalleri', 16)
colsI = ['Kat', 'Mahal No', 'Mahal Adı', 'Alan (m²)', 'Birim Soğ. Yükü (W/m²)', 'Hesaplanan Soğ. Yükü (kW)', 'Ünite Tipi', 'Adet',
         'Birim Soğ. Kap. (kW)', 'Toplam Soğ. Kap. (kW)', 'Kontrol', 'Toplam Isıt. Kap. (kW)', 'Birim Elk. (W)', 'Toplam Elk. (kW)', 'VRF Sistemi', 'Pano']
header(wsI, 4, colsI)
r0 = 5
for i, (kat, no, ad, alan, kaps, sis, ovr) in enumerate(VRF_ODALAR):
    r = r0 + i
    tip = VRF_TIP[kaps[0]][0]
    wsI.cell(row=r, column=1, value=KAT_AD[kat])
    wsI.cell(row=r, column=2, value=no)
    wsI.cell(row=r, column=3, value=ad)
    wsI.cell(row=r, column=4, value=alan).font = fIn
    wsI.cell(row=r, column=5, value=f"='Soğutma Yükü'!AB{rS0 + i}").font = fLink
    wsI.cell(row=r, column=6, value=f"='Soğutma Yükü'!AA{rS0 + i}").font = fLink
    wsI.cell(row=r, column=7, value=tip).font = fIn
    wsI.cell(row=r, column=8, value=len(kaps)).font = fIn
    wsI.cell(row=r, column=9, value=f'=INDEX(Tablolar!$C${TIP_FIRST}:$C${TIP_LAST},MATCH(G{r},{TIPR},0))')
    wsI.cell(row=r, column=10, value=f'=H{r}*I{r}')
    wsI.cell(row=r, column=11, value=f'=IF(J{r}>=F{r},"UYGUN","KAPASİTE ARTIR")')
    wsI.cell(row=r, column=12, value=f'=H{r}*INDEX(Tablolar!$D${TIP_FIRST}:$D${TIP_LAST},MATCH(G{r},{TIPR},0))')
    wsI.cell(row=r, column=13, value=f'=INDEX(Tablolar!$E${TIP_FIRST}:$E${TIP_LAST},MATCH(G{r},{TIPR},0))')
    wsI.cell(row=r, column=14, value=f'=H{r}*M{r}/1000')
    wsI.cell(row=r, column=15, value=sis)
    wsI.cell(row=r, column=16, value=f'{kat}KTP')
    style_row(wsI, r, 16)
    for c in (4, 6, 9, 10, 12):
        wsI.cell(row=r, column=c).number_format = '0.00'
    wsI.cell(row=r, column=14).number_format = '0.000'
rI1 = r0 + len(VRF_ODALAR) - 1
rt = rI1 + 1
wsI.cell(row=rt, column=3, value='TOPLAM')
wsI.cell(row=rt, column=4, value=f'=SUM(D{r0}:D{rI1})')
wsI.cell(row=rt, column=6, value=f'=SUM(F{r0}:F{rI1})')
wsI.cell(row=rt, column=8, value=f'=SUM(H{r0}:H{rI1})')
wsI.cell(row=rt, column=10, value=f'=SUM(J{r0}:J{rI1})')
wsI.cell(row=rt, column=12, value=f'=SUM(L{r0}:L{rI1})')
wsI.cell(row=rt, column=14, value=f'=SUM(N{r0}:N{rI1})')
style_row(wsI, rt, 16, totFill, True)
for c in (4, 6, 10, 12):
    wsI.cell(row=rt, column=c).number_format = '0.00'
wsI.cell(row=rt, column=14).number_format = '0.000'
wsI.cell(row=rt + 2, column=1, value='Soğutma yükü değerleri "Soğutma Yükü" sayfasındaki mahal bazında hesaptan bağlantılıdır (yeşil). Ünite tipi/adet mavi hücreleri değiştirilebilir; Kontrol sütunu kapasite yeterliliğini gösterir.').font = Font(name=F, size=8, italic=True)
wsI.cell(row=rt + 3, column=1, value='Kaynak: Mahal alanları TEMİZ_1.dxf mimari mahal etiketleri; ünite tip/kapasite/güç değerleri TMO Edirne Hizmet Binası VRF projesi iç ünite seçim tablosu.').font = Font(name=F, size=8, italic=True)
wsI.freeze_panes = 'D5'
setw(wsI, [11, 9, 22, 9, 11, 11, 9, 6, 10, 10, 14, 10, 9, 10, 9, 7])
I_KAT = f"'VRF İç Üniteler'!$A${r0}:$A${rI1}"
I_TIP = f"'VRF İç Üniteler'!$G${r0}:$G${rI1}"
I_ADET = f"'VRF İç Üniteler'!$H${r0}:$H${rI1}"
I_SIS = f"'VRF İç Üniteler'!$O${r0}:$O${rI1}"
I_KAP = f"'VRF İç Üniteler'!$J${r0}:$J${rI1}"

# =============================================================== VRF Dış Üniteler
wsD = wb.create_sheet('VRF Dış Üniteler')
title(wsD, 'VRF DIŞ ÜNİTE SEÇİM TABLOSU', PROJ + ' — Hava soğutmalı, tam DC inverter, üstten hava atışlı (bahçe, beton kaide)', 11)
header(wsD, 4, ['Sistem', 'Modül', 'Kapasite (HP)', 'Soğutma Kap. (kW)', 'Elk. Gücü (kW)', 'Gerilim', 'Ölçü WxDxH (mm)',
                'Hizmet Ettiği Katlar', 'Sistem İç Ünite Toplamı (kW)', 'Sistem Dış Ünite Toplamı (kW)', 'Kombinasyon Oranı'])
for i, (sis, mod, hp, qk, ek, olc, katlar) in enumerate(VRF_DIS):
    r = 5 + i
    vals = [sis, mod, hp, qk, ek, '400V 3N~ 50Hz', olc, katlar]
    for c, v in enumerate(vals, 1):
        wsD.cell(row=r, column=c, value=v).font = fIn if c in (3, 4, 5) else fN
    wsD.cell(row=r, column=9, value=f'=SUMIF({I_SIS},A{r},{I_KAP})')
    wsD.cell(row=r, column=10, value=f'=SUMIF($A$5:$A${4 + len(VRF_DIS)},A{r},$D$5:$D${4 + len(VRF_DIS)})')
    wsD.cell(row=r, column=11, value=f'=IF(J{r}=0,0,I{r}/J{r})')
    style_row(wsD, r, 11)
    wsD.cell(row=r, column=11).number_format = '0%'
    for c in (4, 5, 9, 10):
        wsD.cell(row=r, column=c).number_format = '0.00'
rD1 = 4 + len(VRF_DIS); rdt = rD1 + 1
wsD.cell(row=rdt, column=2, value='TOPLAM')
wsD.cell(row=rdt, column=3, value=f'=SUM(C5:C{rD1})')
wsD.cell(row=rdt, column=4, value=f'=SUM(D5:D{rD1})')
wsD.cell(row=rdt, column=5, value=f'=SUM(E5:E{rD1})')
style_row(wsD, rdt, 11, totFill, True)
for c in (4, 5):
    wsD.cell(row=rdt, column=c).number_format = '0.00'
notesD = ['Kombinasyon oranı (iç ünite toplamı / dış ünite toplamı) %50-%130 aralığında olmalıdır; Mardin yüksek dış sıcaklığı nedeniyle %110 altı tercih edilmiştir.',
          'Elektrik güçleri TMO Edirne VRF projesi dış ünite tablosundaki oran ile (≈0,42 kW elektrik / kW soğutma; 12 HP: 13,80 kW) alınmıştır; seçilen markanın katalog değeri esas alınacaktır.',
          'Dış üniteler 10 cm beton kaide üzerine, çelik kafes içinde, kuzey cephe bahçesine konulacaktır. Merkezi kumanda Z-04 Güvenlik-Danışma mahallindedir.']
for i, s in enumerate(notesD):
    wsD.cell(row=rdt + 2 + i, column=1, value=s).font = Font(name=F, size=8, italic=True)
setw(wsD, [9, 9, 10, 11, 10, 14, 16, 20, 14, 14, 12])

# =============================================================== Ana tablo
ws = wb.create_sheet('Elektrik Güç Tablosu', 0)
NC = 21
title(ws, 'MEKANİK EKİPMAN ELEKTRİK GÜÇ TABLOSU', PROJ + ' — Elektrik projesine esas cihaz güç, gerilim ve faz bilgileri', NC)
cols = ['No', 'Cihaz Kodu', 'Sistem', 'Cihaz Adı', 'Teknik Özellik', 'Mahal', 'Kat', 'Adet (Toplam)', 'Çalışan Adet',
        'Birim Güç (kW)', 'Kurulu Güç (kW)', 'Talep Güç (kW)', 'Gerilim (V)', 'Faz', 'cos φ', 'Birim Akım Ib (A)',
        'Önerilen Sigorta (A)', 'Önerilen Kablo (Cu)', 'Besleyen Pano', 'Plan Gösterimi', 'Kaynak / Not']
header(ws, 4, cols)
rows = []  # (kod, sist, ad, oz, mah, kat, adet, cal, kw/formula, V, faz, cos, pano, kaynak, kind, extra)
for e in EKIPMAN:
    kod, sist, ad, oz, mah, kat, adet, cal, kw, v, faz, cos, pano, sym, pos, src = e
    rows.append(dict(kod=kod, sist=sist, ad=ad, oz=oz, mah=mah, kat=KAT_AD[kat], adet=adet, cal=cal, kw=kw, v=v, faz=faz, cos=cos, pano=pano, src=src, plan=f'{KAT_AD[kat]} planı'))
for i, (sis, mod, hp, qk, ek, olc, katlar) in enumerate(VRF_DIS):
    rows.append(dict(kod=mod, sist='KLİMA (VRF)', ad=f'VRF Dış Ünite ({sis})', oz=f'{hp} HP, {qk} kW soğutma, tam DC inverter; {katlar}', mah='BAHÇE - BETON KAİDE (KUZEY)',
                     kat='ZEMİN KAT', adet=1, cal=1, kw=f"='VRF Dış Üniteler'!E{5 + i}", v=400, faz=3, cos=0.95, pano='VRF-P', src='VRF Dış Üniteler sayfası', plan='ZEMİN KAT planı', link=True))
grp = OrderedDict()
for kat, no, ad, alan, kaps, sis, ovr in VRF_ODALAR:
    k = (kat, sis, VRF_TIP[kaps[0]][0], kaps[0])
    grp[k] = 1
for (kat, sis, tip, kap) in grp:
    tipad = VRF_TIP[kap][1]
    rows.append(dict(kod=tip, sist='KLİMA (VRF)', ad=f'VRF İç Ünite ({sis})', oz=f'{tipad}, {kap} kW soğ. / {VRF_TIP[kap][2]} kW ısıtma',
                     mah=f'{KAT_AD[kat]} ofis/çalışma mahalleri', kat=KAT_AD[kat],
                     adet=f'=SUMIFS({I_ADET},{I_KAT},G{{r}},{I_TIP},B{{r}},{I_SIS},"{sis}")', cal=f'=H{{r}}',
                     kw=f'=INDEX(Tablolar!$E${TIP_FIRST}:$E${TIP_LAST},MATCH(B{{r}},{TIPR},0))/1000',
                     v=230, faz=1, cos=0.90, pano=f'{kat}KTP', src='VRF İç Üniteler sayfası (adet mahal listesinden)', plan=f'{KAT_AD[kat]} planı', link=True))

order = ['ISITMA', 'SIHHİ TESİSAT', 'YAĞMUR SUYU', 'HAVALANDIRMA', 'KLİMA', 'KLİMA (VRF)']
rows.sort(key=lambda d: order.index(d['sist']))
r = 5
first = r
for n, d in enumerate(rows, 1):
    def f(v):
        return v.replace('{r}', str(r)) if isinstance(v, str) else v
    ws.cell(row=r, column=1, value=n)
    ws.cell(row=r, column=2, value=d['kod'])
    ws.cell(row=r, column=3, value=d['sist'])
    ws.cell(row=r, column=4, value=d['ad'])
    ws.cell(row=r, column=5, value=d['oz'])
    ws.cell(row=r, column=6, value=d['mah'])
    ws.cell(row=r, column=7, value=d['kat'])
    c = ws.cell(row=r, column=8, value=f(d['adet'])); c.font = fLink if isinstance(d['adet'], str) else fIn
    c = ws.cell(row=r, column=9, value=f(d['cal'])); c.font = fN if isinstance(d['cal'], str) else fIn
    c = ws.cell(row=r, column=10, value=f(d['kw'])); c.font = fLink if isinstance(d['kw'], str) else fIn
    ws.cell(row=r, column=11, value=f'=H{r}*J{r}')
    ws.cell(row=r, column=12, value=f'=I{r}*J{r}')
    ws.cell(row=r, column=13, value=d['v'] if d['v'] else 0).font = fIn
    ws.cell(row=r, column=14, value=d['faz']).font = fIn
    ws.cell(row=r, column=15, value=d['cos']).font = fIn
    ws.cell(row=r, column=16, value=f'=IF(OR(J{r}=0,M{r}=0),0,IF(N{r}=3,J{r}*1000/(SQRT(3)*M{r}*O{r}),J{r}*1000/(M{r}*O{r})))')
    ws.cell(row=r, column=17, value=f'=IF(P{r}=0,"-",INDEX({BRK_A},MATCH(P{r}*1.25-0.001,{BRK_LO},1)))')
    ws.cell(row=r, column=18, value=f'=IF(P{r}=0,"-",IF(N{r}=3,"5x","3x")&INDEX({BRK_K},MATCH(P{r}*1.25-0.001,{BRK_LO},1))&" mm²")')
    ws.cell(row=r, column=19, value=d['pano'])
    ws.cell(row=r, column=20, value=d['plan'])
    ws.cell(row=r, column=21, value=d['src'])
    style_row(ws, r, NC)
    for cc in (10, 11, 12):
        ws.cell(row=r, column=cc).number_format = '0.00'
    ws.cell(row=r, column=15).number_format = '0.00'
    ws.cell(row=r, column=16).number_format = '0.00'
    r += 1
last = r - 1
# sistem toplamları
r += 1
ws.cell(row=r, column=3, value='SİSTEM BAZINDA TOPLAMLAR'); style_row(ws, r, NC, subFill, True); r += 1
sys_first = r
for s in order:
    ws.cell(row=r, column=3, value=s)
    ws.cell(row=r, column=8, value=f'=SUMIF($C${first}:$C${last},C{r},$H${first}:$H${last})')
    ws.cell(row=r, column=11, value=f'=SUMIF($C${first}:$C${last},C{r},$K${first}:$K${last})')
    ws.cell(row=r, column=12, value=f'=SUMIF($C${first}:$C${last},C{r},$L${first}:$L${last})')
    style_row(ws, r, NC)
    for cc in (11, 12):
        ws.cell(row=r, column=cc).number_format = '0.00'
    r += 1
ws.cell(row=r, column=3, value='GENEL TOPLAM (MEKANİK)')
ws.cell(row=r, column=8, value=f'=SUM(H{sys_first}:H{r-1})')
ws.cell(row=r, column=11, value=f'=SUM(K{sys_first}:K{r-1})')
ws.cell(row=r, column=12, value=f'=SUM(L{sys_first}:L{r-1})')
style_row(ws, r, NC, totFill, True)
for cc in (11, 12):
    ws.cell(row=r, column=cc).number_format = '0.00'
grand_row = r
r += 2
notes = [
    'LEJANT: Mavi yazı = değiştirilebilir girdi (adet, birim güç, gerilim, faz, cos φ) · Yeşil yazı = diğer sayfadan bağlantı · Siyah = formül.',
    'Kurulu Güç = Adet × Birim Güç · Talep Güç = Çalışan Adet × Birim Güç (yedek/stand-by cihazlar hariç).',
    'Birim akım: 1~ için Ib = P/(U·cosφ), 3~ için Ib = P/(√3·U·cosφ). Sigorta In ≥ 1,25·Ib (Tablolar sayfası); kablo kesitleri ön değerdir.',
    'Cihaz elektrik güçleri ön seçim değerleridir; satın alınan cihazların katalog değerleri esas alınacak, malzeme onayından sonra elektrik projesi revize edilecektir.',
    'Isıtma (2×80 kW kazan, P-1/P-2 pompa debi-basma), boyler (500 L, 60,7 kW), sirkülasyon (0,4 m³/h - 0,5 mSS), hidrofor (2×1,12 m³/h, 2,9/4,4 bar) ve yağmur suyu verileri TMO Mardin hesap dosyalarından alınmıştır.',
    'Pano kodları: MP = Mekanik Pano (Teshin Merkezi), VRF-P = VRF Dış Ünite Panosu, ZKTP / 1KTP / 2KTP = Zemin / 1. / 2. Kat Tali Panoları.',
]
for s in notes:
    ws.cell(row=r, column=1, value=s).font = Font(name=F, size=8, italic=True)
    r += 1
ws.freeze_panes = 'C5'
setw(ws, [5, 10, 14, 34, 46, 26, 11, 9, 9, 10, 10, 10, 9, 5, 7, 10, 10, 12, 9, 15, 32])
ws.auto_filter.ref = f'A4:U{last}'
ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.sheet_properties.pageSetUpPr.fitToPage = True; ws.page_setup.fitToHeight = 0
ws.cell(row=4, column=10).comment = Comment('Ön seçim değeri. VRF satırları diğer sayfalardan bağlantılıdır.', 'Mekanik')

# =============================================================== Pano / Kat özeti
wsP = wb.create_sheet('Pano ve Kat Özeti', 1)
title(wsP, 'PANO VE KAT BAZINDA MEKANİK YÜK ÖZETİ', PROJ, 6)
G = "'Elektrik Güç Tablosu'"
header(wsP, 4, ['Besleyen Pano', 'Açıklama', 'Cihaz Adedi', 'Kurulu Güç (kW)', 'Talep Güç (kW)', 'Pay (Talep)'])
panos = [('MP', 'Mekanik Pano - Teshin Merkezi (ısıtma, hidrofor, yağmur suyu, teshin fanları)'), ('VRF-P', 'VRF Dış Ünite Panosu (400V 3N~)'),
         ('ZKTP', 'Zemin Kat Tali Panosu'), ('1KTP', '1. Kat Tali Panosu'), ('2KTP', '2. Kat Tali Panosu')]
for i, (p, a) in enumerate(panos):
    rr = 5 + i
    wsP.cell(row=rr, column=1, value=p); wsP.cell(row=rr, column=2, value=a)
    wsP.cell(row=rr, column=3, value=f'=SUMIF({G}!$S${first}:$S${last},A{rr},{G}!$H${first}:$H${last})')
    wsP.cell(row=rr, column=4, value=f'=SUMIF({G}!$S${first}:$S${last},A{rr},{G}!$K${first}:$K${last})')
    wsP.cell(row=rr, column=5, value=f'=SUMIF({G}!$S${first}:$S${last},A{rr},{G}!$L${first}:$L${last})')
    wsP.cell(row=rr, column=6, value=f'=IF($E${5 + len(panos)}=0,0,E{rr}/$E${5 + len(panos)})')
    style_row(wsP, rr, 6)
    wsP.cell(row=rr, column=6).number_format = '0.0%'
    for cc in (4, 5):
        wsP.cell(row=rr, column=cc).number_format = '0.00'
rr = 5 + len(panos)
wsP.cell(row=rr, column=1, value='TOPLAM')
for cc, L in ((3, 'C'), (4, 'D'), (5, 'E')):
    wsP.cell(row=rr, column=cc, value=f'=SUM({L}5:{L}{rr-1})')
wsP.cell(row=rr, column=6, value=f'=SUM(F5:F{rr-1})')
style_row(wsP, rr, 6, totFill, True)
wsP.cell(row=rr, column=6).number_format = '0.0%'
for cc in (4, 5):
    wsP.cell(row=rr, column=cc).number_format = '0.00'
wsP.cell(row=rr + 1, column=1, value=f'Kontrol: genel toplam ile fark (0 olmalı)')
wsP.cell(row=rr + 1, column=4, value=f'=D{rr}-{G}!K{grand_row}')
wsP.cell(row=rr + 1, column=4).number_format = '0.00'
wsP.cell(row=rr + 1, column=1).font = Font(name=F, size=8, italic=True)

r2 = rr + 3
header(wsP, r2, ['Kat', 'Açıklama', 'Cihaz Adedi', 'Kurulu Güç (kW)', 'Talep Güç (kW)', 'Pay (Talep)'])
kats = [('ZEMİN KAT', 'Teshin merkezi, su deposu, bahçe (VRF dış üniteler dahil)'), ('1. KAT', 'Ofisler'), ('2. KAT', 'Yönetim, konferans, mescit')]
for i, (k, a) in enumerate(kats):
    q = r2 + 1 + i
    wsP.cell(row=q, column=1, value=k); wsP.cell(row=q, column=2, value=a)
    wsP.cell(row=q, column=3, value=f'=SUMIF({G}!$G${first}:$G${last},A{q},{G}!$H${first}:$H${last})')
    wsP.cell(row=q, column=4, value=f'=SUMIF({G}!$G${first}:$G${last},A{q},{G}!$K${first}:$K${last})')
    wsP.cell(row=q, column=5, value=f'=SUMIF({G}!$G${first}:$G${last},A{q},{G}!$L${first}:$L${last})')
    wsP.cell(row=q, column=6, value=f'=IF($E${r2 + 1 + len(kats)}=0,0,E{q}/$E${r2 + 1 + len(kats)})')
    style_row(wsP, q, 6)
    wsP.cell(row=q, column=6).number_format = '0.0%'
    for cc in (4, 5):
        wsP.cell(row=q, column=cc).number_format = '0.00'
q = r2 + 1 + len(kats)
wsP.cell(row=q, column=1, value='TOPLAM')
for cc, L in ((3, 'C'), (4, 'D'), (5, 'E')):
    wsP.cell(row=q, column=cc, value=f'=SUM({L}{r2+1}:{L}{q-1})')
wsP.cell(row=q, column=6, value=f'=SUM(F{r2+1}:F{q-1})')
style_row(wsP, q, 6, totFill, True)
wsP.cell(row=q, column=6).number_format = '0.0%'
for cc in (4, 5):
    wsP.cell(row=q, column=cc).number_format = '0.00'
setw(wsP, [13, 62, 11, 14, 14, 11])

wb.save(OUT)
print('ok', last, grand_row)
