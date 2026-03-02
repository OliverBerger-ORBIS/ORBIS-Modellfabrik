# 🏷️ Topic-Naming-Convention - Analyse der Future Factory

**Quellen:** Empirische Analyse (Session *.log, NodeRed Flows). QoS- und Retained-Strategie mit Fischertechnik-Doku abgeglichen.  
**Datum:** 2025-10-08

## 🔑 Trennung: Fischertechnik (v1/ff) vs. ORBIS-Erweiterungen

| Segment | Bedeutung |
|---------|-----------|
| **v1** | Version der Fischertechnik-Topic-Struktur |
| **ff** | **Future Factory** – Fischertechnik APS |

**Fischertechnik-Bereich** (`module/v1/ff/...`, `fts/v1/ff/...`, `/j1/txt/...`): Sensoren wie BME680 (`/j1/txt/1/i/bme680`), Cam (`/j1/txt/1/i/cam`) sind Teil des APS.

**ORBIS-Erweiterungen** (ohne v1/ff): z.B. `dsp/drill/action`, `osf/arduino/vibration/...` – Erweiterungen außerhalb der Fischertechnik-Standard-Topics. **Regel:** Erweiterungen an bestehenden Modulen (z.B. quality_check) nutzen Fischertechnik-Topics; neue ORBIS-Objekte (Sensoren, Arduino) nutzen `osf/`-Namensraum. Siehe [DR-18 OSF-Erweiterungen](../../03-decision-records/18-osf-extensions-ip-and-mqtt-topics.md).

---

## 🎯 Module-Kategorien

### Module OHNE TXT-Controller (kein MQTT)
Diese Module können **nicht selbst** MQTT-Messages senden:
- **MILL** (SVR3QA2098)
- **DRILL** (SVR4H76449)
- **HBW** (SVR3QA0022)

➡️ **NodeRed** übernimmt die MQTT-Kommunikation via OPC-UA

### Module MIT TXT-Controller (mit MQTT)
Diese Module haben einen **Webserver** und können aktiv senden/empfangen:
- **DPS** (SVR4H73275) ✅
- **AIQS** (SVR4H76530) ✅
- **FTS** (5iO4) ✅

➡️ Module senden **selbst** MQTT-Messages

## 🏷️ Topic-Naming-Pattern

### Pattern 1: Module MIT NodeRed-Vermittlung
```
module/v1/ff/NodeRed/<serialId>/<action>
  ↑     ↑   ↑     ↑        ↑         ↑
 Type  Vers NS  Sender  Receiver  Action
```

**Beispiele:**
- `module/v1/ff/NodeRed/SVR4H73275/state` - NodeRed published State für DPS
- `module/v1/ff/NodeRed/SVR4H76530/state` - NodeRed published State für AIQS

**Warum?**
- NodeRed enriched/transformiert OPC-UA Daten
- NodeRed fügt Metadaten hinzu (orderId, timestamps, etc.)
- NodeRed managed VDA-5050 Workflow

### Pattern 2: Module OHNE NodeRed (Direkt)
```
module/v1/ff/<serialId>/<action>
  ↑     ↑   ↑      ↑         ↑
 Type  Vers NS  Receiver  Action
```

**Beispiele:**
- `module/v1/ff/SVR3QA0022/state` - HBW Module (via NodeRed, OHNE TXT)
- `module/v1/ff/SVR3QA2098/state` - MILL Module (via NodeRed, OHNE TXT)
- `module/v1/ff/SVR4H76449/state` - DRILL Module (via NodeRed, OHNE TXT)

**ABER AUCH:**
- `module/v1/ff/SVR4H73275/state` - DPS sendet SELBST (MIT TXT)
- `module/v1/ff/SVR4H76530/state` - AIQS sendet SELBST (MIT TXT)

**Warum?**
- Module OHNE TXT: NodeRed übersetzt OPC-UA → MQTT
- Module MIT TXT: TXT-Controller sendet direkt via MQTT

### Pattern 3: FTS Topics
```
fts/v1/ff/<serialId>/<action>
 ↑   ↑   ↑      ↑         ↑
Type Vers NS  Receiver  Action
```

**Beispiele:**
- `fts/v1/ff/5iO4/order` - CCU-Backend sendet Order an FTS
- `fts/v1/ff/5iO4/state` - FTS sendet State (selbst, hat TXT)

