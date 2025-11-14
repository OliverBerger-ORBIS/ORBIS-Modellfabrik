# PR-17: Message Monitor Service Implementation

## 🎯 Problem Statement

Aktuell haben wir zwei Probleme mit MQTT-Message-Handling:

1. **Sofortige Verfügbarkeit:** Späte Subscriber bekommen nur neue Messages, nicht die letzte. Aktuell verwendet `Gateway` `shareReplay(1)`, aber das funktioniert nicht zuverlässig für alle Use-Cases.

2. **Historie fehlt:** Es gibt keine Möglichkeit, historische Messages pro Topic abzurufen. Das ist wichtig für:
   - Debugging
   - Monitoring
   - UI-Komponenten, die beim Tab-Wechsel die letzten Werte anzeigen sollen

## 📋 Requirements

### Core Features
1. **BehaviorSubject pro Topic:** Sofortige Verfügbarkeit des letzten Payloads
2. **CircularBuffer pro Topic:** Historie mit Rollover (konfigurierbare Retention)
3. **Schema-Validierung:** JSON-Schema-Validierung aus Registry (wie OMF2)
4. **Persistenz:** localStorage für kleine Payloads, IndexedDB für große Historien
5. **Multi-Tab-Sync:** BroadcastChannel für Synchronisation zwischen Browser-Tabs

### Retention-Konfiguration
- **Default:** 50 Einträge pro Topic
- **Pro-Topic konfigurierbar:** Via `setRetention(topic, n)`
- **Spezielle Topics:**
  - Camera-Frames (`/j1/txt/1/i/cam`): **10** (große Payloads, hohe Frequenz, mehr als 10 uninteressant)
  - Sensor-Daten (`/j1/txt/1/i/bme680`, `/j1/txt/1/i/ldr`): **100** (häufige Updates, kleine Payloads)
  - Orders/Config: **50** (Standard)
  - Module-States: **50** (Standard)

### Persistenz-Strategie
- **localStorage:** Für kleine Payloads (< 5MB total)
- **IndexedDB:** Für größere Historien (falls nötig)
- **Camera-Daten:** **NICHT persistieren** (zu groß, zu häufig)
- **Strategie:** Start mit localStorage, später auf IndexedDB migrieren falls nötig

### Schema-Validierung
- **Schemata aus Registry:** JSON-Schemas aus `omf2/registry/schemas/` laden (wie OMF2)
- **Validierungsfehler:** Message trotzdem speichern, aber mit `valid: false` Flag
- **Logging:** Validierungsfehler in Console loggen
- **Fallback:** Wenn kein Schema vorhanden, Message akzeptieren (wie OMF2)

## 🏗️ Architecture Integration

```
ConnectionService (subscribed nur zu spezifischen Topics)
    ↓
MessageMonitorService (stores last + history, Schema-Validierung)
    ↓
Gateway (consumes getLastMessage(topic))
    ↓
Business (aggregates streams)
    ↓
UI Components (consume business streams)
```

### Wichtige Constraints
- **Subscription-Strategie:** `#` (alle Topics) - möglich, da Retention pro Topic konfigurierbar ist
- **Retention pro Topic:** Individuelle Konfiguration verhindert Volumen-Probleme
- **Camera-Daten:** Retention=10, NICHT persistieren, Throttling beibehalten (`throttleTime(1000)`)
- **Unbekannte Topics:** Werden mit Default-Retention (50) behandelt
- **UI-Komponenten:** Sollen nicht unter Overloading leiden (durch Retention-Limits geschützt)

## 📝 Implementation Details

### Service Interface

```typescript
@Injectable({ providedIn: 'root' })
export class MessageMonitorService {
  // Get last message for topic (BehaviorSubject - immediate value)
  getLastMessage(topic: string): Observable<RawMqttMessage>;
  
  // Get history for topic (Array or Observable)
  getHistory(topic: string): RawMqttMessage[];
  getHistory$(topic: string): Observable<RawMqttMessage[]>;
  
  // Management APIs
  setRetention(topic: string, n: number): void;
  setSchema(topic: string, schema: JSONSchema): void;
  clearTopic(topic: string): void;
  getKnownTopics(): string[];
  
  // Internal: Called by ConnectionService when message arrives
  onMessage(message: RawMqttMessage): void;
}
```

### CircularBuffer Implementation

```typescript
class CircularBuffer<T> {
  private buf: Array<T | null>;
  private head: number = 0;
  private size: number = 0;
  private capacity: number;
  
  constructor(capacity: number) {
    this.capacity = capacity;
    this.buf = new Array(capacity).fill(null);
  }
  
  push(item: T): void {
    this.buf[this.head] = item;
    this.head = (this.head + 1) % this.capacity;
    if (this.size < this.capacity) {
      this.size++;
    }
  }
  
  toArray(): T[] {
    const result: T[] = [];
    for (let i = 0; i < this.size; i++) {
      const idx = (this.head - this.size + i + this.capacity) % this.capacity;
      if (this.buf[idx] !== null) {
        result.push(this.buf[idx] as T);
      }
    }
    return result;
  }
}
```

