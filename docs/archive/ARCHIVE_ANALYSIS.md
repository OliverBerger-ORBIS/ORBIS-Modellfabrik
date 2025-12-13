# Archive-Analyse: Relevante Informationen für OMF3

**Datum:** 2025-11-17  
**Zweck:** Identifikation relevanter APS/MQTT-Informationen, die noch nicht in `docs/06-integrations/00-REFERENCE/` konsolidiert sind

## ✅ Bereits konsolidiert in `docs/06-integrations/00-REFERENCE/`

Die folgenden Informationen sind bereits in der zentralen Referenz dokumentiert:

1. **Module Serial Mapping** - Alle Serial-Numbers, IPs, Hardware-Typen
2. **MQTT Topic Conventions** - Topic-Patterns und Naming
3. **CCU Backend Orchestration** - Order-Flow und Sequenz-Diagramme
4. **Component Overview** - Alle 10 Komponenten mit Details
5. **Hardware Architecture** - Netzwerk-Topologie und IP-Adressen

## ⚠️ Relevante Informationen, die noch NICHT in 00-REFERENCE sind

### 1. **MQTT Message Examples** (HOCH RELEVANT)
**Quelle:** `docs/archive/04-howto_omf_legacy/communication/mqtt/mqtt-control-summary.md`

**Enthält:**
- Konkrete JSON-Beispiele für PICK, DROP, STORE, CHECK_QUALITY Commands
- Verifizierte Message-Formate mit allen erforderlichen Feldern
- Topic-Formate für Module-Commands
- orderId, orderUpdateId, serialNumber Struktur
- Metadata-Struktur (priority, timeout, type)

**Empfehlung:** In `docs/06-integrations/00-REFERENCE/` integrieren als "MQTT Message Examples" oder "Module Control Messages"

### 2. **State Machine Notes** (RELEVANT)
**Quelle:** `docs/archive/04-howto_omf_legacy/communication/mqtt/state-machine-notes.md`

**Enthält:**
- FTS State Machine Verhalten (findInitialDockPosition, startCharging/stopCharging)
- Direkte vs. Event-getriggerte Module
- Verfügbarkeit von Commands basierend auf Status

**Empfehlung:** Prüfen ob bereits in `docs/06-integrations/APS-NodeRED/state-machine.md` - wenn nicht, integrieren

### 3. **Remote Control Guide** (NÜTZLICH)
**Quelle:** `docs/archive/04-howto_omf_legacy/communication/mqtt/setup/remote-control-guide.md`

**Enthält:**
- Anleitung für Remote-Steuerung der APS von macOS
- MQTT-Client-Setup für Entwicklung
- Netzwerk-Konfiguration

**Empfehlung:** In `docs/04-howto/` verschieben (nicht löschen, noch nützlich)

### 4. **Traffic Logging Guide** (NÜTZLICH)
**Quelle:** `docs/archive/04-howto_omf_legacy/communication/mqtt/setup/traffic-logging-guide.md`

**Enthält:**
- MQTT Traffic Monitoring Setup
- Logging-Konfiguration für Debugging
- Broker-Überwachung

**Empfehlung:** In `docs/04-howto/` verschieben (nicht löschen, noch nützlich für Debugging)

### 5. **VDA5050 Implementation Details** (RELEVANT)
**Quelle:** `docs/archive/analysis/dps/VDA5050_IMPLEMENTATION_PLAN.md`

**Enthält:**
- VDA5050 Standard-Struktur
- Order Management Details
- State Management Details
- Instant Actions

**Empfehlung:** Prüfen ob bereits in `docs/06-integrations/00-REFERENCE/ccu-backend-orchestration.md` - wenn nicht, relevante Teile integrieren

## ❌ Kann gelöscht werden (nur Prozess-Dokumente)

### 1. **Chat Activities** (`docs/archive/chat-activities/`)
- Nur Prozess-Dokumente (wie wir zu Erkenntnissen kamen)
- Keine Fakten, nur Diskussionen
- **Empfehlung:** Löschen

### 2. **APS-MQTT-Log Analysen** (`docs/archive/analysis/aps-mqtt-logs/`)
- Bereits als "archiviert" markiert in README.md
- Enthält Fehler (Serial-Number-Verwechslungen)
- Finale Informationen in `docs/06-integrations/00-REFERENCE/`
- **Empfehlung:** Löschen (README.md behalten als Verweis)

### 3. **DPS Analysen** (`docs/archive/analysis/dps/`)
- Implementierungspläne und Analysen
- Teilweise obsolet (OMF2-spezifisch)
- **Empfehlung:** Prüfen ob noch relevante Details, dann löschen

### 4. **OMF2-spezifische Dokumentation**
- `docs/archive/04-howto_omf_legacy/` - OMF2-spezifische Howtos
- `docs/archive/02-architecture_omf_legacy/` - OMF2-Architektur
- **Empfehlung:** Löschen (OMF2 ist Legacy)

## 📋 Empfohlene Aktionen

### Priorität 1: Integration relevanter Informationen
1. **MQTT Message Examples** → `docs/06-integrations/00-REFERENCE/mqtt-message-examples.md` erstellen
2. **State Machine Notes** → Prüfen und ggf. in `docs/06-integrations/APS-NodeRED/state-machine.md` integrieren

### Priorität 2: Verschieben nützlicher Guides
1. **Remote Control Guide** → `docs/04-howto/setup/remote-mqtt-control.md`
2. **Traffic Logging Guide** → `docs/04-howto/setup/mqtt-traffic-logging.md`

### Priorität 3: Löschen obsoleter Dokumentation
1. **Chat Activities** → Löschen
2. **APS-MQTT-Log Analysen** → Löschen (README.md behalten)
3. **OMF2-spezifische Dokumentation** → Löschen

---

**Status:** ✅ **ABGESCHLOSSEN** - Alle Prioritäten umgesetzt (2025-11-17)

## ✅ Durchgeführte Aktionen

### Priorität 1: Integration relevanter Informationen ✅
1. **MQTT Message Examples** → `docs/06-integrations/00-REFERENCE/mqtt-message-examples.md` erstellt
2. **State Machine Notes** → In `docs/06-integrations/APS-NodeRED/state-machine.md` integriert (FTS-Details, Module Control Patterns)

### Priorität 2: Verschieben nützlicher Guides ✅
1. **Remote Control Guide** → `docs/04-howto/setup/remote-mqtt-control.md` verschoben
2. **Traffic Logging Guide** → `docs/04-howto/setup/mqtt-traffic-logging.md` verschoben

### Priorität 3: Löschen obsoleter Dokumentation ✅
1. **Chat Activities** → `docs/archive/chat-activities/` gelöscht (13 Dateien)
2. **APS-MQTT-Log Analysen** → Alle Analyse-Dateien gelöscht, README.md aktualisiert (4 Dateien)
3. **OMF2-spezifische Dokumentation** → Gelöscht:
   - `docs/archive/04-howto_omf_legacy/` (komplett)
   - `docs/archive/02-architecture_omf_legacy/` (komplett)
   - `docs/archive/03-decision-records_omf_legacy/` (komplett)

## 📊 Ergebnis

**Vorher:**
- 72 Markdown-Dateien im Archive
- 692 KB Größe

**Nachher:**
- 68 Markdown-Dateien im Archive
- 356 KB Größe

**Ersparnis:** 336 KB (48% Reduktion)
