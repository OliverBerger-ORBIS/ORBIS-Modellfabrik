# Session Manager - Anforderungsdokument

## Übersicht
Neue Streamlit-Anwendung zur Verwaltung und Analyse von MQTT-Sessions für die ORBIS Modellfabrik.

## 🎯 Zweck im Gesamtprojekt

Der Session Manager ist ein **unabhängiger Helper App** zur Analyse der APS Fischertechnik Miniatur-Fabrik. Er dient dem Verständnis der Nachrichten-Semantik und -Funktionsweise für die Entwicklung einer eigenen Steuerungsanwendung.

### 🏭 Kontext: APS-Fischertechnik
- **Reale Miniatur-Fabrik** mit verschiedenen Modulen
- **MQTT-Kommunikation** zwischen Fabrik-Komponenten
- **Ziel:** Verstehen der Nachrichten-Ströme für eigene Steuerung

### 🔗 System-Architektur
- **Status:** Unabhängige Helper-Anwendung
- **Keine Integration:** Vollständig unabhängig vom OMF Dashboard
- **Replay-Zweck:** Abspielen von Sessions über lokalen MQTT-Broker
- **Separate Entwicklung:** Unabhängige Wartung und Weiterentwicklung

## Architektur
- **Name:** Session Manager
- **Framework:** Streamlit (wie omf_dashboard)
- **Struktur:** Komponenten-basiert (wie omf_dashboard)
- **Standards:** Naming-Konventionen und Development Rules wie omf_dashboard

## Tab-Struktur

### 1. 📡 Replay Station
- **Funktionalität:** Wie alte Replay Station - Abspielen aufgenommener Sessions
- **Zweck:** MQTT-Sessions für Tests und Analyse wiedergeben
- **Status:** ✅ Implementiert und testbar

#### 1.1 MQTT-Verbindung
- **Broker:** Mosquitto Broker (localhost:1883)
- **Verbindungsstatus:** Verbunden/Nicht verbunden anzeigen
- **Verbindungssteuerung:** Testen/Trennen Buttons
- **QoS:** Level 1 für zuverlässige Übertragung

#### 1.2 Session-Management
- **Session-Verzeichnis:** `data/omf-data/sessions/aps_persistent_traffic-...`
- **Unterstützte Formate:** SQLite (.db) + Log (.log) Dateien
- **Regex-Filter:** Dateiname-Filterung (z.B. "Waren" für Wareneingang-Sessions)
- **Session-Auswahl:** Dropdown mit gefilterten Sessions
- **Session-Laden:** Ein-Klick Session-Loading

#### 1.3 Replay-Kontrollen
- **Play/Resume:** Session starten/fortsetzen
- **Pause:** Session pausieren
- **Stop:** Session stoppen
- **Reset:** Session zurücksetzen
- **Geschwindigkeit:** 1x, 2x, 5x, 10x Replay-Speed
- **Loop:** Endlosschleife aktivieren/deaktivieren

#### 1.4 Fortschrittsanzeige
- **Progress Bar:** Visueller Fortschrittsbalken
- **Message Count:** Aktuelle/Gesamt Nachrichten
- **Status:** Aktiv/Pausiert/Beendet
- **Live-Updates:** Nahtlose oder periodische Aktualisierung

#### 1.5 Test-Funktionen (Niedrige Priorität)
- **MQTT-Test:** Einzelne Nachrichten für Tests senden
- **Topic-Test:** Spezifische Topics testen
- **Payload-Test:** Custom Payloads senden

### 2. 📊 Session Analyse
- **Funktionalität:** Analyse einer ausgewählten Session
- **Datenquelle:** `aps_persistent_traffic` Database
- **Features:** 
  - Session-Auswahl
  - Timeline-Visualisierung
  - Message-Statistiken

### 3. 🎙️ Session Recorder
- **Funktionalität:** Aufnahme von Sessions
- **Vorgänger:** `aps_persistent_traffic` (nur als Script verfügbar)
- **Script:** `start_end2end_session.py`
- **Features:**
  - Session-Start/Stop
  - Live-Monitoring
  - Session-Speicherung

### 4. 🔍 Template Analyse
- **Funktionalität:** Analyse aller APS-Sessions
- **Fokus:** Konzentration auf bestimmte Topics
- **Features:**
  - Topic-Filterung
  - Template-Erkennung
  - Pattern-Analyse

## Implementierungsplan

### Phase 1: Grundstruktur
1. **Zusammenfassung der Anforderungen** ✅
2. **Komponenten anlegen** (Session Manager Dashboard)
3. **Replay Station Tab** - Sofort testbar implementieren
4. **Session-Verzeichnis** - Verwendung der Sessions in data/omf-data/sessions/  (später ggf anderes Verzeichnis wählen)

### Phase 2: Erweiterte Features
4. **Session Analyse Tab**
5. **Session Recorder Tab**
6. **Template Analyse Tab**

## Technische Anforderungen
- **MQTT Integration:** Einfache paho-mqtt Integration (keine Abhängigkeit zu OMF-Klassen)
- **Database:** SQLite für Session-Speicherung
- **UI/UX:** Konsistent mit omf_dashboard
- **Testing:** Unit Tests für alle Komponenten
- **Unabhängigkeit:** Keine Abhängigkeiten zu OMF-spezifischen Klassen
- **Design Prinzipien:** KISS & DRY

## Implementierungsstatus

