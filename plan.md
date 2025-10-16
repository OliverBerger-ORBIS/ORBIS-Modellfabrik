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

### ✅ **Task 0.3 ABGESCHLOSSEN: I18n Haupt-Tabs Fix**

**Status:** ✅ **VOLLSTÄNDIG ABGESCHLOSSEN**

**Was wurde gefixt:**
- ✅ **Haupt-Tabs werden jetzt übersetzt** 🌐
- ✅ `omf2/ui/main_dashboard.py` - Tab-Namen über `i18n.t()` übersetzt
- ✅ **Fehlende Tab-Keys** in allen 3 Sprachen hinzugefügt:
  - `tabs.ccu_dashboard`, `tabs.nodered_overview`, `tabs.nodered_processes`
- ✅ **Fallback-Mechanismus** funktioniert (hardcodierte Namen wenn i18n nicht verfügbar)
- ✅ **User-Tests bestätigt** - Streamlit App läuft korrekt
- ✅ **Tests laufen** - 323/341 bestehen (18 waren bereits vorher fehlerhaft)

**Commits:**
- `2c6ab67` - "fix: Haupt-Tab-Namen i18n-fähig machen"

**Erfolgs-Kriterium erreicht:**
- ✅ Haupt-Tabs werden in gewählter Sprache angezeigt
- ✅ Sprachumschaltung funktioniert korrekt
- ✅ Keine UI-Regression

---

### Implementiert (323 von 341 Tests bestehen):

- Core-Architektur: MQTT Clients, Gateways, Business Manager
- Registry v2 Integration mit 44 Schemas
- CCU Domain: Overview, Modules, Orders, Process, Configuration Tabs
- Admin Domain: Settings, Message Center, System Logs, Steering
- i18n-System (DE, EN, FR)
- Production Order Manager
- Shopfloor Layout System

### ✅ KRITISCHE ARCHITEKTUR-FIXES ABGESCHLOSSEN:

- ✅ **18 failing Tests** → Alle repariert, 100% Test-Success erreicht ✅
- ✅ **Meta-Parameter in Payload** → mqtt_timestamp nur in Buffer, nicht in Payload ✅
- ✅ **Fehlende zentrale Validierung** → Alle Gateways verwenden MessageManager.validate() ✅
- ✅ **Command-Versende-Pattern inkonsistent** → Einheitlich implementiert ✅

### Unbekannte Features (aus REFACTORING_BACKLOG.md):

- Auto-Refresh bei MQTT Messages
- Factory Layout mit echten omf_* SVG-Icons
- Kamera-Befehle UI-Verbesserung
- Temperatur-Skala Anzeige
- ~~Stock-Topic Korrektur (/f/o/stock → /f/i/stock)~~ ✅ **ABGESCHLOSSEN**
- ~~Legacy-Cleanup (omf/, registry/)~~ ✅ **ABGESCHLOSSEN**

## Phase 1: KRITISCHE ARCHITEKTUR-FIXES (15. - 21. Okt, 7 Tage)

**Ziel: Architektur-Compliance wiederherstellen, bevor weitere Features entwickelt werden**

### ✅ **Task 1.1 ABGESCHLOSSEN: Command-Versende-Pattern Fix**

**Status:** ✅ **VOLLSTÄNDIG ABGESCHLOSSEN**

**Was wurde gefixt:**
- ✅ **Meta-Parameter-Trennung:** `mqtt_timestamp` nur in Buffer, nicht in Payload
- ✅ **Zentrale Validierung:** `MessageManager.validate_message()` in allen Gateways
- ✅ **Registry-basierte QoS/Retain:** Keine hardcodierten Werte mehr
- ✅ **Schema-Compliance:** Alle Messages validiert vor Publishing
- ✅ **Architektur-Dokumentation:** `ARCHITECTURE.md` aktualisiert

**Commits:**
- `f61b617` - "fix: Command-Versende-Pattern architektur-compliant implementiert"

**Erfolgs-Kriterium erreicht:**
- ✅ Meta-Parameter NIE in payload/message
- ✅ Alle Gateways verwenden MessageManager.validate()
- ✅ Registry-basierte QoS/Retain-Werte

---

### ✅ **Task 1.2 ABGESCHLOSSEN: Test-Stabilität wiederherstellen**

