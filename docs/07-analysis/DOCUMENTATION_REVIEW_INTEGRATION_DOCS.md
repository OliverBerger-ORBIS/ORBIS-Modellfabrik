# 📋 Dokumentations-Review: docs/06-integrations

**Datum:** 2025-10-08  
**Reviewer:** AI-Agent basierend auf Session-Analyse & CCU-Backend Code-Analyse  
**Basis:** Factsheet-Analyse aus auftrag-*.db + CCU-Backend JavaScript-Code

---

## ✅ GESICHERTE FAKTEN (Ground Truth)

### Module Serial-Number Mapping

| Serial | Typ | TXT-Controller | OPC-UA Server | Quelle |
|--------|-----|----------------|---------------|--------|
| **SVR4H73275** | **DPS** | ✅ | ✅ | Factsheet: `module/v1/ff/SVR4H73275/factsheet` → `"moduleClass":"DPS"` |
| **SVR4H76530** | **AIQS** | ✅ | ✅ | Factsheet: `module/v1/ff/SVR4H76530/factsheet` → `"moduleClass":"AIQS"` |
| SVR3QA0022 | HBW | ❌ | ✅ | Factsheet: `module/v1/ff/SVR3QA0022/factsheet` → `"moduleClass":"HBW"` |
| SVR4H76449 | DRILL | ❌ | ✅ | Factsheet: `module/v1/ff/SVR4H76449/factsheet` → `"moduleClass":"DRILL"` |
| SVR3QA2098 | MILL | ❌ | ✅ | Factsheet: `module/v1/ff/SVR3QA2098/factsheet` → `"moduleClass":"MILL"` |
| 5iO4 | FTS | ✅ | ❌ | Factsheet: `fts/v1/ff/5iO4/factsheet`, Integration-Doku, kein OPC-UA Port |

### CCU-Backend Orchestration

**Quelle:** `integrations/APS-CCU/ff-central-control-unit/central-control/src/`

- ✅ Subscribes: `ccu/order/request`
- ✅ Generates: UUID mit `uuid.v4()`
- ✅ Publishes: `ccu/order/response`, `fts/v1/ff/<serial>/order`, `module/v1/ff/<serial>/instantAction`, etc.
- ✅ Location: Raspberry Pi Docker Container

### NodeRed Role

**Quelle:** NodeRed flows.json Analyse

- ✅ OPC-UA ↔ MQTT Bridge für MILL/DRILL/HBW
- ✅ State-Enrichment für DPS/AIQS
- ❌ **NICHT** beteiligt an: Order-Management, UUID-Generation
- ❌ **NICHT** published: `fts/v1/ff/<serial>/order`
- ❌ **NICHT** subscribes: `ccu/order/request`

---

## ❌ GEFUNDENE FEHLER

### 1. **docs/06-integrations/APS-Ecosystem/component-mapping.md**

#### Fehler 1.1: Serial-Number-Verwechslung (Zeile 105-106)

**Aktuell (FALSCH):**
```markdown
- **AIQS:** `module/v1/ff/NodeRed/SVR4H73275/connection`
- **DPS:** `module/v1/ff/NodeRed/SVR4H76530/connection`
```

**Korrektur:**
```markdown
- **DPS:** `module/v1/ff/NodeRed/SVR4H73275/connection`
- **AIQS:** `module/v1/ff/NodeRed/SVR4H76530/connection`
```

**Beweis:**
```sql
sqlite3 data/omf-data/sessions/auftrag-blau_1.db "SELECT topic, json_extract(payload, '$.serialNumber'), json_extract(payload, '$.typeSpecification.moduleClass') FROM mqtt_messages WHERE topic LIKE '%factsheet%'"

module/v1/ff/SVR4H73275/factsheet → SVR4H73275 → DPS
module/v1/ff/SVR4H76530/factsheet → SVR4H76530 → AIQS
```

---

