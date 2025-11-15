# OMF3 Project Structure

**Status: VOLLSTÄNDIG DOKUMENTIERT** ✅  
**Datum: 2025-11-15  
**Architektur: Angular-basierte Architektur mit Nx Workspace**  
**OMF3 Dashboard: IN ENTWICKLUNG** 🚧

## 🎯 Übersicht

Das OMF3 Projekt folgt einer **Angular-basierten Architektur** mit klarer Trennung der Verantwortlichkeiten über mehrere Libraries:

```
┌─────────────────────┐
│   MQTT Broker       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  MQTT CLIENT        │  ← Transport Layer (WebSocket)
│  - WebSocketMqttAdapter│
│  - MockMqttAdapter  │
│  - ConnectionService│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  GATEWAY          │  ← Validation & Routing Layer
│  - Topic Mapping  │
│  - Type Conversion│
│  - Error Handling │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  BUSINESS          │  ← Business Logic Layer
│  - State Aggregation│
│  - Derived Streams │
│  - Business Rules  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  ANGULAR UI        │  ← Presentation Layer
│  - Components      │
│  - Services        │
│  - MessageMonitor  │
└─────────────────────┘
```

## 📁 Detaillierte Projektstruktur

```
omf3/
├── apps/
│   └── ccu-ui/                      # 🚀 Angular Dashboard Application
│       ├── src/
│       │   ├── app/
│       │   │   ├── app.component.ts  # Main App Component
│       │   │   ├── app.routes.ts     # Routing Configuration
│       │   │   ├── services/         # Angular Services
│       │   │   │   ├── connection.service.ts      # MQTT Connection Management
│       │   │   │   ├── environment.service.ts      # Environment (Mock/Live/Replay)
│       │   │   │   ├── language.service.ts        # I18n Language Switching
│       │   │   │   ├── message-monitor.service.ts # Message Monitor (State Persistence)
│       │   │   │   └── role.service.ts            # Role Management
│       │   │   ├── components/       # Reusable Components
│       │   │   │   ├── order-card/   # Order Card Component
│       │   │   │   └── shopfloor-preview/ # Shopfloor Preview Component
│       │   │   ├── tabs/             # Dashboard Tabs
│       │   │   │   ├── overview-tab.component.ts
│       │   │   │   ├── order-tab.component.ts
│       │   │   │   ├── process-tab.component.ts
│       │   │   │   ├── configuration-tab.component.ts
│       │   │   │   ├── module-tab.component.ts
│       │   │   │   ├── sensor-tab.component.ts
│       │   │   │   └── message-monitor-tab.component.ts
│       │   │   └── mock-dashboard.ts # Dashboard Controller (Mock/Live/Replay)
│       │   ├── locale/               # 🌐 I18n Translation Files
│       │   │   ├── messages.de.json  # German Translations
│       │   │   └── messages.fr.json  # French Translations
│       │   ├── main.ts               # Application Bootstrap
│       │   └── styles.scss           # Global Styles
│       ├── public/                   # Static Assets
│       │   ├── headings/             # Heading SVG Icons
│       │   │   ├── zentral.svg
│       │   │   ├── dezentral_1.svg
│       │   │   └── ...
│       │   ├── shopfloor/            # Shopfloor SVG Icons
│       │   │   ├── shopfloor_layout.json
│       │   │   ├── robotic.svg
│       │   │   └── ...
│       │   ├── workpieces/           # Workpiece SVG Icons
│       │   └── locale/               # Locale Files (copied to dist)
│       │       ├── messages.de.json
│       │       └── messages.fr.json
│       └── project.json              # Nx Project Configuration
│
├── libs/
│   ├── mqtt-client/                  # 📡 MQTT Client Library
│   │   ├── src/
│   │   │   ├── index.ts              # Public API
│   │   │   ├── mqtt-client.ts        # MqttClientWrapper
│   │   │   ├── websocket-adapter.ts  # WebSocketMqttAdapter
│   │   │   └── mock-adapter.ts       # MockMqttAdapter
│   │   └── README.md
│   │
│   ├── gateway/                      # 🚪 Gateway Library
│   │   ├── src/
│   │   │   ├── index.ts              # Public API
│   │   │   └── gateway.ts            # createGateway() - Topic Mapping
│   │   └── README.md
│   │
│   ├── business/                     # 💼 Business Logic Library
│   │   ├── src/
│   │   │   ├── index.ts              # Public API
│   │   │   └── business.ts           # createBusiness() - Derived Streams
│   │   └── README.md
│   │
│   ├── entities/                     # 📦 Entity Types Library
│   │   ├── src/
│   │   │   └── index.ts              # Type Definitions (Order, Module, FTS, etc.)
│   │   └── tsconfig.lib.json
│   │
│   └── testing-fixtures/             # 🧪 Testing Fixtures Library
│       ├── src/
│       │   ├── index.ts              # Public API
│       │   └── order-fixtures.ts     # createOrderFixtureStream()
│       └── README.md
│
└── testing/
    └── fixtures/                     # 📋 Test Fixtures (JSON/JSONL)
        ├── orders/                   # Order Fixtures
        │   ├── blue/
        │   ├── red/
        │   ├── white/
        │   └── mixed/
        ├── modules/                  # Module Fixtures
        ├── sensors/                  # Sensor Fixtures
        ├── flows/                    # Flow Fixtures
        └── config/                   # Config Fixtures
```

