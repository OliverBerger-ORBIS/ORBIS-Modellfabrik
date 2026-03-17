# Alarm → Fabrik-Stop: CCU-Commands und Gefahrensimulation

**Datum:** 2026-03-10  
**Kontext:** Bei Detektion eines Alarms (z.B. Vibration=RED, Flammensensor) sollen alle Fabrik-Aktionen gestoppt werden. Analyse der verfügbaren CCU-Commands und Empfehlung für die Simulation.

---

## 1. Verfügbare CCU-Commands (Stand APS-CCU)

| Topic | In CCU? | Wirkung |
|-------|---------|---------|
| `ccu/set/park` | ✅ Ja | Parkt alle DPS- und HBW-Module (Calibration Mode → Position PARK). FTS nicht direkt. |
| `ccu/order/cancel` | ✅ Ja | Storniert Aufträge – **nur ENQUEUED**, IN_PROGRESS wird ignoriert. |
| `ccu/set/emergency` | ❌ Nein | Existiert nicht im APS-CCU. War in OMF2 spezifiziert, nie in CCU implementiert. |
| `ccu/set/reset` | ✅ Ja | Factory Reset (Full Reset). |

**Fazit:** `ccu/set/emergency` existiert nicht. OSF enthält keine Referenz darauf (kein Code). Dokumente (publish-buttons-analysis, 99-glossary) erwähnen es als „geplant/nicht implementiert“ – sollte nicht verfolgt werden.

---

## 2. ccu/order/cancel – Verhalten (Fischertechnik-Doku)

**Quelle:** [05-message-structure.md](../06-integrations/fischertechnik-official/05-message-structure.md), [03-ui-integration.md](../06-integrations/fischertechnik-official/03-ui-integration.md)

### Payload

```json
["orderId-1", "orderId-2"]
```

**Format:** `string[]` – Array von Order-IDs. Kein Objekt, kein `orderId: "*"`.

### Verhalten

| Order-State | Verhalten |
|-------------|-----------|
| ENQUEUED | Sofort storniert, erscheint in `ccu/order/completed` mit `state: CANCELLED`. |
| IN_PROGRESS | **Anfrage wird ignoriert.** Order läuft weiter. Keine Fehlermeldung. |

### Beispiel: WHITE in AIQS-Station

- Order ist IN_PROGRESS (FTS hat Werkstück zur AIQS gebracht, CHECK_QUALITY läuft).
- `ccu/order/cancel` mit dieser Order-ID → **ignoriert**.
- Werkstück bleibt in der AIQS. Order wird normal zu Ende geführt (oder schlägt bei Quality-Fail fehl).
- **Blockierung:** Die AIQS ist durch dieses Werkstück belegt. Folgende Orders, die AIQS benötigen, warten. FTS kann blockiert sein.

### Resume nach „Gefahr vorbei“

- Es gibt **kein** `ccu/set/resume` oder `ccu/set/emergency=false`.
- `ccu/order/cancel` stoppt nur wartende Orders, nicht laufende.
- **Praktisch:** Nach Park/Reset bleibt die Anlage in Park/Reset-Zustand. Manueller Eingriff nötig:
  - Physikalisch: Werkstücke prüfen, ggf. entnehmen.
  - `ccu/set/reset` (soft) für Neuaufstellung.
  - FTS: `findInitialDockPosition` etc. (siehe [08-manual-intervention](../06-integrations/fischertechnik-official/08-manual-intervention.md) §8.3).

---

## 3. Dokumentationsfehler: 08-manual-intervention

**Aktuell (falsch):**

```bash
mosquitto_pub -t "ccu/order/cancel" -m '{"orderId":"*","timestamp":"2024-12-08T16:00:00.000Z"}'
```

- Payload ist ein Objekt; CCU erwartet ein Array von Order-IDs.
- `"*"` als „alle“ ist in der CCU **nicht** implementiert.

**Korrekt:** Alle ENQUEUED-Order-IDs aus `ccu/order/active` sammeln und als Array senden:

```bash
mosquitto_pub -t "ccu/order/cancel" -m '["uuid-1","uuid-2"]'
```

---

## 4. Gefahrensimulation – Empfohlener Ansatz

### Ohne `osf/set/emergency`

