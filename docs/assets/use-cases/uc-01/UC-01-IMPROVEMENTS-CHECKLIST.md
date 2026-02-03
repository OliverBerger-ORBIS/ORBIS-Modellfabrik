# UC-01 Track & Trace Genealogy - Verbesserungsvorschläge Checkliste

**Datum:** 2026-01-21  
**Quelle:** ChatGPT-Analyse basierend auf Draw.io-Diagrammen, Screenshots, PNG-Konzept und MD-Beschreibung

---

## 🎯 Kernprobleme identifiziert

- [x] **Hauptproblem:** Vermischung der Ebenen (Prozessfluss/Plan, technische Ausführung/Orders, reale Events, Datenmodell/Objekte) in einem Bild
- [x] **Visuelles Problem:** "Spaghetti-Edges" durch gleichzeitige Darstellung von Plan, Ist und Objektmodell
- [x] **Konzeptproblem:** "Plan vs. Ist" nicht explizit als eigenes Konzept verankert

---

## ✅ Was bereits gut ist (beibehalten)

- [x] Kernprinzip ist klar: eindeutige Workpiece-ID/NFC als Join-Key
- [x] UI-Pattern ist sauber definiert: (1) Tracked Workpieces, (2) Event History als Timeline/Swimlane, (3) Order Context Panel
- [x] Scope-Abgrenzung ist gut: UC-01 = Timeline+Kontext; Sensor-/Umweltdaten-Korrelation explizit in UC-02
- [x] "Live statt Mock" als Story-Element ist stark (Proof-Visual, nicht nur Konzeptfolie)

---

## 📋 Verbesserungsvorschläge - Implementierungs-Checkliste

### 1. Explizit machen: "Plan vs. Ist"

**Status:** ⏳ Offen

**Aufgaben:**
- [ ] **Konzeptabschnitt für A2-Text ergänzen:**
  - Plan kommt aus Orders/Prozessmodell (ERP/MES/WMS/Dispatch): erwartete Soll-Schritte + Zielzustand
  - Ist kommt als Event-Stream (Station/FTS/HBW/Qualität): realer Verlauf inkl. Umwege, Wartezeiten, Rework, Störungen
  - Genealogy ist *nicht* "die geplante Route", sondern die **Korrelation** von Ist-Events zu Plan-Objekten (Order/Operation/Material/Batch) über den Join-Key (NFC)

**Dateien:**
- `docs/assets/use-cases/uc-01/UC-01_Track_Trace-genealogy.md` → Abschnitt "Orchestrierung / Systeminteraktion"

---

### 2. "Join-Key" als Hero-Element

**Status:** ⏳ Offen

**Aufgaben:**
- [ ] Workpiece-ID/NFC muss im Blog-Visual an mindestens 3 Stellen identisch auftauchen:
  - [ ] Workpiece-Liste
  - [ ] Timeline-Header
  - [ ] Order-Context-Panel
- [ ] Visuelles Gesetz dokumentieren (als erstes visuelles Gesetz in A2 zeigen)

**Dateien:**
- `docs/assets/use-cases/uc-01/UC-01_Track_Trace-genealogy.md` → Abschnitt "Join-Key-Prinzip (Pflicht)"
- OSF-Screen: `osf/apps/osf-ui/src/app/pages/use-cases/track-trace-genealogy/`

---

### 3. Zwei getrennte Visuals statt einem

**Status:** ⏳ Offen

**Aufgaben:**

#### Visual 1: "Objekt-Geflecht" (ER/Domain-Mesh – ohne Attribute)
- [ ] Workpiece (NFC) als Zentrum
- [ ] Event als Hub
- [ ] An Event hängen: Station/AGV/Location, Quality Result, Measurements
- [ ] Business-Kontext: Production/Customer/Purchase Order, Material/Batch
- [ ] DSP als Korrelator/Enricher zwischen Event-Stream und Kontext

**Dateien:**
- Draw.io-Diagramm: `docs/assets/use-cases/uc-01/UC-01-ObjectMesh.drawio` (zu erstellen)

#### Visual 2: "Event-Flow mit Soll/Ist-Overlay" (Timeline)
- [ ] Eine horizontale Zeitachse (Ist-Events)
- [ ] Darüber eine "dotted" Soll-Sequenz (Order-Plan)
- [ ] Abweichungen als seitliche "branches" (Reroute via AGV/FTS, Stop, Rework)
- [ ] Jeder Event-Knoten trägt mini-Badges: `workpieceId`, `station`, optional `orderId`

**Dateien:**
- Draw.io-Diagramm: `docs/assets/use-cases/uc-01/UC-01-EventFlow.drawio` (zu erstellen)
- SVG-Generator: `osf/apps/osf-ui/src/app/pages/use-cases/track-trace-genealogy/uc-01-svg-generator.service.ts`

---

### 4. UI-Verbesserungen für OSF-Screen

**Status:** ⏳ Offen

**Aufgaben:**

#### 4.1 "Pinned Join-Key Header"
- [ ] Oben im Event-History-Panel eine feste Zeile implementieren:
  - `Workpiece-ID: <NFC> | Production Order: <ID> | Current Location: <Station>`
- [ ] Macht die Korrelation "ohne Lesen" sichtbar

