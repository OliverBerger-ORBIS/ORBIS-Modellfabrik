# Projektanalyse: Steuerung der Fischertechnik-Modellfabrik

**Datum der Analyse:** 18. August 2025

## 1. Zielsetzung

Das primäre Ziel des Projekts ist die Übernahme der Steuerung einer bestehenden Fischertechnik-Modellfabrik durch eine eigenentwickelte Orbis-Komponente. Die Kommunikation und Steuerung der einzelnen Fabrikmodule soll über das **MQTT-Protokoll** erfolgen, da alle Fischertechnik-Module über diese Schnittstelle ansprechbar sind.

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

## 4. Entwickelte Orbis-Komponenten (`src-orbis/`)

Die Orbis-Steuerungslösung basiert auf mehreren wiederverwendbaren Python-Komponenten:

1.  **Nachrichtenbibliothek (`mqtt_message_library.py`):** Eine zentrale Komponente, die Funktionen zur Erstellung korrekter MQTT-Nachrichten kapselt.
2.  **Remote-Steuerungsclient (`remote_mqtt_client.py`):** Ein Kommandozeilen-Tool zur direkten Interaktion mit der Fabrik.
3.  **Interaktives Dashboard (`aps_dashboard.py`):** Eine Streamlit-Anwendung zur Datenanalyse und zur grafischen Steuerung per MQTT.
4.  **Logging & Analyse-Skripte:** Werkzeuge zum Mitschneiden und Analysieren des MQTT-Traffics, die für Debugging und Validierung entscheidend sind.

## 5. Wichtige Erkenntnisse und nächste Schritte

-   **Direkte vs. automatische Steuerung:** Es wurde festgestellt, dass Basis-Aktionen (z.B. `PICK`) direkt per MQTT steuerbar sind, während komplexe Prozessschritte (z.B. der Fräsvorgang selbst) von der übergeordneten Fischertechnik-Logik ausgelöst werden. Die Orbis-Steuerung muss diese Logik nachbilden oder ersetzen.
-   **Grundlagen sind solide:** Die Analyse, Dokumentation und die entwickelten Werkzeuge bieten eine ausgezeichnete Basis für die vollständige Übernahme der Steuerung.

Diese Zusammenfassung dient als Einstiegspunkt für Entwickler, um die Architektur und den aktuellen Stand des Projekts schnell zu erfassen.
