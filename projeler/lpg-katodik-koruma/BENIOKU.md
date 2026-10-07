# Akaryakıt + LPG İstasyonu – Yerleşim ve LPG Tankı Katodik Koruma (TASLAK T0)

| Dosya | İçerik |
|---|---|
| `istasyon_lpg_kk_taslak.dxf` | AutoCAD 2010 DXF (AutoCAD 2010 ve sonrası açar), birim metre (1 birim = 1 m) |
| `istasyon_lpg_kk_taslak.png` | Önizleme |
| `plan_uret.py` | DXF'i üreten script (`pip install ezdxf matplotlib` → `python3 plan_uret.py --png`) |

Katmanlar: `SINIR-YOL, BINA, KANOPI, POMPA-ADASI, LPG-SAHA, LPG-TANK, LPG-HAT, KK-ANOT, KK-KABLO, KK-OLCUM, KK-IZOLASYON, OLCU, YAZI, PAFTA, TEYIT`

## Kabuller (sahada teyit edilecek)
- Kroki ölçeksiz; ~50 px = 1 m kabulüyle ölçeklendi. LPG sahası krokideki 6 m / 4 m / 1.2 m pah ölçüleriyle çizildi.
- LPG tankı: 1 adet yeraltı, ~5 m³ (Ø1.25 × 4.40 m), kaplamalı ("Tek Tank / Tek Dispenser" tesisat şeması).
- Zemin özdirenci 30 Ω·m (Wenner ölçümü yapılmalı), %10 kaplama hasarı, 20 mA/m², 1.3 emniyet, 20 yıl.
- Sonuç: gerekli ≈ 58 mA → 5 adet 17 lb Mg anot (4 tank + 1 hat), 2 ölçüm kutusu, kalıcı Cu/CuSO4 referans elektrot, 3 izolasyon flanşı.
- `TEYIT` katmanındaki elemanlar krokiden okunamadı.
