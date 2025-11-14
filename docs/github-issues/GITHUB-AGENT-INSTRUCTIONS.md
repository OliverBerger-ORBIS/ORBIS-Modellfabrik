# GitHub Agent Instructions - PR-17 Message Monitor Service

## 🎯 Für den GitHub Agent

**Branch:** `PR-17-message-monitor-service`  
**Issue/PR:** Siehe unten für GitHub UI Anweisungen

## 📋 Aufgabe

Implementiere den `MessageMonitorService` gemäß der folgenden Spezifikation.

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

## 📚 Wichtige Dateien zum Analysieren

1. **Aktuelle Gateway-Implementierung:**
   - `omf3/libs/gateway/src/index.ts` - Wie Messages aktuell verarbeitet werden
   - `omf3/apps/ccu-ui/src/app/services/connection.service.ts` - MQTT Connection Service

2. **OMF2 Referenz (Schema-Validierung):**
   - `omf2/common/message_manager.py` - Wie OMF2 Schema-Validierung macht
   - `omf2/registry/schemas/` - JSON-Schema-Dateien

3. **Aktuelle Business-Logic:**
   - `omf3/libs/business/src/index.ts` - Wie Streams aggregiert werden

## 🚀 Implementierungsreihenfolge

1. **CircularBuffer Klasse** (`omf3/libs/message-monitor/src/circular-buffer.ts`)
2. **MessageMonitorService** (`omf3/apps/ccu-ui/src/app/services/message-monitor.service.ts`)
3. **Integration in ConnectionService** (Message weiterleiten, `#` subscription)
4. **Gateway umstellen** (von `mqttMessages$` auf `MessageMonitorService`)
5. **Schema-Validierung** (Ajv + Registry-Integration)
6. **Persistenz** (localStorage)
7. **Multi-Tab-Sync** (BroadcastChannel)
8. **Tests** (Unit + Integration)

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

---

## 👤 Für den User - GitHub UI Anweisungen

### Schritt 1: Branch pushen

```bash
git checkout PR-17-message-monitor-service
git push origin PR-17-message-monitor-service
```

### Schritt 2: GitHub Issue erstellen

1. Gehe zu: https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik/issues/new
2. **Title:** `PR-17: Implement Message Monitor Service`
3. **Description:** Kopiere den kompletten Inhalt aus dieser Datei (ab "Problem Statement")
4. **Labels:** `enhancement`, `omf3`, `help wanted`
5. **Assignees:** (optional) GitHub Agent
6. **Klicke "Submit new issue"**

### Schritt 3: Pull Request erstellen

1. Gehe zu: https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik/compare
2. **Base:** `main`
3. **Compare:** `PR-17-message-monitor-service`
4. **Title:** `PR-17: Implement Message Monitor Service`
5. **Description:**
   ```
   Closes #[ISSUE-NUMBER]
   
   Implementiert MessageMonitorService gemäß Spezifikation.
   
   Siehe: docs/github-issues/GITHUB-AGENT-INSTRUCTIONS.md
   
   ## Wichtige Änderungen
   - Subscription zu `#` (alle Topics) möglich durch Retention-Konfiguration
   - Camera-Daten: Retention=10, NICHT persistieren
   - Schema-Validierung aus Registry (wie OMF2)
   - Multi-Tab-Sync via BroadcastChannel
   ```
6. **Klicke "Create pull request"**

### Schritt 4: GitHub Agent aktivieren

**Option A: Via GitHub Copilot Chat**
1. Im PR: Öffne GitHub Copilot Chat (rechts oder unten)
2. Prompt:
   ```
   Please implement the MessageMonitorService according to the specification in docs/github-issues/GITHUB-AGENT-INSTRUCTIONS.md
   
   Key requirements:
   - CircularBuffer for history with configurable retention per topic
   - BehaviorSubject per topic for immediate last message access
   - Schema validation from omf2/registry/schemas/
   - localStorage persistence (except camera data)
   - Multi-tab sync via BroadcastChannel
   - Subscribe to "#" (all topics) - retention limits prevent volume issues
   ```

**Option B: Via PR Comment**
1. Kommentiere im PR:
   ```
   @github-copilot please implement according to the specification in docs/github-issues/GITHUB-AGENT-INSTRUCTIONS.md
   ```

**Option C: Via GitHub Actions (falls konfiguriert)**
1. Im PR: Klicke auf "..." → "Ask Copilot" oder "GitHub Copilot"

### Schritt 5: Review & Merge

- Review die Implementierung des GitHub Agents
- Teste lokal: `nx serve ccu-ui`
- Prüfe die Checkliste unten
- Wenn alles passt: Merge in `main`

---

## 🔍 Checkliste für Review

- [ ] MessageMonitorService implementiert
- [ ] CircularBuffer funktioniert (push, toArray, rollover)
- [ ] BehaviorSubject pro Topic für sofortige Verfügbarkeit
- [ ] Schema-Validierung aus Registry (Ajv)
- [ ] Persistenz (localStorage, Camera-Daten NICHT persistieren)
- [ ] Multi-Tab-Sync (BroadcastChannel)
- [ ] Integration in ConnectionService → Gateway
- [ ] Subscription zu `#` (alle Topics) implementiert
- [ ] Retention-Konfiguration: Camera=10, Sensoren=100, Standard=50
- [ ] Unit Tests vorhanden
- [ ] Integration Tests vorhanden
- [ ] Keine Breaking Changes für bestehende UI-Komponenten
- [ ] Dokumentation aktualisiert

---

