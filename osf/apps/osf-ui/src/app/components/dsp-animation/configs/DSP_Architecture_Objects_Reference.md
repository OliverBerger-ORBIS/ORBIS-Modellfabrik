# DSP Architecture Objects Reference

Diese Dokumentation beschreibt alle Objekte (Container), Connections und Function Icons, die in der DSP-Animation verwendet werden, mit Fokus auf **Step 19** (Functional View: "Autonomous & Adaptive Enterprise").

## Übersicht

Step 19 zeigt die vollständige DSP-Architektur mit allen Layern, Containern und Connections. Es ist der finale Überblick, in dem alle Komponenten gleichzeitig sichtbar sind (ohne Highlighting).

## Layer-Struktur

Die DSP-Animation ist in drei horizontale Layer unterteilt:

1. **Business Process Layer** (oben, weiß) - `layer-bp`
2. **DSP Layer** (Mitte, blau) - `layer-dsp`
3. **Shopfloor Layer** (unten, grau) - `layer-sf`

---

## Business Process Layer (`layer-bp`)

### Container IDs

- **`bp-erp`** - ERP Applications
  - **Icon:** `erp-application`
  - **Brand Logo:** `logo-sap` (top-right)
  - **Type:** `business`
  - **Position:** Links, erste Box

- **`bp-mes`** - MES Applications
  - **Icon:** `mes-application`
  - **Brand Logo:** `logo-orbis` (top-left)
  - **Type:** `business`
  - **Position:** Zweite Box

- **`bp-cloud`** - Cloud Applications
  - **Icon:** `bp-cloud-apps`
  - **Brand Logos:** `aws-logo`, `google-cloud-logo` (multiple secondary logos)
  - **Type:** `business`
  - **Position:** Dritte Box

- **`bp-analytics`** - Analytics Applications
  - **Icon:** `bp-analytics`
  - **Brand Logo:** `logo-grafana` (top-right)
  - **Type:** `business`
  - **Position:** Vierte Box
  - **URL:** `/analytics`

- **`bp-data-lake`** - Data Lake
  - **Icon:** `bp-data-lake`
  - **Type:** `business`
  - **Position:** Fünfte Box

### Connections von Business Process Layer

Alle Business Process Container haben Connections zum DSP Edge:

- **`conn_bp-erp_dsp-edge`** - ERP → DSP Edge
  - **From:** `bp-erp` (bottom)
  - **To:** `dsp-edge` (top)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

- **`conn_bp-mes_dsp-edge`** - MES → DSP Edge
  - **From:** `bp-mes` (bottom)
  - **To:** `dsp-edge` (top)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

- **`conn_bp-cloud_dsp-edge`** - Cloud → DSP Edge
  - **From:** `bp-cloud` (bottom)
  - **To:** `dsp-edge` (top)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

- **`conn_bp-analytics_dsp-edge`** - Analytics → DSP Edge
  - **From:** `bp-analytics` (bottom)
  - **To:** `dsp-edge` (top)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

- **`conn_bp-data-lake_dsp-edge`** - Data Lake → DSP Edge
  - **From:** `bp-data-lake` (bottom)
  - **To:** `dsp-edge` (top)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

---

## DSP Layer (`layer-dsp`)

### Container IDs

- **`dsp-ux`** - SmartFactory Dashboard (UX)
  - **Icon:** `ux-box` (center)
  - **Type:** `ux`
  - **Position:** Links, halbe Höhe
  - **URL:** `/dashboard`

- **`dsp-edge`** - DSP Edge
  - **Logo:** `logo-dsp` (top-left)
  - **Center Icon:** `logo-edge`
  - **Type:** `dsp-edge`
  - **Position:** Mitte, volle Höhe
  - **Environment Label:** "On Premise"
  - **URL:** `/edge`
  - **Function Icons:** 9 Edge Function Icons (siehe unten)
  - **Edge Components:** 8 interne Komponenten (nur in Component View sichtbar)

- **`dsp-mc`** - Management Cockpit
  - **Logo:** `logo-orbis` (top-left)
  - **Secondary Logo:** `logo-azure` (top-right)
  - **Center Icon:** `logo-mc`
  - **Type:** `dsp-cloud`
  - **Position:** Rechts, volle Höhe
  - **Environment Label:** "Cloud"
  - **URL:** `/management-cockpit`
  - **Function Icons:** 6 MC Function Icons (siehe unten)

### DSP Edge Function Icons

