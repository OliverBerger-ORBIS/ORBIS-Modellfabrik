# OMF Streamlit Dashboard Anforderungen

## 1) Ziel und Nutzen
- **Nachbau der Applikation APS von Fischertechnuk**
- **Echtzeit-Monitoring** aller Module und deren Status
- **Nachrichtenverwaltung** mit Persistierung und Historie
- **Steuerung der Fabrik-Module, Komponenten und Prozesse** durch Versenden von MQTT-Messages, so wie es die APS Applikation macht.
- **MessageTemplate** Syntaktische und Semantische  Beschreibung der Nachrichten der APS, sowie Kopplung zu den MQTT-Topics, damit eine Steuerung möglich ist.
- **Replay-Station** Abspielen von zuvor aufgenommenn Sessions (Nachrichten-Auustausch) zu Testzwecken, dazu kann das dashboard wahlweise die Verbindung zu APS-MQTT-Broker oder zu einem lokalen BRoker aufgebaut werden, der über ein separates dashboard, die aufgenommenen Nachrichten abspielen=senden kann.

## 2) Architektur (kurz)
- **MessageMonitorService** als zentraler MQTT-Service
- **@st.cache_resource** für persistente Services über Streamlit-Reruns
- **Einzelner MQTT-Client** für Subscribe und Publish
- **Thread-sichere Nachrichtenverarbeitung** mit Queue-System

## 3) Broker, Topics, Rechte
- **Live-Fabrik**: 192.168.0.100:1883 (Standard)
- **Replay-Station**: localhost:1884 (Test)
- **Topic-Subscription**: Alle Topics (#) für vollständiges Monitoring
- **Authentifizierung**: Optional über Username/Password

## 4) Funktionale Anforderungen
### 4.1) Übersicht
- **Modul-Status** in Echtzeit anzeigen aus den bereitgestellten Infos der Mqtt-Nachrichten. Statische Info wird aus den Einstellungen gezogen module.yml
- **Lagerbestand** Ansicht der aktuellen Lager-Belegung (Nachricht vom HBW Modul)
- **Bestellung** Auslösen einer Bestellung von (ROT/WEISS/BLAU) bei Bestellung wird die Produktion gestartet

### 4.2) Produktions-Aufträge (TBD)
- **Auftragsverfolgung** über den gesamten Produktionsprozess
- **Auftragshistorie** mit Zeitstempel und Status

### 4.3) Nachrichten-Zentrale
- **Empfangene Nachrichten** von allen Modulen
- **Gesendete Nachrichten** Nachrichten vom OMF-Dashboard (aus der Steuerung) an den APS-Broker an
- **Nachrichtenfilterung** nach Zeit, Topic, Richtung
- **SQLite-Persistierung** für Audit-Trail

### 4.4) Steuerung
- **Factory Reset** für komplette Fabrik-Rücksetzung
- **Modul-Sequenzen** für AIQS, MILL, DRILL
- **FTS-Befehle** für Transport und Docking
- **Auftragssteuerung** für Produktionsabläufe

### 4.5) Einstellungen
- **MQTT-Broker Konfiguration** (Host, Port, Credentials)
- **Dashboard-Parameter** (Refresh-Rate, Anzeige-Optionen)
- **Debug-Informationen** für Entwickler
- **Modul-Config** mit Angaben zu den Modulen
- **Topic-Config** mit Anaben zu identifizierten Topics
- **MessageTemplates** Yml Beschreibung der NAchrichtenstrukturen


## 5) Nichtziele (MVP)
- **Komplexe Workflow-Engine** (spätere Version)
- **Erweiterte Analytics** (Dashboard-Fokus)
- **Multi-User-Support** (Einzelplatz-System)
- **Externe API-Integration** (MQTT-basiert)
- **Datenretention** konfigurierbar, zunächst unwichtig

## 6) Persistenz & Schemata
- **SQLite-Datenbank** für alle MQTT-Nachrichten
- **Nachrichten-Schema** mit Zeitstempel, Topic, Payload, QoS
- **Indexierung** für schnelle Abfragen nach Zeit und Topic


## 7) Konfiguration & Secrets
- **Streamlit Secrets** für MQTT-Credentials
- **Umgebungsvariablen** für Broker-Einstellungen
- **Default-Werte** für lokale Entwicklung
- **Runtime-Konfiguration** ohne Neustart

## 8) Performance & Skalierung
- **Nachrichten-Queue** mit 5.000 Nachrichten Kapazität
- **Background-Threads** für nicht-blockierende Verarbeitung
- **Effiziente Datenbankabfragen** mit Indizes
- **Memory-Management** für lange Laufzeiten

## 9) Fehlerbehandlung & Monitoring
- **Graceful Degradation** bei Verbindungsproblemen
- **Auto-Reconnect** mit exponentieller Backoff-Strategie
- **Benutzerfreundliche Fehlermeldungen**
- **Logging** für Debugging und Monitoring

## 10) Testing & Entwicklung
- **Test-Buttons** für direkte MQTT-Nachrichten
- **Debug-Informationen** in der Benutzeroberfläche
- **Unit-Tests** für alle Service-Funktionen
- **Integration-Tests** mit Live-Fabrik


