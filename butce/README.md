# Şanlıurfa HRS 1. Etap – MEP Bütçe Çalışması

`URF_1Etap_MEP_Butce_2026-10-06.xlsx` – 5 disiplin (Elektrik, Mekanik, Asansör, Sinyalizasyon, Elektrifikasyon),
kalem kalem, formüllü bütçe. EUR, KDV hariç, montaj dahil, Ekim 2026.

Sayfalar:
- **Ozet** – disiplin bazında bütçe (EUR/USD/TL), risk payı, RFQ (şişirmeli) kıyası, fiyat kaynağı dağılımı; alt kırılım; cetvel sırası dökümü
- **Teklif_Degerlendirme** – gelen tekliflerin bütçe karşılığıyla kıyası, sapmalar, ticari şartlar
- **Elektrik_AG, Haberlesme, Mekanik, Asansor, Sinyal, Cer_Guc, Katener** – kalem kalem: RFQ miktarı, idare düzeltmesi,
  geri alınan metraj payı, net miktar, birim fiyat, tutar, fiyat türü (2026 teklif / geçmiş teklif uyarlaması / tahmin), emsal
- **Teklifler, Teklif_Durumu, Idare_Duzeltme, Varsayimlar**

Yeniden üretmek: `python3 build_butce.py` (veriler `veri/` altında: RFQ kalemleri, fiyatlar, emsal revizyonları, teklif kalemleri).
