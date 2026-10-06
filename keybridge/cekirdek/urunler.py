"""Iki urunun adlari ve kimlikleri. Isim degisirse yalnizca burasi degisir.

PC->Mac : Windows'un klavye/faresi Mac'i yonetir.
          Windows uygulamasi ucretli (Microsoft Store, 15 gun deneme),
          Mac uygulamasi ucretsiz (siteden imzali .dmg).
Mac->PC : Mac'in klavye/faresi Windows'u yonetir.
          Mac uygulamasi ucretli (siteden .dmg, 15 gun deneme + lisans anahtari),
          Windows uygulamasi ucretsiz (Microsoft Store).
"""

MARKA = "KeyBridge"

URUNLER = {
    "pc2mac": {
        "ad": "KeyBridge PC to Mac",
        "kisa": "PC→Mac",
        "yoneten": "windows",
        "yonetilen": "mac",
        "mac_paket": "com.keybridge.pc2mac.receiver",
        "win_paket": "KeyBridge.PCtoMac",
    },
    "mac2pc": {
        "ad": "KeyBridge Mac to PC",
        "kisa": "Mac→PC",
        "yoneten": "mac",
        "yonetilen": "windows",
        "mac_paket": "com.keybridge.mac2pc",
        "win_paket": "KeyBridge.MactoPC.Receiver",
    },
}

DENEME_GUNU = 15
