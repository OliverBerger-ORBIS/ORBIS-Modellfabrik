# FTS Integration - Komponenten & SVG-Mapping

**Datum:** 2025-11-30  
**Status:** Analyse & Planung  
**Ziel:** Vollständiges Mapping der Beispiel-App Komponenten und SVG-Umbenennungsvorschläge

---

## 📦 Komponenten-Mapping

### Beispiel-App Komponenten → OMF3 Integration

| Beispiel-App Komponente | OMF3 Ziel | Status | Anpassungen |
|-------------------------|-----------|--------|-------------|
| `FtsStatusComponent` | `omf3/apps/ccu-ui/src/app/components/fts-status/` | ⏳ Zu migrieren | - Ersetze `FtsMockService` → `MessageMonitorService`<br>- Ersetze `MODULE_NAME_MAP` → `ModuleNameService`<br>- Ersetze Emojis → OMF3-SVGs |
| `FtsBatteryComponent` | `omf3/apps/ccu-ui/src/app/components/fts-battery/` | ⏳ Zu migrieren | - Ersetze `FtsMockService` → `MessageMonitorService`<br>- Ersetze Emojis → OMF3-SVGs |
| `FtsLoadsComponent` | `omf3/apps/ccu-ui/src/app/components/fts-loads/` | ⏳ Zu migrieren | - Ersetze `FtsMockService` → `MessageMonitorService`<br>- Ersetze Workpiece-Icons → `workpieces/*.svg` |
| `FtsRouteComponent` | **NICHT verwenden** | ❌ Wird nicht migriert | - **Ersetzt durch:** `ShopfloorPreviewComponent`<br>- Route & Position werden im Shopfloor-Layout angezeigt |
| `TrackTraceComponent` | `omf3/apps/ccu-ui/src/app/components/track-trace/` | ⏳ Zu migrieren | - Ersetze `FtsMockService` → `MessageMonitorService`<br>- Ersetze alle Emojis → OMF3-SVGs<br>- Ersetze `MODULE_NAME_MAP` → `ModuleNameService` |

### Tab-Komponenten

| Tab | OMF3 Ziel | Komponenten | Status |
|-----|-----------|-------------|--------|
| **FTS/AGV Tab** | `omf3/apps/ccu-ui/src/app/tabs/fts-tab.component.ts` | - `FtsStatusComponent`<br>- `FtsBatteryComponent`<br>- `FtsLoadsComponent`<br>- `ShopfloorPreviewComponent` (Route & Position) | ⏳ Zu erstellen |
| **Track&Trace Tab** | `omf3/apps/ccu-ui/src/app/tabs/track-trace-tab.component.ts` | - `TrackTraceComponent` | ⏳ Zu erstellen |

---

## 🎨 SVG-Mapping & Umbenennungsvorschläge

### Aktuelle OMF3-SVG-Struktur

```
omf3/apps/ccu-ui/public/
├── shopfloor/
│   ├── robotic.svg          # FTS/AGV (aktuell)
│   ├── battery.svg          # ✅ Battery Status (NEU - verwendet)
│   ├── charging-active.svg  # ✅ Charging Active (NEU - verwendet)
│   ├── driving-status.svg   # ✅ Driving Status (NEU - verwendet)
│   ├── stopped-status.svg   # ✅ Stopped Status (NEU - verwendet)
│   ├── paused-status.svg    # ✅ Paused Status (NEU - verwendet)
│   ├── turn-event.svg       # ✅ TURN Event (NEU - verwendet)
│   ├── dock-event.svg       # ✅ DOCK Event (NEU - verwendet)
│   ├── pick-event.svg       # ✅ PICK Event (NEU - verwendet)
│   ├── drop-event.svg       # ✅ DROP Event (NEU - verwendet)
│   ├── pass-event.svg       # ✅ PASS Event (NEU - verwendet)
│   ├── process-event.svg    # ✅ PROCESS Event (NEU - verwendet)
│   ├── location-marker.svg  # ✅ Location Marker (NEU - vorhanden)
│   ├── bohrer.svg           # DRILL (aktuell)
│   ├── milling-machine.svg  # MILL (aktuell)
│   ├── ai-assistant.svg     # AIQS (aktuell)
│   ├── robot-arm.svg        # DPS (aktuell)
│   ├── stock.svg            # HBW (aktuell)
│   ├── fuel.svg             # CHRG (aktuell)
│   ├── intersection{1-4}.svg # Intersections (aktuell)
│   ├── factory.svg          # Factory/Production
│   ├── warehouse.svg        # Warehouse/Storage
│   └── ...
├── workpieces/
│   ├── {color}_product.svg
│   ├── {color}_instock_unprocessed.svg
│   ├── {color}_instock_reserved.svg
│   └── ...
└── headings/
    ├── robotic.svg          # ❓ FEHLT - sollte für FTS Tab verwendet werden
    ├── lieferung-bestellen.svg # Track&Trace Tab
    └── ...
```

