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
    ("EUR/USD kuru", 1.146, "21.09.2026 piyasa kapanışı (USD/EUR 0,8723). Teklif günü TCMB/ECB kuru ile güncelleyin."),
    ("EUR/TRY kuru", 56.10, "20.09.2026 TCMB efektif satış ~56,11. Teklif günü kuru ile güncelleyin."),
    ("Hat uzunluğu – RFQ kabulü (km)", 6.56, "Katener şartnamesi; RFQ cetvellerinde kullanıldı"),
    ("Hat uzunluğu – idare cevabı (km)", 6.44, "İdare cevabı 05.10.2026, soru 18"),
    ("Hat boyu uzunluk düzeltme oranı", "=B6/B5", "Hat boyu iletken/kablo uzunluklarına uygulanır"),
    ("Araç sayısı – RFQ kabulü", 15, "Sinyal RFQ kabul 5"),
    ("Araç sayısı – idare cevabı", 14, "İdare cevabı soru 2 (araçlar ayrı ihale; arayüz yüklenicide)"),
    ("OG ring güzergahı – RFQ (m)", 7000, "Sıra 170 RFQ"),
    ("OG ring güzergahı – idare cevabı (m)", 7964, "İdare cevabı soru 21 (tüm kesitler)"),
    ("Galvanizli katener direği çeliği, imalat+galvaniz+dikim (EUR/kg)", 2.20, "Referans medyanı 1,80 €/kg (2013–2016 tramvay) + yerli üretim/montaj payı; Mitaş teklifi gelince güncelleyin"),
    ("Risk/belirsizlik payı – Asansör", 0.05, "2 firma teklifi var, kapsam net"),
    ("Risk/belirsizlik payı – Sinyalizasyon + AVLS", 0.15, "Ayrı sinyal projesi yok; miktarlar öngörü ağırlıklı; tek teklif (Point Link) aykırı"),
    ("Risk/belirsizlik payı – Katener", 0.10, "Proje var; fiyatlar referans + tahmin"),
    ("Risk/belirsizlik payı – Cer gücü / enerji temini", 0.10, "Proje var; teklif yok (Best Transformer, Alfanar bütçe bekleniyor)"),
    ("Risk/belirsizlik payı – Mekanik", 0.10, "Kalem bazlı; referans + tahmin; Ekura/Protek teklifleri bekleniyor"),
    ("Risk/belirsizlik payı – Elektrik AG / aydınlatma / yangın ihbar / topraklama", 0.10, "Kalem bazlı; referans kapsaması düşük"),
    ("Risk/belirsizlik payı – Kontrol ve haberleşme (SCADA, CCTV, telsiz, YBS, turnike)", 0.10, "Kalem bazlı; turnike adedi mimariden sayılacak"),
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
for a in ("B14", "B15", "B16", "B17", "B18", "B19", "B20"):
    V[a].number_format = "0%"
V.column_dimensions["A"].width = 58
V.column_dimensions["B"].width = 16
V.column_dimensions["C"].width = 95
P_USD, P_TRY, P_HAT, P_ARAC_RFQ, P_ARAC, P_RING_RFQ, P_RING, P_KG = (
    "Varsayimlar!$B$4", "Varsayimlar!$B$5", "Varsayimlar!$B$8", "Varsayimlar!$B$9",
    "Varsayimlar!$B$10", "Varsayimlar!$B$11", "Varsayimlar!$B$12", "Varsayimlar!$B$13")
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
    ("Haberleşme", "Referans – kalem bazlı (fiyatı bulunan 54/86 ana kalem) + sistem bazlı ort. 1.121.764",
     "İletim, telefon, telsiz, anons, CCTV, saat, erişim, SCADA, YBS, turnike",
     1721471, "EUR", "=D13", None, None, "EM_Butce_Tahmini Ozet sayfası (kalem bazlı)"),
    ("Asansör", "Referans – kalem bazlı (metro/tramvay asansör referansları medyanı)",
     "1000 kg medyan 50.992 €, 800 kg 35.293 €",
     647200, "EUR", "=D12", 50992, 35293, "Metro referansları ağırlıklı; teklifler daha düşük"),
]
for i, r in enumerate(trows, start=4):
    for j, v in enumerate(r, 1):
        if j == 6 and isinstance(v, str) and v.startswith("=D"):
            v = f"=D{i}"
        c = T.cell(row=i, column=j, value=v); c.border = BOX; c.alignment = WRAP
        if j in (4, 6, 7, 8): c.number_format = EUR
