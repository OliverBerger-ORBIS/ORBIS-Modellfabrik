# 🎯 GitHub Anforderung: DPS & AIQS Example App

**Datum:** 2025-12-16  
**Zweck:** Erstellung einer Example-App basierend auf DPS und AIQS Session-Daten

---

## 📋 Übersicht

Basierend auf den analysierten Session-Daten sollen zwei Example-Apps erstellt werden, die **als Tabs in OMF3 integriert werden**:

1. **DPS Tab** - Delivery & Pickup Station (Serial: `SVR4H73275`)
2. **AIQS Tab** - AI Quality System (Serial: `SVR4H76530`)

**⚠️ WICHTIG:** Die Apps sollen als Tabs in OMF3 integriert werden, ähnlich wie das **FTS/AGV Tab**. Sie sollen die gleichen Services verwenden und ORBIS-CI Vorgaben berücksichtigen.

---

## 📊 Datenquellen

**⚠️ WICHTIG:** Alle 13 Session-Dateien wurden analysiert. Die Daten enthalten alle möglichen Abläufe.

**Siehe:** `ANALYSIS_SUMMARY.md` für vollständige Übersicht.

### DPS-Analyse-Daten
**Verzeichnis:** `data/osf-data/dps-analysis/`

**Gesamt-Statistik:**
- **13 Sessions analysiert**
- **Commands:** PICK (60x), DROP (61x), INPUT_RGB (18x), RGB_NFC (21x)
- **STORAGE-ORDER Kontext:** 423 Messages (aus 3 Sessions: blue, red, white)
- **PRODUCTION-ORDER Kontext:** 532 Messages (aus 4 Sessions: blue, bwr, red, white)

**Wichtige Dateien:**
- `{session_name}_all_dps_messages.json` - Alle DPS-relevanten Messages
- `{session_name}_storage_order_context.json` - STORAGE-ORDER Kontext (Farberkennung, NFC) - **3 Sessions verfügbar**
- `{session_name}_production_order_context.json` - PRODUCTION-ORDER Kontext (NFC-Auslesen) - **4 Sessions verfügbar**
- `{session_name}_dps_state.json` - DPS State Updates
- `{session_name}_dps_order.json` - DPS Order Commands
- `{session_name}_metadata.json` - Metadaten und Statistiken

### AIQS-Analyse-Daten
**Verzeichnis:** `data/osf-data/aiqs-analysis/`

**Gesamt-Statistik:**
- **13 Sessions analysiert**
- **Commands:** CHECK_QUALITY (53x), PICK (16x), DROP (18x)
- **CHECK_QUALITY Ergebnisse:** 53 (PASSED/FAILED)
- **CHECK_QUALITY Kontext:** 1,113 Messages (Photo, ML, Mustererkennung)

**Wichtige Dateien:**
- `{session_name}_all_aiqs_messages.json` - Alle AIQS-relevanten Messages
- `{session_name}_check_quality_context.json` - CHECK_QUALITY Kontext (Photo, ML, Mustererkennung) - **10 Sessions verfügbar**
- `{session_name}_check_quality_results.json` - CHECK_QUALITY Ergebnisse (PASSED/FAILED) - **10 Sessions verfügbar**
- `{session_name}_aiqs_state.json` - AIQS State Updates
- `{session_name}_aiqs_order.json` - AIQS Order Commands
- `{session_name}_metadata.json` - Metadaten und Statistiken

---

## 🎯 DPS Example App - Anforderungen

### Funktionale Anforderungen

#### 1. STORAGE-ORDER Flow
**Zweck:** Werkstück wird in das System eingelagert

**Flow:**
1. **Farberkennung:** `INPUT_RGB` Command erkennt Farbe des Werkstücks (WHITE/BLUE/RED)
2. **NFC-Auslesen:** `RGB_NFC` Command liest NFC-Code des Werkstücks
3. **Order-Erstellung:** CCU erstellt STORAGE-ORDER basierend auf Farbe und NFC-Code