## 📝 Wichtige Hinweise

1. **Subscription-Strategie:** `#` (alle Topics) ist möglich, da Retention pro Topic konfigurierbar ist
2. **Volumen-Problem gelöst:** Individuelle Retention pro Topic verhindert Überlastung
3. **Camera-Daten:** Bereits throttled (`throttleTime(1000)`), Retention=10, NICHT persistieren
4. **Unbekannte Topics:** Werden mit Default-Retention (50) behandelt
5. **Registry-Integration:** Schemas aus `omf2/registry/schemas/` laden (wie OMF2)

---

# PR-18: I18n Runtime Language Switching

## 🎯 Für den GitHub Agent

**Branch:** `PR-18-i18n-fix`

## 📋 Problem Statement

Die OMF3 Angular-Anwendung benötigt vollständigen I18n-Support (Internationalisierung) für drei Sprachen: Englisch (EN), Deutsch (DE) und Französisch (FR).

**Aktueller Zustand:**
- ✅ Übersetzungsdateien existieren bereits: `messages.de.json`, `messages.fr.json`
- ✅ Language-Selector in der Sidebar ist vorhanden (EN/DE/FR Buttons)
- ✅ URL-Routing funktioniert (`/de/overview`, `/fr/overview`)
- ❌ **Übersetzungen werden nicht angezeigt**: Trotz korrekter URL bleiben alle Texte auf Englisch
- ❌ **Sprachwechsel hat keinen Effekt**: Klick auf "DE" oder "FR" in der Sidebar ändert nur die URL, nicht die angezeigten Texte

## 🎯 Anforderung

**Ziel:** Der Benutzer soll in der Sidebar die Sprache wählen können (EN/DE/FR), und die gesamte Anwendung soll daraufhin in der ausgewählten Sprache angezeigt werden.

**Erwartetes Verhalten:**
1. **Initial Load**: Wenn der Benutzer die Anwendung öffnet, soll die zuletzt gewählte Sprache (oder Standard: EN) verwendet werden
2. **Language Switch**: Klick auf "DE" oder "FR" in der Sidebar soll sofort alle Texte in der Anwendung in der gewählten Sprache anzeigen
3. **URL-Persistenz**: Die gewählte Sprache soll in der URL reflektiert werden (`/:locale/...`)
4. **Persistenz**: Die gewählte Sprache soll gespeichert werden (localStorage), damit sie beim nächsten Besuch erhalten bleibt

## 📋 Technischer Kontext

**Verwendete Technologie:**
- Angular 18.2.0
- `@angular/localize` für i18n
- JSON-basierte Übersetzungsdateien: `omf3/apps/ccu-ui/src/locale/messages.{de,fr}.json`
- Translation-Keys verwenden `$localize`:@@key:Default Text` Format

**Bestehende Dateien:**
- `omf3/apps/ccu-ui/src/main.ts` - App-Entry-Point
- `omf3/apps/ccu-ui/src/app/services/language.service.ts` - Language-Service
- `omf3/apps/ccu-ui/src/app/app.component.ts` - Main Component mit Language-Selector
- `omf3/apps/ccu-ui/src/locale/messages.de.json` - Deutsche Übersetzungen
- `omf3/apps/ccu-ui/src/locale/messages.fr.json` - Französische Übersetzungen

## ✅ Acceptance Criteria

1. ✅ **Initial Load mit DE**: Öffnen von `/de/overview` zeigt alle Texte auf Deutsch
2. ✅ **Initial Load mit FR**: Öffnen von `/fr/overview` zeigt alle Texte auf Französisch
3. ✅ **Language Switch DE → FR**: Klick auf "FR" in der Sidebar ändert URL zu `/fr/overview` UND alle Texte werden auf Französisch angezeigt
4. ✅ **Language Switch FR → DE**: Klick auf "DE" in der Sidebar ändert URL zu `/de/overview` UND alle Texte werden auf Deutsch angezeigt
5. ✅ **Direct URL Access**: Direkter Zugriff auf `/fr/order` zeigt die Seite mit französischen Übersetzungen
6. ✅ **Persistenz**: Die gewählte Sprache wird in localStorage gespeichert und beim nächsten Besuch verwendet
7. ✅ **Fallback**: Bei fehlenden Übersetzungen wird Englisch verwendet

## 🧪 Test-Szenarien

1. **Test 1: Initial Load DE**
   - Öffne: `http://localhost:4200/de/overview`
   - Erwartung: Navigation zeigt "Übersicht", "Aufträge", etc. (deutsche Texte)

2. **Test 2: Language Switch**
   - Starte auf: `/de/overview` (deutsche Texte sichtbar)
   - Klicke auf: "FR" Button in der Sidebar
   - Erwartung: URL wechselt zu `/fr/overview`, Navigation zeigt "Vue d'ensemble", "Commandes", etc. (französische Texte)

3. **Test 3: Direct URL**
   - Öffne direkt: `http://localhost:4200/fr/order`
   - Erwartung: Seite lädt mit französischen Übersetzungen

4. **Test 4: Persistenz**
   - Wähle "DE" in der Sidebar
   - Schließe den Browser-Tab
   - Öffne erneut: `http://localhost:4200`
   - Erwartung: Seite lädt mit deutschen Übersetzungen (aus localStorage)

## 📚 Referenzen

- [Angular i18n Documentation](https://angular.io/guide/i18n)
- [@angular/localize API](https://angular.io/api/localize)
- Translation-Dateien: `omf3/apps/ccu-ui/src/locale/messages.{de,fr}.json`
