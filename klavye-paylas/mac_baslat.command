#!/bin/bash
# Cift tiklayinca calisir. Ilk seferde gerekli paketleri kendisi kurar.
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1 || ! python3 -c "" >/dev/null 2>&1; then
    echo "Python 3 bulunamadi. Acilan pencerede 'Yukle'ye bas, bitince bu dosyaya tekrar cift tikla."
    xcode-select --install 2>/dev/null
    read -n 1 -s -r -p "Kapatmak icin bir tusa bas..."
    exit 1
fi

# Paketler ev klasorune kurulur; program ag diskinden calistirilsa bile sorun olmaz.
VENV="$HOME/.klavye-paylas-venv"
if [ ! -x "$VENV/bin/python" ] || ! "$VENV/bin/python" -c "import Quartz, cryptography" 2>/dev/null; then
    echo "Ilk kurulum yapiliyor (bir kere), biraz surebilir..."
    python3 -m venv "$VENV" && "$VENV/bin/python" -m pip install -q --upgrade pip \
        && "$VENV/bin/python" -m pip install -q -r requirements-mac.txt
    if [ $? -ne 0 ]; then
        read -n 1 -s -r -p "Kurulum basarisiz oldu. Kapatmak icin bir tusa bas..."
        exit 1
    fi
fi

"$VENV/bin/python" mac_taraf.py "$@"
read -n 1 -s -r -p "Program kapandi. Pencereyi kapatmak icin bir tusa bas..."
