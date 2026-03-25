# Analyse: Serial / SerialNumber / SerialId – Begriffs-Konsistenz

**Datum:** 2026-03  
**Kontext:** Zweite AGV-Integration, Codebase-Review  
**Ziel:** Einheitliche Bezeichnung für Geräte-Identifikatoren (5iO4, IeJ4, SVR4H73275, etc.)

---

## 1. Fischertechnik-Protokoll (Referenz)

### 1.1 MQTT-Topic-Pfad

Die Fischertechnik-Dokumentation verwendet `<serial>` als Platzhalter im Topic-Pfad:

```
module/v1/ff/<serial>/state
module/v1/ff/<serial>/order
module/v1/ff/<serial>/connection
fts/v1/ff/<serial>/state
fts/v1/ff/<serial>/order
```

- **APS-CCU 11-appendices.md:** `<serial>`
- **agv.md, hbw.md, dps.md, etc.:** `<serial>`
- **mqtt-topic-conventions.md, mqtt-message-examples.md:** teilweise `<serialId>`

→ **Empfehlung Topic-Platzhalter:** `<serial>` (wie Fischertechnik)

### 1.2 MQTT-Payload (JSON)

In allen Fischertechnik-Payloads wird **`serialNumber`** (camelCase) verwendet:

```json
// Connection
{"serialNumber": "MILL001", "connectionState": "ONLINE"}

// State (Module/FTS)
{"serialNumber": "SVR4H76449", "orderId": "...", "actionState": {...}}

// Order/Command
{"timestamp": "...", "serialNumber": "MILL001", "orderId": "...", "action": {...}}
```

- **integrations/APS-CCU/common/protocol/module.ts:** `serialNumber`
- **integrations/APS-CCU/common/protocol/fts.ts:** `serialNumber`
- **integrations/APS-CCU/common/protocol/ccu.ts:** `serialNumber`
- **docs/06-integrations/fischertechnik-official/05-message-structure.md:** explizit `serialNumber`

→ **Referenz:** Im Protokoll ist **`serialNumber`** der Standard.

---

## 2. Aktuelle Verwendung in der Codebase

### 2.1 Übersicht

| Kontext | Verwendeter Begriff | Beispiele |
|---------|---------------------|-----------|
| **MQTT-Payload / CCU-Protokoll** | `serialNumber` | FtsState, ModuleState, ProductionStep, PairingSnapshot, ProductionCommand |
| **Layout (shopfloor_layout.json)** | `serial` | cells[].serial, fts[].serial |
| **Layout-Typen (ShopfloorCellConfig)** | `serial` | `serial?: string` |
| **modules_hardware.json** | `serial_number` | ModuleHardwareConfig.serial_number (snake_case) |
| **ShopfloorMappingService** | `serialId` | ModuleInfo.serialId, getModuleBySerial(serialId) |
| **AgvOption** | `serial` | { serial: '5iO4', label: 'AGV-1' } – für Topic-Bau |
| **ModuleDetailsSidebar** | `serialId` | @Input() serialId |
| **ModuleNameService.getLocationDisplayText** | `serialId` | Rückgabe: { serialId: string \| null } |
| **TransportOverviewStatus** | `id` | id = serial (z.B. "5iO4") |
| **lastModuleSerialNumber** | `serialNumber` | Referenz auf Modul-Serial (Fischertechnik-konform) |
| **Topic-Helfer (agv-tab)** | `serial` | ftsStateTopic(serial), selectedAgvSerial$ |
| **Docs (mqtt-topic-conventions)** | `serialId` | `module/v1/ff/<serialId>/<action>` |

### 2.2 Inkonsistenzen

1. **serial vs serialId vs serialNumber:** Drei verschiedene Bezeichnungen für denselben Wert (z.B. "5iO4").
2. **Layout:** `serial` (kurz) vs. **modules_hardware:** `serial_number` (snake_case) – unterschiedliche JSON-Schemas.
3. **ModuleInfo.serialId:** Semantisch identisch mit `serialNumber`, aber anderer Name.
4. **Topic-Platzhalter in Docs:** `<serial>` vs. `<serialId>`.

---

## 3. Empfehlung: Einheitliche Konvention

### 3.1 Prinzip: Fischertechnik als Referenz

- **Payload-Felder (JSON):** `serialNumber` (camelCase) – wie im Fischertechnik-Protokoll.
- **Topic-Pfad-Platzhalter:** `<serial>` – wie in der Fischertechnik-Doku.

### 3.2 Vorgeschlagene Zuordnung

