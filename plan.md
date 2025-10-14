# OMF2 Messe-Vorbereitung Plan (bis 25. Nov 2025)

## Aktueller Status (14. Oktober 2025)

### ✅ **Task 0.1 ABGESCHLOSSEN: Stock-Topic Fix**

**Status:** ✅ **VOLLSTÄNDIG ABGESCHLOSSEN - Demo-fähig für morgen!**

**Was wurde gefixt:**
- ✅ Topic korrigiert: `/j1/txt/1/f/o/stock` → `/j1/txt/1/f/i/stock`
- ✅ `omf2/registry/mqtt_clients.yml` - subscribed_topics korrigiert
- ✅ `omf2/ccu/ccu_gateway.py` - order_topics korrigiert
- ✅ `omf2/ccu/order_manager.py` - docstring korrigiert
- ✅ UI zeigt Stock-Daten korrekt an (Inventory Subtab)
- ✅ Tests laufen (18 Tests waren bereits vorher fehlerhaft)
- ✅ Registry ist konsistent

**Commits:**
- `262ef93` - "fix: Stock-Topic korrektur /f/o/stock → /f/i/stock"
- `f61b617` - "cleanup: Legacy-Verzeichnisse löschen + Dokumentations-Updates"

**Erfolgs-Kriterium erreicht:**
- ✅ Topic korrekt: `/j1/txt/1/f/i/stock`
- ✅ Inventory zeigt Stock-Daten an
- ✅ Demo-fähig (kann morgen vorgeführt werden)

---

### ✅ **Task 0.2 ABGESCHLOSSEN: Legacy-Cleanup**

**Status:** ✅ **VOLLSTÄNDIG ABGESCHLOSSEN**

**Was wurde gelöscht:**
- ✅ **`<root>/omf/`** - Vollständig nach `omf2/` migriert (382 Dateien gelöscht)
- ✅ **`<root>/registry/`** - Vollständig nach `omf2/registry/` migriert
- ✅ **68.682 Zeilen Code entfernt** - Repository deutlich kleiner
- ✅ **Saubere Projektstruktur** - nur noch `omf2/` als aktive Quelle

**Ergebnis:**
- 🗂️ **Bessere Übersichtlichkeit** - keine doppelten Legacy-Verzeichnisse
- 📦 **Kleinere Repository-Größe** - weniger Verwirrung
- 🚀 **Fokussierte Entwicklung** - nur noch omf2/ relevant

---

### Implementiert (323 von 341 Tests bestehen):

- Core-Architektur: MQTT Clients, Gateways, Business Manager
- Registry v2 Integration mit 44 Schemas
- CCU Domain: Overview, Modules, Orders, Process, Configuration Tabs
- Admin Domain: Settings, Message Center, System Logs, Steering
- i18n-System (DE, EN, FR)
- Production Order Manager
- Shopfloor Layout System

### KRITISCH: Architektur-Verletzungen (ANTIPATTERN):

- **18 failing Tests** → Agenten haben ohne Tests eingecheckt ❌
- **Meta-Parameter in Payload** → mqtt_timestamp wird fälschlicherweise in message/payload mitgesendet
- **Fehlende zentrale Validierung** → Nicht alle Gateways verwenden MessageManager.validate()
- **Command-Versende-Pattern inkonsistent** → CCU Gateway vs Admin Gateway unterschiedlich

### Unbekannte Features (aus REFACTORING_BACKLOG.md):

- Auto-Refresh bei MQTT Messages
- Factory Layout mit echten omf_* SVG-Icons
- Kamera-Befehle UI-Verbesserung
- Temperatur-Skala Anzeige
- ~~Stock-Topic Korrektur (/f/o/stock → /f/i/stock)~~ ✅ **ABGESCHLOSSEN**
- ~~Legacy-Cleanup (omf/, registry/)~~ ✅ **ABGESCHLOSSEN**

## Phase 1: KRITISCHE ARCHITEKTUR-FIXES (15. - 21. Okt, 7 Tage)

**Ziel: Architektur-Compliance wiederherstellen, bevor weitere Features entwickelt werden**

### Task 1.1: Command-Versende-Pattern Fix (NÄCHSTE PRIORITÄT)

**Keine Abhängigkeiten - SOFORT startbar**

**Problem-Analyse:**

```bash
# Finde alle publish_message() Aufrufe
grep -r "publish_message" omf2/ccu/ omf2/admin/
# Prüfe Meta-Parameter Handling
grep -r "mqtt_timestamp" omf2/
```

**Architektur-Anforderung:**