- **Direkte Alert-Detektion** in OSF oder (später) DSP/MES.
- Bei Alarm (z.B. `osf/arduino/vibration/mpu6050-1/state` mit `vibrationLevel: "red"` oder Flammensensor) → sofort Aktionen auslösen.

### Aktionen bei Alarm

1. **`ccu/set/park`** – Module in Parkposition
   - Payload: `{"timestamp":"<ISO8601>"}`
   - Parkt DPS, HBW (nicht FTS direkt).

2. **`ccu/order/cancel`** – Stornierung wartender Orders
   - Payload: `["orderId1","orderId2",...]` – IDs aus `ccu/order/active`, State ENQUEUED.
   - IN_PROGRESS-Orders werden ignoriert.

### Warum kein `osf/set/emergency`?

- Zusätzliche Abstraktion ohne Nutzen: Ein Subscriber müsste ohnehin `ccu/set/park` und `ccu/order/cancel` senden.
- OSF/DSP erkennt den Alarm bereits – kann direkt die CCU-Commands auslösen.
- Weniger Topics, weniger Fehlerquellen.

### Simulation in OSF-UI (implementiert)

- **Tab:** Sensor-Tab (Vibrations-Kachel) – Alarm-Detektion und Simulation am gleichen Ort.
- **Logik:** `SensorTabComponent` – subscribt `ccu/order/active`, extrahiert ENQUEUED-IDs. `dashboard.commands.simulateDanger(orderIds)` → Business Layer.
- **Button:** „Gefahr simulieren“ – sichtbar in Live/Replay (nicht Mock), aktiv wenn MQTT verbunden.
- **Automatisch (optional):** Beim Empfang von `osf/arduino/.../state` mit Alarm-Zustand (RED/Flame) dieselben Commands senden.
- **Limitation:** IN_PROGRESS-Orders laufen weiter; Werkstück in Station blockiert ggf. folgende Orders. Manueller Eingriff für Vollständigkeit.

---

## 5. Verifikation: ccu/set/park löst KEIN Cancel aus (2026-03)

**Quelle:** APS-CCU `central-control/src/modules/park/index.ts`

Bei Empfang von `ccu/set/park` führt die CCU ausschließlich aus:
- Calibration/Park an alle DPS- und HBW-Module (Position PARK)
- **Kein** automatisches `ccu/order/cancel`, **keine** Stornierung von Orders

**Fischertechnik-UI** (`factory-park.component.ts`): sendet nur `ccu/set/park`, kein Cancel.

**Folge:** Für vollständigen Fabrik-Stop (Park + Stornierung ENQUEUED-Orders) müssen **beide** Befehle gesendet werden: `ccu/set/park` und `ccu/order/cancel` mit ENQUEUED-IDs.

---

## 6. Option C: FTS-Reset durch OSF (2026-03)

**Implementiert:** UC-05 Live-Demo sendet bei Alarm zusätzlich zu Park + Cancel einen RESET-InstantAction an alle bekannten FTS/AGVs:

- Topic: `fts/v1/ff/<serial>/instantAction`
- Payload: `{ serialNumber, timestamp, actions: [{ actionId, actionType: "reset" }] }`
- FTS-Serials: aus `ftsStates$` (active) + Fallback `shopfloor_layout.json` → `fts[].serial`

Damit bleiben AGVs nicht in Bewegung; sie werden physisch angehalten. Recovery: Nach Alarm oft manueller Factory-Reset nötig.

---

## 7. Offene Punkte

- Wirkung von `ccu/set/park` auf Module mit laufender Aktion (z.B. AIQS während CHECK_QUALITY): Wird die Aktion abgebrochen oder erst nach Abschluss geparkt?
- Unterstützung von `orderId: "*"` oder „cancel all“ in der CCU: derzeit nicht vorhanden.

---

## Referenzen

- [APS-CCU protocol](../../integrations/APS-CCU/common/protocol/index.ts) – Topics
- [order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts) – `deleteOrder`, `cancelOrders`
- [08-manual-intervention](../06-integrations/fischertechnik-official/08-manual-intervention.md)
- [05-message-structure](../06-integrations/fischertechnik-official/05-message-structure.md) – Order Cancellation
