# Math Warriors — bot hayatı (her bot 15 dakikada bir maç + sohbet)

Bilgisayarında `bot_runner.py` açık kaldıkça sunucu dakikada bir tetiklenir:

- Her bot yaklaşık 15 dakikada bir (±3 dk) lig puanı yakın başka bir botla 3'te 2 düello yapar.
  Lig puanı, galibiyet/mağlubiyet, seri ve XP gerçek maç kuralıyla değişir (Bronz'da puan kaybı yok).
  Maç yapan bot "çevrimiçi" görünür. 300 bot için dakikada ~10 maç.
- Botlar dünya sohbetinde kendi dillerinde yazar (isimden tahmin: Türkçe, İngilizce, İspanyolca,
  Japonca, Rusça, Arapça, Almanca, Fransızca, İtalyanca, Portekizce): selam, meydan okuma,
  matematik sohbeti, maç sonrası övünme/yakınma. En az 75 sn arayla, sohbeti boğmadan.
- Bir oyuncu "selam / hi / hola…" yazarsa bir bot onun dilinde karşılık verir.
- Program kapanınca botlar durur.

## Sunucuya kurulum (bir kez, cPanel → File Manager)

1. `BotLife.php` → `~/mathwars/src/BotLife.php`
2. `bots_tick.php` → `~/public_html/api/bots_tick.php`
3. `~/mathwars/config.local.php` dizisine bir satır ekle (anahtar en az 30 karakterlik, tahmin edilemeyecek bir değer olsun):
   ```php
   'bot_tick_key' => 'BURAYA_UZUN_RASTGELE_ANAHTAR',
   ```
   Anahtar tanımlı değilse uç nokta kapalıdır (`disabled`).

Gerekli iki sütun (`users.bot_next_ms`, `users.bot_lang`) ilk çağrıda kendiliğinden eklenir.
Mevcut dosyaların hiçbiri değişmez.

## Bilgisayarda çalıştırma

Python 3 yeterli (ek paket yok).

- Mac: anahtarı `~/.mathwars_bot_key` dosyasına yaz, sonra `python3 bot_runner.py`
- Windows: anahtarı `%USERPROFILE%\.mathwars_bot_key` dosyasına yaz, sonra `py bot_runner.py`
- Deneme: `python3 bot_runner.py --once`

Ekranda her dakika oynanan maçlar ve botların sohbet mesajları görünür. Durdurmak: Ctrl+C.
