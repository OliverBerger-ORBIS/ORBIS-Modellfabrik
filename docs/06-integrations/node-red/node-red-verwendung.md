# Einbindung von Modbus, MQTT in Node-Red

> ⚠️ **VERIFIKATION AUSSTEHEND**: Diese Dokumentation basiert auf einer Hypothese und wurde noch nicht verifiziert. Die beschriebenen Node-RED-Integrationen und Kommunikationsprotokolle müssen noch getestet und validiert werden. 

 

## 🔌 1. MQTT in Node-RED einbinden 

Voraussetzungen: 

Ein laufender MQTT-Broker (z. B. Mosquitto auf dem Raspberry Pi oder extern) 

Node-RED installiert 

Schritte: 

a) MQTT-Nodes installieren (falls nicht vorhanden) 

In Node-RED: 

Menü → Manage palette → Install 

Suche nach node-red-node-mqtt und installiere es 

b) MQTT-Broker konfigurieren 

Ziehe einen mqtt in oder mqtt out Node in den Flow. 

Doppelklick auf den Node 

Klicke auf das Stift-Symbol neben dem Server-Feld 

Gib die Adresse deines Brokers ein (z. B. mqtt://localhost:1883) 

Optional: Benutzername/Passwort 

c) Beispiel-Flow 

mqtt in: Topic sensor/temperatur 

debug: zeigt empfangene Daten an 

 
 

## ⚙️ 2. Modbus in Node-RED einbinden 

Voraussetzungen: 

Ein Modbus-fähiges Gerät (z. B. SPS, Sensor, Aktor) 

Verbindung über Modbus TCP oder Modbus RTU (seriell) 

Schritte: 

a) Modbus-Nodes installieren 

In Node-RED: 

Menü → Manage palette → Install 

Suche nach node-red-contrib-modbus und installiere es 

b) Modbus-Verbindung konfigurieren 

Ziehe z. B. einen modbus-read Node in den Flow. 

Doppelklick auf den Node 

Wähle oder erstelle eine neue Modbus-Verbindung: 

Modbus TCP: IP-Adresse und Port (Standard: 502) 

Modbus RTU: Serielle Schnittstelle (z. B. /dev/ttyUSB0), Baudrate, Parität etc. 

Gib die Adresse des Registers an (z. B. Holding Register 40001 → Adresse 0) 

c) Beispiel-Flow 

modbus-read: liest alle 5 Sekunden ein Register 

function: verarbeitet den Wert 

debug: zeigt den Wert an 

 
 

🧪 Beispiel: Temperatur über Modbus lesen und per MQTT senden 

modbus-read → liest Temperaturwert 

function → wandelt Wert um 

mqtt out → sendet an Topic anlage/temperatur 