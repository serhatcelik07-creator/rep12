# -*- coding: utf-8 -*-
"""
Şanlıurfa HRS 1. Etap – Asansör / Sinyalizasyon / Elektrifikasyon bütçe çalışması.
Çıktı: URF_1Etap_Asansor_Sinyal_Elektrifikasyon_Butce_2026-10-06.xlsx (formüllü).

Kaynaklar:
  - URF_1Etap_{ASANSOR,SINYALIZASYON,KATENER,ELEKTRIK}_Teklif_Talebi.xlsx (29.09.2026 RFQ cetvelleri)
  - URF_1Etap_EM_Butce_Tahmini.xlsx (geçmiş teklif veritabanı, EUR Ağu-2026, HICP eskalasyonlu)
  - URF_HRS_1Etap_RFQ_Devir_Notu_2026-10-06.md (gelen teklifler, idare cevapları 05.10.2026)
"""
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = sys.argv[1] if len(sys.argv) > 1 else "URF_1Etap_MEP_Butce_2026-10-06.xlsx"

wb = Workbook()
F_H = Font(bold=True, color="FFFFFF")
FILL_H = PatternFill("solid", fgColor="1F4E78")
FILL_MAIN = PatternFill("solid", fgColor="DDEBF7")
FILL_IN = PatternFill("solid", fgColor="FFF2CC")      # değiştirilebilir giriş
FILL_CHG = PatternFill("solid", fgColor="FCE4D6")     # idare cevabıyla değişen miktar
FILL_TOT = PatternFill("solid", fgColor="C6E0B4")
BOLD = Font(bold=True)
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
EUR = '#,##0;[Red]-#,##0'
EUR2 = '#,##0.00'
QTY = '#,##0.##'
WRAP = Alignment(wrap_text=True, vertical="top")

# ---------------------------------------------------------------- Varsayımlar
V = wb.active
V.title = "Varsayimlar"
V["A1"] = "VARSAYIMLAR (sarı hücreler değiştirilebilir; tüm sayfalar formülle bağlıdır)"
V["A1"].font = Font(bold=True, size=12)
vrows = [
    ("Parametre", "Değer", "Kaynak / açıklama"),
    ("EUR/USD kuru", 1.1225, "ECB referans kuru, 02.10.2026 (eurofxref). Teklif günü kuru ile güncelleyin."),
    ("EUR/TRY kuru", 55.165, "ECB referans kuru, 02.10.2026 (eurofxref). Teklif günü kuru ile güncelleyin."),
    ("Hat uzunluğu – RFQ kabulü (km)", 6.56, "Katener şartnamesi; RFQ cetvellerinde kullanıldı"),
    ("Hat uzunluğu – idare cevabı (km)", 6.44, "İdare cevabı 05.10.2026, soru 18"),
    ("Hat boyu uzunluk düzeltme oranı", "=B6/B5", "Hat boyu iletken/kablo uzunluklarına uygulanır"),
    ("Araç sayısı – RFQ kabulü", 15, "Sinyal RFQ kabul 5"),
    ("Araç sayısı – idare cevabı", 14, "İdare cevabı soru 2 (araçlar ayrı ihale; arayüz yüklenicide)"),
    ("OG ring güzergahı – RFQ (m)", 7000, "Sıra 170 RFQ"),
    ("OG ring güzergahı – idare cevabı (m)", 7964, "İdare cevabı soru 21 (tüm kesitler)"),
    ("Galvanizli katener direği çeliği, imalat+galvaniz+dikim (EUR/kg)", 2.20, "Referans medyanı 1,80 €/kg (2013–2016 tramvay) + yerli üretim/montaj payı; Mitaş teklifi gelince güncelleyin"),
    ("Risk/belirsizlik payı – Asansör", 0.03, "2 firma teklifi var, kapsam net"),
    ("Risk/belirsizlik payı – Sinyalizasyon + AVLS", 0.10, "Ayrı sinyal projesi yok; miktarlar öngörü ağırlıklı; tek teklif (Point Link) aykırı"),
    ("Risk/belirsizlik payı – Katener", 0.05, "Proje var; fiyatlar referans + tahmin"),
    ("Risk/belirsizlik payı – Cer gücü / enerji temini", 0.05, "Proje var; teklif yok (Best Transformer, Alfanar bütçe bekleniyor)"),
    ("Risk/belirsizlik payı – Mekanik", 0.05, "Kalem bazlı; referans + tahmin; Ekura/Protek teklifleri bekleniyor"),
    ("Risk/belirsizlik payı – Elektrik AG / aydınlatma / yangın ihbar / topraklama", 0.05, "Kalem bazlı; referans kapsaması düşük"),
    ("Risk/belirsizlik payı – Kontrol ve haberleşme (SCADA, CCTV, telsiz, YBS, turnike)", 0.05, "Kalem bazlı; turnike adedi mimariden sayılacak"),
    ("Metraj payları geri alınsın mı? (1 = evet, 0 = RFQ metrajı)", 1, "RFQ'da bilinçli şişirme: uzunluklara %10 fire; Mekanik+Elektrik set alt kalemlerinde dağıtık malzemeye %30 (devir notu bölüm 10). Bütçe net metrajla hesaplanır."),
    ("Mitaş direk teklifine nakliye + işçilik (dikim) + overhead payı", 0.20, "Mitaş teklifi FCA Ankara, montaj hariç: ~850 km nakliye + boşaltma, vinçle dikim/şakül/tork, şantiye genel giderleri (teklif bedelinin %)"),
    ("Fiyat esası", "EUR, Ekim 2026, KDV hariç, Şanlıurfa şantiye teslim, montaj+test+devreye alma dahil (taşeron fiyatı)", ""),
]
for i, r in enumerate(vrows, start=3):
    for j, v in enumerate(r, start=1):
        c = V.cell(row=i, column=j, value=v)
        c.border = BOX
        if i == 3:
            c.font = F_H; c.fill = FILL_H
        elif j == 2 and i < 3 + len(vrows) - 1:
            c.fill = FILL_IN
V["B8"].number_format = "0.0000"
for a in ("B14", "B15", "B16", "B17", "B18", "B19", "B20", "B22"):
    V[a].number_format = "0%"
V.column_dimensions["A"].width = 58
V.column_dimensions["B"].width = 16
V.column_dimensions["C"].width = 95
P_USD, P_TRY, P_HAT, P_ARAC_RFQ, P_ARAC, P_RING_RFQ, P_RING, P_KG = (
    "Varsayimlar!$B$4", "Varsayimlar!$B$5", "Varsayimlar!$B$8", "Varsayimlar!$B$9",
    "Varsayimlar!$B$10", "Varsayimlar!$B$11", "Varsayimlar!$B$12", "Varsayimlar!$B$13")
P_PAY = "Varsayimlar!$B$21"
P_NAK = "Varsayimlar!$B$22"
RISK = {"MEKANIK": "Varsayimlar!$B$18", "ELK_AG": "Varsayimlar!$B$19", "HAB": "Varsayimlar!$B$20",
        "ASANSOR": "Varsayimlar!$B$14", "SINYAL": "Varsayimlar!$B$15",
        "KATENER": "Varsayimlar!$B$16", "CER": "Varsayimlar!$B$17"}

# ---------------------------------------------------------------- Teklifler
T = wb.create_sheet("Teklifler")
T["A1"] = "GELEN TEKLİFLER VE REFERANS KIYASLAR (06.10.2026 itibarıyla)"
T["A1"].font = Font(bold=True, size=12)
thdr = ["Disiplin", "Firma", "Kapsam / not", "Tutar (orijinal)", "Para birimi", "Tutar (EUR)",
        "Birim fiyat (EUR) 1000 kg", "Birim fiyat (EUR) 800 kg", "Değerlendirme"]
for j, h in enumerate(thdr, 1):
    c = T.cell(row=3, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
trows = [
    ("Asansör", "Schindler (Mert Can Oğlakkaya)",
     "12 × 37.000 USD (işçilik dahil) + 1 × 800 kg 36.000 USD; bakım hariç",
     480000, "USD", f"=D4/{P_USD}", f"=37000/{P_USD}", f"=36000/{P_USD}", "Şartnameye uygun kabul; bütçede kullanıldı"),
    ("Asansör", "TK Elevator (Betül Okay)",
     "12 × (24.000 malzeme + 8.000 işçilik) + 1 × 30.200; anti-vandal CAT-2",
     414200, "EUR", "=D5", 32000, 30200, "Şartnameye uygun kabul; bütçede kullanıldı"),
    ("Asansör", "Emlift (teklif no 2026/E025, 05.10.2026)",
     "12 × 1.500.000 TL + 1 × 1.500.000 TL; montaj dahil; teknik föyde antivandal/dış ortam yok, kapı 900×2000; kuyu aydınlatma ve topraklama hariç",
     19500000, "TRY", f"=D{{i}}/{P_TRY}", f"=1500000/{P_TRY}", f"=1500000/{P_TRY}", "Sapmalı (şartname dışı detaylar); medyana dahil"),
    ("Sinyalizasyon + AVLS", "Point Link / CASCO (Çin)",
     "Sıra 228–235; DAP şantiye; KDV ve gümrük hariç; AI asistan imzalı yanıt",
     7281784, "EUR", "=D6", None, None,
     "Referanslara göre ~2,3 kat yüksek; kalem dökümü alınmadan bütçeye esas alınmadı (üst sınır kıyası)"),
    ("Sinyalizasyon", "Referans – sistem bazlı (makas başı)",
     "İzmir tramvay H&K 64.862 €/makas, Eminönü Elektroline 46.638 €/makas; ort. 55.750 €/makas × 56",
     3121990, "EUR", "=D7", None, None, "EM_Butce_Tahmini Sistem sayfası (EUR Ağu-2026)"),
    ("Sinyalizasyon", "Referans – kalem bazlı (fiyatı bulunan 5/8 ana kalem)",
     "228, 229, 230, 231, 234 sıraları; 232, 233, 235 fiyatsız",
     1802246, "EUR", "=D8", None, None, "EM_Butce_Tahmini Ozet sayfası"),
    ("Katener", "Referans – sistem bazlı (hat-km başı)",
     "İzmir (Usluel, Siemens), Samsun (Usluel, BBR) ort. 356.767 €/km × 6,56 km",
     2340390, "EUR", "=D9", None, None, "EM_Butce_Tahmini Sistem sayfası"),
    ("Katener", "Referans – kalem bazlı (6/7 ana kalem)",
     "220 için konsol, iletken, gergi; 221 kısmi; direkler kg bazlı",
     2590010, "EUR", "=D10", None, None, "EM_Butce_Tahmini Ozet sayfası"),
    ("Cer gücü", "Referans – sistem bazlı (TM başı)",
     "İzmir Siemens, Bursa Haluk/MET, Kocaeli; ort. 672.038 €/TM × 5 (OG+trafo+redresör+DC; kablo hariç)",
     3360189, "EUR", "=D11", None, None, "EM_Butce_Tahmini Sistem sayfası"),
    ("AVLS (sıra 233–235)", "Mukan Rail (bütçesel, 06.10.2026)",
     "233: 15 araç × 21.300 = 319.500; 234 merkez 314.500; 235 tasarım 154.000; 180 gün geçerli; kabin/UPS/omurga, işletme SIM hariç",
     788000, "EUR", "=D", None, None, "Bütçeye işlendi (233 araç başı × 14 araç)"),
    ("Haberleşme", "Referans – kalem bazlı (fiyatı bulunan 54/86 ana kalem) + sistem bazlı ort. 1.121.764",
     "İletim, telefon, telsiz, anons, CCTV, saat, erişim, SCADA, YBS, turnike",
     1721471, "EUR", "=D13", None, None, "EM_Butce_Tahmini Ozet sayfası (kalem bazlı)"),
    ("Asansör", "Referans – kalem bazlı (metro/tramvay asansör referansları medyanı)",
     "1000 kg medyan 50.992 €, 800 kg 35.293 €",
     647200, "EUR", "=D12", 50992, 35293, "Metro referansları ağırlıklı; teklifler daha düşük"),
]
for i, r in enumerate(trows, start=4):
    for j, v in enumerate(r, 1):
        if j == 6:
            v = f'=D{i}/IF(E{i}="USD",{P_USD},IF(E{i}="TRY",{P_TRY},1))'
        c = T.cell(row=i, column=j, value=v); c.border = BOX; c.alignment = WRAP
        if j in (4, 6, 7, 8): c.number_format = EUR
T["A17"] = "Bekleyen / bütçe fiyatı istenen: Edoux, Adakon-Orona (asansör); Contirail/Mukan Rail (AVLS), Hanning & Kahl, Pintsch, INIT, Frauscher (sinyal); Mitaş, DeSA/Arthur Flury, Erbakır, Kambeton, La Farga, Galland, Revenga (katener); Best Transformer, Alfanar, Savronik, Alstom, Met-Eng, Tema (enerji)."
T["A17"].alignment = WRAP
T.merge_cells("A17:I17"); T.row_dimensions[17].height = 45
for col, w in zip("ABCDEFGHI", (18, 34, 60, 15, 10, 15, 14, 14, 48)):
    T.column_dimensions[col].width = w

# ---------------------------------------------------------------- Disiplin sayfaları
HDR = ["Sıra", "Poz", "Kalem / Alt kalem", "Birim", "Miktar (RFQ cetveli)", "Miktar (idare cevabına göre)",
       "Metraj payı geri alınan", "Net miktar (bütçe)", "Birim fiyat EUR (montaj dahil)", "Tutar EUR",
       "Fiyat türü", "Fiyat kaynağı / emsal (proje, firma, yıl, uyarlama)", "Not / düzeltme"]
WID = [7, 9, 62, 7, 12, 12, 11, 12, 13, 14, 17, 55, 40]
TUR = {"TEKLIF": ("2026 TEKLİF", PatternFill("solid", fgColor="C6EFCE")),
       "EMSAL": ("GEÇMİŞ TEKLİF UYARLAMA", PatternFill("solid", fgColor="DDEBF7")),
       "TAHMIN": ("MÜHENDİSLİK TAHMİNİ", PatternFill("solid", fgColor="FFE699")),
       "SIFIR": ("KAPSAM DIŞI (0)", PatternFill("solid", fgColor="EDEDED"))}
TYPE_TOT = {}
ITEM_COUNT = [0]
ROWMAP = {}


def fiyat_turu(kaynak, q):
    k = (kaynak or "").upper()
    if q == 0:
        return "SIFIR"
    if k.startswith("TEKL"):
        return "TEKLIF"
    if k.startswith("REF") or k.startswith("VARSAYIM"):
        return "EMSAL"
    return "TAHMIN"


import unicodedata
def _norm(t):
    t = (t or "").lower().replace("ı", "i")
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
DAGITIK = ["boru", "sprinkler", "kablo", "tava", "merdiven", "kanal", "linye", "iletken",   # devir notu bölüm 10
           "armatur", "projektor", "downlight", "acil aydinlatma", "priz", "dedektor", "kamera", "hoparlor",
           "ic unite", "suzgec", "menfez"]
HARIC = ["tasarim", "test", "devreye", "proje", "pano", "santral", "pompa", "kompresor", "trafo", "ups", "sunucu",
         "kazi", "dolgu", "beton", "kaplama", "egitim", "yazilim", "lisans"]
NO_PAY_SIRA = {"170", "171", "319", "320", "222", "223", "224", "225", "226"}


def pay_sinifi(kalem, birim, sira, mode):
    """RFQ'daki metraj payı: (etiket, bölen)."""
    if mode is None or sira in NO_PAY_SIRA:
        return "-", 1
    k, b = _norm(kalem), _norm(birim).strip()
    if any(h in k for h in HARIC):
        return ("fire %10", 1.10) if b == "m" and mode == "SK" else ("-", 1)
    dag = mode == "MEP" and any(d in k for d in DAGITIK)
    if b == "m":
        return ("fire+%30", 1.43) if dag else ("fire %10", 1.10)
    if dag and b in ("adet", "ad", "takim", "m2", "m²"):
        return ("%30", 1.30)
    return "-", 1


import csv as _csv, os as _os
REVIZE = {}
_rp = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "veri", "revize.csv")
if _os.path.exists(_rp):
    for _r in _csv.DictReader(open(_rp, encoding="utf-8")):
        REVIZE[(_r["sayfa"], str(_r["sira"]), _r["kalem"].strip())] = _r


TEKLIF_OVR = {}
_tp = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "veri", "teklif_override.csv")
if _os.path.exists(_tp):
    for _r in _csv.DictReader(open(_tp, encoding="utf-8")):
        TEKLIF_OVR[(_r["sayfa"], _r["poz"], _r["kalem"].strip())] = _r


