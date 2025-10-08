# Production Order Manager - Implementation

**Status:** ✅ VOLLSTÄNDIG implementiert  
**Datum:** 2025-10-08  
**Architektur:** MQTT Client → Gateway → Production Order Manager → UI

---

## 🎯 Übersicht

Der **ProductionOrderManager** verwaltet Production Orders und Storage Orders (active, completed) für die CCU-Domain analog zum OrderManager (Inventory).

**Unterscheidung:**
- **PRODUCTION Orders:** HBW → MILL/DRILL → AIQS → DPS (kompletter Workflow)
- **STORAGE Orders:** START → DPS → HBW (nur FTS Transport)

---

## 🏗️ Implementierte Komponenten

### 1. ProductionOrderManager (VOLLSTÄNDIG)
**Datei:** `omf2/ccu/production_order_manager.py`

**Pattern:** Exakt wie OrderManager
- ✅ Singleton Pattern (`get_production_order_manager()`)
- ✅ Non-Blocking Init (kein File I/O)
- ✅ State-Holder (`active_orders`, `completed_orders`) - **Order-ID-basiert (Dict)**
- ✅ Thread-Safety (`threading.Lock()`)
- ✅ MQTT Message Processing
- ✅ **Order-Lifecycle Management** (active → completed)
- ✅ **STORAGE vs PRODUCTION** Unterscheidung
- ✅ **Kompletter Produktionsplan** mit MQTT-Status-Overlay

**API:**
```python
from omf2.ccu.production_order_manager import get_production_order_manager

manager = get_production_order_manager()

# Messages verarbeiten (vom Gateway aufgerufen)
manager.process_active_order_message(topic, message, meta)
manager.process_completed_order_message(topic, message, meta)
manager.process_fts_state_message(topic, message, meta)  # STUB
manager.process_ccu_response_message(topic, message, meta)  # STUB
manager.process_module_state_message(topic, message, meta)  # STUB

# Daten abrufen (von UI aufgerufen)
active_orders = manager.get_active_orders()  # Dict
completed_orders = manager.get_completed_orders()  # Dict
statistics = manager.get_order_statistics()
complete_plan = manager.get_complete_production_plan(order)  # Kompletter Plan
```

### 2. CcuGateway erweitert
**Datei:** `omf2/ccu/ccu_gateway.py`

**Änderungen:**
- ✅ Production Order Topics hinzugefügt (Set-basiert)
- ✅ Lazy Loading für ProductionOrderManager
- ✅ **Zentrale Validierung** über MessageManager (keine doppelte Validierung mehr)
- ✅ Routing implementiert:
  - `ccu/order/active` → `process_active_order_message()`
  - `ccu/order/completed` → `process_completed_order_message()`
  - `ccu/order/response` → `process_ccu_response_message()` (STUB)
  - `fts/v1/ff/5iO4/state` → `process_fts_state_message()` (STUB)
  - `module/v1/ff/<serial>/state` → `process_module_state_message()` (STUB)
  - `ccu/order/request` → Logging only (für später)

### 3. MQTT Client Konfiguration
**Datei:** `omf2/registry/mqtt_clients.yml`

**Subscribed Topics:**
```yaml
ccu_mqtt_client:
  subscribed_topics:
    - "ccu/order/request"
    - "ccu/order/completed"
    - "ccu/order/active"
    - "ccu/order/response"  # CCU Bestätigung für Production Orders
    - "fts/v1/ff/5iO4/state"  # FTS Transport-Updates
    - "module/v1/ff/SVR3QA0022/state"  # HBW Status
    - "module/v1/ff/SVR4H76530/state"  # AIQS Status
    - "module/v1/ff/SVR4H73275/state"  # DPS Status

  business_functions:
    production_order_manager:
      subscribed_topics:
        - "ccu/order/request"
        - "ccu/order/completed"
        - "ccu/order/active"
        - "ccu/order/response"
        - "fts/v1/ff/5iO4/state"
        - "module/v1/ff/SVR3QA0022/state"
        - "module/v1/ff/SVR4H76530/state"
        - "module/v1/ff/SVR4H73275/state"
```

### 4. UI Integration (REFACTORED)
**Dateien:** 
- `omf2/ui/ccu/ccu_orders/ccu_orders_tab.py` (Wrapper mit Tabs)
- `omf2/ui/ccu/ccu_orders/production_orders_subtab.py` (nur PRODUCTION)
- `omf2/ui/ccu/ccu_orders/storage_orders_subtab.py` (nur STORAGE)

**Features:**
- ✅ **Zwei Subtabs:** Production Orders vs Storage Orders
- ✅ **Order Statistics** (Total, Active, Completed, Mode)
- ✅ **Active Orders** (ID, Type, State, OrderType)
- ✅ **Completed Orders** (unterhalb Active, ausgegraut)
- ✅ **Production Steps** (expandable, mit Icons)
- ✅ **STORAGE vs PRODUCTION** unterschiedliche Darstellung
- ✅ **Echte MQTT-Daten** (via ProductionOrderManager)
- ✅ **Order-Lifecycle** (active → completed)

---

## 📊 Payload-Struktur

