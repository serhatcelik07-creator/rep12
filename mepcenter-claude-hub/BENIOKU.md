# MepCenter Claude Hub

Bütün Claude'larının (Mac, Windows, laptop, claude.ai web/mobil, Cowork) ortak hafızası ve iletişim merkezi.
Adresi: **https://mepcenter.com.tr/claude**

- **Görev kodu:** Herhangi bir Claude'a `kod matwar` ya da `mepcenter'a git, matwar görevine bak, devam edelim`
  dediğinde Claude o görevin son durumunu, kararlarını, tüm konuşmalarını, dosyalarını ve şu an kimin
  üzerinde çalıştığını okur, sonra kaldığı yerden devam eder.
- **Tam kayıt:** Claude Code oturumlarında her istek, cevap, araç çağrısı, yazılan/düzenlenen her kod ve
  komut çıktısı otomatik olarak hub'a yazılır. Değişen dosyalar da yüklenir. Gizli anahtarlar maskelenir,
  `.env` gibi dosyalar yüklenmez.
- **Yönetim paneli:** Oturumlar, canlı sohbet, görevler, kayıtlar, dosyalar, ortak veri, ajan/token
  yönetimi ve Claude talimatı tek yerde.
- **Köprü ajanı (7/24):** Bilgisayar açılınca başlar. Panelden o bilgisayara yazdığın işi oradaki
  Claude Code'a yaptırır ve cevabı panele yazar.
- **Güvenlik:** Hub'a sadece senin oluşturduğun token'larla bağlanılır. Her bilgisayara ayrı token
  verilir, panelden tek tıkla iptal edilir. Panelin kendi şifresi ve deneme sınırı vardır.

```
sunucu/claude/   → sitene yüklenecek klasör (public_html/claude)
istemci/         → her bilgisayara kurulacak küçük Python programı (kur.py)
```

---

## 1. Sunucu kurulumu (bir kez)

1. cPanel'de `mepcente_claude` veritabanını ve aynı adlı kullanıcıyı oluştur. Kullanıcıya veritabanında
   **tüm yetkileri** ver.
2. `sunucu/claude` klasörünü `public_html/claude` olarak yükle. (Zip'i cPanel Dosya Yöneticisi'nde
   açabilirsin.)
3. Tarayıcıda **https://mepcenter.com.tr/claude/install.php** adresini aç:
   - Veritabanı: `localhost`, `mepcente_claude`, `mepcente_claude`, şifre
   - Panel girişi: kullanıcı adı `claude` ve **yeni, güçlü bir şifre**. Sohbette yazdığın şifreyi kullanma.
   - İlk ajan: örn. `mac-claude`. Gösterilen token'ı kopyala, yalnızca bir kez görünür.
4. Kurulum bitince `install.php` kendini kilitler. Panel: **https://mepcenter.com.tr/claude/admin/**

Gereksinimler: PHP 7.4+ (8.x önerilir), MySQL 5.7+ / MariaDB 10.3+, HTTPS.
Yükleme sınırı varsayılan 20 MB. Büyük dosyalar için PHP `post_max_size` / `upload_max_filesize`
ayarlarını cPanel'den yükselt.

## 2. Her bilgisayar için token

Panel → **Ajanlar / Token** → `mac-claude`, `windows-claude`, `laptop-claude`, `web-claude` gibi ayrı ajanlar
oluştur. Bir cihaz kaybolursa sadece onun token'ını iptal et.

## 3. Bilgisayara kurulum (Mac / Windows)

**Python gerekir** (başka program gerekmez):
- **Mac:** Terminal'de `python3 --version` yaz. Yoksa `xcode-select --install` ile kurulur
  (ya da python.org'dan indir).
- **Windows:** python.org'dan Python 3 kur. Kurulumda **"Add python.exe to PATH"** kutusunu işaretle.

Sonra `istemci` klasöründe:

```bash
python3 kur.py        # Windows: py kur.py
```

Kurulum sırasıyla şunları sorar:
1. Hub adresi (`https://mepcenter.com.tr/claude/`)
2. Bilgisayar adı
3. Token
4. Claude Desktop'a da eklensin mi?
5. Köprü ajanı kurulsun mu?

