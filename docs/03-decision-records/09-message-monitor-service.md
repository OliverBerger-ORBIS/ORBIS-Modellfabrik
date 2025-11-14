# Message Monitor Service - Architektur-Entscheidung

## Kontext

GitHub Copilot hat einen Vorschlag für einen `MessageMonitorService` gemacht, der zwei Probleme gleichzeitig löst:
1. **Sofortige Verfügbarkeit** des letzten Payloads pro Topic (BehaviorSubject)
2. **Historie** pro Topic mit Rollover (CircularBuffer)

## Aktueller Stand

- `Gateway` verwendet `shareReplay(1)` für letztes Payload
- Keine Historie vorhanden
- Keine Persistenz über Reloads
- Späte Subscriber bekommen nur neue Messages, nicht die letzte

## Entscheidung: ✅ **Implementieren**

Der Vorschlag passt perfekt in unsere Architektur:
- Ergänzt `ConnectionService` → `MessageMonitorService` → `Gateway` → `Business` → UI
- Löst beide Probleme (sofortige Verfügbarkeit + Historie)
- Erweitert um Schema-Validierung, Persistenz, Multi-Tab-Sync

## Vergleich mit OMF2 Architektur

### OMF2 Ansatz
- **Admin-Domäne:** Subscribed zu ALLEN Topics (`#` Wildcard)
- **CCU-Domäne:** Subscribed nur zu spezifischen Topics aus Registry
- **Schema-Validierung:** Zentral über Registry (`omf2/registry/schemas/*.schema.json`)
- **Per-Topic-Buffer:** `deque(maxlen=1000)` pro Topic
- **MessageManager:** Validiert gegen Schema aus Registry via `jsonschema`

### Unterschiede zu OMF3
- **OMF3 aktuell:** Nur spezifische Topics subscribed (kein Wildcard)
- **OMF3 aktuell:** Keine Historie, nur `shareReplay(1)`
- **OMF3 aktuell:** Keine Schema-Validierung

### Wichtige Erkenntnisse aus OMF2
1. **Camera-Daten:** Hochfrequent (100+ msgs/min, 2-3 fps) + große Payloads (base64 JPEG)
2. **Overloading-Problem:** UI-Komponenten sollten nicht unter "alle Topics subscribed" leiden
3. **Schema-Validierung:** Sollte aus Registry kommen (wie OMF2), nicht manuell in App

## Antworten auf GitHub-Fragen (aktualisiert)

### 1. Retention Default und pro-Topic Konfiguration
- **Default:** 50 Einträge pro Topic
- **Pro-Topic konfigurierbar:** Ja, via `setRetention(topic, n)`
- **Spezielle Topics:** 
  - **Camera-Frames (`/j1/txt/1/i/cam`):** 10 (große Payloads, hohe Frequenz, mehr als 10 uninteressant)
  - **Sensor-Daten (`/j1/txt/1/i/bme680`, `/j1/txt/1/i/ldr`):** 100 (häufige Updates, kleine Payloads)
  - **Orders/Config:** 50 (Standard)
  - **Module-States:** 50 (Standard)

### 2. Persistenz über Reloads
- **Ja, Persistenz gewünscht**
- **localStorage** für kleine Payloads (< 5MB total)
- **IndexedDB** für größere Historien (falls nötig)
- **Strategie:** Start mit localStorage, später auf IndexedDB migrieren falls nötig
- **Camera-Daten:** NICHT persistieren (zu groß, zu häufig)

### 3. Schema-Validierung
- **Schemata pro Topic:** Aus Registry laden (wie OMF2), nicht manuell in App
- **Registry-Integration:** JSON-Schemas aus `omf2/registry/schemas/` verwenden
- **Validierungsfehler:** Message trotzdem speichern, aber mit `valid: false` Flag
- **Logging:** Validierungsfehler in Console loggen
- **Fallback:** Wenn kein Schema vorhanden, Message akzeptieren (wie OMF2)

### 4. Multi-Tab-Synchronisation
- **Ja, Browser-Tabs synchronisieren**
- **BroadcastChannel** für Multi-Tab-Sync
- **Fallback:** Wenn BroadcastChannel nicht verfügbar, nur lokale Persistenz

### 5. Subscription-Strategie
- **NICHT alle Topics subscriben** (wie Admin in OMF2)
- **Nur spezifische Topics** (wie CCU in OMF2)
- **Throttling für Camera-Daten:** Bereits implementiert (`throttleTime(1000)`), beibehalten
- **UI-Komponenten:** Sollen nicht unter Overloading leiden

### 6. Branch/PR-Policy
- **Branch:** `PR-17-message-monitor-service`
- **PR:** Nach Implementierung auf `main` (ehemaliger `omf3`)

## Implementierungsplan

### Phase 1: Core Service
1. `MessageMonitorService` mit BehaviorSubject pro Topic
2. CircularBuffer für Historie
3. Integration in `ConnectionService` → `MessageMonitorService` → `Gateway`

### Phase 2: Erweiterungen
1. Schema-Validierung (Ajv)
2. Persistenz (localStorage)
3. Multi-Tab-Sync (BroadcastChannel)

### Phase 3: UI-Integration
1. Demo-Komponente für Historie-Anzeige
2. Integration in existierende Tabs (optional)

## Architektur-Integration

```
ConnectionService (subscribed to MQTT topics)
    ↓
MessageMonitorService (stores last + history)
    ↓
Gateway (consumes getLastMessage(topic))
    ↓
Business (aggregates streams)
    ↓
UI Components (consume business streams)
```

## Offene Fragen

- Soll `MessageMonitorService` auch für Mock-Fixtures verwendet werden?
- Sollen historische Messages auch in Mock-Mode gespeichert werden?
- Soll es eine UI-Komponente für Historie-Anzeige geben (ähnlich OMF2 Message Monitor)?