### Emoji → SVG Mapping (Beispiel-App)

| Emoji | Verwendung | Aktueller OMF3 SVG | Vorschlag Umbenennung | Neuer Name |
|-------|------------|-------------------|----------------------|------------|
| 🚗 | FTS/AGV Icon | `shopfloor/robotic.svg` | ✅ **OK** | `shopfloor/fts.svg` oder `shopfloor/agv.svg` |
| 🔍 | Track & Trace | ❌ **FEHLT** | ➕ **NEU** | `headings/track-trace.svg` oder `headings/search.svg` |
| 🔋 | Battery | ✅ **VORHANDEN** | ✅ **VERWENDET** | `shopfloor/battery.svg` |
| ⚡ | Charging | ✅ **VORHANDEN** | ✅ **VERWENDET** | `shopfloor/charging-active.svg` |
| 📦 | Loads, DPS | ✅ **VORHANDEN** | ✅ **VERWENDET** | `headings/box.svg` (für Load Information) |
| 📤 | PICK Event | ✅ **VORHANDEN** | ✅ **VERWENDET** | `shopfloor/pick-event.svg` |
| 📥 | DROP Event, Storage Order | ✅ **VORHANDEN** | ✅ **VERWENDET** | `shopfloor/drop-event.svg` |
| ⚙️ | PROCESS Event, MILL | ✅ **VORHANDEN** | ✅ **VERWENDET** | `shopfloor/process-event.svg` |
| ↩️ | TURN Event | ✅ **VORHANDEN** | ✅ **VERWENDET** | `shopfloor/turn-event.svg` |
| ➡️ | PASS Event | ✅ **VORHANDEN** | ✅ **VERWENDET** | `shopfloor/pass-event.svg` |
| 🔗 | DOCK Event | ✅ **VORHANDEN** | ✅ **VERWENDET** | `shopfloor/dock-event.svg` |
| 🚀 | Driving Status | ✅ **VORHANDEN** | ✅ **VERWENDET** | `shopfloor/driving-status.svg` |
| 🛑 | Stopped Status | ✅ **VORHANDEN** | ✅ **VERWENDET** | `shopfloor/stopped-status.svg` |
| ⏸️ | Paused Status | ✅ **VORHANDEN** | ✅ **VERWENDET** | `shopfloor/paused-status.svg` |
| 📍 | Location Marker | ✅ **VORHANDEN** | ⏳ **NOCH NICHT VERWENDET** | `shopfloor/location-marker.svg` |
| 📋 | Order Context | `headings/lieferung-bestellen.svg` | ✅ **OK** | (bereits vorhanden) |
| 🏭 | Production Order | `headings/maschine.svg` | ✅ **OK** | (bereits vorhanden - korrigiert!) |
| 📥 | Storage Order | `headings/ladung.svg` | ✅ **OK** | (bereits vorhanden - korrigiert!) |
| 🏢 | HBW Station | `shopfloor/stock.svg` | ✅ **OK** | (bereits vorhanden) |
| 🔩 | DRILL Station | `shopfloor/bohrer.svg` | ✅ **OK** | (bereits vorhanden) |
| 🔍 | AIQS Station | `shopfloor/ai-assistant.svg` | ✅ **OK** | (bereits vorhanden) |
| 💡 | Info/Help | ❌ **FEHLT** | ➕ **NEU** | `headings/info.svg` oder `headings/help.svg` |
| 🗺️ | Route/Map | ❌ **FEHLT** | ➕ **NEU** | `headings/route.svg` oder `headings/map.svg` |

---

## 🔄 SVG-Umbenennungsvorschläge

