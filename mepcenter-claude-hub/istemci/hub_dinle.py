#!/usr/bin/env python3
"""MepCenter Claude Hub - dinleme modu (Claude Code için).

Bu oturuma (veya herkese) yeni bir hub mesajı gelene kadar bekler; gelince mesajları
yazdırıp çıkar. Claude Code bunu arka planda çalıştırır; komut bitince Claude uyanır,
mesajı okur, hub_send ile cevaplar ve dinleyiciyi yeniden başlatır.

Kullanım:  python hub_dinle.py [en_fazla_dakika]   (varsayılan 120)
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hub_client import HubError, api  # noqa: E402


def main():
    limit_min = float(sys.argv[1]) if len(sys.argv) > 1 else 120
    deadline = time.time() + limit_min * 60
    out = open(sys.stdout.fileno(), "w", encoding="utf-8", closefd=False)
    while time.time() < deadline:
        try:
            msgs = api("wait", params={"timeout": 25}, timeout=60)["messages"]
        except HubError as e:
            out.write(f"(hub hatası, 15 sn sonra tekrar: {e})\n")
            out.flush()
            time.sleep(15)
            continue
        if msgs:
            out.write("YENİ HUB MESAJLARI:\n")
            for m in msgs:
                topic = f" ({m['topic']})" if m.get("topic") else ""
                out.write(f"- [#{m['id']} {m['created_at']}] {m['from_label']}{topic} -> {m['to_type']}"
                          f"{':' + m['to_value'] if m.get('to_value') else ''}:\n{m['body']}\n")
            out.write("\nCevap vermek için hub_send kullan (panelden geldiyse to=\"admin\"), "
                      "sonra dinlemeye devam etmek için bu komutu yeniden arka planda başlat.\n")
            out.flush()
            return
    out.write("Dinleme süresi doldu, yeni mesaj yok.\n")


if __name__ == "__main__":
    main()
