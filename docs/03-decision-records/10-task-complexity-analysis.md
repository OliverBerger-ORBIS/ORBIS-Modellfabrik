# Task Complexity Analysis - I18n vs. Message Monitor Service

## Aufgabe 1: I18n Fix

### Problem
- Language-Switch funktioniert nicht korrekt
- Übersetzungen werden nicht geladen/angezeigt
- `$localize` funktioniert nicht wie erwartet

### Aktueller Stand
- Angular's `$localize` mit separaten Builds pro Locale
- Runtime-Loading von Translation-Files (`locale/messages.{lang}.json`)
- `LanguageService` mit `localStorage` für Locale-Persistenz
- `main.ts` lädt Translations asynchron vor Bootstrap

### Was muss gemacht werden
1. Translation-Files korrekt laden (Format prüfen)
2. `$localize` korrekt initialisieren
3. Language-Switch ohne Page-Reload (oder mit korrektem Reload)
4. Möglicherweise Build-Konfiguration anpassen
5. Template-Strings mit `i18n` Attributen prüfen

### Komplexität: **MITTEL** ⚠️
- **Abhängigkeiten:** Wenig (Angular i18n System)
- **Risiko:** Niedrig (isoliertes Problem)
- **Scope:** Begrenzt (hauptsächlich Konfiguration)
- **Schätzung:** 2-4 Stunden

---

## Aufgabe 2: Message Monitor Service

### Problem
1. Letzte Payloads pro Topic sofort verfügbar (aktuell nur `shareReplay(1)`)
2. Historie pro Topic mit Rollover (aktuell keine Historie)
3. Schema-Validierung aus Registry (aktuell keine Validierung)
4. Persistenz über Reloads (aktuell keine Persistenz)
5. Multi-Tab-Synchronisation (aktuell keine Sync)

### Aktueller Stand
- `Gateway` verwendet `shareReplay(1)` für letztes Payload
- Keine Historie vorhanden
- Keine Schema-Validierung
- Keine Persistenz
- Späte Subscriber bekommen nur neue Messages

### Was muss gemacht werden
1. **Neuer Service:** `MessageMonitorService` erstellen
2. **BehaviorSubject pro Topic:** Für sofortige Verfügbarkeit
3. **CircularBuffer:** Für Historie mit Rollover
4. **Schema-Validierung:** Ajv + Registry-Integration (`omf2/registry/schemas/`)
5. **Persistenz:** localStorage (kleine Payloads) + IndexedDB (große Historien)
6. **Multi-Tab-Sync:** BroadcastChannel
7. **Integration:** ConnectionService → MessageMonitorService → Gateway
8. **Throttling:** Camera-Daten bereits throttled, beibehalten
9. **Retention-Konfiguration:** Pro-Topic konfigurierbar (Camera: 10, Sensoren: 100, Standard: 50)
10. **Registry-Integration:** JSON-Schemas aus `omf2/registry/schemas/` laden

### Komplexität: **HOCH** 🔴
- **Abhängigkeiten:** Viele (ConnectionService, Gateway, Registry, RxJS, Ajv, BroadcastChannel, localStorage/IndexedDB)
- **Risiko:** Hoch (komplexe Architektur-Integration)
- **Scope:** Groß (neuer Service, viele Features)
- **Schätzung:** 8-16 Stunden

---

## Entscheidung: Message Monitor Service → GitHub

**Begründung:**
- **Komplexität:** Message Monitor Service ist deutlich komplizierter
- **Abhängigkeiten:** Viele Integrationen nötig
- **Architektur-Impact:** Größere Änderungen an bestehender Architektur
- **Test-Aufwand:** Umfangreichere Tests nötig

**I18n Fix:**
- **Einfacher:** Isoliertes Problem
- **Schneller:** Kann parallel gemacht werden
- **Niedrigeres Risiko:** Weniger Abhängigkeiten

---

## Parallel-Arbeit

### Branch-Strategie
1. **`PR-17-message-monitor-service`** → GitHub (komplizierter)
2. **`PR-18-i18n-fix`** → Lokal (einfacher, parallel)

### Merge-Strategie
- I18n-Fix sollte relativ leicht gemerged werden können (isolierte Änderungen)
- Message Monitor Service erfordert möglicherweise Konflikt-Resolution

