# 📚 APS "as IS" - Zentrale Referenz

**ORBIS-spezifische Ergänzung zur offiziellen Fischertechnik-Dokumentation**

> **📌 Offizielle Fischertechnik-Dokumentation (extern, öffentlich):**  
> - **MQTT-Dokumentation:** [GitHub – docs](https://github.com/fischertechnik/Agile-Production-Simulation-24V-Dev/tree/release/docs)  
> - **CCU (Anleitung + Source Code):** [GitHub – Agile-Production-Simulation-24V-Dev](https://github.com/fischertechnik/Agile-Production-Simulation-24V-Dev)  
> → Siehe [FISCHERTECHNIK-OFFICIAL](../FISCHERTECHNIK-OFFICIAL.md) für Details.

Diese Sektion ergänzt die offizielle Dokumentation mit **ORBIS-spezifischen, verifizierten Informationen**, basierend auf:
- ✅ Session-Analysen (data/osf-data/sessions/*.log)
- ✅ CCU-Backend Source-Code
- ✅ NodeRed Flow-Analyse
- ✅ MQTT-Log-Analysen

---

## 🗂️ Referenz-Dokumente

### 1. [**Component Overview**](component-overview.md) 🌟
**Komplett-Übersicht aller APS-Komponenten**
- Alle 10 Komponenten mit Details
- Komponenten-Matrix & Architektur-Diagramm
- Rollen, Protokolle, IPs, Client-IDs
- Quick-Lookup für häufige Fragen

### 2. [**Module Serial Mapping**](module-serial-mapping.md) ⭐
**Die zentrale Referenz-Tabelle**
- Module-Serial-Numbers
- Hardware-Typen (DPS, AIQS, FTS, etc.)
- TXT-Controller & OPC-UA Zuordnung
- IP-Adressen & Will Messages

### 3. [**Hardware-Architektur**](hardware-architecture.md)
**Physische System-Übersicht**
- Raspberry Pi & Docker-Container
- TXT-Controller Hardware
- SPS S7-1200 Module
- Netzwerk-Topologie (2 Diagramme)

### 4. [**MQTT-Topic-Conventions**](mqtt-topic-conventions.md)
**Topic-Naming-Patterns**
- Topic-Struktur (`<type>/<version>/<namespace>/<sender>/<receiver>/<action>`)
- Sender/Receiver-Semantik
- Beispiele & Regeln

### 5. [**CCU-Backend Orchestration**](ccu-backend-orchestration.md)
**Order-Management & Workflow**
- Order-Request → UUID-Generation → FTS-Order
- Complete Order-Flow Sequenz-Diagramm
- Published Topics des CCU-Backends
- Code-Referenzen & Implementierung

### 6. [**MQTT Message Examples**](mqtt-message-examples.md) ⭐
**Verifizierte Message-Formate für Module Control**
- Konkrete JSON-Beispiele für alle Module
- PICK, DROP, STORE, CHECK_QUALITY Commands
- Sequential Command Patterns
- Message Format Requirements

---

## 🔗 Verwandte Dokumentation

### **Detaillierte Komponenten-Dokumentation:**
- [APS-CCU](../APS-CCU/README.md) - CCU Docker-Container Details
- [APS-NodeRED](../APS-NodeRED/README.md) - NodeRed Flows & OPC-UA Bridge
- [TXT-Controller](../TXT-DPS/README.md) - TXT-DPS, TXT-AIQS, TXT-FTS

### **Architektur & System-Kontext:**
- [Architektur-Übersicht](../../02-architecture/README.md) – OSF-Systemkontext
- [APS Data Flow](../../02-architecture/aps-data-flow.md) – Datenverarbeitung & Kommunikation

---

## 📖 Wie diese Dokumentation nutzen

### **Für Komplett-Übersicht:**
→ [Component Overview](component-overview.md) - **START HIER!** 🌟

### **Für schnelle Referenz:**
→ [Module Serial Mapping](module-serial-mapping.md)

### **Für System-Verständnis:**
1. [Component Overview](component-overview.md) - Was gibt es? (Alle 10 Komponenten)
2. [Hardware-Architektur](hardware-architecture.md) - Was ist wo? (Netzwerk, IPs)
3. [MQTT-Topic-Conventions](mqtt-topic-conventions.md) - Wie kommunizieren sie?
4. [MQTT Message Examples](mqtt-message-examples.md) - Welche Messages werden gesendet?
5. [CCU-Backend Orchestration](ccu-backend-orchestration.md) - Wie funktioniert Order-Management?

### **Für Implementierung:**
→ [CCU-Backend Orchestration](ccu-backend-orchestration.md) - Code-Referenzen & Flows  
→ [MQTT Message Examples](mqtt-message-examples.md) - Message-Formate & Beispiele  
→ [Component Overview](component-overview.md) - Komponenten-Matrix

---

## ⚠️ Wichtige Hinweise

### **Verifizierte Informationen:**
Alle Informationen in dieser Sektion sind **verifiziert** durch:
- ✅ Session-Daten (MQTT-Traffic)
- ✅ Source-Code (CCU-Backend JavaScript)
- ✅ NodeRed-Flows (flows.json)
- ✅ Hardware-Tests

### **Nicht verifiziert:**
- ⚠️ Cloud-Integration (fischertechnik-cloud.com)
- ⚠️ Interne CCU-Backend Datenstrukturen
- ⚠️ TXT-Controller interne Logik

---

**Erstellt:** 2025-10-08  
**Aktualisiert:** 2025-02 – Verweis auf offizielle Fischertechnik-Dokumentation  
**Status:** ORBIS-spezifische APS-Referenz – ergänzt offizielle Fischertechnik-Docs

