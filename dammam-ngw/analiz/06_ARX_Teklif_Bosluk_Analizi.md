# ARX Tender Design Proposal – Kapsam Boşluk Analizi (MEP ve Depo Ekipmanı)

**Belge:** 503-ARX-BD-PTD-005-00, V00, 16.11.2026 – "Tender Design Services, SAR NGW Dammam"
**Karşılaştırma bazı:** SOW v2.1 (Addendum 01), D3 Pricing Table (Add.01), D2 Employer's Requirements
**Ücret:** 1.780.000 SAR + 900.000 SAR success fee (KDV hariç). 8 haftalık program. İhale kazanılırsa IFC'ye kadar detay tasarım münhasırlığı istiyor.

---

## 1. Genel sonuç

ARX teklifi bir **tender design ve metraj (quantity take-off) hizmeti**. Kapsamın odağı track, toprak işleri, drenaj ve yapı.

**MEP tarafında yalnızca şunlar var:**
- Elektrik SLD'leri: MV/LV, trafo merkezleri, jeneratör, UPS, shore power ve PFC
- Benzer depolardan **benchmark ile türetilmiş** bina bazlı MEP metrajı

**HVAC, sıhhi tesisat, yangın ve ELV için:**
- Ne yerleşim ne sistem tasarımı ne de hesap var.
- Yangın tesisatı ayrıca "specialist/vendor design" diyerek hariç tutulmuş.

**Depo ekipmanı için:**
- Seçim, şartname ve metraj tamamen **hariç**.
- Yalnızca inşai hazırlıklar dahil: pit, temel, kren yolu, gömülü ray.

**Kısacası:** Teklif, ihale kapsamındaki MEP ve depo ekipmanı gereksinimlerini **karşılamıyor**. Lump sum ve yeniden ölçüm olmayan bir sözleşmede maliyetin büyük kısmı MEP ve ekipmanda. Örnek: diğer oturumun bütçesinde MB1'in MEP ve ekipman payı yaklaşık 13,7M USD, bina toplamının yarısından fazlası. Bu kalemler bu teklifle doğrulanmamış benchmark olarak kalır.

---

## 2. MEP – gereksinim ile ARX kapsamı karşılaştırması