**Relevante Topics:**
- `module/v1/ff/SVR4H73275/order` - DPS Order Commands (`INPUT_RGB`, `RGB_NFC`)
- `module/v1/ff/SVR4H73275/state` - DPS State Updates (enthält Farbe und NFC-Code)
- `module/v1/ff/NodeRed/SVR4H73275/state` - NodeRed enriched State (mit orderId)
- `ccu/order/request` - CCU Order Request (mit `orderType: "STORAGE"`)
- `ccu/order/active` - CCU Active Order
- `/j1/txt/1/f/i/stock` - DPS Stock Information
- `/j1/txt/1/i/cam` - DPS Camera Data

**Wichtige Payload-Felder:**
- `action.command`: `"INPUT_RGB"` oder `"RGB_NFC"`
- `action.metadata.type`: Farbe (`"WHITE"`, `"BLUE"`, `"RED"`)
- `action.metadata.workpieceId`: NFC-Code (14-stelliger Hex-String)
- `actionState.result`: `"PASSED"` oder `"FAILED"`

#### 2. PRODUCTION-ORDER Flow
**Zweck:** Werkstück wird nach Produktion verifiziert

**Flow:**
1. **Produktion:** Werkstück durchläuft Produktionsprozess
2. **NFC-Auslesen:** Nach PRODUCTION-ORDER wird NFC-Code erneut ausgelesen
3. **Verifikation:** NFC-Code wird verifiziert (gleicher Code wie vorher)

**Relevante Topics:**
- `module/v1/ff/SVR4H73275/order` - DPS Order Commands (`RGB_NFC`)
- `module/v1/ff/SVR4H73275/state` - DPS State Updates (enthält NFC-Code)
- `ccu/order/completed` - CCU Completed Order (enthält `orderType: "PRODUCTION"`)
- `ccu/order/active` - CCU Active Order

**Wichtige Payload-Felder:**
- `action.command`: `"RGB_NFC"`
- `action.metadata.workpieceId`: NFC-Code
- `actionState.result`: `"PASSED"` oder `"FAILED"`

#### 3. Connection & Availability
**Zweck:** Modul-Status überwachen

**Relevante Topics:**
- `module/v1/ff/SVR4H73275/connection` - DPS Connection Status
- `module/v1/ff/NodeRed/SVR4H73275/connection` - NodeRed enriched Connection
- `ccu/pairing/state` - CCU Pairing State (enthält DPS Info)

**Wichtige Payload-Felder:**
- `connectionState`: `"ONLINE"` oder `"OFFLINE"`
- `available`: `"READY"`, `"BUSY"`, `"ERROR"`
- `connected`: `true` oder `false`

### Technische Anforderungen

- **MQTT-Client:** Subscribe zu allen relevanten Topics
- **Message-Parsing:** JSON-Payloads parsen und strukturieren
- **State-Management:** DPS State verfolgen (Connection, Availability, Commands)
- **UI:** Visualisierung von:
  - Connection Status
  - Availability Status
  - Aktuelle Commands (INPUT_RGB, RGB_NFC, PICK, DROP)
  - Farbe des Werkstücks
  - NFC-Code
  - Order Status (STORAGE/PRODUCTION)

---

## 🎯 AIQS Example App - Anforderungen

### Funktionale Anforderungen

#### 1. CHECK_QUALITY Flow
**Zweck:** Qualitätsprüfung von Werkstücken mittels ML-basierter Mustererkennung

**Flow:**
1. **PICK:** Werkstück wird aufgenommen
2. **Photo:** AIQS macht ein Photo vom Werkstück
3. **ML-Analyse:** Mustererkennung prüft Qualität anhand von Mustern
4. **Ergebnis:** PASSED oder FAILED wird zurückgegeben
5. **DROP:** Werkstück wird abgelegt (oder verworfen bei FAILED)

**Relevante Topics:**
- `module/v1/ff/SVR4H76530/order` - AIQS Order Commands (`PICK`, `CHECK_QUALITY`, `DROP`)
- `module/v1/ff/SVR4H76530/state` - AIQS State Updates (enthält CHECK_QUALITY Ergebnis)
- `module/v1/ff/NodeRed/SVR4H76530/state` - NodeRed enriched State (mit orderId)
- `ccu/order/completed` - CCU Completed Order (enthält CHECK_QUALITY Ergebnisse)
- `/j1/txt/1/i/bme680` - AIQS Environmental Sensor (BME680)