Kurulum şunları yapar:
- `~/.mepcenter/` klasörüne dosyaları ve ayarları koyar
- Claude Code'a **hook'ları** (otomatik kayıt) ve **mepcenter MCP sunucusunu** (Claude'un hub araçları) ekler
- `~/.claude/CLAUDE.md` dosyasına kısa bir not ekler
- İstersen **köprü ajanını** açılışta başlayacak şekilde kurar (Mac: LaunchAgent, Windows: Başlangıç, Linux: systemd)

Kurulumdan sonra açık Claude Code pencerelerini kapatıp yeniden aç. Deneme için Claude Code'a `kod deneme`
yaz; panelde "Görevler" altında `deneme` görünmeli.

Diğer komutlar:
- `python3 kur.py --kopru`: yalnızca köprü ayarlarını yeniden yapar
- `python3 kur.py --kaldir`: her şeyi geri alır

## 4. claude.ai (web / mobil), Claude Desktop sohbet ve Cowork

Bu ortamlar bilgisayarda betik çalıştıramaz. Bunun yerine hub'ı **bağlayıcı (connector)** olarak eklersin:

1. Panelde `web-claude` adında bir ajan oluştur ve token'ını al.
2. claude.ai → **Ayarlar → Connectors (Bağlayıcılar) → Add custom connector**
   - Ad: `MepCenter Hub`
   - URL: `https://mepcenter.com.tr/claude/mcp/?k=WEB_CLAUDE_TOKENI`
3. Sohbette bağlayıcıyı açıp şunu yaz: *"matwar görevine bak, devam edelim"*.

claude.ai → Ayarlar → Profil → "Kişisel tercihler" alanına şunu eklemen önerilir:
> Bir görev kodu söylediğimde (örn. "kod matwar") MepCenter Hub bağlayıcısındaki hub_set_project aracını çağır,
> özeti oku ve kaldığımız yerden devam et. Önemli kararları hub_log ile, ilerlemeyi hub_project_update ile kaydet.

> Not: Bu URL token içerir; kimseyle paylaşma. Sızarsa panelden o token'ı yenile.
> Web/mobilde hook olmadığı için konuşmalar otomatik kaydedilmez. Claude, talimat gereği kararları ve
> "son durum" notunu kendisi yazar.

Claude Code'da Python kurmadan kullanmak istersen (otomatik kayıt olmadan, yalnızca araçlar):
```bash
claude mcp add --scope user --transport http mepcenter https://mepcenter.com.tr/claude/mcp/ --header "Authorization: Bearer TOKEN"
```

## 5. Kullanım

| Ne istiyorsun | Ne yaparsın |
|---|---|
| Bir işe devam etmek | Herhangi bir Claude'a: `kod matwar` / `matwar görevine bak, devam edelim` |
| Yeni görev açmak | `kod yeniis` (ilk kez kullanılan kod yeni görev açar) |
| Diğer bilgisayarda ne yapılıyor? | Claude'a sor ya da panel → **Oturumlar** |
| Açık bir Claude'a yazmak | Panel → **Sohbet** → oturumu seç → yaz |
| Bilgisayara iş vermek (Claude açık olmasa bile) | Panel → **Sohbet** → o makinenin **kopru** oturumu → yaz |
| Görevin son durumunu düzeltmek | Panel → **Görevler** → kod → "Son durum" |
| Tüm konuşma geçmişi | Panel → **Kayıtlar** (görev koduna göre filtrelenebilir) |
| Claude'ların davranışını değiştirmek | Panel → **Ayarlar** → "Claude ajanları için talimat" |

### Açık bir Claude'la canlı sohbet (dinleme modu)
Claude Code kendiliğinden uyanmaz. Panelden yazdığın mesajı, sen o pencereye bir şey yazdığında görür.
Pencereyi "dinlemede" tutmak için Claude'a **"dinle"** de. Claude `~/.mepcenter/hub_dinle.py` dosyasını
arka planda çalıştırır, mesaj gelince uyanıp cevaplar ve dinlemeye devam eder.

### Köprü ajanı komutları (panel sohbetinden)
- `/durum`: makine, klasör ve çalışan iş
- `/yeni`: yeni Claude konuşması
- `/klasor ~/Projeler/matwar`: çalışma klasörünü değiştirir
- `/iptal`: çalışan işi durdurur

Köprünün izin modu (`~/.mepcenter/config.json` → `kopru.permission_mode`):
- `acceptEdits` (varsayılan): Claude dosya okuyup düzenleyebilir ama terminal komutu çalıştıramaz.
- `default`: yalnızca okur.
- `bypassPermissions`: her şeye izinlidir. Panel şifren ele geçerse bilgisayarın da ele geçer;
  dikkatli kullan.

Belirli komutlara izin vermek için `kopru.allowed_tools` listesine örneğin `"Bash(git status:*)"` ekle.

Bilgisayar uykudaysa köprü çalışmaz. Kurulumda "uykuya geçmesin" seçeneğini seç. Mac'te kapak kapalıyken
de çalışması için Sistem Ayarları → Pil/Enerji ayarlarına bak.

## 6. Güvenlik notları

- Panel şifresi en az 10 karakterdir. 15 dakikada 5 hatalı girişten sonra giriş kilitlenir.
  Formlarda CSRF koruması vardır.
- Ajan token'ları veritabanında yalnızca SHA-256 özeti olarak tutulur.
- `config.php`, `lib/` ve `data/` (yüklenen dosyalar) dışarıdan erişime kapalıdır (`.htaccess`).
  Sunucun Nginx ise bu klasörleri Nginx ayarından da kapat.
- İstersen `config.php` → `allowed_ips` ile API'yi yalnızca kendi IP'lerine açabilirsin.
- Hook'lar `sk-…`, `ghp_…`, `password=…` gibi kalıpları kayıttan önce maskeler. Hariç tutulan dosyalar:
  `~/.mepcenter/config.json` → `exclude`.
- Konuşmaların tamamı sunucuna kaydedilir. Müşteri verisi gibi hassas işlerde `auto_log: false` yapabilirsin.

## 7. Sorun giderme

- **Hook çalışmıyor:** `~/.mepcenter/hook.log` dosyasına bak.
- **Köprü çalışmıyor:** `~/.mepcenter/kopru.log` dosyasına bak.
  - Mac: `launchctl list | grep mepcenter`
  - Windows: Görev Yöneticisi'nde `python.exe` işlemini ara.
- **401 Token gerekli (Apache):** `.htaccess` içindeki Authorization satırları sunucuda etkin olmalı.
  İstemci zaten `X-Hub-Token` başlığını da gönderir.
- **Mac'te SSL hatası:** `/Applications/Python 3.x/Install Certificates.command` dosyasını çalıştır.
- **Paylaşımlı hosting yavaş:** Dinleme/köprü bağlantıları 25 sn'lik bekleme istekleri yapar. Her bilgisayar
  bir PHP işlemi tutar. Hosting "Entry Processes" sınırı düşükse (ör. 10) aynı anda çok fazla köprü açma.
