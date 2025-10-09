# 📋 REGISTRY-TOPIC-STRUKTUR FÜR registry/topics/xyz.yml

**Datum:** 2025-10-09  
**Status:** ✅ Vollständige Topic-Schema-Korrelation + Semantische Felder  
**Gesamt:** 99 Topics in 5 Domains  
**Update:** Neue semantische Felder für OMF2-Guidance (2025-10-09)

---

## 🆕 NEUE SEMANTISCHE FELDER (2025-10-09)

### **Zweck:**
Ergänzende Felder in Topic-Definitionen für bessere Entwicklungs-Unterstützung und Architektur-Verständnis.

### **Neue Felder:**

#### **1. observed_publisher_aps** (String)
- **Bedeutung:** Welche APS-Komponente publiziert dieses Topic in der echten Anlage
- **Beispiel:** `"APS-Dashboard Frontend (MQTT-Browser)"`, `"CCU-Backend (Order Module)"`
- **Verwendung:** Verständnis der APS "as-IS" Architektur

#### **2. observed_subscriber_aps** (String)
- **Bedeutung:** Welche APS-Komponente(n) subscribieren dieses Topic
- **Beispiel:** `"CCU-Backend (Pairing Module), Dashboards"`
- **Verwendung:** Verständnis der Datenflüsse im APS-System

#### **3. semantic_role** (String)
- **Bedeutung:** Semantische Rolle des Topics im System
- **Beispiele:** 
  - `order_trigger_primary` - Primärer Auslöser für Orders
  - `connection_status_direct` - Direkte Connection-Status-Meldung
  - `module_state_enriched` - Mit orderId angereicherter State
- **Verwendung:** Schnelles Verständnis der Topic-Bedeutung

#### **4. triggers** (String oder null)
- **Bedeutung:** Welchen Workflow/Prozess triggert dieses Topic
- **Beispiele:** `production_order_workflow`, `fts_navigation`, `module_production`
- **Verwendung:** Workflow-Analyse und Event-Tracking

#### **5. omf2_usage** (String)
- **Bedeutung:** Empfohlene Verwendung in OMF2-Komponenten
- **Beispiel:** `"ProductionOrderManager → subscribe to detect new orders (PRIMARY trigger, REQUIRED)"`
- **Verwendung:** Entwicklungs-Guidance für OMF2-Agent

#### **6. omf2_note** (String, optional)
- **Bedeutung:** Wichtige Hinweise für OMF2-Entwicklung
- **Beispiel:** `"This is the REQUIRED trigger - /j1/txt/1/f/o/order is optional alternative"`
- **Verwendung:** Architektur-Entscheidungen und Warnungen

#### **7. verified** (Boolean)
- **Bedeutung:** Wurde diese Information durch Session-Analyse oder Code-Review verifiziert?
- **Werte:** `true` (verifiziert), `false` (spekulativ)
- **Verwendung:** Vertrauenswürdigkeit der Information

#### **8. data_source** (String)
- **Bedeutung:** Quelle der Verifikation
- **Beispiel:** `"Session orderBlueLocal - 2 messages, Code: modules/order/index.js"`
- **Verwendung:** Nachvollziehbarkeit der Analyse

#### **9. analysis_note** (String, optional)
- **Bedeutung:** Zusätzliche Analyse-Erkenntnisse
- **Beispiel:** `"Identical timestamp with /j1/txt/1/f/o/order - Frontend sends both (Fan-Out)"`
- **Verwendung:** Wichtige Zusammenhänge dokumentieren

### **Beispiel: Vollständige Topic-Definition**

```yaml
- topic: ccu/order/request
  qos: 2
  retain: 0
  schema: ccu_order_request.schema.json
  description: "Production Order Request - PRIMARY trigger for order workflow"
  
  # APS as-IS Observation:
  observed_publisher_aps: "APS-Dashboard Frontend (MQTT-Browser)"
  observed_subscriber_aps: "CCU-Backend (Order Module - handleMessage)"
  
  # OMF2 Guidance (manual configuration):
  semantic_role: order_trigger_primary
  triggers: production_order_workflow
  omf2_usage: "ProductionOrderManager → subscribe to detect new orders (PRIMARY trigger, REQUIRED)"
  omf2_note: "This is the REQUIRED trigger - /j1/txt/1/f/o/order is optional alternative"
  
  # Verification:
  verified: true
  data_source: "Session orderBlueLocal_orderRedCloud - 2 messages (BLUE, RED), Code: modules/order/index.js"
  analysis_note: "Identical timestamp with /j1/txt/1/f/o/order - Frontend sends both (Fan-Out)"
```