### Kategorie 1: Klare Funktionszuordnung (HOCH PRIORITÄT)

#### Shopfloor Icons - FTS/AGV spezifisch (✅ ALLE VORHANDEN UND VERWENDET)

| SVG Name | Status | Verwendung in FTS Tab |
|----------|--------|----------------------|
| `shopfloor/robotic.svg` | ✅ Vorhanden | FTS/AGV Icon (Heading, Status) |
| `shopfloor/battery.svg` | ✅ Vorhanden | Battery Status Icon |
| `shopfloor/charging-active.svg` | ✅ Vorhanden | Charging Active Icon |
| `shopfloor/driving-status.svg` | ✅ Vorhanden | Driving Status Badge |
| `shopfloor/stopped-status.svg` | ✅ Vorhanden | Stopped Status Badge |
| `shopfloor/paused-status.svg` | ✅ Vorhanden | Paused Status Badge |
| `shopfloor/turn-event.svg` | ✅ Vorhanden | TURN Action Icon |
| `shopfloor/dock-event.svg` | ✅ Vorhanden | DOCK Action Icon |
| `shopfloor/pick-event.svg` | ✅ Vorhanden | PICK Action Icon |
| `shopfloor/drop-event.svg` | ✅ Vorhanden | DROP Action Icon |
| `shopfloor/pass-event.svg` | ✅ Vorhanden | PASS Action Icon |
| `shopfloor/process-event.svg` | ✅ Vorhanden | PROCESS Action Icon |
| `shopfloor/location-marker.svg` | ✅ Vorhanden | Location Marker (noch nicht verwendet) |

#### Headings Icons

| Aktueller Name | Neuer Name | Grund |
|----------------|------------|-------|
| | `headings/fts.svg` | NEU - für FTS Tab Heading |
| | `headings/track-trace.svg` | NEU - für Track&Trace Tab Heading |
| | `headings/route.svg` | NEU - für Route/Map Heading |
| | `headings/info.svg` | NEU - für Info/Help |

### Kategorie 2: Station Icons (BEREITS OK)

| Icon | Status | Verwendung |
|------|--------|------------|
| `shopfloor/bohrer.svg` | ✅ OK | DRILL Station |
| `shopfloor/milling-machine.svg` | ✅ OK | MILL Station |
| `shopfloor/ai-assistant.svg` | ✅ OK | AIQS Station |
| `shopfloor/robot-arm.svg` | ✅ OK | DPS Station |
| `shopfloor/stock.svg` | ✅ OK | HBW Station |
| `shopfloor/factory.svg` | ✅ OK | Production Order |
| `shopfloor/warehouse.svg` | ✅ OK | Storage Order |
| `shopfloor/intersection{1-4}.svg` | ✅ OK | Intersections |

### Kategorie 3: Workpiece Icons (BEREITS OK)

| Icon Pattern | Status | Verwendung |
|--------------|--------|------------|
| `workpieces/{color}_product.svg` | ✅ OK | DROP Event, Finished Product |
| `workpieces/{color}_instock_unprocessed.svg` | ✅ OK | PICK Event, Raw Material |
| `workpieces/{color}_instock_reserved.svg` | ✅ OK | Reserved Workpiece |
| `workpieces/slot_empty.svg` | ✅ OK | Empty Slot |

---

## 🎯 Platzhalter vs. SVGs - Entscheidungshilfe

### Option A: Platzhalter verwenden (EMPFOHLEN für schnellen Start)

**Vorteile:**
- ✅ Schneller Start - keine SVG-Erstellung nötig
- ✅ UI-Symbole (Emojis/Unicode) funktionieren sofort
- ✅ Später einfach durch SVGs ersetzen
- ✅ Fokus auf Funktionalität statt Design

**Nachteile:**
- ⚠️ Inkonsistentes Design (Emojis vs. SVGs)
- ⚠️ Später Refactoring nötig

**Vorgehen:**
- Verwende Unicode-Symbole/Emojis als Platzhalter
- Später durch SVGs ersetzen (einfaches Find/Replace)

**Beispiel (wie in `order-card.component.ts`):**
```typescript
const STATUS_ICONS = {
  driving: '🚀',
  stopped: '🛑',
  paused: '⏸️',
  // Später: 'shopfloor/driving.svg'
};
```

