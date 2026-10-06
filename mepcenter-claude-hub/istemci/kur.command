#!/bin/bash
# Mac: bu dosyaya çift tıklayın
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 bulunamadı. Açılan pencerede 'Yükle'ye basın, kurulum bitince bu dosyaya tekrar çift tıklayın."
  xcode-select --install
  read -p "Kapatmak için Enter'a basın..."
  exit 1
fi
python3 kur.py
read -p "Bitti. Kapatmak için Enter'a basın..."
