# Arduino Sketches – ORBIS Modellfabrik

Arduino-Programme für die APS-Modellfabrik. Struktur orientiert sich an [TXT-Controller / ROBO Pro](../README.md).

**Arduino IDE:** Den Ordner `integrations/Arduino` (absoluter Pfad zum Projekt) als **Sketchbook-Speicherort** in den Einstellungen eintragen. Siehe [Arduino IDE Setup](../../docs/04-howto/setup/arduino-ide-setup.md).

## Sketches

| Sketch                 | Hardware         | Doku                                                    |
|------------------------|------------------|---------------------------------------------------------|
| Vibrationssensor_SW420 | SW-420, Relais, 12V Ampel (Legacy) | [arduino-r4-multisensor.md](../../docs/05-hardware/arduino-r4-multisensor.md) |
| OSF_MultiSensor_R4WiFi | R4 WiFi: MPU-6050, SW-420, DHT11, Flamme, MQ-2, 4-Relais, 12V Ampel | [arduino-r4-multisensor.md](../../docs/05-hardware/arduino-r4-multisensor.md) |

## Verzeichnisstruktur

```
integrations/Arduino/
├── README.md
├── Vibrationssensor_SW420/      (Legacy, Ethernet)
├── Vibrationssensor_MPU6050/    (Legacy, Ethernet)
└── OSF_MultiSensor_R4WiFi/     (Aktiv – R4 WiFi, alle Sensoren)
```

**Workflow:** Arduino IDE öffnen → Sketch auswählen → Board & Port konfigurieren → Upload. **R4 WiFi:** Board „Arduino Uno R4 WiFi“ wählen.
