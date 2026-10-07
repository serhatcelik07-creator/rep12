# Akaryakıt + LPG İstasyonu – Yerleşim ve LPG Tankı Katodik Koruma (TASLAK T0)

| Dosya | İçerik |
|---|---|
| `istasyon_lpg_kk_taslak.dxf` | AutoCAD 2010 DXF (AutoCAD 2010 ve sonrası açar), birim metre (1 birim = 1 m) |
| `istasyon_lpg_kk_taslak.png` | Önizleme |
| `plan_uret.py` | DXF'i üreten script (`pip install ezdxf matplotlib` → `python3 plan_uret.py --png`) |

Katmanlar: `SINIR-YOL, BINA, KANOPI, POMPA-ADASI, LPG-SAHA, LPG-TANK, LPG-HAT, KK-ANOT, KK-KABLO, KK-OLCUM, KK-IZOLASYON, OLCU, YAZI, PAFTA, TEYIT`

## Kabuller (sahada teyit edilecek)
- Kroki ölçeksiz; ~50 px = 1 m kabulüyle ölçeklendi. LPG sahası krokideki 6 m / 4 m / 1.2 m pah ölçüleriyle çizildi.
- LPG tankı: 10 m³ (plaka poz 25); hesapta Ø1,60 × 5,40 m kabul (plakadaki Ø2350 tank etiketinden teyit edilmeli).
- Zemin özdirenci 30 Ω·m (Wenner ölçümü yapılmalı), %10 kaplama hasarı, 20 mA/m², 1.3 emniyet, 20 yıl.
- Sonuç: gerekli ≈ 92 mA → 4 × 10 Lb (tank) + 2 × 3,5 Lb (dispenser) Mg anot, 2 ölçüm kutusu, referans elektrot, izolasyon flanşları.
- `TEYIT` katmanındaki elemanlar krokiden okunamadı.

## Saha plakasından okunanlar (bkz. `plaka/PLAKA_ANALIZI.md`)
- Poz 25: LPG stok tankı **10 m³** · Poz 24: **2 × 10 Lb** Mg anot · Poz 17: **2 × 3,5 Lb** Mg anot · Poz 13: 6 × izole flanş kiti
- Taslak bu verilere göre güncellendi: **4 × 10 Lb + 2 × 3,5 Lb** Mg anot, gereken akım ≈ 92 mA, ömür ≈ 28 yıl.