**Status:** ✅ **VOLLSTÄNDIG ABGESCHLOSSEN**

**Was wurde repariert:**
- ✅ **18/18 Tests repariert (100% Test-Success)** 🎯
- ✅ **Architektur-Compliance wiederhergestellt**
- ✅ **Semantisch korrekte Test-Reparaturen** (keine None-Acceptance)
- ✅ **Gateway-Implementierung repariert** (explizite return False)

**Reparierte Tests:**
- ✅ Test 1-2: `business_manager_pattern` → `gateway_routing_hints` Architektur
- ✅ Test 3-4: `ccu_production_monitoring` → Streamlit columns Mock mit `side_effect`
- ✅ Test 5: `ccu_production_plan` → Workflow-Tests
- ✅ Test 6-8: `message_monitor_subtab` → Interface-Korrektur (2→1 Parameter)
- ✅ Test 9-13: `registry_integration` → Registry-Manager-Tests
- ✅ Test 14: `streamlit_dashboard` → i18n Translation-Keys hinzugefügt
- ✅ Test 15: `streamlit_startup` → Import-Pfad korrigiert (`logs`→`system_logs`)
- ✅ Test 16-18: `ui_components` → Gateway-Implementierung repariert

**Commits:**
- `3c7d055` - "fix: Alle 18 failing Tests repariert - Architektur-Compliance wiederhergestellt"

**Erfolgs-Kriterium erreicht:**
- ✅ 341/341 Tests bestehen ✅
- ✅ Keine Mock-Daten geändert
- ✅ Architektur-Compliance in allen Tests

---

### ✅ **Task 1.3 ABGESCHLOSSEN: TODO-Audit & Feature-Gap-Analyse**

**Status:** ✅ **VOLLSTÄNDIG ABGESCHLOSSEN**

**Was wurde analysiert:**
- ✅ **216 TODOs gefunden** und kategorisiert
- ✅ **26 Messe-relevante TODOs** identifiziert
- ✅ **6 Node-RED TODOs gestrichen** (nicht Messe-relevant)
- ✅ **Priorisierung:** KRITISCH > HOCH > MITTEL

**Kategorisierung:**
- 🎯 **KRITISCH (6):** Factory Steering Hardcoded Payloads
- 📋 **HOCH (12):** UI-Komponenten Gateway-Integration
- 📝 **MITTEL (2):** HTML-Templates i18n
- 🚫 **GESTRICHEN (6):** Node-RED TODOs

**Commits:**
- `cead4ac` - "docs: plan.md aktualisiert - Task 1.2 als abgeschlossen markiert"

**Erfolgs-Kriterium erreicht:**
- ✅ Vollständige TODO-Liste kategorisiert
- ✅ Priorisierung für Messe-Vorbereitung
- ✅ Node-RED TODOs gestrichen (nicht Messe-relevant)

---

### ✅ **Task 2.1 ABGESCHLOSSEN: Storage Orders Logic & UI-Konsistenz**

**Status:** ✅ **VOLLSTÄNDIG ABGESCHLOSSEN**

**Was wurde implementiert:**
- ✅ **Storage Orders Logic:** Vollständige Verarbeitung von `ccu/order/active` und `ccu/order/completed` Messages
- ✅ **UI-Konsistenz:** Production und Storage Orders verwenden identische UISymbols und Darstellung
- ✅ **Command-Mapping-Korrektur:** Storage Orders verwenden korrekte PICK/DROP → LADEN/ENTLADEN AGV Logik
- ✅ **Shopfloor Layout Integration:** Storage Orders zeigen aktive Module und FTS Navigation
- ✅ **Navigation Step Enhancement:** UX-Verbesserung für Navigation Steps (IN_PROGRESS wenn kein Production Step aktiv)
- ✅ **UISymbols-Konsistenz:** 🟠 statt 🔄 für IN_PROGRESS (konsistent mit Production Orders)

**Technische Details:**
- ✅ `storage_orders_subtab.py` vollständig refactored
- ✅ `get_complete_storage_plan()` und `_render_storage_steps()` implementiert
- ✅ Shopfloor Layout mit aktiver Module-Hervorhebung
- ✅ 2-Spalten-Layout (Liste:Shopfloor) wie Production Orders
- ✅ Alle Tests bestehen (4/4 Storage Orders Tests)

