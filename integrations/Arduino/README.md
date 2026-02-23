# Arduino Sketches – ORBIS Modellfabrik

Arduino-Programme für die APS-Modellfabrik. Struktur orientiert sich an [TXT-Controller / ROBO Pro](../README.md).

**Arduino IDE:** Den Ordner `integrations/Arduino` (absoluter Pfad zum Projekt) als **Sketchbook-Speicherort** in den Einstellungen eintragen. Siehe [Arduino IDE Setup](../../docs/04-howto/setup/arduino-ide-setup.md).

## Sketches

| Sketch                 | Hardware         | Doku                                                    |
|------------------------|------------------|---------------------------------------------------------|
| Vibrationssensor_SW420 | SW-420, Relais, 12V Ampel | [arduino-vibrationssensor.md](../../docs/05-hardware/arduino-vibrationssensor.md) |

## Verzeichnisstruktur

```
integrations/Arduino/
├── README.md
└── Vibrationssensor_SW420/
    └── Vibrationssensor_SW420.ino
```

**Workflow:** Arduino IDE öffnen → Sketch `Vibrationssensor_SW420` auswählen → Board & Port konfigurieren → Upload.