### 2. **docs/06-integrations/TXT-FTS/README.md**

#### Fehler 2.1: FTS mit OPC-UA erwähnt (Zeile 10)

**Aktuell (FALSCH):**
```markdown
Die Steuerung des fahrerlosen Transportsystems (FTS) bzw. Automated Guided Vehicle (AGV) 
nach dem VDA 5050 Standard ist in der Datei implizit enthalten, insbesondere durch die 
Verarbeitung von Aufträgen (Orders) und deren Weiterleitung über OPC UA Nodes.
```

**Problem:**
- FTS hat **KEIN** OPC-UA
- FTS hat **NUR** TXT-Controller mit MQTT

**Korrektur:**
```markdown
Die Steuerung des fahrerlosen Transportsystems (FTS) bzw. Automated Guided Vehicle (AGV) 
nach dem VDA 5050 Standard erfolgt über MQTT-Topics (`fts/v1/ff/5iO4/*`). 

Das FTS hat einen TXT-Controller (KEIN OPC-UA Server) und kommuniziert ausschließlich 
via MQTT mit dem CCU-Backend.
```

#### Fehler 2.2: NodeRed schreibt an FTS via OPC-UA (Zeile 18)

**Aktuell (FALSCH):**
```markdown
Die Funktion Write Order (z. B. Node e7e0014dac56a4d5) schreibt Befehle an das FTS über OPC UA.
```

**Problem:**
- FTS bekommt Orders via **MQTT** vom **CCU-Backend**
- NodeRed ist **NICHT** beteiligt an FTS-Order-Management

**Korrektur:**
```markdown
FTS-Orders werden vom CCU-Backend erstellt und via MQTT an das FTS gesendet:
- Topic: `fts/v1/ff/5iO4/order`
- Sender: CCU-Backend (`modules/fts/navigation/navigation.js`)
- Protokoll: MQTT (QoS 2)
- Kein OPC-UA beteiligt!
```

---

## ⚠️ MISSVERSTÄNDNISSE IN DOKU

### TXT-FTS/README.md ist irreführend

**Problem:**
- Dokument beschreibt NodeRed-Flows für FTS
- **ABER:** FTS hat kein OPC-UA!
- NodeRed orchestriert Module (MILL/DRILL/HBW), **NICHT** FTS
- FTS wird vom **CCU-Backend** direkt via MQTT gesteuert

**Empfehlung:**
- Dokument umbenennen oder neu strukturieren
- Klarstellen: NodeRed Flows sind für **Module**, nicht für FTS
- FTS-Steuerung ist im **CCU-Backend** (`modules/fts/`)

---

## 📊 DOKUMENTATIONS-ZUSTAND

### ✅ Korrekte Dokumente (keine Fehler gefunden):

1. **docs/06-integrations/APS-CCU/README.md**
   - Korrekte Beschreibung der CCU-Komponenten
   - Keine Serial-Number-Fehler
   - ✅ Gut strukturiert

2. **docs/06-integrations/APS-NodeRED/README.md**
   - Korrekte Beschreibung der NodeRed-Rolle
   - Keine Serial-Number-Fehler
   - ✅ Gut strukturiert

3. **docs/06-integrations/APS-Ecosystem/system-overview.md**
   - Korrekte System-Architektur
   - Keine Serial-Number-Fehler
   - ✅ Gut strukturiert

### ❌ Dokumente mit Fehlern:

1. **docs/06-integrations/APS-Ecosystem/component-mapping.md**
   - ❌ Serial-Number-Verwechslung (DPS ↔ AIQS)
   - Zeilen 105-106

2. **docs/06-integrations/TXT-FTS/README.md**
   - ❌ FTS mit OPC-UA beschrieben (falsch)
   - ❌ NodeRed schreibt an FTS via OPC-UA (falsch)
   - ⚠️ Generell irreführend bezüglich FTS-Steuerung

---

## 💡 EMPFEHLUNGEN

### Sofort-Korrekturen (kritisch):

1. ✅ **component-mapping.md korrigieren:**
   - Zeile 105: `SVR4H73275` → **DPS** (nicht AIQS)
   - Zeile 106: `SVR4H76530` → **AIQS** (nicht DPS)

2. ✅ **TXT-FTS/README.md korrigieren:**
   - Entferne alle OPC-UA-Referenzen für FTS
   - Klarstelle: FTS = NUR MQTT, KEIN OPC-UA
   - CCU-Backend steuert FTS, NICHT NodeRed

### Konsolidierungs-Vorschläge:

#### Option A: Neue Struktur mit zentraler Referenz

**Erstelle:**
```
docs/06-integrations/
├── 00-REFERENCE/
│   ├── module-serial-mapping.md          ← SINGLE SOURCE OF TRUTH
│   ├── hardware-architecture.md          ← Hardware-Übersicht
│   └── mqtt-topic-conventions.md         ← Topic-Naming
├── APS-CCU/
│   ├── README.md
│   └── backend-orchestration.md          ← Link zu 07-analysis
├── APS-NodeRED/
│   ├── README.md
│   ├── flows.md
│   └── opc-ua-bridge.md                  ← NodeRed-Rolle klarstellen
└── ...
```

#### Option B: Konsolidierung & Deprecation

**Konsolidiere:**
1. Merge `APS-Ecosystem/component-mapping.md` → `00-REFERENCE/module-serial-mapping.md`
2. Merge unsere Analysen aus `07-analysis/` → `06-integrations/APS-CCU/`
3. Deprecate veraltete/fehlerhafte Dokumente

**Deprecation-Marker:**
```markdown
> ⚠️ **DEPRECATED - ENTHÄLT FEHLER**
> 
> Dieses Dokument enthält veraltete Informationen:
> - SVR4H73275 = DPS (nicht AIQS)
> - SVR4H76530 = AIQS (nicht DPS)
> 
> **Neue Dokumentation:** `docs/07-analysis/ccu-backend-mqtt-orchestration.md`
```

---

## 🎯 VORSCHLAG: Documentation Cleanup Sprint

### Phase 1: Fehler-Korrektur (Sofort)
- [ ] `component-mapping.md` - Serial-Numbers korrigieren
- [ ] `TXT-FTS/README.md` - OPC-UA-Referenzen entfernen

### Phase 2: Konsolidierung (Später)
- [ ] Neue `00-REFERENCE/` Section erstellen
- [ ] `module-serial-mapping.md` als SINGLE SOURCE OF TRUTH
- [ ] Analysen aus `07-analysis/` in `06-integrations/` integrieren

### Phase 3: Deprecation (Optional)
- [ ] Veraltete Dokumente mit Deprecation-Marker
- [ ] Links auf neue Doku setzen

---

## 📝 ZUSAMMENFASSUNG

### Fehler gefunden:
- ❌ **2 Dokumente** mit Fehlern
- ❌ **4 konkrete Fehler** (2x Serial-Verwechslung, 2x FTS-OPC-UA)

### Dokumentations-Qualität:
- ✅ **3 Dokumente** korrekt
- ⚠️ **2 Dokumente** mit Fehlern
- 📊 **Gesamt:** 60% fehlerfreie Dokumente

### Kritische Fehler:
1. ⚠️ **Serial-Number-Verwechslung** - kann zu falschen Implementierungen führen
2. ⚠️ **FTS-OPC-UA-Fehler** - FTS hat kein OPC-UA!

### Nächste Schritte:
1. ✅ Sofort: `component-mapping.md` korrigieren
2. ✅ Sofort: `TXT-FTS/README.md` korrigieren
3. 💡 Später: Konsolidierung & Referenz-Struktur

---

**Status:** Review abgeschlossen - Korrekturen identifiziert 🎯