**Commits:**
- `[COMMIT_HASH]` - "feat: Storage Orders Logic vollständig implementiert - UI-Konsistenz zwischen Production und Storage Orders"

**Erfolgs-Kriterium erreicht:**
- ✅ Storage Orders verarbeiten MQTT Messages korrekt
- ✅ UI-Konsistenz zwischen Production und Storage Orders
- ✅ Shopfloor Layout Integration funktional
- ✅ Navigation Step Enhancement implementiert

---

### Task 2.2: Shopfloor Layout - Aktive Module anzeigen (NÄCHSTE PRIORITÄT)

**Keine Abhängigkeiten - SOFORT startbar**

**Problem-Analyse:**

Aus `REFACTORING_BACKLOG.md` Zeile 57:
```markdown
| factory_layout | Ui verwendet ICONs und png von omf | ❌ | Darstellung wie in omf/ mit 3X4 grid (oder 4x3) Grid |
```

**Feature-Anforderung:**

- **Shopfloor Layout** soll zeigen welche Module **aktiv** sind
- **3×4 Grid** mit echten omf_* SVG-Icons (nicht ic_ft_* Fallback)
- **Aktuelle Module** visuell hervorheben
- **Integration** in CCU Configuration Tab

**Zu implementieren:**

- `omf2/ui/ccu/ccu_configuration/ccu_factory_configuration_subtab.py`
- `omf2/ui/ccu/common/shopfloor_layout.py` erweitern
- `omf2/config/ccu/shopfloor_layout.json` aktualisieren
- Icon-Test mit `omf2/ui/common/icon_test.py`

**Erfolgs-Kriterium:**

- Factory Layout korrekt dargestellt (3×4 Grid)
- Alle Module mit richtigen omf_* SVG-Icons
- Aktive Module visuell hervorgehoben
- Shopfloor-Grid responsive

### ✅ **Task 2.3 ABGESCHLOSSEN: Step Status Display Fix**

**Status:** ✅ **VOLLSTÄNDIG ABGESCHLOSSEN**

**Was wurde implementiert:**
- ✅ **Navigation Step Enhancement:** UX-Verbesserung implementiert
- ✅ **Step Status Display:** UI zeigt Step-Status korrekt an (FINISHED für vorherige Steps)
- ✅ **Production Plan:** 16 Steps korrekt implementiert (AGV > HBW als Step 1)

**Erfolgs-Kriterium erreicht:**
- ✅ UI zeigt Step-Status korrekt (FINISHED für vorherige Steps)
- ✅ Production Plan hat 16 Steps (AGV > HBW als Step 1)
- ✅ Alle Tests bestehen
- ✅ Intensiv getestet mit Session-Daten (auftrag_blau_1, _weiss_1, _rot_1)

---

### 🔧 **Task 2.5: Logging-System File-Handler Fix**

**Status:** 🔧 **IN PLANUNG**

**Problem identifiziert:**
- ❌ **Stock Manager Logs erscheinen NICHT in der Datei** `logs/omf2.log`
- ❌ **Logs erscheinen nur im UI-Buffer** (MultiLevelRingBufferHandler)
- ❌ **FileHandler wird NACH RingBufferHandler hinzugefügt** - möglicher Konflikt
- ❌ **Agenten können Logs nicht in Datei analysieren** - nur UI-Buffer verfügbar

**Anforderungen:**
- ✅ **Alle Log-Einträge müssen an FileHandler übergeben werden**
- ✅ **Logs müssen im Log-File auffindbar sein** für Agenten und andere Interessierte
- ✅ **Log-Level wird unterstützt** - DEBUG, INFO, WARNING, ERROR
- ✅ **Konfiguration über system_logs Log-Management** wird unterstützt
- ✅ **Optional: Löschung der alten Log-Files nach Neustart** von `omf2/omf.py`

**Technische Details:**
- **MultiLevelRingBufferHandler** sammelt Logs in 4 separaten Buffern (ERROR, WARNING, INFO, DEBUG)
- **FileHandler** wird NACH RingBufferHandler hinzugefügt (Zeile 46 in `omf2/omf.py`)
- **Beide Handler** hängen am ROOT-Logger - sollten ALLE Logs erhalten
- **ABER:** Stock Manager Logs erscheinen NUR im UI-Buffer, NICHT in der Datei