---

## 🎯 EMPFOHLENE REGISTRY-DATEI-STRUKTUR

### 📁 registry/topics/fts_topics.yml (4 Topics)
```yaml
# FTS Domain Topics
topics:
  - topic: fts/v1/ff/5iO4/connection
    schema: Fts_V1_Ff_Serial_Connection Schema
  - topic: fts/v1/ff/5iO4/factsheet
    schema: Fts_V1_Ff_Serial_Factsheet Schema
  - topic: fts/v1/ff/5iO4/order
    schema: Fts_V1_Ff_Serial_Order Schema
  - topic: fts/v1/ff/5iO4/state
    schema: Fts_V1_Ff_Serial_State Schema
```

### 📁 registry/topics/module_topics.yml (29 Topics)
```yaml
# Module Domain Topics
topics:
  # CHRG0 Module (Wildcard Schema)
  - topic: module/v1/ff/CHRG0/connection
    schema: Wildcard Schema
  - topic: module/v1/ff/CHRG0/factsheet
    schema: Wildcard Schema
  - topic: module/v1/ff/CHRG0/order
    schema: Wildcard Schema
  - topic: module/v1/ff/CHRG0/state
    schema: Wildcard Schema

  # SVR3QA0022 Module (Specific Schemas)
  - topic: module/v1/ff/SVR3QA0022/connection
    schema: Module_V1_Ff_Serial_Connection Schema
  - topic: module/v1/ff/SVR3QA0022/factsheet
    schema: Module_V1_Ff_Serial_Factsheet Schema
  - topic: module/v1/ff/SVR3QA0022/instantAction
    schema: Module_V1_Ff_Serial_Instantaction Schema
  - topic: module/v1/ff/SVR3QA0022/order
    schema: Module_V1_Ff_Serial_Order Schema
  - topic: module/v1/ff/SVR3QA0022/state
    schema: Module_V1_Ff_Serial_State Schema

  # SVR3QA2098 Module (Specific Schemas)
  - topic: module/v1/ff/SVR3QA2098/connection
    schema: Module_V1_Ff_Serial_Connection Schema
  - topic: module/v1/ff/SVR3QA2098/factsheet
    schema: Module_V1_Ff_Serial_Factsheet Schema
  - topic: module/v1/ff/SVR3QA2098/instantAction
    schema: Module_V1_Ff_Serial_Instantaction Schema
  - topic: module/v1/ff/SVR3QA2098/order
    schema: Module_V1_Ff_Serial_Order Schema
  - topic: module/v1/ff/SVR3QA2098/state
    schema: Module_V1_Ff_Serial_State Schema

  # SVR4H73275 Module (Specific Schemas)
  - topic: module/v1/ff/SVR4H73275/connection
    schema: Module_V1_Ff_Serial_Connection Schema
  - topic: module/v1/ff/SVR4H73275/factsheet
    schema: Module_V1_Ff_Serial_Factsheet Schema
  - topic: module/v1/ff/SVR4H73275/instantAction
    schema: Module_V1_Ff_Serial_Instantaction Schema
  - topic: module/v1/ff/SVR4H73275/order
    schema: Module_V1_Ff_Serial_Order Schema
  - topic: module/v1/ff/SVR4H73275/state
    schema: Module_V1_Ff_Serial_State Schema

  # SVR4H76449 Module (Specific Schemas)
  - topic: module/v1/ff/SVR4H76449/connection
    schema: Module_V1_Ff_Serial_Connection Schema
  - topic: module/v1/ff/SVR4H76449/factsheet
    schema: Module_V1_Ff_Serial_Factsheet Schema
  - topic: module/v1/ff/SVR4H76449/instantAction
    schema: Module_V1_Ff_Serial_Instantaction Schema
  - topic: module/v1/ff/SVR4H76449/order
    schema: Module_V1_Ff_Serial_Order Schema
  - topic: module/v1/ff/SVR4H76449/state
    schema: Module_V1_Ff_Serial_State Schema

  # SVR4H76530 Module (Specific Schemas)
  - topic: module/v1/ff/SVR4H76530/connection
    schema: Module_V1_Ff_Serial_Connection Schema
  - topic: module/v1/ff/SVR4H76530/factsheet
    schema: Module_V1_Ff_Serial_Factsheet Schema
  - topic: module/v1/ff/SVR4H76530/instantAction
    schema: Module_V1_Ff_Serial_Instantaction Schema
  - topic: module/v1/ff/SVR4H76530/order
    schema: Module_V1_Ff_Serial_Order Schema
  - topic: module/v1/ff/SVR4H76530/state
    schema: Module_V1_Ff_Serial_State Schema
```

