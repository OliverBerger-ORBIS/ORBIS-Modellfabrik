# Projektanalyse: Steuerung der Fischertechnik-Modellfabrik

**Datum der Analyse:** 18. August 2025  
**Letztes Update:** 19. August 2025

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
    -   `tests-orbis/`: Zukünftiger Ort für Tests der Orbis-Komponenten.

## 3. Kerntechnologie: MQTT

MQTT wurde als zentrale Schnittstelle für die Kommunikation identifiziert. Die Analyse der MQTT-Kommunikation hat entscheidende Erkenntnisse geliefert, die in der Dokumentation festgehalten sind:

-   **Funktionierende Befehle:** Eine detaillierte Liste von verifizierten MQTT-Nachrichten für Module wie `DRILL`, `MILL` und `AIQS` ist in `docs-orbis/mqtt/working-mqtt-messages.md` dokumentiert.
-   **Steuerungszusammenfassung:** Eine Management-Übersicht in `docs-orbis/mqtt/mqtt-control-summary.md` fasst die direkt steuerbaren Aktionen (`PICK`, `DROP`, `STORE`, `CHECK_QUALITY`) pro Modul zusammen.
-   **Verbindungsparameter:** Der MQTT-Broker ist unter `192.168.0.100:1883` mit den Standard-Credentials `default`/`default` erreichbar.

## 4. Entwickelte Orbis-Komponenten (`src_orbis/`)

Die Orbis-Steuerungslösung basiert auf mehreren erweiterten Python-Komponenten:

### **4.1 Template Message System:**
1. **Template Message Manager (`template_message_manager.py`):** Kernkomponente für parameterisierte MQTT-Nachrichten mit ORDER-ID Tracking
2. **Template Control Dashboard (`template_control.py`):** Streamlit UI-Komponenten für Template-Steuerung und Order-Monitoring
3. **9 verschiedene Templates:** Für alle Workflow-Typen (Wareneingang, Auftrag, AI-not-ok) und Farben (Rot, Weiss, Blau)

### **4.2 Dashboard & Analyse:**
4. **Interaktives Dashboard (`aps_dashboard.py`):** Erweiterte Streamlit-Anwendung mit Template Control, Icon-Integration und Session-Analyse
5. **Session-Analyse Tools:** Umfassende MQTT-Traffic Analyse (15 Sessions, 12.420 Nachrichten analysiert)
6. **Workflow-Dokumentation:** Systematische Dokumentation aller APS-Workflows

### **4.3 MQTT Infrastructure:**
7. **Enhanced MQTT Client (`remote_mqtt_client.py`):** Erweiterte MQTT-Kommunikation mit Template-Unterstützung
8. **Message Library (`mqtt_message_library.py`):** Zentrale Bibliothek für MQTT-Nachrichten
9. **Persistent Logging:** Session-basierte MQTT-Traffic Aufzeichnung und Analyse

## 5. Wichtige Erkenntnisse und aktueller Stand

### **5.1 Template Message Strategie (August 2025):**
- **CCU-Orchestrierung:** Die CCU (Central Control Unit) generiert ORDER-IDs und orchestriert alle Workflows
- **Template Messages:** 9 verschiedene Templates decken alle Workflow-Typen ab (Wareneingang, Auftrag, AI-not-ok)
- **Farb-spezifische Verarbeitung:** ROT (MILL), WEISS (DRILL), BLAU (DRILL+MILL)
- **Workflow-Konsistenz:** Auftrag und AI-not-ok haben identische Workflows pro Farbe
- **ORDER-ID Tracking:** CCU-generierte IDs werden vom Dashboard verfolgt

### **5.2 Vollständige Workflow-Analyse:**
- **15 Sessions analysiert:** Wareneingang (9), Auftrag (3), AI-not-ok (3)
- **12.420 MQTT-Nachrichten:** Systematisch analysiert und dokumentiert
- **3 Workflow-Typen:** Vollständig verstanden und als Templates implementiert
- **Konsistente ORDER-ID Generierung:** CCU-Verhalten dokumentiert und vorhergesagt

### **5.3 Nächste Schritte:**
1. **Template Manager Integration:** Dashboard-Integration für Live-Test
2. **Live APS Test:** Template Messages mit echter APS validieren
3. **ORDER-ID Tracking:** CCU-generierte IDs in Echtzeit verfolgen
4. **Workflow Automation:** Erweiterte Automatisierung implementieren

### **5.4 Projekt-Status:**
- ✅ **Template Message Manager:** Vollständig implementiert und getestet
- ✅ **Workflow-Analyse:** Umfassend abgeschlossen und dokumentiert  
- ✅ **Dashboard Components:** UI für Template Control fertiggestellt
- 🚧 **Live-Integration:** Bereit für Dashboard-Integration und Live-Test

Diese Zusammenfassung spiegelt den aktuellen Stand (August 2025) wider: Ein vollständig implementiertes Template Message System, bereit für Live-Integration und Test mit der echten APS-Modellfabrik.