```
Business Function → Gateway.publish_message(topic, payload, meta=None)
                     ↓
Gateway → MessageManager.validate(payload, schema)
                     ↓
Gateway → MQTT Client.publish(topic, payload_clean, qos, retain)
                     ↓
MQTT Client fügt Meta-Parameter GETRENNT hinzu (nicht in payload!)
```

**Zu fixen:**

- `omf2/ccu/ccu_gateway.py::publish_message()` - Meta-Parameter-Handling prüfen
- `omf2/admin/admin_gateway.py::publish_message()` - Meta-Parameter-Handling prüfen
- Zentrale MessageManager.validate() für alle Gateways verwenden
- Tests: Echte MQTT-Payloads unverändert lassen, Code anpassen

**Erfolgs-Kriterium:**

- Meta-Parameter NIE in payload/message
- Alle Gateways verwenden MessageManager.validate()
- Tests zeigen saubere Trennung

### Task 1.2: Test-Stabilität wiederherstellen (KRITISCH)

**Abhängigkeit: Task 1.1 abgeschlossen**

**Antipattern beheben:** Agenten haben eingecheckt ohne Tests zu laufen

**Strategie:**

1. Jeden failing Test einzeln analysieren (kontext-abhängig)
2. NIEMALS echte MQTT-Testdaten ändern (Source of Truth!)
3. Code an Tests anpassen, nicht umgekehrt
4. Für jeden Test: Analyse → Rückfrage → Fix → Validierung

**Failing Tests (18):**

```
test_business_manager_pattern.py (2)
test_ccu_production_monitoring_subtab.py (2)
test_ccu_production_plan_subtab.py (1)
test_message_monitor_subtab.py (3)
test_registry_integration.py (5)
test_streamlit_dashboard.py (1)
test_streamlit_startup.py (1)
test_ui_components.py (3)
```

**Prozess pro Test:**

1. Test lesen und verstehen
2. Failure-Grund identifizieren
3. Echte MQTT-Daten prüfen (data/omf-data/test_topics/)
4. Kontext-abhängige Rückfrage an User
5. Fix implementieren
6. Test erneut laufen lassen

**Erfolgs-Kriterium:**

- 341/341 Tests bestehen ✅
- Keine Mock-Daten geändert
- Architektur-Compliance in allen Tests

### Task 1.3: TODO-Audit & Feature-Gap-Analyse

**Keine Abhängigkeiten - parallel zu 1.1/1.2 möglich**

```bash
# Alle TODOs finden
grep -r "TODO" omf2/ --include="*.py" > docs/TODO_AUDIT.md
# Kritische TODOs markieren
grep -r "TODO.*KRITISCH\|TODO.*CRITICAL" omf2/
```

**Kategorisierung:**

- CRITICAL: Messe-Blocker (z.B. Node-RED TODOs → STREICHEN)
- HIGH: Feature-Lücken (z.B. Auto-Refresh)
- MEDIUM: UI-Polish
- LOW: Nice-to-have

**Erfolgs-Kriterium:**

- Vollständige TODO-Liste in docs/TODO_AUDIT.md
- Priorisierung: CRITICAL > HIGH > MEDIUM > LOW
- Node-RED TODOs gestrichen (nicht Messe-relevant)

## Phase 2: KRITISCHE FEATURES (22. Okt - 4. Nov, 14 Tage)

### Task 2.1: Auto-Refresh Implementation

**Abhängigkeit: Task 1.2 (Tests grün)**

**MQTT-Trigger für UI-Refresh:**

- `ccu/order/active` → CCU Orders Tab
- `ccu/order/completed` → CCU Orders Tab
- `module/v1/ff/*/state` → CCU Modules Tab
- `/j1/txt/1/f/i/stock` → CCU Overview Tab (Inventory) ✅ **TOPIC KORREKT**
- `fts/v1/ff/*/state` → CCU Process Tab

**Pattern:**

```python
def on_mqtt_message(self, topic, message, meta):
    # 1. Verarbeite Message
    # 2. Update State-Holder
    # 3. Trigger UI-Refresh
    request_refresh()
```

**Erfolgs-Kriterium:**

- UI aktualisiert sich automatisch bei relevanten MQTT Messages
- Keine Performance-Probleme (max 1 Refresh/Sekunde)

### Task 2.2: Factory Layout Integration

**Abhängigkeit: Task 2.1 (Auto-Refresh)**

**Shopfloor 3×4 Grid wie in omf/:**

- Echte omf_* SVG-Icons (nicht ic_ft_* Fallback)
- Integration in CCU Configuration Tab
- Icon-Test mit `omf2/ui/common/icon_test.py`