| # | İhale gereksinimi (kaynak) | ARX kapsamı | Durum |
|---|---|---|---|
| 1 | **HVAC:** MB1, MB2 ve WLB için DX AHU sistemi. Enerji verimli, mümkünse doğal havalandırma. Havalandırma arızası SCADA'ya kritik alarm verir. Hesaplar Faz 1 ve Faz 2'nin tamamını kapsar. (SOW §4.2.1–4.2.2 "Power Supply and MEP") | Layout yok, ısı yükü hesabı yok, metraj benchmark | ❌ Eksik |
| 2 | **Yangın stratejisi:** Civil Defense onaylı Fire Strategy (SOW "Fire Strategy") | Hiç geçmiyor | ❌ Eksik |
| 3 | **Yangın tesisatı:** sprinkler, hidrant, standpipe, yangın pompası, clean agent, algılama (SRES şartnameleri, NFPA/SBC 801) | Layout hariç. "Specialist design – fire protection" hariç | ❌ Eksik |
| 4 | **Yangın ve kullanma suyu deposu kapasitesi** (SOW'da yok, ARX de "not stated" diyor) | Yalnızca tank yapısal boyutu. Hidrolik talep ve depolama süresi hesabı yok | ❌ Kritik. Bütçedeki 2.000 m³ varsayımı dayanaksız |
| 5 | **Sıhhi tesisat:** içme suyu, pis su, NWC entegrasyonu, pit drenajı, yağlı su ayırıcılar | Layout yok, benchmark metraj | ❌ Eksik |
| 6 | **Endüstriyel/proses su:** Water Treatment Station (SWA lisansı), yıkama tesisi su geri kazanımı, kimyasal dozlama, çamur ve atık su | Hiç geçmiyor | ❌ Eksik |
| 7 | **CET ve yakıt:** tank, pompa, sızıntı algılama, hazardous-area sınıflandırması, havalandırma, koku kontrolü | Hiç geçmiyor. Yalnızca inşai kısım | ❌ Eksik |
| 8 | **Atölye servisleri:** basınçlı hava (MB1 kompresör odası), fluid supply station, fume extraction, pit aydınlatması, her hatta shore connection panel, akü şarj | Hiç geçmiyor | ❌ Eksik |
| 9 | **Elektrik dağıtım:** trafo merkezleri, jeneratör, UPS, shore power ve PFC | SLD var | ✅ Kısmen |
| 10 | Yük hesabı, aydınlatma, priz, kablo güzergâhları | SLD'ye dayanak yük listesi belirtilmemiş | ⚠️ Belirsiz |
| 11 | **Topraklama, yıldırım ve EMC:** E&B ve EMC Control Plan (SOW, SRES) | Geçmiyor | ❌ Eksik |
| 12 | **ELV:** CCTV, access control, intrusion, PA, master clock, yangın alarm, Wi-Fi, LAN, BMS, SCADA (SOW §4.2.2, §1710–1714) | Layout hariç. Kadroda ELV mühendisi var ama ELV deliverable'ı yok | ❌ Eksik |
| 13 | Asansör (ofis binası) | Vendor tasarımı hariç | ⚠️ Kabul edilebilir. Metraj ve kapasite varsayımı gerekli |
| 14 | Enerji verimliliği ve sürdürülebilirlik (SOW, ER) | Specialist studies hariç | ⚠️ |
| 15 | Room data sheets, equipment schedules, BIM koordinasyonu (SOW §3) | BIM hariç. Buna rağmen RVT/IFC teslimi yazıyor, kendi içinde tutarsız | ⚠️ Netleştirilmeli |
| 16 | Appendix G Mandatory List (onaylı vendor) ile uyum | Fiyatlama ve tedarikçi hariç | ⚠️ Bizde kalır |

---

## 3. Depo ekipmanı – gereksinim ile ARX kapsamı karşılaştırması

ARX yalnızca **inşai hazırlıkları** yapıyor: pit, temel, kren yolu, gömülü ray. Ekipmanın seçimi, şartnamesi ve metrajı hariç. Ekipman verisi gelmezse temelleri de varsayımla boyutlandıracak.

SOW v2.1'de açıkça istenen ekipmanlar şunlar:

| Ekipman (SOW) | Bina / Faz | ARX |
|---|---|---|
| Overhead crane: MB1 (en az 2 × 25 t), heavy repair, minor component, warehouse | MB1, Ofis/Depo (A/B) | Yalnızca kren yolu |
| 25 t kren | WLB (B) | Yalnızca kren yolu |
| Tandem underfloor wheel lathe ve makine pit'i | WLB (B) | Yalnızca temel ve pit |
| Lifting jack, pit lifting table | MB1 | Yalnızca pit |
| 2 × bogie drop facility, bogie turntable | MB1 | Yalnızca inşai |
| 2 × fixed wheel profile measurement, axle load measurement | MB1 | ❌ |
| Forklift 5 t / 10 t / 20 t / 40 t, shunter | MB1 | ❌ |
| Mobile platform, iki katlı çelik platform, elevated platform | MB1, MB2 | Yapısal boyutlandırma var. Ekipman yok |
| Fume extractor, hydraulic bearing extractor, battery charger | MB1 | ❌ |
| Her hatta shore connection panel | MB1 | ❌ |
| Tren dış yıkama tesisi ve su geri kazanımı | Faz 2 | ❌ |
| AVIS (otomatik araç muayene sistemi) | Faz 2 | ❌ |
| CET servis sistemi, yakıt dolum pompası | Faz 2 | ❌ |
| DPS interlock (kapılar, pit aydınlatma, kren ve jack, bogie drop, platform, wheel lathe) ve DOCS | Tümü | ❌ (rail systems hariç) |
| Capital spares ve special tools (PS05) | — | ❌ |

---

## 4. Diğer önemli bulgular

1. **Program bid tarihine yetişmiyor.** ARX'in 8 haftalık takvimi NTP'den başlıyor ve teklif metni bid tarihinin 15.12.2026'dan ileri alınacağını varsayıyor. Bugünden kalan süre yaklaşık 4 hafta. Uzatma çıkmazsa final paket bid'den sonraya kalır.
2. **Bill 01 item 1.4 hariç.** RAMS, safety assurance ve cybersecurity ile tüm signalling, telecom, DPS ve DOCS hariç. Bunlar fiyat tablosunda ayrı Level 1 kalemler (1.4 ve 3.1–3.4). Ayrı bir sistem uzmanı gerekir.
3. **Survey ve geoteknik hariç, kendi verilerini kullanacak.** Toprak işleri ve temel metrajı varsayıma dayanacak. ARX bunu açıkça risk olarak yazmış.
4. **Kadro eksik.** Yangın mühendisi, sıhhi tesisat ve proses (su arıtma, yıkama, CET, yakıt) uzmanı, depo ekipmanı ve bakım planlama uzmanı yok. HVAC tek bir makine mühendisinde.
5. **Bina boyutları.** ARX birçok bina için "not stated in SoW" diyor. Diğer oturumun bütçesinde ise GEA değerleri var. Kaynakları karşılaştırılmalı.
6. **Ticari şartlar:** Sorumluluk limiti ücretle sınırlı, PI sigortası 10M USD. İhaleyi kazanırsak IFC tasarımında ARX'e münhasırlık şartı var. Bu, tasarımcı seçimini kısıtlar ve müzakere edilmeli.

---

## 5. Öneriler

**A – ARX'ten kapsam ilavesi istenirse (minimum):**
- Fire strategy özeti ve yangın hidrolik talebi
  - Bina bazında tehlike sınıfı
  - Sprinkler ve hidrant debisi
  - Depolama süresi
  - Tank hacmi ve yangın pompası seçimi
- HVAC blok yük hesabı (W/m² değil, bina bazında hesap), DX AHU adet ve kapasite listesi
- Elektrik yük listesi (SLD'ye dayanak), jeneratör ve trafo boyutlandırma notu
- Sıhhi tesisat ve endüstriyel atık su konsept şeması
  - Pit drenajı ve yağlı su ayırıcı
  - Yıkama tesisi su geri kazanımı
  - CET
- Atölye servisleri konsepti: basınçlı hava, fume extraction, shore connection
- Her MEP disiplini için ER ve SRES uyum matrisi (TD-01'den ayrı)
- BIM ve RVT teslim tutarsızlığının netleştirilmesi

**B – Ya da bu kısım bizde kalır (MEP firması olarak tercih edilebilir):**
- ARX kapsamı civil, track ve structure ile sınırlanıp ücret düşürülür.
- MEP tasarım bazı ve metrajı diğer oturumun **MEP BOQ R1** çalışmasıyla devam eder. Bu çalışmada 3.834 satır detay ve depo ekipmanı fiyatları zaten var.
- Depo ekipmanı listesi ve vendor teklifleri ayrıca toplanmalı. Wheel lathe, kren, jack, AVIS, yıkama ve CET için Appendix G onaylı vendor listesine bakılmalı. Bu teklifler ARX'in inşai hazırlık varsayımlarına input olarak verilmeli.

**C – Her durumda:**
- Bid tarihine göre program yeniden yazdırılmalı: final paket en geç ~8–10 Aralık.
- IFC münhasırlık maddesi çıkarılmalı ya da opsiyon olarak bırakılmalı.
- Signalling, telecom, DPS ve RAMS (1.4, 3.1–3.4) için ayrı sistem uzmanı teklifi alınmalı.
