# Session Manager Migration Analyse

**Datum:** 2025-10-08  
**Branch:** omf2-refactoring  
**Ziel:** Migration von `omf/helper_apps/session_manager/` nach `<root>/session_manager/`

---

## 📊 Aktueller Stand

### 📁 Verzeichnisstruktur (IST)
```
omf/
├── helper_apps/
│   └── session_manager/          ← 17 Python-Dateien
│       ├── components/
│       ├── utils/
│       ├── session_manager.py
│       └── mqtt_client.py
├── analysis_tools/               ← 13 Python-Dateien
│   ├── find_first_order_topic.py
│   ├── module_manager.py
│   ├── mqtt_client_subscription_analyzer.py
│   ├── order_tracking_manager.py
│   ├── start_end2end_session.py
│   └── template_analyzers/       ← 8 Template Analyzers
└── tools/                        ← 20 Legacy-Tools
```

---

## 🔍 Abhängigkeits-Analyse

### ✅ Session Manager Abhängigkeiten (aktiv verwendet)

| Modul | Verwendet in | In omf2? | Pfad in omf2 |
|-------|-------------|----------|--------------|
| `omf.dashboard.tools.logging_config` | 15 Dateien | ✅ | `omf2/common/logging_config.py` |
| `omf.dashboard.utils.ui_refresh` | 7 Dateien | ✅ | `omf2/ui/utils/ui_refresh.py` |
| `omf.dashboard.tools.path_constants` | 5 Dateien | ❌ | **FEHLT** (muss erstellt werden) |
| `omf.dashboard.tools.streamlit_log_buffer` | 1 Datei | ✅ | `omf2/common/streamlit_log_buffer.py` |
| `omf.dashboard.tools.registry_manager` | 1 Datei | ✅ | `omf2/registry/manager/registry_manager.py` |
| `omf.tools.topic_manager` | 3 Dateien | ✅ | `omf2/common/topic_manager.py` |

### ❌ Analysis Tools Abhängigkeiten (NICHT aktiv)

**Wichtig:** `template_analysis.py` wird **NICHT** in `session_manager.py` verwendet!
- Das Template-Analysis-Tab ist **NICHT aktiv** → Kann ignoriert werden
- `omf.analysis_tools.*` wird **NUR** in `template_analysis.py` importiert
- `template_analyzers/` haben **VIELE** Abhängigkeiten zu `omf.tools.*` (Legacy)

**Empfehlung:** `template_analysis.py` bei Migration entfernen oder auskommentieren.

---

## 📋 Migrations-Plan

### Phase 1: Vorbereitung ✅ (Agent)

- [x] Abhängigkeits-Analyse abgeschlossen
- [x] omf2-Module identifiziert
- [x] Fehlende Module identifiziert: `path_constants.py`

### Phase 2: Fehlende Module erstellen (Agent)

- [ ] `omf2/common/path_constants.py` erstellen (basierend auf omf-Version)
- [ ] Import-Pfade anpassen für omf2-Struktur

### Phase 3: Session Manager Migration (Agent)

#### 3.1 Verzeichnis verschieben
```bash
# Altes Verzeichnis
omf/helper_apps/session_manager/

# Neues Verzeichnis
<root>/session_manager/
```

#### 3.2 Import-Anpassungen (17 Dateien)

**Tabelle der Import-Änderungen:**

| Alte Imports (omf) | Neue Imports (omf2) |
|-------------------|-------------------|
| `from omf.dashboard.tools.logging_config import get_logger` | `from omf2.common.logging_config import get_logger` |
| `from omf.dashboard.utils.ui_refresh import request_refresh` | `from omf2.ui.utils.ui_refresh import request_refresh` |
| `from omf.dashboard.tools.path_constants import PROJECT_ROOT` | `from omf2.common.path_constants import PROJECT_ROOT` |
| `from omf.dashboard.tools.streamlit_log_buffer import ...` | `from omf2.common.streamlit_log_buffer import ...` |
| `from omf.dashboard.tools.registry_manager import get_registry` | `from omf2.registry.manager.registry_manager import get_registry` |
| `from omf.tools.topic_manager import OmfTopicManager` | `from omf2.common.topic_manager import OmfTopicManager` |
| `from omf.helper_apps.session_manager.components.* import ...` | **Relative Imports:** `from .components.* import ...` |

