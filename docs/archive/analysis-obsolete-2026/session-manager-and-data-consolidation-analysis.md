# Analyse: Session-Manager & Data-Konsolidierung

**Erstellt:** 2026-03-02  
**Ziel:** Tiefe Analyse der Session-Manager-Funktionalität, Data-Pfade und Preloads – mit Plan und abstimmbaren Todos.

---

## 1. Session-Manager – Funktionalitätsanalyse

### 1.1 Übersicht der Tabs

| Tab | Zweck | IM Einsatz | Bewertung |
|-----|-------|------------|-----------|
| **📡 Replay Station** | Sessions abspielen, Preloads senden, Test-Topics | ✅ **Ja** | **Kern-Feature** – zentral für osf-ui Replay-Tests |
| **🎙️ Session Recorder** | MQTT-Sessions aufnehmen (SQLite + Log) | ⚠️ Gelegentlich | **Behalten** – für neue Sessions nach Topic-Änderungen |
| **📊 Session Analyse** | Timeline, Payload-Sequenz, Order-Flow, Auftrag-Analyse | ❓ Unklar | **Prüfen** – externe Scripts übernehmen Analyse |
| **📂 Topic Recorder** | Erste Message pro Topic speichern (→ Test-Daten) | ✅ **Behalten** | **Behalten** – echte Beispielnachrichten für Analyse, DSP-Weitergabe, Logik-Rekonstruktion |
| **⚙️ Einstellungen** | Pfade, MQTT-Broker | ✅ Ja | Behalten |
| **📝 Logging** | Log-Level, Live-Viewer | ✅ Ja | Behalten |

### 1.2 Replay Station – ✅ Behalten

- **Funktion:** Session-Dateien abspielen, Preloads senden, individuelle Test-Topics
- **Einsatz:** Replay-Tests osf-ui ohne APS
- **Preloads:** `data/osf-data/test_topics/preloads/*.json` – alle werden gesendet
- **Sessions:** `data/osf-data/sessions/*.db`, `*.log`

### 1.3 Session Recorder – ✅ Behalten

- **Funktion:** Live-MQTT aufnehmen → SQLite + Log
- **Einsatz:** Neue Sessions nach Änderungen (z.B. `request-id` in ccu/order/request)
- **Speicherort:** `data/osf-data/sessions/`
- **Empfehlung:** Behalten, Dokumentation aktualisieren

### 1.4 Session Analyse – ⚠️ Prüfen / Reduzieren

- **Funktion:** Timeline, Payload-Sequenz, Order-Flow (order_analyzer, auftrag_rot_analyzer)
- **Alternative:** Externe Scripts `scripts/analyze_*_sessions.py` (dps, hbw, mill, drill, fts, aiqs)
- **Befund:** Analyse-Tab und Scripts überschneiden sich. Scripts erzeugen JSON in `data/osf-data/*-analysis/`
- **Optionen:**
  - **A) Behalten** – wenn interaktive UI für schnelle Ad-hoc-Analyse genutzt wird
  - **B) Reduzieren** – nur Timeline + Payload-Sequenz, Order/Auftrag-Analyse entfernen
  - **C) Entfernen** – komplett, Nutzer nutzen Scripts

### 1.5 Topic Recorder – ✅ Behalten

- **Funktion:** Erste Message pro Topic speichern → echte Beispielnachrichten
- **Ziel-Pfad:** `data/aps-data/topics/` (bzw. `data/osf-data/` nach Konsolidierung)
- **Sinn:**
  - Echte Beispielnachrichten aller Topics für Analyse und Weiterverwendung
  - Weitergabe an andere Projekte (z.B. DSP)
  - Rekonstruktion der Logik-Abläufe (z.B. wie ändern sich `ccu/order/active`, Topics über Zeit)
- **Empfehlung:** Behalten, Ziel-Pfad bei omf-data→osf-data migriert

---

## 2. Data-Pfade – Konsolidierung

### 2.1 Aktuelle Struktur