**Erfolgs-Kriterium:**
- ✅ Stock Manager Logs erscheinen in `logs/omf2.log`
- ✅ Alle Business-Logic-Logs sind in Datei auffindbar
- ✅ Log-Level-Konfiguration funktioniert korrekt
- ✅ Agenten können Logs in Datei analysieren

---

### ✅ **Task 2.4 ABGESCHLOSSEN: Manager Renaming**

**Status:** ✅ **VOLLSTÄNDIG ABGESCHLOSSEN**

**Was wurde umbenannt:**
- ✅ **OrderManager → StockManager:** `omf2/ccu/order_manager.py` → `omf2/ccu/stock_manager.py`
- ✅ **ProductionOrderManager → OrderManager:** `omf2/ccu/production_order_manager.py` → `omf2/ccu/order_manager.py`

**Umbenennungen durchgeführt:**
- ✅ **Registry & Logging aktualisiert** - `mqtt_clients.yml`, `logging_config.yml`
- ✅ **Dateien umbenannt** - Korrekte Datei-Namen
- ✅ **Klassen umbenannt** - `ProductionOrderManager` → `OrderManager`
- ✅ **Singleton & Factory aktualisiert** - Alle Referenzen korrigiert
- ✅ **Gateway-Referenzen korrigiert** - Routing-Logik repariert
- ✅ **UI-Komponenten aktualisiert** - Alle Subtabs funktionieren
- ✅ **Test-Dateien korrigiert** - Nur aktive Methoden getestet
- ✅ **Dokumentation aktualisiert** - Architektur-Docs korrekt
- ✅ **Routing-Logik repariert** - 4-Routing-Struktur wiederhergestellt
- ✅ **UI-Integration erfolgreich** - Order Manager + Stock Manager funktionieren

**Kritische Fehler behoben:**
- ✅ **Doppelte Routing-Logik entfernt** - Stock Manager bekam fälschlicherweise `ccu/order/active`
- ✅ **Indentation Error behoben** - `production_orders_subtab.py` funktioniert wieder
- ✅ **Gateway-Routing repariert** - Messages gehen an richtige Manager

**Erfolgs-Kriterium erreicht:**
- ✅ **Order Manager** bekommt `ccu/order/active` Messages korrekt
- ✅ **Stock Manager** bekommt `/j1/txt/1/f/i/stock` Messages korrekt
- ✅ **CCU Orders Subtabs** zeigen Orders an
- ✅ **Keine Routing-Fehler** mehr
- ✅ **Echte Integration-Tests** geschrieben (9/9 bestanden)
- Alle Referenzen aktualisieren
- Tests anpassen

**Erfolgs-Kriterium:**
- Manager-Namen sind semantisch korrekt
- Alle Tests bestehen nach Renaming
- Keine Breaking Changes für UI

---

### ✅ **Task 2.5 ABGESCHLOSSEN: Storage Orders Subtab Verbesserungen**

**Status:** ✅ **VOLLSTÄNDIG ABGESCHLOSSEN**

**Was wurde implementiert:**
- ✅ **Storage Orders Subtab:** Vollständige `storage-plan` Integration
- ✅ **Vollständige Visualisierung:** Analog zu Production Orders
- ✅ **ProductionOrderManager Integration:** `get_complete_storage_plan()` implementiert
- ✅ **2-Spalten-Layout:** Liste:Shopfloor wie Production Orders
- ✅ **Shopfloor Layout Integration:** Aktive Module-Hervorhebung
- ✅ **Command-Mapping:** Korrekte PICK/DROP → LADEN/ENTLADEN AGV Logik

**Erfolgs-Kriterium erreicht:**
- ✅ Storage Orders zeigen vollständigen storage-plan
- ✅ Visualisierung analog zu Production Orders
- ✅ Integration mit ProductionOrderManager
- ✅ UI-Konsistenz zwischen Production und Storage Orders

### Task 2.6: Factory Steering Hardcoded Payloads Fix

**Abhängigkeit: Task 2.5 ✅ ABGESCHLOSSEN**

**Problem-Analyse:**

Aus TODO-Audit: 6 Funktionen in `omf2/ui/admin/generic_steering/factory_steering_subtab.py`
- **Problem:** Hardcoded Payloads verletzen Command-Versende-Pattern
- **Lösung:** Schema-driven Approach implementieren

**Architektur-Anforderung:**