**Wichtige Payload-Felder:**
- `action.command`: `"CHECK_QUALITY"`
- `actionState.command`: `"CHECK_QUALITY"`
- `actionState.result`: `"PASSED"` oder `"FAILED"`
- `actionState.state`: `"FINISHED"` oder `"ERROR"`
- `actionState.id`: Action ID (UUID)
- `orderId`: Order ID (UUID)
- `workpieceId`: NFC-Code des Werkstücks

#### 2. Production Flow Integration
**Zweck:** CHECK_QUALITY ist Teil des Production-Order-Flows

**Flow:**
1. Werkstück durchläuft Produktionsprozess (DRILL, MILL)
2. Werkstück kommt zu AIQS
3. AIQS führt CHECK_QUALITY durch
4. Bei PASSED: Order wird fortgesetzt
5. Bei FAILED: Order wird abgebrochen (ERROR State)

**Relevante Topics:**
- `ccu/order/active` - CCU Active Order
- `ccu/order/completed` - CCU Completed Order (enthält `productionSteps` mit CHECK_QUALITY)
- `ccu/order/request` - CCU Order Request

**Wichtige Payload-Felder:**
- `orderType`: `"PRODUCTION"`
- `productionSteps`: Array von Steps (enthält CHECK_QUALITY Step)
- `state`: `"FINISHED"`, `"ERROR"`, `"CANCELLED"`

#### 3. Connection & Availability
**Zweck:** Modul-Status überwachen

**Relevante Topics:**
- `module/v1/ff/SVR4H76530/connection` - AIQS Connection Status
- `module/v1/ff/NodeRed/SVR4H76530/connection` - NodeRed enriched Connection
- `ccu/pairing/state` - CCU Pairing State (enthält AIQS Info)

**Wichtige Payload-Felder:**
- `connectionState`: `"ONLINE"` oder `"OFFLINE"`
- `available`: `"READY"`, `"BUSY"`, `"ERROR"`
- `connected`: `true` oder `false`

### Technische Anforderungen

- **MQTT-Client:** Subscribe zu allen relevanten Topics
- **Message-Parsing:** JSON-Payloads parsen und strukturieren
- **State-Management:** AIQS State verfolgen (Connection, Availability, CHECK_QUALITY Ergebnisse)
- **UI:** Visualisierung von:
  - Connection Status
  - Availability Status
  - Aktuelle Commands (PICK, CHECK_QUALITY, DROP)
  - CHECK_QUALITY Ergebnisse (PASSED/FAILED)
  - Order Status
  - Workpiece ID (NFC-Code)
  - Photo-Status (wenn verfügbar)

---

## 📝 Datenformat

### Message-Format
```json
{
  "timestamp": "2025-11-10T18:16:47.562237",
  "topic": "module/v1/ff/SVR4H73275/state",
  "payload": "{...}",
  "qos": 2
}
```

### Payload-Format (Beispiel DPS State)
```json
{
  "serialNumber": "SVR4H73275",
  "timestamp": "2025-11-10T17:01:07.544758Z",
  "actionState": {
    "command": "RGB_NFC",
    "state": "FINISHED",
    "result": "PASSED",
    "id": "4db0d5dc-3841-4f92-85e1-fde21f9a569d",
    "timestamp": "2025-11-10T17:01:07.544476Z"
  },
  "actionStates": [
    {
      "command": "PICK",
      "metadata": {
        "workpiece": {
          "type": "RED",
          "workpieceId": "04d78cca341290",
          "state": "PROCESSED"
        }
      },
      "state": "FINISHED",
      "result": "PASSED"
    }
  ],
  "orderId": "c9da720e-98e6-4d96-84d3-7baad5c5383d",
  "orderUpdateId": 11
}
```

