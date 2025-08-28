# Projektanalyse: Steuerung der Fischertechnik-Modellfabrik

**Datum der Analyse:** 18. August 2025  
**Letztes Update:** 28. August 2025

## 1. Zielsetzung

Das primäre Ziel des Projekts ist die vollständige Übernahme der Steuerung einer bestehenden Fischertechnik-Modellfabrik durch eine eigenentwickelte Orbis-Komponente. Die Kommunikation erfolgt über **Template Messages** mit **MQTT-Protokoll**, wobei die CCU (Central Control Unit) die ORDER-ID Generierung und Workflow-Orchestrierung übernimmt.

## 2. Projektstruktur und Organisation

Das Projekt ist logisch in zwei Bereiche unterteilt, um eine klare Trennung zwischen den ursprünglichen Fischertechnik-Artefakten und den neuen Orbis-Entwicklungen zu gewährleisten.

-   **Original Fischertechnik-Komponenten:**
    -   `Node-RED/`: Flows und Konfigurationen für Node-RED.
    -   `PLC-programs/`: Programme für die S7-SPS.
    -   `TXT4.0-programs/`: Programme für den Fischertechnik TXT 4.0 Controller.
    -   `doc/`: Original-Dokumentation und Bilder.

-   **Orbis-spezifische Entwicklungen:**
    -   `src-orbis/`: Der Quellcode für die neuen Steuerungs- und Analysekomponenten (in Python).
    -   `docs-orbis/`: Eine dedizierte, erweiterte Dokumentation für die Orbis-Komponenten und die MQTT-Analyse.
    -   `tests-orbis/`: Unit Tests für die Orbis-Komponenten.

## 3. Kerntechnologie: MQTT

MQTT wurde als zentrale Schnittstelle für die Kommunikation identifiziert. Die Analyse der MQTT-Kommunikation hat entscheidende Erkenntnisse geliefert, die in der Dokumentation festgehalten sind:

-   **Funktionierende Befehle:** Eine detaillierte Liste von verifizierten MQTT-Nachrichten für Module wie `DRILL`, `MILL` und `AIQS` ist in `docs-orbis/mqtt/working-mqtt-messages.md` dokumentiert.
-   **Steuerungszusammenfassung:** Eine Management-Übersicht in `docs-orbis/mqtt/mqtt-control-summary.md` fasst die direkt steuerbaren Aktionen (`PICK`, `DROP`, `STORE`, `CHECK_QUALITY`) pro Modul zusammen.
-   **Verbindungsparameter:** Der MQTT-Broker ist unter `192.168.0.100:1883` mit den Standard-Credentials `default`/`default` erreichbar.

## 4. Entwickelte Orbis-Komponenten (`src_orbis/`)

Die Orbis-Steuerungslösung basiert auf mehreren erweiterten Python-Komponenten mit moderner YAML-basierter Konfiguration:

### **4.1 Zentrale Konfigurations-Manager:**
1. **NFC Code Manager (`nfc_code_manager.py`):** Zentrale Verwaltung aller NFC-Codes mit Friendly-IDs
2. **Module Manager (`module_manager.py`):** Konfiguration aller APS-Module (ID, Name, Typ, IP-Range)
3. **Topic Manager (`topic_manager.py`):** Topic-Mappings und Friendly-Names für alle MQTT-Topics
4. **Message Template Manager (`message_template_manager.py`):** YAML-basierte MQTT-Templates mit UI-Konfiguration

### **4.2 Dashboard & Analyse:**
5. **Interaktives Dashboard (`aps_dashboard.py`):** Modernisierte Streamlit-Anwendung mit:
   - Template-basierte Modul-Steuerung (DRILL, MILL, AIQS, FTS)
   - Factory Reset Integration
   - Order Management (ROT, WEISS, BLAU)
   - Zentrale Konfigurations-Verwaltung
   - Node-RED Integration
6. **Session-Analyse Tools:** Template Analyzer für CCU, TXT, Module, Node-RED
7. **Order Tracking Manager (`order_tracking_manager.py`):** Order-Status und -Historie

### **4.3 MQTT Infrastructure:**
8. **Enhanced MQTT Client:** Erweiterte MQTT-Kommunikation mit Template-Unterstützung
9. **Persistent Logging:** Session-basierte MQTT-Traffic Aufzeichnung und Analyse

## 5. Wichtige Erkenntnisse und aktueller Stand

### **5.1 Moderne Architektur (August 2025):**
- **YAML-basierte Konfiguration:** Alle Einstellungen zentral in YAML-Dateien
- **Manager-Pattern:** Separate Manager für NFC, Module, Topics, Templates
- **Template-basierte Steuerung:** Alle Module über Message Templates gesteuert
- **Dashboard-Integration:** Vollständige Integration aller Konfigurationen
- **Bereinigte Struktur:** Alte Komponenten entfernt, moderne Architektur

### **5.2 Template Message Strategie:**
- **CCU-Orchestrierung:** Die CCU (Central Control Unit) generiert ORDER-IDs und orchestriert alle Workflows
- **Template Messages:** Vollständige YAML-basierte Template-Bibliothek
- **Farb-spezifische Verarbeitung:** ROT (MILL), WEISS (DRILL), BLAU (DRILL+MILL)
- **Workflow-Konsistenz:** Auftrag und AI-not-ok haben identische Workflows pro Farbe
- **ORDER-ID Tracking:** CCU-generierte IDs werden vom Dashboard verfolgt

### **5.3 Vollständige Workflow-Analyse:**
- **15 Sessions analysiert:** Wareneingang (9), Auftrag (3), AI-not-ok (3)
- **12.420 MQTT-Nachrichten:** Systematisch analysiert und dokumentiert
- **3 Workflow-Typen:** Vollständig verstanden und als Templates implementiert
- **Konsistente ORDER-ID Generierung:** CCU-Verhalten dokumentiert und vorhergesagt

### **5.4 Nächste Schritte:**
1. **Live APS Test:** Template Messages mit echter APS validieren
2. **ORDER-ID Tracking:** CCU-generierte IDs in Echtzeit verfolgen
3. **Workflow Automation:** Erweiterte Automatisierung implementieren

### **5.5 Projekt-Status:**
- ✅ **Zentrale Konfiguration:** NFC, Module, Topics, Templates vollständig YAML-basiert
- ✅ **Message Template Manager:** Vollständig implementiert und getestet
- ✅ **Dashboard Integration:** Template-basierte Steuerung vollständig integriert
- ✅ **Order Tracking:** Order-Status und -Historie implementiert
- ✅ **System Modernisierung:** Alte Komponenten entfernt, neue YAML-basierte Architektur
- ✅ **Live-Integration:** Dashboard funktioniert vollständig mit allen Features
- ✅ **Dokumentation bereinigt:** Veraltete Dokumentation entfernt, aktuelle Architektur dokumentiert

Diese Zusammenfassung spiegelt den aktuellen Stand (August 2025) wider: Ein vollständig modernisiertes System mit zentraler YAML-Konfiguration, bereit für Live-Integration und Test mit der echten APS-Modellfabrik.