def sheet(name, title, groups, mode=None):
    """groups: list of (sira, poz, baslik, items); item = (kalem, birim, q_rfq, q_corr, bf, kaynak, not)"""
    ws = wb.create_sheet(name)
    ws["A1"] = title; ws["A1"].font = Font(bold=True, size=13)
    ws["A2"] = ("EUR, KDV hariç, montaj+test+devreye alma dahil (taşeron fiyatı), Ekim 2026. "
                "Turuncu miktar: idare cevabıyla (05.10.2026) değişen kalem. Metraj payı: RFQ'daki bilinçli şişirmenin "
                "(%10 fire, dağıtık malzemede %30) bütçeden geri alınması. Fiyat türü renkleri: yeşil = 2026 firma teklifi; "
                "mavi = geçmiş tekliften uyarlama (ECB kuru + Euro Bölgesi HICP ile Ağu-2026'ya taşınmış, gerekirse montaj/boyut "
                "düzeltmeli); sarı = mühendislik tahmini (emsal yok); gri = idare cevabıyla kapsam dışı.")
    ws["A2"].alignment = WRAP; ws.merge_cells("A2:M2"); ws.row_dimensions[2].height = 48
    for j, h in enumerate(HDR, 1):
        c = ws.cell(row=4, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
    ws.row_dimensions[4].height = 42
    for j, w in enumerate(WID, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = "D5"
    ws.auto_filter.ref = "A4:M4"
    r = 5
    main_cells, rfq_terms = [], []
    for sira, poz, baslik, items in groups:
        mr = r
        for j, v in enumerate([sira, poz, baslik], 1):
            ws.cell(row=mr, column=j, value=v)
        for j in range(1, 14):
            ws.cell(row=mr, column=j).fill = FILL_MAIN; ws.cell(row=mr, column=j).font = BOLD
            ws.cell(row=mr, column=j).border = BOX
        r += 1
        first = r
        ITEM_COUNT[0] += len(items)
        for kalem, birim, q_rfq, q_corr, bf, kaynak, notu in items:
            tv = TEKLIF_OVR.get((name, poz, kalem.strip()))
            rv = None if tv else REVIZE.get((name, str(sira), kalem.strip()))
            if tv:
                if abs(float(tv["bf"]) - float(bf or 0)) > 0.005:
                    notu = (notu + " | " if notu else "") + f"Teklif öncesi BF {float(bf or 0):,.2f}"
                bf = float(tv["bf"]); kaynak = tv["kaynak"]
            if rv and rv["bf_yeni"] not in ("", None):
                if abs(float(rv["bf_yeni"]) - float(rv["bf_eski"] or 0)) > 0.005:
                    notu = (notu + " | " if notu else "") + f"İlk tahmin BF {float(rv['bf_eski']):,.2f}"
                bf = float(rv["bf_yeni"])
                kaynak = rv["kaynak_yeni"] + (f" – {rv['emsal_ozet']}" if rv["emsal_ozet"] else "") + \
                    (f" [Emsal ID: {rv['ref_idler']}]" if rv.get("ref_idler") else "")
            qc = q_rfq if q_corr is None else q_corr
            ROWMAP[(name, str(sira), kalem.strip())] = r
            etk, bol = pay_sinifi(kalem, birim, sira, mode)
            tur = fiyat_turu(kaynak, qc if isinstance(qc, (int, float)) else 1)
            vals = {2: poz, 3: kalem, 4: birim, 5: q_rfq, 6: qc, 7: etk,
                    8: f"=F{r}/IF({P_PAY}=1,{bol},1)" if bol != 1 else f"=F{r}",
                    9: bf, 10: f"=H{r}*I{r}", 11: TUR[tur][0], 12: kaynak, 13: notu}
            for j, v in vals.items():
                c = ws.cell(row=r, column=j, value=v); c.border = BOX
                if j in (3, 12, 13): c.alignment = WRAP
            for j in (5, 6, 8): ws.cell(row=r, column=j).number_format = QTY
            ws.cell(row=r, column=9).number_format = EUR2; ws.cell(row=r, column=9).fill = FILL_IN
            ws.cell(row=r, column=10).number_format = EUR
            ws.cell(row=r, column=11).fill = TUR[tur][1]
            if q_corr is not None and q_corr != q_rfq:
                ws.cell(row=r, column=6).fill = FILL_CHG
            ws.cell(row=r, column=1).border = BOX
            ws.row_dimensions[r].outlineLevel = 1
            r += 1
        last = r - 1
        ws.cell(row=mr, column=10, value=f"=SUM(J{first}:J{last})").number_format = EUR
        ws.cell(row=mr, column=8, value="RFQ tutarı →")
        ws.cell(row=mr, column=9, value=f"=SUMPRODUCT(E{first}:E{last},I{first}:I{last})").number_format = EUR
        main_cells.append(f"J{mr}"); rfq_terms.append(f"I{mr}")
    r += 1
    labels = [("TOPLAM (net metraj, idare cevaplarına göre)", "=" + "+".join(main_cells)),
              ("Karşılaştırma: RFQ cetvel miktarlarıyla (şişirmeli, düzeltmesiz) tutar", "=" + "+".join(rfq_terms)),
              ("Fark (metraj payları + idare cevapları)", f"=J{r}-J{r+1}")]
    for k, (lab, f) in enumerate(labels):
        ws.cell(row=r + k, column=3, value=lab).font = BOLD
        ws.cell(row=r + k, column=10, value=f).number_format = EUR
        for j in (3, 10):
            ws.cell(row=r + k, column=j).fill = FILL_TOT; ws.cell(row=r + k, column=j).border = BOX
    rt = r + 4
    ws.cell(row=rt, column=3, value="FİYAT TÜRÜNE GÖRE DAĞILIM").font = BOLD
    TYPE_TOT[name] = {}
    for k, key in enumerate(("TEKLIF", "EMSAL", "TAHMIN")):
        rr = rt + 1 + k
        ws.cell(row=rr, column=3, value=TUR[key][0]).fill = TUR[key][1]
        ws.cell(row=rr, column=10, value=f'=SUMIF($K$5:$K${last},"{TUR[key][0]}",$J$5:$J${last})').number_format = EUR
        ws.cell(row=rr, column=11, value=f"=IF($J${r}=0,0,J{rr}/$J${r})").number_format = "0%"
        TYPE_TOT[name][key] = f"'{name}'!$J${rr}"
    rr = rt + 4
    ws.cell(row=rr, column=3, value="İdare cevabıyla kapsam dışı kalan kalemlerin RFQ'daki değeri (bilgi)").fill = TUR["SIFIR"][1]
    ws.cell(row=rr, column=10, value=f'=SUMPRODUCT(($K$5:$K${last}="{TUR["SIFIR"][0]}")*$E$5:$E${last}*$I$5:$I${last})').number_format = EUR
    TYPE_TOT[name]["SIFIR"] = f"'{name}'!$J${rr}"
    # sayfa başı özet kutusu
    ws.sheet_properties.outlinePr.summaryBelow = False
    ws["A3"] = "DİSİPLİN TOPLAMI →"; ws["A3"].font = Font(bold=True, color="FFFFFF"); ws["A3"].fill = FILL_H
    ws.merge_cells("A3:B3")
    ws["C3"] = (f'="Kalem bazlı toplam: "&TEXT(J{r},"#,##0")&" €   |   2026 teklif: "&TEXT(K{rt+1},"0%")&'
                f'"   |   Geçmiş teklif uyarlaması: "&TEXT(K{rt+2},"0%")&"   |   Tahmin: "&TEXT(K{rt+3},"0%")&'
                f'"   |   Kalem kalem görmek için sol kenardaki [+] / [1][2] düğmelerini kullanın"')
    ws["C3"].font = Font(bold=True, color="1F4E78"); ws.merge_cells("C3:M3"); ws.row_dimensions[3].height = 22
    return ws, f"'{name}'!$J${r}", f"'{name}'!$J${r+1}", {g[0]: main_cells[i] for i, g in enumerate(groups)}


H = P_HAT          # hat boyu oranı
NA = P_ARAC        # araç sayısı (idare)

# ================================================================ ASANSÖR
avg1000 = "=MEDIAN(Teklifler!$G$4:$G$6)"
avg800 = "=MEDIAN(Teklifler!$H$4:$H$6)"
asansor = [
    ("364", "5010.A", "2 Duraklı 13 Kişilik Asansör (12 adet – 4 üst geçit × 3)", [
        ("Asansör 1000 kg, 2 durak, MRL dişlisiz, VVVF, 1 m/s, cam+paslanmaz kabin – S09 Hızmalı Köprüsü", "adet", 3, None, avg1000,
         "TEKLİF medyanı (Schindler, TK, Emlift)", "Bakım hariç; yeşil etiket, eğitim dahil"),
        ("Asansör 1000 kg – S10 Balıklıgöl", "adet", 3, None, avg1000, "TEKLİF medyanı", ""),
        ("Asansör 1000 kg – S11 Eyyüp Peygamber", "adet", 3, None, avg1000, "TEKLİF medyanı", ""),
        ("Asansör 1000 kg – S12 Rasathane", "adet", 3, None, avg1000, "TEKLİF medyanı", ""),
    ]),
    ("365", "5010.B", "2 Duraklı 10 Kişilik 800 kg Asansör (D01 idari bina)", [
        ("Asansör 800 kg, 2 durak (zemin/1. kat), MRL, VVVF, 1 m/s – D01", "adet", 1, None, avg800, "TEKLİF medyanı", ""),
    ]),
]
ws_as, AS_TOT, AS_RFQ, AS_MAIN = sheet("Asansor", "3 ASANSÖR – Sıra 364–365 (13 asansör)", asansor)

# ================================================================ SİNYALİZASYON + AVLS
sinyal = [
    ("228", "3001", "Sinyalizasyon Sistemi Tasarımı", [
        ("Tasarım paketi: simülasyon, mimari/kilitleme tabloları, uygulama ve kablo projeleri, RAMS/Safety Case (SIL3/SIL2), ISA, test prosedürleri, KET izin dosyası",
         "set", 1, None, 207246, "REF (4 ref; seçilen BF)", "İdare: sıra 228 yalnız tasarım; ekipman 229–232'den"),
    ]),
    ("229", "3001.A", "Hat Boyu Sinyalizasyon Sistemi", [
        ("Elektrikli makas motoru (IP67, iç kilitli, uç konum dedektörlü) – ana hat", "takım", 12, 16, 17785,
         "REF (CONTEC CSV24 / H&K HW61 / Elektroline TSH102: 15.255–19.316)", "İdare soru 3: ana hattaki tüm makaslar motorlu (+4, C4 kruvazmanı)"),
        ("Makas motoru tahrik/dedeksiyon çubukları + dil kilidi seti", "takım", 12, 16, 2969, "REF (Bombardier bars)", "Motor adedine bağlı"),
        ("Manuel makas hareket mekanizması (ana hat)", "takım", 4, 0, 5484, "REF", "İdare soru 3: manuel makas yok"),
        ("Manuel makas konum izleme kutusu (IO/RTU)", "adet", 1, 0, 3000, "TAHMİN", "Manuel makas kalmadı"),
        ("Lokal kontrol ve kumanda kabini SKP (SIL3, GRP IP54)", "adet", 3, 4, 88734,
         "REF (12 ref, medyan)", "C4 kruvazmanı motorlu olduğundan ilave kontrol birimi (temkinli kabul)"),
        ("Sorgulayıcı (interrogator) birimi – SKP içi", "adet", 4, 5, 6000, "TAHMİN", "SKP ile birlikte +1"),
        ("Alıcı endüktif lup (güzergah talep) – makas bölgeleri", "adet", 11, None, 2814, "REF (4 ref)", ""),
        ("Ray devresi / kütle dedektörü (makas kilitleme, bölge meşgul)", "adet", 34, None, 5614, "REF (4 ref)", ""),
        ("Ana hat makas sinyal lambası 3 ışıklı LED + talep alındı lambası", "takım", 11, None, 5173, "REF (3 ref)", ""),
        ("Sinyal lamba direği – makas bölgeleri", "adet", 11, None, 1200, "TAHMİN", ""),
        ("Lokal talep anahtarı – makas bölgeleri", "adet", 11, None, 800, "TAHMİN", ""),
        ("Karayolu kavşağı sinyalizasyon kontrol kabini TSP (tramvay öncelik)", "adet", 5, None, 8627, "REF (3 ref)", "Tramvay tarafı; kapsamda kalır"),
        ("Alıcı endüktif lup (ON/OFF öncelik talep) – kavşaklar", "adet", 24, None, 2814, "REF (makas lupu BF)", ""),
        ("Tramvay sinyal lambası 2 ışıklı LED – kavşaklar", "adet", 12, None, 3600, "TAHMİN (tek ref 7.268 aykırı)", ""),
        ("Tramvay sinyal direği – kavşaklar", "adet", 12, None, 1200, "TAHMİN", ""),
        ("Lokal kumanda anahtarı – kavşaklar", "adet", 12, None, 800, "TAHMİN", ""),
        ("Yaya geçidi tramvay uyarı seti (flaşör + levha)", "adet", 6, None, 2500, "TAHMİN", ""),
        ("Yaya geçidi uyarı kontrol kutusu + aktivasyon lupu", "takım", 3, None, 6000, "TAHMİN", ""),
        ("TSKP karayolu kavşak kontrol cihazı", "adet", 6, 0, 18000, "TAHMİN", "İdare soru 1: TSKP kapsam dışı"),
        ("Karayolu trafik lambası 300'lük başüstü", "adet", 20, 0, 900, "TAHMİN", "İdare soru 1: kapsam dışı"),
        ("Karayolu trafik lambası 200'lük direk tipi", "adet", 44, 0, 450, "TAHMİN", "İdare soru 1: kapsam dışı"),
        ("Yaya lambası + yaya butonu", "takım", 44, 0, 500, "TAHMİN", "İdare soru 1: kapsam dışı"),
        ("Trafik lambası direği 3,5 m / 6 m konsollu", "adet", 64, 0, 900, "TAHMİN", "İdare soru 1: kapsam dışı"),
        ("Karayolu trafik sinyal kabloları (TSKP–lambalar)", "m", 2695, 0, 6, "TAHMİN", "İdare soru 1: kapsam dışı"),
        ("Karayolu sinyal kablo borusu HDPE Ø63", "m", 1210, 0, 4, "TAHMİN", "İdare soru 1: kapsam dışı"),
        ("Lup besleme kablosu 2x2x1,0 ekranlı", "m", 5468, f"=5468*{H}", 4, "TAHMİN", "Hat boyu 6,44/6,56"),
        ("Lup kablosu (hat yatağı içi iletken + koruma kanalı)", "adet", 41, None, 400, "TAHMİN", ""),
        ("Ray devresi / dedektör kablosu 2x2x1,0", "m", 2673, f"=2673*{H}", 4, "TAHMİN", "Hat boyu oranı"),
        ("Makas motoru güç+kumanda kablosu 12x2,5", "m", 541, f"=ROUND(541*16/12,0)", 9, "TAHMİN", "+4 motor oranında"),
        ("Sinyal lambası kablosu 12x1,5", "m", 1348, f"=1348*{H}", 7, "TAHMİN", ""),
        ("Lokal kumanda anahtarı kablosu 7x1,5", "m", 1348, f"=1348*{H}", 4.5, "TAHMİN", ""),
        ("TSP/SKP–TSKP arayüz kablosu 19x1,5", "m", 198, None, 10, "TAHMİN", "İdare: irtibat kablolaması kapsamda"),
        ("Manuel makas konum kontağı kablosu 7x1,5", "m", 117, 0, 4.5, "TAHMİN", "Manuel makas yok"),
        ("Yaya geçidi flaş lamba kablosu 3x1,5", "m", 264, None, 2.5, "TAHMİN", ""),
        ("Kabin besleme kablosu NYY 3x6 (TM UPS panosundan)", "m", 5905, f"=5905*{H}", 4.5, "TAHMİN", ""),
        ("Kablo koruma borusu HDPE Ø50", "m", 2327, f"=2327*{H}", 3, "TAHMİN", ""),
        ("Kablo koruma borusu HDPE Ø110 (hat/yol altı)", "m", 605, None, 7, "TAHMİN", ""),
        ("Kabin ve sinyal direği temelleri", "adet", 100, None, 350, "TAHMİN", ""),
        ("Test, devreye alma, entegre test, 15 gün test işletmesi – hat boyu", "set", 1, None, 40669, "REF (5 ref)", ""),
    ]),
    ("230", "3001.B", "Depo Sahası ve Tesisleri Sinyalizasyon Sistemi", [
        ("Elektrikli makas motoru – depo (IP67, el kranklı, uç konum dedektörlü)", "takım", 20, 40, 12000,
         "REF (H&K HWE 14.713, CONTEC 15.090)", "İdare soru 4: depo makaslarının tamamı motorlu (+20)"),
        ("Makas motoru tahrik/dedeksiyon çubuk seti + dil kilidi – depo", "takım", 20, 40, 2969, "REF", "Motor adedine bağlı"),
        ("Manuel makas hareket mekanizması – depo", "takım", 20, 0, 5541, "REF (2 ref)", "İdare soru 4: manuel yok"),
        ("Depo sinyalizasyon kontrol ünitesi SKP (SIL2) + IO", "adet", 2, None, 80000,
         "TAHMİN (CONTEC TCS300 16 makas: 115.167 sistem)", "40 motor için I/O kapasitesi artırıldı"),
        ("Depo manuel güzergah talep paneli MSP", "adet", 4, None, 1604, "REF (2 ref)", ""),
        ("Depo sinyal lambası (makas pozisyon/kilit) + direği", "takım", 20, 40, 1500, "TAHMİN (CONTEC PPI 874 + direk)", "Her motorlu makasa 1"),
        ("Ray devresi / kütle dedektörü – depo", "adet", 24, 40, 3085, "REF (CONTEC)", "Her motorlu makas için kilitleme algılaması"),
        ("Makas motoru güç+kumanda kablosu 12x2,5 – depo", "m", 552, 1104, 9, "TAHMİN", "Motor sayısı ×2"),
        ("Manuel makas konum kontağı kablosu 7x1,5 – depo", "m", 959, 0, 4.5, "TAHMİN", "Manuel makas yok"),
        ("Depo sinyal lambası kablosu 12x1,5", "m", 992, 1984, 7, "TAHMİN", "Lamba sayısı ×2"),
        ("Ray devresi / dedektör kablosu 2x2x1,0 – depo", "m", 816, 1360, 4, "TAHMİN", "Dedektör 24→40"),
        ("MSP panel kablosu 24x1,5", "m", 176, None, 12, "TAHMİN", ""),
        ("SKP besleme kablosu NYY 3x6", "m", 563, None, 4.5, "TAHMİN", ""),
        ("SKP–TCC veri bağlantısı 6 core MM FO", "m", 662, None, 3.5, "TAHMİN", ""),
        ("Kablo koruma borusu HDPE Ø110 – depo ana güzergah", "m", 880, None, 7, "TAHMİN", ""),
        ("Kablo koruma borusu HDPE Ø50 – depo", "m", 1452, 2200, 3, "TAHMİN", "Cihaz sayısı artışı"),
        ("Kabin / sinyal direği / MSP temelleri", "adet", 27, 47, 350, "TAHMİN", "+20 lamba direği"),
        ("Depo güzergah/kilitleme yazılımı (15+ güzergah), test ve devreye alma", "set", 1, None, 70169, "REF (Elektroline EYAS)", ""),
    ]),
    ("231", "3001.C", "Araç Üstü Sinyalizasyon Sistemi", [
        ("Araç sinyalizasyon işletim paneli – her kabine 1", "adet", 30, f"=2*{NA}", 1500, "TAHMİN", "İdare soru 2: 14 araç"),
        ("Araç alıcı-verici (transponder) + alt şasi anteni – her uca 1", "adet", 30, f"=2*{NA}", 2500, "TAHMİN (H&K HCS-V 5.047/kabin)", "14 araç"),
        ("Araç üstü sinyalizasyon kontrol/kodlayıcı birimi (EN 50155)", "adet", 15, f"={NA}", 6000, "TAHMİN", "14 araç"),
        ("Anten kabloları, araç içi kablaj ve montaj aparatları", "set", 15, f"={NA}", 1500, "TAHMİN", "14 araç"),
        ("Araç arayüzü (hız/odometri, kabin aktif, kapı, TCMS/AVLS)", "set", 15, f"={NA}", 2000, "TAHMİN", "14 araç"),
        ("Araç tipi entegrasyon mühendisliği + ilk araç tip testi", "set", 1, None, 30000, "TAHMİN", "Araç ayrı ihale; arayüz yüklenicide"),
        ("Araç başına montaj + statik/dinamik test", "adet", 15, f"={NA}", 2411, "REF (H&K Konya)", "14 araç"),
    ]),
    ("232", "3001.D", "Sinyalizasyon Merkez Donanımı & Sistem Yazılımları", [
        ("Sinyalizasyon ana işlemcisi (sunucu) – sıcak yedekli", "adet", 2, None, 11925, "REF (3 ref)", ""),
        ("Sunucu konsolu KVM + 21\" LCD", "takım", 1, None, 2500, "TAHMİN", ""),
        ("19\" sinyalizasyon cihaz dolabı + PDU", "adet", 1, None, 4000, "TAHMİN", ""),
        ("Ana hat sinyalizasyon operatör iş istasyonu (2 monitör)", "takım", 2, None, 6000, "TAHMİN", ""),
        ("Depo sinyalizasyon operatör iş istasyonu", "takım", 1, None, 5000, "TAHMİN", ""),
        ("Sinyalizasyon LAN anahtarı (yedekli) + patch + çevirici", "takım", 2, None, 4000, "TAHMİN", ""),
        ("Sinyalizasyon özel yazılımı + lisanslar (ana uygulama, sinoptik, protokoller)", "set", 1, None, 150000, "TAHMİN", "Tramvay referansı yok (metro CBTC ref. 2,7–12 M€ kullanılmadı)"),
        ("Araç ve sinyalizasyon simülatör yazılımı + PC", "set", 1, None, 40000, "TAHMİN", ""),
        ("Arayüzler: AVLS, SCADA, NTP, YBS", "set", 1, None, 40000, "TAHMİN", ""),
        ("Sistem mühendisliği hizmetleri", "ay", 12, None, 9000, "TAHMİN", ""),
        ("Eğitim (10 kursiyer, 2 hafta) + dokümanlar", "set", 1, None, 15000, "TAHMİN (ref. 8.254–8.569/hafta)", ""),
        ("Bakım/arıza bulma yazılımı + dizüstü teşhis bilgisayarı", "set", 1, None, 8000, "TAHMİN", ""),
        ("Mevcut depo kontrol merkezi entegrasyonu – uyarlama ve lisans", "set", 1, 0, 60000, "TAHMİN", "İdare soru 17: mevcut sistem yok"),
    ]),
    ("233", "3002", "Araç Takip Sistemi (AVLS) – araç üstü ve saha", [
        ("AVLS araç üstü + saha (araç bilgisayarı, anten, 2 sürücü HMI, araç arayüzü, SIM, depo AP, lup aktarımı, kurulum/test) – araç başı",
         "araç", 15, f"={NA}", 21300, "TEKLİF (Mukan Rail, bütçesel 06.10.2026: 15 × 21.300)", "İdare soru 2: 14 araç"),
    ]),
    ("234", "3003", "Tramvay Araç Takip Sistemi Merkezi Donanımı ve Yazılımı", [
        ("AVLS merkez: yedekli sunucu, NAS, operatör PC, duvar monitörü, router/firewall, LAN, merkezi yazılım + lisans (172.500), belediye AVLS arayüzü, kurulum/test/eğitim",
         "set", 1, None, 314500, "TEKLİF (Mukan Rail)", "Ref. H&K İzmir 136.568; 19\" kabin/UPS/omurga hariç"),
    ]),
    ("235", "3004", "Araç Takip Sistemi Tasarımı", [
        ("AVLS tasarımı: mimari, konumlandırma, merkez ekranları, siber güvenlik, uygulama projeleri", "set", 1, None, 154000, "TEKLİF (Mukan Rail)", ""),
    ]),
]
ws_sn, SN_TOT, SN_RFQ, SN_MAIN = sheet("Sinyal", "4 SİNYALİZASYON VE ARAÇ TAKİP (AVLS) – Sıra 228–235", sinyal, "SK")

# ================================================================ KATENER
MITAS = "TEKLİF (Mitaş POLT-3709-R0, 06.10.2026, FCA Ankara, USD, KDV hariç) + %20 nakliye/işçilik/overhead"
direk = lambda kod, ad, n, kg, usd_govde, usd_sablon, ek=(): (kod, ad, [
    (f"{ad} gövdesi – sıcak daldırma galvanizli dikişli boru, taban plakası + kapak dahil ({kg:,.0f} kg toplam) – nakliye ve dikim dahil".replace(",", "."),
     "adet", n, None, f"={usd_govde}/{P_USD}*(1+{P_NAK})", MITAS,
     f"Mitaş {usd_govde:,.0f} USD/direk".replace(",", ".") + " × (1+%20 nakliye+işçilik+overhead); topraklama, etiket, testler hariç"),
    (f"{ad} ankraj şablonu (ankraj bulonları + şablon, alt montaj takımı)", "takım", n, None, f"={usd_sablon}/{P_USD}*(1+{P_NAK})", MITAS,
     f"Mitaş {usd_sablon:,.0f} USD/takım".replace(",", ".") + " × (1+%20); temel inşaat kapsamında"),
    *ek,
])
TOZ_BOYA = [("OPSİYON – Direklere toz boya (galvaniz üzeri, 228 direğin tümü)", "set", 1, None, f"=45000/{P_USD}*(1+{P_NAK})",
             MITAS.replace("TEKLİF (", "TEKLİF – OPSİYON ("), "Mitaş opsiyonu 45.000 USD (tüm direkler) × (1+%20); bütçeye dahil edildi")]
katener = [
    ("220", "2012.A", "Hat Boyu ve Depo Bağlantı Hatları Katener Sistemi", [
        ("Kontak teli 120 mm² Cu ETP (EN 50149, Ø13,2) – çekme dahil", "m", 18748.5, f"=18748.5*{H}", 18,
         "REF BF 16 €/m (31 ref) + montaj", "Hat boyu 6,44/6,56 (Erbakır teklifi bekleniyor)"),
        ("Destek iletkeni 2×120 mm² Cu (iletken metresi)", "m", 37497, f"=37497*{H}", 16,
         "REF medyan 14 €/m + montaj", "Hat boyu oranı"),
        ("Konsol hoban komplesi (çift yalıtımlı) – hat", "adet", 358, None, 1116, "REF medyan (22 ref)", ""),
        ("Konsol hoban komplesi – depo bağlantı hattı", "adet", 40, None, 1116, "REF", ""),
        ("Otomatik gerdirme tertibatı (ağırlıklı, kontak + 2 destek)", "takım", 48, None, 2500, "REF BF (49 ref)", ""),
        ("Antişöminman (mid-point) düzenlemesi", "takım", 24, None, 1164, "REF BF (28 ref)", ""),
        ("Ankraj lentesi teçhizatı (ana hat)", "takım", 66, 0, 485, "REF", "İdare soru 6: ana hatta lente yok"),
        ("Ankraj lentesi temeli – kazı (ana hat)", "m³", 1014.8, 0, 8, "TAHMİN", "İdare soru 6"),
        ("Ankraj lentesi temeli – grobeton C16", "m³", 48.1, 0, 75, "TAHMİN", "İdare soru 6"),
        ("Ankraj lentesi temeli – C25/30 beton", "m³", 618.8, 0, 95, "TAHMİN", "İdare soru 6"),
        ("Ankraj lentesi temeli – kalıp", "m²", 990, 0, 15, "TAHMİN", "İdare soru 6"),
        ("Ankraj lentesi temeli – donatı B500C", "kg", 37125, 0, 0.9, "TAHMİN", "İdare soru 6"),
        ("Ankraj lentesi temeli – ankraj çubuğu/gömme plaka M36", "takım", 66, 0, 250, "TAHMİN", "İdare soru 6"),
        ("Ankraj lentesi temeli – geri dolgu", "m³", 348, 0, 6, "TAHMİN", "İdare soru 6"),
        ("Ankraj direk başı bağlantı (ankraj konsolu, gergi klemensi)", "adet", 78, None, 600, "TAHMİN", "Lentesiz ankraj: T3-D direkleri"),
        ("Hava aralıklı overlap (mekanik, izolesiz)", "adet", 12, None, 3000, "TAHMİN", ""),
        ("Hava aralıklı izoleli seksiyon overlap (TM önü)", "adet", 10, None, 4000, "TAHMİN", ""),
        ("Makas bölgesi hava makası", "adet", 16, None, 2500, "TAHMİN", ""),
        ("Kruvazman katener kesişmesi", "adet", 2, None, 5000, "TAHMİN", ""),
        ("Yaylı gerdirme tertibatı (makas diyagonalleri)", "takım", 12, None, 1481, "REF BF (10 ref)", ""),
        ("Seksiyon izolatörü ünitesi", "adet", 8, None, 2070, "REF BF (21 ref)", "DeSA / Arthur Flury teklifi bekleniyor"),
        ("Motorlu yük ayırıcı 4000 A DC, direk tipi, SCADA arabirimli", "adet", 13, None, 6000, "REF medyan 4.825 + motor tahrik payı", ""),
        ("Aşırı gerilim koruyucu VLD (ray–direk)", "adet", 13, None, 594, "REF medyan (5 ref)", ""),
        ("Besleme (fider) bağlantı düzeneği (bara izolatörü, 1×300 çıkış)", "takım", 16, None, 1500, "TAHMİN", ""),
        ("Parafudr 1 kV DC 10 kA + toprak elektrodu", "takım", 20, None, 744, "REF medyan (4 ref)", ""),
        ("Akım köprüsü 95 mm² örgülü Cu", "adet", 59, None, 461, "REF", ""),
        ("Elektriksel jumper seti 95 mm²", "adet", 44, None, 299, "REF", ""),
        ("95 mm² örgülü esnek Cu iletken", "m", 339.9, None, 25, "TAHMİN", ""),
        ("Gömülü destek iletkeni 150 mm² Cu", "m", 246.4, None, 35, "TAHMİN", ""),
        ("Destek iletkeni ekleri, pabuçlar, direk çıkış aparatları", "adet", 16, None, 150, "TAHMİN", ""),
        ("Tünel/köprü taşıyıcı destek elemanı", "adet", 2, None, 2000, "TAHMİN", ""),
        ("Direk numaralandırma levhası", "adet", 228, None, 37, "REF (3 ref)", ""),
        ("Ayırıcı motor enerji kablosu 3×2,5 NYY", "m", 935, None, 4, "TAHMİN", ""),
        ("Ayırıcı kumanda/konum kablosu 12×1,5 + kilitleme teçhizatı", "m", 935, None, 7, "TAHMİN", ""),
        ("Katener uygulama projesi, EN 50119 hesapları, direk statiği", "set", 1, None, 47158, "REF medyan (4 ref)", ""),
        ("Test, ölçüm, enerjilendirme, devreye alma; 2 yıllık yedek parça", "set", 1, None, 60000, "TAHMİN", "İdare: yedek parça listesi bağlayıcı (sıra 384)"),
    ]),
    ("221", "2012.B", "Depo Sahası ve Tesisleri Katener Sistemi", [
        ("Kontak teli 120 mm² Cu ETP – depo hatları", "m", 5288.1, None, 18, "REF + montaj", ""),
        ("Yaylı gerdirme tertibatı (kontak teli)", "takım", 42, None, 1100, "REF (2 ref)", ""),
        ("Sabit ankraj / sabit germe tertibatı 10 kN", "takım", 42, None, 517, "REF (6 ref)", ""),
        ("Ankraj lentesi teçhizatı (depo ankraj direkleri)", "takım", 21, None, 485, "REF", "İdare cevabı yalnız ana hat lentesi için"),
        ("Hava makası (depo makasları)", "adet", 40, None, 1500, "TAHMİN", ""),
        ("Kruvazman katener kesişmesi (depo)", "adet", 1, None, 4000, "TAHMİN", ""),
        ("Headspan sistemi – komple", "takım", 8, None, 1779, "REF (6 ref)", ""),
        ("Headspan enine taşıyıcı + steady tel", "m", 750.4, None, 20, "TAHMİN", ""),
        ("Headspan altı askı-rapel takımı", "adet", 78, None, 250, "TAHMİN", ""),
        ("Konsol hoban komplesi (tek hat) – depo", "adet", 29, None, 1116, "REF", ""),
        ("Seksiyon izolatörü ünitesi (depo bölümleme)", "adet", 10, None, 2070, "REF", "DeSA formu: depo 10 izolatör"),
        ("Direk tipi motorlu ayırıcı 4000 A (SCADA)", "adet", 6, None, 6000, "REF + motor", ""),
        ("Topraklı elle kumandalı ayırıcı (kilitli kol)", "adet", 4, None, 3553, "REF BF (18 ref)", ""),
        ("Besleme bağlantı düzeneği depo", "takım", 4, None, 1500, "TAHMİN", ""),
        ("Parafudr 1 kV DC + toprak elektrodu", "takım", 4, None, 744, "REF", ""),
        ("VLD ayırıcılı direkler", "adet", 10, None, 594, "REF", ""),
        ("Atölye katlanır (döner) katener mekanizması – A2/A3", "set", 2, None, 20534, "REF medyan (9 ref)", ""),
        ("Atölye sabit kontak hattı A1 ~75 m", "set", 1, None, 7702, "REF", ""),
        ("Atölye ana kesicisi (DC) + kilitlenebilir hat ayırıcıları", "set", 1, None, 25000, "TAHMİN", ""),
        ("Kilitleme sistemi (gezer vinç, katlanır katener, platform, kriko, kapılar)", "set", 1, None, 40000, "TAHMİN", ""),
        ("Acil gerilim kesme butonu + 'katener enerjili' ikaz lambası", "adet", 12, None, 600, "TAHMİN", ""),
        ("Atölye/depo katener güç ve kontrol kabloları", "m", 1595, None, 8, "TAHMİN", ""),
        ("Direk numaralandırma levhası (depo)", "adet", 77, None, 37, "REF", ""),
        ("Depo headspan/portal direği C tipi L=9 m", "adet", 18, 0, 0, "—", "İdare soru 7: depo direkleri cetvel direk kalemlerinde (çift sayım)"),
        ("Depo headspan/portal direği C tipi L=8 m", "adet", 12, 0, 0, "—", "İdare soru 7"),
        ("Depo ara direği A tipi L=8 m", "adet", 26, 0, 1821, "REF", "İdare soru 7"),
        ("Depo ankraj direği D tipi L=8 m", "adet", 21, 0, 0, "—", "İdare soru 7"),
        ("Depo direkleri çelik ağırlığı (galvaniz)", "kg", 44194, 0, f"={P_KG}", "Varsayımlar", "İdare soru 7: çift sayım – düşüldü"),
        ("Portal kirişi HEB-200", "kg", 3752, 0, f"={P_KG}", "Varsayımlar", "İdare soru 7"),
        ("Depo direk temelleri (fore kazık Ø60, beton, donatı, bulon)", "set", 1, 0, 120000, "TAHMİN", "İdare soru 7: temeller sıra 13 (inşaat)"),
        ("Depo lente temelleri (kazı, beton, kalıp, donatı, dolgu)", "set", 1, 0, 30000, "TAHMİN", "Temel işleri inşaat kapsamı (sıra 13)"),
        ("Depo katener uygulama projesi, test ve devreye alma", "set", 1, None, 25000, "TAHMİN", ""),
    ]),
    direk("222", "T1-A Tipi Katener Direği (114 adet)", 114, 39216, 746, 226),
    direk("223", "T2-B Tipi Katener Direği (17 adet)", 17, 7293, 956, 425),
    direk("224", "T2-B1 Tipi Katener Direği (4 adet)", 4, 1452, 860, 426),
    direk("225", "T3-D Tipi Katener Direği (33 adet)", 33, 21912, 1374, 523),
    direk("226", "T3-C Tipi Katener Direği (60 adet)", 60, 39840, 1361, 523, TOZ_BOYA),
]
# direk() returns (sira, title, items) – add poz
katener = katener[:2] + [(s, p, t, it) for (s, t, it), p in zip(katener[2:], ("2012.C", "2012.D", "2012.E", "2012.G", "2012.F"))]
ws_kt, KT_TOT, KT_RFQ, KT_MAIN = sheet("Katener", "5 ELEKTRİFİKASYON (B) – KATENER – Sıra 220–226", katener, "SK")

# ================================================================ CER GÜCÜ / ENERJİ TEMİNİ
RING = f"{P_RING}/{P_RING_RFQ}"
def tm(n, cab_ac, cab_dc, cab_bag, cab_vld, pabuc):
    return [
        ("Cer trafosu 2750 kVA 34,5/0,6-0,6 kV Dy5-Dd0, dökme reçine, EN 50329", "adet", n, None, 85000,
         "REF (3300 kVA: Aktif 97.981, ABB Al 93.263, ABB Cu/Cu 151.850)", "Best Transformer teklifi bekleniyor"),
        ("Trafo sıcaklık rölesi + sekonder toprak kaçağı koruması + izole kaide", "takım", n, None, 3000, "TAHMİN", ""),
        ("Doğrultucu 12 darbeli 2500 kW 750 V DC, Class VI", "adet", n, None, 48000, "REF (ABB 37.927–49.610; Haluk 1,2 MW 35.975)", ""),
        ("Trafo–doğrultucu AC kabloları 1×300 Cu 1,8/3 kV", "m", cab_ac, None, 45, "TAHMİN", ""),
        ("DC giriş (incoming) hücresi 6300 A", "adet", n, None, 36500, "REF (Aktif 36.216–36.824)", ""),
        ("DC fider hücresi HSCB 3600 A", "adet", 4 * n, None, 36000, "REF (Haluk 44.641, MET 43.769, ABB 38.797, Aktif 37.456)", ""),
        ("Negatif hücre (negatif bara, şönt, ayırıcı)", "adet", n, None, 25000, "REF (Aktif 18.852–27.906, ABB 33.751)", ""),
        ("Ray–toprak gerilim sınırlayıcı VLD panosu", "adet", n, None, 20000, "REF (Haluk 13.818, Aktif 16.824–20.961)", ""),
        ("Hat ayırıcı panosu (4 fider + 2 by-pass ayırıcı 4000 A)", "adet", n, None, 45000, "TAHMİN (Aktif ayırıcı hücresi 36.123)", ""),
        ("DC fider kabloları 1×300 Cu 1,8/3 kV", "m", cab_dc, None, 45, "TAHMİN (ref. DC kablo 27–44 €/m)", ""),
        ("Doğrultucu–DC şalt/negatif bağlantısı", "m", cab_bag, None, 45, "TAHMİN", ""),
        ("VLD bağlantı kabloları 1×300 + 1×50", "m", cab_vld, None, 40, "TAHMİN", ""),
        ("DC kablo pabuçları/başlıkları 300 mm²", "adet", pabuc, None, 25, "TAHMİN", ""),
        ("DC şalt izole kaide + çerçeve kaçak koruması (64)", "takım", n, None, 6000, "TAHMİN", ""),
        ("OG–DC kilitleme (anahtar transfer) düzenekleri", "takım", n, None, 4000, "TAHMİN", ""),
        ("Kontrol-koruma, SCADA I/O, 110 V DC kontrol kabloları", "set", n, None, 12000, "TAHMİN", ""),
        ("FAT ve saha testleri, devreye alma, kısa devre testi", "set", n, None, 25000, "TAHMİN", ""),
    ]

cer = [
    ("169", "2001", "Güç Temini ve Cer Gücü Tasarımı", [
        ("Uygulama projeleri (OG ring, TEİAŞ bağlantısı, 5 TM), cer gücü simülasyonu, kısa devre/selektivite, topraklama ve kaçak akım (EN 50122), kompanzasyon raporları, as-built",
         "set", 1, None, 150000, "REF (metro: 133.738–620.171; tramvay ölçeğine indirildi)", ""),
        ("DEDAŞ/TEİAŞ bağlantı projesi onayı ve kurum masrafları", "set", 1, None, 40000, "TAHMİN", ""),
    ]),
    ("170", "2002.A", "OG Ring Şebekesi 3×1×240/25 mm² 20,3/35 kV Al XLPE", [
        ("YAXC7V-R (NA2XSY) 1×240/25 Al XLPE LSHF tek damar kablo – çekme dahil", "m", 21000, f"=3*{P_RING}", 11,
         "REF (Prysmian 1×400 15 €/m; Haluk 1×150 11 €/m)", "İdare soru 21: güzergah 7.964 m"),
        ("36 kV 1×240 kablo başlığı", "adet", 24, None, 450, "TAHMİN", ""),
        ("36 kV 1×240 ek mufu", "adet", 33, f"=ROUND(33*{RING},0)", 400, "TAHMİN", "Güzergah oranında"),
        ("Trefoil kelepçe / kanal içi askı", "adet", 6500, f"=ROUND(6500*{RING},0)", 6, "TAHMİN", "Güzergah oranında"),
        ("Yangın durdurucu (TM geçişleri)", "adet", 10, None, 200, "TAHMİN", ""),
        ("Kablo etiket / güzergah markörü", "adet", 140, f"=ROUND(140*{RING},0)", 15, "TAHMİN", ""),
        ("OG kablo saha testleri (VLF, kılıf)", "set", 4, None, 3000, "TAHMİN", ""),
    ]),
    ("171", "2002.B", "TEİAŞ Bağlantısı 2×4×(1×400+35) mm² 20,3/35 kV – transe dahil", [
        ("YAXC7V-R 1×400/35 Al XLPE zırhlı LSHF – çekme dahil", "m", 35424, None, 16, "REF (Prysmian 15 €/m malzeme) + çekme", "İdare: 8.856 m × 4 kablo – uyumlu"),
        ("36 kV 1×400 kablo başlığı", "adet", 16, None, 600, "TAHMİN", ""),
        ("36 kV 1×400 ek mufu", "adet", 68, None, 550, "TAHMİN", ""),
        ("Kablo kanalı kazısı 0,80×1,40 m", "m³", 9919, None, 8, "TAHMİN", ""),
        ("HDPE/koruge boru Ø160 (her damar ayrı)", "m", 38966.4, None, 6, "TAHMİN", ""),
        ("Yol geçişleri yedek boş boru Ø160", "m", 4383.72, None, 6, "TAHMİN", ""),
        ("Dolgu kumu", "m³", 3542, None, 18, "TAHMİN", ""),
        ("Harman tuğlası", "adet", 44280, None, 0.25, "TAHMİN", ""),
        ("Plastik ikaz bandı", "m", 19483.2, None, 0.3, "TAHMİN", ""),
        ("C14 koruma betonu", "m³", 709, None, 75, "TAHMİN", ""),
        ("Yol/kaldırım kaplamasının eski haline getirilmesi", "m²", 6200, None, 25, "TAHMİN", ""),
        ("Kazı fazlası nakli", "m³", 4430, None, 6, "TAHMİN", ""),
        ("Güzergah işaret taşı", "adet", 180, None, 30, "TAHMİN", ""),
        ("OG kablo saha testleri", "set", 2, None, 4000, "TAHMİN", ""),
    ]),
    ("172", "2003", "Enerji Kalitesi ve Yönetimi Sistemi", [
        ("AG tristörlü kompanzasyon kademesi 50 kVAr 690 V", "adet", 12, None, 1500, "TAHMİN", ""),
        ("AG tristörlü kompanzasyon kademesi 25 kVAr 690 V", "adet", 8, None, 1000, "TAHMİN", ""),
        ("Kompanzasyon panosu (röle, Modbus, fan) – her TM 1", "adet", 5, None, 6000, "TAHMİN", ""),
        ("MCCB 3×250 A + besleme kablosu 3×70", "set", 1, None, 12300, "TAHMİN", "10 MCCB + 143 m kablo"),
        ("OG şönt reaktör sistemi (TM-4 çıkışı)", "set", 1, None, 60000, "TAHMİN", ""),
        ("36 kV 630 A kesicili kompanzasyon fider hücresi", "adet", 1, None, 28000, "REF (36 kV kesicili hücre)", ""),
        ("34,5/0,4 kV 630 kVA kuru tip kompanzasyon trafosu", "adet", 1, None, 18000, "REF (Aktif 630 kVA 22.231 Al)", ""),
        ("Enerji kalite kaydedicisi Class A", "adet", 5, None, 4000, "TAHMİN", ""),
        ("AG enerji analizörü + Modbus ağ geçidi", "set", 1, None, 12400, "TAHMİN", "6 analizör + 11 gateway"),
        ("Enerji yönetim yazılımı (ISO 50001) + TCC operatör", "set", 1, None, 25000, "TAHMİN", ""),
        ("Haberleşme kabloları, harmonik ölçümleri, devreye alma, DEDAŞ raporu", "set", 1, None, 11500, "TAHMİN", ""),
    ]),
    ("173", "2004.A", "Ring Giriş/Çıkış 34,5 kV Şalt Panosu (12 hücre)", [
        ("36 kV 1250 A 25 kA SF6 kesicili hücre + AT + sayısal röle + ölçü + kilitleme + FAT/SAT", "adet", 12, None, 26000,
         "REF (Haluk LSC2B ring hücresi 30.518) + röle/test", ""),
    ]),
    ("174", "2004.B", "Cer Trafo Besleme 34,5 kV Şalt Panosu (5 hücre)", [
        ("36 kV kesicili trafo koruma hücresi + röle + analizör + DC kilitleme", "adet", 5, None, 24000, "REF (Haluk 26.130) + pay", ""),
        ("OG bağlantı kablosu 3(1×95/16) Al – hücre/cer trafosu", "m", 108, None, 25, "TAHMİN", ""),
        ("36 kV 1×95 kablo başlığı (büzüşmeli + geçmeli)", "adet", 30, None, 350, "TAHMİN", ""),
    ]),
    ("175", "2004.C", "İç İhtiyaç Trafo Besleme 34,5 kV Şalt Panosu (6 hücre)", [
        ("36 kV kesicili iç ihtiyaç trafo fider hücresi + röle", "adet", 6, None, 23000, "REF (Haluk 26.130) + pay", ""),
        ("OG bağlantı kablosu 3(1×95/16) Al", "m", 129, None, 25, "TAHMİN", ""),
        ("36 kV 1×95 kablo başlığı", "adet", 36, None, 350, "TAHMİN", ""),
    ]),
    ("176", "2004.D", "Ölçü 34,5 kV Şalt Panosu", [
        ("36 kV akım-gerilim ölçü hücresi (TEİAŞ girişli TM)", "adet", 2, None, 19254, "REF (Haluk)", ""),
        ("36 kV bara gerilim ölçü (VT) hücresi", "adet", 3, None, 13534, "REF (Haluk; Aktif 10.831–12.623)", ""),
        ("Elektronik sayaç cl 0,2S + sayaç panosu/modem", "set", 1, None, 9000, "TAHMİN", "4 sayaç + 2 pano"),
    ]),
    ("177", "2004.E", "TEİAŞ Giriş 34,5 kV Şalt Panosu (mevcut TM-4'te fider ilavesi)", [
        ("36 kV kesicili fider hücresi ilavesi, bara uzatma, kurum izinleri", "set", 2, None, 45000, "REF (Haluk 39.293, MET 29.821) + pay", ""),
    ]),
    ("178", "2005.A", "Hat TM İç İhtiyaç Trafosu 250 kVA (4 adet)", [
        ("34,5/0,4 kV 250 kVA Dyn11 kuru tip trafo Cu/Cu, röle, kaide, test", "adet", 4, None, 16000,
         "TAHMİN (Al ref 4.625–7.264 yağlı/hermetik; kuru tip Cu)", "İdare: iç ihtiyaç trafoları Cu/Cu zorunlu"),
    ]),
    ("179", "2005.B", "Depo TM İç İhtiyaç Trafosu 2000 kVA (2 adet)", [
        ("34,5/0,4 kV 2000 kVA Dyn11 kuru tip trafo Cu/Cu, fanlı, röle, test", "adet", 2, None, 42000,
         "REF (2×2000 kVA set 92.552–104.613) + Cu", "İdare: Cu/Cu zorunlu"),
    ]),
    ("187", "2006.H", "Hat Trafo Binaları AG Ana Dağıtım Panoları (4 set)", [
        ("ADP/1 panosu (MCCB 320 A giriş, analizör, parafudr, istasyon/klima çıkışları) + UDP + montaj/test", "set", 4, None, 24000, "TAHMİN", ""),
    ]),
    ("188", "2007.A", "Hat TM Cer Merkezi – 1×2,75 MVA (4 adet)", tm(4, 961, 687, 618, 143, 479)),
    ("189", "2007.B", "Depo TM Cer Merkezi – 1×2,75 MVA (1 adet)", tm(1, 241, 172, 155, 36, 120)),
    ("197", "2008.H", "Hat Trafo Binaları Topraklama Tesisatı (4 set)", [
        ("Temel altı ağ 1×120 mm² çıplak Cu", "m", 1019, None, 18, "TAHMİN", ""),
        ("Bakır kazık elektrod Ø20×1,5 m", "adet", 63, None, 120, "TAHMİN", ""),
        ("Bina içi şerit, bara, ekipman topraklama iletkenleri, klemensler", "set", 1, None, 10500, "TAHMİN", ""),
        ("Egzotermik kaynak", "adet", 120, None, 25, "TAHMİN", ""),
        ("Topraklama/adım-dokunma ölçümleri", "set", 4, None, 800, "TAHMİN", ""),
    ]),
    ("200", "2009.A", "Hat TM 110 V DC Akü-Şarj (4 set)", [
        ("110 V DC 160 Ah VRLA akü + 50 A şarj + DC dağıtım paneli + MCB + izolasyon izleme + test", "set", 4, None, 23000,
         "REF (İnform/Legrand redresör 19.596 + akü 13.023; Kocaeli 17.680)", ""),
    ]),
    ("201", "2009.B", "Depo TM 110 V DC Akü-Şarj (1 set)", [
        ("110 V DC 160 Ah VRLA akü + şarj + dağıtım paneli + test", "set", 1, None, 23000, "REF", ""),
    ]),
    ("202-208", "2010.A-G", "İstasyon (6) ve Depo Kaçak Akım İzleme / Korozyon Kontrolü", [
        ("İstasyon bölgesi: test kutuları, referans elektrot, donatı süreklilik, peron metal izolasyonu, ölçümler", "set", 6, None, 6000,
         "TAHMİN (REF 2010.B 2.958 kısmi)", ""),
        ("Depo: izole ray eki, DC süreklilik kabloları, VLD arabirimi, test kutuları, ölçümler", "set", 1, None, 24346, "REF", ""),
    ]),
    ("209", "2010.H", "Hat TM Kaçak Akım İzleme (4 set)", [
        ("Ray potansiyeli/kaçak akım izleme ünitesi + drenaj panosu", "set", 4, None, 11000, "TAHMİN", ""),
        ("Ölçüm/bağlantı kabloları, test kutuları, referans elektrot, devreye alma", "set", 1, None, 25000, "TAHMİN", ""),
    ]),
    ("210", "2010.I", "Hatboyu ve Üst Geçit Kaçak Akım İzleme / Korozyon Kontrolü", [
        ("Cross-bond, hatlar arası bağlantı, test kutuları, referans elektrotlar, merkezi yazılım, EN 50122-2 ölçümleri", "set", 1, None, 108713, "REF", ""),
    ]),
    ("219", "2011.I", "Hat Trafo Binaları AG Kabloları ve Kablo Taşıma (4 set)", [
        ("AG kabloları (N2XH 1×240, 4×6, 3×2,5, PE, 110 V DC)", "set", 1, None, 28000, "TAHMİN", ""),
        ("Kablo tavası/merdiveni, tava topraklaması, HDPE, yangın durdurucu, test", "set", 1, None, 52000, "TAHMİN", ""),
    ]),
    ("227", "2013.A", "Depo Trafo Binası Busbar (kablo bağlantısı)", [
        ("N2XH 1×240 Cu + pabuç + bara/mesnet + merdiven + kelepçe + test", "set", 1, None, 44000, "TAHMİN (ref. busbar 15.151–55.516)", ""),
    ]),
]
ws_cg, CG_TOT, CG_RFQ, CG_MAIN = sheet("Cer_Guc", "5 ELEKTRİFİKASYON (A) – GÜÇ TEMİNİ / CER GÜCÜ / ENERJİ TEMİNİ (5 TM, OG ring, TEİAŞ bağlantısı)", cer, "MEP")


# ================================================================ MEKANİK / ELEKTRİK AG / HABERLEŞME (CSV'den)
import csv, os, collections
MEP_DIR = os.environ.get("MEP_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "veri"))


# Alt kalemleri "bina başına" verilmiş, cetvel miktarı 4 olan satırlar (çarpan düzeltmesi)
CARP_OVERRIDE = {"elektrik": {"331": 4, "341": 4}}


def groups_from_csv(key):
    rows = list(csv.DictReader(open(os.path.join(MEP_DIR, f"{key}_in.csv"), encoding="utf-8")))
    out = {r["id"]: r for r in csv.DictReader(open(os.path.join(MEP_DIR, f"{key}_out.csv"), encoding="utf-8"))}
    num = lambda v: float(v) if v not in (None, "") else None
    groups, cur, carp = [], None, 1
    for r in rows:
        if r["tip"] == "ANA":
            carp = CARP_OVERRIDE.get(key, {}).get(r["sira"], num(r["carpan"]) or 1)
            cur = [r["sira"], r["poz"], f"{r['kalem']} ({r['miktar']} {r['birim']})", []]
            groups.append(cur)
            if r["id"] in out:  # alt kalemi olmayan ana kalem
                o = out[r["id"]]
                q = num(r["miktar"]); qc = num(o["q_corr"])
                cur[3].append((r["kalem"], r["birim"], q, qc if qc is not None else None,
                               num(o["bf_eur"]) or 0, o["kaynak"], o["not"]))
            continue
        o = out.get(r["id"])
        if o is None:
            raise SystemExit(f"fiyat yok: {r['id']}")
        q = (num(r["miktar"]) or 0) * carp
        qc = num(o["q_corr"])
        notu = o["not"] + (f" (alt miktar ×{carp:g} set)" if carp != 1 else "")
        ref = f" [ref {r['ref_BF']}]" if r["ref_BF"] and o["kaynak"] != "REF" else ""
        cur[3].append((r["kalem"], r["birim"], q, None if qc is None else qc * carp,
                       num(o["bf_eur"]) or 0, o["kaynak"] + ref, notu.strip()))
    return [tuple(g) for g in groups if g[3]]


mekanik = groups_from_csv("mekanik")
ws_mk, MK_TOT, MK_RFQ, MK_MAIN = sheet("Mekanik", "2 MEKANİK – Sıra 159–168, 343–363 (HVAC, yangın, drenaj, sıhhi, basınçlı hava)", mekanik, "MEP")
elk_ag = groups_from_csv("elektrik")
ws_ea, EA_TOT, EA_RFQ, EA_MAIN = sheet("Elektrik_AG", "1 ELEKTRİK (A) – AG dağıtım, topraklama, AG kablolar, AG tesisat-aydınlatma, yangın ihbar", elk_ag, "MEP")
hab = groups_from_csv("haberlesme")
ws_hb, HB_TOT, HB_RFQ, HB_MAIN = sheet("Haberlesme", "1 ELEKTRİK (B) – Kontrol ve haberleşme (iletim, telefon, telsiz, anons, CCTV, saat, erişim, SCADA, YBS, ücret toplama)", hab, "MEP")



# ---------------------------------------------------------------- İhale geneli (MEP dışı) – bilgi
B = wb.create_sheet("Ihale_Geneli_Bilgi")
B["A1"] = "İHALE GENELİ – MEP DIŞI GELEN TEKLİFLER (bilgi amaçlı; MEP bütçesine dahil değildir)"
B["A1"].font = Font(bold=True, size=13)
B["A2"] = ("Tutarlar EUR, KDV hariç. Rayba: demiryolu işleri teklifi beton ve donatı hariç; işlerin bölünmesi halinde birim fiyatlar "
           "değişebilir; 31.12.2026'ya kadar geçerli. S-LINE: malzeme teklifi, en az 15.000 hat-metre için geçerli, teslim Şanlıurfa, "
           "%25 avans/%75 teslimde. Not: 'S-LINE kauçuk kapsül' kalemi, demiryolu teklifindeki hat döşeme fiyatının içinde olabilir – "
           "çift sayım için ayrı alt toplam verilmiştir.")
B["A2"].alignment = WRAP; B.merge_cells("A2:K2"); B.row_dimensions[2].height = 48
bh = ["Firma", "Teklif", "Tarih", "No", "Kalem", "Birim", "Miktar", "Malzeme BF €", "İşçilik BF €", "Toplam €", "Not"]
for j, h in enumerate(bh, 1):
    c = B.cell(row=4, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
_b = 5; _grp = {}
for _r in csv.DictReader(open(os.path.join(MEP_DIR, "ihale_geneli_teklifler.csv"), encoding="utf-8")):
    for j, k in enumerate(["firma", "teklif", "tarih", "no", "kalem", "birim", "miktar", "malzeme_bf", "iscilik_bf", "toplam", "not"], 1):
        v = _r[k]
        if k in ("miktar", "malzeme_bf", "iscilik_bf") and v != "":
            v = float(v)
        if k == "toplam":
            v = f"=G{_b}*(H{_b}+N(I{_b}))"
        c = B.cell(row=_b, column=j, value=v); c.border = BOX; c.alignment = WRAP
        if j in (8, 9, 10): c.number_format = EUR2 if j < 10 else EUR
    _grp.setdefault(_r["teklif"], []).append(_b)
    _b += 1
_b += 1
B.cell(row=_b, column=5, value="ALT TOPLAMLAR").font = BOLD
IHALE_GENEL = []
for t, rows_ in _grp.items():
    _b += 1
    B.cell(row=_b, column=5, value=t).font = BOLD
    c = B.cell(row=_b, column=10, value=f"=SUM(J{rows_[0]}:J{rows_[-1]})"); c.number_format = EUR; c.font = BOLD
    IHALE_GENEL.append((t, f"'Ihale_Geneli_Bilgi'!$J${_b}"))
_b += 1
B.cell(row=_b, column=5, value="TOPLAM (iki teklif birlikte – çift sayım kontrol edilmeli)").font = BOLD
c = B.cell(row=_b, column=10, value="=" + "+".join(x[1] for x in IHALE_GENEL)); c.number_format = EUR; c.font = BOLD
for j in (5, 10):
    B.cell(row=_b, column=j).fill = FILL_TOT
_b += 2
B.cell(row=_b, column=1, value="Diğer bilgi: Point Link / CASCO sinyalizasyon teklifi 7.281.784 € (DAP, KDV ve gümrük hariç, dökümsüz) – MEP sinyal bütçesinde kullanılmadı; Teklif_Degerlendirme sayfasında.").alignment = WRAP
B.merge_cells(start_row=_b, start_column=1, end_row=_b, end_column=11); B.row_dimensions[_b].height = 30
for col, w in zip("ABCDEFGHIJK", (14, 34, 16, 5, 52, 9, 10, 12, 12, 14, 30)):
    B.column_dimensions[col].width = w



# ---------------------------------------------------------------- Point Link kalem kalem kıyas
PL = wb.create_sheet("PointLink_Kiyas")
PL["A1"] = "POINT LINK / CASCO SİNYALİZASYON + AVLS TEKLİFİ – KALEM KALEM KIYAS (teklif 01.10.2026, 7.281.784 EUR, DAP Şanlıurfa, KDV ve gümrük hariç)"
PL["A1"].font = Font(bold=True, size=13)
PL["A2"] = ("Kaynak: PointLink_2026-10-01_Sinyalizasyon_AVLS_Teklif.pdf (8 sayfa; win1 G:\\urfa_ihale\\...\\Gelen_Teklifler\\03_SINYALIZASYON'dan aktarıldı). "
            "Uyarı: teklif maili mepcenter Gmail'de bulunamıyor; mailimiz firmaya üçüncü kişi tarafından iletilmiş (Fwd) ve yanıt 'Eva' adlı yapay zekâ asistanı imzalı – kaynak teyidi gerekir. "
            "Teklif RFQ (şişirmeli, idare cevabı öncesi) miktarlarıyla verilmiştir; 'idareye göre uyarlanmış' sütunu aynı birim fiyatlarla idare cevaplarını uygular.")
PL["A2"].alignment = WRAP; PL.merge_cells("A2:H2"); PL.row_dimensions[2].height = 58
h = ["Sıra", "Kalem", "Point Link teklif € (RFQ miktarı)", "Point Link – idare cevaplarına göre uyarlanmış €", "Uyarlama", "Bütçemiz (kalem bazlı) €", "Fark (PL uyarlanmış / bütçe − 1)"]
for j, t in enumerate(h, 1):
    c = PL.cell(row=4, column=j, value=t); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
PL.row_dimensions[4].height = 42
pl_rows = [
    ("228", "Sinyalizasyon sistemi tasarımı (RAMS, ISA 180.000 dahil)", 540000, "=C5", "—"),
    ("229", "Hat boyu sinyalizasyon", 2599016, "=C6-151800-156350-60368-13552-11520-7475+4*7950+4*2220",
     "TSKP (151.800), trafik lambaları/direkleri (156.350), trafik kablo+boru (73.920), manuel makas+izleme (18.995) düşüldü; +4 motorlu makas (PL birim fiyatıyla)"),
    ("230", "Depo sinyalizasyon", 972370, "=C7-52800+20*7080+20*1980", "20 manuel makas düşüldü; +20 motorlu makas + çubuk seti"),
    ("231", "Araç üstü sinyalizasyon", 848725, "=(C8-85000)*14/15+85000", "15 → 14 araç"),
    ("232", "Sinyalizasyon merkez donanımı ve yazılım", 927605, "=C9-82500", "Mevcut depo kontrol merkezi entegrasyonu (82.500) düşüldü"),
    ("233", "Araç takip – araç üstü", 381565, "=(C10-8960-21600-65000)*14/15+8960+21600+65000", "15 → 14 araç"),
    ("234", "Araç takip – merkez", 509700, "=C11", "—"),
    ("235", "Araç takip – tasarım", 150000, "=C12", "—"),
]
for i, (sira, ad, pl, adj, nt) in enumerate(pl_rows, start=5):
    vals = [sira, ad, pl, adj, nt, f"='Sinyal'!{SN_MAIN[sira]}", f"=IF(F{i}=0,\"\",D{i}/F{i}-1)"]
    for j, v in enumerate(vals, 1):
        c = PL.cell(row=i, column=j, value=v); c.border = BOX; c.alignment = WRAP
        if j in (3, 4, 6): c.number_format = EUR
        if j == 7: c.number_format = "+0%;-0%"
    PL.row_dimensions[i].height = 30
_t = 5 + len(pl_rows)
PL.cell(row=_t, column=2, value="Ara toplam").font = BOLD
for col in "CDF":
    c = PL[f"{col}{_t}"]; c.value = f"=SUM({col}5:{col}{_t-1})"; c.number_format = EUR; c.font = BOLD
PL.cell(row=_t + 1, column=2, value="Nakliye ve sigorta (DAP, malzemenin %8'i – PL; uyarlanmışta orantılı)")
PL[f"C{_t+1}"] = 352802; PL[f"D{_t+1}"] = f"=C{_t+1}*D{_t}/C{_t}"
PL.cell(row=_t + 2, column=2, value="GENEL TOPLAM (gümrük vergisi ve KDV hariç)").font = BOLD
for col in "CD":
    PL[f"{col}{_t+2}"] = f"={col}{_t}+{col}{_t+1}"; PL[f"{col}{_t+2}"].font = BOLD
PL[f"F{_t+2}"] = f"=F{_t}"; PL[f"G{_t+2}"] = f"=D{_t+2}/F{_t+2}-1"
for rr in (_t, _t + 1, _t + 2):
    for col in "CDF": PL[f"{col}{rr}"].number_format = EUR
    PL[f"G{rr}"].number_format = "+0%;-0%"
    for j in range(1, 8): PL.cell(row=rr, column=j).fill = FILL_TOT; PL.cell(row=rr, column=j).border = BOX
PL[f"G{_t}"] = f"=D{_t}/F{_t}-1"
PLT = {"orj": f"'PointLink_Kiyas'!$C${_t+2}", "adj": f"'PointLink_Kiyas'!$D${_t+2}"}

_u = _t + 5
PL.cell(row=_u - 1, column=1, value="BİRİM FİYAT KIYASI – farkı oluşturan başlıca kalemler (montajlı birim fiyat, €)").font = Font(bold=True, size=12)
for j, t in enumerate(["Sıra", "Kalem", "Point Link montajlı BF €", "Bütçemiz BF €", "Fark %", "Yorum"], 1):
    c = PL.cell(row=_u, column=j, value=t); c.font = F_H; c.fill = FILL_H; c.border = BOX
uk = [("229", "Elektrikli makas motoru (IP67, iç kilitli, uç konum dedektörlü) – ana hat", 7950, "PL daha düşük (CASCO tramvay tipi; Adapazarı teklifinden)"),
      ("230", "Elektrikli makas motoru – depo (IP67, el kranklı, uç konum dedektörlü)", 7080, "PL daha düşük"),
      ("229", "Lokal kontrol ve kumanda kabini SKP (SIL3, GRP IP54)", 166750, "PL ~2,4 kat; Konya/Adapazarı SIL4 kilitleme birimi 165.000 bazlı"),
      ("230", "Depo sinyalizasyon kontrol ünitesi SKP (SIL2) + IO", 126500, "PL yüksek"),
      ("229", "Ray devresi / kütle dedektörü (makas kilitleme, bölge meşgul)", 5340, "PL aks sayacı önerir (ray devresi yerine)"),
      ("229", "Karayolu kavşağı sinyalizasyon kontrol kabini TSP (tramvay öncelik)", 78200, "PL ~9 kat; emsallerimiz 7–23 bin €"),
      ("229", "Test, devreye alma, entegre test, 15 gün test işletmesi – hat boyu", 360000, "PL saha hizmetleri çok yüksek (Konya 1,1 M€ toplam hizmet)"),
      ("232", "Sinyalizasyon özel yazılımı + lisanslar (ana uygulama, sinoptik, protokoller)", 299000, "PL ~2 kat"),
      ("230", "Depo güzergah/kilitleme yazılımı (15+ güzergah), test ve devreye alma", 150000, "PL ~2 kat")]
for k, (sira, kal, plbf, yorum) in enumerate(uk, start=_u + 1):
    rr = ROWMAP.get(("Sinyal", sira, kal))
    ours = f"='Sinyal'!I{rr}" if rr else None
    vals = [sira, kal, plbf, ours, f"=IF(D{k}=0,\"\",C{k}/D{k}-1)", yorum]
    for j, v in enumerate(vals, 1):
        c = PL.cell(row=k, column=j, value=v); c.border = BOX; c.alignment = WRAP
        if j in (3, 4): c.number_format = EUR
        if j == 5: c.number_format = "+0%;-0%"
_n = _u + len(uk) + 2
for k, t in enumerate([
    "DEĞERLENDİRME",
    "• Point Link (CASCO) teklifi, idare cevaplarına göre uyarlandığında bile bütçemizin belirgin üstündedir. Fark, makas motoru veya aks sayacı gibi saha ekipmanından değil; kontrol kabinleri (SKP/TSP), yazılım, tasarım/ISA ve test-devreye alma hizmetlerinden kaynaklanır.",
    "• Teklifteki birim fiyatların bir kısmı firmanın kendi beyanına göre Konya ve Adapazarı CASCO tekliflerinden aktarılmış, döngü/sorgulayıcı/AVLS kalemleri 'mühendislik tahmini'dir. Teklif SIL4 → SIL3/SIL2 düşürmesini yalnız kısmen yansıtır.",
    "• Bütçe kararı: sinyalizasyon bütçesi geçmiş teklif emsalleri ve Mukan AVLS teklifiyle korunmuştur; Point Link uyarlanmış toplamı 'üst sınır / ithal anahtar teslim senaryosu' olarak raporlanır. Gümrük vergisi ve ithalat masrafları ayrıca eklenmelidir.",
    "• Teklif PDF'i (Quotation_Sanliurfa_Phase1_Signalling_AVLS_20261001, 01.10.2026) 07.10.2026'da doğrudan iletildi; veri/gelen_teklifler arşivindedir. Rakamlar bu PDF ile birebir aynıdır."], start=_n):
    c = PL.cell(row=k, column=1, value=t); c.alignment = WRAP
    PL.merge_cells(start_row=k, start_column=1, end_row=k, end_column=7); PL.row_dimensions[k].height = 15 if t == "DEĞERLENDİRME" else 30
PL.cell(row=_n, column=1).font = BOLD
for col, w in zip("ABCDEFG", (7, 52, 18, 20, 48, 18, 16)):
    PL.column_dimensions[col].width = w

# ---------------------------------------------------------------- Gelen tekliflerin değerlendirmesi
E = wb.create_sheet("Teklif_Degerlendirme", 1)
E["A1"] = "GELEN TEKLİFLERİN DEĞERLENDİRMESİ (06.10.2026 itibarıyla okunabilen teklifler)"
E["A1"].font = Font(bold=True, size=13)
E["A2"] = ("Tutarlar KDV hariç. EUR karşılığı Varsayımlar sayfasındaki kurla. 'Bütçe karşılığı' = aynı kapsam için bu "
           "çalışmadaki kalem bazlı tutar (net metraj, idare cevaplarına göre). Fark = teklif / bütçe − 1.")
E["A2"].alignment = WRAP; E.merge_cells("A2:N2"); E.row_dimensions[2].height = 30
eh = ["Disiplin", "Firma", "Tarih", "Kapsam (cetvel sıra)", "Teklif tutarı", "PB", "Teklif EUR", "Bütçe karşılığı EUR",
      "Fark %", "Birim fiyat (EUR)", "Teknik uygunluk / sapmalar", "Ticari şartlar", "Bütçede kullanımı", "Değerlendirme"]
for j, h in enumerate(eh, 1):
    c = E.cell(row=4, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
E.row_dimensions[4].height = 32
as12 = f"'Asansor'!{AS_MAIN['364']}"; as1 = f"'Asansor'!{AS_MAIN['365']}"
avls = "+".join(f"'Sinyal'!{SN_MAIN[k]}" for k in ("233", "234", "235"))
KAT_DIREK = "+".join(f"'Katener'!{KT_MAIN[k]}" for k in ("222", "223", "224", "225", "226"))
MSS_BUT = "+".join(f"'Haberlesme'!{HB_MAIN[k]}" for k in ("281", "282", "283", "284", "285", "286", "287", "288", "289"))
YBS_BUT = "+".join(f"'Haberlesme'!{HB_MAIN[k]}" for k in ("310", "311", "312", "313", "314", "315", "316", "317"))
erows = [
    ("Asansör", "Schindler Türkeli", "01.10.2026", "364–365 (13 asansör)", 480000, "USD", f"=E5/{P_USD}", f"={AS_TOT}",
     "1000 kg: 37.000 USD; 800 kg: 36.000 USD", "Şartnameye uygun beyan; bakım hariç",
     "Geçerlilik/ödeme Excel'de belirtilmemiş", "Medyan hesabına dahil", "En yüksek teklif; kapsam tam"),
    ("Asansör", "TK Elevator", "02.10.2026", "364–365 (13 asansör)", 414200, "EUR", "=E6", f"={AS_TOT}",
     "1000 kg: 32.000 (24.000 malz.+8.000 işç.); 800 kg: 30.200", "Antivandal CAT-2, dış ortam; kapı 900×2000 (talep 1100×2100); seyir 6 m (proje ~7,46 m)",
     "Geçerlilik 30 gün (talep 180); ödeme %50/%40/%10; teslim 8 ay; çelik işleri hariç; bakım 120 €/ay/adet",
     "Medyan = TK birim fiyatı (bütçe esası)", "Teknik olarak en uygun; geçerlilik süresi uzatılmalı, kapı ölçüsü teyit"),
    ("Asansör", "Emlift", "05.10.2026", "364–365 (13 asansör)", 19500000, "TRY", f"=E7/{P_TRY}", f"={AS_TOT}",
     "1.500.000 TL/adet (≈" + "26.700 €)", "Teknik föy başka işten kopya (15 m seyir, 135×145 kabin); antivandal/dış ortam yok; kapı 900×2000",
     "Geçerlilik ve ödeme şartı yok; kuyu aydınlatma, topraklama, MMO/belediye harçları hariç",
     "Medyan hesabına dahil (alt sınır)", "En düşük ama şartname sapmalı; teknik föy yenilenmeli"),
    ("Sinyalizasyon – AVLS", "Mukan Rail", "06.10.2026", "233–235 (araç takip)", 788000, "EUR", "=E8", f"={avls}",
     "Araç başı 21.300; merkez 314.500 (yazılım+lisans 172.500); tasarım 154.000",
     "11 soruya verilen varsayımlar esas; 2 sunucu + NAS; konum güncelleme ≤3 sn",
     "Bütçesel; 180 gün; %20 avans/%70 hakediş/%10 kabul; kabin, UPS, omurga, işletme SIM, yedek parça hariç",
     "Bütçeye işlendi (233: 14 araç)", "Tek teklif; H&K İzmir referansının ~2 katı – pazarlık payı var"),
    ("Elektrik – saat sistemi", "ON Elektronik (RayON)", "06.10.2026", "281–289 (MSS)", 81600, "EUR", "=E10", f"={MSS_BUT}",
     "Peron saati 3.000; master saat (Mobatime) 4.500; duvar saati 850–1.500", "Üretici; şartnameye uygun beyan",
     "Kablolar ana yüklenicide (bütçede ayrıca var); geçerlilik belirtilmemiş", "Kalem kalem bütçeye işlendi",
     "Mevcut depo entegrasyonu (2.500) idare cevabıyla düşüldü"),
    ("Elektrik – yolcu bilgilendirme", "ON Elektronik (RayON)", "06.10.2026", "310–317 (YBS)", 171000, "EUR", "=E11", f"={YBS_BUT}",
     "55\" dış ortam ekran 3.500; askı 1.250; yazılım 25.000; tasarım+doküman 26.000", "Medya oynatıcı ekrana dahil",
     "Kablolar ana yüklenicide; geçerlilik belirtilmemiş", "Kalem kalem bütçeye işlendi",
     "Mevcut depo entegrasyonu (11.000) idare cevabıyla düşüldü"),
    ("Katener – direkler", "Mitaş Endüstri", "06.10.2026", "222–226 (228 direk + ankraj şablonu + toz boya ops.)", 360070, "USD", "", f"={KAT_DIREK}",
     "Direk 746–1.374 USD; ankraj şablonu 226–523 USD", "Sıcak daldırma galvaniz, dikişli boru, EN 1090-2 EXC2; C/D tipleri Mitaş çizimine göre",
     "FCA Ankara (nakliye hariç); %40 avans, bakiye teslimden önce; 13.10.2026'ya kadar sabit; montaj, topraklama, testler hariç",
     "Kalem kalem bütçeye işlendi: teklif + toz boya opsiyonu, üzerine %20 nakliye+işçilik+overhead", "Teklif tutarı 315.070 + 45.000 USD toz boya opsiyonu; bütçe = teklif × 1,20"),
    ("Sinyalizasyon (tümü)", "Point Link / CASCO (Çin)", "01.10.2026", "228–235 (RFQ miktarlarıyla)", 7281784, "EUR", "=E12", f"={SN_TOT}",
     "Makas motoru 7.950; SKP 166.750; TSP 78.200; aks sayacı 5.340; araç başı 82.019 (sinyal+AVLS)",
     "Kalem kalem döküm var (PointLink_Kiyas). Aks sayacı ray devresi yerine; TSKP/trafik ekipmanı dahil; mevcut sistem entegrasyonu dahil; 15 araç",
     "DAP şantiye; KDV, gümrük vergisi hariç; 180 gün; garanti 24 ay. Orijinal PDF 07.10.2026'da iletildi (veri/gelen_teklifler)",
     "Kullanılmadı – üst sınır senaryosu", "İdareye göre uyarlanmış toplam da bütçenin belirgin üstünde; fark kabin, yazılım ve hizmet kalemlerinde (PointLink_Kiyas)"),
]
for i, row in enumerate(erows, start=5):
    row = list(row)
    row[6] = f'=E{i}/IF(F{i}="USD",{P_USD},IF(F{i}="TRY",{P_TRY},1))'
    vals = row[:8] + [f"=IF(H{i}=0,\"\",G{i}/H{i}-1)"] + row[8:]
    for j, v in enumerate(vals, 1):
        c = E.cell(row=i, column=j, value=v); c.border = BOX; c.alignment = WRAP
        if j in (5, 7, 8): c.number_format = EUR
        if j == 9: c.number_format = "+0%;-0%"
    E.row_dimensions[i].height = 60
_rr = 5 + len(erows)
E.cell(row=_rr, column=1, value="Bilgi – MEP dışı").border = BOX
for j, v in enumerate(["Rayba Yapı (demiryolu üstyapı)", "02.10 / 05.10.2026", "Ray, makas, kruvazman; S-LINE bağlantı",
                       17348355 + 1759956, "EUR", "", "", "", "42×R50 + 2×R100 makas + 3 kruvazman (= 56 makas, sinyal kabulüyle uyumlu); 17.231 m oluklu ray",
                       "Beton/donatı hariç; 31.12.2026'ya kadar geçerli", "", "MEP bütçesine dahil değil",
                       "Makas adedi sinyalizasyon/katener metrajını teyit ediyor"], start=2):
    c = E.cell(row=_rr, column=j, value=v); c.border = BOX; c.alignment = WRAP
    if j == 5: c.number_format = EUR
E.row_dimensions[_rr].height = 45
E["A14"] = "TEKLİF DURUMU ÖZETİ (Gmail, 29.09–06.10.2026)"; E["A14"].font = BOLD
ozet_txt = [
    "Elektrik: ON Elektronik saat (81.600 €) ve YBS (171.000 €) teklifleri işlendi. Teknomaks (CCTV) ve Lev Müh. (yangın ihbar) çalışıyor; Best Transformer (trafo) dönmedi. Alfanar, Tema, EVA, DC Group vermiyor (Alfanar'dan RMU bütçesi istendi).",
    "Mekanik: Fiyatlı teklif yok. Ekura en geç 09.10 verecek; Protek (FM200) soru sordu. MET, Demta, Birleşim, Genç Müh. vermiyor.",
    "Asansör: 3 teklif (Schindler, TK, Emlift). Edoux verecek; Adakon (Orona) ithal ürünle bütçe verecek; KONE dönmedi.",
    "Sinyalizasyon: Mukan (AVLS) teklifi geldi; Point Link/CASCO kalem kalem teklifi (7,28 M€) win1 arşivinden alındı. Hugotek ve İntetra dönecek; Alstom ve Savronik vermiyor (bütçe istendi); Hanning & Kahl dönmedi.",
    "Elektrifikasyon: Mitaş katener direği teklifi (315.070 USD FCA Ankara + 45.000 USD toz boya opsiyonu) %20 nakliye/işçilik/overhead ile bütçeye işlendi; Best Transformer trafo için dönmedi; DeSA (seksiyon izolatörü), Erbakır (iletken), Kambeton (beton direk) sorularına cevap verildi; Doruk ve KAM vermiyor.",
    "Ulaşmayan adres: 26 (mailer-daemon). Ayrıntı: Teklif_Durumu sayfası.",
]
for k, t in enumerate(ozet_txt):
    c = E.cell(row=15 + k, column=1, value=t); c.alignment = WRAP
    E.merge_cells(start_row=15 + k, start_column=1, end_row=15 + k, end_column=14); E.row_dimensions[15 + k].height = 30
for col, w in zip("ABCDEFGHIJKLMN", (18, 22, 11, 18, 13, 6, 13, 14, 8, 26, 38, 38, 22, 34)):
    E.column_dimensions[col].width = w


# ---------------------------------------------------------------- YÖNTEM (metodoloji)
Y = wb.create_sheet("Yontem")
Y.sheet_view.showGridLines = False
Y.column_dimensions["A"].width = 4
for col, w in zip("BCDEFGHIJKL", (30, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16)):
    Y.column_dimensions[col].width = w
H1 = Font(bold=True, size=16, color="1F4E78"); H2 = Font(bold=True, size=12, color="FFFFFF")
FILL_SEC = PatternFill("solid", fgColor="1F4E78"); FILL_SOFT = PatternFill("solid", fgColor="F2F2F2")
Y["B2"] = "BİRİM FİYATLAR NASIL BELİRLENDİ? – YÖNTEM VE İZLENEBİLİRLİK"; Y["B2"].font = H1
Y["B3"] = ("Bu bütçedeki her kalem, cetveldeki miktarı ve izlenebilir bir fiyat kaynağıyla birlikte verilmiştir. "
           "Aşağıda fiyatların hangi veriden, hangi kurallarla ve hangi düzeltmelerle türetildiği adım adım açıklanmıştır.")
Y["B3"].alignment = WRAP; Y.merge_cells("B3:L3"); Y.row_dimensions[3].height = 32
_y = 5


def sec(title):
    global _y
    _y += 1
    Y.cell(row=_y, column=2, value=title).font = H2
    for j in range(2, 13):
        Y.cell(row=_y, column=j).fill = FILL_SEC
    _y += 1


def para(text, h=30):
    global _y
    c = Y.cell(row=_y, column=2, value=text); c.alignment = WRAP
    Y.merge_cells(start_row=_y, start_column=2, end_row=_y, end_column=12); Y.row_dimensions[_y].height = h
    _y += 1


def table(hdr, rows, fmt=None):
    global _y
    for j, h in enumerate(hdr, 2):
        c = Y.cell(row=_y, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
    Y.row_dimensions[_y].height = 30
    _y += 1
    for r_ in rows:
        for j, v in enumerate(r_, 2):
            c = Y.cell(row=_y, column=j, value=v); c.border = BOX; c.alignment = WRAP
            if fmt and j - 2 in fmt: c.number_format = fmt[j - 2]
        _y += 1


sec("1. FİYAT ÖNCELİK SIRASI (her kalem için bu sırayla)")
table(["Öncelik", "Fiyat türü", "Açıklama", "", "", "", "Renk"], [
    [1, "2026 TEKLİF", "Bu ihale için 29.09–06.10.2026 arasında alınan firma teklifleri (Schindler, TK Elevator, Emlift, Mukan Rail, ON Elektronik). Teklif kalem fiyatı doğrudan kullanılır.", "", "", "", "Yeşil"],
    [2, "GEÇMİŞ TEKLİF UYARLAMA", "Aynı tip/boyutta ekipman için geçmiş raylı sistem projelerinde alınmış gerçek teklifler (emsal). Kur ve enflasyonla 2026'ya taşınır; gerekirse montaj/boyut düzeltmesi yapılır.", "", "", "", "Mavi"],
    [3, "MÜHENDİSLİK TAHMİNİ", "Veritabanında karşılaştırılabilir emsal bulunmayan kalemler (tasarım, test, yazılım, inşaat payları vb.). 2026 Türkiye piyasa bilgisiyle tahmin edilir; her satırda gerekçe yazılıdır.", "", "", "", "Sarı"],
    ["–", "KAPSAM DIŞI (0)", "İdare cevaplarıyla (05.10.2026) kapsam dışı kalan kalemler; miktar 0, bilgi için satırda bırakılmıştır.", "", "", "", "Gri"]])
for rr_ in range(_y - 4, _y):
    Y.merge_cells(start_row=rr_, start_column=4, end_row=rr_, end_column=7); Y.row_dimensions[rr_].height = 42
    Y.cell(row=rr_, column=8).fill = TUR[["TEKLIF", "EMSAL", "TAHMIN", "SIFIR"][rr_ - (_y - 4)]][1]

sec("2. GEÇMİŞ TEKLİF VERİTABANI")
para("Kaynak: MEP Center proje arşivindeki raylı sistem projelerinin 'MALIYET / GELEN_TEKLIF' klasörlerinde bulunan tedarikçi teklifleri. "
     "Tekliflerdeki fiyat satırları tek tek okunmuş, her satır kaynak dosya yolu, firma, tarih, para birimi ve kapsamıyla (malzeme / malzeme+montaj) kaydedilmiştir.", 32)
table(["Gösterge", "Veritabanı (tümü)", "Bu bütçede kullanılan emsaller"], [
    ["Fiyat satırı", 6809, f"=COUNTA(Emsal_Kaynaklari!A5:A5000)"],
    ["Proje", 42, 28], ["Firma", 222, 103], ["Teklif yılları", "2008 – 2025", "ağırlıkla 2014 – 2025"],
    ["Tramvay / LRT satırı", 1352, 535], ["Metro satırı", 3273, 509], ["Diğer (YHT, banliyö, anahat, bina)", 2184, 139]], {1: "#,##0", 2: "#,##0"})
para("Başlıca tramvay/LRT referansları: Bursa T2 Kent Meydanı–Terminal (Haluk, MET, AKE, Delta, FER, AKT), İzmir Konak/Karşıyaka tramvayı (Siemens, Usluel, Hanning & Kahl, CONTEC, Aktif, Netaş), "
     "Kocaeli tramvayı (Sekaray, Özgür Mak., Uluhanlar), Konya Alaaddin–Adliye (Hanning & Kahl, ABB), Eminönü–Alibeyköy (Elektroline), Samsun LRT (Usluel, Balfour Beatty, Uskom). "
     "Metro referansları (İzmir Buca, Narlıdere, Kabataş–Mahmutbey, Kirazlı–Halkalı vb.) yalnız tramvay emsali yoksa ve ölçek düzeltmesiyle kullanılmıştır.", 46)

sec("3. FİYATI 2026'YA TAŞIMA ZİNCİRİ")
table(["Adım", "İşlem", "Kaynak"], [
    ["1", "Orijinal birim fiyat (teklifteki para birimi ile)", "Teklif dokümanı (dosya yolu Emsal_Kaynaklari sayfasında)"],
    ["2", "EUR'ya çevirme: Fiyat ÷ teklif günündeki kur (TRY, USD → EUR)", "ECB euro referans kurları (eurofxref-hist), teklif günü veya önceki iş günü"],
    ["3", "Enflasyon eskalasyonu: × HICP(Ağu-2026) ÷ HICP(teklif ayı)", "Euro Bölgesi HICP genel endeksi (ECB ICP.M.U2.N.000000.4.INX, 2015=100); Ağu-2026 = Ağu-2025 × 1,033 (Eurostat öncü %3,3)"],
    ["4", "Kapsam düzeltmesi: yalnız malzeme ise montaj payı eklenir", "Bölüm 5'teki oranlar"],
    ["5", "Boyut/teknoloji düzeltmesi (kVA, kW, kesit, yaş)", "Bölüm 5'teki kurallar"],
    ["6", "Emsallerin medyanı alınır (≥2 emsal); tek emsalde mevcut tahminle %50 harmanlanır", "Aykırı değerler ve iç maliyet tahminleri düşük ağırlıklı"]])
for rr_ in range(_y - 6, _y):
    Y.merge_cells(start_row=rr_, start_column=3, end_row=rr_, end_column=6); Y.merge_cells(start_row=rr_, start_column=7, end_row=rr_, end_column=12)
    Y.row_dimensions[rr_].height = 30

sec("4. ÖRNEK HESAPLAR (canlı formül – hücreleri değiştirerek kontrol edilebilir)")
HICP_HEDEF = 133.57723
_eh = ["Kalem", "Emsal (ID – proje – firma – tarih)", "Orijinal fiyat", "Para birimi", "Kur (1 EUR =)", "EUR (teklif günü)",
       "HICP teklif ayı", "HICP Ağu-2026", "Eskalasyon katsayısı", "EUR Ağu-2026", "Bütçe BF €"]
for j, h in enumerate(_eh, 2):
    c = Y.cell(row=_y, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
Y.row_dimensions[_y].height = 32
_y += 1
_ex = [("DC fider hücresi HSCB (Cer_Guc 188)", "R00877 – Bursa T2 Kent Meydanı–Terminal – Haluk Elektrik – 04.06.2015", 102250, "TRY", 3.0377, 100.72,
        "Haluk 44.641 / MET 43.769 / Kocaeli 74.194 → medyan 44.641 €"),
       ("Depo elektrikli makas motoru (Sinyal 230)", "R06521 – İzmir Konak tramvayı – Hanning & Kahl – 11.02.2014", 10920, "EUR", 1, 99.14,
        "H&K 14.713 / CONTEC 15.090 / Elektroline 9.121 → medyan 14.713 + %8 montaj = 15.890 €"),
       ("OG kablo 1×400 Al 36 kV (Cer_Guc 171)", "R00678 – İzmir Üçyol–Buca metrosu – Türk Prysmian – 03.05.2021", 14.43, "USD", 1.2044, 107.42,
        "Prysmian 14,90 + 2 € çekme; Haluk 17,29; MET 19,14 → medyan 17,29 €/m")]
for ad, em, fy, pb, kur, hicp, sonuc in _ex:
    r_ = _y
    vals = [ad, em, fy, pb, kur, f"=D{r_}/F{r_}", hicp, HICP_HEDEF, f"=I{r_}/H{r_}", f"=G{r_}*J{r_}", sonuc]
    for j, v in enumerate(vals, 2):
        c = Y.cell(row=r_, column=j, value=v); c.border = BOX; c.alignment = WRAP
        if j in (4, 7, 11): c.number_format = "#,##0.00"
        if j in (6, 8, 9): c.number_format = "0.0000"
        if j == 10: c.number_format = "0.0000"
    Y.cell(row=r_, column=11).font = BOLD
    Y.row_dimensions[r_].height = 45
    _y += 1
para("Örnek: Haluk'un 2015'teki 102.250 TL'lik DC fider hücresi, teklif günü kuru 3,0377 ile 33.660 €; Euro Bölgesi enflasyonu ile (×1,3262) Ağustos 2026'da 44.641 € eder. "
     "Aynı kalem için başka bağımsız tekliflerle birlikte medyan alınır; tek bir teklif bütçeyi belirlemez.", 32)

sec("5. DÜZELTME KURALLARI")
table(["Durum", "Uygulanan düzeltme", "Gerekçe"], [
    ["Emsal yalnız malzeme (montaj hariç)", "Kablo +%25–35 · tava +%40 · armatür/dedektör +%30 · ekipman +%8–20 · elektronik +%5–15", "Bütçe fiyatları montaj+test dahil (taşeron fiyatı)"],
    ["Farklı güç/boyut", "Trafo kVA^0,6 · VRF kW^0,8 · kompresör debi^0,7 · kablo kesit/bakır ağırlığı oranı", "Ölçek ekonomisi; aynı tipte en yakın boyut tercih edildi"],
    ["Eski elektronik (CCTV, IT, sunucu)", "2014 öncesi ×0,4–0,5 · 2015 ×0,85", "Elektronik fiyatları zamanla düşer; HICP eskalasyonu fazla gösterir"],
    ["Bakır yoğun kalemler (2012–2015 emsal)", "+%15–30", "2026 bakır fiyatı 2015'in belirgin üstünde"],
    ["Metro (1500 V DC, yeraltı) emsali", "Ölçek ve gerilim düzeltmesi, ancak tramvay emsali yoksa", "Metro ekipmanı tramvaya göre pahalıdır"],
    ["Tek emsal", "Mevcut tahminle %50 harman ('REF-derin(1)')", "Tek veriye aşırı güvenmemek için"],
    ["İç maliyet / keşif (İDİS, MET keşfi vb.)", "Düşük ağırlık; gerçek tedarikçi teklifi varsa kullanılmaz", "Tedarikçi teklifi piyasa fiyatını daha iyi yansıtır"]])
for rr_ in range(_y - 7, _y):
    Y.merge_cells(start_row=rr_, start_column=3, end_row=rr_, end_column=7); Y.merge_cells(start_row=rr_, start_column=8, end_row=rr_, end_column=12)
    Y.row_dimensions[rr_].height = 32

sec("6. MİKTARLAR")
para("Miktarlar idarenin birim fiyat cetveli, ihale projeleri ve şartnamelerden çıkarılan RFQ (teklif talebi) cetvellerinden alınmıştır. "
     "Tedarikçilere gönderilen cetvellerde bilinçli olarak yukarıdan tutulan metraj payları (uzunluklarda %10 fire; Mekanik/Elektrik set alt kalemlerinde dağıtık malzemeye %30) bu bütçede geri alınmıştır (Varsayımlar'da açılıp kapatılabilir). "
     "İdarenin 05.10.2026 tarihli açıklama cevapları uygulanmıştır (Idare_Duzeltme sayfası): 14 araç, tüm makaslar motorlu, ana hatta lente yok, kavşak TSKP kapsam dışı, hat 6,44 km, OG ring 7.964 m, fiber 24/8 core SM, istasyon UPS 20 dk vb.", 58)

sec("7. KONTROLLER")
para("• Her kalem tek tek eşleştirilmiş; emsal ID'leri ilgili satırın 'Fiyat kaynağı / emsal' sütununda ve Emsal_Kaynaklari sayfasında yer alır.  "
     "• Disiplin toplamları sistem bazlı ölçütlerle (hat-km, makas başı, TM başı) karşılaştırılmıştır (Ozet ve Teklifler).  "
     "• Gelen 2026 teklifleri bütçe karşılığıyla kıyaslanmıştır (Teklif_Degerlendirme): Asansör ±%16, AVLS +%3, saat/YBS ±%6 içinde.  "
     "• Tüm tutarlar formüllüdür; kur, risk payı ve metraj payı Varsayimlar sayfasından değiştirilebilir.", 62)

sec("8. SINIRLAMALAR")
para("Emsal bulunamayan kalemler (toplamın ~%20'si) mühendislik tahminidir; tedarikçi teklifleri geldikçe bu kalemler teklif fiyatına dönüştürülecektir. "
     "Euro Bölgesi enflasyonu Türkiye'deki yerel işçilik maliyet artışını tam yansıtmayabilir. Fiyatlar KDV, gümrük ve bakım hariçtir.", 32)

# ---------------------------------------------------------------- EMSAL KAYNAKLARI
K = wb.create_sheet("Emsal_Kaynaklari")
K["A1"] = "EMSAL KAYNAKLARI – bu bütçede kullanılan geçmiş teklif satırları (her satır kaynak teklif dosyasına izlenebilir)"
K["A1"].font = Font(bold=True, size=13)
K["A2"] = "EUR (Ağu-2026) = Orijinal fiyat ÷ ECB kuru (teklif günü) × HICP(Ağu-2026)/HICP(teklif ayı). Kullanıldığı kalem sayısı: bu emsale atıf yapan bütçe satırı adedi."
K["A2"].alignment = WRAP; K.merge_cells("A2:N2"); K.row_dimensions[2].height = 28
_used = collections.Counter()
for _r in REVIZE.values():
    for x in (_r.get("ref_idler") or "").replace(",", ";").split(";"):
        if x.strip(): _used[x.strip()] += 1
_kh = ["Emsal ID", "Proje", "Hat tipi", "Firma", "Teklif tarihi", "Kalem (teklifteki ifade)", "Birim", "Orijinal BF",
       "Para birimi", "Kapsam", "EUR (Ağu-2026)", "Eşleşen URF poz", "Kullanıldığı kalem sayısı", "Not"]
for j, h in enumerate(_kh, 1):
    c = K.cell(row=4, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
_k = 5
for _r in csv.DictReader(open(os.path.join(MEP_DIR, "veri_referans.csv"), encoding="utf-8")):
    if _r["ID"] not in _used: continue
    def _f(v):
        try: return float(v)
        except (TypeError, ValueError): return v
    vals = [_r["ID"], _r["Proje"], _r["Hat tipi"], _r["Firma"], (_r["Teklif tarihi"] or "")[:10], _r["Kalem (teklif)"], _r["Birim (teklif)"],
            _f(_r["Birim fiyat (orijinal)"]), _r["Para birimi"], _r["Kapsam"], _f(_r["EUR (Ağu-2026)"]), _r["URF poz"], _used[_r["ID"]], _r["Not"]]
    for j, v in enumerate(vals, 1):
        c = K.cell(row=_k, column=j, value=v)
        if j in (8, 11): c.number_format = "#,##0.00"
    _k += 1
K.auto_filter.ref = f"A4:N{_k-1}"; K.freeze_panes = "B5"
for col, w in zip("ABCDEFGHIJKLMN", (10, 26, 9, 24, 11, 60, 8, 12, 8, 9, 13, 10, 10, 50)):
    K.column_dimensions[col].width = w

# ---------------------------------------------------------------- Teklif durumu (Gmail)
G = wb.create_sheet("Teklif_Durumu")
G["A1"] = "TEDARİKÇİ DÖNÜŞLERİ – serhat@mepcenter.com.tr Gmail taraması (29.09–06.10.2026) ve okunan teklif ekleri"
G["A1"].font = Font(bold=True, size=12)
_gp = os.path.join(MEP_DIR, "gmail_teklif_durumu.csv")
_cols = ["tarih", "firma", "disiplin", "durum", "kapsam_kalemler", "ekler", "not"]
for j, h in enumerate(["Tarih", "Firma", "Disiplin", "Durum", "Kapsam", "Ekler", "Not"], 1):
    c = G.cell(row=3, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX
_i = 4
for _r in sorted(csv.DictReader(open(_gp, encoding="utf-8-sig")), key=lambda x: (x["disiplin"], x["durum"])):
    for j, k in enumerate(_cols, 1):
        c = G.cell(row=_i, column=j, value=_r[k]); c.alignment = WRAP; c.border = BOX
    _i += 1
_i += 2
G.cell(row=_i, column=1, value="EKLERDEN OKUNAN TEKLİF KALEMLERİ").font = Font(bold=True, size=12)
_i += 1
_kc = ["firma", "tarih", "disiplin", "sira", "poz", "kalem", "birim", "miktar", "malzeme_bf", "iscilik_bf", "para_birimi", "toplam", "not"]
for j, h in enumerate(_kc, 1):
    c = G.cell(row=_i, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX
_i += 1
for _r in csv.DictReader(open(os.path.join(MEP_DIR, "gelen_teklif_kalemleri.csv"), encoding="utf-8-sig")):
    for j, k in enumerate(_kc, 1):
        v = _r.get(k, "")
        try:
            v = float(v) if k in ("miktar", "malzeme_bf", "iscilik_bf", "toplam") and v not in ("", None) else v
        except ValueError:
            pass
        c = G.cell(row=_i, column=j, value=v); c.alignment = WRAP; c.border = BOX
    _i += 1
for col, w in zip("ABCDEFGHIJKLM", (11, 30, 12, 14, 40, 40, 50, 9, 12, 12, 9, 14, 40)):
    G.column_dimensions[col].width = w

# ---------------------------------------------------------------- İdare düzeltmeleri
D = wb.create_sheet("Idare_Duzeltme")
D["A1"] = "İDARE CEVAPLARI (05.10.2026) – BU BÜTÇEYE UYGULANAN DÜZELTMELER"
D["A1"].font = Font(bold=True, size=12)
dh = ["No", "Konu", "RFQ kabulü", "İdare cevabı", "Bütçeye etkisi", "Sayfa"]
for j, h in enumerate(dh, 1):
    c = D.cell(row=3, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX
drows = [
    (1, "Kavşak sinyal (229)", "TSKP + 64 trafik lambası + 64 direk + 2.695 m kablo dahil", "TSKP ve lambalar kapsam dışı; irtibat kablolaması kapsamda", "Düşüldü (TSP, lup, arayüz kablosu kalır)", "Sinyal"),
    (2, "Araç adedi (231, 233)", "15 araç", "14 araç; araçlar ayrı ihale", "Araç başı kalemler 14'e indirildi", "Sinyal"),
    (3, "Ana hat makasları", "12 motorlu + 4 manuel", "Tüm makaslar motorlu", "+4 motor, +çubuk seti, +1 SKP (temkinli); manuel kalemler sıfır", "Sinyal"),
    (4, "Depo makasları", "20 motorlu + 20 manuel", "Tamamı motorlu", "+20 motor, +20 lamba, +16 dedektör, kablolar ×2; manuel sıfır", "Sinyal"),
    (6, "Ana hat lentesi", "66 lente + 68 temel", "Kullanılmayacak", "Lente teçhizatı ve temelleri düşüldü", "Katener"),
    (7, "Depo direkleri", "221 setinde 77 direk + temeller", "Cetvel direk kalemleri + sıra 13", "Depo direk/temel kalemleri düşüldü (çift sayım)", "Katener"),
    (11, "İstasyon UPS", "2 saat", "İstasyon 20 dk; TM 2 saat", "Bu bütçede yalnız TM UPS'leri var (2 saat korundu)", "Cer_Guc"),
    (17, "Mevcut sistem entegrasyonu", "Dahil", "Mevcut sistem yok", "Düşüldü", "Sinyal"),
    (18, "Hat uzunluğu", "6,56 km", "6,44 km", "Hat boyu iletken/kablolar × 0,9817", "Katener, Sinyal"),
    (21, "OG ring (170)", "7.000 m", "Tüm kesitler 7.964 m", "Kablo, muf, kelepçe güzergah oranında artırıldı", "Cer_Guc"),
    (22, "TEİAŞ kablosu (171)", "4 kablo/güzergah, 35.424 m", "Aynı", "Değişiklik yok", "Cer_Guc"),
    ("—", "İç ihtiyaç trafoları", "Belirtilmemişti", "Cu/Cu sargı zorunlu", "250 / 2000 kVA trafolar Cu/Cu fiyatlandı", "Cer_Guc"),
    ("—", "Sıra 228", "Tasarım", "Yalnız tasarım; ekipman 229–232", "Uyumlu", "Sinyal"),
    (26, "Kabin splitleri (6001.A–F)", "İstasyon mekaniğinde", "Sıra 143 kabin fiyatında", "Güvenlik kabini split kalemleri sıfırlandı", "Mekanik"),
    (11, "İstasyon UPS aküsü", "2 saat", "20 dk; Göbeklitepe 10 kVA", "İstasyon UPS akü kalemleri 20 dk'ya göre fiyatlandı", "Elektrik_AG"),
    (24, "İstasyon topraklama elektrodu", "Som bakır (112 adet)", "Galvaniz köşebent", "Elektrot birim fiyatı galvaniz köşebent", "Elektrik_AG"),
    (13, "Hatboyu fiber", "2×96 SM + 24 MM", "24 ve 8 core SM", "Fiber kabloları 24/8 core SM olarak fiyatlandı", "Haberlesme"),
    (16, "Saat sistemi", "4 set (depo)", "Cevap yok", "Kabul korundu", "Haberlesme"),
    (14, "Turnike adedi", "Cetvel 27 + 19", "Onaylı mimari projeler", "Cetvel adedi kullanıldı; mimariden sayılınca güncellenmeli", "Haberlesme"),
    ("—", "Garanti / yedek parça", "—", "24 ay; 2 yıllık yedek parça sıra 384'ten", "Katener test kalemine yedek parça payı dahil; sinyal yedekleri sıra 384'te", "—"),
]
for i, r in enumerate(drows, start=4):
    for j, v in enumerate(r, 1):
        c = D.cell(row=i, column=j, value=v); c.border = BOX; c.alignment = WRAP
for col, w in zip("ABCDEF", (6, 26, 38, 40, 55, 14)):
    D.column_dimensions[col].width = w

# ---------------------------------------------------------------- Özet
O = wb.create_sheet("Ozet", 0)
O["A1"] = "ŞANLIURFA HRS 1. ETAP – MEP BÜTÇE ÇALIŞMASI (ELEKTRİK, MEKANİK, ASANSÖR, SİNYALİZASYON, ELEKTRİFİKASYON)"
O["A1"].font = Font(bold=True, size=13)
O["A2"] = ("İKN 2026/1327584 • Teklif sahibi: ÖZVER İNŞAAT A.Ş. • Hazırlayan: MEP Center • 06.10.2026 • "
           "EUR, KDV hariç, montaj+test+devreye alma dahil (taşeron fiyatı), Şanlıurfa şantiye teslim. "
           "Miktarlar RFQ cetvelleri + idare cevapları (05.10.2026) ile düzeltilmiştir.")
O["A2"].alignment = WRAP; O.merge_cells("A2:K2"); O.row_dimensions[2].height = 36
oh = ["Disiplin", "Cetvel sıraları", "Kalem bazlı bütçe (düzeltilmiş) EUR", "Risk payı %", "Önerilen bütçe EUR",
      "Önerilen bütçe USD", "Önerilen bütçe TL", "RFQ miktarlarıyla (düzeltmesiz) EUR", "Referans / teklif kıyası EUR",
      "Kıyas kaynağı", "Açıklama"]
for j, h in enumerate(oh, 1):
    c = O.cell(row=4, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
O.row_dimensions[4].height = 45
sub = [  # (disiplin, alt kalem, sıralar, tutar, risk, rfq, kıyas, kıyas kaynağı, açıklama)
    ("1 ELEKTRİK", "AG dağıtım, AG kablolar, iç tesisat-aydınlatma, UPS, yangın ihbar, topraklama", "180–186, 190–196, 198–199, 211–218, 322–342",
     EA_TOT, RISK['ELK_AG'], EA_RFQ, None, "", "İstasyon/depo ADP, AG besleme kabloları, aydınlatma, UPS'ler, yangın ihbar"),
    ("1 ELEKTRİK", "Kontrol ve haberleşme (fiber, telefon, telsiz, anons, CCTV, saat, erişim, SCADA, YBS, turnike)", "236–321",
     HB_TOT, RISK['HAB'], HB_RFQ, "=Teklifler!F14", "Referans kalem bazlı", "ON Elektronik (saat+YBS) ve Teknomaks (CCTV) teklifleri ekte/bekleniyor"),
    ("2 MEKANİK", "Isıtma-soğutma, havalandırma, yangın söndürme, drenaj, sıhhi tesisat, basınçlı hava", "159–168, 343–363",
     MK_TOT, RISK['MEKANIK'], MK_RFQ, None, "", "Asansör hariç (ayrı disiplin)"),
    ("3 ASANSÖR", "13 asansör (12 üst geçit 1000 kg + 1 idari bina 800 kg)", "364–365",
     AS_TOT, RISK['ASANSOR'], AS_RFQ, "=MIN(Teklifler!F4:F6)", "En düşük teklif (Emlift, sapmalı)", "3 teklifin medyanı (Schindler 480.000 USD, TK 414.200 EUR, Emlift 19,5 M TL); bakım hariç"),
    ("4 SİNYALİZASYON", "Hat boyu + depo sinyalizasyon, araç üstü, merkez, araç takip (AVLS)", "228–235",
     SN_TOT, RISK['SINYAL'], SN_RFQ, "=Teklifler!F8", "Sistem bazlı ref. (makas başı)", "AVLS 233–235 Mukan Rail teklifiyle; Point Link 7,28 M€ kıyas dışı (kalem dökümü PointLink_Kiyas)"),
    ("5 ELEKTRİFİKASYON", "Güç temini ve cer gücü (OG ring, TEİAŞ bağlantısı, 34,5 kV hücreler, 5 cer TM, kaçak akım)", "169–179, 187–189, 197, 200–210, 219, 227",
     CG_TOT, RISK['CER'], CG_RFQ, "=Teklifler!F12", "Sistem bazlı ref. (5 TM; yalnız OG+trafo+DC)", ""),
    ("5 ELEKTRİFİKASYON", "Katener (hat boyu, depo, direkler)", "220–226",
     KT_TOT, RISK['KATENER'], KT_RFQ, "=Teklifler!F10", "Sistem bazlı ref. (km başı)", "Direk temelleri inşaatta; ana hatta lente yok"),
]
DIS = ["1 ELEKTRİK", "2 MEKANİK", "3 ASANSÖR", "4 SİNYALİZASYON", "5 ELEKTRİFİKASYON"]
oh = ["Disiplin", "Kapsam", "Kalem bazlı bütçe EUR", "Risk payı EUR", "Önerilen bütçe EUR",
      "Önerilen bütçe USD", "Önerilen bütçe TL", "Pay %", "RFQ cetvel miktarlarıyla (şişirmeli) EUR", "Referans / teklif kıyası EUR",
      "Teklife dayanan %", "Geçmiş teklif uyarlaması %", "Mühendislik tahmini %"]
for j, h in enumerate(oh, 1):
    c = O.cell(row=4, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
O.row_dimensions[4].height = 45
r0 = 5
rT = r0 + len(DIS)
rS0 = rT + 4          # alt kırılım tablosu başlığı
O.cell(row=rS0 - 1, column=1, value="ALT KIRILIM (disiplin içi)").font = Font(bold=True, size=12)
sh2 = ["Disiplin", "Alt kalem", "Cetvel sıraları", "Kalem bazlı EUR", "Risk %", "Önerilen EUR", "RFQ miktarlarıyla EUR",
       "Kıyas EUR", "Kıyas kaynağı", "Açıklama", "2026 teklifine dayanan EUR", "Geçmiş teklif uyarlaması EUR", "Mühendislik tahmini EUR"]
for j, h in enumerate(sh2, 1):
    c = O.cell(row=rS0, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
for i, (d, ad, sira, tot, risk, rfq, kiyas, ksrc, acik) in enumerate(sub):
    r = rS0 + 1 + i
    shn = tot.split("'")[1]
    vals = [d, ad, sira, f"={tot}", f"={risk}", f"=D{r}*(1+E{r})", f"={rfq}", kiyas, ksrc, acik,
            f"={TYPE_TOT[shn]['TEKLIF']}", f"={TYPE_TOT[shn]['EMSAL']}", f"={TYPE_TOT[shn]['TAHMIN']}"]
    for j, v in enumerate(vals, 1):
        c = O.cell(row=r, column=j, value=v); c.border = BOX; c.alignment = WRAP
        if j in (4, 6, 7, 8, 11, 12, 13): c.number_format = EUR
        if j == 5: c.number_format = "0%"
rS1, rS2 = rS0 + 1, rS0 + len(sub)
kapsam = {"1 ELEKTRİK": "AG tesisat, aydınlatma, yangın ihbar, topraklama, kontrol-haberleşme, SCADA",
          "2 MEKANİK": "HVAC, yangın söndürme, drenaj, sıhhi tesisat, basınçlı hava",
          "3 ASANSÖR": "13 asansör", "4 SİNYALİZASYON": "Sinyalizasyon + araç takip (AVLS)",
          "5 ELEKTRİFİKASYON": "Güç temini/cer gücü + katener"}
for i, d in enumerate(DIS):
    r = r0 + i
    rng = lambda col: f"SUMIF($A${rS1}:$A${rS2},$A{r},{col}${rS1}:{col}${rS2})"
    vals = [d, kapsam[d], "=" + rng("D"), f"=E{r}-C{r}", "=" + rng("F"), f"=E{r}*{P_USD}", f"=E{r}*{P_TRY}",
            f"=E{r}/$E${rT}", "=" + rng("G"), "=" + rng("H"),
            f"=IF(C{r}=0,0,{rng('K')}/C{r})", f"=IF(C{r}=0,0,{rng('L')}/C{r})", f"=IF(C{r}=0,0,{rng('M')}/C{r})"]
    for j, v in enumerate(vals, 1):
        c = O.cell(row=r, column=j, value=v); c.border = BOX; c.alignment = WRAP
        if j in (3, 4, 5, 6, 7, 9, 10): c.number_format = EUR
        if j in (8, 11, 12, 13): c.number_format = "0%"
    O.cell(row=r, column=1).font = BOLD
O.cell(row=rT, column=1, value="TOPLAM MEP").font = BOLD
for col in "CDEFGIJ":
    c = O[f"{col}{rT}"]; c.value = f"=SUM({col}{r0}:{col}{rT-1})"; c.number_format = EUR; c.font = BOLD
O[f"H{rT}"] = f"=SUM(H{r0}:H{rT-1})"; O[f"H{rT}"].number_format = "0.0%"
for col in "KLM":
    c = O[f"{col}{rT}"]; c.value = f"=SUMPRODUCT(C{r0}:C{rT-1},{col}{r0}:{col}{rT-1})/C{rT}"; c.number_format = "0%"; c.font = BOLD
for j in range(1, 14):
    O.cell(row=rT, column=j).fill = FILL_TOT; O.cell(row=rT, column=j).border = BOX
FILL_HL = PatternFill("solid", fgColor="FCE4D6"); FILL_HLT = PatternFill("solid", fgColor="C55A11")
THICK = Side(style="medium", color="C55A11"); HBOX = Border(left=THICK, right=THICK, top=THICK, bottom=THICK)


def hl_title(row, text, ncol=8):
    c = O.cell(row=row, column=1, value=text); c.font = Font(bold=True, size=12, color="FFFFFF")
    for j in range(1, ncol + 1):
        O.cell(row=row, column=j).fill = FILL_HLT
    O.row_dimensions[row].height = 20


_ib = rS2 + 2
# --- Vurgu 1: idare cevabıyla kapsam dışı kalanlar
hl_title(_ib, "▶ KAPSAM DIŞI KALEMLER – İdare cevaplarıyla (05.10.2026) bütçeden düşülen kalemlerin RFQ'daki değeri")
_h = ["Disiplin sayfası", "Düşülen başlıca kalemler", "", "", "RFQ birim fiyatlarıyla değer €"]
for j, h in enumerate(_h, 1):
    c = O.cell(row=_ib + 1, column=j, value=h); c.font = BOLD; c.fill = FILL_HL; c.border = BOX
_kd = [("Sinyal", "Kavşak TSKP, trafik lambaları/direkleri/kabloları; manuel makas mekanizmaları; mevcut depo kontrol merkezi entegrasyonu"),
       ("Katener", "Ana hat ankraj lentesi + 68 lente temeli; depo direkleri ve temelleri (cetvel direk kalemleriyle çift sayım)"),
       ("Mekanik", "Güvenlik kabini splitleri (sıra 143 modüler kabin fiyatında)"),
       ("Elektrik_AG", "Kavşak TSKP beslemeleri"),
       ("Haberlesme", "Mevcut sistem entegrasyonları (mevcut sistem yok)")]
for k, (shn, txt) in enumerate(_kd):
    r_ = _ib + 2 + k
    O.cell(row=r_, column=1, value=shn); O.cell(row=r_, column=2, value=txt).alignment = WRAP
    O.merge_cells(start_row=r_, start_column=2, end_row=r_, end_column=4)
    c = O.cell(row=r_, column=5, value=f"={TYPE_TOT[shn]['SIFIR']}"); c.number_format = EUR
    for j in range(1, 6): O.cell(row=r_, column=j).border = BOX
    O.row_dimensions[r_].height = 30
_kt = _ib + 2 + len(_kd)
O.cell(row=_kt, column=1, value="Toplam düşülen").font = BOLD
c = O.cell(row=_kt, column=5, value=f"=SUM(E{_ib+2}:E{_kt-1})"); c.number_format = EUR; c.font = BOLD
O.cell(row=_kt + 1, column=1, value=("Ayrıca RFQ'daki bilinçli metraj payları (%10 fire, dağıtık malzemede %30) bütçeden geri alınmıştır; "
                                    "etkisi: 'RFQ cetvel miktarlarıyla' sütunu − 'Kalem bazlı bütçe'.")).alignment = WRAP
O.merge_cells(start_row=_kt + 1, start_column=1, end_row=_kt + 1, end_column=8); O.row_dimensions[_kt + 1].height = 28

# --- Vurgu 2: yüklenici kapsamındaki depo ekipmanları (MEP dışı) – tahmini
_db = _kt + 3
hl_title(_db, "▶ KAPSAM DIŞI EKİPMANLAR – Yüklenici kapsamındaki depo ekipmanları (MEP paketlerinde yok) – bilgi amaçlı tahmini bütçe")
_h = ["Ekipman", "Açıklama", "Miktar", "Birim fiyat €", "Tutar €", "Fiyat türü"]
for j, h in enumerate(_h, 1):
    c = O.cell(row=_db + 1, column=j, value=h); c.font = BOLD; c.fill = FILL_HL; c.border = BOX
DEPO_EKIP = [("Köprülü vinç 7,5 t", "Atölye, ~20 m açıklık, ray+yürüyüş yolu, montaj dahil", 1, 55000),
             ("Köprülü vinç 1 t", "Atölye yardımcı vinç / monoray", 1, 15000),
             ("Araç kaldırma lifti 11 t", "Senkron kolon lift (10 + 2 yedek), kumanda dahil", 12, 16000),
             ("Katener bakım aracı", "Karayolu-demiryolu, kaldırma platformlu, ölçüm donanımlı", 1, 650000),
             ("Manevra aracı (shunter)", "Karayolu-demiryolu tip, tramvay çekebilir", 1, 400000)]
for k, (ad, ac, q, bf) in enumerate(DEPO_EKIP):
    r_ = _db + 2 + k
    vals = [ad, ac, q, bf, f"=C{r_}*D{r_}", "PİYASA TAHMİNİ (veritabanında emsal yok)"]
    for j, v in enumerate(vals, 1):
        c = O.cell(row=r_, column=j, value=v); c.border = BOX; c.alignment = WRAP
        if j in (4, 5): c.number_format = EUR
    O.cell(row=r_, column=6).fill = TUR["TAHMIN"][1]
_dt = _db + 2 + len(DEPO_EKIP)
O.cell(row=_dt, column=1, value="Toplam (bilgi)").font = BOLD
c = O.cell(row=_dt, column=5, value=f"=SUM(E{_db+2}:E{_dt-1})"); c.number_format = EUR; c.font = BOLD
O.cell(row=_dt + 1, column=1, value="İdare cevabı: depo ekipmanları (1 t + 7,5 t köprülü vinç, 12 × 11 t lift, katener bakım aracı, shunter vb.) yüklenici kapsamındadır; MEP teklif paketlerine dahil edilmemiştir. Rakamlar teklif alınana kadar mertebe göstergesidir.").alignment = WRAP
O.merge_cells(start_row=_dt + 1, start_column=1, end_row=_dt + 1, end_column=8); O.row_dimensions[_dt + 1].height = 28

# --- Vurgu 3: Rayba (ihale geneli, MEP dışı)
_ib = _dt + 3
hl_title(_ib, "▶ İHALE GENELİ – MEP DIŞI GELEN TEKLİF: RAYBA YAPI (demiryolu üstyapı) – MEP toplamına dahil değil")
for j, h in enumerate(["Firma", "Teklif", "", "", "EUR", "USD", "TL"], 1):
    c = O.cell(row=_ib + 1, column=j, value=h); c.font = BOLD; c.fill = FILL_HL; c.border = BOX
for k, (t, ref) in enumerate(IHALE_GENEL):
    r_ = _ib + 2 + k
    O.cell(row=r_, column=1, value="Rayba Yapı"); O.cell(row=r_, column=2, value=t)
    O.merge_cells(start_row=r_, start_column=2, end_row=r_, end_column=4)
    for j, f in ((5, f"={ref}"), (6, f"=E{r_}*{P_USD}"), (7, f"=E{r_}*{P_TRY}")):
        c = O.cell(row=r_, column=j, value=f); c.number_format = EUR; c.font = Font(bold=True, color="C55A11")
    for j in range(1, 8): O.cell(row=r_, column=j).border = BOX
_rt = _ib + 2 + len(IHALE_GENEL)
O.cell(row=_rt, column=1, value=("Rayba teklifi 42×R50 + 2×R100 makas + 3 kruvazman (= 56 makas) ile sinyal/katener makas kabulünü teyit ediyor. "
                                 "S-LINE kapsülleri hat döşeme fiyatında olabilir – çift sayım kontrolü; beton/donatı hariç. Ayrıntı: Ihale_Geneli_Bilgi.")).alignment = WRAP
O.merge_cells(start_row=_rt, start_column=1, end_row=_rt, end_column=8); O.row_dimensions[_rt].height = 30
rT = _rt + 1   # aşağıdaki döküm için

# Ana kalem dökümü
rB = rT + 3
O.cell(row=rB - 1, column=1, value="CETVEL SIRASI BAZINDA DÖKÜM (risk payı hariç, EUR)").font = Font(bold=True, size=12)
for j, h in enumerate(["Disiplin", "Sıra", "Kalem", "Tutar EUR"], 1):
    c = O.cell(row=rB, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX
rr = rB + 1
for disip, groups, mains, sh in (("1 Elektrik – AG/aydınlatma/yangın", elk_ag, EA_MAIN, "Elektrik_AG"),
                                 ("1 Elektrik – haberleşme/SCADA", hab, HB_MAIN, "Haberlesme"),
                                 ("2 Mekanik", mekanik, MK_MAIN, "Mekanik"), ("3 Asansör", asansor, AS_MAIN, "Asansor"),
                                 ("4 Sinyalizasyon", sinyal, SN_MAIN, "Sinyal"),
                                 ("5 Elektrifikasyon – güç temini/cer", cer, CG_MAIN, "Cer_Guc"),
                                 ("5 Elektrifikasyon – katener", katener, KT_MAIN, "Katener")):
    for g in groups:
        O.cell(row=rr, column=1, value=disip)
        O.cell(row=rr, column=2, value=g[0])
        O.cell(row=rr, column=3, value=g[2])
        c = O.cell(row=rr, column=4, value=f"='{sh}'!{mains[g[0]]}"); c.number_format = EUR
        for j in range(1, 5): O.cell(row=rr, column=j).border = BOX
        rr += 1

rN = rr + 2
notes = [
    "NOTLAR",
    "1. Kalem bazlı bütçe: RFQ cetvellerindeki alt kalemler × birim fiyat. Birim fiyat önceliği: 2026 teklifi > geçmiş teklif referansı (EM_Butce_Tahmini, HICP ile Ağu-2026'ya taşınmış, tramvay/LRT öncelikli) > mühendislik tahmini. Her satırda kaynak yazılıdır.",
    "2. İdare cevaplarına göre düzeltmeler Idare_Duzeltme sayfasında; değişen miktarlar disiplin sayfalarında turuncu işaretlidir. 'RFQ miktarlarıyla' sütunu aynı birim fiyatlarla düzeltmesiz tutarı gösterir.",
    "3. Risk payı, eksik teklif ve öngörü miktarları için Varsayımlar sayfasından değiştirilebilir. Önerilen bütçe = kalem bazlı × (1 + risk payı).",
    "4. Kapsam dışı: katener direk temelleri (sıra 13, inşaat), depo ekipmanları (vinç, lift, katener bakım aracı – yüklenici), modüler kabinler ve kabin splitleri (sıra 143), asansör kuyusu; yürüyen merdiven ihalede yok. Kavşak TSKP/trafik lambaları kapsam dışı.",
    "5. Sinyalizasyonda ayrı proje yoktur; miktarlar şematik paftalardan öngörülmüştür. Point Link/CASCO teklifi (7.281.784 € DAP, gümrük ve KDV hariç) kalem kalem PointLink_Kiyas sayfasında idare cevaplarına göre uyarlanmıştır; bütçede kullanılmamış, üst sınır senaryosu olarak raporlanmıştır.",
    "6. Kur: EUR/USD ve EUR/TRY Varsayımlar sayfasındadır (Eylül 2026 sonu piyasa değerleri); teklif günü kuruyla güncellenmelidir.",
    "7. Gelen yeni teklifler (Mitaş, Erbakır, DeSA, Best Transformer, Contirail vb.) ilgili satırın birim fiyatına yazılarak bütçe güncellenebilir.",
]
for i, t in enumerate(notes):
    c = O.cell(row=rN + i, column=1, value=t); c.alignment = WRAP
    O.merge_cells(start_row=rN + i, start_column=1, end_row=rN + i, end_column=11)
    O.row_dimensions[rN + i].height = 15 if i == 0 else 32
O.cell(row=rN, column=1).font = BOLD
for col, w in zip("ABCDEFGHIJKLM", (24, 48, 18, 16, 18, 16, 18, 10, 18, 18, 30, 16, 16)):
    O.column_dimensions[col].width = w
O.freeze_panes = "A5"


# ---------------------------------------------------------------- Özet: KPI kartları + grafikler
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
for col, w in zip("OPQRS", (30, 18, 18, 18, 4)):
    O.column_dimensions[col].width = w
_kpi = [("TOPLAM MEP ÖNERİLEN BÜTÇE (EUR)", f"=E{r0+len(DIS)}", EUR),
        ("USD karşılığı", f"=F{r0+len(DIS)}", EUR), ("TL karşılığı", f"=G{r0+len(DIS)}", EUR),
        ("Fiyatlandırılan kalem sayısı", ITEM_COUNT[0], "#,##0"),
        ("Teklif + geçmiş teklif emsaline dayanan pay", f"=K{r0+len(DIS)}+L{r0+len(DIS)}", "0%")]
O["O4"] = "BÜTÇE GÖSTERGELERİ"; O["O4"].font = Font(bold=True, color="FFFFFF", size=12)
for j in range(15, 18): O.cell(row=4, column=j).fill = FILL_H
for k, (lab, f, nf) in enumerate(_kpi):
    r_ = 5 + k
    O.cell(row=r_, column=15, value=lab).font = BOLD
    c = O.cell(row=r_, column=16, value=f); c.number_format = nf; c.font = Font(bold=True, size=12, color="1F4E78")
    for j in (15, 16): O.cell(row=r_, column=j).border = BOX
# grafik verisi
_gd = 12
O.cell(row=_gd, column=15, value="Grafik verisi (EUR, risk hariç)").font = BOLD
for j, h in enumerate(["Disiplin", "2026 teklif", "Geçmiş teklif uyarlama", "Mühendislik tahmini"], 15):
    c = O.cell(row=_gd + 1, column=j, value=h); c.font = F_H; c.fill = FILL_H
for i, d in enumerate(DIS):
    r_ = _gd + 2 + i
    O.cell(row=r_, column=15, value=d)
    for j, col in zip((16, 17, 18), "KLM"):
        c = O.cell(row=r_, column=j, value=f"=SUMIF($A${rS1}:$A${rS2},$O{r_},{col}${rS1}:{col}${rS2})"); c.number_format = EUR
ch = BarChart(); ch.type = "bar"; ch.grouping = "stacked"; ch.overlap = 100
ch.title = "Disiplin bazında bütçe ve fiyat kaynağı (EUR)"; ch.y_axis.title = "EUR"; ch.height = 9; ch.width = 18
data = Reference(O, min_col=16, max_col=18, min_row=_gd + 1, max_row=_gd + 1 + len(DIS))
cats = Reference(O, min_col=15, min_row=_gd + 2, max_row=_gd + 1 + len(DIS))
ch.add_data(data, titles_from_data=True); ch.set_categories(cats)
for ser, colr in zip(ch.series, ("70AD47", "5B9BD5", "FFC000")):
    ser.graphicalProperties.solidFill = colr; ser.graphicalProperties.line.solidFill = colr
O.add_chart(ch, f"O{_gd + 3 + len(DIS)}")
pc = PieChart(); pc.title = "Disiplin payları (önerilen bütçe)"; pc.height = 8; pc.width = 12
pc.add_data(Reference(O, min_col=5, min_row=r0 - 1, max_row=r0 + len(DIS) - 1), titles_from_data=True)
pc.set_categories(Reference(O, min_col=1, min_row=r0, max_row=r0 + len(DIS) - 1))
pc.dataLabels = DataLabelList(); pc.dataLabels.showPercent = True
O.add_chart(pc, f"O{_gd + 23 + len(DIS)}")
O.sheet_view.showGridLines = False

# ---------------------------------------------------------------- Teklif istenen firmalar
_fp = os.path.join(MEP_DIR, "rfq_firmalar.csv")
if os.path.exists(_fp):
    FM = wb.create_sheet("Teklif_Istenen_Firmalar")
    FM["A1"] = "TEKLİF İSTENEN FİRMALAR – serhat@mepcenter.com.tr ile 29.09–06.10.2026 arasında gönderilen teklif talepleri"
    FM["A1"].font = Font(bold=True, size=13)
    _fr = list(csv.DictReader(open(_fp, encoding="utf-8-sig")))
    _order = ["ELEKTRIK", "MEKANIK", "ASANSOR", "SINYALIZASYON", "KATENER"]
    _fr.sort(key=lambda f: (min([_order.index(x) for x in _order if x in (f.get("paketler") or "").upper()] or [9]), f.get("firma", "")))
    _cols = [("firma", "Firma", 30), ("firma_turu", "Firma türü", 22), ("faaliyet", "Faaliyet alanı", 34), ("ulke", "Ülke", 7),
             ("paketler", "Paket(ler)", 20), ("durum", "Dönüş durumu", 15), ("ilk_gonderim", "İlk gönderim", 11),
             ("hatirlatma", "Hatırlatma", 9), ("email_adresleri", "E-posta", 34), ("not", "Not", 40)]
    # özet sayaçları
    FM["A3"] = "Toplam firma"; FM["B3"] = len(_fr); FM["A3"].font = BOLD
    _cnt = collections.Counter(f.get("durum") or "CEVAP YOK" for f in _fr)
    FM["D3"] = "Dönüş durumu: " + " · ".join(f"{k}: {v}" for k, v in _cnt.most_common())
    FM.merge_cells("D3:J3")
    _DFILL = {"TEKLİF GELDİ": "C6EFCE", "VERECEK": "DDEBF7", "SORU SORDU": "FFF2CC", "YÖNLENDİRDİ": "FFF2CC",
              "VERMİYOR": "F8CBAD", "ULAŞMADI": "EDEDED", "CEVAP YOK": "FFFFFF"}
    for j, (k, h, w) in enumerate(_cols, 1):
        c = FM.cell(row=5, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
        FM.column_dimensions[get_column_letter(j)].width = w
    for i, f in enumerate(_fr, start=6):
        for j, (k, h, w) in enumerate(_cols, 1):
            c = FM.cell(row=i, column=j, value=f.get(k, "")); c.border = BOX; c.alignment = WRAP
        d = (f.get("durum") or "CEVAP YOK").upper()
        for key, colr in _DFILL.items():
            if key in d:
                FM.cell(row=i, column=6).fill = PatternFill("solid", fgColor=colr); break
    FM.auto_filter.ref = f"A5:J{5 + len(_fr)}"; FM.freeze_panes = "B6"


_order = ["Ozet", "Yontem", "Teklif_Degerlendirme", "PointLink_Kiyas", "Ihale_Geneli_Bilgi", "Elektrik_AG", "Haberlesme", "Mekanik", "Asansor", "Sinyal", "Cer_Guc", "Katener",
          "Emsal_Kaynaklari", "Teklif_Istenen_Firmalar", "Teklifler", "Teklif_Durumu", "Idare_Duzeltme", "Varsayimlar"]
wb._sheets = [wb[n] for n in _order if n in wb.sheetnames] + [w for w in wb.worksheets if w.title not in _order]
_tabs = {"Ozet": "1F4E78", "Teklif_Degerlendirme": "70AD47", "Elektrik_AG": "FFC000", "Haberlesme": "FFC000", "Mekanik": "5B9BD5",
         "Asansor": "A5A5A5", "Sinyal": "ED7D31", "Cer_Guc": "7030A0", "Katener": "7030A0"}
for n, col in _tabs.items():
    wb[n].sheet_properties.tabColor = col
for ws in wb.worksheets:
    ws.sheet_view.zoomScale = 90
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1

from copy import copy as _copy
for _ws in wb.worksheets:
    for _row in _ws.iter_rows():
        for _c in _row:
            if _c.has_style or _c.value is not None:
                _f = _copy(_c.font); _f.name = "Arial"
                if not _f.sz: _f.sz = 10
                _c.font = _f
wb.save(OUT)
print("OK", OUT)
