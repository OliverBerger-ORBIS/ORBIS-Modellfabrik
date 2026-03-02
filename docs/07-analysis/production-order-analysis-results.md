# 📋 Order Manager - Analyse-Erkenntnisse (vormals Production Order Manager)

**Quelle:** Session-Analyse von auftrag-*.log Sessions  
**Datum:** 2025-10-08  
**Analyse-Tool:** `session_manager/components/order_analyzer.py` (Order Analyzer Tab)

## 🎯 Order-Identifikation

### Gültige OrderIDs
- **Format:** UUID (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
- **Ungültig:** Test-IDs wie `1001`, leere Strings, `0`
- **Validierung:** Regex-Pattern für UUID erforderlich

```python
import re

def is_valid_order_id(order_id: str) -> bool:
    """Validiert OrderID als UUID"""
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, order_id, re.IGNORECASE))
```

### Order-Sequenz-Charakteristik
- **Signifikante Orders:** >10 Messages (typisch: 94-120 Messages)
- **"Alte" OrderIDs:** 2-7 Messages (Reste aus vorherigen Sessions - ignorieren)
- **Primäre Order:** OrderID mit höchster Message-Count

## 🚀 Order-Workflow (typische Sequenz)

### Analysierte Sessions

| Session | Primäre OrderID | Messages | Alte OrderIDs | Erstes Topic |
|---------|-----------------|----------|---------------|--------------|
| auftrag-blau_1 | 598cba14-... | 120 | 3 (7,6,2 msgs) | `fts/v1/ff/5iO4/order` |
| auftrag-rot-omf | 6d6d105d-... | 94 | 0 | `fts/v1/ff/5iO4/order` |
| auftrag-rot_1 | 8ae07a6e-... | 94 | 0 | `fts/v1/ff/5iO4/order` |
| auftrag-weiss_1 | 258beef9-... | 100 | 2 (7,6 msgs) | `fts/v1/ff/5iO4/order` |

### 1. **Order-Start** ⭐
```
Topic: fts/v1/ff/5iO4/order
OrderID: <uuid>
Message #: ~95-134 (nach Session-Start)
```
➡️ **Dies ist IMMER das erste Topic mit einer gültigen OrderID**

### 2. **CCU-Bestätigung**
```
Topic: ccu/order/response
Payload: { orderId, state: "IN_PROGRESS" }
Message #: +3-5 nach Start
```

### 3. **FTS-Transport** (Hauptanteil)
```
Topic: fts/v1/ff/5iO4/state
Messages: 56-72 State-Updates
Payload: { orderId, ... }
```

### 4. **Module-Orders**
```
Topics:
  - module/v1/ff/SVR3QA0022/order
  - module/v1/ff/SVR4H73275/order
  - module/v1/ff/SVR3QA2098/order
  - module/v1/ff/SVR4H76530/order
  - module/v1/ff/SVR4H76449/order
  - module/v1/ff/NodeRed/.../order
Messages: 3-5 pro Modul
```

### 5. **Module-States**
```
Topics: module/.../state
Messages: 6 pro Modul
Payload: { orderId, state, ... }
```

## 📊 Topic-Verteilung (typische Order)

| Topic-Pattern | Messages | Zweck |
|---------------|----------|-------|
| `fts/v1/ff/5iO4/state` | 56-72 | FTS Transport-Status |
| `module/.../state` | 6 pro Modul | Modul-Bearbeitung |
| `fts/v1/ff/5iO4/order` | 4-5 | FTS Orders |
| `module/.../order` | 3 pro Modul | Modul Orders |
| `ccu/order/response` | 1 | CCU Bestätigung |

## 🔑 Payload-Struktur

### Wichtige Felder in Messages
```json
{
  "orderId": "uuid-string",
  "workpieceId": "string",
  "state": "IN_PROGRESS|COMPLETED|...",
  "status": "string",
  "command": "PICK|PLACE|DRILL|...",
  "timestamp": "ISO-8601"
}
```

## 💡 Order Manager - Anforderungen

### Core-Funktionen
1. **Order-Tracking:** Alle Messages einer OrderID sammeln
2. **State-Management:** Order-Status über Lifecycle verfolgen
3. **Topic-Routing:** Messages nach Topic-Pattern zuordnen
4. **Sequence-Detection:** Erste gültige OrderID in Session finden
5. **Multi-Order:** Mehrere parallele Orders unterstützen (Sessions haben 1-4 OrderIDs)

### Lifecycle-States
```
PENDING → IN_PROGRESS → COMPLETED
              ↓
           ERROR/CANCELLED
```

### Erkennungs-Logik (Pseudocode)
```python
# 1. UUID-Validierung
def is_valid_order_id(order_id: str) -> bool:
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, order_id, re.IGNORECASE))

# 2. Sequenz-Analyse
def find_order_sequences(messages) -> Dict[str, List]:
    """
    Gruppiert Messages nach OrderID
    Filtert: Nur UUIDs mit >10 Messages = echte Orders
    Returns: Dict[order_id -> List[messages]]
    """
    order_sequences = defaultdict(list)
    for msg in messages:
        order_id = extract_order_id(msg)
        if is_valid_order_id(order_id):
            order_sequences[order_id].append(msg)

    # Filter: Nur signifikante Orders
    return {oid: msgs for oid, msgs in order_sequences.items() if len(msgs) > 10}

# 3. Erstes Topic finden
def get_first_order_topic(order_id: str, messages: List) -> str:
    """
    IMMER: fts/v1/ff/5iO4/order
    (basierend auf Session-Analyse)
    """
    for msg in messages:
        if msg['orderId'] == order_id:
            return msg['topic']
```

## 📁 Test-Daten

### Sessions verfügbar
- `data/osf-data/sessions/auftrag-blau_1.log` (120 msgs)
- `data/osf-data/sessions/auftrag-rot_1.log` (94 msgs)
- `data/osf-data/sessions/auftrag-weiss_1.log` (100 msgs)
- `data/osf-data/sessions/auftrag-rot-omf_20250915_104029.log` (94 msgs)

### Analyse-Tool
```bash
# Session Manager starten – Order Analyzer Tab nutzen
python -m session_manager

# Analysiert Session-Daten aus data/osf-data/sessions/ (*.log, JSON-Zeilen)
```

## 🎯 Implementierungs-Prioritäten für Order Manager

### Phase 1: Order-Erkennung
1. ✅ **UUID-Validierung** - Filter für gültige OrderIDs
2. ✅ **Order-Sequence-Detection** - Finde alle OrderIDs mit Message-Count
3. ✅ **Primary-Order-Selection** - Höchste Message-Count = Haupt-Order

### Phase 2: Topic-Handling
4. ✅ **Topic-Pattern-Matching** - FTS, Module, CCU Topics zuordnen
5. ✅ **Message-Routing** - Messages nach OrderID gruppieren

### Phase 3: State-Management
6. ✅ **State-Tracking** - Order-Lifecycle verfolgen
7. ✅ **Event-Sequencing** - Chronologische Order-Events

### Phase 4: Integration
8. ✅ **Real-time Updates** - Live MQTT-Integration
9. ✅ **UI-Visualisierung** - Dashboard-Komponenten

## 📝 Wichtige Erkenntnisse

### ✅ Gesicherte Fakten
1. **Erste OrderID erscheint bei:** Message #79-134 (variiert je Session)
2. **Erstes Topic ist IMMER:** `fts/v1/ff/5iO4/order`
3. **Signifikante Orders haben:** >10 Messages (typisch 94-120)
4. **OrderID-Format:** Nur UUIDs sind gültig
5. **Test-IDs werden gefiltert:** z.B. `1001` ist ungültig

### ⚠️ Edge Cases
- **Alte OrderIDs in Session:** 2-7 Messages (ignorieren)
- **Multiple Orders:** Sessions können 1-4 verschiedene OrderIDs enthalten
- **Order-Start-Verzögerung:** Erste Messages (1-78) enthalten oft keine/alte OrderIDs

## 🔗 Verwandte Dokumentation

- **Analyse-Tool:** `session_manager/components/order_analyzer.py`
- **Fischertechnik Order-Protokoll:** `docs/06-integrations/fischertechnik-official/02-architecture.md`
- **Track & Trace:** `docs/03-decision-records/13-track-trace-architecture.md`

---

## 🔍 Order-Trigger-Sequenz (VOR der ersten OrderID)

### ⭐ WICHTIGE ERKENNTNIS: Order-Start-Befehl

**Message #89** (6 Messages VOR der ersten OrderID):
```
Topic: /j1/txt/1/f/o/order
Payload: {"type":"BLUE","ts":"2025-08-19T09:28:37.422Z"}
```

**Message #90** (5 Messages VOR der ersten OrderID):
```
Topic: ccu/order/request
Payload: {"type":"BLUE","timestamp":"2025-08-19T09:28:37.422Z","orderType":"PRODUCTION"}
```

**Message #95** (ERSTE OrderID):
```
Topic: fts/v1/ff/5iO4/order
Payload: {"orderId":"598cba14-5cb5-43e7-b8cc-530d87d2cfa3",...}
```

### Ablauf:

1. **TXT-Controller** sendet Order-Anfrage: `/j1/txt/1/f/o/order` mit `type: "BLUE"`
2. **CCU** empfängt TXT-Request und published: `ccu/order/request` mit `type: "BLUE"` und `orderType: "PRODUCTION"`
3. **CCU-Backend** subscribes `ccu/order/request` und generiert UUID
4. **CCU-Backend** sendet Order an **FTS**: `fts/v1/ff/5iO4/order` mit UUID

### 🎯 Order-Creation-Topics:

| Position | Topic | Publisher | Subscriber | Zweck |
|----------|-------|-----------|------------|-------|
| #89 | `/j1/txt/1/f/o/order` | TXT | CCU | TXT initiiert Order |
| #90 | `ccu/order/request` | CCU | CCU-Backend | CCU broadcast Order-Request |
| #95 | `fts/v1/ff/5iO4/order` | CCU-Backend | FTS | FTS bekommt Order mit UUID |

### 💡 Order Manager Anforderungen:

1. **Order-Request-Detection:**
   - Topic: `/j1/txt/1/f/o/order` oder `ccu/order/request`
   - Payload: `type: "BLUE"|"RED"|"WHITE"`

2. **Order-ID-Generator-Pattern:**
   - Subscribe: `ccu/order/request`
   - Generate: UUID (v4 Format)
   - Publish: `fts/v1/ff/5iO4/order` mit `orderId`

3. **Farb-Mapping:**
   - TXT sendet Farbe → CCU published Request → CCU-Backend generiert UUID → FTS erhält Order
   - Pattern: `ccu/order/request` mit `type` + `orderType` → `fts/v1/ff/5iO4/order` mit `orderId`

---

## 🔍 ANALYSE-UPDATE: Wer generiert die OrderID?

### NodeRed-Flow-Analyse (flows.json vom 2025-09-15):

**Gefunden:**
- ✅ NodeRed (DPS): `send-store-order` published `ccu/order/request` (für STORAGE Orders)
- ❌ **KEIN** NodeRed-Flow subscribes `ccu/order/request`
- ❌ **KEIN** NodeRed-Flow published `fts/v1/ff/5iO4/order`

### ⭐ SCHLUSSFOLGERUNG:

**CCU-Backend** (externe Software auf CCU Raspberry Pi, NICHT NodeRed) ist verantwortlich für:

1. ✅ Subscribe: `ccu/order/request`
2. ✅ UUID-Generierung
3. ✅ Publish: `fts/v1/ff/5iO4/order` mit `orderId`

**Beweis:**
- Topic-Namespace `fts/v1/ff/...` = **Future Factory** (CCU-Backend)
- Wenn NodeRed wäre: `module/v1/ff/NodeRed/...`
- NodeRed Flows enthalten **keine** Subscription auf `ccu/order/request`
- NodeRed Flows enthalten **keine** UUID-Generierung für Production Orders

### TXT-Topic Rolle unklar:

- Message #89: `/j1/txt/1/f/o/order` → {"type":"BLUE"}
- Erscheint VOR `ccu/order/request`
- **ABER:** Order-Auslösung funktioniert auch **nur** mit `ccu/order/request` (ohne TXT-Topic)

**Vermutung:**
- `/j1/txt/1/f/o/order` = UI-Event vom TXT-Controller (optional)
- `ccu/order/request` = Eigentlicher Order-Trigger (erforderlich)

### 🎯 Korrigierter Ablauf:

```
1. [Optional] TXT-UI → /j1/txt/1/f/o/order → {"type":"BLUE"}
                           ↓
2. CCU empfängt (intern) und published → ccu/order/request
                           ↓
3. CCU-Backend subscribes → ccu/order/request
                           ↓
4. CCU-Backend generiert UUID
                           ↓
5. CCU-Backend publishes → fts/v1/ff/5iO4/order → {"orderId":"<uuid>"}
```

**Alternative:**
CCU-Backend macht alles intern (gleicher Prozess):
```
1. TXT-UI → /j1/txt/1/f/o/order → {"type":"BLUE"}
            ↓
2. CCU-Backend empfängt
            ↓
3. CCU-Backend published → ccu/order/request (Event-Notification)
            ↓ (gleicher Prozess, anderer Thread)
4. CCU-Backend generiert UUID
            ↓
5. CCU-Backend published → fts/v1/ff/5iO4/order
```

### ⚠️ OFFENE FRAGEN:

1. **Ist CCU-Backend eine separate Anwendung oder Teil von NodeRed?**
   - Vermutlich: Separate Anwendung
   - Namespace `fts/v1/ff/` deutet darauf hin

2. **Welche Rolle spielt `/j1/txt/1/f/o/order`?**
   - Optional? UI-Trigger?
   - Tests zeigen: `ccu/order/request` reicht alleine aus

3. **Wo läuft CCU-Backend?**
   - Auf CCU Raspberry Pi?
   - Eigene Software-Komponente?

---

**Status:** OSF Order Manager / Track & Trace Implementation basiert auf diesen Erkenntnissen. Referenziert von `docs/03-decision-records/13-track-trace-architecture.md`.