**Dateien:**
- Component: `osf/apps/osf-ui/src/app/pages/use-cases/track-trace-genealogy/track-trace-genealogy-use-case.component.ts`
- Template: `osf/apps/osf-ui/src/app/pages/use-cases/track-trace-genealogy/track-trace-genealogy-use-case.component.html`
- Styles: `osf/apps/osf-ui/src/app/pages/use-cases/track-trace-genealogy/track-trace-genealogy-use-case.component.scss`

#### 4.2 "Plan-Next vs. Actual-Next" Indikator
- [ ] Kleiner Block rechts im Order-Context:
  - [ ] Expected next step (aus Plan/Route/Order)
  - [ ] Observed last event (aus Timeline)
  - [ ] Deviation badge, wenn mismatch / reroute

**Dateien:**
- Component: `osf/apps/osf-ui/src/app/pages/use-cases/track-trace-genealogy/track-trace-genealogy-use-case.component.ts`
- Service: `osf/apps/osf-ui/src/app/pages/use-cases/track-trace-genealogy/uc-01-structure.config.ts`

#### 4.3 Domain-Filter + Missing-Event Marker
- [ ] Timeline: Toggle **Shopfloor / Logistics / Quality** (bereits gruppiert vorhanden)
- [ ] "missing/late" Marker (z. B. wenn Start ohne End)

**Dateien:**
- Component: `osf/apps/osf-ui/src/app/pages/use-cases/track-trace-genealogy/track-trace-genealogy-use-case.component.ts`
- Service: `osf/apps/osf-ui/src/app/pages/use-cases/track-trace-genealogy/uc-01-structure.config.ts`

---

### 5. Datenmodell-Schärfung

**Status:** ⏳ Offen

**Aufgaben:**
- [ ] **Kanonisches "Event" definieren:**
  - [ ] `eventId, ts, domain (shopfloor|logistics|quality), type`
  - [ ] `workpieceId (NFC)` **(mandatory join key)**
  - [ ] `assetId/stationId` (optional)
  - [ ] `locationId` (optional)
  - [ ] `orderRefs[]` (productionOrderId, storageOrderId, transportOrderId …)
  - [ ] `payloadRef` (QualityResultId, MeasurementSetId, ErrorId …)

**Zweck:**
- Timeline bauen (sort by ts)
- Kontextpanel bauen (resolve orderRefs)
- Objekt-Geflecht rendern (Graph traversal ab workpieceId)

**Dateien:**
- TypeScript Interfaces: `osf/apps/osf-ui/src/app/pages/use-cases/track-trace-genealogy/uc-01-structure.config.ts`
- Event Service: `osf/apps/osf-ui/src/app/pages/use-cases/track-trace-genealogy/` (zu prüfen/erstellen)

---

### 6. Terminologie-Glättung

**Status:** ⏳ Offen

**Aufgaben:**
- [ ] Konsistente Benennung dokumentieren:
  - [ ] **SinglePart = Workpiece** (ein physisches Teil, identifiziert durch NFC)
  - [ ] **HU** nur, wenn wirklich "Container-Trace" gezeigt werden soll (sonst optional)
  - [ ] **Transport Order** (Order) vs. **Mission/Step** (Ausführung) klar trennen
  - [ ] **Production Order** (Business/ERP/MES) vs. **Shopfloor Events** (Ist)

**Dateien:**
- Glossar: `docs/99-glossary.md`
- UC-01 Dokumentation: `docs/assets/use-cases/uc-01/UC-01_Track_Trace-genealogy.md`

---

## 📊 Priorisierung

### Phase 1: Konzept & Visuals (für A2-Blog)
1. ✅ Dokumentation aktualisiert
2. ⏳ Visual 1: Objekt-Geflecht (Draw.io)
3. ⏳ Visual 2: Event-Flow mit Soll/Ist-Overlay (Draw.io)
4. ⏳ "Plan vs. Ist" Konzeptabschnitt ergänzen

### Phase 2: UI-Verbesserungen (OSF-Screen)
5. ⏳ "Pinned Join-Key Header"
6. ⏳ "Plan-Next vs. Actual-Next" Indikator
7. ⏳ Domain-Filter + Missing-Event Marker

### Phase 3: Datenmodell & Terminologie
8. ⏳ Kanonisches Event-Modell definieren
9. ⏳ Terminologie-Glättung dokumentieren

---

## 📝 Notizen

- ChatGPT hat eine **zusätzliche, extrem reduzierte Draw.io-Variante** für Visual 1 erzeugt (noch nicht im Repo)
- Visual 2 (Soll/Ist-Timeline) kann als draw.io-Datei im gleichen reduzierten Stil erstellt werden
- Ziel: **Vermeidung der "alles-in-einem"-Unübersichtlichkeit**

---

## 🔗 Referenzen

- Hauptdokumentation: `docs/assets/use-cases/uc-01/UC-01_Track_Trace-genealogy.md`
- Planungsvorlage: `docs/assets/use-cases/uc-01/UC-01-TIMELINE-PLANNING.txt`
- ChatGPT-Analyse: User-Query vom 2026-01-21
- Draw.io-Diagramme: (noch nicht im Repo, werden nach Planung hinzugefügt)