### 📁 registry/topics/ccu_topics.yml (30 Topics)
```yaml
# CCU Domain Topics
topics:
  # Control Topics (Wildcard Schema)
  - topic: ccu/control
    schema: Wildcard Schema
  - topic: ccu/control/command
    schema: Wildcard Schema
  - topic: ccu/control/order
    schema: Wildcard Schema
  - topic: ccu/global
    schema: Wildcard Schema

  # Order Topics (Specific Schemas)
  - topic: ccu/order/active
    schema: Ccu_Order_Active Schema
  - topic: ccu/order/completed
    schema: Ccu_Order_Completed Schema
  - topic: ccu/order/request
    schema: Ccu_Order_Request Schema

  # Pairing Topics (Specific Schemas)
  - topic: ccu/pairing/state
    schema: Ccu_Pairing_State Schema

  # Set Topics (Mixed Schemas)
  - topic: ccu/set/calibration
    schema: Ccu_Set_Calibration Schema
  - topic: ccu/set/charge
    schema: Ccu_Set_Charge Schema
  - topic: ccu/set/config
    schema: Wildcard Schema
  - topic: ccu/set/default_layout
    schema: Wildcard Schema
  - topic: ccu/set/delete-module
    schema: Wildcard Schema
  - topic: ccu/set/flows
    schema: Wildcard Schema
  - topic: ccu/set/layout
    schema: Wildcard Schema
  - topic: ccu/set/module-duration
    schema: Wildcard Schema
  - topic: ccu/set/park
    schema: Wildcard Schema
  - topic: ccu/set/reset
    schema: Ccu_Set_Reset Schema

  # State Topics (Mixed Schemas)
  - topic: ccu/state
    schema: Wildcard Schema
  - topic: ccu/state/config
    schema: Ccu_State_Config Schema
  - topic: ccu/state/error
    schema: Wildcard Schema
  - topic: ccu/state/flow
    schema: Wildcard Schema
  - topic: ccu/state/flows
    schema: Ccu_State_Flows Schema
  - topic: ccu/state/layout
    schema: Ccu_State_Layout Schema
  - topic: ccu/state/status
    schema: Wildcard Schema
  - topic: ccu/state/stock
    schema: Ccu_State_Stock Schema
  - topic: ccu/state/version-mismatch
    schema: Ccu_State_Version-Mismatch Schema

  # Status Topics (Wildcard Schema)
  - topic: ccu/status
    schema: Wildcard Schema
  - topic: ccu/status/connection
    schema: Wildcard Schema
  - topic: ccu/status/health
    schema: Wildcard Schema
```

### 📁 registry/topics/nodered_topics.yml (19 Topics)
```yaml
# NodeRed Domain Topics
topics:
  # CHRG0 NodeRed (Specific Schemas)
  - topic: module/v1/ff/NodeRed/CHRG0/connection
    schema: Module_V1_Ff_Serial_Connection Schema
  - topic: module/v1/ff/NodeRed/CHRG0/factsheet
    schema: Module_V1_Ff_Serial_Factsheet Schema
  - topic: module/v1/ff/NodeRed/CHRG0/state
    schema: Module_V1_Ff_Serial_State Schema

  # SVR3QA0022 NodeRed (Specific Schemas)
  - topic: module/v1/ff/NodeRed/SVR3QA0022/connection
    schema: Module_V1_Ff_Serial_Connection Schema
  - topic: module/v1/ff/NodeRed/SVR3QA0022/factsheet
    schema: Module_V1_Ff_Serial_Factsheet Schema
  - topic: module/v1/ff/NodeRed/SVR3QA0022/state
    schema: Module_V1_Ff_Serial_State Schema

  # SVR3QA2098 NodeRed (Specific Schemas)
  - topic: module/v1/ff/NodeRed/SVR3QA2098/connection
    schema: Module_V1_Ff_Serial_Connection Schema
  - topic: module/v1/ff/NodeRed/SVR3QA2098/factsheet
    schema: Module_V1_Ff_Serial_Factsheet Schema
  - topic: module/v1/ff/NodeRed/SVR3QA2098/state
    schema: Module_V1_Ff_Serial_State Schema

  # SVR4H73275 NodeRed (Specific Schemas)
  - topic: module/v1/ff/NodeRed/SVR4H73275/connection
    schema: Module_V1_Ff_Serial_Connection Schema
  - topic: module/v1/ff/NodeRed/SVR4H73275/factsheet
    schema: Module_V1_Ff_Serial_Factsheet Schema
  - topic: module/v1/ff/NodeRed/SVR4H73275/state
    schema: Module_V1_Ff_Serial_State Schema

  # SVR4H76449 NodeRed (Specific Schemas)
  - topic: module/v1/ff/NodeRed/SVR4H76449/connection
    schema: Module_V1_Ff_Serial_Connection Schema
  - topic: module/v1/ff/NodeRed/SVR4H76449/factsheet
    schema: Module_V1_Ff_Serial_Factsheet Schema
  - topic: module/v1/ff/NodeRed/SVR4H76449/state
    schema: Module_V1_Ff_Serial_State Schema

  # SVR4H76530 NodeRed (Specific Schemas)
  - topic: module/v1/ff/NodeRed/SVR4H76530/connection
    schema: Module_V1_Ff_Serial_Connection Schema
  - topic: module/v1/ff/NodeRed/SVR4H76530/factsheet
    schema: Module_V1_Ff_Serial_Factsheet Schema
  - topic: module/v1/ff/NodeRed/SVR4H76530/state
    schema: Module_V1_Ff_Serial_State Schema

  # NodeRed Status (Wildcard Schema)
  - topic: module/v1/ff/NodeRed/status
    schema: Wildcard Schema
```