**Erfolgs-Kriterium:**

- Factory Layout korrekt dargestellt
- Alle Module mit richtigen Icons
- Shopfloor-Grid responsive

## Phase 3: UI-POLISH & i18n (5. - 18. Nov, 14 Tage)

### Task 3.1: Sensor Data UI-Verbesserung

**Abhängigkeit: Phase 2 abgeschlossen**

- Temperatur-Skala mit Farbverlauf (Thermometer)
- Kamera-Controls verbessern (3×3 Grid)
- Bild-Anzeige implementieren

### Task 3.2: HTML-Templates i18n

**Abhängigkeit: Keine - parallel möglich**

- `omf2/assets/html_templates.py::get_workpiece_box_template()`
- Hardcoded Texte entfernen ("Bestand:", "Verfügbar:", "Ja", "Nein")
- Alle drei Sprachen (DE, EN, FR)

### Task 3.3: Production Order Manager Polish

**Abhängigkeit: Task 2.1 (Auto-Refresh)**

- STORAGE Orders mit storage-plan
- Order-Filterung & Sortierung
- Completed Orders limitieren (max 10)

### Task 3.4: Rollenbasierte Tab-Sichtbarkeit

**Abhängigkeit: Keine - parallel möglich**

**Messe-Relevanz:**

- Operator: CCU Overview, Orders, Process, Configuration, Modules
- Admin: Admin Settings, Message Center, System Logs, Steering
- ~~Supervisor: Node-RED~~ (GESTRICHEN - nicht Messe-relevant)

## Phase 4: LIVE-TESTING & FINAL POLISH (19. - 24. Nov, 6 Tage)

**ALLE Live-Test Sessions nur im Büro möglich - keine Remote-Abhängigkeit!**

### Task 4.1: Live-Test Session #1 (Baseline)

**Abhängigkeit: Phase 1 abgeschlossen + im Büro**

- omf2 mit echter Fabrik verbinden
- Alle CCU Tabs durchklicken
- Alle Admin Tabs durchklicken
- Fehler dokumentieren (wie Chat-C Protokoll)

### Task 4.2: Live-Test Session #2 (Regression)

**Abhängigkeit: Phase 2 abgeschlossen + im Büro**

- Vergleich mit Session #1
- Stock-Topic Validierung ✅ **BEREITS VALIDIERT**
- Auto-Refresh Validierung
- Factory Layout Validierung

### Task 4.3: Live-Test Session #3 (Workflows)

**Abhängigkeit: Phase 3 abgeschlossen + im Büro**

- Vollständige Workflows testen (Order → Production → Completion)
- Alle Rollen testen
- Alle Sprachen testen (DE, EN, FR)

### Task 4.4: Live-Test Session #4 (Marathon)

**Abhängigkeit: Task 4.3 + im Büro**

- 8h Dauerlauf mit echter Fabrik
- Stabilität unter Last
- Memory Leaks prüfen
- Performance messen

### Task 4.5: Messe-Präsentation vorbereiten

**Abhängigkeit: Task 4.4**

- Demo-Szenarien definieren (3-5 Szenarien à 5-10 Minuten)
- Backup-Strategie (Mock-Mode als Fallback)
- Quick Reference für Messe-Stand (DE/EN)
- User Guide (DE/EN/FR)

## Phase 5: MESSE-TAG (25. Nov)

### Task 5.1: Setup & Smoke-Test

**Abhängigkeit: Phase 4 abgeschlossen**

- Hardware-Verbindung prüfen (1h vor Messe-Start)
- Alle Environments testen (live, replay, mock)
- Emergency-Rollback vorbereiten

### Task 5.2: Messe-Standby

**Abhängigkeit: Task 5.1**

- Live-Monitoring während Demo
- Quick-Fixes bei Bedarf
- Feedback sammeln für Post-Messe Improvements

## Risiken & Mitigation

### KRITISCH (Messe-Blocker):

1. **18 failing Tests** → Phase 1 Task 1.2 (höchste Priorität)
2. **Command-Versende-Pattern** → Phase 1 Task 1.1 (SOFORT fix)
3. **Live-Fabrik-Zugriff** → Nur im Büro, Termine vorab planen

### HOCH:

1. ~~**Stock-Topic Fehler** → Phase 2 Task 2.1~~ ✅ **GELÖST**
2. **Auto-Refresh** → Phase 2 Task 2.1
3. **Factory Layout** → Phase 2 Task 2.2

### MITTEL:

1. **UI-Polish** → Phase 3 (kann reduziert werden)
2. **i18n Vollständigkeit** → Phase 3 (Basis funktioniert)
3. **Performance** → Phase 4 (wird in Marathon getestet)

