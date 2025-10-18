# 🚀 Production Order Manager - Quick Reference

**Für:** Production Order Manager Implementation  
**Datum:** 2025-10-08  
**Status:** Bereit für Implementierung

---

## ⚡ TL;DR - Die wichtigsten Fakten

### 1. **Erste OrderID erscheint bei:**
- **Topic:** `fts/v1/ff/5iO4/order`
- **Message #:** ~95-134 (nach Session-Start)
- **Format:** UUID (z.B. `598cba14-5cb5-43e7-b8cc-530d87d2cfa3`)

### 2. **Order-Trigger:**
- **Topic:** `ccu/order/request`
- **Payload:** `{"type":"BLUE|RED|WHITE", "orderType":"PRODUCTION"}`
- **Subscriber:** CCU-Backend

### 3. **UUID-Generator:**
- **Komponente:** CCU-Backend (Raspberry Pi Docker)
- **Code:** `integrations/APS-CCU/.../modules/order/index.js` Zeile 128
- **Funktion:** `uuid.v4()`

### 4. **Order-Response:**
- **Topic:** `ccu/order/response`
- **Payload:** `{"orderId":"<uuid>", "productionSteps":[...], "state":"ENQUEUED"}`

### 5. **Typische Order hat:**
- **94-120 Messages** mit gleicher OrderID
- **>10 Messages** = "Echte" Order
- **2-7 Messages** = Alte/Rest-OrderIDs (ignorieren)

---

## 📋 Order-Flow (Komplett)

```
1. ccu/order/request → {"type":"BLUE","orderType":"PRODUCTION"}
         ↓
2. CCU-Backend empfängt (modules/order/index.js)
         ↓
3. CCU-Backend: orderId = uuid.v4()
         ↓
4. CCU-Backend → ccu/order/response → {"orderId":"<uuid>", "productionSteps":[...]}
         ↓
5. CCU-Backend → fts/v1/ff/5iO4/order → {"orderId":"<uuid>", "nodes":[...]}
         ↓
6. FTS fährt, Module arbeiten
         ↓
7. CCU-Backend → ccu/order/active (Update)
         ↓
8. CCU-Backend → ccu/order/completed (Completion)
```

---

## 🔑 Wichtige Topics

### CCU-Topics (vom CCU-Backend published):
```
ccu/order/request      ← Trigger (von Frontend)
ccu/order/response     ← Bestätigung (von CCU-Backend)
ccu/order/active       ← Aktive Orders (Array, retain)
ccu/order/completed    ← Abgeschlossene Orders (Array, retain)
```

### FTS-Topics:
```
fts/v1/ff/5iO4/order   ← CCU-Backend sendet Navigation (QoS 2)
fts/v1/ff/5iO4/state   ← FTS sendet Status-Updates
```

### Module-Topics:
```
module/v1/ff/<serial>/order            ← Orders an Module
module/v1/ff/<serial>/state            ← RAW State vom Modul
module/v1/ff/NodeRed/<serial>/state    ← ENRICHED State (mit orderId)
```

---

## 🎯 UUID-Validierung

```python
import re

def is_valid_order_id(order_id: str) -> bool:
    """Nur UUIDs sind gültig (Test-IDs wie '1001' nicht!)"""
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, order_id, re.IGNORECASE))
```

---

## 📊 Topic-Verteilung (Typische Order)

| Topic-Pattern | Messages | Zweck |
|---------------|----------|-------|
| `fts/v1/ff/5iO4/state` | 56-72 | FTS Transport-Status |
| `module/.../state` | 6 pro Modul | Modul-Bearbeitung |
| `fts/v1/ff/5iO4/order` | 4-5 | FTS Orders |
| `module/.../order` | 3 pro Modul | Modul Orders |
| `ccu/order/response` | 1 | CCU Bestätigung |

---

## 🔍 Module-Mapping (Quick)

| Serial | Typ | TXT | OPC-UA |
|--------|-----|-----|--------|
| SVR4H73275 | DPS | ✅ | ✅ |
| SVR4H76530 | AIQS | ✅ | ✅ |
| 5iO4 | FTS | ✅ | ❌ |
| SVR3QA0022 | HBW | ❌ | ✅ |
| SVR4H76449 | DRILL | ❌ | ✅ |
| SVR3QA2098 | MILL | ❌ | ✅ |

---

## 📁 Wichtige Referenz-Dokumente

### 1. Zentrale Referenz:
→ `docs/06-integrations/00-REFERENCE/`

### 2. Session-Analyse:
→ `docs/07-analysis/production-order-analysis-results.md`

### 3. CCU-Backend Details:
→ `docs/06-integrations/00-REFERENCE/ccu-backend-orchestration.md`

### 4. Test-Daten:
```
data/omf-data/sessions/auftrag-blau_1.db (120 msgs, OrderID: 598cba14-...)
data/omf-data/sessions/auftrag-rot_1.db (94 msgs, OrderID: 8ae07a6e-...)
data/omf-data/sessions/auftrag-weiss_1.db (100 msgs, OrderID: 258beef9-...)
```

### 5. Analyse-Script:
→ `omf/analysis_tools/find_first_order_topic.py`

---

## 💡 Implementierungs-Tipps

### Order-Detection:
```python
# 1. Subscribe zu relevanten Topics
topics = [
    "ccu/order/request",
    "ccu/order/response", 
    "ccu/order/active",
    "fts/v1/ff/+/order",
    "fts/v1/ff/+/state",
    "module/v1/ff/+/state",
    "module/v1/ff/NodeRed/+/state"
]

# 2. OrderID aus Message extrahieren
def extract_order_id(payload):
    if 'orderId' in payload and is_valid_order_id(payload['orderId']):
        return payload['orderId']
    return None

# 3. Messages nach OrderID gruppieren
order_sequences = defaultdict(list)
for msg in messages:
    order_id = extract_order_id(msg['payload'])
    if order_id:
        order_sequences[order_id].append(msg)

# 4. Nur signifikante Orders (>10 Messages)
significant_orders = {
    oid: msgs for oid, msgs in order_sequences.items() 
    if len(msgs) > 10
}
```

### State-Tracking:
```python
# Order-Lifecycle
PENDING → ENQUEUED → IN_PROGRESS → COMPLETED
                           ↓
                        ERROR/CANCELLED
```

---

## 🔗 Vollständige Dokumentation

**Detaillierte Analysen:**
- [Production Order Analysis](production-order-analysis-results.md) - Komplett
- [CCU-Backend Orchestration](../06-integrations/00-REFERENCE/ccu-backend-orchestration.md) - Code
- [MQTT Topic Conventions](../06-integrations/00-REFERENCE/mqtt-topic-conventions.md) - Patterns

**Module-Details:**
- [Module Serial Mapping](../06-integrations/00-REFERENCE/module-serial-mapping.md) - Hardware
- [Hardware Architecture](../06-integrations/00-REFERENCE/hardware-architecture.md) - Netzwerk

---

**Bereit für Production Order Manager Implementation! 🚀**