## 🏗️ Architektur-Komponenten

### **🔌 MQTT CLIENT LAYER (Transport)**

**Verantwortlichkeiten:**
- WebSocket-basierte MQTT-Kommunikation
- Connection State Management
- Message Publishing/Subscribing
- Mock Adapter für Testing/Replay

**Implementierung:**
```typescript
// omf3/libs/mqtt-client/src/mqtt-client.ts
export interface MqttClientWrapper {
  connect(url: string): Promise<void>;
  subscribe(topic: string): Promise<void>;
  publish(topic: string, payload: unknown): Promise<void>;
  messages$: Observable<MqttMessage>;
  connectionState$: Observable<ConnState>;
}
```

**Adapters:**
- `WebSocketMqttAdapter`: Echte MQTT-Verbindung über WebSocket
- `MockMqttAdapter`: Mock für Testing/Replay

### **🚪 GATEWAY LAYER (Validation & Routing)**

**Verantwortlichkeiten:**
- Topic-basierte Message-Routing
- Type Conversion (Raw → Typed Entities)
- Error Handling

**Implementierung:**
```typescript
// omf3/libs/gateway/src/gateway.ts
export interface GatewayStreams {
  orders$: Observable<OrderActive>;
  stock$: Observable<StockMessage>;
  modules$: Observable<ModuleState>;
  fts$: Observable<FtsState>;
}
```

### **💼 BUSINESS LAYER (Business Logic)**

**Verantwortlichkeiten:**
- State Aggregation
- Derived Streams (Order Counts, Stock Levels, etc.)
- Business Rules

**Implementierung:**
```typescript
// omf3/libs/business/src/business.ts
export interface BusinessStreams {
  orderCounts$: Observable<OrderCounts>;
  stockByPart$: Observable<StockByPart>;
  moduleStates$: Observable<ModuleStates>;
  ftsStates$: Observable<FtsStates>;
}
```

### **🖥️ ANGULAR UI LAYER (Presentation)**

**Verantwortlichkeiten:**
- Component Rendering
- User Interaction
- Message Monitor (State Persistence)
- I18n Language Switching

**Services:**
- `ConnectionService`: MQTT Connection Management
- `EnvironmentService`: Environment (Mock/Live/Replay) Management
- `LanguageService`: I18n Language Switching
- `MessageMonitorService`: Message State Persistence (BehaviorSubject + CircularBuffer)

**Components:**
- Tab Components: Overview, Order, Process, Configuration, Module, Sensor, Message Monitor
- Reusable Components: Order Card, Shopfloor Preview

## 🔄 Data Flow

```
MQTT Broker
    ↓ (WebSocket)
MqttClientWrapper (mqtt-client)
    ↓ (Raw Messages)
Gateway (gateway)
    ↓ (Typed Entities)
Business (business)
    ↓ (Derived Streams)
Angular Components (ccu-ui)
    ↓ (User Interaction)
MessageMonitorService (State Persistence)
```

## 📦 Nx Workspace

**Commands:**
```bash
# Development
nx serve ccu-ui                    # Start Development Server
nx serve ccu-ui --configuration=development  # With locale support

# Testing
nx test ccu-ui                    # Run Tests
nx test mqtt-client               # Test MQTT Client
nx test gateway                  # Test Gateway
nx test business                 # Test Business

# Building
nx build ccu-ui                   # Build Production Bundle
nx build ccu-ui --configuration=production  # Multi-locale Build

# Graph
nx graph                          # Dependency Graph
```

## 🌐 I18n (Internationalization)

**Locales:**
- `en`: English (Source Locale)
- `de`: German
- `fr`: French

**Translation Files:**
- `omf3/apps/ccu-ui/src/locale/messages.<locale>.json`
- Copied to `public/locale/` for development builds

**Usage:**
```typescript
// In Components
$localize`:@@navOverview:Overview`
```

## 🧪 Testing

**Test Structure:**
- Unit Tests: `*.spec.ts` files alongside source files
- Integration Tests: `omf3/testing/fixtures/` for replay data

**Test Commands:**
```bash
nx test ccu-ui                    # Run all ccu-ui tests
nx test mqtt-client               # Run mqtt-client tests
nx test gateway                   # Run gateway tests
nx test business                  # Run business tests
```

## 📝 Notes

- **Nx Workspace**: Monorepo-Struktur für bessere Code-Organisation
- **RxJS**: Reactive Programming mit Observables
- **TypeScript**: Type Safety über alle Libraries
- **Angular**: Modern UI Framework mit Component-based Architecture
- **MessageMonitorService**: State Persistence für sofortige Datenanzeige

---

*Letzte Aktualisierung: 2025-11-15*
