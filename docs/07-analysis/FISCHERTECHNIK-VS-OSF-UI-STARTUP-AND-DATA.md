# Fischertechnik Dashboard vs. OSF-UI: Aktualisierung bei App-Start

**Datum:** 18.02.2026  
**Kontext:** Sprint 16, Architektur-Vergleich Daten-Aktualisierung  
**Quellen:** Fischertechnik-Referenz (`docs/06-integrations/fischertechnik-official/`), OSF-UI Codebase (`osf/`)

---

## 1. Kurzzusammenfassung

| Aspekt | Fischertechnik (Offizielles Frontend) | OSF-UI |
|--------|--------------------------------------|--------|
| **Datenspeicherung** | Nur MQTT-Broker (Retained Messages) | Broker + **Client-Persistenz** (localStorage) + In-Memory |
| **Sofortige Anzeige bei Reload** | Ja, via Broker-Retained beim Subscribe | Ja, via localStorage + MessageMonitor + ggf. Broker-Retained |
| **Betriebsmodi** | Nur Live (MQTT verbunden) | Live, Replay, Mock |
| **Topics für Darstellung** | Identisch (ccu/state/*, module/v1/ff/+/state, …) | Identisch + OSF-Erweiterungen (/j1/txt/1/i/*, dsp/#, osf/#) |
| **Architektur-Pattern** | Einfach: Subscribe → Retained sofort → Anzeige | Zwei Patterns: Tab Stream Pattern 1 & 2 |

---

## 2. Datenspeicherung

### 2.1 Fischertechnik

**Speicherort:** Ausschließlich **MQTT-Broker** (Mosquitto).

- State-Topics (`module/v1/ff/<serial>/state`, `fts/v1/ff/<serial>/state`, `connection`, `factsheet`) werden mit **retained** publiziert.
- CCU-Topics (`ccu/state/stock`, `ccu/state/layout`, `ccu/state/config`, `ccu/state/flows`, `ccu/order/active`, `ccu/order/completed`, `ccu/pairing/state`) sind retained.
- Zitat aus 02-architecture: *"All values displayed in the UI have to be retained to survive a reload"*.

**Keine clientseitige Persistenz.** Das Dashboard speichert keine Daten in localStorage oder IndexedDB.

### 2.2 OSF-UI

**Speicherorte (Mehrschichtig):**

1. **MQTT-Broker** (Live-Modus): Retained Messages wie bei Fischertechnik.
2. **MessageMonitorService (In-Memory)**:
   - Circular Buffer pro Topic (Retention 50–100 je Topic).
   - BehaviorSubject pro Topic für sofortigen Zugriff auf letzte Nachricht.
3. **MessagePersistenceService (localStorage)**:
   - Speichert Message-History für persistierte Topics (max. 5 MB).
   - Ausnahme: Camera (`/j1/txt/1/i/cam`) nicht persistiert.
   - Beim App-Start: `loadPersistedData()` lädt alle gespeicherten Topics in Buffers und BehaviorSubjects.
4. **Replay-Modus**: Session-Log-Dateien (JSONL) statt Broker.
5. **Mock-Modus**: Fixtures (startup, Order-Fixtures) statt Broker.

---

## 3. Wann wird aktualisiert?

### 3.1 Fischertechnik

| Zeitpunkt | Mechanismus |
|-----------|-------------|
| **Browser-Reload** | 1. Verbindung zum Broker, 2. Subscribe auf Topics, 3. Broker liefert sofort alle **retained** Messages → UI zeigt aktuellen Stand |
| **Während Laufzeit** | Event-driven: State nur bei Änderung, kein 30s-Periodic-Refresh |
| **Neuer Tab** | Kein Multi-Tab-Sync, jeder Tab verbindet sich eigenständig und erhält retained |

**Kritisch:** Ohne Retained auf dem Broker zeigt die UI nach Reload nichts, bis die nächste State-Änderung kommt.

### 3.2 OSF-UI

| Zeitpunkt | Mechanismus |
|-----------|-------------|
| **App-Start (vor Verbindung)** | MessageMonitor lädt aus localStorage → Tabs können sofort mit Pattern 2 Daten anzeigen |
| **Nach MQTT-Connect** | ConnectionService: `subscribeToRequiredTopics()` → Broker sendet retained → `startMessageMonitoring()` leitet an MessageMonitor → Gateway-Streams |
| **Tab öffnet später** | Tab Stream Pattern 1/2: `getLastMessage()` oder `shareReplay` stellen letzte Daten bereit |
| **Multi-Tab** | BroadcastChannel synchronisiert MessageMonitor über Tabs |

**Zwei Architektur-Pattern für timing-unabhängige Darstellung:**

- **Pattern 1** (Streams mit `startWith`): `shareReplay({ bufferSize: 1, refCount: false })` – hält letzten Wert auch ohne Subscriber.
- **Pattern 2** (Streams ohne `startWith`): `merge(getLastMessage(topic), dashboardStream$)` – MessageMonitor liefert initialen Wert, Stream liefert Echtzeit-Updates.

---

## 4. Topic-Vergleich

### 4.1 Gemeinsame Topics (Fischertechnik = OSF-UI)

| Topic-Muster | Fischertechnik | OSF-UI | Zweck |
|--------------|----------------|--------|-------|
| `module/v1/ff/+/state` | ✅ retained | ✅ subscribed | Modul-Status |
| `module/v1/ff/+/connection` | ✅ retained | ✅ (in module/v1/#) | Modul Online/Offline |
| `module/v1/ff/+/factsheet` | ✅ retained | ✅ (in module/v1/#) | Modul-Fähigkeiten |
| `fts/v1/ff/+/state` | ✅ retained | ✅ (in fts/v1/#) | AGV-Status |
| `fts/v1/ff/+/connection` | ✅ retained | ✅ (in fts/v1/#) | AGV Online/Offline |
| `ccu/state/stock` | ✅ retained | ✅ | Lagerbestand |
| `ccu/state/layout` | ✅ retained | ✅ (in ccu/state/* implizit) | Layout |
| `ccu/state/config` | ✅ retained | ✅ | Konfiguration |
| `ccu/state/flows` | ✅ retained | ✅ | Produktionsabläufe |
| `ccu/pairing/state` | ✅ retained | ✅ | Modul-Pairing |
| `ccu/order/active` | ✅ retained | ✅ (in ccu/order/#) | Aktive Aufträge |
| `ccu/order/completed` | ✅ retained | ✅ (in ccu/order/#) | Abgeschlossene Aufträge |

### 4.2 OSF-Erweiterungen (nur OSF-UI)

| Topic | Zweck |
|-------|-------|
| `dsp/#` | DSP-Aktionen, Korrelation |
| `osf/#` | Arduino, Sensoren etc. |
| `/j1/txt/1/i/bme680` | BME680-Sensor |
| `/j1/txt/1/i/ldr` | LDR-Sensor |
| `/j1/txt/1/i/cam` | Kamera-Frames |
| `/j1/txt/1/i/quality_check` | AIQS-Qualitätsbilder |

---

## 5. Architektur-Unterschiede im Detail

### 5.1 Fischertechnik: Ein Mechanismus

```
[Browser Reload] → [MQTT Connect] → [Subscribe Topics] → [Broker sendet retained] → [UI zeigt Daten]
```

- Einzige Voraussetzung: Broker muss retained Messages für alle UI-relevanten Topics halten.
- Kein Fallback bei Broker-Ausfall oder fehlendem Retain.

### 5.2 OSF-UI: Drei Betriebsmodi + Client-Persistenz

```
[App Start]
    ├── MessageMonitor.loadPersistedData() → localStorage → Buffer + BehaviorSubject
    ├── ConnectionService.connect() (Live) oder Mock/Replay
    │       ├── subscribeToRequiredTopics()
    │       ├── startMessageMonitoring() → addMessage() → Buffer + Persist + Broadcast
    │       └── Broker retained → sofortige Nachrichten
    └── Tabs: Pattern 1 (shareReplay) oder Pattern 2 (getLastMessage + merge)
```

**Vorteile OSF-UI:**

1. **Timing-unabhängig:** Tab kann vor oder nach der ersten Nachricht geöffnet werden.
2. **Offline-fähig (Replay):** Session-Logs ohne Broker nutzbar.
3. **localStorage-Fallback:** Auch nach Reload ohne sofortige Verbindung zeigen sich zuletzt persistierte Daten.
4. **Multi-Tab:** BroadcastChannel hält MessageMonitor über Tabs synchron.

**Trade-off:** Höhere Komplexität (MessageMonitor, Persistence, Tab Stream Patterns).

---

## 6. Ablauf bei App-Start im Browser

### 6.1 Fischertechnik

1. Angular-App lädt.
2. MQTT-Client verbindet sich mit Broker.
3. Subscribe auf Topics (z. B. `ccu/state/stock`, `ccu/order/active`, `module/v1/ff/+/state`, …).
4. Broker liefert **sofort** retained Messages für alle passenden Subscriptions.
5. UI rendert mit diesen Daten.

**Latenz:** Verbindungszeit + Subscribe-Zeit (typisch < 1 s).

### 6.2 OSF-UI (Live-Modus)

1. Angular-App lädt.
2. **MessageMonitor.**`loadPersistedData()` lädt aus localStorage → sofortige Anzeige alter Daten in Pattern-2-Tabs.
3. **ConnectionService** verbindet mit MQTT.
4. Nach Connect: `startMessageMonitoring()` + `subscribeToRequiredTopics()`.
5. Broker sendet retained → Messages landen in MessageMonitor und Gateway.
6. Tabs erhalten Updates über merge/getLastMessage und Gateway-Streams.

**Latenz:**

- Mit localStorage: Sofort (ggf. veraltete Daten).
- Ohne localStorage: Bis Broker retained liefert (wie Fischertechnik).

---

## 7. Empfehlungen / Erkenntnisse

1. **Topics:** OSF-UI nutzt dieselben Topics wie Fischertechnik für die Kernfunktionen. Keine Änderung nötig.
2. **Retained:** OSF-UI profitiert von retained genauso wie Fischertechnik. Bei Live-Modus ist Retained weiterhin wichtig.
3. **OSF-spezifisch:** Client-Persistenz und Tab Stream Pattern sind zusätzliche Sicherheitslagen, die Fischertechnik nicht hat.
4. **Replay/Mock:** Ermöglichen Entwicklung und Demo ohne physische Modellfabrik.

---

## 8. Referenzen

- [Fischertechnik 02-architecture](../06-integrations/fischertechnik-official/02-architecture.md)
- [Fischertechnik 03-ui-integration](../06-integrations/fischertechnik-official/03-ui-integration.md)
- [Fischertechnik 05-message-structure](../06-integrations/fischertechnik-official/05-message-structure.md)
- [Tab Stream Initialization Pattern](../03-decision-records/11-tab-stream-initialization-pattern.md)
- [OSF Services README](../../osf/apps/osf-ui/src/app/services/README.md)
- [AS-IS Fischertechnik Comparison](./AS-IS-FISCHERTECHNIK-COMPARISON.md)