**Publisher:**
- `order` → CCU-Backend
- `state`, `connection`, `factsheet` → FTS selbst

### Pattern 4: CCU Topics
```
ccu/<category>/<action>
```

**Beispiele:**
- `ccu/order/request` - Order-Anforderung (von wem auch immer)
- `ccu/order/response` - CCU-Backend bestätigt Order
- `ccu/order/active` - CCU-Backend veröffentlicht aktive Orders
- `ccu/pairing/state` - CCU-Backend zeigt gepaarte Module

**Publisher:** CCU-Backend (externe Software)

### Pattern 5: OSF Arduino Topics
```
osf/arduino/<sensorTyp>/<deviceId>/<action>
  ↑     ↑         ↑            ↑         ↑
 NS  Plattform  Sensor-Typ  Device-ID   Action
```

**Beispiele:**
- `osf/arduino/vibration/sw420-1/state` – SW-420 Vibrationssensor Status
- `osf/arduino/vibration/sw420-1/connection` – LWT, Online-Status
- `osf/arduino/vibration/mpu6050-1/state` – MPU-6050 (geplant)

**Regel:** Neue ORBIS-Sensoren/Arduinos → `osf/arduino/...`. Details: [DR-18 OSF-Erweiterungen](../../03-decision-records/18-osf-extensions-ip-and-mqtt-topics.md).

### Pattern 6: TXT Topics (Fischertechnik)
```
/j1/txt/1/f/i/<category>  - Input (vom TXT)
/j1/txt/1/f/o/<category>  - Output (zum TXT)
```

**Beispiele:**
- `/j1/txt/1/f/o/order` - TXT-UI sendet Order-Anfrage
- `/j1/txt/1/f/i/stock` - TXT empfängt Stock-Status
- `/j1/txt/1/i/cam` - TXT Kamera-Stream

**Publisher:** TXT-Controller (DPS Modul)

## 🔍 Doppelte Topics erklärt

### DPS (SVR4H73275) - erscheint DOPPELT:
```
module/v1/ff/NodeRed/SVR4H73275/state  ← NodeRed enriched
module/v1/ff/SVR4H73275/state          ← DPS TXT-Controller direkt
```

### AIQS (SVR4H76530) - erscheint DOPPELT:
```
module/v1/ff/NodeRed/SVR4H76530/state  ← NodeRed enriched
module/v1/ff/SVR4H76530/state          ← AIQS TXT-Controller direkt
```

**Erklärung:**
1. DPS/AIQS TXT-Controller sendet **RAW-State** via MQTT
2. NodeRed empfängt via OPC-UA, enriched mit OrderID/Workflow
3. NodeRed published **ENRICHED-State** mit `NodeRed` im Topic

## 📊 Topic-Struktur-Interpretation

### Interpretation: Sender im Topic-Namen

```
<type> / <version> / <namespace> / <sender> / <receiver> / <action>
```

**Beispiele:**

| Topic | Type | Version | Namespace | Sender | Receiver | Action |
|-------|------|---------|-----------|--------|----------|--------|
| `module/v1/ff/NodeRed/SVR4H73275/state` | module | v1 | ff | **NodeRed** | SVR4H73275 | state |
| `module/v1/ff/SVR3QA0022/state` | module | v1 | ff | **(implizit: NodeRed)** | SVR3QA0022 | state |
| `module/v1/ff/SVR4H73275/state` | module | v1 | ff | **(implizit: TXT)** | SVR4H73275 | state |
| `fts/v1/ff/5iO4/order` | fts | v1 | ff | **(implizit: CCU-Backend)** | 5iO4 | order |
| `fts/v1/ff/5iO4/state` | fts | v1 | ff | **(implizit: FTS-TXT)** | 5iO4 | state |

**Regel:**
- **MIT "NodeRed":** NodeRed hat diese Message enriched/transformiert
- **OHNE "NodeRed":** 
  - Module MIT TXT: TXT-Controller sendet direkt
  - Module OHNE TXT: NodeRed sendet (NodeRed implizit)
  - FTS: FTS-TXT sendet direkt
  - CCU: CCU-Backend sendet

## 🎯 Module-Übersicht