### Option B: Direkt SVGs erstellen (EMPFOHLEN für konsistentes Design)

**Vorteile:**
- ✅ Konsistentes Design von Anfang an
- ✅ Kein späteres Refactoring nötig
- ✅ Professionelleres Aussehen

**Nachteile:**
- ⚠️ Mehr Zeit für SVG-Erstellung
- ⚠️ Design-Entscheidungen nötig

**Vorgehen:**
- Erstelle alle benötigten SVGs im OMF3-Design-System
- Nutze bestehende SVGs als Vorlage

### Empfehlung: **Option A (Platzhalter) für schnellen Start**

**Begründung:**
1. Funktionalität hat Priorität
2. SVGs können später schrittweise ersetzt werden
3. Bestehende OMF3-Komponenten nutzen auch Emojis als Platzhalter (`order-card.component.ts`)

---

## 📋 Umbenennungs-Plan

### Phase 1: Neue SVGs erstellen (FEHLENDE) - ODER Platzhalter verwenden

#### Priorität HOCH (für FTS Tab)
1. `shopfloor/battery.svg` - Batteriestatus Icon
2. `shopfloor/charging-active.svg` - Aktives Laden Icon
3. `shopfloor/driving.svg` - Driving Status Icon
4. `shopfloor/stopped.svg` - Stopped Status Icon
5. `shopfloor/paused.svg` - Paused Status Icon
6. `shopfloor/load.svg` - Load Information Icon
7. `headings/fts.svg` - FTS Tab Heading

#### Priorität MITTEL (für Track&Trace Tab)
8. `shopfloor/location.svg` - Location Marker
9. `shopfloor/turn.svg` - TURN Event Icon
10. `shopfloor/pass.svg` - PASS Event Icon
11. `headings/track-trace.svg` - Track&Trace Tab Heading
12. `headings/info.svg` - Info/Help Icon
13. `headings/route.svg` - Route/Map Icon

### Phase 2: Bestehende SVGs umbenennen (OPTIONAL)

#### Option A: Konservativ (NUR neue SVGs erstellen)
- ✅ Keine Umbenennungen
- ✅ Bestehende SVGs bleiben unverändert
- ✅ Neue SVGs werden ergänzt
- **Vorteil:** Keine Breaking Changes
- **Nachteil:** Inkonsistente Namensgebung

#### Option B: Umbenennungen (EMPFOHLEN)
- 🔄 `shopfloor/robotic.svg` → `shopfloor/fts.svg`
- 🔄 `shopfloor/fuel.svg` → `shopfloor/charging.svg`
- **Vorteil:** Klarere Zuordnung, konsistente Namensgebung
- **Nachteil:** Breaking Changes (alle Referenzen müssen aktualisiert werden)

### Phase 3: Referenzen aktualisieren

Nach Umbenennungen müssen folgende Dateien aktualisiert werden:
- [ ] `omf3/apps/ccu-ui/src/app/tabs/module-tab.component.ts` (falls `robotic.svg` verwendet)
- [ ] `omf3/apps/ccu-ui/src/app/components/fts-view.component.ts` (falls vorhanden)
- [ ] Alle Tab-Komponenten, die `robotic.svg` oder `fuel.svg` verwenden
- [ ] `omf3/apps/ccu-ui/src/app/assets/icon-registry.ts` (falls vorhanden)

---

## 🎯 Empfohlene SVG-Namenskonvention

### Struktur
```
{category}/{function}-{variant}.svg
```

### Kategorien
- `shopfloor/` - Shopfloor-Module, Stationen, FTS
- `workpieces/` - Workpieces (bereits vorhanden)
- `headings/` - Tab-Headings, Section-Headings
- `details/` - Detail-Icons (bereits vorhanden)

### Beispiele
- `shopfloor/fts.svg` - FTS/AGV Icon
- `shopfloor/battery.svg` - Battery Icon
- `shopfloor/charging.svg` - Charging Station
- `shopfloor/charging-active.svg` - Active Charging
- `shopfloor/driving.svg` - Driving Status
- `shopfloor/stopped.svg` - Stopped Status
- `shopfloor/paused.svg` - Paused Status
- `shopfloor/load.svg` - Load Information
- `shopfloor/location.svg` - Location Marker
- `shopfloor/turn.svg` - TURN Event
- `shopfloor/pass.svg` - PASS Event
- `headings/fts.svg` - FTS Tab Heading
- `headings/track-trace.svg` - Track&Trace Tab Heading
- `headings/route.svg` - Route/Map Heading
- `headings/info.svg` - Info/Help Icon

