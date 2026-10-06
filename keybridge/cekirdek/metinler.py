"""Arayuz metinleri (Turkce / Ingilizce). Sistem dili Turkce degilse Ingilizce."""

_METINLER = {
    # ---- genel ----
    "baslik": ("KeyBridge", "KeyBridge"),
    "araniyor": ("Mac aranıyor… Mac'te KeyBridge açık mı?", "Looking for your Mac… Is KeyBridge open on the Mac?"),
    "mac_secin": ("Birden fazla Mac bulundu. Aşağıdan birini seçin.", "More than one Mac found. Choose one below."),
    "baglaniyor": ("{ad} cihazına bağlanılıyor…", "Connecting to {ad}…"),
    "kod": ("{ad} ekranında bu kodu görüp İzin Ver'e basın:\n{kod}",
            "On {ad}, check this code and click Allow:\n{kod}"),
    "bagli": ("Bağlı: {ad}. Mac'e geçmek için {tus}.", "Connected to {ad}. Press {tus} to switch to the Mac."),
    "mac_modunda": ("Klavye ve fare şu an Mac'te. Geri dönmek için {tus}.",
                    "Keyboard and mouse are on the Mac. Press {tus} to come back."),
    "reddedildi": ("Bağlanılamadı: {neden}", "Could not connect: {neden}"),
    "koptu": ("{ad} bağlantısı koptu, yeniden deneniyor…", "Lost connection to {ad}, retrying…"),
    # ---- Windows ayarlar penceresi ----
    "bolum_baglanti": ("Bağlantı", "Connection"),
    "mac": ("Mac:", "Mac:"),
    "eslesmeyi_kaldir": ("Eşleşmeyi kaldır", "Unpair"),
    "bolum_kisayollar": ("Kısayollar", "Shortcuts"),
    "maca_gec": ("Mac'e geç:", "Switch to Mac:"),
    "windowsa_don": ("Windows'a dön:", "Back to Windows:"),
    "degistir": ("Değiştir", "Change"),
    "tusa_basin": ("Bir tuşa ya da kombinasyona basın…", "Press a key or a combination…"),
    "ayni_kisayol": ("İki kısayol aynı olamaz.", "The two shortcuts must be different."),
    "kisayol_ipucu": ("Tek tuşlu kısayol sadece tek başına basınca çalışır; Shift+↓ gibi kombinasyonlar normal çalışmaya devam eder.",
                      "A single-key shortcut works only when pressed alone; combinations like Shift+↓ keep working as usual."),
    "bolum_fare": ("Fare ve klavye", "Mouse and keyboard"),
    "fare_hizi": ("Fare hızı", "Pointer speed"),
    "teker_hizi": ("Kaydırma hızı", "Scroll speed"),
    "teker_ters": ("Kaydırma yönünü ters çevir", "Reverse scroll direction"),
    "ctrl_cmd": ("Ctrl tuşu Mac'te Cmd gibi çalışsın (Ctrl+C = Kopyala)", "Use Ctrl as Cmd on the Mac (Ctrl+C = Copy)"),
    "ses": ("Geçişte ses çal", "Play a sound when switching"),
    "bolum_lisans": ("Lisans", "License"),
    "satin_al": ("Satın al", "Buy"),
    "lisans_tam": ("Lisanslı. Teşekkürler!", "Licensed. Thank you!"),
    "lisans_deneme": ("Deneme sürümü: {gun} gün kaldı", "Free trial: {gun} days left"),
    "lisans_deneme_suresiz": ("Deneme sürümü", "Free trial"),
    "lisans_bitti": ("Deneme süresi bitti. Kullanmaya devam etmek için lisans satın alın.",
                     "Your free trial has ended. Buy a license to keep using KeyBridge."),
    "lisans_gelistirici": ("Geliştirici sürümü", "Developer build"),
    "kullanilamaz_lisans": ("Deneme süresi bitti. Geçiş için lisans gerekli.", "Your trial has ended. A license is needed to switch."),
    "arkaplan_notu": ("Pencereyi kapatınca KeyBridge görev çubuğunun sağındaki simgede çalışmaya devam eder.",
                      "When you close this window, KeyBridge keeps running in the notification area."),
    "menu_ayarlar": ("Ayarlar", "Settings"),
    "menu_cikis": ("Çıkış", "Quit"),
    # ---- Mac menusu ----
    "mac_bekleniyor": ("Windows bekleniyor", "Waiting for Windows"),
    "mac_bagli": ("Bağlı: {ad}", "Connected: {ad}"),
    "mac_kontrol_mac": ("Klavye/fare: Mac'te", "Keyboard/mouse: on this Mac"),
    "mac_kontrol_win": ("Klavye/fare: Windows'ta", "Keyboard/mouse: on Windows"),
    "mac_izin_gerekli": ("Erişilebilirlik izni gerekli…", "Accessibility permission needed…"),
    "mac_izin_aciklama": ("KeyBridge'in Windows'tan gelen tuşları ve fareyi uygulayabilmesi için Sistem Ayarları > Gizlilik ve Güvenlik > Erişilebilirlik bölümünde KeyBridge'i açın.",
                          "To apply keys and mouse movement from Windows, turn on KeyBridge in System Settings > Privacy & Security > Accessibility."),
    "mac_ayarlari_ac": ("Ayarları Aç", "Open Settings"),
    "mac_eslesmeleri_sifirla": ("Eşleşmeleri sıfırla", "Forget paired PCs"),
    "mac_giriste_baslat": ("Oturum açılınca başlat", "Open at login"),
    "mac_onay_baslik": ("{ad} bağlanmak istiyor", "{ad} wants to connect"),
    "mac_onay_metin": ("Windows bilgisayarında da bu kod görünüyorsa İzin Ver'e basın:\n\n{kod}\n\nİzin verirseniz o bilgisayarın klavyesi ve faresi bu Mac'i kontrol edebilir.",
                       "If the Windows PC shows the same code, click Allow:\n\n{kod}\n\nThat PC's keyboard and mouse will then be able to control this Mac."),
    "izin_ver": ("İzin Ver", "Allow"),
    "reddet": ("Reddet", "Deny"),
    "cikis": ("KeyBridge'den çık", "Quit KeyBridge"),
}

_turkce = False


def dil_ayarla(turkce):
    global _turkce
    _turkce = bool(turkce)


def T(anahtar, **degerler):
    tr, en = _METINLER[anahtar]
    metin = tr if _turkce else en
    return metin.format(**degerler) if degerler else metin
