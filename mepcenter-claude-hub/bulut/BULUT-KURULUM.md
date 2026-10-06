# Bulut Claude Code oturumlarını (claude.ai/code) hub'a bağlamak

Bulut oturumları Anthropic'in sunucularında çalışır. Senin bilgisayarına veya G: gibi ağ sürücülerine
erişemezler, ama mepcenter.com.tr üzerinden her şeyi görebilirler:
görevler, konuşmalar, diğer Claude'lar ve bilgisayarlardan gönderilen dosyalar.

## 1. Bulut için anahtar oluştur
Panel → **Bilgisayarlar** → en alttaki "Gelişmiş: elle anahtar oluştur" bölümünde Ad: `bulut` yaz, **Oluştur**'a bas.
Çıkan `mch_…` anahtarını kopyala. Bu anahtarı sohbete yapıştırma.

## 2. Bulut ortamının ayarları (bir kez)
claude.ai/code'da oturumun üst çubuğundaki ortam (environment) menüsü → **Edit**:
- **Network access:** `Custom` seç, "Allowed domains" listesine `mepcenter.com.tr` ekle.
  Varsayılan paket listesini (npm, pypi…) koru.
- **Environment variables:** `MEPCENTER_TOKEN` = 1. adımdaki anahtar.

Ayrıntılı adımlar: https://code.claude.com/docs/en/cloud-environments#network-access
Bu ayarlar yeni açılan oturumlarda geçerli olur.

## 3. Depoya bağlantı dosyasını ekle
Bu klasördeki `.mcp.json` dosyasını, bulutta çalıştığın deponun kök klasörüne koy ve commit'le.
(Depoda zaten bir `.mcp.json` varsa içindeki "mepcenter" bölümünü onun "mcpServers" kısmına ekle.)

## 4. Kullan
Yeni bir bulut oturumu aç ve "kod matwar" de. Claude görevin son durumunu, kararlarını ve dosya listesini okur.
- Metin/kod dosyalarını doğrudan okur.
- PDF, Excel, çizim gibi dosyaları ortamdaki `MEPCENTER_TOKEN` ile kendi klasörüne indirir.
- Bulutta ürettiği dosyaları hub'a geri yükler. Böylece win1'deki köprü veya diğer Claude'lar onları alabilir.

## G: sürücüsündeki dosyalar buluta nasıl gelir?
G:'ye bağlı bilgisayarda (ör. win1) `klasor-gonder.bat` dosyasına çift tıkla, klasörü (ör. `G:\Projeler\Matwar`)
ve görev kodunu yaz. Dosyalar hub'a gider; sürücünün şifresi o bilgisayarda kalır.
Sürekli güncel tutmak için:
`py %USERPROFILE%\.mepcenter\hub_senkron.py "G:\Projeler\Matwar" --kod matwar --izle 10`
