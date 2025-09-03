# OMF Streamlit Dashboard Anforderungen

## 1) Ziel und Nutzen
- **Nachbau der Applikation APS von Fischertechnuk**
- **Echtzeit-Monitoring** aller Module und deren Status
- **Nachrichtenverwaltung** mit Persistierung und Historie
- **Steuerung der Fabrik-Module, Komponenten und Prozesse** durch Versenden von MQTT-Messages, so wie es die APS Applikation macht.
- **MessageTemplate** Syntaktische und Semantische  Beschreibung der Nachrichten der APS, sowie Kopplung zu den MQTT-Topics, damit eine Steuerung möglich ist.
- **Replay-Station** Abspielen von zuvor aufgenommenn Sessions (Nachrichten-Auustausch) zu Testzwecken, dazu kann das dashboard wahlweise die Verbindung zu APS-MQTT-Broker oder zu einem lokalen BRoker aufgebaut werden, der über ein separates dashboard, die aufgenommenen Nachrichten abspielen=senden kann.

## 2) Architektur (kurz)
- **OMFMqttClient** als zentraler MQTT-Client (Singleton-Pattern)
- **@st.cache_resource** für persistente Services über Streamlit-Reruns
- **Einzelner MQTT-Client** für Subscribe und Publish
- **Thread-sichere Nachrichtenverarbeitung** mit deque-System
- **Hinweis:** MessageMonitorService wurde durch OMFMqttClient ersetzt

### 2.1) Dashboard Tab-Struktur
- **Übersicht**: Modul-Status und Lagerbestand
- **Nachrichten-Zentrale**: Empfangene und gesendete MQTT-Nachrichten
- **Steuerung**: Haupt-Tab mit zwei Untertabs
  - **Factory Steuerung**: Traditionelle Steuerungsfunktionen (Factory Reset, Module, FTS, Orders)
  - **Generic Steuerung**: Erweiterte MQTT-Steuerung (Freier Modus, Topic-getrieben, Message-getrieben)
- **Einstellungen**: MQTT-Konfiguration und Dashboard-Parameter

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

### 4.3) Nachrichten-Zentrale - 🔄 TEILWEISE IMPLEMENTIERT
- **Empfangene Nachrichten** von allen Modulen ✅
- **Gesendete Nachrichten** Nachrichten vom OMF-Dashboard (aus der Steuerung) an den APS-Broker an ❌
- **Nachrichtenfilterung** nach Zeit, Topic, Richtung ✅
- **SQLite-Persistierung** für Audit-Trail ✅
- **Status:** Empfangene Nachrichten funktionieren, gesendete Nachrichten werden nicht angezeigt
- **Bekanntes Problem:** History löschen funktioniert nicht korrekt

### 4.4) Steuerung
**Haupt-Tab mit zwei Untertabs für bessere Übersichtlichkeit:**

#### 4.4.1) Factory Steuerung (Untertab 1) - ✅ IMPLEMENTIERT
- **Factory Reset** für komplette Fabrik-Rücksetzung ✅
- **Modul-Sequenzen** für AIQS, MILL, DRILL ✅
  - Einzelne Schritte: PICK, PROCESS (MILL/CHECK_QUALITY/DRILL), DROP ✅
  - Komplette Sequenzen für jedes Modul ✅
- **FTS-Befehle** für Transport und Docking ✅
  - Laden, Entladen, Reset, Stop ✅
  - Docke an (nur nach Factory Reset) ✅
- **Auftragssteuerung** für Produktionsabläufe ✅
  - ROT, WEISS, BLAU Aufträge ✅
- **Status:** Funktioniert mit hardcodierten funktionierenden Topic-Payload-Kombinationen
- **Hinweis:** MessageGenerator-Integration noch nicht implementiert

#### 4.4.2) Generic Steuerung (Untertab 2) - 🔄 TEILWEISE IMPLEMENTIERT
- **Freier Modus**: Topic und Message können frei eingegeben werden ✅
  - Editierbare Textfelder für Topic und JSON-Payload ✅
  - Button "Versenden mit MQTT-Client" sendet direkt über OMFMqttClient ✅
  - Verwendet die gleichen Komponenten wie Factory Reset (OMFMqttClient, MessageGenerator) ✅
- **Topic-getrieben**: Verwendung des MessageGenerators und Auswahl eines Topics aus der `topic-config.yml` ❌
  - Verfügbare Messages werden vorgeschlagen ❌
  - Messages können editiert werden ❌
  - Versenden über MQTT-Client ❌
- **Message-getrieben**: Verwendung des MessageGenerators Auswahl einer Message aus `messageTemplate.yml` ❌
  - Dazugehöriges Topic wird in Auswahlbox angeboten ❌
  - Messages können editiert und versendet werden ❌
- **Status:** Nur "Freier Modus" funktional, YAML-Integration noch nicht implementiert

#### 4.4.3) Architektur
- **Tab-Struktur**: Haupt-Tab "Steuerung" mit zwei Untertabs
- **Komponenten-Wiederverwendung**: Nutzt OMFMqttClient und MessageGenerator wie bei Factory Reset
- **Saubere Trennung**: Factory-Funktionen und Generic-Funktionen getrennt
- **Einheitliche API**: Beide Untertabs verwenden den gleichen MQTT-Client

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


