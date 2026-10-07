# Saha Plakası Analizi – "Shell & Turcas – Tek Tank / Tek Dispenser Tesisat Şeması"

Plaka tel çitin arkasında olduğu için tek bir fotoğrafta tam okunamıyor. Farklı açılardan çekilmiş 5 fotoğraf
(184920, 185113, 185348, 185354, 185405) tam çözünürlükte, ters asılı olanlar 180° döndürülerek karşılaştırıldı.

## Katodik koruma açısından kritik kalemler

| Poz | Adet | Ebat | Marka/Belge | Açıklama | Kaynak fotoğraf |
|---|---|---|---|---|---|
| **25** | 1 | **10M3** | Shell & Turcas standartlarında | **LPG Stok Tankı** | 185348'de tam okunuyor; 184920/185113'te ilk karakter tele denk geliyor |
| **24** | **2** | – | TSE Belg. | **10 Lb Magnezyum Anot** | 185348'de "10 Lb" tam okunuyor |
| **17** | **2** | – | TSE Belg. | **3,5 Lb Magnezyum Anot** | 184920, 185113, 185348 |
| 13 | 6 | – | YUY-SAN, PN40 | İzole Flanş Kiti | 184920, 185113 |

Şemada tank kesitinin üzerinde **Ø 2350** ölçüsü okunuyor (`plaka_tank_O2350.jpg`). Ancak 10 m³'lük bir tank için
Ø2,35 m alışılmadık derecede kısa bir tank anlamına gelir; tipik ölçü Ø1,60 × ~5,4 m'dir. Plaka standart bir
şablon olabilir. **Tank etiketinden (isim plakası) çap ve boy teyit edilmeli.** Hesapta yüzeyi daha büyük olan
Ø1,60 × 5,40 m kullanıldı (emniyetli taraf).

Şemadaki yerleşime göre 24 numaralı anotlar (10 Lb) tank yanında, 17 numaralı anotlar (3,5 Lb) dispenser
altındaki hat girişinde gösterilmiş.

## Malzeme listesinin tamamı (okunabildiği kadarıyla)

| Poz | Adet | Ebat | Marka | Sınıfı | Açıklama |
|---|---|---|---|---|---|
| 1 | 4 | D?5 | OMAL | PN40 | Tam geçişli, pnömatik aktüatörlü vana |
| 2 | 1 | ? | PAKKENS | PN40 | Tank manometresi Q63 – 0-25 bar gliserinli |
| 3 | 1 | ? | REGO | 300# | Dolum valfi (REGO 7579C / OMEGA VRN 20) |
| 4 | 1 | ? | ÖZEL | – | Dolum hattı by-pass adaptörü |
| 5 | ? | DN.. (1/2") | MHA | PN500 | Termal (?) tahliye valfi |
| 6 | 1 | D?0 | AYVAZ | PN40 | Metal örgülü esnek (flexible) bağlantı (30 cm) |
| 7 | 1 | – | – | – | Yeraltı (?) harici pompa |
| 8 | 1 | – | CORKEN | 300# | CORKEN B166 by-pass valfi |
| 9 | 1 | D?2 | – | PN40 | Çek valf |
| 10 | 5 | – | REGO | 300# | Emniyet valfi – REGO 3129 |
| 11 | 2 | DN32 | OMAL | PN40 | Tam geçişli, pnömatik aktüatörlü vana |
| 12 | 2 | DN32 | AYVAZ | PN40 | Metal örgülü esnek (flexible) bağlantı (30 cm) |
| 13 | 6 | – | YUY-SAN | PN40 | İzole flanş kiti |
| 14 | 2 | DN32 | – | PN40 | Tam geçişli, küresel gaz-fazı vanası (TSE 9809) |
| 15 | 2 | 1/2" | PAKKENS | PN40 | Q100 – 0-25 bar gliserinli manometre |
| 16 | 2 | 3/4" | – | PN40 | R1 – esnek bağlantı hortumu |
| 17 | 2 | – | TSE Belg. | – | **3,5 Lb magnezyum anot** |
| 18 | 2 | DN25 | – | PN40 | Tam geçişli, küresel gaz-fazı vanası (TSE 9809) |
| 19 | 1 | – | – | SCH80 | Redüksiyon |
| 20 | – | 1" | – | SCH80 | Dikişsiz çelik çekme boru |
| 21 | – | 1 1/2" | – | SCH80 | Dikişsiz çelik çekme boru |
| 22 | 1 | DN25 | AYVAZ | PN40 | Metal örgülü esnek (flexible) bağlantı (30 cm) |
| 23 | 1 | 2" | Pimaş boru | – | Emniyet ventili bacası (min 1 m) |
| 24 | 2 | – | TSE Belg. | – | **10 Lb magnezyum anot** |
| 25 | 1 | 10M3 | Shell & Turcas std. | – | **LPG stok tankı** |

"?" ile gösterilen hücreler tel çitin arkasında kalıyor. Plakadaki not: *"Toprak altı tüm hatlarda min. %50
bindirme yapılacaktır (iki kat). Tüm hatlarda Sch80 dikişsiz çelik çekme boru kullanılacaktır."*

## Tasarıma etkisi
- Tank: 10 m³ → yüzey ≈ 31,6 m² (önceki taslakta 5 m³ / 20 m² kabul edilmişti).
- Gerekli akım ≈ 92 mA (kabuller: 30 Ω·m, %10 kaplama hasarı, 20 mA/m², 1,3 emniyet).
- Plakadaki mevcut düzen (2 × 10 Lb + 2 × 3,5 Lb) bu kabullerle ≈ 16 yıl ömür veriyor. 20 yıl hedefi için
  taslakta **4 × 10 Lb (tank) + 2 × 3,5 Lb (dispenser) = 6 anot** önerildi → ≈ 28 yıl, 245 mA kapasite.
- Zemin özdirenci ölçülünce sayı yeniden kontrol edilecek.
