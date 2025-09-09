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
- **📊 Übersicht**: Modul-Status, Lagerbestand, **Produktkatalog** (Blau, Weiß, Rot)
- **📡 Nachrichten-Zentrale**: Empfangene und gesendete MQTT-Nachrichten
- **🏭 Fertigungsaufträge**: **ERWEITERT** um Produktplanung & Produktionsverfolgung
- **🎮 Steuerung**: Haupt-Tab mit drei Untertabs
  - **Factory Steuerung**: Traditionelle Steuerungsfunktionen (Factory Reset, Module, FTS, Orders)
  - **Generic Steuerung**: Erweiterte MQTT-Steuerung (Freier Modus, Topic-getrieben, Message-getrieben)
  - **🎯 Sequenz-Steuerung**: Automatisierte Sequenz-Ausführung mit WAIT-Steps
- **🏗️ Shopfloor**: **NEU** - Routenplanung, Positionierung, Shopfloor-Layout (4x3-Grid)
- **⚙️ Einstellungen**: MQTT-Konfiguration und Dashboard-Parameter

## 3) Broker, Topics, Rechte
- **Live-Fabrik**: 192.168.0.100:1883 (Standard)
- **Replay-Station**: localhost:1884 (Test)
- **Topic-Subscription**: Alle Topics (#) für vollständiges Monitoring
- **Authentifizierung**: Optional über Username/Password

## 4) Funktionale Anforderungen
### 4.1) Übersicht - ✅ IMPLEMENTIERT + ✅ ERWEITERT
- **Modul-Status** in Echtzeit anzeigen aus den bereitgestellten Infos der Mqtt-Nachrichten. Statische Info wird aus den Einstellungen gezogen module.yml ✅
- **Lagerbestand** Ansicht der aktuellen Lager-Belegung (Nachricht vom HBW Modul) ✅
- **Kundenaufträge** Auslösen einer Bestellung von (ROT/WEISS/BLAU) bei Bestellung wird die Produktion gestartet ✅
- **Rohmaterial-Bestellungen** Übersicht über benötigte und verfügbare Rohmaterialien ✅
- **📦 Produktkatalog** - **NEU** - YAML-basierte Produktdefinitionen (Blau, Weiß, Rot) ✅
- **Status:** Vollständig funktional mit HTML-Templates für visuelle Darstellung, ohne falsche Bestand/Verfügbar-Info

#### **Begriffliche Unterscheidungen - Order-Typen**

**Problem:** Aktuell verwenden wir unklare Begriffe wie "order" oder "order_raw" für verschiedene Konzepte.

**Lösung:** Klare Trennung von Aufträgen und Bestellungen:

| **Zweck** | **Bezeichnung (Englisch)** | **URL-Pfad** |
|-----------|----------------------------|--------------|
| Kundenauftrag | **Customer Order** | `/customer_order` |
| Interner Fertigungsauftrag | **Production Order** | `/production_order` |
| Rohmaterialbeschaffung | **Purchase Order** | `/purchase_order` |

#### **✅ Implementierte Komponenten-Namensersetzungen**

**Overview-Komponenten:**
- `overview_order` → `overview_customer_order` ✅ **IMPLEMENTIERT**
- `overview_order_raw` → `overview_purchase_order` ✅ **IMPLEMENTIERT**

**Order-Komponenten:**
- `order` → `production_order` ✅ **IMPLEMENTIERT**
- `order_current` → `production_order_current` ✅ **IMPLEMENTIERT**
- `order_management` → `production_order_management` ✅ **IMPLEMENTIERT**

#### **Tab-Namen mit klarer Bedeutung**

| **Tab-Name** | **Bedeutung** |
|--------------|---------------|
| **Kundenaufträge (Customer Orders)** | Kundenbestellungen |
| **Fertigungsaufträge (Production Orders)** | Was aktuell produziert werden soll |
| **Rohmaterial-Bestellungen (Purchase Orders)** | Bestellungen bei Lieferanten |

> **✅ ABGESCHLOSSEN:** Alle Namensersetzungen wurden erfolgreich implementiert


### 4.2) Fertigungsaufträge (Production Orders) - 🔄 IN ENTWICKLUNG + 🆕 ERWEITERT

#### **Funktionalitäten:**
- **Auftragsverfolgung** über den gesamten Produktionsprozess
- **Ongoing Orders** - Gibt es welche, wenn ja, dann Auflistung
- **Aktuelle Produktionsschritte pro Ongoing Auftrag** - Aktualisierung der Info. Darstellung des Prozesses als Liste. Mit Status: geplant, in Arbeit, abgeschlossen
- **📋 Produktplanung** - **NEU** - Fertigungsaufträge aus Produktkatalog generieren ✅
- **🔄 Produktionsverfolgung** - **NEU** - Echtzeit-Tracking der Fertigungsaufträge ✅

#### **Beispiel: Production Order für ROTES Werkstück**

**Production Order ID:** `PO-2025-001-RED`  
**Werkstück-Typ:** RED  
**Status:** IN_PROGRESS  
**Erstellt:** 2025-01-04T10:30:00Z  

**Produktionsschritte:**

| **Schritt** | **Aktion** | **Modul** | **Status** | **Zeitstempel** |
|-------------|------------|-----------|------------|-----------------|
| 1 | Werkstück aus HBW holen | HBW → FTS | ✅ Abgeschlossen | 10:30:15 |
| 2 | FTS zu MILL transportieren | FTS | ✅ Abgeschlossen | 10:30:45 |
| 3 | Werkstück in MILL laden | MILL | ✅ Abgeschlossen | 10:31:00 |
| 4 | **Fräsen** | MILL | 🔄 **In Arbeit** | 10:31:15 |
| 5 | Werkstück aus MILL laden | MILL → FTS | ⏳ Geplant | - |
| 6 | FTS zu AIQS transportieren | FTS | ⏳ Geplant | - |
| 7 | Werkstück in AIQS laden | AIQS | ⏳ Geplant | - |
| 8 | Qualitätsprüfung | AIQS | ⏳ Geplant | - |
| 9 | Werkstück aus AIQS laden | AIQS → FTS | ⏳ Geplant | - |
| 10 | FTS zu DPS transportieren | FTS | ⏳ Geplant | - |
| 11 | Werkstück in DPS entladen | DPS | ⏳ Geplant | - |

**🎯 Current Production Step:** Schritt 4 - Fräsen in MILL  
**📍 Werkstück-Position:** MILL (grafische Hervorhebung in Fabrik-Landschaft)

#### **Order Information:**
- **Auftrags-ID:** `PO-2025-001-RED`
- **Werkstück-ID:** `RED-047f8cca341290`
- **Priorität:** Normal
- **Geschätzte Fertigstellung:** 10:35:00

#### **Weitere Funktionalitäten:**
- **Auftragshistorie** mit Zeitstempel und Status
- **Grafische Hervorhebung** der aktuellen Werkstück-Position in der Fabrik-Landschaft
- ***ProduktionsProzess-Definition***
- ****Prozess Blau****: HBW -> MILL > DRILL -> AIQS -> DPS (Ausgang)
- ****Prozess Rot****: HBW -> MILL -> AIQS -> DPS (Ausgang)
- ****Prozess Weiß****: HBW -> DRILL -> AIQS -> DPS (Ausgang)


### 4.3) Nachrichten-Zentrale - ✅ IMPLEMENTIERT
- **Empfangene Nachrichten** von allen Modulen ✅
- **Gesendete Nachrichten** Nachrichten vom OMF-Dashboard (aus der Steuerung) an den APS-Broker ✅
- **Nachrichtenfilterung** nach Zeit, Topic, Richtung ✅
- **SQLite-Persistierung** für Audit-Trail ✅
- **Status:** Vollständig funktional - sowohl empfangene als auch gesendete Nachrichten werden korrekt angezeigt
- **Hinweis:** History löschen wurde implementiert und funktioniert

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
- **Hinweis:** Diese Funktionalitäten sind für zukünftige Erweiterungen geplant

#### 4.4.3) Architektur
- **Tab-Struktur**: Haupt-Tab "Steuerung" mit zwei Untertabs
- **Komponenten-Wiederverwendung**: Nutzt OMFMqttClient und MessageGenerator wie bei Factory Reset
- **Saubere Trennung**: Factory-Funktionen und Generic-Funktionen getrennt
- **Einheitliche API**: Beide Untertabs verwenden den gleichen MQTT-Client

### 4.5) Einstellungen - ✅ IMPLEMENTIERT
- **MQTT-Broker Konfiguration** (Host, Port, Credentials) ✅
- **Dashboard-Parameter** (Refresh-Rate, Anzeige-Optionen) ✅
- **Debug-Informationen** für Entwickler ✅
- **Modul-Config** mit Angaben zu den Modulen ✅
- **Topic-Config** mit Anaben zu identifizierten Topics ✅
- **MessageTemplates** Yml Beschreibung der NAchrichtenstrukturen ✅
- **Status:** Vollständig funktional mit allen Konfigurationsmöglichkeiten


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

## 11) Dashboard-Komponenten-Architektur (Bewährtes Vorgehen)

### 11.1) Komponenten-Struktur
**Basierend auf erfolgreichem Shopfloor-Refactoring:**

```
src_orbis/omf/dashboard/components/
├── [komponente].py              # Hauptkomponente (Wurzel)
├── [komponente]_[sub].py        # Unterkomponenten
├── [komponente]_utils.py        # Gemeinsame Utility-Funktionen
└── [komponente]_[funktion].py   # Spezifische Funktionalitäten
```

### 11.2) Architektur-Prinzipien
- **Hauptkomponente als Wurzel**: `[komponente].py` importiert alle Unterkomponenten
- **Utils-Datei für gemeinsame Funktionen**: Vermeidet zirkuläre Imports
- **Klare Abhängigkeiten**: Unterkomponenten importieren von Utils, nicht von Hauptkomponente
- **Streamlit-Integration**: Tabs/Untertabs in Hauptkomponente

### 11.3) Implementierungs-Schritte
1. **Analyse**: Bestehende Komponenten identifizieren
2. **Architektur-Design**: Hauptkomponente, Unterkomponenten, Utils definieren
3. **Komponenten-Implementierung**: Hauptkomponente mit Tabs, Unterkomponenten mit Funktionen
4. **Tests erstellen**: Unit-Tests für jede Komponente in `tests_orbis/test_omf/`
5. **Pre-commit Validierung**: Alle Tests müssen durchlaufen (black, isort, ruff, pytest)

### 11.4) Beispiel: Shopfloor-Komponenten (✅ Erfolgreich implementiert)
```
shopfloor.py              # Hauptkomponente mit Tabs
├── shopfloor_layout.py   # Layout-Unterkomponente
├── shopfloor_routes.py   # Routen-Unterkomponente
├── shopfloor_positioning.py # Positionierungs-Unterkomponente
└── shopfloor_utils.py    # Gemeinsame Utility-Funktionen
```

**Status:** ✅ **Bewährtes Vorgehen** - Alle Tests laufen durch, Pre-commit funktioniert

## 12) Implementierte Features (Januar 2025)

### 12.1) Dashboard-Komponenten-Erweiterung ✅
**Neue Komponenten implementiert:**
- **📦 Produktkatalog** (`overview_product_catalog.py`) - YAML-basierte Produktdefinitionen
- **📋 Produktplanung** (`production_order_production_planning.py`) - Fertigungsaufträge aus Produktkatalog
- **🗺️ Shopfloor-Layout** (`shopfloor_layout.py`) - 4x3 Grid mit Modul-Icons

### 12.2) HTML-Template-System ✅
**Neue Templates erstellt:**
- **`get_product_catalog_template()`** - Produktboxen ohne Bestand/Verfügbar-Info
- **`get_workpiece_box_template()`** - Bestehende Templates für andere Verwendungen
- **Konsistente Darstellung** - ROT, BLAU, WEISS Produkte mit Material/Farbe/Größe

### 12.3) Icon-System-Integration ✅
**Modul-Icons korrekt geladen:**
- **Direkte `st.image()` Integration** - Wie ORBIS-Logo im Header
- **Icon-Mapping** - CHRG0 → CHRG für Ladestation
- **Fallback-Emojis** - Wenn Icons nicht gefunden werden
- **Robuste Pfad-Auflösung** - Keine komplexen AssetManager-Imports

### 12.4) YAML-Konfiguration ✅
**Erweiterte Produktkatalog-Struktur:**
```yaml
products:
  red:
    name: "Rot"
    material: "Kunststoff"
    color: "Rot"
    size: "Standard"
    manufacturing_steps:
      - {step: 1, module: "MILL", description: "Fräsen"}
      - {step: 2, module: "AIQS", description: "Qualitätskontrolle"}
```

### 12.5) Test-Abdeckung ✅
**Umfassende Tests erstellt:**
- **`test_new_dashboard_components.py`** - 9 Tests für neue Komponenten
- **Import-Tests** - Alle Komponenten können importiert werden
- **Funktionalitäts-Tests** - YAML-Loading, HTML-Templates, Icon-Loading
- **Struktur-Tests** - YAML-Konfiguration validiert
- **24 Tests laufen erfolgreich durch** - 100% Erfolgsrate

### 12.6) Architektur-Konsistenz ✅
**Bewährtes Vorgehen befolgt:**
- **Ein Script pro Tab/Untertab** - Konsistente Struktur
- **Namenskonventionen** - `overview_product_catalog.py`, `production_order_production_planning.py`
- **Keine zirkulären Imports** - Saubere Abhängigkeiten
- **Pre-commit-konform** - Alle Tests laufen durch

### 12.7) Fertigungsablauf-Darstellung ✅
**Produktionsplanung implementiert:**
- **Vertikale Boxen** - Fertigungsschritte untereinander
- **HBW als erste Box** - Anlieferung
- **DPS als letzte Box** - Abgabe
- **Modul-Icons** - Visuelle Darstellung der Fertigungsschritte
- **Beschreibungen** - Aus YAML-Konfiguration

**Status:** ✅ **Alle Features vollständig implementiert und getestet**