### NIEDRIG:

1. **Rollenbasierte Tabs** → Kann manuell gesteuert werden
2. **Sensor Data Polish** → Nice-to-have

## Erfolgs-Kriterien

### MUST (Messe-Blocker wenn nicht erfüllt):

- ✅ 341/341 Tests bestehen
- ✅ Command-Versende-Pattern architektur-compliant
- ✅ Live-Demo funktioniert 100% (Session #4 erfolgreich)
- ✅ Keine MQTT Connection-Loops
- ✅ Core-Workflows (Orders, Production, Inventory) fehlerfrei

### SHOULD (Messe-Qualität reduziert wenn nicht erfüllt):

- ✅ Auto-Refresh funktioniert
- ✅ ~~Stock-Topic korrekt~~ ✅ **GELÖST**
- ✅ Factory Layout korrekt dargestellt
- ✅ Alle drei Sprachen funktionieren
- ✅ Rollenbasierte Tabs funktionieren

### NICE-TO-HAVE (Keine Auswirkung auf Messe):

- ⭕ Temperatur-Skala perfekt
- ⭕ Kamera-Controls polished
- ⭕ Order-Filterung komplett
- ⭕ Performance maximal optimiert

## Agent-Orchestrierung (KRITISCH)

### ANTIPATTERN VERMEIDEN:

- ❌ NIEMALS ohne Tests einchecken
- ❌ NIEMALS echte MQTT-Testdaten ändern
- ❌ NIEMALS ohne Rückfrage Tests "fixen"

### BEST PRACTICE:

1. **Analyse**: Code UND Tests lesen
2. **Rückfrage**: Kontext-abhängig bei jedem Test-Fix
3. **Implementierung**: Code an Tests anpassen (nicht umgekehrt)
4. **Validierung**: `pytest omf2/tests/ -v` MUSS grün sein
5. **Commit**: Nur wenn alle Tests grün

### Status-Tracking:

- **Täglich**: MESSE_PROGRESS.md aktualisieren
- **Wöchentlich**: Phase-Review + Risiko-Assessment
- **Critical**: Sofort eskalieren wenn Messe-Blocker

**Zeitbudget: 41 Tage bis Messe**

**Kritischer Pfad: Phase 1 (7d) → Phase 2 (14d) → Phase 3 (14d) → Phase 4 (6d)**

**Buffer: 0 Tage → KEINE Verzögerungen erlaubt bei MUST-Kriterien**

### To-dos

- [x] ~~KRITISCHER FIX: Stock-Topic /f/o/stock → /f/i/stock + StockManager Refactoring~~ ✅ **ABGESCHLOSSEN**
- [x] ~~Legacy-Cleanup: omf/ und registry/ Verzeichnisse löschen~~ ✅ **ABGESCHLOSSEN**
- [ ] Alle 18 failing Tests reparieren → 100% Test-Success
- [ ] Dokumentations-Audit: TODOs finden, Feature-Lücken identifizieren
- [ ] Live-Test Session #1 mit echter Fabrik durchführen
- [ ] Auto-Refresh bei MQTT Messages implementieren
- [ ] Live-Test Session #2: Regression-Check und Vergleich mit Session #1
- [ ] Factory Layout: 3×4 Grid mit echten omf_* SVG-Icons
- [ ] Sensor Data UI: Temperatur-Skala, Kamera-Controls, Bild-Anzeige
- [ ] Production Order Manager: STORAGE Orders, Filterung, Limitierung
- [ ] Node-RED MQTT Clients: Environment-Switch, Registry-Topics
- [ ] HTML-Templates i18n: Workpiece-Box übersetzen (DE/EN/FR)
- [ ] Live-Test Session #3: Workflows, Rollen, Sprachen komplett testen
- [ ] Performance-Optimierung: MQTT, UI-Rendering, Memory Leaks
- [ ] Error-Handling Audit: User-friendly Messages, Fallbacks
- [ ] Rollenbasierte Tab-Sichtbarkeit: Operator/Supervisor/Admin
- [ ] Live-Test Session #4: 8h Dauerlauf mit echter Fabrik
- [ ] Dokumentation: User Guide, Quick Reference, Troubleshooting (DE/EN/FR)
- [ ] Messe-Präsentation: Demo-Szenarien, Backup-Strategie, Installation
- [ ] Messe-Setup: Hardware-Check, Environment-Tests, Emergency-Rollback
- [ ] Messe-Standby: Monitoring, Quick-Fixes, Feedback sammeln
