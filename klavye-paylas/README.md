# Klavye Paylaş — Windows klavyesini Mac'te kullan

Windows laptopun klavyesi ve faresi (touchpad dahil) aynı ağdaki Mac'i yönetir.

| Tuş | Ne olur |
|---|---|
| **↓ (aşağı ok)** | Klavye ve fare **Mac'e** geçer. Windows artık tuş/fare almaz. |
| **↑ (yukarı ok)** | **Windows'a** geri döner. Mac modundayken ↑ Mac'e gönderilmez, her zaman Windows'a aittir. |

- Geçiş sadece ok tuşuna **tek başına** basınca olur. `Shift+↓`, `Ctrl+↑` gibi kombinasyonlar o an aktif olan bilgisayara normal gider (metin seçmek vb. için).
- Bunun bedeli: Windows modunda tek başına ↓, Mac modunda tek başına ↑ kullanılamaz. Başka tuş istersen `windows_taraf.py` içindeki `GIT_TUSU` / `DON_TUSU` değerlerini değiştir ([VK kodları](https://learn.microsoft.com/windows/win32/inputdev/virtual-key-codes)).
- Geçişte kısa bir bip sesi çalar (Mac'e: tiz, Windows'a: pes). Kapatmak için `--sessiz`.
- Bağlantı koparsa klavye otomatik olarak Windows'a döner, kilitli kalmazsın.
- Trafik iki tarafta girdiğin şifreyle **şifrelenir**; ağdaki başka biri tuşlarını göremez ve Mac'e tuş gönderemez.

## Kurulum

Bu `klavye-paylas` klasörünü iki bilgisayara da kopyala. İkisinde de [Python 3.9+](https://www.python.org/downloads/) olmalı.

### Mac

**`mac_baslat.command`** dosyasına çift tıkla. İlk seferde gerekli paketleri kendisi kurar.
(`.py` dosyasına çift tıklama, düzenleyicide açılır.)

- "Geliştiricisi doğrulanamadı" derse: dosyaya **sağ tık → Aç → Aç**.
- **Sistem Ayarları → Gizlilik ve Güvenlik → Erişilebilirlik** bölümünde Terminal'e izin ver, pencereyi kapatıp dosyaya tekrar çift tıkla.
- "Gelen bağlantılara izin verilsin mi?" sorusuna **İzin Ver** de.

### Windows

**`windows_baslat.bat`** dosyasına çift tıkla. İlk seferde gerekli paketleri kendisi kurar.
Python kurarken **"Add python.exe to PATH"** kutusunu işaretlemeyi unutma. Windows Güvenlik Duvarı sorarsa **Özel ağlar** için izin ver.

İki tarafta da aynı şifreyi gir. Windows, Mac'i ağda kendisi bulur ve `[+] Mac'e baglanildi` yazar. Artık **↓** ile Mac'e, **↑** ile Windows'a geçebilirsin.

## Seçenekler

**Mac (`mac_taraf.py`)**

| Seçenek | Açıklama |
|---|---|
| `--sifre X` | Şifreyi sormadan ver |
| `--ctrl-cmd` | Windows'taki **Ctrl** Mac'te **Cmd** gibi çalışsın (Ctrl+C = kopyala, Ctrl+V = yapıştır). Windows tuşu da Control olur. |
| `--hiz 1.5` | Fare hızı çarpanı |
| `--teker-hiz 40` | Bir teker/kaydırma adımında kaç piksel kaysın |

Varsayılan tuş eşlemesi: Ctrl → Control, Windows tuşu → Cmd, Alt → Option, AltGr → sağ Option.

**Windows (`windows_taraf.py`)**

| Seçenek | Açıklama |
|---|---|
| `--sifre X` | Şifreyi sormadan ver |
| `--mac-ip 192.168.1.20` | Otomatik bulma çalışmazsa Mac'in IP'sini elle ver (Mac'te: Sistem Ayarları → Wi-Fi → Ayrıntılar) |
| `--sessiz` | Bip sesini kapat |

## Bilinmesi gerekenler

- Tuşlar **konuma göre** gönderilir; hangi harfin çıkacağını Mac'te seçili klavye düzeni belirler. Windows'ta Türkçe Q kullanıyorsan Mac'te de **Türkçe Q** düzenini seç.
- Windows'ta **yönetici olarak çalışan** bir pencere öndeyken tuşlar yakalanamaz. Gerekirse `windows_taraf.py`'yi de yönetici olarak çalıştır.
- `Ctrl+Alt+Del` her zaman Windows'a gider (Windows buna izin vermez).
- Mac'te **Caps Lock** sanal olarak açılıp kapatılamıyor; büyük harf için Shift kullan.
- Mac'te ISO klavyelerde `<` ve `"` tuşlarının yeri ters çıkarsa `mac_taraf.py` içindeki `0x29` ve `0x56` eşlemelerini yer değiştir.
- Kullanılan portlar: TCP 24800 (bağlantı), UDP 24801 (Mac'i ağda bulma).
