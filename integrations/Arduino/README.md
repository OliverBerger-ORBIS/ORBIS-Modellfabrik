# Arduino Sketches – ORBIS Modellfabrik

Arduino-Programme für die APS-Modellfabrik. Struktur orientiert sich an [TXT-Controller / ROBO Pro](../README.md).

**Arduino IDE:** Den Ordner `integrations/Arduino` (absoluter Pfad zum Projekt) als **Sketchbook-Speicherort** in den Einstellungen eintragen. Siehe [Arduino IDE Setup](../../docs/04-howto/setup/arduino-ide-setup.md).

## Sketches

| Sketch                 | Hardware         | Doku                                                    |
|------------------------|------------------|---------------------------------------------------------|
| Vibrationssensor_SW420 | SW-420, Relais, 12V Ampel | [arduino-vibrationssensor.md](../../docs/05-hardware/arduino-vibrationssensor.md) |
| OSF_MultiSensor_R4WiFi | R4 WiFi: MPU-6050, SW-420, DHT11, Flamme, 4-Relais, 12V Ampel | [Implementierungsplan](../../docs/07-analysis/arduino-r4-wifi-mpu6050-implementation-plan-2026-03.md) |

## Verzeichnisstruktur

```
integrations/Arduino/
├── README.md
├── Vibrationssensor_SW420/
│   └── Vibrationssensor_SW420.ino
└── OSF_MultiSensor_R4WiFi/
    └── OSF_MultiSensor_R4WiFi.ino
```

**Workflow:** Arduino IDE öffnen → Sketch auswählen → Board & Port konfigurieren → Upload. **R4 WiFi:** Board „Arduino Uno R4 WiFi“ wählen.
