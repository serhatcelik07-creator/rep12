# TMO Mardin Hizmet Binası — Mekanik Ekipman Elektrik Güçleri

`TEMİZ_1.dxf` mimari planına mekanik ekipmanlar sembolleriyle işlendi. Her cihazın yanına elektrik gücü ve gerilim bilgisi yazıldı. Ayrıca elektrik projesine esas olacak tablolar ve ofis soğutma yükü hesabı hazırlandı.

## Dosyalar

| Dosya | İçerik |
|---|---|
| `TEMIZ_1_MEKANIK_ELEKTRIK_GUCLERI.dxf` | Zemin, 1. ve 2. kat planlarında semboller, cihaz kodları ve kW / V / faz etiketleri. Her kat paftasında o katın güç tablosu var. Yeni **07** paftasında genel güç tablosu, soğutma yükü + VRF iç ünite tablosu, VRF dış ünite tablosu, sembol lejantı ve notlar yer alıyor. |
| `TMO_MARDIN_MEKANIK_EKIPMAN_ELEKTRIK_GUCLERI.xlsx` | Formüllü tablolar. Sayfalar: Elektrik Güç Tablosu · Pano ve Kat Özeti · Tablolar · **Soğutma Yükü** · VRF İç Üniteler · VRF Dış Üniteler |
| `onizleme/*.png` | Paftaların önizlemeleri |
| `scripts/` | Çizimi ve Excel'i yeniden üreten Python betikleri (ezdxf, openpyxl) |

## DXF katmanları
`MEK-ELK-VRF-IC`, `MEK-ELK-VRF-DIS`, `MEK-ELK-ISITMA`, `MEK-ELK-SIHHI`, `MEK-ELK-HVL`, `MEK-ELK-KLIMA`, `MEK-ELK-ETIKET`, `MEK-ELK-GUC` (kW/V yazıları), `MEK-ELK-TABLO`, `MEK-ELK-KAIDE`. Mimari katmanlara dokunulmadı.

## Özet (kurulu / talep)
- VRF klima: 3 dış ünite toplam 48,6 kW (400V 3N~) + 37 kaset iç ünite. Dış üniteler kuzey cephe bahçesinde, beton kaide üzerinde (çatıda değil).
- Z-10 Server + Z-11 Elektrik Ana Pano odası: ortak multi split. 2 duvar tipi iç ünite (3,5 + 2,5 kW), 1 asıl (MSP-1) + 1 yedek (MSP-1Y) dış ünite (6,8 kW, 2,10 kW elektrik, 7/24). Ana dağıtım panosundan (ADP) beslenir.
- Isıtma, sıhhi tesisat, yağmur suyu ve havalandırma: yaklaşık 9,4 kW
- **Mekanik toplam: 62,2 kW kurulu / 59,0 kW talep** (yedek cihazlar talebe katılmaz)

## Kaynaklar ve varsayımlar
- Kazan (2×80 kW), pompa debi/basma, boyler (500 L), sirkülasyon, hidrofor ve yağmur suyu değerleri TMO Mardin hesap Excel'lerinden alındı. Cihaz yerleşimi `mardin_2` ve `ısıtma_v11` taslaklarından alındı.
- Fan, davlumbaz, VRF tip ve güç değerleri TMO Edirne örnek projesindeki gibi alındı.
- Soğutma yükü basitleştirilmiş CLTD/CLF yöntemiyle hesaplandı. Tasarım şartları: dış 38,5 °C, iç 24 °C. Kuzey oku planda sağ-alta bakıyor (≈ −53°). Pencere ve duvar metrajı DXF'ten çıkarıldı. AL1/AL5 şerit pencerelerde kat başına 3,50 m cam yüksekliği varsayıldı.
- Cihaz güçleri ön seçim değerleridir. Malzeme onayından sonra katalog değerleriyle elektrik projesi revize edilmelidir.
