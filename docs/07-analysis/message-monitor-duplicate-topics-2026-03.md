# Analyse: Message Monitor – Topics doppelt (Regression)

**Datum:** 2026-03  
**Kontext:** Sprint 18 – Message Monitor zeigt Topics/Nachrichten doppelt. Blockiert Debugging auf Messe. Verfälschte Daten (z.B. Event-Anzahl für Track & Trace).

**Sprint:** Code-Fix als Task unter [Sprint 18 → Aufgaben → Message Monitor](../sprints/sprint_18.md#aufgaben-thematisch-mit-haken). **OSF-UI Konsole:** [osf-ui-console-debug.md](../04-howto/osf-ui-console-debug.md).

**Constraint (KRITISCH):** Mock-Modus darf den Live-Modus in keiner Weise beeinflussen. Fixes nur in Mock-spezifischem Code (z.B. `if (isMockMode)`-Blöcke).

---

## 1. Symptom

- **Message Monitor:** Anzeige aller Topics doppelt (Regression)
- **Folge:** Verfälschte Daten – z.B. Event-Anzahl für Track & Trace, getMessageCountForModule (Shopfloor)
- **Nicht direkte Blockade**, aber stört Debugging und Datenqualität

---

## 2. Ursachenanalyse

### 2.1 Doppelte addMessage-Aufrufe (Shopfloor-Tab)

**Flow in Mock-Modus:**

1. **Mock-Dashboard** (`setupMessageMonitorForwarding`): Subscribt `messageSubject` und ruft für jede Nachricht `messageMonitor.addMessage()` auf.
2. **Shopfloor-Tab** Fixture-Loader (`loadModuleStatusFixture`, `loadQualityCheckFixture`, etc.):
   - `dashboard.injectMessage(message)` → `messageSubject.next(message)` → löst (1) aus → **addMessage #1**
   - `messageMonitor.addMessage(message)` → **addMessage #2** (direkt)

**Ergebnis:** Dieselbe Nachricht wird zweimal in den MessageMonitor-Buffer geschrieben → Duplikate in der Anzeige.

**Betroffene Stellen (shopfloor-tab.component.ts):**

- `loadModuleStatusFixture`: Zeilen 602, 616
- `loadDrillActionFixture`: Zeile 641
- `loadAiqsActionFixture`: Zeile 662
- `loadModuleActionHistoryFixture`: Zeile 682
- `loadQualityCheckFixture`: Zeile 709

### 2.2 Mögliche Überlappung: Tab-Fixture + Tab-spezifische Fixtures

Beim Laden von „startup“, „blue“ etc. im Shopfloor-Tab:

1. `dashboard.loadTabFixture('module-status-test')` – Haupt-Fixture (orders, modules, stock, …) → `messageSubject`
2. `loadModuleStatusFixture()` – zusätzliche Shopfloor-Status-Fixtures
3. `loadQualityCheckFixture()` – AIQS-Quality-Check-Fixtures

Wenn Haupt-Fixture und Tab-Fixtures dieselben Topics abdecken (z.B. `ccu/pairing/state`), können Nachrichten aus beiden Quellen in den Monitor gelangen. Das ist kein Duplikat derselben Nachricht, aber kann zu verwirrend vielen Einträgen führen.

### 2.3 BroadcastChannel (Multi-Tab)

`MessageMonitorService` nutzt `BroadcastChannel` zur Synchronisation zwischen Tabs. Ein Tab sendet, andere Tabs empfangen und rufen `addToBuffer` auf. Der sendende Tab empfängt seine eigene Nachricht **nicht** (BroadcastChannel-Verhalten). Duplikate durch Broadcast sind daher unwahrscheinlich.

### 2.4 Live/Replay-Modus

- **ConnectionService:** Einzige Quelle – `mqttClient.messages$` → `addMessage` (einmal pro Nachricht).
- **Mock-Dashboard:** Bei `mqttClient` wird `setupMessageMonitorForwarding` nicht aktiv (nur bei `!mqttClient`).

→ In Live/Replay sollte es keine Duplikate durch doppelte addMessage-Aufrufe geben.

---

## 3. Betroffene Consumer

| Consumer | Nutzung | Auswirkung bei Duplikaten |
|----------|---------|---------------------------|
| **Message Monitor Tab** | `getAllMessages()` → `getHistory(topic)` | Doppelte Zeilen in der Tabelle |
| **Shopfloor getMessageCountForModule** | `getHistory(topic)` für Zählung | Erhöhte Event-Anzahl |
| **Track & Trace / WorkpieceHistory** | Indirekt über Streams | Möglicherweise verfälschte Event-Historie |
| **DSP-Action-Tab** | `getHistory(topicPattern)` | Doppelte DSP-Actions |

---

## 4. Lösungsplan

### Option A: Direkte addMessage-Aufrufe in Shopfloor entfernen (empfohlen)

**Prinzip:** Nur eine Quelle für `addMessage` pro Nachricht.

- **Shopfloor-Tab:** In allen Fixture-Loadern die direkten `messageMonitor.addMessage()`-Aufrufe **entfernen**.
- **Beibehalten:** `dashboard.injectMessage(message)` – die Nachricht geht in `messageSubject`, und `setupMessageMonitorForwarding` ruft `addMessage` auf.

**Vorteil:** Einfach, konsistent mit dem bestehenden Mock-Flow.  
**Risiko:** Gering – `injectMessage` ist bereits vorhanden und wird genutzt.

**Live-Modus unberührt:** Alle betroffenen Fixture-Loader sind in `if (!this.isMockMode) { return; }`-Blöcken – sie laufen im Live-Modus gar nicht. Keine Änderung an ConnectionService oder MQTT-Pfad.

### Option B: injectMessage entfernen, nur addMessage

- Shopfloor ruft nur `messageMonitor.addMessage()` auf.
- `injectMessage` wird nicht mehr genutzt (oder nur für Streams, nicht für MessageMonitor).

**Nachteil:** Dashboard-Streams (z.B. `moduleOverview$`) bekommen die Nachricht nicht über `messageSubject`. Die Tab-Fixtures müssten weiterhin über `messageSubject` laufen. Daher weniger geeignet.

### Option C: Deduplizierung im MessageMonitorService

- Vor `addToBuffer`: Prüfen, ob die letzte Nachricht für dasselbe Topic mit gleichem Timestamp bereits existiert.
- Wenn ja: nicht erneut hinzufügen.

**Vorteil:** Robuster gegen mehrere Quellen.  
**Nachteil:** Zusätzliche Logik, mögliche Edge-Cases (z.B. legitime Duplikate mit gleichem Timestamp).

---

## 5. Empfehlung

**Option A umsetzen:** In `shopfloor-tab.component.ts` alle direkten `messageMonitor.addMessage()`-Aufrufe in den Fixture-Loadern entfernen. Nur `injectMessage` beibehalten.

**Zusätzlich prüfen:** Ob `dsp-action-tab` ähnlich doppelt füttert (z.B. wenn Haupt-Fixture und Tab-Fixture beide DSP-Actions liefern). Dort gibt es nur `addMessage`, kein `injectMessage` – Duplikate entstehen nur, wenn dieselbe Nachricht von zwei Stellen kommt.

---

## 6. Implementierungsschritte (Option A)

**Voraussetzung:** Alle Änderungen ausschließlich in Mock-only-Code (z.B. `loadModuleStatusFixture` hat `if (!this.isMockMode) return` – Live-Modus wird nicht ausgeführt).

1. `loadModuleStatusFixture`: `messageMonitor.addMessage` entfernen (Zeilen 602, 616).
2. `loadDrillActionFixture`: `messageMonitor.addMessage` entfernen (Zeile 641).
3. `loadAiqsActionFixture`: `messageMonitor.addMessage` entfernen (Zeile 662).
4. `loadModuleActionHistoryFixture`: `messageMonitor.addMessage` entfernen (Zeile 682).
5. `loadQualityCheckFixture`: `messageMonitor.addMessage` entfernen (Zeile 709).
6. Sicherstellen, dass überall `injectMessage` vorher aufgerufen wird (bereits der Fall).
7. Manuell testen: Mock-Modus, Fixture laden, Message Monitor – keine doppelten Einträge.
8. Unit-Tests anpassen, falls nötig.

**Stand 2026-03-30:** `shopfloor-tab.component.ts` — Fixture-Loader nur `dashboard.injectMessage` (kein zweites `messageMonitor.addMessage`; Regressions-Analyse §2.1 damit abgedeckt). **`dsp-action-tab.component.ts`** — `loadDrillActionFixture` von direktem `messageMonitor.addMessage` auf **`injectMessage`** umgestellt, damit derselbe Mock-Pfad gilt (**messageSubject** → `setupMessageMonitorForwarding` → ein `addMessage`), und optional **Gateway-Streams** die DSP-Messages mitsehen.

---

## 7. Testanleitung (Vorher/Nachher)

### Voraussetzung

- **Mock-Modus:** Umgebung „Mock“ in der Sidebar wählen.
- **Fixtures im Build:** Development (`nx serve`) oder Production mit Fixtures (seit 2026-03).

### Test 1: Nachrichten aus Haupt-Fixture (Order/Process Tab)

1. Umgebung auf **Mock** stellen.
2. Tab **Aufträge** oder **Prozesse** öffnen.
3. Fixture **Startup** oder **Blau** laden (Fixture-Buttons).
4. Tab **Message Monitor** öffnen.

**Erwartung:** Nachrichten zu `ccu/order/active`, `ccu/state/flows`, `ccu/pairing/state` etc. sichtbar.

### Test 2: Nachrichten aus Shopfloor-Fixtures

1. Umgebung **Mock**.
2. Tab **Module** (Shopfloor) öffnen.
3. Fixture **Shopfloor-Status** oder **Startup** laden.
4. Tab **Message Monitor** öffnen.

**Erwartung:** Nachrichten zu `ccu/pairing/state`, `module/v1/ff/...`, `fts/v1/ff/...` sichtbar. **Keine Duplikate** (jede Nachricht nur einmal).

### Test 3: Live-Modus unberührt

1. Umgebung auf **Live** oder **Replay** stellen.
2. MQTT verbinden.
3. Message Monitor prüfen.

**Erwartung:** Nachrichten wie bisher (ConnectionService als einzige Quelle). Keine Änderung.

### Falls gar keine Nachrichten erscheinen

1. **Browser-Console prüfen (F12 → Console):**
   - `[mock-dashboard] Setting up MessageMonitor forwarding for fixture messages` → Weiterleitung aktiv, Nachrichten sollten ankommen.
   - `[mock-dashboard] MessageMonitor forwarding skipped (no messageMonitor passed to controller)` → Controller wurde ohne MessageMonitor erstellt (z.B. Tab vor App-Init). Fix: App-Init stellt Controller immer mit `messageMonitor` her.
   - `[mock-dashboard] MessageMonitor forwarding skipped (mqttClient present, using ConnectionService)` → Controller hat MQTT-Client (Live/Replay), Fixture-Weiterleitung ist deaktiviert. Umgebung prüfen.

2. **Fixture-Dateien:** Bei `nx serve` sind Fixtures in `fixtures/` enthalten. Bei Production-Build auf RPi: Fixtures seit 2026-03 im Build.

3. **Fixture geladen?** Nach Klick auf Fixture-Button sollte sich die Anzeige (Aufträge, Module, etc.) ändern. Bei „Shopfloor Status“: Module/AGV-Overlays im Shopfloor-Preview.

---

## Referenzen

- [MessageMonitorService](../../osf/apps/osf-ui/src/app/services/message-monitor.service.ts)
- [mock-dashboard.ts setupMessageMonitorForwarding](../../osf/apps/osf-ui/src/app/mock-dashboard.ts)
- [shopfloor-tab.component.ts Fixture-Loader](../../osf/apps/osf-ui/src/app/tabs/shopfloor-tab.component.ts)