### 📁 registry/topics/txt_topics.yml (17 Topics)
```yaml
# TXT Domain Topics
topics:
  # TXT Component Topics (Specific Schemas)
  - topic: /j1/txt/1/c/bme680
    schema: J1_Txt_1_C_Bme680 Schema
  - topic: /j1/txt/1/c/cam
    schema: J1_Txt_1_C_Cam Schema
  - topic: /j1/txt/1/c/ldr
    schema: J1_Txt_1_C_Ldr Schema

  # TXT Factory Input Topics (Mixed Schemas)
  - topic: /j1/txt/1/f/i/config/hbw
    schema: J1_Txt_1_F_I_Config_Hbw Schema
  - topic: /j1/txt/1/f/i/error
    schema: J1_Txt_1_F_I_Order Schema
  - topic: /j1/txt/1/f/i/order
    schema: J1_Txt_1_F_I_Order Schema
  - topic: /j1/txt/1/f/i/status
    schema: J1_Txt_1_F_I_Order Schema
  - topic: /j1/txt/1/f/i/stock
    schema: J1_Txt_1_F_I_Stock Schema

  # TXT Factory Output Topics (Wildcard Schema)
  - topic: /j1/txt/1/f/o/error
    schema: Wildcard Schema
  - topic: /j1/txt/1/f/o/order
    schema: Wildcard Schema
  - topic: /j1/txt/1/f/o/status
    schema: Wildcard Schema
  - topic: /j1/txt/1/f/o/stock
    schema: Wildcard Schema

  # TXT Input Topics (Specific Schemas)
  - topic: /j1/txt/1/i/bme680
    schema: J1_Txt_1_I_Bme680 Schema
  - topic: /j1/txt/1/i/broadcast
    schema: J1_Txt_1_I_Broadcast Schema
  - topic: /j1/txt/1/i/cam
    schema: J1_Txt_1_I_Cam Schema
  - topic: /j1/txt/1/i/ldr
    schema: J1_Txt_1_I_Ldr Schema

  # TXT Output Topics (Wildcard Schema)
  - topic: /j1/txt/1/o/broadcast
    schema: Wildcard Schema
```

---

## 🔧 REGISTRY-KONFIGURATION

### 📁 Datei-Struktur
```
registry/topics/
├── fts_topics.yml      → 4 Topics (FTS Domain)
├── module_topics.yml   → 29 Topics (Module Domain)
├── ccu_topics.yml      → 30 Topics (CCU Domain)
├── nodered_topics.yml  → 19 Topics (NodeRed Domain)
└── txt_topics.yml      → 17 Topics (TXT Domain)
```

### 🎯 Schema-Typen
- **Specific Schemas:** Präzise Schema-Definitionen für spezifische Topics
- **Wildcard Schema:** Generische Schema-Definitionen für flexible Topics

### ✅ Status
- **Alle 99 Topics haben Schema-Korrelation** ✅
- **Registry-Schema-Zuordnung ist vollständig** ✅
- **Domain-basierte Struktur empfohlen** ✅

---

**📝 Dokument erstellt:** 2025-10-05  
**🔄 Letzte Aktualisierung:** 2025-10-09  
**✅ Status:** Vollständige Registry-Struktur + Semantische Felder definiert