| Serial | Typ | TXT-Controller | MQTT-Fähig | Topics |
|--------|-----|----------------|------------|--------|
| SVR3QA2098 | MILL | ❌ | ❌ | `module/v1/ff/SVR3QA2098/*` (via NodeRed) |
| SVR4H76449 | DRILL | ❌ | ❌ | `module/v1/ff/SVR4H76449/*` (via NodeRed) |
| SVR3QA0022 | HBW | ❌ | ❌ | `module/v1/ff/SVR3QA0022/*` (via NodeRed) |
| SVR4H73275 | DPS | ✅ | ✅ | `module/v1/ff/SVR4H73275/*` (direkt) + `module/v1/ff/NodeRed/SVR4H73275/*` (enriched) |
| SVR4H76530 | AIQS | ✅ | ✅ | `module/v1/ff/SVR4H76530/*` (direkt) + `module/v1/ff/NodeRed/SVR4H76530/*` (enriched) |
| 5iO4 | FTS | ✅ | ✅ | `fts/v1/ff/5iO4/*` (direkt) |

## 💡 Wichtige Erkenntnisse

### 1. **NodeRed = OPC-UA → MQTT Bridge**
Für Module OHNE TXT-Controller:
```
Modul (OPC-UA) → NodeRed → MQTT (module/v1/ff/<serial>/*)
```

### 2. **NodeRed = State-Enrichment**
Für Module MIT TXT-Controller:
```
Modul-TXT → MQTT (module/v1/ff/<serial>/*)        [RAW]
Modul-OPC-UA → NodeRed → MQTT (module/v1/ff/NodeRed/<serial>/*) [ENRICHED]
```

### 3. **CCU-Backend = Workflow-Orchestrator**
```
CCU-Backend subscribes: ccu/order/request
CCU-Backend generates: UUID
CCU-Backend publishes: fts/v1/ff/5iO4/order
```

## 🚀 Production Order Manager - Konsequenzen

### Order-Trigger-Chain (KORRIGIERT):

```
1. [Optional] TXT-UI → /j1/txt/1/f/o/order → {"type":"BLUE"}
                           ↓
2. CCU-Backend empfängt (subscribe /j1/txt/1/f/o/order?)
                           ↓
3. CCU-Backend publishes → ccu/order/request (Event-Notification)
                           ↓ (gleicher Prozess, interner Event)
4. CCU-Backend generiert UUID
                           ↓
5. CCU-Backend publishes → fts/v1/ff/5iO4/order → {"orderId":"<uuid>"}
```

**ODER (wahrscheinlicher):**

CCU-Backend macht alles intern:
```
CCU-Backend empfängt: ccu/order/request (von extern)
              ↓
CCU-Backend generiert UUID
              ↓
CCU-Backend publishes: fts/v1/ff/5iO4/order
```

### Test-Erkenntnis:
- ✅ Order funktioniert **nur** mit `ccu/order/request`
- ❓ `/j1/txt/1/f/o/order` ist optional (UI-Anzeige?)
- ✅ `ccu/order/request` ist der **eigentliche Trigger**

---

---

## 📌 QoS- und Retained-Strategie

**Quelle:** Fischertechnik-Referenz (02-architecture, 05-message-structure)  
**Zweck:** UI-Persistenz, reduzierte Last, konsistente Nutzung

### QoS-Werte

| Nachrichtentyp | QoS | Begründung |
|----------------|-----|------------|
| Commands (Order, Instant Actions) | 2 | Zuverlässige Übermittlung, mindestens einmal |
| State, Connection, Factsheet | 1 | Bestätigung, Retained unterstützt |
| Events (optional) | 0 | Fire-and-forget bei hoher Frequenz |

### Retained Messages

| Topic-Typ | Retain | Begründung |
|-----------|--------|------------|
| `*/connection` | Yes | Letzter Status bei Broker-Reconnect sofort verfügbar |
| `*/state` | Yes | UI-Persistenz, „Reduces MQTT traffic by ~95%“ (nur bei Änderung) |
| `*/factsheet` | Yes | Modul-Metadaten beim Start laden |
| Commands | No | Keine Persistenz nötig |

### State-Message-Verhalten

- State **nur bei Änderung** (event-driven), kein periodischer 30s-Refresh
- Retained für UI-Persistenz nach Reconnect

---

**Status:** Bereit für Production Order Manager mit korrekter Topic-Interpretation 🚀
