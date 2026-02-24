# Glossary – Eindeutige Begrifflichkeiten

> **Referenz** für Begriffe im OSF-Projekt. Technische Details: [Naming Conventions](02-architecture/naming-conventions.md).

---

## Kernbegriffe & Terminologie (Core Concepts)

### Event (Ereignis)
Ein diskretes Vorkommnis auf dem Shopfloor, z.B. eine Statusänderung eines Sensors oder der Start/Stopp einer Maschine. Im OSF/DSP-Kontext werden Events **normalisiert** (standardisiert), um sie systemunabhängig verarbeitbar zu machen.

### Context (Kontext)
Informationen, die einem Event Bedeutung geben. Ein rohes Sensor-Signal wird erst durch Kontext wertvoll: Welcher **Auftrag** (Order)? Welches **Werkstück** (Workpiece)? Welche **Station**? Welche **Zeit**? Der Prozess des Hinzufügens dieser Information heißt **Enrichment** (Anreichern).

### Order (Auftrag)
Eine Anforderung zur Herstellung eines Produkts oder Erbringung einer Dienstleistung.
- **Customer Order:** Vertriebsauftrag (ERP).
- **Production Order:** Fertigungsauftrag (MES).
- **Transport Order:** Fahrauftrag an das FTS.

### Workpiece / SinglePart (Werkstück)
Das physische Produkt, das gefertigt wird. In der Modellfabrik identifiziert durch einen **NFC-Code** (SinglePart-Tracking). Im DSP-Kontext oft als "SinglePart" bezeichnet, um die Granularität (Losgröße 1) zu betonen.

### Station
Ein physischer Ort oder eine Maschine, an dem ein Wertschöpfungsschritt stattfindet (z.B. Bohren an der DRILL-Station, Fräsen an der MILL-Station).

### Transfer (FTS / AGV)
Die Bewegung von Material zwischen Stationen.
- **FTS:** Fahrerloses Transportsystem (deutscher Begriff).
- **AGV:** Automated Guided Vehicle (internationaler Begriff).
In der UI wird meist "FTS (AGV)" verwendet, um beide Begriffe abzudecken.

---

## Konzept & Systeme

### OSF (ORBIS-SmartFactory)
Konzept und Vision – unsere Produkte (DSP, MES, …) und Leistungen demonstrierbar machen. Use Cases, Demos, Messeauftritte. OSF ist kein produktives System, sondern Demonstrator.

### OSF-UI
Unser Dashboard zur Visualisierung des OSF-Konzeptes. Angular (`osf/`), ehemals OMF3.

### FMF (Fischertechnik-ModellFabrik)
Physische Komponenten – Shopfloor der Miniatur-Fabrik (HBW, DRILL, MILL, AIQS, DPS, FTS, …). Teil des Fischertechnik-Produkts APS 24V.

### APS (Agile Production Simulation)
Software-Teil der Fischertechnik APS 24V: CCU, Node-RED, Frontend, mosquitto, TXT-Programme, PLC-Programme. Steuert die FMF.

### ORBIS-DSP, ORBIS-MES
Externe ORBIS-Produkte. Änderungen erfolgen nicht in diesem Repo.

### OMF2 (Legacy)
Legacy Streamlit-Dashboard (`omf2/`). Wird durch OSF-UI ersetzt.

---

## Rollen & Zielgruppen

### Anwender / Demonstratoren
Präsentieren OSF auf Messen oder bei Kunden. Nutzen Use-Case-Bibliothek, OBS-Setup. Siehe Quick Start – Anwender/Demonstratoren.

### Messebauer
Firmen/Bau, die den Messetisch bauen. **Messetisch-Spezifikation** (`05-hardware/messetisch-spezifikation.md`) ist für Messebauer, nicht für Demonstratoren.

---

## System-Komponenten

### APS-CCU (Central Control Unit)
Zentrale Steuerungseinheit (Raspberry PI). Erstellt und verwaltet Produktionsaufträge. MQTT: `ccu/order/request`, `ccu/state/*`

### APS-NodeRED
MQTT ↔ OPC-UA Vermittler. Übersetzt MQTT-Befehle zu OPC-UA, aggregiert Status-Daten.

### Module
Physische Produktionsmodule (HBW, DRILL, MILL, AIQS, DPS). Teil der FMF. Steuerung über OPC-UA (via Node-RED), Status über MQTT.

### FTS (Fahrerlose Transportsysteme)
Automatische Transporteinheiten. MQTT: `fts/v1/ff/5iO4/*`

### TXT Controller
Fischertechnik TXT 4.0 Controller für Sensoren, Kamera, NFC. MQTT: `/j1/txt/1/f/i/*`

---

## MQTT & Messages

### Topic
MQTT-Topic-String. Schema: `module/v1/ff/{serial}/{type}`

### Template
Topic-freie Definition einer MQTT-Nachrichtenstruktur. Schema: `domain.object.variant` (z.B. `module.state.drill`). Templates enthalten KEINE Topic-Strings.

### Mapping
Verbindung zwischen Topic und Template. Exact > Pattern.

### Order (Outbound)
Befehl an Module. z.B. `module/v1/ff/SVR4H76449/order` mit `{"command": "DRILL"}`

### State (Inbound)
Status-Update von Modul. z.B. `module/v1/ff/SVR4H76449/state`

### Connection States
`ONLINE`, `OFFLINE`, `CONNECTIONBROKEN`

---

## IDs

### Serial Numbers (Module)
Format: `SVR` + 3 Ziffern + 2 Buchstaben + 4 Ziffern. Beispiele: `SVR3QA0022` (HBW), `SVR4H76449` (DRILL).

### NFC Codes (Workpieces)
14-stellige Hex-Zeichenkette. Regex: `^[0-9A-Fa-f]{14}$`

### Order IDs
UUID v4 oder sequenzielle Nummer.

### Action IDs
UUID v4, eindeutig je Aktion.

---

## Action States

- **PENDING** – wartet auf Start
- **RUNNING** – wird ausgeführt
- **FINISHED** – erfolgreich
- **FAILED** – fehlgeschlagen

---

## Commands

### Module
PICK, DROP, STORE, DRILL, MILL, CHECK_QUALITY

### CCU
RESET_FACTORY, PAUSE_PRODUCTION, RESUME_PRODUCTION

---

## Workpiece Types

**Farben:** RED, WHITE, BLUE

**Order Types:** STORAGE, PRODUCTION, AI

---

## Template-Keys (Auswahl)

- `module.state.{subtype}`, `module.connection.{subtype}`, `module.order.{subtype}`
- `ccu.state.pairing`, `ccu.state.status`, `ccu.state.stock`
- `fts.connection`, `fts.state`, `fts.order`

---

## Topic-Patterns

```
module/v1/ff/{module_id}/state → module.state
module/v1/ff/{module_id}/order → module.order
ccu/state/pairing → ccu.state.pairing
```
