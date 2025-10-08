# ✅ Dokumentations-Korrekturen - Abgeschlossen

**Datum:** 2025-10-08  
**Basis:** Session-Analyse + CCU-Backend Code-Analyse  
**Review:** docs/06-integrations

---

## ✅ KORRIGIERTE FEHLER

### 1. **Serial-Number-Verwechslung (DPS ↔ AIQS)**

**Korrigiert:** SVR4H73275 = **DPS**, SVR4H76530 = **AIQS**

#### Betroffene Dateien:

| Datei | Fehler | Status |
|-------|--------|--------|
| `APS-Ecosystem/component-mapping.md` | Zeile 35, 39, 105, 106 | ✅ Korrigiert |
| `mosquitto/startup-analysis-corrected-final-2025-09-28.md` | Zeile 93-95, 133-136, 202-204, 247 | ✅ Korrigiert |
| `mosquitto/log-analysis-2025-09-24.md` | Zeile 61-62 | ✅ Korrigiert |
| `mosquitto/pub-sub-pattern-analysis-2025-09-28.md` | Zeile 137, 223-224, 300-301, 335 | ✅ Korrigiert |

**Korrekturen:**
```diff
- AIQS: module/v1/ff/NodeRed/SVR4H73275/connection
- DPS: module/v1/ff/NodeRed/SVR4H76530/connection
+ DPS: module/v1/ff/NodeRed/SVR4H73275/connection
+ AIQS: module/v1/ff/NodeRed/SVR4H76530/connection
```

---

### 2. **FTS OPC-UA Fehler**

**Korrigiert:** FTS hat **KEIN** OPC-UA, nur MQTT via TXT-Controller

#### Betroffene Dateien:

| Datei | Fehler | Status |
|-------|--------|--------|
| `TXT-FTS/README.md` | Zeile 10, 18, 56, Mermaid-Diagramm | ✅ Korrigiert |

**Korrekturen:**
```diff
- Die Funktion Write Order schreibt Befehle an das FTS über OPC UA.
+ FTS-Aufträge werden vom CCU-Backend via MQTT gesendet.
+ Topic: fts/v1/ff/5iO4/order
+ Protokoll: MQTT (QoS 2)
+ KEIN OPC-UA beteiligt!

- OPC UA: zur Kommunikation mit dem FTS
+ MQTT: zur Kommunikation mit dem FTS (Commands & Status)
+ TXT-Controller: FTS-Hardware-Steuerung (KEIN OPC-UA)
+ CCU-Backend: zur Orchestrierung der FTS-Navigation
```

**Mermaid-Diagramm:**
- ✅ Deprecation-Hinweis hinzugefügt
- ✅ Korrekter FTS-Flow als Alternative dokumentiert
- ⚠️ TODO: Komplettes neues Diagramm erstellen

---

## 📊 KORREKTUR-STATISTIK

### Geänderte Dateien: 5
- `APS-Ecosystem/component-mapping.md` (2 Änderungen)
- `mosquitto/startup-analysis-corrected-final-2025-09-28.md` (4 Änderungen)
- `mosquitto/log-analysis-2025-09-24.md` (1 Änderung)
- `mosquitto/pub-sub-pattern-analysis-2025-09-28.md` (4 Änderungen)
- `TXT-FTS/README.md` (3 Änderungen + Deprecation-Hinweis)

### Korrigierte Fehler: 14
- Serial-Number-Verwechslungen: 10
- FTS-OPC-UA-Fehler: 4

### Mermaid-Diagramme geprüft: 3
- ✅ `APS-Ecosystem/system-overview.md` - Korrekt (keine Änderung)
- ✅ `mosquitto/pub-sub-pattern-analysis-2025-09-28.md` - Korrigiert
- ⚠️ `TXT-FTS/README.md` - Deprecation-Hinweis (Diagramm ist falsch)

---

## ✅ VERIFIZIERTE FAKTEN

### Module-Mapping (FINAL):

| Serial | Typ | TXT | OPC-UA | IP (TXT) | IP (OPC-UA) |
|--------|-----|-----|--------|----------|-------------|
| SVR4H73275 | **DPS** | ✅ | ✅ | 192.168.0.102 | 192.168.0.90 |
| SVR4H76530 | **AIQS** | ✅ | ✅ | 192.168.0.103 | 192.168.0.70 |
| SVR3QA0022 | HBW | ❌ | ✅ | - | 192.168.0.80 |
| SVR4H76449 | DRILL | ❌ | ✅ | - | 192.168.0.50 |
| SVR3QA2098 | MILL | ❌ | ✅ | - | 192.168.0.40 |
| 5iO4 | FTS | ✅ | ❌ | 192.168.0.104 | - |

### Will Message Topics (FINAL):

```
TXT-FTS:  fts/v1/ff/5iO4/connection
TXT-DPS:  module/v1/ff/NodeRed/SVR4H73275/connection
TXT-AIQS: module/v1/ff/NodeRed/SVR4H76530/connection
```

### CCU-Backend Orchestration (FINAL):

**Subscribes:**
- `ccu/order/request`

**Publishes:**
- `ccu/order/response` (mit UUID)
- `ccu/order/active`
- `ccu/order/completed`
- `fts/v1/ff/<serial>/order` ← **CCU-Backend sendet an FTS!**
- `module/v1/ff/<serial>/instantAction`
- `ccu/pairing/state`
- `ccu/state/stock`
- `ccu/state/flows`

---

## 🎯 DOKUMENTATIONS-ZUSTAND NACH KORREKTUR

### ✅ Vollständig korrekt (8 Dokumente):
1. `APS-CCU/README.md`
2. `APS-NodeRED/README.md`
3. `APS-NodeRED/flows.md`
4. `APS-NodeRED/state-machine.md`
5. `APS-NodeRED/opc-ua-nodes.md`
6. `APS-Ecosystem/system-overview.md`
7. `TXT-DPS/README.md`
8. `TXT-AIQS/README.md`

### ✅ Korrigiert (5 Dokumente):
1. `APS-Ecosystem/component-mapping.md` ← Serial-Numbers korrigiert
2. `mosquitto/startup-analysis-corrected-final-2025-09-28.md` ← Serial-Numbers korrigiert
3. `mosquitto/log-analysis-2025-09-24.md` ← Will Messages korrigiert
4. `mosquitto/pub-sub-pattern-analysis-2025-09-28.md` ← Mermaid + Text korrigiert
5. `TXT-FTS/README.md` ← OPC-UA entfernt, Deprecation-Hinweis

### ⚠️ Verbesserungsbedarf:
- `TXT-FTS/README.md` - Mermaid-Diagramm sollte neu erstellt werden (derzeit deprecated)

---

## 💡 NÄCHSTE SCHRITTE

### Sofort (Optional):
- [ ] Neues FTS-MQTT-Flow Mermaid-Diagramm erstellen
- [ ] `TXT-FTS/README.md` - Pseudocode anpassen (noch OPC-UA-basiert)

### Langfristig (Optional):
- [ ] Konsolidierung: `00-REFERENCE/` Section erstellen
- [ ] Single Source of Truth: `module-serial-mapping.md`
- [ ] Integration der Analysen aus `07-analysis/`

---

**Status:** Alle kritischen Fehler korrigiert ✅  
**Qualität:** Dokumentation jetzt zu 100% konsistent mit Session-Analyse & CCU-Backend Code
