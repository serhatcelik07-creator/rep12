"""Tus tablolari.

Agda tuslar "PC scan kodu (set 1) + genisletilmis bayragi" olarak tasinir.
Bu konuma dayali bir koddur: hangi karakterin cikacagini hedef bilgisayardaki
klavye duzeni (or. Turkce Q) belirler.
"""

# PC scan kodu -> Mac sanal tus kodu
SCAN_MAC = {
    0x01: 53, 0x02: 18, 0x03: 19, 0x04: 20, 0x05: 21, 0x06: 23, 0x07: 22,
    0x08: 26, 0x09: 28, 0x0A: 25, 0x0B: 29, 0x0C: 27, 0x0D: 24, 0x0E: 51,
    0x0F: 48, 0x10: 12, 0x11: 13, 0x12: 14, 0x13: 15, 0x14: 17, 0x15: 16,
    0x16: 32, 0x17: 34, 0x18: 31, 0x19: 35, 0x1A: 33, 0x1B: 30, 0x1C: 36,
    0x1D: 59, 0x1E: 0, 0x1F: 1, 0x20: 2, 0x21: 3, 0x22: 5, 0x23: 4,
    0x24: 38, 0x25: 40, 0x26: 37, 0x27: 41, 0x28: 39, 0x29: 50, 0x2A: 56,
    0x2B: 42, 0x2C: 6, 0x2D: 7, 0x2E: 8, 0x2F: 9, 0x30: 11, 0x31: 45,
    0x32: 46, 0x33: 43, 0x34: 47, 0x35: 44, 0x36: 60, 0x37: 67, 0x38: 58,
    0x39: 49, 0x3A: 57, 0x3B: 122, 0x3C: 120, 0x3D: 99, 0x3E: 118,
    0x3F: 96, 0x40: 97, 0x41: 98, 0x42: 100, 0x43: 101, 0x44: 109,
    0x45: 113, 0x46: 107, 0x47: 89, 0x48: 91, 0x49: 92, 0x4A: 78, 0x4B: 86,
    0x4C: 87, 0x4D: 88, 0x4E: 69, 0x4F: 83, 0x50: 84, 0x51: 85, 0x52: 82,
    0x53: 65, 0x56: 10, 0x57: 103, 0x58: 111,
}
SCAN_MAC_GENIS = {
    0x1C: 76, 0x1D: 62, 0x45: 71, 0x35: 75, 0x37: 105, 0x38: 61, 0x47: 115, 0x48: 126,
    0x49: 116, 0x4B: 123, 0x4D: 124, 0x4F: 119, 0x50: 125, 0x51: 121,
    0x52: 114, 0x53: 117, 0x5B: 55, 0x5C: 54, 0x5D: 110,
}

# Mac sanal tus kodu -> (scan kodu, genisletilmis)
MAC_SCAN = {kod: (scan, 0) for scan, kod in SCAN_MAC.items()}
MAC_SCAN.update({kod: (scan, 1) for scan, kod in SCAN_MAC_GENIS.items()})
MAC_SCAN[63] = None  # fn: Mac'e ozgu, karsiligi yok

# Ctrl ile Windows/Cmd tusunun yer degistirmesi (ayar: ctrl_cmd)
CTRL_CMD_TAKAS = {(0x1D, 0): (0x5B, 1), (0x1D, 1): (0x5C, 1), (0x5B, 1): (0x1D, 0), (0x5C, 1): (0x1D, 1)}

# ---- degistirici tuslar (kisayollar icin) ----
WIN_DEGISTIRICI = {
    0x11: "ctrl", 0xA2: "ctrl", 0xA3: "ctrl",
    0x10: "shift", 0xA0: "shift", 0xA1: "shift",
    0x12: "alt", 0xA4: "alt", 0xA5: "alt",
    0x5B: "win", 0x5C: "win",
}
MAC_DEGISTIRICI = {59: "ctrl", 62: "ctrl", 56: "shift", 60: "shift", 58: "alt", 61: "alt", 55: "win", 54: "win"}

DEGISTIRICI_ADLARI = {
    "windows": {"ctrl": "Ctrl", "alt": "Alt", "shift": "Shift", "win": "Win"},
    "mac": {"ctrl": "⌃", "alt": "⌥", "shift": "⇧", "win": "⌘"},
}
DEGISTIRICI_SIRASI = ("ctrl", "alt", "shift", "win")

# ---- tus adlari ----
WIN_TUS_ADLARI = {
    0x08: "Backspace", 0x09: "Tab", 0x0D: "Enter", 0x13: "Pause", 0x14: "Caps Lock",
    0x1B: "Esc", 0x20: "Space", 0x21: "Page Up", 0x22: "Page Down", 0x23: "End",
    0x24: "Home", 0x25: "←", 0x26: "↑", 0x27: "→", 0x28: "↓", 0x2C: "Print Screen",
    0x2D: "Insert", 0x2E: "Delete", 0x5D: "Menu", 0x90: "Num Lock", 0x91: "Scroll Lock",
    0x6A: "Num *", 0x6B: "Num +", 0x6D: "Num -", 0x6E: "Num .", 0x6F: "Num /",
}
WIN_TUS_ADLARI.update({0x30 + i: str(i) for i in range(10)})
WIN_TUS_ADLARI.update({0x41 + i: chr(0x41 + i) for i in range(26)})
WIN_TUS_ADLARI.update({0x60 + i: f"Num {i}" for i in range(10)})
WIN_TUS_ADLARI.update({0x70 + i: f"F{i + 1}" for i in range(24)})

MAC_TUS_ADLARI = {
    0: "A", 1: "S", 2: "D", 3: "F", 4: "H", 5: "G", 6: "Z", 7: "X", 8: "C", 9: "V",
    11: "B", 12: "Q", 13: "W", 14: "E", 15: "R", 16: "Y", 17: "T", 18: "1", 19: "2",
    20: "3", 21: "4", 22: "6", 23: "5", 24: "=", 25: "9", 26: "7", 27: "-", 28: "8",
    29: "0", 30: "]", 31: "O", 32: "U", 33: "[", 34: "I", 35: "P", 36: "Return", 37: "L",
    38: "J", 39: "'", 40: "K", 41: ";", 42: "\\", 43: ",", 44: "/", 45: "N", 46: "M",
    47: ".", 48: "Tab", 49: "Space", 50: "`", 51: "Delete", 53: "Esc",
    122: "F1", 120: "F2", 99: "F3", 118: "F4", 96: "F5", 97: "F6", 98: "F7", 100: "F8",
    101: "F9", 109: "F10", 103: "F11", 111: "F12", 105: "F13", 107: "F14", 113: "F15",
    115: "Home", 119: "End", 116: "Page Up", 121: "Page Down", 117: "⌦",
    123: "←", 124: "→", 125: "↓", 126: "↑",
}

TUS_ADLARI = {"windows": WIN_TUS_ADLARI, "mac": MAC_TUS_ADLARI}
DEGISTIRICILER = {"windows": WIN_DEGISTIRICI, "mac": MAC_DEGISTIRICI}

# Varsayilan gecis tuslari: ↓ uzak bilgisayara gecer, ↑ geri getirir.
VARSAYILAN_KISAYOL = {
    "windows": ({"vk": 0x28, "degistiriciler": []}, {"vk": 0x26, "degistiriciler": []}),
    "mac": ({"vk": 125, "degistiriciler": []}, {"vk": 126, "degistiriciler": []}),
}
