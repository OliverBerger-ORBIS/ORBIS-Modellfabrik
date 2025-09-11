# Session Manager - Anforderungsdokument

## Übersicht
Neue Streamlit-Anwendung zur Verwaltung und Analyse von MQTT-Sessions für die ORBIS Modellfabrik.

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
- **Session-Verzeichnis:** `mqtt-data/sessions/aps_persistent_traffic-...`
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
4. **Session-Verzeichnis** - Verwendung der Sessions in mqtt-data/sessions/  (später ggf anderes Verzeichnis wählen)

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
4. **Session-Verzeichnis** - Verwendung der Sessions in mqtt-data/sessions/ ✅

### 🔧 Phase 1.1: Replay Station Verbesserungen (IN ARBEIT)
1. **MQTT Integration** ✅ - mosquitto_pub subprocess calls
2. **Session Loading** ✅ - SQLite + Log file support
3. **Replay Controls** ✅ - Play/Pause/Stop/Reset
4. **Progress Display** ✅ - Progress bar + message count
5. **Logging System** ✅ - Detailliertes Logging für Debugging
6. **UI State Management** ✅ - st.rerun() für sofortige Updates

### ✅ Phase 1.2: Bekannte Probleme (BEHOBEN)
1. **Replay Controls:** Play-Button sendet keine Nachrichten ✅
2. **Progress Bar:** Bleibt bei 0% stehen ✅
3. **Button States:** Pause-Button bleibt aktiv nach Pause ✅
4. **Threading:** Replay Worker Thread-Probleme ✅
5. **Original Timing:** Echte Zeitdifferenzen aus Session-Timestamps ✅
6. **Geschwindigkeiten:** 1/5x, 1/3x, 1/2x, 1x, 2x, 3x, 5x ✅

### 📋 Phase 2: Erweiterte Features (GEPLANT)
1. **Session Analyse Tab** - Timeline-Visualisierung
2. **Session Recorder Tab** - Live-Aufnahme
3. **Template Analyse Tab** - Pattern-Analyse

## Next Steps

### ✅ Sofort verfügbar
- **Replay Station:** Vollständig funktionsfähig und getestet
- **Original Timing:** Echte Zeitdifferenzen aus Session-Timestamps
- **Geschwindigkeiten:** 1/5x bis 5x mit korrekter Skalierung
- **MQTT Integration:** mosquitto_pub subprocess calls
- **Session Management:** SQLite + Log file support

### 🔧 Nächste Schritte
1. **Tests implementieren** für Session Manager Komponenten
2. **Session Analyse Tab** entwickeln
3. **Session Recorder Tab** implementieren
4. **Template Analyse Tab** erstellen
5. **CI/CD Integration** mit pre-commit hooks

### 🚀 Deployment
- **Branch:** `helper/session-manager` erstellt
- **Status:** Bereit für Commit und Push
- **Testing:** Manuelle Tests erfolgreich durchgeführt

## Technische Details

### MQTT Integration
- **Protokoll:** mosquitto_pub subprocess calls
- **Broker:** localhost:1883 (Standard MQTT Port)
- **QoS:** Level 1 für zuverlässige Übertragung
- **Timeout:** 5 Sekunden pro Nachricht

### Session Management
- **Formate:** SQLite (.db) + Log (.log) Dateien
- **Verzeichnis:** mqtt-data/sessions/
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