#### 3.3 Dateien mit Import-Anpassungen (Priorität)

**Hoch-Priorität (Kern-Module):**
1. `session_manager.py` - Hauptapp (6 omf-Imports)
2. `components/session_analysis.py` - Session-Analyse (4 omf-Imports)
3. `components/topic_recorder.py` - Topic-Recording (3 omf-Imports)
4. `components/replay_station.py` - Replay-Funktion (2 omf-Imports)
5. `components/session_recorder.py` - Session-Recording (3 omf-Imports)

**Mittel-Priorität (UI & Utils):**
6. `components/ui_components.py` - UI-Helpers (4 omf-Imports)
7. `components/session_analyzer.py` - Analyzer (3 omf-Imports)
8. `components/settings_ui.py` - Settings-UI (3 omf-Imports)
9. `components/logs.py` - Logs-Tab (3 omf-Imports)
10. `components/order_analyzer.py` - Order-Analyzer (2 omf-Imports)
11. `components/auftrag_rot_analyzer.py` - Auftrag-Analyzer (2 omf-Imports)
12. `components/timeline_visualizer.py` - Timeline (2 omf-Imports)
13. `components/topic_manager.py` - Topic-Manager (2 omf-Imports)

**Niedrig-Priorität (Helpers):**
14. `mqtt_client.py` - MQTT-Client (1 omf-Import)
15. `components/settings_manager.py` - Settings (1 omf-Import)
16. `utils/session_logger.py` - Logger (1 omf-Import)

**Zu entfernen:**
17. `components/template_analysis.py` - **NICHT VERWENDET** (5 omf-Imports zu analysis_tools)

#### 3.4 Struktur-Änderungen

**Neue session_manager Struktur:**
```
session_manager/
├── __init__.py                    ← NEU: Package-Init
├── session_manager.py             ← Hauptapp (Streamlit)
├── mqtt_client.py                 ← MQTT-Client
├── session_manager_settings.json  ← Settings
├── components/
│   ├── __init__.py                ← NEU
│   ├── replay_station.py          ← ✅ Behalten
│   ├── session_analysis.py        ← ✅ Behalten
│   ├── session_analyzer.py        ← ✅ Behalten
│   ├── session_recorder.py        ← ✅ Behalten
│   ├── topic_recorder.py          ← ✅ Behalten
│   ├── settings_ui.py             ← ✅ Behalten
│   ├── settings_manager.py        ← ✅ Behalten
│   ├── logs.py                    ← ✅ Behalten
│   ├── ui_components.py           ← ✅ Behalten
│   ├── order_analyzer.py          ← ✅ Behalten
│   ├── auftrag_rot_analyzer.py    ← ✅ Behalten
│   ├── topic_manager.py           ← ✅ Behalten
│   ├── timeline_visualizer.py     ← ✅ Behalten
│   └── template_analysis.py       ← ❌ ENTFERNEN (nicht verwendet)
├── utils/
│   ├── __init__.py                ← NEU
│   └── session_logger.py          ← ✅ Behalten
└── README.md                      ← NEU: Dokumentation
```

---

## ⚠️ Risiken & Abhängigkeiten

### 🔴 Kritische Risiken

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Import-Fehler nach Migration | **HOCH** | HOCH | Schrittweise Migration, Tests nach jedem Schritt |
| `path_constants.py` funktioniert nicht | MITTEL | HOCH | Gründliche Tests mit pyproject.toml-Erkennung |
| Registry-Zugriff bricht | MITTEL | HOCH | Pfad-Validierung vor Migration |
| MQTT-Verbindung Probleme | NIEDRIG | MITTEL | Config-Dateien prüfen |
| Logging nicht initialisiert | MITTEL | MITTEL | logging_config.py Tests |

### ✅ Keine Registry-Abhängigkeiten in analysis_tools

**Prüfung:** `grep -r "registry" omf/analysis_tools/` → 91 Treffer  
**Analyse:** Alle Treffer sind **Text-Referenzen** in Kommentaren/Strings, keine Code-Abhängigkeiten

**Keine Blockers für Migration!** ✅

---

## 📝 Migrations-Schritte (Detailliert)