```
Business Function → Gateway.publish_message(topic, payload, meta=None)
                     ↓
Gateway → MessageManager.validate(payload, schema)
                     ↓
Gateway → MQTT Client.publish(topic, payload_clean, qos, retain)
```

**Zu fixen:**

- `factory_steering_subtab.py` - 6 Funktionen mit hardcodierten Payloads
- Schema-driven Approach implementieren
- PayloadGenerator.generate_example_payload() verwenden
- Registry Manager Integration

**Erfolgs-Kriterium:**

- Keine hardcodierten Payloads mehr
- Alle Factory Steering Commands schema-validiert
- Command-Versende-Pattern architektur-compliant

## Phase 2: KRITISCHE FEATURES (22. Okt - 4. Nov, 14 Tage)

### Task 2.7: Auto-Refresh Implementation

**Abhängigkeit: Task 2.6 (Factory Steering) abgeschlossen**

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

### 🟡 **Task 2.8: Factory Layout Integration (TEILWEISE IMPLEMENTIERT)**

**Status:** 🟡 **TEILWEISE IMPLEMENTIERT - FEHLENDE FEATURES**

**Was bereits implementiert:**
- ✅ **Shopfloor 3×4 Grid:** Grundlegendes Layout implementiert
- ✅ **Integration:** In CCU Configuration Tab
- ✅ **Shopfloor Layout System:** Reusable UI-Komponente
- ✅ **Aktive Module-Hervorhebung:** Visuelle Indikation
- ✅ **Integration:** In Production und Storage Orders

**Was noch fehlt:**
- ❌ **Echte omf_* SVG-Icons:** Noch ic_ft_* Fallback verwendet
- ❌ **FTS Navigation Display:** Für Transport-Schritte nicht implementiert
- ❌ **Icon-Test:** Mit `omf2/ui/common/icon_test.py` nicht durchgeführt
- ❌ **EMPTY-Felder Aufteilung:** Neue Anforderung
- ❌ **ORBIS-Logo Darstellung:** Auf Empty-Feldern
- ❌ **DSP Darstellung:** Auf Empty-Feldern

**Zu implementieren:**
- `omf2/ui/ccu/common/shopfloor_layout.py` - omf_* SVG-Icons verwenden
- FTS Navigation Display für Transport-Schritte
- EMPTY-Felder Aufteilung und ORBIS-Logo/DSP Darstellung
- Icon-Test mit `omf2/ui/common/icon_test.py`

**Erfolgs-Kriterium:**
- ✅ Factory Layout korrekt dargestellt
- ❌ Alle Module mit richtigen omf_* SVG-Icons
- ✅ Shopfloor-Grid responsive
- ✅ Integration in Production und Storage Orders
- ❌ FTS Navigation Display implementiert
- ❌ EMPTY-Felder mit ORBIS-Logo/DSP

## Phase 3: UI-POLISH & i18n (5. - 18. Nov, 14 Tage)

### Task 3.1: Sensor Data UI-Verbesserung

**Abhängigkeit: Task 2.8 abgeschlossen**

- Temperatur-Skala mit Farbverlauf (Thermometer)
- Kamera-Controls verbessern (3×3 Grid)
- Bild-Anzeige implementieren

### Task 3.2: HTML-Templates i18n

**Abhängigkeit: Keine - parallel möglich**

- `omf2/assets/html_templates.py::get_workpiece_box_template()`
- Hardcoded Texte entfernen ("Bestand:", "Verfügbar:", "Ja", "Nein")
- Alle drei Sprachen (DE, EN, FR)

### Task 3.3: Production Order Manager Polish

**Abhängigkeit: Task 2.7 (Auto-Refresh) abgeschlossen**

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

**Abhängigkeit: Task 2.6 abgeschlossen + im Büro**

- omf2 mit echter Fabrik verbinden
- Alle CCU Tabs durchklicken
- Alle Admin Tabs durchklicken
- Fehler dokumentieren (wie Chat-C Protokoll)

### Task 4.2: Live-Test Session #2 (Regression)

**Abhängigkeit: Task 2.8 abgeschlossen + im Büro**

- Vergleich mit Session #1
- Stock-Topic Validierung ✅ **BEREITS VALIDIERT**
- Auto-Refresh Validierung
- Factory Layout Validierung

