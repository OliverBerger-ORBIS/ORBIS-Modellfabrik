# GitHub Agent Instructions - PR-17 Message Monitor Service

## 🎯 Für den GitHub Agent

**Branch:** `PR-17-message-monitor-service`  
**Issue/PR:** Siehe unten für GitHub UI Anweisungen

## 📋 Aufgabe

Implementiere den `MessageMonitorService` gemäß der Spezifikation in `docs/github-issues/PR-17-message-monitor-service.md`.

### Wichtige Dateien zum Analysieren

1. **Aktuelle Gateway-Implementierung:**
   - `omf3/libs/gateway/src/index.ts` - Wie Messages aktuell verarbeitet werden
   - `omf3/apps/ccu-ui/src/app/services/connection.service.ts` - MQTT Connection Service

2. **OMF2 Referenz (Schema-Validierung):**
   - `omf2/common/message_manager.py` - Wie OMF2 Schema-Validierung macht
   - `omf2/registry/schemas/` - JSON-Schema-Dateien

3. **Aktuelle Business-Logic:**
   - `omf3/libs/business/src/index.ts` - Wie Streams aggregiert werden

### Implementierungsreihenfolge

1. **CircularBuffer Klasse** (`omf3/libs/message-monitor/src/circular-buffer.ts`)
2. **MessageMonitorService** (`omf3/apps/ccu-ui/src/app/services/message-monitor.service.ts`)
3. **Integration in ConnectionService** (Message weiterleiten, `#` subscription)
4. **Gateway umstellen** (von `mqttMessages$` auf `MessageMonitorService`)
5. **Schema-Validierung** (Ajv + Registry-Integration)
6. **Persistenz** (localStorage)
7. **Multi-Tab-Sync** (BroadcastChannel)
8. **Tests** (Unit + Integration)

### Wichtige Constraints

- **Subscription:** `#` (alle Topics) - möglich durch Retention-Konfiguration pro Topic
- **Retention pro Topic:** Individuelle Konfiguration verhindert Volumen-Probleme
- **Camera-Daten:** Retention max 10, NICHT persistieren
- **Throttling beibehalten:** Camera-Daten bereits `throttleTime(1000)`, nicht ändern
- **Registry-Schemas:** Aus `omf2/registry/schemas/` laden, nicht manuell in App
- **Unbekannte Topics:** Default-Retention (50) verwenden

### Testing

- **Unit Tests:** Für CircularBuffer, MessageMonitorService
- **Integration Tests:** ConnectionService → MessageMonitorService → Gateway
- **E2E:** UI-Komponenten erhalten letzte Werte beim Tab-Wechsel

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
3. **Description:** Kopiere den kompletten Inhalt aus `docs/github-issues/PR-17-message-monitor-service.md`
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
   
   Siehe: docs/github-issues/PR-17-message-monitor-service.md
   
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
   Please implement the MessageMonitorService according to the specification in docs/github-issues/PR-17-message-monitor-service.md
   
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
   @github-copilot please implement according to the specification in docs/github-issues/PR-17-message-monitor-service.md
   ```

**Option C: Via GitHub Actions (falls konfiguriert)**
1. Im PR: Klicke auf "..." → "Ask Copilot" oder "GitHub Copilot"

### Schritt 5: Review & Merge

- Review die Implementierung des GitHub Agents
- Teste lokal: `nx serve ccu-ui`
- Prüfe:
  - [ ] MessageMonitorService implementiert
  - [ ] CircularBuffer funktioniert
  - [ ] Schema-Validierung aus Registry
  - [ ] Persistenz (localStorage, Camera NICHT)
  - [ ] Multi-Tab-Sync (BroadcastChannel)
  - [ ] Subscription zu `#` (alle Topics)
  - [ ] Retention-Konfiguration: Camera=10, Sensoren=100, Standard=50
  - [ ] Unit Tests vorhanden
  - [ ] Integration Tests vorhanden
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
