# SAR NGW Dammam – ARX Boşluklarının İç Kaynakla Kapatılması (MEP ve Depo Ekipmanı)

**Bağlam:** ARX Tender Design Proposal (503-ARX-BD-PTD-005-00) MEP ve depo ekipmanında eksik. Eksikler `06_ARX_Teklif_Bosluk_Analizi.md` dosyasında. Ekibimizde 5 depo projesinde MEP ve depo ekipmanı tasarımı ile entegrasyonu yapmış bir uzman var. Bu rapor, bu eksiklerin ne kadarının iç tecrübeyle kapatılabileceğini, nelerin dışarıdan teyit gerektirdiğini ve ARX ile iş bölümünün nasıl olacağını gösteriyor.

**Ek dosya:** `07_Depo_Ekipmani_Arayuz_Listesi.xlsx`
- Sayfa 1: 41 ekipman satırı ve 18 arayüz sütunu. Boyut, ağırlık ve yük, temel/pit, elektrik, basınçlı hava, su, drenaj, egzoz, ısı yükü, data, DPS ve ATEX bilgileri.
- Sayfa 2: 20 kalemlik MEP tasarım bazı çıktı listesi.

---

## 1. Özet

| | |
|---|---|
| **İç tecrübeyle tamamen kapatılabilir** | MEP'in 16 eksik başlığından 13'ü. 15 ana depo ekipmanı grubunun tamamının arayüz verisi. |
| **Kısmen; dış teyit gerekir** | Su arıtma istasyonu (SWA lisanslı uzman). DPS interlock matrisi (rail systems uzmanı). Özel ekipmanların nihai verisi (wheel lathe, AVIS, yıkama tesisi; vendor). |
| **Bizim kapsamımız değil** | Signalling, telecom, GSM-R, DOCS yazılımı. RAMS ve cybersecurity (D3 1.4, 3.1–3.4). Survey ve geoteknik. Track, toprak işleri ve yapı (ARX'te kalır). |
| **Bütçedeki ağırlığı** | Diğer oturumun Budget R1 dosyasında MEP ve depo ekipmanı **44,3M USD**. Bu, toplam maliyetin (115,65M USD) **yaklaşık %38'i**. Yalnızca depo ekipmanı 19,1M USD (yaklaşık %16,5). |

**Sonuç:** Toplam maliyetin yaklaşık %38'i MEP ve depo ekipmanında. ARX bu kısmı benchmark metrajla bırakıyor. Bu kısım bizim tecrübemizle hesaba ve arayüz verisine dayalı hale getirilebilir. Ayrıca ARX'in pit, temel ve kren yolu boyutlandırması için ihtiyaç duyduğu ekipman verisini de **biz sağlarız**. Böylece ARX'in teklifinde "assumption" olarak bıraktığı riskin büyük kısmı ortadan kalkar.

---

## 2. MEP – kapsama matrisi

| # | Eksik başlık | Bizde | Not ve dış teyit |
|---|---|---|---|
| 1 | HVAC blok ısı yükü, DX AHU listesi | ✅ | Dammam iklim verisi (ASHRAE/SBC) |
| 2 | Havalandırma stratejisi ve SCADA alarmı | ✅ | Pit, akü, kompresör, dizel egzoz, fume |
| 3 | Fire Strategy özeti | ✅ | Nihai onay Civil Defense'ten |
| 4 | Yangın suyu hidrolik talebi, tank hacmi, pompa | ✅ | NFPA 13/14/20/24 ve SBC 801. Türk MMO/TS EN 12845 değil. |
| 5 | Clean agent (trafo merkezleri, SE ve sistem odaları) | ✅ | — |
| 6 | Yakıt ve CET alanı: köpük, gaz algılama, ATEX sınıflandırması | ✅ | NFPA 30 |
| 7 | Elektrik yük listesi; trafo, jeneratör ve UPS boyutu | ✅ | SEC bağlantı gücü |
| 8 | Shore power yükü, gerilimi ve PFC | ✅ | **SAR tren verisi gerekli** |
| 9 | Topraklama, yıldırım ve EMC | ✅ | — |
| 10 | Basınçlı hava sistemi | ✅ | — |
| 11 | Akışkan besleme istasyonu | ✅ | Tren bakım planı |
| 12 | Sıhhi tesisat ve NWC bağlantısı | ✅ | — |
| 13 | Endüstriyel atık su: pit drenajı, yağlı su ayırıcı, yıkama suyu geri kazanımı, CET | ✅ | Yıkama tesisi vendor verisi |
| 14 | Su arıtma istasyonu prosesi | ⚠️ Kısmen | SWA lisansı gerekiyor. Lisanslı alt yüklenici veya vendor. |
| 15 | ELV, BMS, SCADA nokta listesi | ✅ | SAR OCC arayüzü |
| 16 | MEP ER ve SRES uyum matrisi | ✅ | — |

---

## 3. Depo ekipmanı – vereceğimiz arayüz verisi

Excel listesinde her ekipman için sarı hücreler doldurulacak.

| Veri grubu | İçerik | Kime gider |
|---|---|---|
| Fiziksel | Boyut, ağırlık, tekerlek ve nokta yükleri | ARX (yapı, temel) |
| Fiziksel | Pit, gömülü ray, kren yolu açıklığı ve kotu | ARX (yapı, temel) |
| Elektrik | V, faz, kW/kVA, besleme tipi (bara, pano, priz), UPS ihtiyacı | Biz (yük listesi, SLD). ARX'in SLD'sine input |
| Mekanik | Basınçlı hava (bar, Nl/dk) | Biz (MEP hesapları) |
| Mekanik | Su, drenaj ve atık tipi | Biz (MEP hesapları) |
| Mekanik | Egzoz debisi, hidrolik yağ ve diğer akışkanlar, ısı yükü | Biz (MEP hesapları) |
| Kontrol | LAN, SCADA ve BMS bağlantısı | Biz ve rail systems uzmanı |
| Kontrol | DPS interlock gereği (kapı, pit ışığı, kren/jack, bogie drop, platform, lathe) | Biz ve rail systems uzmanı |
| Güvenlik | Yangın, ATEX ve güvenlik gereksinimi | Biz |

**Vendor teyidi önerilen ekipmanlar** (tecrübe verisi ilk aşamada yeterli, nihai teklif için vendor datası gerekir):
- Tandem underfloor wheel lathe: makine temeli, pit ve titreşim
- AVIS
- Drive-through yıkama tesisi ve geri kazanım ünitesi
- Bogie drop facility
- Senkronize lifting jack ve pit lifting table

Bu firmalar Appendix G (SAR Mandatory List) ile karşılaştırılmalı.

---

## 4. Budget R1 (diğer oturum) – tecrübeyle düzeltilmesi gereken noktalar

MEP BOQ'daki etiketler (ör. `307-AHU-SF-01`, `312-CBL-...`) başka bir depo projesinden aktarıldığını gösteriyor. Yani metrajlar benchmark. Kontrol edilmesi gerekenler:

1. **Sprinkler (MB1).** Yalnızca 128 sprinkler başlığı var (yaklaşık 3.100 USD); yangın tesisatının geri kalanı ayrıca kontrol edilmeli. 12.535 m²'lik atölye tamamen sprinkler'lı olacaksa bu sayı birkaç kat artar. Fire strategy kararı gerekiyor: atölye sprinkler'lı mı olacak, yoksa yalnız ofis ve depo alanları mı?
2. **Clean agent.** Hiç kalem yok. Trafo merkezleri, SE odaları ve sistem odaları için eklenmeli.
3. **Basınçlı hava.** Yalnızca boru kalemleri var (toplam yaklaşık 63 bin USD). Kompresör, kurutucu ve tank yok, oysa SOW MB1'de kompresör odası istiyor.
4. **Akışkan besleme istasyonu, pit aydınlatması ve yağlı su ayırıcı.** Kalem yok.
5. **Access control ve yıldırımdan korunma.** Kalem yok. Bütçede yalnızca topraklama var.
6. **Yakıt alanı.** Gaz algılama ve köpük sistemi yok.
7. **Bogie turntable.** Bütçede 4 adet. SOW'da adet yazmıyor; tren ve hat düzenine göre teyit edilmeli.
8. **Yangın suyu deposu.** 2.000 m³ varsayımı, hidrolik talep hesabıyla doğrulanmalı (madde 2.4).

---

## 5. ARX ile önerilen iş bölümü

| Alan | ARX | Biz |
|---|---|---|
| Track, toprak işleri, drenaj, yol, yapı, mimari layout | ✅ | Input: ekipman yükleri ve pit verisi |
| Elektrik SLD | ✅ (çizim) | Yük listesi ve kriterler. Alternatif olarak tamamı bizde. |
| HVAC, sıhhi tesisat, yangın, ELV, BMS: tasarım bazı ve metraj | — | ✅ |
| Depo ekipmanı: liste, arayüz verisi, metraj, vendor | — | ✅ |
| Pit, temel, kren yolu boyutlandırma | ✅ | Input veririz |
| Rail systems, DPS sistem tasarımı, RAMS | — | — (ayrı uzman) |

**Ticari etkisi:**
- ARX'ten "MEP quantities derived per building" kalemi çıkarılabilir; SLD kalemi isteğe bağlı. Bunun karşılığında ücret indirimi istenebilir.
- ARX'in program riski azalır. Teklifinde risk olarak yazdığı "equipment data not available" maddesini 1–2. haftada biz karşılarız.
- IFC münhasırlık maddesi en azından MEP ve ekipman kapsamı için kaldırılmalı.

---

## 6. Takvim (bid tarihi 15.12.2026)

| Hafta | İş |
|---|---|
| 1 (18–24 Kas) | Ekipman arayüz listesinin doldurulması (tecrübe verisi). Vendor talepleri gönderilir. |
| 2 (25 Kas – 1 Ara) | ARX'e ekipman inputu. HVAC ve elektrik yük hesabı. Yangın hidroliği ve tank hacmi. |
| 3 (2–8 Ara) | MEP BOQ revizyonu (madde 4). Uyum matrisi. Vendor verisiyle güncelleme. |
| 4 (9–15 Ara) | Fiyatlamaya son input. Teknik teklif MEP metodolojisi. Varsayım ve çekince listesi. |

---

## 7. Riskler ve dikkat edilecekler

- **Tecrübe verisinin geçerliliği.** Değerler SAR'ın yeni 20 intercity trenine göre teyit edilmeli: dingil yükü, rake uzunluğu, dizel veya bimode, shore besleme gerilimi. SOW "Reference documents for the equipment design are available" diyor; bu dokümanlar SAR'dan istenmeli.
- **Lump sum ve yeniden ölçüm yok.** Tecrübeyle alınan her değer Excel'in "Veri kaynağı" sütununda işaretlenmeli. Belirsiz kalanlar teklifte varsayım olarak yazılmalı.
- **Faz ayrımı.** Ekipmanın çoğu MB1'de (Section A, kesin kapsam). Wheel lathe Section B'de; AVIS, yıkama, CET ve yakıt Faz 2'de, yani opsiyon. Buna rağmen tüm tasarım kesin kapsamda, dolayısıyla Faz 2 ekipman arayüzleri de şimdi tasarlanmalı.