Diese Icons werden innerhalb des `dsp-edge` Containers angezeigt (nur in Functional View, wenn `showFunctionIcons: true`):

1. **`edge-interoperability`** - Interoperabilität
   - **Icon Key:** `edge-interoperability`
   - **Size:** 48px
   - **Beschreibung:** Ermöglicht die Kommunikation zwischen verschiedenen Systemen und Protokollen

2. **`edge-network`** - Netzwerk / Connectivity
   - **Icon Key:** `edge-network`
   - **Size:** 48px
   - **Beschreibung:** Netzwerk-Konnektivität und Kommunikationsinfrastruktur

3. **`edge-event-driven`** - Event-Driven Processing
   - **Icon Key:** `edge-event-driven`
   - **Size:** 48px
   - **Beschreibung:** Ereignisgesteuerte Verarbeitung von Shopfloor-Events

4. **`edge-choreography`** - Process Choreography
   - **Icon Key:** `edge-choreography`
   - **Size:** 48px
   - **Beschreibung:** Dezentrale Prozess-Choreographie ohne zentrale Orchestrierung

5. **`edge-digital-twin`** - Digital Twin
   - **Icon Key:** `edge-digital-twin`
   - **Size:** 48px
   - **Beschreibung:** Digitale Abbildung physischer Assets und Prozesse

6. **`edge-best-of-breed`** - Best-of-Breed Integration
   - **Icon Key:** `edge-best-of-breed`
   - **Size:** 48px
   - **Beschreibung:** Integration verschiedener Best-of-Breed Lösungen

7. **`edge-analytics`** - Analytics
   - **Icon Key:** `edge-analytics`
   - **Size:** 48px
   - **Beschreibung:** Lokale Datenanalyse und Auswertung

8. **`edge-ai-enablement`** - AI Enablement
   - **Icon Key:** `edge-ai-enablement`
   - **Size:** 48px
   - **Beschreibung:** KI-Funktionalitäten am Edge

9. **`edge-autonomous-enterprise`** - Autonomous Enterprise
   - **Icon Key:** `edge-autonomous-enterprise`
   - **Size:** 48px
   - **Beschreibung:** Autonome und adaptive Fertigungsprozesse

**Hinweis:** In Step 19 sind diese Function Icons **nicht sichtbar** (`showFunctionIcons: false`). Sie werden in früheren Steps (Step 3-12) schrittweise eingeblendet.

### Management Cockpit (MC) Function Icons

Diese Icons werden innerhalb des `dsp-mc` Containers angezeigt (nur in Functional View, wenn `showFunctionIcons: true`):

1. **`mc-hierarchical-structure`** - Hierarchische Struktur
   - **Icon Key:** `mc-hierarchical-structure`
   - **Size:** 48px
   - **Beschreibung:** Hierarchische Organisation mehrerer Edge-Instanzen

2. **`mc-orchestration`** - Orchestrierung
   - **Icon Key:** `mc-orchestration`
   - **Size:** 48px
   - **Beschreibung:** Zentrale Orchestrierung von Edge-Prozessen

3. **`mc-governance`** - Governance
   - **Icon Key:** `mc-governance`
   - **Size:** 48px
   - **Beschreibung:** Governance und Compliance-Management

4. **`logo-edge-a`** - Edge Instance A
   - **Icon Key:** `logo-edge-a`
   - **Size:** 48px
   - **Beschreibung:** Repräsentiert eine Edge-Instanz (wird in Step 18 angezeigt)

5. **`logo-edge-b`** - Edge Instance B
   - **Icon Key:** `logo-edge-b`
   - **Size:** 48px
   - **Beschreibung:** Repräsentiert eine Edge-Instanz (wird in Step 18 angezeigt)

6. **`logo-edge-c`** - Edge Instance C
   - **Icon Key:** `logo-edge-c`
   - **Size:** 48px
   - **Beschreibung:** Repräsentiert eine Edge-Instanz (wird in Step 18 angezeigt)

**Hinweis:** 
- In Step 18 werden nur die `logo-edge-*` Icons angezeigt (3 Edge-Instanzen)
- In anderen Steps werden nur die MC-Funktions-Icons (`mc-hierarchical-structure`, `mc-orchestration`, `mc-governance`) angezeigt
- In Step 19 sind alle Function Icons **nicht sichtbar** (`showFunctionIcons: false`)

### Edge Components (nur in Component View sichtbar)