```
data/
├── osf-data/           # Haupt-Nutzdaten (aktiv)
│   ├── sessions/       # Aufgezeichnete Sessions (.db, .log)
│   ├── test_topics/    # Test-Topics, Preloads
│   ├── *-analysis/    # Analyse-Output (dps, hbw, mill, drill, fts, aiqs)
│   └── ...
├── aps-data/           # Legacy/Teilweise ungenutzt
│   ├── topics/        # LEER – Topic Recorder Ziel
│   └── mosquitto/     # Nur in Doku (PHASE_1_BACKUP_SCRIPT, ssh_commands)
└── mqtt-data/         # Legacy
    └── sessions/      # default_test_session.db/.log + README (veraltet)
```

### 2.2 Befunde

| Pfad | Inhalt | Verwendung |
|------|--------|------------|
| `osf-data/sessions/` | Sessions | Session Recorder, Replay Station, Scripts |
| `osf-data/test_topics/` | Test-Topics, Preloads | Replay Station, test_order_flow.sh |
| `osf-data/*-analysis/` | Script-Output | analyze_*_sessions.py |
| `aps-data/topics/` | **Leer** | Topic Recorder (ungenutzt) |
| `aps-data/mosquitto/` | Backup-Doku | ssh_commands.md, PHASE_1_BACKUP_SCRIPT |
| `mqtt-data/sessions/` | default_test_session.db/.log (Duplikat von osf-data) | Legacy – **keine Referenzen** in Code; alles nutzt osf-data |

### 2.3 Umbenennung omf-data → osf-data (erledigt)

**Wunsch:** `omf-data` → `osf-data` (Projekt heißt OSF, nicht OMF) – **abgeschlossen**

**Betroffene Stellen (ca. 50+ Referenzen):**

- `session_manager/` – path_constants, settings, replay_station, etc.
- `scripts/` – analyze_*, replay-sessions, build_order_fixtures, run-order-test
- `docs/` – How-Tos, Doku
- `integrations/APS-CCU/` – ccu-modification-and-deployment-analysis
- `osf/` – shopfloor-tab (sequenceFile), connection.service
- `.cursorrules`, `.cursorignore`, `.vscode/settings.json`

**Risiken:** Breaking Change – alle Pfade müssen angepasst werden. Datenbestand muss migriert oder Symlink gesetzt werden.

### 2.4 Konsolidierungs-Plan

| Maßnahme | Aufwand | Abhängigkeiten |
|----------|---------|----------------|
| **Topic Recorder** – behalten, Pfad migrieren | Gering | Bei osf-data |
| **mqtt-data prüfen** | Gering | default_test_session evtl. nach osf-data migrieren |
| **osf-data → osf-data** | Mittel–Hoch | Alle Referenzen, Doku, ggf. Migration |

---

## 3. Preloads – HBW-DEMO & HBW-MISSING

### 3.1 HBW-DEMO – Herkunft und Zweck

**Herkunft:** Commit `d2052f95` (feat: Order requestId-Erweiterung + Production-Fix)

**Dateien:**
- `data/osf-data/test_topics/preloads/module_v1_ff_HBW-DEMO_connection.json`
- `data/osf-data/test_topics/preloads/module_v1_ff_HBW-DEMO_state.json`
- `data/osf-data/test_topics/preloads/module_v1_ff_HBW-DEMO_factsheet.json`
- `data/osf-data/test_topics/layout_hbw_demo.json`

**Zweck:** Order-Flow-Tests **ohne echtes HBW-Modul**. Die CCU erwartet ein HBW im Layout; HBW-DEMO simuliert es mit Lagerbestand (loads in state).

**Verwendung:**
- `data/osf-data/test_topics/test_order_flow.sh` – Layout + Preloads + Order
- `data/osf-data/test_topics/correlation_test.py`
- `data/osf-data/test_topics/order_test.py`
- `integrations/APS-CCU/central-control/data/factory-layout.json` – Referenz HBW-DEMO

**Problem ("störend"):**  
Die Replay Station sendet beim Klick „Preloads jetzt senden“ **alle** Preloads – inkl. HBW-DEMO. Wer z.B. nur Vibrationssensor oder allgemeine osf-ui-Features testet, erhält HBW-DEMO im Modul-Tab → irritierend.

### 3.2 HBW-MISSING – Keine Preloads

**Befund:** Es gibt **keine** HBW-MISSING Preloads in `data/osf-data/test_topics/preloads/`.

HBW-MISSING erscheint nur in:
- `integrations/APS-CCU-LEGACY/` – default_layout
- `integrations/APS-CCU/central-control/src/modules/layout/default_reset/default_layout.ts` – als Platzhalter für fehlendes HBW

