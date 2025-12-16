# SVG Icon Guide für DSP Animation System

## 📁 SVG-Verzeichnisstruktur

SVG-Icons sind in `omf3/apps/ccu-ui/src/assets/svg/` organisiert:

```
assets/svg/
├── shopfloor/
│   ├── stations/          # Device-Icons (physische Maschinen/Stationen)
│   │   ├── drill-station.svg
│   │   ├── mill-station.svg
│   │   ├── laser-station.svg      # ← Neue Device-SVGs hier
│   │   ├── cnc-station.svg        # ← Neue Device-SVGs hier
│   │   ├── printer-3d-station.svg # ← Neue Device-SVGs hier
│   │   ├── robot-arm-station.svg  # ← Neue Device-SVGs hier
│   │   └── warehouse-station.svg  # ← Neue Device-SVGs hier
│   │
│   ├── systems/           # System-Icons (Software-Systeme)
│   │   ├── agv-system.svg
│   │   ├── any-system.svg
│   │   ├── bp-system.svg
│   │   └── warehouse-system.svg
│   │
│   └── shared/            # Geteilte Icons (für Devices UND Systems)
│       └── agv-vehicle.svg
│
├── business/              # Business Application Icons
│   ├── erp-application.svg
│   ├── mes-application.svg
│   └── ...
│
└── brand/                # Brand/Provider Logos
    ├── sap-logo.svg
    └── ...
```

## 🎯 Neue Device-SVGs hinzufügen

### Schritt 1: SVG-Datei ablegen
**Pfad:** `omf3/apps/ccu-ui/src/assets/svg/shopfloor/stations/`
- Beispiel: `laser-station.svg`, `cnc-station.svg`, `printer-3d-station.svg`, etc.

### Schritt 2: IconKey zum Type hinzufügen
**Datei:** `omf3/apps/ccu-ui/src/app/components/dsp-animation/configs/types.ts`

```typescript
export type GenericIconKey = 
  // Devices
  | 'drill' | 'mill' | 'oven' | 'laser' | 'cnc' | 'printer-3d' 
  | 'robot-arm' | 'conveyor' | 'warehouse' | 'agv' | 'hbw'
  | 'my-new-device'  // ← Hier hinzufügen
```

### Schritt 3: Icon in Icon-Registry registrieren
**Datei:** `omf3/apps/ccu-ui/src/app/assets/icon-registry.ts`

```typescript
// Generic device icons
'generic-device-laser': 'assets/svg/shopfloor/stations/laser-station.svg',
'generic-device-cnc': 'assets/svg/shopfloor/stations/cnc-station.svg',
'generic-device-printer-3d': 'assets/svg/shopfloor/stations/printer-3d-station.svg',
'generic-device-robot-arm': 'assets/svg/shopfloor/stations/robot-arm-station.svg',
'generic-device-warehouse': 'assets/svg/shopfloor/stations/warehouse-station.svg',
```

**Wichtig:** Der IconKey muss auch zum `IconKey` Type hinzugefügt werden (falls noch nicht vorhanden).

### Schritt 4: In Customer-Config verwenden
```typescript
{
  id: 'sf-device-1',
  label: 'Laser Cutting Station',
  iconKey: 'laser',  // Wird automatisch zu generic-device-laser gemappt
}
```

## 🔄 Duplikate vermeiden

### Regel 1: Klare Trennung Devices vs. Systems
- **Devices** (physische Maschinen) → `stations/`
- **Systems** (Software-Systeme) → `systems/`
- **Geteilte Icons** (beide Verwendungen) → `shared/`

### Regel 2: Wenn das gleiche SVG für Devices UND Systems verwendet wird

**Option A: In `shared/` ablegen (empfohlen)**
```
shared/
  └── warehouse.svg  # Wird für Devices UND Systems verwendet
```

Dann in `icon-registry.ts`:
```typescript
// Für Devices
'generic-device-warehouse': 'assets/svg/shopfloor/shared/warehouse.svg',

// Für Systems  
'shopfloor-warehouse': 'assets/svg/shopfloor/shared/warehouse.svg',
'generic-system-warehouse-system': 'assets/svg/shopfloor/shared/warehouse.svg',
```

**Option B: In einem Ordner ablegen und referenzieren**
```
systems/
  └── warehouse-system.svg  # Original
```

Dann in `icon-registry.ts`:
```typescript
// Für Devices: Auf das gleiche SVG verweisen
'generic-device-warehouse': 'assets/svg/shopfloor/systems/warehouse-system.svg',

// Für Systems: Auf das gleiche SVG verweisen
'shopfloor-warehouse': 'assets/svg/shopfloor/systems/warehouse-system.svg',
```

### Regel 3: Namenskonvention
- **Device-SVGs:** `*-station.svg` (z.B. `laser-station.svg`, `cnc-station.svg`)
- **System-SVGs:** `*-system.svg` (z.B. `warehouse-system.svg`, `agv-system.svg`)
- **Geteilte SVGs:** Neutraler Name (z.B. `warehouse.svg`, `agv-vehicle.svg`)

## 📝 Beispiel: Warehouse SVG für Devices hinzufügen

**Aktueller Stand:**
- `warehouse-system.svg` existiert in `systems/` (für Systems)
- `generic-device-warehouse` zeigt auf `hbw-station.svg` (Fallback)

**Lösung (wenn neues Device-SVG erstellt wird):**

1. **Neue Datei:** `assets/svg/shopfloor/stations/warehouse-station.svg`
2. **Icon-Registry aktualisieren:**
   ```typescript
   'generic-device-warehouse': 'assets/svg/shopfloor/stations/warehouse-station.svg',
   ```

**ODER (wenn das gleiche SVG verwendet werden soll):**

1. **Bestehende Datei verwenden:** `assets/svg/shopfloor/systems/warehouse-system.svg`
2. **Icon-Registry aktualisieren:**
   ```typescript
   'generic-device-warehouse': 'assets/svg/shopfloor/systems/warehouse-system.svg',
   ```

## ✅ Checkliste für neue Device-SVGs

- [ ] SVG-Datei in `assets/svg/shopfloor/stations/` abgelegt
- [ ] IconKey zu `GenericIconKey` in `types.ts` hinzugefügt
- [ ] Icon zu `ICON_MAP` in `icon-registry.ts` hinzugefügt (Format: `generic-device-<iconKey>`)
- [ ] IconKey zu `IconKey` Type hinzugefügt (falls noch nicht vorhanden)
- [ ] In Customer-Config getestet

## 🔍 Bestehende Fallbacks ersetzen

Aktuell werden Fallbacks verwendet:
- `laser` → `mill-station.svg` (Fallback)
- `cnc` → `mill-station.svg` (Fallback)
- `printer-3d` → `mixer.svg` (Fallback)
- `robot-arm` → `chrg-station.svg` (aktuell verwendet)
- `warehouse` → `hbw-station.svg` (Fallback)

Um diese zu ersetzen:
1. Neue SVG-Dateien in `stations/` erstellen
2. Icon-Registry aktualisieren (Fallback-Kommentare entfernen)
3. Tests durchführen