Diese Komponenten sind innerhalb des `dsp-edge` Containers angeordnet (3x3 Grid):

**Row 1:**
- **`edge-comp-disc`** - DISC Component
  - **Icon:** `edge-component-disc`
  - **Position:** Row 1, Column 1 (links)

- **`edge-comp-event-bus`** - Event Bus Component
  - **Icon:** `edge-component-event-bus`
  - **Position:** Row 1, Column 3 (rechts)

**Row 2:**
- **`edge-comp-app-server`** - App Server Component
  - **Icon:** `edge-component-app-server`
  - **Position:** Row 2, Column 1 (links)

- **`edge-comp-router`** - Router Component
  - **Icon:** `edge-component-router`
  - **Position:** Row 2, Column 2 (mitte)

- **`edge-comp-agent`** - Agent Component
  - **Icon:** `edge-component-agent`
  - **Position:** Row 2, Column 3 (rechts)

**Row 3:**
- **`edge-comp-log-server`** - Log Server Component
  - **Icon:** `edge-component-log-server`
  - **Position:** Row 3, Column 1 (links)

- **`edge-comp-disi`** - DISI Component
  - **Icon:** `edge-component-disi`
  - **Position:** Row 3, Column 2 (mitte)

- **`edge-comp-database`** - Database Component
  - **Icon:** `edge-component-database`
  - **Position:** Row 3, Column 3 (rechts)

### Connections im DSP Layer

- **`conn_dsp-ux_dsp-edge`** - UX → Edge
  - **From:** `dsp-ux` (right)
  - **To:** `dsp-edge` (left)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

- **`conn_dsp-edge_dsp-mc`** - Edge → Management Cockpit
  - **From:** `dsp-edge` (right)
  - **To:** `dsp-mc` (left)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

---

## Shopfloor Layer (`layer-sf`)

### Container IDs

#### Shopfloor Systems Group (`sf-systems-group`)

- **`sf-system-any`** - Any System (Generic)
  - **Icon:** `shopfloor-systems`
  - **Type:** `device`
  - **URL:** `/fts`

- **`sf-system-fts`** - FTS/AGV System
  - **Icon:** `shopfloor-fts`
  - **Type:** `device`
  - **URL:** `/process`

- **`sf-system-warehouse`** - Warehouse System
  - **Icon:** `shopfloor-systems` (oder `shopfloor-warehouse` bei Customer Config)
  - **Type:** `device`
  - **URL:** `/process`

- **`sf-system-factory`** - Factory System
  - **Icon:** `shopfloor-systems` (oder `shopfloor-factory` bei Customer Config)
  - **Type:** `device`
  - **URL:** `/process`

**Hinweis:** Bei Customer Configs werden diese durch konkrete System-IDs ersetzt (z.B. `sf-system-1`, `sf-system-2`, etc.).

#### Shopfloor Devices Group (`sf-devices-group`)

- **`sf-device-mill`** - Mill Station
  - **Icon:** `device-mill`
  - **Type:** `device`
  - **URL:** `/module`

- **`sf-device-drill`** - Drill Station
  - **Icon:** `device-drill`
  - **Type:** `device`
  - **URL:** `/module`

- **`sf-device-aiqs`** - AIQS Station
  - **Icon:** `device-aiqs`
  - **Type:** `device`
  - **URL:** `/module`

- **`sf-device-hbw`** - HBW Station
  - **Icon:** `device-hbw`
  - **Type:** `device`
  - **URL:** `/module`

- **`sf-device-dps`** - DPS Station
  - **Icon:** `device-dps`
  - **Type:** `device`
  - **URL:** `/module`

- **`sf-device-chrg`** - Charging Station
  - **Icon:** `device-chrg`
  - **Type:** `device`
  - **URL:** `/module`

**Hinweis:** Bei Customer Configs werden diese durch konkrete Device-IDs ersetzt (z.B. `sf-device-1`, `sf-device-2`, etc.).

### Connections von Shopfloor Layer

Alle Shopfloor Systems und Devices haben Connections zum DSP Edge:

#### System Connections

- **`conn_dsp-edge_sf-system-any`** - Edge → Any System
  - **From:** `dsp-edge` (bottom)
  - **To:** `sf-system-any` (top)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

- **`conn_dsp-edge_sf-system-fts`** - Edge → FTS System
  - **From:** `dsp-edge` (bottom)
  - **To:** `sf-system-fts` (top)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

**Hinweis:** Bei Customer Configs werden diese durch dynamische Connection-IDs ersetzt: `conn_dsp-edge_${system.id}`

