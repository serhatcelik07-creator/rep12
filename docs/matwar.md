# MatWar (Matematik Savaşı) — çalışma notları

## Oturumlar

| Tarih | Oturum | Yapılanlar |
|---|---|---|
| 2026-10-06 | https://claude.ai/code/session_016F6U5H2bfvjouTCp3gHnH7 | Zıpzıp'a Matematik Savaşı modu, hareketli emoji atma, emoji paketleri, hediye kartı yarışması notları |

Dal: `claude/kod-mathwar-vsgczw`

## Oyun kuralları

- 2-4 oyuncu aynı ekranda aynı soruyu görür. 4 cevap 4 yöne dizilir.
- Her oyuncunun 5 canı var. İlk doğru cevap diğer herkesten 1 can götürür. Yanlış cevap kendi canından 1 götürür ve o soruda kilitler.
- Sorular zorlaşır: toplama/çıkarma → 4. sorudan itibaren çarpma → 7. sorudan itibaren bölme. Süre 10 sn'den 5 sn'ye iner.
- Canı kalan son oyuncu kazanır. 30 soru sonunda en çok canı olan kazanır, eşitlik berabere.

## Emojiler (savaş içi)

- Mağazada **karakterler** ve **emoji paketleri** satılır. Eski item'lar kaldırıldı, yerine emoji paketleri geldi.
- Her paket 3 emoji içerir. Oyuncunun taktığı paket savaşta 3 emoji tuşuna dağılır.
- Emoji, rakibe (diğer oyuncular içinde canı en çok olana) atılır:
  - kavis çizerek dönerek uçar,
  - rakibin paneline çarpınca büyüyüp zıplar, etrafa renkli parçacıklar saçar,
  - rakibin paneli sarsılır.
- Spam olmasın diye her oyuncu 2 saniyede bir emoji atabilir. Bekleme süresindeki emojiler soluk görünür, hazır olanlar hafifçe zıplar.
- Elenen oyuncu da emoji atabilir.

| Oyuncu | Cevap | Emoji |
|---|---|---|
| P1 | W A S D | Q E R |
| P2 | Ok tuşları | , . / |
| P3 | I J K L | U O Y |
| P4 | Numpad 8 4 5 6 | Numpad 7 9 1 |
| Gamepad | D-Pad / sol analog | X Y B |

Paketler `scripts/emoji_packs.gd` içinde. Yeni paket eklemek için listeye bir satır eklemek yeterli:

| Paket | Fiyat (coin) | Emojiler |
|---|---|---|
| Temel | ücretsiz | 😎 😂 👍 |
| Dostane | 150 | 🤝 👏 ❤️ |
| Ateşli | 200 | 🔥 💪 🏆 |
| Alaycı | 300 | 🤣 🐢 💤 |
| Dahi | 400 | 🧠 🤓 ⚡ |

Emojiler sistem fontundan çiziliyor (Android, iOS ve Windows renkli emoji fontu içeriyor). Bazı Linux makinelerde emoji fontu yoksa kutucuk görünebilir.

## Android / iOS

Mağazaya gönderilen asıl MatWar uygulamasının kodu bu depoda değil. O depoya Claude'un erişimi açılınca yapılacaklar:

1. Mağaza: item ürünlerini kaldır, emoji paketlerini ekle (App Store Connect ve Google Play Console'da uygulama içi ürünleri de güncelle).
2. Daha önce item satın almış kullanıcılara karşılık olarak emoji paketi veya coin ver.
3. Savaş ekranına yukarıdaki emoji atma sistemini taşı (dokunmatik ekranda 3 emoji butonu).
4. Çevrimiçi savaş varsa emoji gönderimini sunucu üzerinden ilet ve sunucuda da bekleme süresi uygula.

## Ayın birincisine hediye kartı (Apple / Google Play)

Yapılabilir, ama **beceri yarışması** olarak kurulmalı, **indirme karşılığı ödül** olarak değil.

- İndirme, puan verme veya yorum karşılığı ödül iki mağazada da yasak ("teşvikli indirme"). Reklamda "İndir, kazan" değil, "Her ay en yüksek puan ödül kazanır" denmeli.
- Katılım ücretsiz olmalı ve uygulama içi satın almaya bağlanmamalı.
- Kazanan puanla belirlenmeli. Kura/şans varsa Türkiye'de çekiliş sayılır ve Milli Piyango İdaresi izni gerekir. Eşitlikte "puana ilk ulaşan" kazanır.
- Puanlar sunucuda doğrulanmalı (hile riski).
- Ödülün vergisi (stopaj) ve KVKK aydınlatma metni için mali müşavir / avukat onayı alınmalı.
- 18 yaş altı kazananlar için veli onayı istenmeli.

### Uygulama içinde gösterilecek resmî kurallar (taslak)

> **MatWar Aylık Şampiyonluk Yarışması — Resmî Kurallar**
>
> 1. **Düzenleyen:** Yarışmayı [geliştirici adı / şirket unvanı] düzenler ve tüm sorumluluğu ona aittir.
> 2. **Apple ve Google:** Apple Inc. ve Google LLC bu yarışmanın sponsoru değildir ve yarışmaya hiçbir şekilde dahil değildir. Apple ve Google Play, ilgili şirketlerin ticari markalarıdır.
> 3. **Katılım:** Katılım ücretsizdir. Satın alma yapmak kazanma şansını artırmaz. Uygulamada hesabı olan herkes otomatik olarak katılır.
> 4. **Süre:** Her takvim ayı ayrı bir yarışmadır (Türkiye saatiyle ayın 1'i 00:00 – ayın son günü 23:59).
> 5. **Kazanan:** Ay içinde en yüksek doğrulanmış puanı alan oyuncu kazanır. Eşitlikte bu puana ilk ulaşan kazanır. Kazanan kura ile belirlenmez.
> 6. **Ödül:** [tutar] TL değerinde Apple Gift Card veya Google Play hediye kartı (kazananın cihazına göre). Ödül nakde çevrilemez, devredilemez.
> 7. **Bildirim:** Kazanan, ayın bitişinden sonraki 7 gün içinde uygulama içinden bilgilendirilir. 14 gün içinde yanıt vermezse ödül ikinci sıradaki oyuncuya geçer.
> 8. **Hile:** Hile, otomasyon veya puan manipülasyonu tespit edilen hesaplar diskalifiye edilir.
> 9. **Yaş:** 18 yaşından küçük kazananlar ödülü veli onayıyla alır.
> 10. **Kişisel veriler:** Kazananla iletişim için toplanan bilgiler yalnızca ödül teslimi için kullanılır ([KVKK aydınlatma metni bağlantısı]).
> 11. **Vergi:** Ödüle ilişkin yasal vergi yükümlülükleri düzenleyen tarafından karşılanır.

Köşeli parantezli alanlar doldurulmalı ve metin yayından önce bir hukukçuya gösterilmeli.