### Payload-Format (Beispiel AIQS CHECK_QUALITY)
```json
{
  "serialNumber": "SVR4H76530",
  "timestamp": "2025-11-10T17:00:24.896410Z",
  "actionState": {
    "command": "CHECK_QUALITY",
    "result": "PASSED",
    "id": "b361aca3-dece-46ba-b07e-a360600c2516",
    "timestamp": "2025-11-10T17:00:24.895445Z",
    "state": "FINISHED"
  },
  "orderUpdateId": 10,
  "orderId": "c9da720e-98e6-4d96-84d3-7baad5c5383d"
}
```

---

## 🚀 Erwartete Features

### DPS Example App
- ✅ MQTT-Client mit Topic-Subscription
- ✅ STORAGE-ORDER Flow Visualisierung
- ✅ PRODUCTION-ORDER Flow Visualisierung
- ✅ Farberkennung (INPUT_RGB) Anzeige
- ✅ NFC-Code (RGB_NFC) Anzeige
- ✅ Connection & Availability Status
- ✅ Command-History
- ✅ Order-Status Tracking

### AIQS Example App
- ✅ MQTT-Client mit Topic-Subscription
- ✅ CHECK_QUALITY Flow Visualisierung
- ✅ CHECK_QUALITY Ergebnisse (PASSED/FAILED) Anzeige
- ✅ Photo-Status (wenn verfügbar)
- ✅ ML-Analyse Status
- ✅ Connection & Availability Status
- ✅ Command-History
- ✅ Order-Status Tracking

---

## 📚 Zusätzliche Informationen

### Dokumentation
- **DPS-Analyse README:** `data/osf-data/dps-analysis/README.md`
- **AIQS-Analyse README:** `data/osf-data/aiqs-analysis/README.md`
- **MQTT Topic Conventions:** `docs/06-integrations/00-REFERENCE/mqtt-topic-conventions.md`
- **MQTT Message Examples:** `docs/06-integrations/00-REFERENCE/mqtt-message-examples.md`

### Serial IDs
- **DPS:** `SVR4H73275`
- **AIQS:** `SVR4H76530`

### Wichtige Topics
- **DPS:** `module/v1/ff/SVR4H73275/*`, `module/v1/ff/NodeRed/SVR4H73275/*`
- **AIQS:** `module/v1/ff/SVR4H76530/*`, `module/v1/ff/NodeRed/SVR4H76530/*`
- **CCU Orders:** `ccu/order/*`
- **CCU Pairing:** `ccu/pairing/state`
- **CCU Calibration:** `ccu/state/calibration/{serialId}`, `ccu/set/calibration`

---

## 🔗 OMF3 Integration

### Tab-Integration

Die Example-Apps sollen **als Tabs in OMF3 integriert werden**, ähnlich wie das **FTS/AGV Tab**.

**Referenz:** `omf3/apps/ccu-ui/src/app/tabs/fts-tab.component.ts`

### Verwendete Services (wie im FTS Tab)

Die Tabs sollen die **gleichen Services** verwenden wie das FTS Tab:

1. **MessageMonitorService**
   - Für MQTT-Message-Monitoring
   - `getLastMessage(topic)` - Letzte Message zu einem Topic
   - `getMessagesByTopic(topic)` - Alle Messages zu einem Topic
   - Pattern: `shareReplay({ bufferSize: 1, refCount: false })` für persistente Streams

2. **ConnectionService**
   - Für MQTT-Verbindung
   - `publish(topic, payload, qos)` - Messages senden
   - `isConnected$` - Connection Status

3. **ShopfloorMappingService**
   - Für Serial-ID ↔ Modul-Typ ↔ Cell-ID Mapping
   - `getModuleBySerial(serialId)` - Modul-Info aus Serial-ID
   - `getModuleIcon(serialId)` - Icon aus Serial-ID
   - `initializeLayout(layout)` - Layout initialisieren

4. **ModuleNameService**
   - Für Modul-Namen (i18n)
   - `getModuleDisplayText(moduleType, format)` - Lokalisierte Modul-Namen

5. **EnvironmentService**
   - Für Environment-Info (MOCK, REPLAY, LIVE)
   - `current.key` - Aktuelles Environment

6. **LanguageService**
   - Für Sprach-Umschaltung
   - `currentLanguage$` - Aktuelle Sprache

### Tab-Struktur (analog zu FTS Tab)