#### Device Connections

- **`conn_dsp-edge_sf-device-mill`** - Edge → Mill
  - **From:** `dsp-edge` (bottom)
  - **To:** `sf-device-mill` (top)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

- **`conn_dsp-edge_sf-device-drill`** - Edge → Drill
  - **From:** `dsp-edge` (bottom)
  - **To:** `sf-device-drill` (top)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

- **`conn_dsp-edge_sf-device-aiqs`** - Edge → AIQS
  - **From:** `dsp-edge` (bottom)
  - **To:** `sf-device-aiqs` (top)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

- **`conn_dsp-edge_sf-device-hbw`** - Edge → HBW
  - **From:** `dsp-edge` (bottom)
  - **To:** `sf-device-hbw` (top)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

- **`conn_dsp-edge_sf-device-dps`** - Edge → DPS
  - **From:** `dsp-edge` (bottom)
  - **To:** `sf-device-dps` (top)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

- **`conn_dsp-edge_sf-device-chrg`** - Edge → Charging
  - **From:** `dsp-edge` (bottom)
  - **To:** `sf-device-chrg` (top)
  - **Bidirectional:** Ja
  - **Arrow:** Ja

**Hinweis:** Bei Customer Configs werden diese durch dynamische Connection-IDs ersetzt: `conn_dsp-edge_${device.id}`

---

## Connection-Naming-Konvention

Alle Connections folgen dem Schema:

```
conn_<from-id>_<to-id>
```

**Beispiele:**
- `conn_dsp-ux_dsp-edge` - Von UX zu Edge
- `conn_dsp-edge_dsp-mc` - Von Edge zu Management Cockpit
- `conn_bp-erp_dsp-edge` - Von ERP zu Edge
- `conn_dsp-edge_sf-device-mill` - Von Edge zu Mill Device

**Connection-Eigenschaften:**
- **`fromSide`** / **`toSide`**: `'top'`, `'bottom'`, `'left'`, `'right'`
- **`hasArrow`**: `true` (zeigt Richtung an)
- **`bidirectional`**: `true` (zweiseitige Verbindung)
- **`state`**: `'hidden'` (wird in Step 19 auf `'visible'` gesetzt)

---

## Container-Typen

- **`layer`** - Layer-Hintergrund (Gruppe)
- **`business`** - Business Process Container
- **`ux`** - UX/Dashboard Container
- **`dsp-edge`** - DSP Edge Container
- **`dsp-cloud`** - Management Cockpit Container
- **`device`** - Shopfloor Device/System Container
- **`shopfloor-group`** - Shopfloor Group Container (Gruppe)

---

## Visuelles Diagramm erstellen

### Option 5: Vorhandenes Architektur-Diagramm verwenden (Empfohlen)

**Vorteil:** Das vorhandene DSP-Architektur-Diagramm zeigt bereits alle Boxen und Connections korrekt positioniert.

**Vorgehen:**

1. **Screenshot von Step 19 erstellen:**
   - Öffnen Sie die DSP-Animation in der Browser-Ansicht
   - Navigieren Sie zu Step 19 (Functional View)
   - Erstellen Sie einen Screenshot des gesamten Diagramms
   - **Tipp:** Verwenden Sie Browser DevTools → Screenshot-Funktion für hohe Qualität

2. **Screenshot in die Dokumentation einbinden:**
   ```markdown
   ![DSP Architecture Step 19](./assets/dsp-architecture-step19.png)
   ```

3. **Annotation hinzufügen (optional):**
   - Verwenden Sie ein Bildbearbeitungsprogramm (z.B. Figma, Draw.io, GIMP)
   - Fügen Sie Text-Labels für Container-IDs hinzu
   - Fügen Sie Pfeil-Labels für Connection-IDs hinzu
   - Verwenden Sie Farbcodierung für verschiedene Container-Typen

4. **Screenshot speichern:**
   - Speichern Sie den Screenshot in `omf3/apps/ccu-ui/src/app/components/dsp-animation/configs/assets/`
   - Verwenden Sie einen aussagekräftigen Dateinamen: `dsp-architecture-step19.png`

**Beispiel-Struktur:**
```
configs/
├── assets/
│   ├── dsp-architecture-step19.png (Screenshot)
│   └── dsp-architecture-step19-diagram.svg (SVG Diagramm)
├── DSP_Architecture_Objects_Reference.md
└── ...
```