### ✅ Phase 1: Grundstruktur (ABGESCHLOSSEN)
1. **Zusammenfassung der Anforderungen** ✅
2. **Komponenten anlegen** (Session Manager Dashboard) ✅
3. **Replay Station Tab** - Sofort testbar implementieren ✅
4. **Session-Verzeichnis** - Verwendung der Sessions in data/omf-data/sessions/ ✅

### 🔄 Phase 2: Alle Komponenten (IN ENTWICKLUNG)
1. **Session Recorder** ✅ - MQTT-Aufnahme, SQLite/Log-Speicherung, manueller Refresh
2. **Session Analyse** 🔄 - Timeline-Visualisierung ✅, Graph-Visualisierung ❌
3. **Replay Station** ✅ - Session-Replay, Geschwindigkeitskontrolle, nur .db Dateien
4. **Template Analyse** 🔄 - Integration der bestehenden template_analyzers ❌
5. **Settings Management** ✅ - Zentralisierte Konfiguration aller Komponenten

### ✅ Phase 3: Architektur & Qualität (ABGESCHLOSSEN)
1. **Tab-Unabhängigkeit** ✅ - Jeder Tab vollständig unabhängig
2. **Settings-Integration** ✅ - Einheitliche Konfiguration
3. **Thread-Sicherheit** ✅ - Sichere MQTT-Callbacks
4. **Performance-Optimierung** ✅ - Keine unnötigen st.rerun() Calls
5. **Code-Qualität** ✅ - Debug-Logs entfernt, sauberer Code

## Status: IN ENTWICKLUNG 🔄

### ✅ Funktional verfügbar
- **Session Recorder:** MQTT-Aufnahme mit SQLite/Log-Speicherung
- **Replay Station:** Session-Replay mit Geschwindigkeitskontrolle
- **Settings Management:** Zentralisierte Konfiguration

### 🔄 In Entwicklung
- **Session Analyse:** Timeline-Visualisierung ✅, Graph-Visualisierung ❌
- **Template Analyse:** Integration der bestehenden template_analyzers ❌

### 🎯 Nächste Schritte: Graph-Visualisierung & Template-Integration
- **Graph-Visualisierung:** Message-Ketten basierend auf Meta-Daten (orderID, workpieceId, nfcCode)
- **Template-Integration:** Bestehende `analysis_tools/template_analyzers` nutzen
- **Message-Ketten-Analyse:** Identifikation der Verbindungen zwischen Messages

## Geplante Features

### 📊 Session Analyse - Graph-Visualisierung
**Ziel:** Gerichteter Graph aus Message-Ketten basierend auf Meta-Informationen
- **Wurzel-Message:** Startpunkt (z.B. CCU-Nachricht mit orderID)
- **Verbindungen:** Anhand von orderID, workpieceId, nfcCode, etc.
- **Visualisierung:** Graphische Darstellung der Message-Abhängigkeiten
- **Erkenntnis:** Welche Komponenten in welcher Reihenfolge beteiligt sind
- **Technologie:** NetworkX + Plotly für interaktive Graphen

### 🔍 Template Analyse - Message-Struktur-Bibliothek
**Ziel:** Template-Bibliothek für MessageGenerator
- **Bestehende Basis:** `analysis_tools/template_analyzers` nutzen
- **Verfügbare Analyzer:**
  - `ccu_template_analyzer.py` - CCU-Nachrichten analysieren
  - `module_template_analyzer.py` - Modul-Nachrichten analysieren
  - `node_red_message_analyzer.py` - Node-RED Nachrichten analysieren
  - `nodered_template_analyzer.py` - Node-RED Templates analysieren
  - `txt_template_analyzer.py` - TXT-Nachrichten analysieren
- **Funktion:** Messages generieren und parsen
- **Output:** YAML-Templates für MessageGenerator
- **UI:** Template-Bibliothek mit Vorschau und Validierung

## Technische Details

### MQTT Integration
- **Protokoll:** mosquitto_pub subprocess calls
- **Broker:** localhost:1883 (Standard MQTT Port)
- **QoS:** Level 1 für zuverlässige Übertragung
- **Timeout:** 5 Sekunden pro Nachricht

### Session Management
- **Formate:** SQLite (.db) + Log (.log) Dateien
- **Verzeichnis:** data/omf-data/sessions/
- **Filtering:** Regex-basierte Session-Auswahl
- **Loading:** Automatische Format-Erkennung

### UI/UX Features
- **Responsive Design:** Streamlit Column-Layout
- **Real-time Updates:** st.rerun() nach Aktionen
- **Progress Tracking:** Visual progress bar + message count
- **Error Handling:** User-friendly Fehlermeldungen
- **Logging:** Detailliertes Debug-Logging

### Threading & State Management
- **Background Threads:** Replay Worker für non-blocking UI
- **Session State:** Thread-safe data copying
- **State Updates:** Robuste st.session_state Zugriffe
- **Error Recovery:** Graceful error handling

## Debugging & Monitoring

### Logging System
- **File Logging:** session_manager.log
- **Console Logging:** Real-time output
- **Log Levels:** INFO, WARNING, ERROR
- **User Actions:** Alle Button-Clicks werden geloggt
- **MQTT Operations:** Nachrichten-Senden wird geloggt
- **Thread Operations:** Replay Worker wird geloggt

### Performance Monitoring
- **Message Throughput:** Nachrichten pro Sekunde
- **Thread Health:** Replay Worker Status
- **UI Responsiveness:** Button State Updates
- **Error Tracking:** Fehlerhäufigkeit und -typen