### Active Order (ccu/order/active)
```json
[
  {
    "orderId": "7590e1ad-d1bc-4d89-9358-65d4c6cff292",
    "orderType": "STORAGE",
    "type": "RED",
    "state": "IN_PROGRESS",
    "workpieceId": "04fa8cca341290",
    "timestamp": "2025-10-01T11:15:43.904Z",
    "receivedAt": "2025-10-01T11:15:44.011Z",
    "startedAt": "2025-10-01T11:15:44.012Z",
    "productionSteps": [
      {
        "id": "3b0f63cf-543e-44d8-ab7a-5b6aaf6d1f0c",
        "type": "NAVIGATION",
        "state": "FINISHED",
        "source": "START",
        "target": "DPS",
        "startedAt": "2025-10-01T11:15:44.038Z",
        "stoppedAt": "2025-10-01T11:15:45.639Z"
      },
      {
        "id": "345fb1ad-37dd-4311-adcb-35d00c27f74f",
        "type": "MANUFACTURE",
        "state": "FINISHED",
        "command": "DROP",
        "moduleType": "DPS",
        "serialNumber": "SVR4H73275",
        "startedAt": "2025-10-01T11:15:45.645Z",
        "stoppedAt": "2025-10-01T11:16:00.211Z",
        "dependentActionId": "3b0f63cf-543e-44d8-ab7a-5b6aaf6d1f0c"
      }
    ]
  }
]
```

**Payload-Typ:** Array oder `null` (wenn keine Orders)

---

## 🧪 Testing

### Unit Tests
**Datei:** `omf2/tests/test_production_order_infrastructure.py`

**Tests:**
1. ✅ Manager Initialisierung
2. ✅ Active Order Message Processing
3. ✅ Completed Order Message Processing
4. ✅ Order Statistics

**Ergebnis:** 4/4 Tests bestanden

### Infrastruktur-Test (mit echten MQTT-Daten)
**Test:**
1. OMF2 App starten
2. System Logs prüfen
3. CCU Orders Tab öffnen

**Ergebnis:**
- ✅ MQTT Client empfängt Messages
- ✅ Gateway routet korrekt
- ✅ Manager verarbeitet Messages
- ✅ UI zeigt Daten an

---

## 🔄 Dataflow

```
MQTT Broker
    ↓
CCU MQTT Client (ccu/order/active)
    ↓
CCU Gateway (_route_ccu_message)
    ↓
Production Order Manager (process_active_order_message)
    ↓
State-Holder (self.active_orders = [...])
    ↓
UI (render_ccu_orders_tab)
    ↓
Streamlit Display
```

---

## 📝 Implementierungsstatus

### ✅ VOLLSTÄNDIG Implementiert
- ✅ **MQTT-Infrastruktur** funktioniert
- ✅ **Messages werden empfangen** und verarbeitet
- ✅ **Order-ID-basierte Zuordnung** (Dict statt Array)
- ✅ **Order-Lifecycle Management** (active → completed)
- ✅ **STORAGE vs PRODUCTION** Unterscheidung
- ✅ **Kompletter Produktionsplan** mit MQTT-Status-Overlay
- ✅ **Completed Orders** werden aus active_orders entfernt
- ✅ **UI mit zwei Subtabs** (Production vs Storage)
- ✅ **Completed Orders Anzeige** (ausgegraut)
- ✅ **Log-Rotation** (max 10MB pro Datei, 5 Backups)
- ✅ **Zentrale Validierung** über MessageManager
- ✅ **Warning-Logging** für doppelte UUIDs

### ⚠️ STUB (noch nicht implementiert)
- ⚠️ FTS State Messages (`process_fts_state_message()`)
- ⚠️ CCU Response Messages (`process_ccu_response_message()`)
- ⚠️ Module State Messages (`process_module_state_message()`)

### 📋 BACKLOG (für später)
- 🔄 Code-Duplikate in ccu_process-tab prüfen
- 🔄 factory_layout Integration in Order View
- 🔄 factory_layout mit omf2-spezifischen Icons
- 🔄 Completed Orders limitieren (z.B. max 10)
- 🔄 Order-Filterung (Type, State)
- 🔄 Order-Sortierung (Timestamp)
- 🔄 Order Actions (Pause, Resume, Cancel) implementieren

---

## 🎯 Wichtige Erkenntnisse

### 1. **STORAGE vs PRODUCTION Orders:**
```
PRODUCTION:
  - Kompletter fester Plan: HBW → MILL/DRILL → AIQS → DPS
  - MQTT-Status wird auf festen Plan überlagert
  - Komplexer Workflow mit 11+ Steps

STORAGE:
  - Einfacher Plan: START → DPS → HBW
  - MQTT-Steps direkt verwendet (kein fester Plan)
  - Nur FTS Transport (4 Steps)
```

### 2. **Order-Lifecycle:**
```
1. ccu/order/active → self.active_orders[orderId] = order
2. ccu/order/completed → self.completed_orders[orderId] = order
3. del self.active_orders[orderId]  # WICHTIG!
```

### 3. **Logging:**
```
- Root Logger + RingBufferHandler (UI)
- Root Logger + RotatingFileHandler (logs/omf2.log)
- Kein Console-Handler (nur kurz bei request_refresh)
```

---

**Letzte Aktualisierung:** 2025-10-08  
**Status:** Production Order Manager VOLLSTÄNDIG implementiert und getestet ✅