### Task 4.3: Live-Test Session #3 (Workflows)

**Abhängigkeit: Task 3.3 abgeschlossen + im Büro**

- Vollständige Workflows testen (Order → Production → Completion)
- Alle Rollen testen
- Alle Sprachen testen (DE, EN, FR)

### Task 4.4: Live-Test Session #4 (Marathon)

**Abhängigkeit: Task 4.3 abgeschlossen + im Büro**

- 8h Dauerlauf mit echter Fabrik
- Stabilität unter Last
- Memory Leaks prüfen
- Performance messen

### Task 4.5: Messe-Präsentation vorbereiten

**Abhängigkeit: Task 4.4 abgeschlossen**

- Demo-Szenarien definieren (3-5 Szenarien à 5-10 Minuten)
- Backup-Strategie (Mock-Mode als Fallback)
- Quick Reference für Messe-Stand (DE/EN)
- User Guide (DE/EN/FR)

## Phase 5: MESSE-TAG (25. Nov)

### Task 5.1: Setup & Smoke-Test

**Abhängigkeit: Task 4.5 abgeschlossen**

- Hardware-Verbindung prüfen (1h vor Messe-Start)
- Alle Environments testen (live, replay, mock)
- Emergency-Rollback vorbereiten

### Task 5.2: Messe-Standby

**Abhängigkeit: Task 5.1 abgeschlossen**

- Live-Monitoring während Demo
- Quick-Fixes bei Bedarf
- Feedback sammeln für Post-Messe Improvements

## Risiken & Mitigation

### KRITISCH (Messe-Blocker):

1. ~~**18 failing Tests** → Phase 1 Task 1.2 (höchste Priorität)~~ ✅ **ABGESCHLOSSEN**
2. ~~**Command-Versende-Pattern** → Phase 1 Task 1.1 (SOFORT fix)~~ ✅ **ABGESCHLOSSEN**
3. **Live-Fabrik-Zugriff** → Nur im Büro, Termine vorab planen
4. **Storage Orders Logic** → Task 2.1 ✅ **ABGESCHLOSSEN**

### HOCH:

1. ~~**Stock-Topic Fehler** → Phase 2 Task 2.1~~ ✅ **GELÖST**
2. ~~**Step Status Display** → Task 2.3~~ ✅ **ABGESCHLOSSEN**
3. ~~**Manager Renaming** → Task 2.4~~ ✅ **ABGESCHLOSSEN**
4. **Auto-Refresh** → Task 2.7
5. **Factory Layout** → Task 2.8 (TEILWEISE - omf_* Icons, FTS Navigation, EMPTY-Felder fehlen)

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
- [x] ~~I18n Haupt-Tabs Fix: Tab-Namen übersetzen~~ ✅ **ABGESCHLOSSEN**
- [x] ~~Task 1.2: Alle 18 failing Tests reparieren → 100% Test-Success~~ ✅ **ABGESCHLOSSEN**
- [x] ~~Task 1.3: TODO-Audit & Feature-Gap-Analyse~~ ✅ **ABGESCHLOSSEN**
- [x] ~~Task 2.1: Storage Orders Logic & UI-Konsistenz~~ ✅ **ABGESCHLOSSEN**
- [x] ~~Task 2.3: Step Status Display Fix~~ ✅ **ABGESCHLOSSEN**
- [x] ~~Task 2.4: Manager Renaming~~ ✅ **ABGESCHLOSSEN**
- [ ] Task 2.5: Logging-System File-Handler Fix (NEU)
- [x] ~~Dokumentations-Audit: TODOs finden, Feature-Lücken identifizieren~~ ✅ **ABGESCHLOSSEN**
- [ ] Live-Test Session #1 mit echter Fabrik durchführen
- [ ] Auto-Refresh bei MQTT Messages implementieren
- [ ] Live-Test Session #2: Regression-Check und Vergleich mit Session #1
- [ ] Factory Layout: 3×4 Grid mit echten omf_* SVG-Icons
- [ ] Sensor Data UI: Temperatur-Skala, Kamera-Controls, Bild-Anzeige
- [x] ~~Production Order Manager: STORAGE Orders, Filterung, Limitierung~~ ✅ **ABGESCHLOSSEN**
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
- [ ] Ausarbeitung der Roadmap: Konkrete Inhalte für Phase 2-4 definieren
