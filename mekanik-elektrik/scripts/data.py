# -*- coding: utf-8 -*-
"""TMO Mardin Hizmet Binası - mekanik ekipman elektrik güç verileri (DXF ve Excel ortak kaynak)."""

# Kat -> plan x-offset (TEMİZ_1.dxf içinde paftalar 6000 birim aralıklı)
KAT_AD = {'Z': 'ZEMİN KAT', '1': '1. KAT', '2': '2. KAT'}
KAT_DX = {'Z': 0, '1': 6000, '2': 12000}

# VRF kaset/gizli tavan tipleri (Edirne TMO VRF projesi tablosu ile aynı tip numaraları)
VRF_TIP = {
    2.2: ('TİP-21', 'Kaset Tip 4 Yöne Üflemeli', 2.5, 0.050, '570x570x260'),
    2.8: ('TİP-22', 'Kaset Tip 4 Yöne Üflemeli', 3.2, 0.050, '570x570x260'),
    3.6: ('TİP-23', 'Kaset Tip 4 Yöne Üflemeli', 4.0, 0.060, '570x570x260'),
    4.5: ('TİP-24', 'Kaset Tip 4 Yöne Üflemeli', 5.0, 0.060, '570x570x260'),
    5.6: ('TİP-25', 'Kaset Tip 4 Yöne Üflemeli', 6.3, 0.062, '570x570x260'),
    7.1: ('TİP-26', 'Kaset Tip 4 Yöne Üflemeli', 8.0, 0.062, '840x840x204'),
}

# Ofis / çalışma mahalleri: (kat, mahal no, mahal adı, alan m², [ünite kapasiteleri kW], VRF sistemi, bbox override)
# Kapasite ön seçimi: Mardin yaz dış tasarım 38-40 °C için ~150 W/m² (konferans/mescit kalabalık mahallerde artırıldı).
VRF_ODALAR = [
    ('Z', '04',   'GÜVENLİK-DANIŞMA', 8.35,  [2.2],      'VRF-1', None),
    ('Z', '09/A', 'YEMEKHANE',        42.50, [3.6, 3.6], 'VRF-1', None),
    ('Z', '28',   'DİNLENME ALANI',   19.70, [3.6],      'VRF-1', None),
    ('Z', '24/A', 'MİSAFİRHANE-1',    17.66, [2.8],      'VRF-1', (6049, 2235, 6404, 2557)),
    ('Z', '25/A', 'MİSAFİRHANE-2',    22.15, [3.6],      'VRF-1', (6444, 2235, 6809, 2557)),
    ('Z', '26/A', 'MİSAFİRHANE-3',    16.07, [2.8],      'VRF-1', (6494, 1005, 6809, 1290)),
    ('Z', '27/A', 'MİSAFİRHANE-4',    16.40, [2.8],      'VRF-1', (6149, 1005, 6474, 1290)),
    ('1', '13',   'OFİS',             42.65, [3.6, 3.6], 'VRF-1', None),
    ('1', '14',   'ÇOCUK BAKIM/OYUN', 43.80, [3.6, 3.6], 'VRF-1', None),
    ('1', '19',   'OFİS',             27.50, [4.5],      'VRF-1', None),
    ('1', '20',   'OFİS',             24.15, [4.5],      'VRF-1', None),
    ('1', '06',   'OFİS',             21.80, [3.6],      'VRF-1', None),
    ('1', '07',   'OFİS',             24.00, [3.6],      'VRF-1', None),
    ('1', '08',   'OFİS',             19.48, [3.6],      'VRF-1', None),
    ('1', '09',   'OFİS',             24.53, [4.5],      'VRF-1', None),
    ('1', '10',   'OFİS',             39.90, [3.6, 3.6], 'VRF-1', None),
    ('1', '11',   'OFİS',             39.65, [3.6, 3.6], 'VRF-1', None),
    ('2', '15',   'MÜDÜR YARD. ODASI', 24.00, [3.6],     'VRF-2', None),
    ('2', '16',   'HUKUK SERVİSİ',    23.75, [3.6],      'VRF-2', None),
    ('2', '17',   'BAŞ MÜŞAVİR ODASI', 22.95, [3.6],     'VRF-2', None),
    ('2', '24/B', 'KADIN MESCİT',     15.37, [2.8],      'VRF-2', None),
    ('2', '25/B', 'ERKEK MESCİT',     16.26, [3.6],      'VRF-2', None),
    ('2', '06',   'OFİS',             21.80, [3.6],      'VRF-2', None),
    ('2', '07',   'OFİS',             24.00, [3.6],      'VRF-2', None),
    ('2', '08',   'OFİS',             18.48, [2.8],      'VRF-2', None),
    ('2', '09',   'OFİS',             24.55, [4.5],      'VRF-2', None),
    ('2', '10',   'KONFERANS SALONU', 43.05, [4.5, 4.5], 'VRF-2', None),
    ('2', '11',   'SEKRETERYA',       14.45, [2.8],      'VRF-2', None),
    ('2', '12',   'BAŞ MÜDÜR ODASI',  42.17, [3.6, 3.6], 'VRF-2', None),
    ('2', '13',   'MÜDÜR YARD. ODASI', 21.92, [3.6],     'VRF-2', None),
]

