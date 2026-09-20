## Settings for micro:bit

20-09-2026

### Bluetooth Settings

![makecode_project_settings](/Users/zfp165/Documents/diku_teach/stem_academy/images/makecode_project_settings.png)

### Advanced settings (continue past warning)

```bash
{
    "name": "teachable_m_01",
    "description": "",
    "dependencies": {
        "core": "*",
        "microphone": "*",
        "bluetooth": "*"
    },
    "files": [
        "main.blocks",
        "main.ts",
        "README.md",
        "main.py"
    ],
    "preferredEditor": "blocksprj",
    "yotta": {
        "config": {
            "microbit-dal": {
                "bluetooth": {
                    "open": 1,
                    "pairing_mode": 0,
                    "whitelist": 0,
                    "security_level": null
                }
            }
        }
    }
}
```