| Anwendungsfall | Begriff | Begründung |
|----------------|---------|------------|
| **MQTT-Payload, CCU-Order, Entities** | `serialNumber` | Protokoll-Konformität mit Fischertechnik |
| **Topic-Pfad-Segment / URL-artige IDs** | `serial` | Kurz, entspricht `<serial>` im Topic |
| **Layout-Konfiguration (cells, fts)** | `serial` | Wird direkt für Topic-Subscription/Commands verwendet |
| **AgvOption, Topic-Builder** | `serial` | Baut `fts/v1/ff/${serial}/state` |
| **externes Schema (modules_hardware.json)** | `serial_number` | Beibehalten – externes Format (OMF2, snake_case) |
| ** interne API (ModuleInfo, getModuleBySerial)** | `serialNumber` oder `serial` | Siehe Optionen unten |

### 3.3 Optionen für ModuleInfo / interne APIs

**Option A: `serialNumber` überall (Protokoll-Nähe)**  
- ModuleInfo: `serialId` → `serialNumber`
- getModuleBySerial(serialId) → getModuleBySerial(serialNumber)
- ModuleDetailsSidebar: `serialId` → `serialNumber`
- Pro: Ein Begriff für „Geräte-ID“  
- Contra: `serial` bleibt in Layout/AgvOption – bewusste Ausnahme für kurze Pfad-Kontexte

**Option B: `serial` für interne IDs, `serialNumber` nur für Protokoll**  
- ModuleInfo: `serialId` → `serial`
- Klare Trennung: `serial` = kurzer Identifikator, `serialNumber` = Feldname in JSON
- Pro: Kürzer, einheitlich mit Layout  
- Contra: Zwei Begriffe für praktisch dasselbe

**Option C: Beibehaltung + Dokumentation**  
- `serialId` in ModuleInfo/APIs beibehalten  
- Explizit dokumentieren: „serialId enthält den serialNumber-Wert (Geräte-Seriennummer)“  
- Pro: Weniger Refactoring  
- Contra: Drei Begriffe (serial, serialId, serialNumber) weiterhin im Umlauf

### 3.4 Empfehlung

- **Kurzfristig (ohne großes Refactoring):** Option C – Dokumentation klären, keine Umbenennung.
- **Mittelfristig (bei nächster größeren Refactor-Runde):** Option A – `serialId` schrittweise zu `serialNumber` migrieren, damit ein einheitlicher Begriff für „Geräte-Seriennummer“ gilt. `serial` nur dort bewusst beibehalten, wo es um Topic-Pfade oder sehr kurze Kontexte geht (Layout, AgvOption).

---

## 4. Konkrete Zuordnung (Status Quo → Ziel)

| Datei/Kontext | Aktuell | Ziel (Empfehlung) |
|---------------|---------|-------------------|
| shopfloor_layout.json cells, fts | `serial` | `serial` ✓ (bleibt) |
| modules_hardware.json | `serial_number` | `serial_number` ✓ (externes Schema) |
| ModuleInfo, getModuleBySerial | `serialId` | `serialNumber` (langfristig) oder `serialId` (kurzfristig, dokumentiert) |
| AgvOption | `serial` | `serial` ✓ (Topic-Bau) |
| TransportOverviewStatus.id | `id` | `id` ✓ (generischer Key) |
| FtsState, ModuleState, etc. | `serialNumber` | `serialNumber` ✓ |
| ProductionStep | `serialNumber` | `serialNumber` ✓ |
| Topic-Platzhalter in Docs | `<serial>` / `<serialId>` | `<serial>` |

---

## 5. Referenzen

- [Fischertechnik Message Structure](../06-integrations/fischertechnik-official/05-message-structure.md) – `serialNumber`
- [APS-CCU 11-appendices](../../integrations/APS-CCU/docs/11-appendices.md) – Topic `<serial>`, Payload `serialNumber`
- [Module Serial Mapping](../06-integrations/00-REFERENCE/module-serial-mapping.md)
- [second-agv-2026-03.md](second-agv-2026-03.md)

---

## 6. Durchgeführte Änderungen (März 2026)

Die folgenden Anpassungen wurden umgesetzt:

- **ModuleInfo.serialId** → **serialNumber**
- **ShopfloorMappingService:** Methoden-Parameter `serialId` → `serialNumber`
- **ModuleDetailsSidebar:** `@Input() serialId` → `serialNumber`
- **ModuleNameService.getLocationDisplayText:** Rückgabe `serialId` → `serialNumber`
- **SerialToModuleInfo:** `serialId` → `serialNumber`
- **Track-Trace getLocationInfo:** `serialId` → `serialNumber`
- **shopfloor-tab:** `selectedModuleSerialId` → `selectedModuleSerialNumber`, localStorage-Key angepasst
- **WorkpieceHistoryService.getModuleNameFromSerial:** Parameter `serialId` → `serialNumber`
- **Docs:** `<serialId>` → `<serial>` in mqtt-topic-conventions, topic-naming-convention-analysis, shopfloor-mapping-service

---

*Erstellt: März 2026 | Refactoring umgesetzt*
