# Laufmodi-Matrix: OSF + Session Manager + Mosquitto

Kurze Referenz fuer den Betrieb der drei Systeme `OSF`, `Session Manager` und `Mosquitto`.

## Ziel

- Klarer Betriebsmodus pro Test-/Demo-Fall
- Keine Vermischung von Live- und Replay-Nachrichten
- Reproduzierbares Verhalten auf Mac/Windows/RPi

## Modus Uebersicht

| Modus | OSF | Session Manager | MQTT-Broker | Typischer Zweck |
|---|---|---|---|---|
| **A: Local Replay** | Lokal (Mac/Windows) | Lokal | Lokal (`localhost`) oder externer erreichbarer Broker | Reproduzierbare Analyse/Debug ohne Fabriklauf |
| **B: Live auf RPi** | Auf RPi | Optional (nur Analyse) | RPi/Fabrik-Broker (`192.168.0.100`) | Produktnaher Betrieb und Praesentation |
| **C: Live mit lokalem OSF** | Lokal (Mac/Windows) | Optional | RPi/Fabrik-Broker (`192.168.0.100`) | Lokale Entwicklung gegen Live-Daten vor RPi-Deployment |

## Konfig-Regeln (verbindlich)

1. **Modus vor Start festlegen** (A/B/C) und nur passende Broker-Config verwenden.
2. **No-Mix-Regel:** Live und Replay nicht gleichzeitig auf denselben Topics/Brokern betreiben.
3. **Replay auf Windows ohne lokalen Mosquitto ist erlaubt**, wenn ein externer Broker erreichbar ist und korrekt konfiguriert wurde.
4. **RPi ist Zielumgebung fuer stabile Demo/Praesentation**; lokaler OSF-Live-Betrieb dient der Vorabvalidierung.

## Schnell-Check pro Modus

- **A: Local Replay**
  - Session-Dateien lokal vorhanden
  - OSF und Session Manager laufen
  - Broker in beiden Tools konsistent gesetzt
- **B: Live auf RPi**
  - RPi-Stack laeuft
  - Broker `192.168.0.100` erreichbar
  - Kein Replay-Inject parallel aktiv
- **C: Live mit lokalem OSF**
  - Lokales OSF verbindet auf `192.168.0.100`
  - Session Manager nur wenn noetig (kein Replay-Mix)
  - Ergebnis als Vorstufe fuer spaeteres RPi-Deployment nutzen

## Typische Fehlerbilder

- **Symptom:** "Keine Orders" / keine AGV-Daten  
  **Check:** Broker-Ziel falsch (localhost statt `192.168.0.100` oder umgekehrt).

- **Symptom:** Unerwartete/duplizierte Zustandswechsel  
  **Check:** Replay und Live laufen parallel auf denselben Topics.

- **Symptom:** Replay sendet nicht auf Windows  
  **Check:** Externer Broker nicht erreichbar, Port/Credentials/Firewall pruefen.
