# Decision Record: MessageMonitorService - Speicherverwaltung und Retention

**Datum:** 2025-11-15  
**Status:** Accepted  
**Kontext:** Der MessageMonitorService in OMF3 benötigt eine klare Speicherverwaltung mit Überlauf-Prävention und konfigurierbarer Retention pro Topic.

---

## Entscheidung

Verwendung eines **Circular Buffer** Systems mit konfigurierbarer Retention pro Topic, localStorage-Persistierung mit 5MB Limit und automatischer Überlauf-Prävention.

## Speicherverwaltung

### Circular Buffer (In-Memory)

- **Struktur:** Pro Topic ein eigener Circular Buffer
- **Standard-Retention:** 50 Nachrichten pro Topic
- **Verhalten:** Älteste Nachrichten werden automatisch entfernt, wenn Limit erreicht wird
- **Implementierung:** `CircularBuffer<T>` Interface mit `items[]` und `maxSize`

```typescript
interface CircularBuffer<T> {
  items: T[];
  maxSize: number;
}
```

### localStorage Persistierung

- **Limit:** 5 MB gesamt (`STORAGE_SIZE_LIMIT = 5 * 1024 * 1024`)
- **Prüfung:** Vor jeder Persistierung wird Gesamtgröße geprüft
- **Verhalten:** Wenn Limit erreicht, wird Persistierung für neue Nachrichten übersprungen
- **Key-Pattern:** `omf3.message-monitor.<topic>`

### Überlauf-Prävention

1. **Circular Buffer:** Automatisches Trimmen auf `maxSize` (Zeile 204-206)
2. **localStorage:** Größenprüfung vor Persistierung (Zeile 252-255)
3. **Excluded Topics:** Camera-Daten werden nicht persistiert (Zeile 24, 237-239)

## Retention-Konfiguration

### Standard-Retention

```typescript
const DEFAULT_RETENTION = 50; // Nachrichten pro Topic
```

### Topicspezifische Retention

Konfiguriert in `RETENTION_CONFIG` (Zeilen 27-31):

```typescript
const RETENTION_CONFIG: Record<string, number> = {
  '/j1/txt/1/i/cam': 10,      // Camera frames: niedrige Retention (große Payloads)
  '/j1/txt/1/i/bme680': 100,  // BME680 sensor: hohe Retention (kleine Payloads)
  '/j1/txt/1/i/ldr': 100,     // LDR sensor: hohe Retention (kleine Payloads)
};
```

### Runtime-Konfiguration

Retention kann zur Laufzeit geändert werden:

```typescript
messageMonitor.setRetention('ccu/state/stock', 200);
const retention = messageMonitor.getRetention('ccu/state/stock');
```

## Persistierung

### Ausgeschlossene Topics

Topics, die **nicht** in localStorage persistiert werden:

```typescript
const NO_PERSIST_TOPICS = ['/j1/txt/1/i/cam'];
```

**Grund:** Camera-Daten sind zu groß für localStorage (mehrere MB pro Frame).

### Persistierungs-Strategie

1. **Bei `addMessage()`:** Nachricht wird zu Circular Buffer hinzugefügt
2. **Persistierung:** Nur wenn Topic nicht in `NO_PERSIST_TOPICS`
3. **Größenprüfung:** Vor Persistierung wird Gesamtgröße geprüft
4. **Fehlerbehandlung:** Fehler bei localStorage werden geloggt, aber nicht geworfen

## Multi-Tab Synchronisation

- **BroadcastChannel:** Synchronisation zwischen Browser-Tabs
- **Channel-Name:** `omf3-message-monitor`
- **Verhalten:** Neue Nachrichten werden an alle Tabs broadcastet

## Konsequenzen

### Positiv:

- **Speicher-Effizienz:** Circular Buffer verhindert unbegrenztes Wachstum
- **Überlauf-Prävention:** 5MB localStorage-Limit verhindert Browser-Crashes
- **Flexibilität:** Retention pro Topic konfigurierbar
- **Performance:** In-Memory Buffer für schnellen Zugriff
- **Persistenz:** Wichtige Daten über Browser-Neustarts erhalten
- **Multi-Tab:** Konsistente Daten über alle Tabs hinweg

### Negativ:

- **Speicher-Limit:** 5MB kann bei vielen Topics schnell erreicht werden
- **Camera-Daten:** Werden nicht persistiert (zu groß)
- **localStorage:** Browser-spezifische Limits können variieren

## Implementierung

### Datei

`osf/apps/osf-ui/src/app/services/message-monitor.service.ts`

### Wichtige Konstanten

```typescript
const DEFAULT_RETENTION = 50;
const STORAGE_SIZE_LIMIT = 5 * 1024 * 1024; // 5MB
const STORAGE_KEY_PREFIX = 'omf3.message-monitor';
const NO_PERSIST_TOPICS = ['/j1/txt/1/i/cam'];
const RETENTION_CONFIG: Record<string, number> = {
  '/j1/txt/1/i/cam': 10,
  '/j1/txt/1/i/bme680': 100,
  '/j1/txt/1/i/ldr': 100,
};
```

### Wichtige Methoden

- `addMessage(topic, payload, timestamp?)` - Nachricht hinzufügen
- `getLastMessage<T>(topic)` - Letzte Nachricht als Observable
- `getHistory<T>(topic)` - Historie als Array
- `setRetention(topic, limit)` - Retention zur Laufzeit ändern
- `getRetention(topic)` - Aktuelle Retention abfragen
- `clearTopic(topic)` - Topic löschen
- `clearAll()` - Alle Daten löschen

## Konfiguration

### Neue Topics hinzufügen

Um Retention für neue Topics zu konfigurieren, `RETENTION_CONFIG` erweitern:

```typescript
const RETENTION_CONFIG: Record<string, number> = {
  '/j1/txt/1/i/cam': 10,
  '/j1/txt/1/i/bme680': 100,
  '/j1/txt/1/i/ldr': 100,
  'ccu/state/stock': 200,  // Neue Konfiguration
};
```

### Topics von Persistierung ausschließen

Topics zu `NO_PERSIST_TOPICS` hinzufügen:

```typescript
const NO_PERSIST_TOPICS = [
  '/j1/txt/1/i/cam',
  'module/v1/#/camera',  // Neue Ausnahme
];
```

## Monitoring

### Storage-Größe prüfen

Die aktuelle Storage-Größe wird intern in `getStorageSize()` berechnet und vor jeder Persistierung geprüft.

### Logging

- **Warnung:** Wenn Storage-Limit erreicht wird
- **Info:** Anzahl geladener Topics beim Start
- **Error:** Fehler bei Persistierung/Ladung

## Zukünftige Erweiterungen

- [ ] IndexedDB statt localStorage für größere Datenmengen
- [ ] Konfigurierbares Storage-Limit pro Topic
- [ ] Automatische Bereinigung alter Topics
- [ ] Storage-Statistiken im Message Monitor Tab

---

*Entscheidung getroffen von: Projektteam*