**Fazit:** HBW-MISSING ist ein CCU-Layout-Platzhalter, nicht Teil der Preloads. Der Nutzer meint vermutlich HBW-DEMO als „störend“.

### 3.3 Lösungsoptionen für HBW-DEMO

| Option | Beschreibung | Vor/Nachteile |
|--------|--------------|---------------|
| **A) Preload-Kategorien** | `preloads/order-flow/`, `preloads/osf-ui/` – Replay wählt Kategorie | Aufwand: Mittel. Saubere Trennung. |
| **B) Exclude-Liste** | HBW-DEMO in Config ausschließen, wenn „nur osf-ui“ | Gering. Flexibel. |
| **C) HBW-DEMO aus Preloads entfernen** | Nur in test_order_flow.sh manuell laden | Preloads „Preloads jetzt senden“ ohne HBW. Order-Flow-Tests nutzen eigenes Script. |
| **D) Beibehalten** | Nichts ändern | Einfach, aber weiterhin störend bei allgemeinen Tests. |

**Empfehlung:** Option C – HBW-DEMO aus `preloads/` in Unterverzeichnis z.B. `preloads/order-flow/` verschieben. Replay Station sendet nur `preloads/*.json` (ohne Unterordner) → Standard-Preloads ohne HBW-DEMO. `test_order_flow.sh` lädt explizit aus `preloads/order-flow/`.

---

## 4. Abstimmbare Todos

### Phase 1 – Session-Manager (niedriger Aufwand)

| # | Todo | Priorität | Aufwand |
|---|------|-----------|---------|
| 1.1 | **Topic Recorder** – behalten (echte Beispielnachrichten, DSP-Weitergabe, Logik-Rekonstruktion) | – | – |
| 1.2 | **Session Analyse** – Entscheidung: Behalten / Reduzieren / Entfernen | Mittel | – |
| 1.3 | **Default-Tab** von „Topic Recorder“ auf „Replay Station“ setzen | ✅ Erledigt | Gering |

### Phase 2 – Preloads (mittlerer Aufwand)

| # | Todo | Priorität | Aufwand |
|---|------|-----------|---------|
| 2.1 | **HBW-DEMO** – Verschieben nach `preloads/order-flow/` (oder ähnlich) | Hoch | Mittel |
| 2.2 | **test_order_flow.sh** – Pfad auf `preloads/order-flow/` anpassen | Hoch | Gering |
| 2.3 | **correlation_test.py, order_test.py** – Pfade anpassen | Hoch | Gering |
| 2.4 | **Preload-Logik** – Replay nur `preloads/*.json` (keine Unterordner) oder Konfiguration | Mittel | Gering |

### Phase 3 – Data-Konsolidierung (hoher Aufwand)

| # | Todo | Priorität | Aufwand |
|---|------|-----------|---------|
| 3.1 | **osf-data → osf-data** – Umbenennung durchführen | Hoch | Hoch |
| 3.2 | **path_constants, settings, Doku** – alle Referenzen anpassen | Hoch | Mittel |
| 3.3 | **aps-data/topics** – entfernen (nach Topic Recorder) | Niedrig | Gering |
| 3.4 | **mqtt-data** – prüfen: default_test_session migrieren oder mqtt-data auflösen | Niedrig | Mittel |

### Phase 4 – Dokumentation

| # | Todo | Priorität | Aufwand |
|---|------|-----------|---------|
| 4.1 | **Session Manager README** – aktualisierte Tab-Beschreibung | Niedrig | Gering |
| 4.2 | **.cursorrules** – data/osf-data statt osf-data (nach Umbenennung) | Niedrig | Gering |
| 4.3 | **Data-Struktur Doku** – docs/02-architecture oder 07-analysis | Niedrig | Gering |

---

## 5. Zusammenfassung

- **Replay Station** und **Session Recorder** sind zentral und bleiben.
- **Topic Recorder** und **Session Analyse** können reduziert oder entfernt werden.
- **osf-data → osf-data** ist sinnvoll, erfordert aber umfassende Anpassungen.
- **HBW-DEMO** aus Standard-Preloads auslagern, Order-Flow-Tests nutzen eigenen Pfad.

**Nächster Schritt:** Abstimmung der Todos (Phase 1–4) und Priorisierung.