---

## 📊 Mapping-Tabelle (Final - KORRIGIERT)

### ✅ Korrekturen

1. **Production Order:** `headings/maschine.svg` (bereits vorhanden) ✅
2. **Storage Order:** `headings/ladung.svg` (bereits vorhanden) ✅
3. **Platzhalter-Strategie:** Emojis/Unicode als Platzhalter, später durch SVGs ersetzen ✅

### FTS Tab Komponenten

| Komponente | Icon-Verwendung | OMF3 SVG (Platzhalter) | OMF3 SVG (Final) |
|------------|-----------------|------------------------|------------------|
| **FtsStatusComponent** | | | |
| | Heading Icon | `🚗` oder `shopfloor/robotic.svg` | `headings/fts.svg` (NEU) |
| | AGV Status Icon | `🚗` | `shopfloor/fts.svg` (NEU) |
| | Driving Status | `🚀` | `shopfloor/driving.svg` (NEU) |
| | Stopped Status | `🛑` | `shopfloor/stopped.svg` (NEU) |
| | Paused Status | `⏸️` | `shopfloor/paused.svg` (NEU) |
| | Loading Status | `📦` | `shopfloor/load.svg` (NEU) |
| **FtsBatteryComponent** | | | |
| | Heading Icon | `🔋` oder `shopfloor/robotic.svg` | `headings/fts.svg` (NEU) |
| | Battery Icon | `🔋` | `shopfloor/battery.svg` (NEU) |
| | Charging Icon | `⚡` | `shopfloor/charging-active.svg` (NEU) |
| **FtsLoadsComponent** | | | |
| | Heading Icon | `📦` oder `shopfloor/robotic.svg` | `headings/fts.svg` (NEU) |
| | Load Icon | `📦` | `shopfloor/load.svg` (NEU) |
| | Workpiece Icons | ✅ `workpieces/{color}_*.svg` | ✅ (bereits vorhanden) |
| **ShopfloorPreviewComponent** | | | |
| | Route/Map Icon | `🗺️` | `headings/route.svg` (NEU) |
| | FTS Position | `shopfloor/robotic.svg` | `shopfloor/fts.svg` (NEU) |
| | Module Icons | ✅ `shopfloor/{module}.svg` | ✅ (bereits vorhanden) |

### Track&Trace Tab Komponenten

| Komponente | Icon-Verwendung | OMF3 SVG (Platzhalter) | OMF3 SVG (Final) |
|------------|-----------------|------------------------|------------------|
| **TrackTraceComponent** | | | |
| | Heading Icon | `🔍` | `headings/track-trace.svg` (NEU) |
| | Search Icon | `🔍` | `headings/track-trace.svg` (NEU) |
| | Info Icon | `💡` | `headings/info.svg` (NEU) |
| | DOCK Event | `🔗` oder `shopfloor/robotic.svg` | `shopfloor/fts.svg` (NEU) |
| | PICK Event | ✅ `workpieces/{color}_instock_unprocessed.svg` | ✅ (bereits vorhanden) |
| | DROP Event | ✅ `workpieces/{color}_product.svg` | ✅ (bereits vorhanden) |
| | TURN Event | `↩️` | `shopfloor/turn.svg` (NEU) |
| | PASS Event | `➡️` | `shopfloor/pass.svg` (NEU) |
| | TRANSPORT Event | `🚗` oder `shopfloor/robotic.svg` | `shopfloor/fts.svg` (NEU) |
| | PROCESS Event | ✅ `shopfloor/bohrer.svg` oder `shopfloor/milling-machine.svg` | ✅ (bereits vorhanden) |
| | Storage Order | ✅ `headings/ladung.svg` | ✅ **KORRIGIERT - bereits vorhanden** |
| | Production Order | ✅ `headings/maschine.svg` | ✅ **KORRIGIERT - bereits vorhanden** |
| | Location Marker | `📍` | `shopfloor/location.svg` (NEU) |
| | Station Icons | ✅ `shopfloor/{station}.svg` | ✅ (bereits vorhanden) |

