# Lokale Mosquitto-Konfiguration für Development

Diese Konfigurationsdateien sind für die lokale Entwicklungsumgebung gedacht, wenn Entwickler **ohne APS-Anbindung** (reale Fabrik) testen möchten.

## 🎯 Verwendungszweck

- **Session Manager**: Lokale MQTT-Broker für Session-Aufnahme und -Replay
- **Replay Station**: Wiedergabe von aufgezeichneten Sessions
- **OSF Dashboard**: Testing ohne reale Hardware-Verbindung
- **Lokale Entwicklung**: Entwicklung und Testing ohne APS-Netzwerk

## 📋 Verfügbare Konfigurationen

### `mosquitto.conf.local`
Vollständige Konfiguration mit Authentifizierung:
- TCP MQTT auf Port 1883 (für Backend-Services)
- WebSocket MQTT auf Port 9001 (für Browser-Anwendungen)
- Passwort-Authentifizierung aktiviert
- Logging aktiviert

### `mosquitto.conf.local-simple`
Vereinfachte Konfiguration ohne Authentifizierung:
- TCP MQTT auf Port 1883
- WebSocket MQTT auf Port 9001
- Keine Authentifizierung (für schnelles Testing)
- Logging aktiviert

## 🔧 Installation (macOS mit Homebrew)

```bash
# Mosquitto installieren
brew install mosquitto

# Konfigurationsdatei kopieren
cp docs/04-howto/setup/mosquitto/mosquitto.conf.local /opt/homebrew/etc/mosquitto/mosquitto.conf

# Oder für einfache Version ohne Auth:
cp docs/04-howto/setup/mosquitto/mosquitto.conf.local-simple /opt/homebrew/etc/mosquitto/mosquitto.conf

# Mosquitto starten
brew services start mosquitto

# Status prüfen
brew services list | grep mosquitto
```

## 🔧 Installation (Linux)

```bash
# Mosquitto installieren
sudo apt-get install mosquitto mosquitto-clients

# Konfigurationsdatei kopieren
sudo cp docs/04-howto/setup/mosquitto/mosquitto.conf.local /etc/mosquitto/mosquitto.conf

# Mosquitto starten
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

## ✅ Verifizierung

```bash
# TCP MQTT testen
mosquitto_pub -h localhost -p 1883 -t test/topic -m "Hello World"

# WebSocket MQTT testen (mit Browser-Tools oder wscat)
# Port 9001 sollte erreichbar sein
```

## 📝 Hinweise

- Diese Konfigurationen sind **nur für lokale Entwicklung** gedacht
- Für Produktion/APS-Anbindung siehe `integrations/mosquitto/config/mosquitto.conf`
- Die `.local` Varianten sind speziell für Homebrew-Setup auf macOS optimiert
- Log-Dateien werden in `/opt/homebrew/var/log/mosquitto/` geschrieben (macOS)

## 🔗 Weitere Informationen

- [Project Setup Guide](../project-setup.md)
- [Session Manager Documentation](../../helper_apps/session-manager/README.md)
- [APS Mosquitto Integration](../../../06-integrations/mosquitto/README.md)

