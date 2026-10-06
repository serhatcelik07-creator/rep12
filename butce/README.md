# Şanlıurfa HRS 1. Etap – Asansör / Sinyalizasyon / Elektrifikasyon Bütçesi

`URF_1Etap_Asansor_Sinyal_Elektrifikasyon_Butce_2026-10-06.xlsx`: formüllü bütçe modeli
(EUR, KDV hariç, montaj+test dahil). `build_butce.py` dosyayı yeniden üretir:

    python3 build_butce.py

Sayfalar:
- **Ozet**: disiplin toplamları, risk payı, USD/TL karşılıkları, referans kıyası, cetvel sırası dökümü
- **Varsayimlar**: kurlar, hat uzunluğu, araç sayısı, OG ring uzunluğu, direk €/kg, risk payları
- **Teklifler**: Schindler, TK Elevator, Point Link/CASCO ve referans kıyasları
- **Asansor / Sinyal / Katener / Cer_Guc**: RFQ miktarı, idare cevabına göre miktar, birim fiyat, kaynak
- **Idare_Duzeltme**: 05.10.2026 idare cevaplarından bütçeye yansıyanlar