---

## ✅ Nächste Schritte

### 1. SVG-Analyse abschließen
- [ ] Prüfe ob alle benötigten SVGs vorhanden sind
- [ ] Identifiziere fehlende SVGs
- [ ] Entscheide über Umbenennungs-Strategie (Option A oder B)

### 2. SVG-Umbenennungen durchführen (falls Option B)
- [ ] `shopfloor/robotic.svg` → `shopfloor/fts.svg`
- [ ] `shopfloor/fuel.svg` → `shopfloor/charging.svg`
- [ ] Alle Referenzen aktualisieren

### 3. Neue SVGs erstellen
- [ ] Priorität HOCH: FTS Tab Icons
- [ ] Priorität MITTEL: Track&Trace Tab Icons

### 4. Komponenten-Migration starten
- [ ] Beginne mit `FtsStatusComponent`
- [ ] Ersetze alle Emojis durch OMF3-SVGs
- [ ] Teste Icon-Loading

---

## ⚠️ Breaking Changes Analyse

### Aktuelle Verwendung von `robotic.svg` und `fuel.svg`

**`shopfloor/robotic.svg` wird verwendet in:**
- `omf3/apps/ccu-ui/src/app/tabs/message-monitor-tab.component.ts` (Zeile 35, 317)
- `omf3/apps/ccu-ui/src/app/assets/icon-registry.ts` (Zeile 103: `'shopfloor-fts': 'shopfloor/robotic.svg'`)

**`shopfloor/fuel.svg` wird verwendet in:**
- `omf3/apps/ccu-ui/src/app/assets/icon-registry.ts` (Zeile 93: `'device-chrg': 'shopfloor/fuel.svg'`)

### Empfehlung: **Option A (Konservativ) - NEUE SVGs erstellen**

**Begründung:**
1. ✅ **Keine Breaking Changes:** Bestehende Referenzen bleiben funktionsfähig
2. ✅ **Rückwärtskompatibilität:** Alte Komponenten funktionieren weiterhin
3. ✅ **Klare Trennung:** Neue FTS-Features nutzen neue, spezifische Icons
4. ✅ **Einfachere Migration:** Keine Suche/Ersetze-Operationen nötig

**Vorgehen:**
- Neue SVGs mit klaren Namen erstellen (`shopfloor/fts.svg`, `shopfloor/battery.svg`, etc.)
- Bestehende `robotic.svg` und `fuel.svg` bleiben unverändert
- Neue FTS-Komponenten nutzen neue Icons
- Optional: Alte Referenzen können später schrittweise migriert werden

### Alternative: **Option B (Umbenennungen) - NUR wenn Breaking Changes akzeptabel**

**Vorgehen:**
1. `shopfloor/robotic.svg` → `shopfloor/fts.svg` kopieren (nicht verschieben!)
2. `shopfloor/fuel.svg` → `shopfloor/charging.svg` kopieren (nicht verschieben!)
3. Alle Referenzen aktualisieren:
   - `message-monitor-tab.component.ts` (2 Stellen)
   - `icon-registry.ts` (2 Stellen)
4. Alte Dateien löschen

**⚠️ Risiko:** Breaking Changes für bestehende Komponenten

---

## 🔍 Offene Fragen

1. **SVG-Umbenennungen:** ✅ **Entscheidung: Option A (konservativ)** - Neue SVGs erstellen, keine Umbenennungen
2. **Neue SVGs:** Sollen wir bestehende SVGs anpassen oder komplett neue erstellen?
3. **Icon-Style:** Sollen neue Icons im gleichen Design-System wie bestehende sein?
4. **Breaking Changes:** ✅ **Entscheidung: Vermeiden** - Option A gewählt

---

## 📋 Finale SVG-Liste (Option A - Konservativ)

### ✅ Bereits vorhandene SVGs (KEINE Änderung nötig)

- ✅ `headings/maschine.svg` - Production Order (bereits vorhanden)
- ✅ `headings/ladung.svg` - Storage Order (bereits vorhanden)
- ✅ `workpieces/{color}_*.svg` - Workpiece Icons (bereits vorhanden)
- ✅ `shopfloor/{station}.svg` - Station Icons (bereits vorhanden)
- ✅ `shopfloor/robotic.svg` - FTS Icon (als Fallback/Platzhalter)

