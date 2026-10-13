#!/usr/bin/env python3
"""Math Warriors bot hayatı: bu program açık kaldıkça sunucudaki botlar oynar ve sohbet eder.

Dakikada bir https://mepcenter.com.tr/api/bots_tick.php çağrılır. Her bot ~15 dakikada bir başka
bir botla düello yapar (lig puanı, galibiyet, seri ve XP gerçekten değişir), botlar dünya sohbetinde
kendi dillerinde konuşur. Program kapanınca botlar da durur.

Kullanım:
    python3 bot_runner.py                # anahtarı MW_BOT_KEY ortam değişkeninden ya da ~/.mathwars_bot_key dosyasından okur
    python3 bot_runner.py --once         # tek tur çalıştır (deneme)

Anahtar, sunucudaki ~/mathwars/config.local.php dosyasındaki 'bot_tick_key' ile aynı olmalı.
Yalnızca Python 3 standart kütüphanesi kullanılır.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

URL = os.environ.get("MW_BOT_URL", "https://mepcenter.com.tr/api/bots_tick.php")
INTERVAL_S = 60


def read_key() -> str:
    key = os.environ.get("MW_BOT_KEY", "").strip()
    if not key:
        f = Path.home() / ".mathwars_bot_key"
        if f.is_file():
            key = f.read_text(encoding="utf-8").strip()
    if not key:
        sys.exit("Anahtar yok: MW_BOT_KEY ortam değişkenini ayarla ya da ~/.mathwars_bot_key dosyasına yaz.")
    return key


def tick(key: str) -> None:
    req = urllib.request.Request(URL, data=b"{}", method="POST",
                                 headers={"X-Bot-Key": key, "Content-Type": "application/json", "User-Agent": "mw-bot-runner/1"})
    now = datetime.now().strftime("%H:%M:%S")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:200]
        print(f"[{now}] sunucu hatası {e.code}: {body}", flush=True)
        if e.code in (401, 403):
            sys.exit("Anahtar reddedildi ya da sunucuda bot_tick_key tanımlı değil.")
        return
    except Exception as e:  # ağ kesintisi: bir sonraki turda tekrar dener
        print(f"[{now}] bağlantı hatası: {e}", flush=True)
        return
    matches, chat = data.get("matches", []), data.get("chat", [])
    print(f"[{now}] {len(matches)} maç" + (": " + " | ".join(matches) if matches else ""), flush=True)
    for line in chat:
        print(f"           💬 {line}", flush=True)


def main() -> None:
    key = read_key()
    if "--once" in sys.argv:
        tick(key)
        return
    print(f"Bot hayatı başladı ({URL}). Durdurmak için Ctrl+C.", flush=True)
    while True:
        started = time.monotonic()
        tick(key)
        time.sleep(max(1.0, INTERVAL_S - (time.monotonic() - started)))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDurduruldu.")