### Schema-Validierung mit Ajv

```typescript
import Ajv from 'ajv';

// Load schema from Registry
async function loadSchema(topic: string): Promise<JSONSchema | null> {
  // Load from omf2/registry/schemas/*.schema.json
  // Map topic to schema file (e.g., 'ccu/state/stock' → 'ccu_state_stock.schema.json')
  const schemaPath = `omf2/registry/schemas/${topicToSchemaFile(topic)}`;
  // Fetch and parse schema
}

// Validate message
function validateMessage(topic: string, message: any, schema: JSONSchema): ValidationResult {
  const ajv = new Ajv();
  const validate = ajv.compile(schema);
  const valid = validate(message);
  
  return {
    valid,
    errors: validate.errors || [],
    message: valid ? message : { ...message, valid: false }
  };
}
```

### Integration in ConnectionService

```typescript
// In ConnectionService.subscribeToRequiredTopics()
// ÄNDERUNG: Statt spezifische Topics → subscribe to "#" (alle Topics)
this._mqttClient.subscribe('#', { qos: 0 }).then(() => {
  console.log('[connection] Subscribed to all topics (#)');
});

// Forward all messages to MessageMonitorService
this._mqttClient.messages$.subscribe((message) => {
  // MessageMonitorService entscheidet pro Topic über Retention
  this.messageMonitorService.onMessage(message);
});
```

### Integration in Gateway

```typescript
// In createGateway()
export const createGateway = (
  messageMonitor: MessageMonitorService, // Instead of mqttMessages$
  options?: { publish?: GatewayPublishFn }
): GatewayStreams => {
  // Get last message from MessageMonitorService
  const orders$ = messageMonitor.getLastMessage('ccu/order/+').pipe(
    filter((msg) => matchTopic(msg.topic, 'ccu/order')),
    // ... rest of processing
  );
  
  // ... other streams
};
```

## 🧪 Testing Requirements

1. **Unit Tests:**
   - CircularBuffer: push, toArray, rollover
   - Schema-Validierung: valid/invalid messages
   - Retention-Konfiguration: pro-Topic unterschiedlich
   - Persistenz: localStorage save/load

2. **Integration Tests:**
   - ConnectionService → MessageMonitorService → Gateway
   - Multi-Tab-Sync (BroadcastChannel)
   - Camera-Daten: Throttling + Retention (max 10)

3. **E2E Tests:**
   - UI-Komponenten erhalten letzte Werte beim Tab-Wechsel
   - Historie-Anzeige (falls UI-Komponente implementiert)

## 📚 References

- **OMF2 Architektur:** `omf2/common/message_manager.py` (Schema-Validierung)
- **OMF2 Registry:** `omf2/registry/schemas/` (JSON-Schemas)
- **Aktuelle Gateway-Implementierung:** `omf3/libs/gateway/src/index.ts`
- **Aktuelle ConnectionService:** `omf3/apps/ccu-ui/src/app/services/connection.service.ts`

## ✅ Acceptance Criteria

- [ ] `MessageMonitorService` implementiert mit BehaviorSubject pro Topic
- [ ] CircularBuffer für Historie mit konfigurierbarer Retention
- [ ] Schema-Validierung aus Registry (Ajv)
- [ ] Persistenz (localStorage, Camera-Daten NICHT persistieren)
- [ ] Multi-Tab-Sync (BroadcastChannel)
- [ ] Integration in ConnectionService → Gateway
- [ ] Retention-Konfiguration: Camera=10, Sensoren=100, Standard=50
- [ ] Unit Tests für alle Features
- [ ] Integration Tests für Architektur-Integration
- [ ] Dokumentation aktualisiert

## 🚀 Implementation Steps

1. **Phase 1: Core Service**
   - CircularBuffer implementieren
   - MessageMonitorService mit BehaviorSubject pro Topic
   - Integration in ConnectionService

2. **Phase 2: Gateway Integration**
   - Gateway auf MessageMonitorService umstellen
   - Tests für bestehende Streams

3. **Phase 3: Erweiterungen**
   - Schema-Validierung (Ajv + Registry)
   - Persistenz (localStorage)
   - Multi-Tab-Sync (BroadcastChannel)

4. **Phase 4: Testing & Documentation**
   - Unit Tests
   - Integration Tests
   - Dokumentation

## 📝 Notes

- **Camera-Daten:** Bereits throttled (`throttleTime(1000)`), beibehalten
- **Registry-Integration:** Schemas aus `omf2/registry/schemas/` (wie OMF2)
- **Subscription-Strategie:** `#` (alle Topics) - möglich durch Retention-Konfiguration pro Topic
- **Volumen-Problem gelöst:** Individuelle Retention pro Topic verhindert Überlastung
- **Unbekannte Topics:** Werden mit Default-Retention (50) behandelt, kein Problem da System bekannt
- **UI-Overloading:** Verhindert durch Retention-Limits pro Topic