T["A15"] = "Bekleyen / bütçe fiyatı istenen: Edoux, Adakon-Orona (asansör); Contirail/Mukan Rail (AVLS), Hanning & Kahl, Pintsch, INIT, Frauscher (sinyal); Mitaş, DeSA/Arthur Flury, Erbakır, Kambeton, La Farga, Galland, Revenga (katener); Best Transformer, Alfanar, Savronik, Alstom, Met-Eng, Tema (enerji)."
T["A15"].alignment = WRAP
T.merge_cells("A15:I15"); T.row_dimensions[15].height = 45
for col, w in zip("ABCDEFGHI", (18, 34, 60, 15, 10, 15, 14, 14, 48)):
    T.column_dimensions[col].width = w

# ---------------------------------------------------------------- Disiplin sayfaları
HDR = ["Sıra", "Poz", "Kalem / Alt kalem", "Birim", "Miktar (RFQ)", "Miktar (idare cevabına göre)",
       "Birim fiyat EUR (montaj dahil)", "Tutar EUR", "Fiyat kaynağı", "Düzeltme / not"]
WID = [7, 9, 70, 8, 13, 15, 15, 15, 34, 48]


def sheet(name, title, groups):
    """groups: list of (sira, poz, baslik, items); item = (kalem, birim, q_rfq, q_corr, bf, kaynak, not)"""
    ws = wb.create_sheet(name)
    ws["A1"] = title; ws["A1"].font = Font(bold=True, size=12)
    ws["A2"] = ("Birim fiyatlar EUR, KDV hariç, montaj+test+devreye alma dahil. Sarı: değiştirilebilir. "
                "Turuncu miktar: idare cevabı (05.10.2026) ile RFQ'dan farklılaşan kalem. "
                "Kaynak kodları: REF = EM_Butce_Tahmini referans BF (geçmiş teklifler, HICP ile Ağu-2026); "
                "TEKLİF = 2026 firma teklifi; TAHMİN = mühendislik tahmini (referans yok).")
    ws["A2"].alignment = WRAP; ws.merge_cells("A2:J2"); ws.row_dimensions[2].height = 42
    for j, h in enumerate(HDR, 1):
        c = ws.cell(row=4, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
    for j, w in enumerate(WID, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = "A5"
    r = 5
    main_cells = []
    rfq_terms = []
    for sira, poz, baslik, items in groups:
        mr = r
        for j, v in enumerate([sira, poz, baslik], 1):
            ws.cell(row=mr, column=j, value=v)
        for j in range(1, 11):
            ws.cell(row=mr, column=j).fill = FILL_MAIN; ws.cell(row=mr, column=j).font = BOLD
            ws.cell(row=mr, column=j).border = BOX
        r += 1
        first = r
        for kalem, birim, q_rfq, q_corr, bf, kaynak, notu in items:
            ws.cell(row=r, column=2, value=poz)
            ws.cell(row=r, column=3, value=kalem).alignment = WRAP
            ws.cell(row=r, column=4, value=birim)
            ws.cell(row=r, column=5, value=q_rfq).number_format = QTY
            qc = q_rfq if q_corr is None else q_corr
            c6 = ws.cell(row=r, column=6, value=qc); c6.number_format = QTY
            if q_corr is not None and q_corr != q_rfq:
                c6.fill = FILL_CHG
            c7 = ws.cell(row=r, column=7, value=bf); c7.number_format = EUR2; c7.fill = FILL_IN
            ws.cell(row=r, column=8, value=f"=F{r}*G{r}").number_format = EUR
            ws.cell(row=r, column=9, value=kaynak).alignment = WRAP
            ws.cell(row=r, column=10, value=notu).alignment = WRAP
            for j in range(1, 11):
                ws.cell(row=r, column=j).border = BOX
            r += 1
        last = r - 1
        ws.cell(row=mr, column=8, value=f"=SUM(H{first}:H{last})").number_format = EUR
        ws.cell(row=mr, column=5, value="RFQ tutarı →")
        ws.cell(row=mr, column=6, value=f"=SUMPRODUCT(E{first}:E{last},G{first}:G{last})").number_format = EUR
        main_cells.append(f"H{mr}")
        rfq_terms.append(f"F{mr}")
    r += 1
    ws.cell(row=r, column=3, value="TOPLAM (idare cevaplarına göre düzeltilmiş)").font = BOLD
    ws.cell(row=r, column=8, value="=" + "+".join(main_cells)).number_format = EUR
    ws.cell(row=r + 1, column=3, value="Karşılaştırma: RFQ miktarlarıyla aynı birim fiyatlardan tutar").font = BOLD
    ws.cell(row=r + 1, column=8, value="=" + "+".join(rfq_terms)).number_format = EUR
    ws.cell(row=r + 2, column=3, value="İdare cevaplarının net etkisi").font = BOLD
    ws.cell(row=r + 2, column=8, value=f"=H{r}-H{r+1}").number_format = EUR
    for rr in (r, r + 1, r + 2):
        for j in (3, 8):
            ws.cell(row=rr, column=j).fill = FILL_TOT; ws.cell(row=rr, column=j).border = BOX
    return ws, f"'{name}'!$H${r}", f"'{name}'!$H${r+1}", {g[0]: main_cells[i] for i, g in enumerate(groups)}


H = P_HAT          # hat boyu oranı
NA = P_ARAC        # araç sayısı (idare)

# ================================================================ ASANSÖR
avg1000 = "=AVERAGE(Teklifler!$G$4,Teklifler!$G$5)"
avg800 = "=AVERAGE(Teklifler!$H$4,Teklifler!$H$5)"
asansor = [
    ("364", "5010.A", "2 Duraklı 13 Kişilik Asansör (12 adet – 4 üst geçit × 3)", [
        ("Asansör 1000 kg, 2 durak, MRL dişlisiz, VVVF, 1 m/s, cam+paslanmaz kabin – S09 Hızmalı Köprüsü", "adet", 3, None, avg1000,
         "TEKLİF ort. (Schindler, TK Elevator)", "Bakım hariç; yeşil etiket, eğitim dahil"),
        ("Asansör 1000 kg – S10 Balıklıgöl", "adet", 3, None, avg1000, "TEKLİF ort.", ""),
        ("Asansör 1000 kg – S11 Eyyüp Peygamber", "adet", 3, None, avg1000, "TEKLİF ort.", ""),
        ("Asansör 1000 kg – S12 Rasathane", "adet", 3, None, avg1000, "TEKLİF ort.", ""),
    ]),
    ("365", "5010.B", "2 Duraklı 10 Kişilik 800 kg Asansör (D01 idari bina)", [
        ("Asansör 800 kg, 2 durak (zemin/1. kat), MRL, VVVF, 1 m/s – D01", "adet", 1, None, avg800, "TEKLİF ort.", ""),
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
        ("Elektrikli makas motoru – depo (IP67, el kranklı, uç konum dedektörlü)", "takım", 20, 40, 15000,
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
        ("Araç üstü AVLS bilgisayarı (EN 50155, 48 kanal GPS, LTE, odometri)", "adet", 15, f"={NA}", 3500, "TAHMİN", "14 araç"),
        ("Entegre GSM/GPS çatı anteni + kablosu", "adet", 15, f"={NA}", 400, "TAHMİN", "14 araç"),
        ("Sürücü HMI terminali – her kabine 1", "adet", 30, f"=2*{NA}", 1500, "TAHMİN", "14 araç"),
        ("Araç içi arayüz (odometri, PIS/anons, sinyal paneli), kablaj, montaj", "set", 15, f"={NA}", 1500, "TAHMİN", "14 araç"),
        ("M2M data SIM / APN aktivasyonu", "adet", 15, f"={NA}", 100, "TAHMİN", "14 araç"),
        ("Depo veri indirme kablosuz erişim noktası", "adet", 2, None, 2500, "TAHMİN", ""),
        ("Hat boyu lup konum verisinin AVLS'ye aktarımı", "set", 1, None, 10000, "TAHMİN", ""),
        ("Kurulum, araç bazlı test ve devreye alma", "set", 1, None, 25000, "TAHMİN", ""),
    ]),
    ("234", "3003", "Tramvay Araç Takip Sistemi Merkezi Donanımı ve Yazılımı", [
        ("AVLS merkez paketi: yedekli sunucu, NAS, operatör PC, 65\" duvar monitörü, VPN router/firewall, LAN, merkezi yazılım+lisans, belediye AVLS entegrasyonu, kurulum/test/eğitim",
         "set", 1, None, 136568, "REF (H&K İzmir 136.568; Kocaeli 212.046)", "Mevcut belediye AVLS entegrasyonu dahil"),
    ]),
    ("235", "3004", "Araç Takip Sistemi Tasarımı", [
        ("AVLS tasarımı: mimari, konumlandırma (GPS+odometri+lup), merkez ekranları, siber güvenlik, uygulama projeleri",
         "set", 1, None, 60000, "TAHMİN", ""),
    ]),
]
ws_sn, SN_TOT, SN_RFQ, SN_MAIN = sheet("Sinyal", "4 SİNYALİZASYON VE ARAÇ TAKİP (AVLS) – Sıra 228–235", sinyal)

# ================================================================ KATENER
direk = lambda kod, ad, n, kg, bulon: (kod, ad, [
    (f"{ad} gövdesi – galvanizli çelik (imalat+galvaniz+dikim)", "kg", kg, None, f"={P_KG}",
     "REF medyan 1,80 €/kg + pay (Varsayımlar)", "Mitaş teklifi bekleniyor (dikişli S355)"),
    (f"{ad} ankraj bulonu M30 (somun+rondela HDG)", "adet", bulon, None, 22, "TAHMİN", "Temel inşaat kapsamında"),
    (f"{ad} dikim/montaj (vinç, şakül, tork)", "adet", n, None, 300, "TAHMİN", ""),
])
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
    direk("222", "T1-A Tipi Katener Direği (114 adet)", 114, 39216, 456),
    direk("223", "T2-B Tipi Katener Direği (17 adet)", 17, 7293, 136),
    direk("224", "T2-B1 Tipi Katener Direği (4 adet)", 4, 1452, 32),
    direk("225", "T3-D Tipi Katener Direği (33 adet)", 33, 21912, 330),
    direk("226", "T3-C Tipi Katener Direği (60 adet)", 60, 39840, 600),
]
# direk() returns (sira, title, items) – add poz
katener = katener[:2] + [(s, p, t, it) for (s, t, it), p in zip(katener[2:], ("2012.C", "2012.D", "2012.E", "2012.G", "2012.F"))]
ws_kt, KT_TOT, KT_RFQ, KT_MAIN = sheet("Katener", "5 ELEKTRİFİKASYON (B) – KATENER – Sıra 220–226", katener)

# ================================================================ CER GÜCÜ / ENERJİ TEMİNİ
RING = f"{P_RING}/{P_RING_RFQ}"
def tm(n, cab_ac, cab_dc, cab_bag, cab_vld, pabuc):
    return [
        ("Cer trafosu 2750 kVA 34,5/0,6-0,6 kV Dy5-Dd0, dökme reçine, EN 50329", "adet", n, None, 100000,
         "REF (3300 kVA: Aktif 97.981, ABB Al 93.263, ABB Cu/Cu 151.850)", "Best Transformer teklifi bekleniyor"),
        ("Trafo sıcaklık rölesi + sekonder toprak kaçağı koruması + izole kaide", "takım", n, None, 3000, "TAHMİN", ""),
        ("Doğrultucu 12 darbeli 2500 kW 750 V DC, Class VI", "adet", n, None, 48000, "REF (ABB 37.927–49.610; Haluk 1,2 MW 35.975)", ""),
        ("Trafo–doğrultucu AC kabloları 1×300 Cu 1,8/3 kV", "m", cab_ac, None, 45, "TAHMİN", ""),
        ("DC giriş (incoming) hücresi 6300 A", "adet", n, None, 36500, "REF (Aktif 36.216–36.824)", ""),
        ("DC fider hücresi HSCB 3600 A", "adet", 4 * n, None, 40000, "REF (Haluk 44.641, MET 43.769, ABB 38.797, Aktif 37.456)", ""),
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
        ("YAXC7V-R (NA2XSY) 1×240/25 Al XLPE LSHF tek damar kablo – çekme dahil", "m", 21000, f"=3*{P_RING}", 14,
         "REF (Prysmian 1×400 15 €/m; Haluk 1×150 11 €/m)", "İdare soru 21: güzergah 7.964 m"),
        ("36 kV 1×240 kablo başlığı", "adet", 24, None, 450, "TAHMİN", ""),
        ("36 kV 1×240 ek mufu", "adet", 33, f"=ROUND(33*{RING},0)", 400, "TAHMİN", "Güzergah oranında"),
        ("Trefoil kelepçe / kanal içi askı", "adet", 6500, f"=ROUND(6500*{RING},0)", 6, "TAHMİN", "Güzergah oranında"),
        ("Yangın durdurucu (TM geçişleri)", "adet", 10, None, 200, "TAHMİN", ""),
        ("Kablo etiket / güzergah markörü", "adet", 140, f"=ROUND(140*{RING},0)", 15, "TAHMİN", ""),
        ("OG kablo saha testleri (VLF, kılıf)", "set", 4, None, 3000, "TAHMİN", ""),
    ]),
    ("171", "2002.B", "TEİAŞ Bağlantısı 2×4×(1×400+35) mm² 20,3/35 kV – transe dahil", [
        ("YAXC7V-R 1×400/35 Al XLPE zırhlı LSHF – çekme dahil", "m", 35424, None, 20, "REF (Prysmian 15 €/m malzeme) + çekme", "İdare: 8.856 m × 4 kablo – uyumlu"),
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
        ("36 kV 1250 A 25 kA SF6 kesicili hücre + AT + sayısal röle + ölçü + kilitleme + FAT/SAT", "adet", 12, None, 32000,
         "REF (Haluk LSC2B ring hücresi 30.518) + röle/test", ""),
    ]),
    ("174", "2004.B", "Cer Trafo Besleme 34,5 kV Şalt Panosu (5 hücre)", [
        ("36 kV kesicili trafo koruma hücresi + röle + analizör + DC kilitleme", "adet", 5, None, 29000, "REF (Haluk 26.130) + pay", ""),
        ("OG bağlantı kablosu 3(1×95/16) Al – hücre/cer trafosu", "m", 108, None, 25, "TAHMİN", ""),
        ("36 kV 1×95 kablo başlığı (büzüşmeli + geçmeli)", "adet", 30, None, 350, "TAHMİN", ""),
    ]),
    ("175", "2004.C", "İç İhtiyaç Trafo Besleme 34,5 kV Şalt Panosu (6 hücre)", [
        ("36 kV kesicili iç ihtiyaç trafo fider hücresi + röle", "adet", 6, None, 27000, "REF (Haluk 26.130) + pay", ""),
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
ws_cg, CG_TOT, CG_RFQ, CG_MAIN = sheet("Cer_Guc", "5 ELEKTRİFİKASYON (A) – GÜÇ TEMİNİ / CER GÜCÜ / ENERJİ TEMİNİ (5 TM, OG ring, TEİAŞ bağlantısı)", cer)


# ================================================================ MEKANİK / ELEKTRİK AG / HABERLEŞME (CSV'den)
import csv, os
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
ws_mk, MK_TOT, MK_RFQ, MK_MAIN = sheet("Mekanik", "2 MEKANİK – Sıra 159–168, 343–363 (HVAC, yangın, drenaj, sıhhi, basınçlı hava)", mekanik)
elk_ag = groups_from_csv("elektrik")
ws_ea, EA_TOT, EA_RFQ, EA_MAIN = sheet("Elektrik_AG", "1 ELEKTRİK (A) – AG dağıtım, topraklama, AG kablolar, AG tesisat-aydınlatma, yangın ihbar", elk_ag)
hab = groups_from_csv("haberlesme")
ws_hb, HB_TOT, HB_RFQ, HB_MAIN = sheet("Haberlesme", "1 ELEKTRİK (B) – Kontrol ve haberleşme (iletim, telefon, telsiz, anons, CCTV, saat, erişim, SCADA, YBS, ücret toplama)", hab)

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
     HB_TOT, RISK['HAB'], HB_RFQ, "=Teklifler!F12", "Referans kalem bazlı", "ON Elektronik (saat+YBS) ve Teknomaks (CCTV) teklifleri ekte/bekleniyor"),
    ("2 MEKANİK", "Isıtma-soğutma, havalandırma, yangın söndürme, drenaj, sıhhi tesisat, basınçlı hava", "159–168, 343–363",
     MK_TOT, RISK['MEKANIK'], MK_RFQ, None, "", "Asansör hariç (ayrı disiplin)"),
    ("3 ASANSÖR", "13 asansör (12 üst geçit 1000 kg + 1 idari bina 800 kg)", "364–365",
     AS_TOT, RISK['ASANSOR'], AS_RFQ, "=Teklifler!F5", "En düşük teklif (TK Elevator)", "Schindler + TK ortalaması; Emlift teklifi ekte (okunamadı)"),
    ("4 SİNYALİZASYON", "Hat boyu + depo sinyalizasyon, araç üstü, merkez, araç takip (AVLS)", "228–235",
     SN_TOT, RISK['SINYAL'], SN_RFQ, "=Teklifler!F7", "Sistem bazlı ref. (makas başı)", "Point Link 7,28 M€ kıyas dışı; Mukan AVLS teklifi ekte"),
    ("5 ELEKTRİFİKASYON", "Güç temini ve cer gücü (OG ring, TEİAŞ bağlantısı, 34,5 kV hücreler, 5 cer TM, kaçak akım)", "169–179, 187–189, 197, 200–210, 219, 227",
     CG_TOT, RISK['CER'], CG_RFQ, "=Teklifler!F11", "Sistem bazlı ref. (5 TM; yalnız OG+trafo+DC)", ""),
    ("5 ELEKTRİFİKASYON", "Katener (hat boyu, depo, direkler)", "220–226",
     KT_TOT, RISK['KATENER'], KT_RFQ, "=Teklifler!F9", "Sistem bazlı ref. (km başı)", "Direk temelleri inşaatta; ana hatta lente yok"),
]
DIS = ["1 ELEKTRİK", "2 MEKANİK", "3 ASANSÖR", "4 SİNYALİZASYON", "5 ELEKTRİFİKASYON"]
oh = ["Disiplin", "Kapsam", "Kalem bazlı bütçe EUR", "Risk payı EUR", "Önerilen bütçe EUR",
      "Önerilen bütçe USD", "Önerilen bütçe TL", "Pay %", "RFQ miktarlarıyla (düzeltmesiz) EUR", "Referans / teklif kıyası EUR", "Açıklama"]
for j, h in enumerate(oh, 1):
    c = O.cell(row=4, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
O.row_dimensions[4].height = 45
r0 = 5
rT = r0 + len(DIS)
rS0 = rT + 4          # alt kırılım tablosu başlığı
O.cell(row=rS0 - 1, column=1, value="ALT KIRILIM (disiplin içi)").font = Font(bold=True, size=12)
sh2 = ["Disiplin", "Alt kalem", "Cetvel sıraları", "Kalem bazlı EUR", "Risk %", "Önerilen EUR", "RFQ miktarlarıyla EUR",
       "Kıyas EUR", "Kıyas kaynağı", "Açıklama"]
for j, h in enumerate(sh2, 1):
    c = O.cell(row=rS0, column=j, value=h); c.font = F_H; c.fill = FILL_H; c.border = BOX; c.alignment = WRAP
for i, (d, ad, sira, tot, risk, rfq, kiyas, ksrc, acik) in enumerate(sub):
    r = rS0 + 1 + i
    vals = [d, ad, sira, f"={tot}", f"={risk}", f"=D{r}*(1+E{r})", f"={rfq}", kiyas, ksrc, acik]
    for j, v in enumerate(vals, 1):
        c = O.cell(row=r, column=j, value=v); c.border = BOX; c.alignment = WRAP
        if j in (4, 6, 7, 8): c.number_format = EUR
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
            f"=E{r}/$E${rT}", "=" + rng("G"), "=" + rng("H"), ""]
    for j, v in enumerate(vals, 1):
        c = O.cell(row=r, column=j, value=v); c.border = BOX; c.alignment = WRAP
        if j in (3, 4, 5, 6, 7, 9, 10): c.number_format = EUR
        if j == 8: c.number_format = "0.0%"
    O.cell(row=r, column=1).font = BOLD
O.cell(row=rT, column=1, value="TOPLAM MEP").font = BOLD
for col in "CDEFGIJ":
    c = O[f"{col}{rT}"]; c.value = f"=SUM({col}{r0}:{col}{rT-1})"; c.number_format = EUR; c.font = BOLD
O[f"H{rT}"] = f"=SUM(H{r0}:H{rT-1})"; O[f"H{rT}"].number_format = "0.0%"
for j in range(1, 12):
    O.cell(row=rT, column=j).fill = FILL_TOT; O.cell(row=rT, column=j).border = BOX
rT = rS2 + 1   # aşağıdaki döküm için

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
    "5. Sinyalizasyonda ayrı proje yoktur; miktarlar şematik paftalardan öngörülmüştür. Point Link/CASCO teklifi (7.281.784 € DAP, gümrük ve KDV hariç) kalem dökümü alınana kadar yalnız üst sınır göstergesidir.",
    "6. Kur: EUR/USD ve EUR/TRY Varsayımlar sayfasındadır (Eylül 2026 sonu piyasa değerleri); teklif günü kuruyla güncellenmelidir.",
    "7. Gelen yeni teklifler (Mitaş, Erbakır, DeSA, Best Transformer, Contirail vb.) ilgili satırın birim fiyatına yazılarak bütçe güncellenebilir.",
]
for i, t in enumerate(notes):
    c = O.cell(row=rN + i, column=1, value=t); c.alignment = WRAP
    O.merge_cells(start_row=rN + i, start_column=1, end_row=rN + i, end_column=11)
    O.row_dimensions[rN + i].height = 15 if i == 0 else 32
O.cell(row=rN, column=1).font = BOLD
for col, w in zip("ABCDEFGHIJK", (24, 48, 18, 16, 18, 16, 18, 10, 18, 18, 40)):
    O.column_dimensions[col].width = w
O.freeze_panes = "A5"

for ws in wb.worksheets:
    ws.sheet_view.zoomScale = 90
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1

wb.save(OUT)
print("OK", OUT)