### Schritt 1: Fehlende Module erstellen (Agent)

```bash
# 1. path_constants.py nach omf2/common/ kopieren
cp omf/dashboard/tools/path_constants.py omf2/common/path_constants.py

# 2. Anpassen: REGISTRY_DIR auf omf2/registry zeigen lassen
# REGISTRY_DIR = PROJECT_ROOT / "omf2" / "registry"
```

### Schritt 2: session_manager verschieben (Agent)

```bash
# Verzeichnis verschieben
mv omf/helper_apps/session_manager session_manager

# __init__.py erstellen
touch session_manager/__init__.py
touch session_manager/components/__init__.py
touch session_manager/utils/__init__.py

# template_analysis.py entfernen (nicht verwendet)
rm session_manager/components/template_analysis.py
```

### Schritt 3: Import-Anpassungen (Agent)

**Automatisiert mit search_replace Tool:**
- 17 Dateien × 6-10 Imports/Datei = ~80-100 Import-Statements
- Systematisch: Datei für Datei, Import für Import

### Schritt 4: Relative Imports anpassen (Agent)

**Beispiel:**
```python
# ALT
from omf.helper_apps.session_manager.components.session_analyzer import SessionAnalyzer

# NEU (relativ)
from .session_analyzer import SessionAnalyzer
```

### Schritt 5: README erstellen (Agent)

- Installation
- Start-Anleitung
- Architektur-Übersicht
- Abhängigkeiten

### Schritt 6: Testing (User)

**Test-Checkliste:**
- [ ] Streamlit-App startet: `streamlit run session_manager/session_manager.py`
- [ ] MQTT-Verbindung funktioniert
- [ ] Session Recording funktioniert
- [ ] Session Replay funktioniert
- [ ] Test-Topic Management funktioniert
- [ ] Settings laden/speichern funktioniert
- [ ] Logs-Tab zeigt Logs an
- [ ] Session-Analyse funktioniert
- [ ] Timeline-Visualisierung funktioniert

---

## 🚀 Nächste Schritte

### Was der Agent jetzt machen kann:

1. ✅ **Schritt 1:** `omf2/common/path_constants.py` erstellen
2. ✅ **Schritt 2:** session_manager verschieben
3. ✅ **Schritt 3:** Alle Imports anpassen (17 Dateien)
4. ✅ **Schritt 4:** `__init__.py` Dateien erstellen
5. ✅ **Schritt 5:** `README.md` erstellen
6. ✅ **Schritt 6:** Pre-commit Hooks prüfen/anpassen

### Was der User danach machen muss:

7. ⚠️ **Testing:** Streamlit-App starten und testen (siehe Test-Checkliste)
8. ⚠️ **Entscheidung:** Was mit `omf/` passieren soll (archivieren/löschen)
9. ⚠️ **Entscheidung:** Was mit `omf/analysis_tools/` passieren soll (falls benötigt)

---

## 📊 Aufwandsabschätzung

| Phase | Aufgabe | Aufwand (Agent) | Aufwand (User) |
|-------|---------|----------------|----------------|
| 1 | Analyse | ✅ Erledigt | - |
| 2 | path_constants.py erstellen | 5 min | - |
| 3 | session_manager verschieben | 2 min | - |
| 4 | Imports anpassen (17 Dateien) | 30-45 min | - |
| 5 | __init__.py + README | 10 min | - |
| 6 | Pre-commit Hooks | 5 min | - |
| **Gesamt (Agent)** | | **~1 Stunde** | |
| 7 | Testing | - | **30-60 min** |
| 8 | Entscheidungen | - | **10 min** |
| **Gesamt (User)** | | | **~1 Stunde** |

---

## ✅ Fazit

**Migration ist machbar!** 🎉

- ✅ Alle benötigten omf2-Module existieren (bis auf path_constants.py)
- ✅ Keine Registry-Konflikte
- ✅ Keine analysis_tools-Abhängigkeiten (template_analysis.py nicht verwendet)
- ✅ Klare Import-Struktur erkennbar
- ✅ Automatisierte Migration möglich

**Empfehlung:** Agent startet jetzt mit Phase 2-6, User testet dann ausführlich.

**Nächster Schritt:** `path_constants.py` erstellen → Migration starten? 🚀