# VRF dış üniteler: (sistem, modül, HP, soğutma kW, elektrik kW, ölçü, hizmet ettiği katlar)
VRF_DIS = [
    ('VRF-1', 'VRF-1A', 12, 33.5, 13.80, '1240x765x1690', 'Zemin Kat + 1. Kat'),
    ('VRF-1', 'VRF-1B', 14, 40.0, 16.40, '1240x765x1690', 'Zemin Kat + 1. Kat'),
    ('VRF-2', 'VRF-2A', 10, 28.0, 11.25, '930x765x1690', '2. Kat'),
    ('VRF-2', 'VRF-2B', 10, 28.0, 11.25, '930x765x1690', '2. Kat'),
]

# Diğer mekanik ekipmanlar
# kod, sistem, ad, özellik, mahal, kat, adet, çalışan adet, birim kW, gerilim, faz, cosφ, pano, sembol, konum(x,y TEMİZ koordinatı), kaynak
EKIPMAN = [
    # --- ISITMA (Teshin Merkezi) ---
    ('KZ-1', 'ISITMA', 'Yoğuşmalı Duvar Tipi Doğalgaz Kazanı', '80 kW, kaskad, 70/55 °C, dahili primer pompa', 'TESHİN MERKEZİ', 'Z', 1, 1, 0.30, 230, 1, 0.90, 'MP', 'KAZAN', (4185, 2175), 'KAZAN_BORU_POMPA_HESABI: 2x80 kW'),
    ('KZ-2', 'ISITMA', 'Yoğuşmalı Duvar Tipi Doğalgaz Kazanı', '80 kW, kaskad, 70/55 °C, dahili primer pompa', 'TESHİN MERKEZİ', 'Z', 1, 1, 0.30, 230, 1, 0.90, 'MP', 'KAZAN', (4250, 2175), 'KAZAN_BORU_POMPA_HESABI: 2x80 kW'),
    ('KP-1', 'ISITMA', 'Kaskad Kontrol Paneli', 'Dış hava kompanzasyonlu, BMS bağlantılı', 'TESHİN MERKEZİ', 'Z', 1, 1, 0.05, 230, 1, 0.90, 'MP', 'PANEL', (4185, 2125), 'Isıtma v11 kazan dairesi şeması'),
    ('P-1', 'ISITMA', 'Radyatör Devresi Sirkülasyon Pompası', 'İkiz, frekans kontrollü ıslak rotorlu; Q=4,43 m³/h, H=2,24 mSS', 'TESHİN MERKEZİ', 'Z', 2, 1, 0.20, 230, 1, 0.85, 'MP', 'POMPA2', (4335, 2180), 'KAZAN_BORU_POMPA_HESABI sf.4'),
    ('P-2', 'ISITMA', 'Boyler Devresi Sirkülasyon Pompası', 'İkiz, ıslak rotorlu; Q=3,5 m³/h (60,7 kW, ΔT=15 K), H≈3 mSS', 'TESHİN MERKEZİ', 'Z', 2, 1, 0.15, 230, 1, 0.85, 'MP', 'POMPA2', (4420, 2180), 'BOYLER_HESABI: 60,7 kW'),
    ('SP-1', 'SIHHİ TESİSAT', 'Kullanım Sıcak Suyu Resirkülasyon Pompası', 'Q=0,4 m³/h, H=0,5 mSS, bronz gövde', 'TESHİN MERKEZİ', 'Z', 1, 1, 0.05, 230, 1, 0.85, 'MP', 'POMPA', (4505, 2180), 'SİRKÜLASYON_POMPASI_HESABI'),
    ('B-1', 'SIHHİ TESİSAT', 'Serpantinli Boyler', '500 L, kazan beslemeli (elektriksiz)', 'TESHİN MERKEZİ', 'Z', 1, 1, 0.00, 0, 0, 1.0, '-', 'BOYLER', (4600, 2165), 'BOYLER_HESABI: 500 L'),
    ('GD-1', 'ISITMA', 'Doğalgaz Kaçak Dedektörü + Selenoid Vana', 'Sesli/ışıklı alarm, NC selenoid', 'TESHİN MERKEZİ', 'Z', 1, 1, 0.02, 230, 1, 0.90, 'MP', 'GAZ', (4440, 1955), 'Doğalgaz iç tesisat esasları'),
    ('EF-01', 'HAVALANDIRMA', 'Teshin Merkezi Taze Hava Fanı', 'Kanal tipi aksiyal, ex-proof, 750 m³/h', 'TESHİN MERKEZİ', 'Z', 1, 1, 0.20, 230, 1, 0.85, 'MP', 'FAN', (4190, 1950), 'Edirne HVL EF-01 eşdeğeri'),
    ('EF-02', 'HAVALANDIRMA', 'Teshin Merkezi Egzost Fanı', 'Kanal tipi aksiyal, ex-proof, 500 m³/h', 'TESHİN MERKEZİ', 'Z', 1, 1, 0.20, 230, 1, 0.85, 'MP', 'FAN', (4290, 1950), 'Edirne HVL EF-02 eşdeğeri'),
    # --- TEMİZ SU (Su Deposu) ---
    ('HD-1', 'SIHHİ TESİSAT', 'Temiz Su Hidroforu (Paket)', '2 pompalı, frekans konv.; Q=2x1,12 m³/h, Palt=2,9 / Püst=4,4 bar, 100 L tank', 'YAĞ.SİS. VE GENEL SU DEPOSU', 'Z', 2, 2, 0.75, 400, 3, 0.85, 'MP', 'HIDROFOR', (4210, 2400), 'TEMİZ_SU_DEPO_HİDROFOR_HESABI'),
    # --- YAĞMUR SUYU ---
    ('SH-1', 'YAĞMUR SUYU', 'Bahçe Sulama Hidroforu', '2 pompalı, yağmur suyu deposundan; 1000 m² bahçe', 'MANEVRA ODASI (BAHÇE)', 'Z', 2, 1, 0.75, 230, 1, 0.85, 'MP', 'HIDROFOR', (3980, 2800), 'YAĞMUR_SUYU_HESABI / mardin_2'),
    ('YP-1', 'YAĞMUR SUYU', 'Yağmur Suyu Deposu Taşma/Boşaltma Dalgıç Pompası', '12 m³ gömülü depo, flatörlü', 'YAĞMUR SUYU DEPOSU (BAHÇE)', 'Z', 1, 1, 1.10, 230, 1, 0.85, 'MP', 'DALGIC', (3700, 2850), 'Edirne yağmur suyu (1-1,5 kW)'),
    # --- HAVALANDIRMA ---
    ('EF-03', 'HAVALANDIRMA', 'Zemin Kat WC / Personel Egzost Fanı', 'Kanal tipi, 500 m³/h, hız anahtarlı', 'WC HOLÜ', 'Z', 1, 1, 0.20, 230, 1, 0.85, 'ZKTP', 'FAN', (5465, 2145), 'Mimari not: MEK.HVL.'),
    ('EF-04', 'HAVALANDIRMA', 'Misafirhane Banyo + Çamaşırhane Egzost Fanı', 'Kanal tipi, 450 m³/h', 'MİSAFİRHANE KORİDOR', 'Z', 1, 1, 0.20, 230, 1, 0.85, 'ZKTP', 'FAN', (6700, 1745), 'Edirne HVL EF-05 eşdeğeri'),
    ('ASP-1', 'HAVALANDIRMA', 'Mutfak Davlumbaz Aspiratörü', 'Ankastre, karbon filtreli, 650 m³/h', 'MUTFAK', 'Z', 1, 1, 0.20, 230, 1, 0.85, 'ZKTP', 'DAVLUMBAZ', (4445, 1335), 'Edirne HVL ASP-1 eşdeğeri'),
    ('EF-05', 'HAVALANDIRMA', '1. Kat WC Grubu Egzost Fanı', 'Kanal tipi, 600 m³/h, hız anahtarlı', 'WC HOLÜ', '1', 1, 1, 0.25, 230, 1, 0.85, '1KTP', 'FAN', (11946, 2185), 'Mimari not: MEK.HVL.'),
    ('EF-06', 'HAVALANDIRMA', '2. Kat WC Grubu Egzost Fanı', 'Kanal tipi, 600 m³/h, hız anahtarlı', 'WC HOLÜ', '2', 1, 1, 0.25, 230, 1, 0.85, '2KTP', 'FAN', (17946, 2185), 'Mimari not: MEK.HVL.'),
    ('EF-07', 'HAVALANDIRMA', 'Abdesthane Egzost Fanı', 'Kanal tipi, 400 m³/h', 'ABDESTHANELER', '2', 1, 1, 0.20, 230, 1, 0.85, '2KTP', 'FAN', (18180, 2255), 'Edirne HVL EF-04 eşdeğeri'),
    # --- KLİMA (VRF dışı) ---
    ('MK-1', 'KLİMA', 'VRF Merkezi Kumanda', 'Dokunmatik, tüm iç üniteler', 'GÜVENLİK-DANIŞMA', 'Z', 1, 1, 0.02, 230, 1, 0.90, 'ZKTP', 'KUMANDA', (5700, 1700), 'Edirne VRF notu'),
    ('SPLT-1', 'KLİMA', 'Server Odası Split Klima (İç+Dış)', '12.000 Btu/h (3,5 kW), 7/24, 1 asıl + 1 yedek', 'SERVER ODASI', 'Z', 2, 1, 1.10, 230, 1, 0.90, 'ZKTP', 'SPLIT', (3530, 1135), 'Edirne SPLT-1 eşdeğeri'),
]

# VRF dış ünite konumu (bahçe, kuzey cephe, beton kaide üzerinde)
VRF_DIS_KONUM = {'VRF-1A': (4720, 2720), 'VRF-1B': (4870, 2720), 'VRF-2A': (5040, 2720)}
SPLIT_DIS_KONUM = [(3440, 850), (3560, 850)]
YAGMUR_DEPO = (3600, 2770, 3880, 2930)   # gömülü depo dikdörtgeni

# Elle konumlandırılan iç üniteler (küçük/etiketle çakışan mahaller): (x, y, etiket yönü 'B'=alt, 'R'=sağ)
VRF_POS = {('Z', '04'): [(5395, 1715, 'B')], ('Z', '26/A'): [(6600, 1048, 'R')]}

# Mahal birim soğutma yükü ön değerleri (W/m²) - varsayılan 150
WM2 = {('Z', '09/A'): 160, ('2', '10'): 200, ('2', '24/B'): 180, ('2', '25/B'): 180}