### Neue SVGs zu erstellen (Priorität HOCH) - ODER Platzhalter verwenden

**Option: Platzhalter (Emojis/Unicode)**
- 🚗 FTS/AGV Icon
- 🚀 Driving Status
- 🛑 Stopped Status
- ⏸️ Paused Status
- 📦 Load Information
- 🔋 Battery Status
- ⚡ Charging Active

**Option: SVGs erstellen**
1. `shopfloor/fts.svg` - FTS/AGV Icon (NEU, nicht umbenennen von `robotic.svg`)
2. `shopfloor/battery.svg` - Batteriestatus Icon
3. `shopfloor/charging-active.svg` - Aktives Laden Icon
4. `shopfloor/driving.svg` - Driving Status Icon
5. `shopfloor/stopped.svg` - Stopped Status Icon
6. `shopfloor/paused.svg` - Paused Status Icon
7. `shopfloor/load.svg` - Load Information Icon
8. `headings/fts.svg` - FTS Tab Heading

### Neue SVGs zu erstellen (Priorität MITTEL) - ODER Platzhalter verwenden

**Option: Platzhalter (Emojis/Unicode)**
- 🔍 Track&Trace Icon
- 💡 Info/Help Icon
- 🗺️ Route/Map Icon
- 🔗 DOCK Event
- ↩️ TURN Event
- ➡️ PASS Event
- 📍 Location Marker

**Option: SVGs erstellen**
9. `shopfloor/location.svg` - Location Marker
10. `shopfloor/turn.svg` - TURN Event Icon
11. `shopfloor/pass.svg` - PASS Event Icon
12. `headings/track-trace.svg` - Track&Trace Tab Heading
13. `headings/info.svg` - Info/Help Icon
14. `headings/route.svg` - Route/Map Icon

### Bestehende SVGs (unverändert)

- ✅ `shopfloor/robotic.svg` - Bleibt für bestehende Komponenten
- ✅ `shopfloor/fuel.svg` - Bleibt für bestehende Komponenten (`device-chrg`)
- ✅ Alle anderen bestehenden SVGs bleiben unverändert

---

**Status:** ✅ Komponenten-Mapping abgeschlossen  
**Status:** ✅ SVG-Mapping abgeschlossen (KORRIGIERT)  
**Status:** ✅ Breaking Changes Analyse abgeschlossen  
**Status:** ✅ Production/Storage Order Icons korrigiert (`headings/maschine.svg`, `headings/ladung.svg`)  
**Entscheidung:** ✅ Option A (Konservativ) - Neue SVGs erstellen ODER Platzhalter verwenden  
**Empfehlung:** ✅ Platzhalter (Emojis) für schnellen Start, später durch SVGs ersetzen  

**Nächster Schritt:** 
- **Option 1:** Mit Platzhaltern starten → Phase 2 (FTS Tab) implementieren
- **Option 2:** SVGs erstellen → Dann Phase 2 (FTS Tab) starten

---

## ✅ Implementierungs-Status (2025-11-30)

### FTS Tab - Implementiert
- ✅ FTS Tab Komponente erstellt (`fts-tab.component.ts`)
- ✅ Integration in Navigation und Routing
- ✅ Layout: 1:2:1 Grid (Status/Battery | Route & Position | Load Information)
- ✅ AGV Status mit Current Action und Recent Actions
- ✅ Battery Status mit Details (Current Voltage, Voltage Range, Charging)
- ✅ Load Information mit 3 Slots (leer/besetzt)
- ✅ Route & Position mit Shopfloor Preview
- ✅ Action Timeline mit verketteten Punkten
- ✅ SVG Icons für Actions (TURN, DOCK, PICK, DROP, PASS, PROCESS)
- ✅ Fixtures für Mock-Mode (Startup, Mixed)
- ✅ Replay-Mode Support (keine Fixtures im Replay-Mode)

### Offene Punkte / Verbesserungen
- ⏳ FTS Animation im Shopfloor (Position wird berechnet, Animation noch nicht vollständig)
- ⏳ Route-Segmente in Orange hervorheben (teilweise implementiert)
- ⏳ Track&Trace Tab (noch nicht implementiert)
- ⏳ i18n Übersetzungen (teilweise vorhanden)