**Vorteile dieser Methode:**
- ✅ Zeigt exakte Positionen und Layout
- ✅ Enthält bereits alle visuellen Details (Icons, Farben, Connections)
- ✅ Keine manuelle Nachzeichnung nötig
- ✅ Bleibt synchron mit dem tatsächlichen Code
- ✅ Einfach zu aktualisieren (neuer Screenshot bei Änderungen)

---

## SVG-Diagramm

Ein strukturiertes SVG-Diagramm wurde erstellt, das alle Container und Connections zeigt:

![DSP Architecture Step 19 Diagram](./assets/dsp-architecture-step19-diagram.svg)

**Hinweis:** Dieses SVG-Diagramm zeigt die strukturelle Übersicht. Für detaillierte visuelle Darstellung mit echten Icons und exakten Positionen verwenden Sie einen Screenshot der tatsächlichen Animation (siehe Option 5 oben).

---

## Wartung und Erweiterung

### Neue Container hinzufügen

1. **Container in `layout.shared.config.ts` erstellen:**
   ```typescript
   containers.push({
     id: 'neuer-container',
     label: '',
     x: 100,
     y: 200,
     width: 150,
     height: 100,
     type: 'device',
     state: 'hidden',
     logoIconKey: 'device-example' as IconKey,
     // ...
   });
   ```

2. **Container-ID zu Step 19 hinzufügen:**
   ```typescript
   visibleContainerIds: [
     // ... bestehende IDs
     'neuer-container',
   ],
   ```

3. **Connection erstellen (falls nötig):**
   ```typescript
   {
     id: 'conn_dsp-edge_neuer-container',
     fromId: 'dsp-edge',
     toId: 'neuer-container',
     fromSide: 'bottom',
     toSide: 'top',
     state: 'hidden',
     hasArrow: true,
     bidirectional: true,
   }
   ```

### Connection-Verhalten verstehen

**Connection-Rendering:**
- Connections werden als SVG-Pfade (`<path>`) gerendert
- **Anchors:** Verbindungspunkte an Container-Rändern (top, bottom, left, right)
- **Routing:** Automatisches Routing um Container herum
- **Arrows:** Pfeilspitzen zeigen Richtung an (bei `hasArrow: true`)
- **Bidirectional:** Zweiseitige Verbindung (beide Richtungen)

**Connection-Sichtbarkeit:**
- `state: 'hidden'` - Connection ist nicht sichtbar
- `state: 'normal'` - Connection ist sichtbar (grau)
- `state: 'highlighted'` - Connection ist hervorgehoben (blau, dicker)

### Function Icons hinzufügen

1. **Function Icon zu Container hinzufügen:**
   ```typescript
   functionIcons: [
     // ... bestehende Icons
     { iconKey: 'neues-icon' as IconKey, size: 48 },
   ],
   ```

2. **Icon in `icon-registry.ts` registrieren:**
   ```typescript
   'neues-icon': 'assets/svg/dsp/functions/neues-icon.svg',
   ```

3. **Icon in Functional View Steps verwenden:**
   ```typescript
   highlightedFunctionIcons: ['neues-icon'],
   ```

---

## Zusammenfassung

**Step 19 enthält:**

- **3 Layer:** Business Process, DSP, Shopfloor
- **5 Business Process Container:** ERP, MES, Cloud, Analytics, Data Lake
- **3 DSP Container:** UX, Edge, Management Cockpit
- **9 Edge Function Icons:** Interoperability, Network, Event-Driven, Choreography, Digital Twin, Best-of-Breed, Analytics, AI Enablement, Autonomous Enterprise
- **6 MC Function Icons:** Hierarchical Structure, Orchestration, Governance, Edge Instance A/B/C
- **8 Edge Components:** DISC, Event Bus, App Server, Router, Agent, Log Server, DISI, Database
- **2 Shopfloor Groups:** Systems Group, Devices Group
- **4 Default Systems:** Any, FTS, Warehouse, Factory
- **6 Default Devices:** Mill, Drill, AIQS, HBW, DPS, Charging
- **5 Business → Edge Connections**
- **1 UX → Edge Connection**
- **1 Edge → MC Connection**
- **2 System → Edge Connections** (default)
- **6 Device → Edge Connections** (default)

**Total: ~20 Container + ~15 Connections + 15 Function Icons**

Bei Customer Configs können die Shopfloor-Container und Connections variieren, basierend auf der Kundenkonfiguration.
