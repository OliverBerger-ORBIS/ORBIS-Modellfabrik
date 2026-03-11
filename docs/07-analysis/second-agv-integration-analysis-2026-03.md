# Zweites FTS/AGV Integration – Analyse

**Sprint:** 17  
**Task:** Zweites FTS/AGV mit Serial-ID jp93  
**Referenz:** [sprint_17.md](../sprints/sprint_17.md) – LogiMAT Vorbereitung  
**Dokumentation:** [Fischertechnik Agile Production Simulation – Add-On AGV](https://www.fischertechnik.de/en/industry-and-universities/technical-documents/simulate/agile-production-simulation#update-blog) (Download: Documentation_APS_AddOn_AGV_EN-09-2024 en.pdf)

---

## 1. Übersicht

Es soll ein zweites AGV (Serial-ID **jp93**) in OSF eingebunden werden. Aktuell ist ein AGV mit Serial **5iO4** im Einsatz. Die Analyse umfasst alle relevanten Schichten: TXT-FTS, CCU, Gateway/Business, osf-ui (inkl. **AGV/FTS-Tab**), Shopfloor-Layout, Fixtures.

---

## 2. Architektur-Zusammenfassung

Die meisten Komponenten sind **bereits für mehrere AGVs ausgelegt**:

| Komponente | Mehrere FTS? | Kurzbefund |
|------------|-------------|------------|
| **CCU (FtsPairingStates)** | ✅ | `knownModules`-Map pro `serialNumber` |
| **FactoryLayoutService** | ✅ | Node-Blocking pro FTS-Serial (`FactoryNodeBlocker.ftsSerialNumber`) |
| **NavigatorService** | ✅ | Path pro `serialNumber` |
| **MQTT-Topics** | ✅ | `fts/v1/ff/<serial>/state`, `/order`, `/connection`, `/factsheet` |
| **TXT-FTS** | ✅ | Serial aus `/etc/deviceid` – jede Instanz nutzt eigene Topics |
| **Gateway fts$** | ✅ | Filtert `fts/v1` – empfängt alle Serials |
| **Business ftsStates$** | ✅ | `Record<string, FtsState>` – Key `ftsId` oder `serialNumber` |
| **AGV/FTS-Tab** | ❌ | Nur Topic `fts/v1/ff/5iO4/state` – hardcoded |
| **Shopfloor-Tab** | ⚠️ | Fallback `5iO4` im Registry; FTS-Position aus `ftsEntries[0]` |
| **WorkpieceHistoryService** | ❌ | Nur `fts/v1/ff/5iO4/state` – zweites AGV **nicht** in Track & Trace |
| **shopfloor_layout.json** | ⚠️ | Ein Eintrag in `fts`-Array |

---

## 3. Fischertechnik Add-On AGV – Betriebsanleitung (Kerninhalte)

*Quelle: fischertechnik „APS Add On: Automated Guided Vehicle – Operating instructions“ (Version 1, 09/2024)*

### 3.1 Umfang / Kontext

- Das **AGV Add-On** erweitert die APS um den werkstücktransport zwischen Modulen.
- **Batteriebetrieben** (im Gegensatz zu den Modulen).
- Lieferumfang: 1× AGV, 3× leere Werkstückträger.
- **Drei Lagerplätze** auf dem AGV (analog Hochregallager).

### 3.2 Strom / Batterie / Laden

- Batterie bei Lieferung geladen – AGV kann direkt gestartet werden.
- **Manuelles Laden** (wenn Batterie zu niedrig zum Starten):
  - APS-Ladestation oder 9V-Ladegerät.
  - **Wichtig:** APS darf **nicht** im Betrieb sein während manuellem Laden.
  - Voraussetzungen: Ladegerät an Ladestation + Netz, 24V-Versorgung der Ladestation, TXT 4.0 auf AGV aus, AGV manuell in Ladestation platzieren.
  - LED-Anzeigen: Rot blinkend = lädt, konstant = Charge voll.

### 3.3 Netzwerk / Steuerung

- **Raspberry Pi** + **APS-Router** im Wareneingang/-ausgangsmodul → stellt APS-Netz bereit.
- **AGV TXT 4.0 an APS-WLAN anbinden:**
  1. TXT 4.0 einschalten, AGV-Programm ggf. stoppen.
  2. Einstellungen → Netzwerk → WLAN.
  3. Mit APS-Router-WLAN verbinden (SSID + Passwort auf Wareneingangsmodul).
  4. Programm **`fts_main`** auf TXT 4.0 starten.
- **APS-Web-UI:** http://192.168.0.100 → Module → alle sechs Module + AGV sichtbar, **Connected**-Spalte prüfen.
- Bei Verbindungsproblemen: **Reset**-Button in der UI nutzen.

### 3.4 Inbetriebnahme (pro AGV)

- **Position:** AGV vor Wareneingang/-ausgang, Kamera Richtung Modul.
- **Richtiges AGV wählen:** AGV-ID auf TXT-Display muss mit AGV-ID im APS-Dashboard übereinstimmen (z.B. `kD33`).
- **Nach Restart/Reset:** Jedes AGV muss erneut **„Dock to DPS“** ausführen. Schritt immer für alle AGVs erforderlich.
- **Ladestation freigeben:** „Finish charging“ klicken, damit das nächste AGV andocken kann.

### 3.5 Mehrere AGVs – APS-Konfiguration

- **Konfiguration → Number of workpieces that can be produced in parallel:**
  - Standard: **2**
  - **Zwei AGVs:** auf **4** setzen
  - **Mehr als 2 AGVs:** entsprechend in Zweierschritten erhöhen
- Änderung mit **Save** im Dashboard speichern.

### 3.6 Checkliste (Repo-relevant)

- TXT 4.0 mit APS-WLAN verbunden (SSID/Passwort auf Wareneingangsmodul).
- AGV führt Programm **`fts_main`** aus.
- Nach APS-Restart/Reset: jedes AGV erneut **„Dock to DPS“**.
- Mehr-AGV: Ladestation freigeben („Finish charging“), bevor das nächste AGV andockt.
- Bei zwei AGVs: parallele Werkstücke von **2 → 4** setzen.

---

## 4. AGV/FTS-Tab – Detailanalyse

Der **AGV-Tab** (`osf/apps/osf-ui/src/app/tabs/agv-tab.component.ts`) ist aktuell komplett auf ein einzelnes FTS ausgerichtet.

### 4.1 Hardcodierte Referenzen

| Zeile | Konstante/Verwendung | Aktueller Wert |
|-------|----------------------|----------------|
| 66–69 | `FTS_SERIAL`, `FTS_STATE_TOPIC`, `FTS_ORDER_TOPIC`, `FTS_INSTANT_ACTION_TOPIC` | `5iO4` |
| 365 | `getLastMessage(FTS_STATE_TOPIC)` | Nur `fts/v1/ff/5iO4/state` |
| 384 | `getLastMessage(FTS_ORDER_TOPIC)` | Nur `fts/v1/ff/5iO4/order` |
| 689–690 | `sendCharge(FTS_SERIAL)` | Commands an 5iO4 |
| 693 | `dockFts(FTS_SERIAL, DOCK_NODE_DPS)` |  |
| 710 | `buildOrderToIntersection2()` – payload.serialNumber |  |
| 723 | `publish(FTS_INSTANT_ACTION_TOPIC, …)` |  |
| 821 | `publish(FTS_ORDER_TOPIC, payload)` |  |
| 625–672 | Beispiel-Payloads (chargeExamplePayload, dockExamplePayload, …) | Alle mit `FTS_SERIAL` |

### 4.2 Datenfluss

- **MessageMonitorService** mit fixem Topic `fts/v1/ff/5iO4/state` → `ftsState$`
- Einzelnes FTS: Status, Battery, Loads, Position, Route, Actions
- Commands (Charge, Dock, Drive) gehen ausschließlich an dieses FTS

### 4.3 Anpassungen für zweites AGV (jp93)

**Option A – FTS-Auswahl per Dropdown**

- FTS-Auswahl (z.B. 5iO4, jp93)
- Streams dynamisch: `fts/v1/ff/${selectedSerial}/state` und `/order`
- Commands an `selectedSerial`

**Option B – Mehrere FTS-Kacheln**

- Liste aller FTS aus `ftsStates$` oder `ccu/pairing/state` (transports)
- Pro FTS eine Kachel mit Status, Battery, Loads, Position
- Command-Buttons pro FTS (Serial als Parameter)

**Option C – Erstes verfügbares FTS (Quick-Win)**

- Topics mit Wildcard-Strategie oder dynamische Serial-Liste aus Layout/Config
- Tab zeigt das „erste“ FTS (z.B. alphabetisch oder Reihenfolge in Config)
- Commands weiterhin an ausgewähltes FTS

#### Anwendungsfall & Migrationspfad

- **Primärer Use-Case:** Ein FTS aktiv; das zweite ersetzt FTS-1 beim Laden. Kein paralleler Betrieb.
- **Perspektive:** Paralleler Betrieb prinzipiell möglich – Architektur unterstützt es.
- **Zeitlich:** Machbar.

**Empfehlung – Migrationspfad:**

1. **Phase A (zuerst):** Option A – FTS-Auswahl per Dropdown. Reicht für Ersatz-Betrieb, geringerer Aufwand.
2. **Phase B (wenn noch Zeit):** Option B – Mehrere FTS-Kacheln. Ermöglicht parallelen Betrieb mit Übersicht aller AGVs.

Dieser Pfad deckt den aktuellen Bedarf ab und lässt die Erweiterung zu B offen.

---

## 5. Betroffene Komponenten – Übersicht

### 5.1 Hardware / TXT-FTS

| Schritt | Aktion |
|---------|--------|
| 1 | Zweiten TXT mit FTS-Software aus `integrations/TXT-FTS/` provisionieren |
| 2 | `/etc/deviceid` auf dem neuen TXT = **jp93** (AGV-ID = Serial in MQTT/dashboard) |
| 3 | Programm **`fts_main`** auf TXT starten; TXT an APS-WLAN anbinden |
| 4 | Nach Restart/Reset: **„Dock to DPS“** pro AGV ausführen (OSF/AGV-Tab oder APS-UI) |

### 5.2 osf-ui – Anpassungsstellen

| Datei | Änderung |
|-------|----------|
| **agv-tab.component.ts** | FTS-Serial dynamisch (Auswahl oder Liste); Topics/Commands pro Serial |
| **shopfloor-tab.component.ts** | Zeile 384: Fallback von `5iO4` zu dynamischer FTS-Liste (Layout oder `ftsStates$`) |
| **workpiece-history.service.ts** | §5.5: FTS-State-Subscription auf beide Serials; FTS-Check dynamisch |
| **shopfloor_layout.json** | `fts`-Array um zweites FTS erweitern (serial_number: jp93) |

### 5.3 CCU / Backend

- FTS werden über Factsheet/Connection dynamisch erkannt.
- **Mehr-AGV-Betrieb:** `maxParallelOrders` in `general-config.json` bzw. APS-UI erhöhen: 2 AGVs → **4** (siehe §3.5).

### 5.4 Fixtures & Tests

- Fixtures mit `jp93`-Topics erweitern (z.B. `fts/v1/ff/jp93/state`)
- Unit-/E2E-Tests für Mehr-FTS-Szenarien

### 5.5 Track & Trace – Auswirkungen (WorkpieceHistoryService)

Der **WorkpieceHistoryService** baut die Werkstück-Historie für Track & Trace aus FTS-State- und Modul-State-Nachrichten. Mit nur einem abonnierten FTS-Topic fehlen alle Events von Werkstücken, die auf dem zweiten AGV transportiert werden.

#### Kritische Stellen

| Zeile | Problem | Auswirkung |
|-------|---------|------------|
| **223** | `getLastMessage('fts/v1/ff/5iO4/state')` – nur 5iO4 | Werkstücke auf **jp93** erscheinen **nicht** in Track & Trace |
| **241** | `getLastMessage('ccu/order/fts')` – TURN-Richtung | Falls CCU pro FTS `fts/v1/ff/<serial>/order` verwendet: beide Order-Streams abonnieren oder aggregieren |
| **407** | `moduleSerialId = … \|\| '5iO4'` | Fallback unnötig, wenn beide Serials geliefert werden |
| **455–458** | `serialId === '5iO4'` für FTS-Namen | Muss **jp93** (und weitere Serials) als FTS erkennen |

#### Erforderliche Änderungen

1. **FTS-State-Subscription erweitern**
   - Statt eines Topics: `merge(ftsState5iO4$, ftsStateJp93$)` bzw. dynamische Liste aus Layout/Config
   - Jeder FTS-State wird separat in `updateWorkpieceHistory` verarbeitet – die Logik unterstützt mehrere Serials bereits (per `state.serialNumber` / `_moduleSerialId`)

2. **getModuleNameFromSerial**
   - `serialId === '5iO4'` ersetzen durch Prüfung gegen bekannte FTS-Serials (Layout, `ftsStates$` oder Konfiguration)
   - Alternativ: `serialId.toLowerCase().includes('fts')` beibehalten, oder Serial-Liste `['5iO4','jp93']` aus Config

3. **FTS-Order-Stream für TURN-Richtung**
   - Wenn TURN-Richtungen aus Orders kommen: beide `fts/v1/ff/5iO4/order` und `fts/v1/ff/jp93/order` abonnieren, oder prüfen ob `ccu/order/fts` alle FTS-Orders aggregiert
   - `turnDirectionByActionId` ist global – actionIds sind eindeutig, daher kein Konflikt bei mehreren AGVs

4. **Modul-Event-Zuordnung (DOCK)**
   - Zeile 609–614: Suche nach DOCK-Events mit `e.moduleName === 'FTS'`
   - Mit zwei AGVs: Beide liefern DOCK-Events. Matching über `orderId` + `orderUpdateId` – pro Auftrag ist nur ein AGV zuständig, daher kein Konflikt

#### Ergebnis ohne Anpassung

- Werkstücke, die ausschließlich auf **jp93** transportiert werden, erscheinen **nicht** in Track & Trace
- Bei parallelem Betrieb mit zwei AGVs ist die Historie unvollständig

---

## 6. Business/Gateway – ftsStates$

- **Gateway** `fts$`: filtert `matchTopic(msg.topic, 'fts/v1')` → alle `fts/v1/ff/<serial>/state` werden empfangen
- **Business** `ftsStates$`: `scan` mit Key `fts.ftsId ?? 'unknown'`
- **Hinweis:** MQTT-State hat `serialNumber`, Entities-FtsState erwartet `ftsId`. Gateway muss `serialNumber` → `ftsId` mappen oder Payload beide Felder liefern, sonst landet zweites FTS unter Key `'unknown'`.

---

## 7. Implementierungsplan

### 7.1 Randbedingungen

- **Kein Live-Modus-Test:** Validierung nur über Mock/Replay und Unit-Tests.
- **Fixtures:** FTS-1 (5iO4) Topics liegen vor. FTS-2 (jp93) Topics sind strukturell identisch – Simulation durch duplizierte Fixtures mit Serial-ID jp93.
- **Schrittweise Umsetzung** mit Tests pro Schritt.

### 7.2 Namensgebung (Anzeige)

- **Serial-ID:** 5iO4, jp93 (technische Identifikation).
- **Logischer Name (Anzeige):** **AGV-1**, **AGV-2** – nicht FTS-1/FTS-2, nicht Serial-ID.
- **Referenz:** [MARKETING_CONSISTENCY_PLAN.md](MARKETING_CONSISTENCY_PLAN.md) – DE: „FTS (AGV)“, EN: „AGV“; für die konkrete Fahrzeugbezeichnung einheitlich AGV-1/AGV-2.

Mapping: `5iO4` → AGV-1, `jp93` → AGV-2.

### 7.3 Implementierungsschritte (Reihenfolge)

| Schritt | Aufgabe | Test |
|---------|---------|------|
| **1** | **AGV-Config/Layout erweitern** – `shopfloor_layout.json`: FTS-Array um `serial_number` ergänzen; erstes FTS: `serial_number: "5iO4"`, `label: "AGV-1"`; zweites: `serial_number: "jp93"`, `label: "AGV-2"` | Layout laden, beide Einträge mit Mapping |
| **2** | **WorkpieceHistoryService** – beide Topics abonnieren (`merge(fts5iO4$, ftsJp93$)`), `getModuleNameFromSerial` dynamisch (Serials aus Layout/Config) | Unit-Test: Events von beiden Serials erzeugen |
| **3** | **Fixtures jp93** – z.B. `storage_blue` um jp93-Variante erweitern oder neues Fixture „storage_blue_agv2“ (5iO4 → jp93 ersetzen in Kopie) | Replay: Track & Trace zeigt Werkstücke von jp93 |
| **4** | **AGV-Tab Phase A** – FTS-Auswahl-Dropdown: AGV-1 (5iO4), AGV-2 (jp93); Topics/Commands dynamisch nach Auswahl | Unit-Test: Dropdown-Wechsel; Fixture mit beiden AGVs |
| **5** | **Shopfloor-Tab** – Fallback von `5iO4` auf dynamische FTS-Liste (aus Layout); Transport-Rows zeigen AGV-1/AGV-2 statt FTS | Unit-Test: beide Serials im Registry |
| **5b** | **Orders/Steps** – Bei NAVIGATION-Steps: FTS → AGV (generisch) bzw. AGV-1/AGV-2 wenn `serialNumber` im Step vorhanden (CCU fügt dies evtl. bei In-Progress/Completed hinzu) | Order-Card mit optionalem serialNumber |
| **6** | **I18n** – Keys für AGV-1, AGV-2 falls nötig | Lint/Extract |

### 7.4 Test-Strategie

- **Unit-Tests:** WorkpieceHistoryService (multi-AGV-Subscription), agv-tab (Dropdown, Command-Target), shopfloor-tab.
- **Fixtures:** storage_blue + jp93-Variante; Order-Fixtures mit beiden FTS-Topics.
- **Replay:** Session mit 5iO4 + jp93 Messages (falls Replay-Tool die Topics filtert: beide einbinden).

### 7.5 jp93-Fixture (storage_blue_agv2)

AGV-2 (jp93) Fixture vorhanden: `storage_blue_agv2` – Kopie von storage_blue mit 5iO4→jp93 in Topics und Payload. AGV-Tab bietet es als „Storage Blue (AGV-2)“ an.

### 7.6 Fixture „storage_blue_parallel“ (Option A)

Beide AGVs (5iO4 und jp93) in derselben Session für Replay-Tests von Track-Trace und WorkpieceHistory. Merge aus `storage_blue` (5iO4 mit Storage-Order 3adc738c) und jp93-Messages (RED-Order c9da720e, Werkstück 04d78cca341290). Erreichbar im Track & Trace- und AGV-Tab als „Storage Blue (Both AGVs)“.

### 7.7 Orders/Steps: AGV-Anzeige (Schritt 5b)

- **Vor dem Zuweisen:** Wir wissen noch nicht, ob AGV-1 oder AGV-2 den NAVIGATION-Step übernimmt – Anzeige: **AGV** (generisch).
- **Nach Zuweisung/Completion:** Wenn die CCU `serialNumber` im ProductionStep ergänzt (wie bei MANUFACTURE-Steps), zeigt die Order-Card **AGV-1** oder **AGV-2**.
- **Implementierung:** `ProductionStep` hat optionales `serialNumber`. Order-Card nutzt `ShopfloorMappingService.getAgvLabel(step.serialNumber)` und fällt auf AGV zurück, wenn kein Serial/Label verfügbar ist.
- **CCU-Erweiterung:** Falls die CCU `serialNumber` bei NAVIGATION-Steps noch nicht setzt, kann diese Erweiterung später nachgezogen werden – die UI ist vorbereitet.

---

## 8. Referenzen

- [agv.md](../06-integrations/fischertechnik-official/06-modules/agv.md) – AGV-Modul-Doku
- [TXT-FTS README](../06-integrations/TXT-FTS/README.md)
- [13-track-trace-architecture.md](../03-decision-records/13-track-trace-architecture.md) – Track & Trace Architektur
- [sprint_17.md](../sprints/sprint_17.md)
- [MARKETING_CONSISTENCY_PLAN.md](MARKETING_CONSISTENCY_PLAN.md) – FTS/AGV Namensgebung

---

*Erstellt: März 2026 | Implementierungsplan ergänzt*