```typescript
@Component({
  standalone: true,
  selector: 'app-dps-tab', // oder 'app-aiqs-tab'
  imports: [CommonModule, ShopfloorPreviewComponent],
  templateUrl: './dps-tab.component.html',
  styleUrl: './dps-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DpsTabComponent implements OnInit, OnDestroy {
  constructor(
    private readonly messageMonitor: MessageMonitorService,
    private readonly environmentService: EnvironmentService,
    private readonly connectionService: ConnectionService,
    private readonly moduleNameService: ModuleNameService,
    private readonly mappingService: ShopfloorMappingService,
    private readonly cdr: ChangeDetectorRef,
  ) {}
}
```

### Routing

Die Tabs müssen in `app.routes.ts` registriert werden:

```typescript
{
  path: 'dps',
  loadComponent: () => import('./tabs/dps-tab.component').then(m => m.DpsTabComponent),
},
{
  path: 'aiqs',
  loadComponent: () => import('./tabs/aiqs-tab.component').then(m => m.AiqsTabComponent),
},
```

### ORBIS-CI Vorgaben

1. **TypeScript:** Strikte Typisierung, keine `any` ohne Begründung
2. **ESLint:** Alle Linting-Regeln müssen erfüllt sein
3. **RxJS:** Observable Patterns korrekt verwenden (`shareReplay`, `refCount: false` für persistente Streams)
4. **Angular:** Component-basierte Architektur, Services für Business Logic
5. **i18n:** `$localize` für Übersetzungen verwenden
6. **SVG Icons:** OMF3 SVG-Pfade verwenden (`assets/svg/...`)
7. **Change Detection:** `ChangeDetectionStrategy.OnPush` verwenden
8. **Tests:** Unit Tests für alle Komponenten und Services

### Dateistruktur

```
omf3/apps/ccu-ui/src/app/
├── tabs/
│   ├── dps-tab.component.ts          # NEU: DPS Tab
│   ├── dps-tab.component.html
│   ├── dps-tab.component.scss
│   ├── aiqs-tab.component.ts          # NEU: AIQS Tab
│   ├── aiqs-tab.component.html
│   └── aiqs-tab.component.scss
├── components/
│   ├── dps-status/                   # Optional: DPS-spezifische Komponenten
│   └── aiqs-quality/                 # Optional: AIQS-spezifische Komponenten
└── services/
    ├── dps-data.service.ts           # Optional: DPS State Management
    └── aiqs-data.service.ts          # Optional: AIQS State Management
```

### UI-Standards

- **Headings:** SVG Icons aus `assets/svg/ui/heading-*.svg`
- **Module Icons:** SVG Icons aus `assets/svg/shopfloor/stations/*.svg`
- **Workpiece Icons:** SVG Icons aus `assets/svg/workpieces/*.svg`
- **Design:** Konsistent mit anderen Tabs (FTS Tab als Referenz)
- **i18n:** Alle Texte mit `$localize` versehen (DE, EN, FR)

## ✅ Erfolgskriterien

1. **Funktionalität:** Beide Tabs können MQTT-Messages empfangen und verarbeiten
2. **Visualisierung:** Alle wichtigen States und Commands werden angezeigt
3. **Datenverarbeitung:** Payloads werden korrekt geparst und strukturiert
4. **OMF3 Integration:** Tabs sind in OMF3 integriert (Routing, Services, UI)
5. **Services:** Verwendet die gleichen Services wie FTS Tab
6. **ORBIS-CI:** Erfüllt alle ORBIS-CI Vorgaben (TypeScript, ESLint, RxJS, Angular)
7. **Dokumentation:** Code ist dokumentiert und nachvollziehbar
8. **Beispiele:** Verwendet echte Daten aus den Session-Analysen

---

## 📝 Hinweise

- Alle Daten sind im JSON-Format
- Payloads sind als JSON-Strings gespeichert (müssen mit `json.loads()` geparst werden)
- Timestamps sind im ISO-Format
- Die Daten enthalten keine großen Binärdaten (Photos werden nicht gespeichert, nur Metadaten)
- Connection und Availability werden extrahiert, auch wenn sie bereits ausgewertet werden
