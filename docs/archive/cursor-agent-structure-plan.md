# 🧠 Modellfabrik – Doku-Struktur für CURSOR-Agent

> ⚠️ **VERALTET** – Dieses Dokument beschreibt eine ältere Projektstruktur. Aktuelle Regeln: [.cursorrules](../../.cursorrules), [docs/README.md](../README.md).  
> Relevante Abweichungen: `/omf/` → `osf/`, `analysis/` aufgelöst → `07-analysis/`, `PROJECT_OVERVIEW.md` entfernt.

Dieses Dokument dient als Leitfaden für die Dokumentationsstruktur der ORBIS-Modellfabrik innerhalb des Git-Projekts. Es unterstützt den CURSOR-Agenten dabei, Inhalte korrekt einzuordnen, bestehende Strukturen zu respektieren und neue Analyse- und Architektur-Informationen logisch abzulegen.

## 🎯 **Multi-Cursor-Koordination**

### **Chat-spezifische Bereiche in PROJECT_STATUS.md:**
- **Chat-A: Architektur & Dokumentation** - System-Context, Mermaid-Diagramme, Namenskonventionen
- **Chat-B: Code & Implementation** - APS-Dashboard, OMF-Komponenten, Manager-Duplikate
- **Chat-C: Testing & Validation** - Fabrik-Tests, Cross-Platform, Template-Analyzer

### **Wichtige Regeln:**
- ✅ **Chat-Bereiche respektieren** - Nicht in andere Bereiche eingreifen
- ✅ **Realistische Status-Updates** - Implementiert ≠ Funktioniert
- ✅ **Testing-Priorität** - Immer testen bevor "abgeschlossen" markieren
- ✅ **CHAT-Aktivitäten protokollieren** - Jeder Agent erstellt ein chat-xy*<beschreibung>_Date-time.md  `/docs/07-analysis/chat-activities/`
- ✅ **APS/OMF Namenskonvention** - APS (As-Is), OMF (To-Be), Groß-Schreibweise mit Bindestrich

---

## 📁 Zielstruktur im Projekt

### Quellcode & Teststruktur

```bash
/omf/                    # Python-Code (DSP, MQTT-Komponenten, Cloud-Anbindung)
├── dashboard/           # OSF-UI Komponenten
├── helper_apps/         # Helper Apps (Session Manager, etc.)
├── analysis_tools/      # Analyse-Tools und Scripts
├── tools/               # Utility-Tools und Scripts
├── config/              # Konfigurationsdateien (Legacy)
└── scripts/             # Build- und Utility-Scripts

/tests/                  # Unit & Integration Tests
├── test_omf/           # OMF-Tests
├── test_helper_apps/   # Helper Apps Tests
└── mock_mqtt_client.py # MQTT-Mock für Tests

/logs/                   # Nicht versionierte Log-Dateien (lokal)
/data/                   # MQTT-Sessions für Replay-Tests ohne reale APS
├── aps-data/           # APS-Sessions
├── osf-data/           # OSF-Sessions (früher omf-data)
└── mqtt-data/          # MQTT-Sessions

/registry/               # MQTT-Kontrakte, Templates, Topic-Spezifikationen
├── model/              # Registry-Modelle
├── observations/       # Beobachtungen und Validierungen
└── schemas/            # JSON-Schemas

/vendor/                 # Submodul: Originalquellen Fischertechnik
/tools/                  # Projekt-Tools (nicht in omf/)
/git-hooks/              # Git-Hooks (pre-commit, etc.)
```

### Alle APS-Komponenten/Systeme:  Sourcen und Scripte

```bash
/integrations/
├── APS-CCU/                 # APS-CCU Komponente (Docker-Container, Konfiguration, Logs)
├── APS-NodeRED/             # APS-NodeRED Komponente (Flows, Konfiguration)
├── TXT-DPS/                 # TXT-DPS Komponente (.ft, .json, .py Programme)
├── TXT-FTS/                 # TXT-FTS Komponente (.ft, .json, .py Programme)
├── TXT-AIQS/                # TXT-AIQS Komponente (.ft, .json, .py Programme)
├── mosquitto/               # MQTT-Broker Komponente (Konfiguration, Logs)
└── OPC-UA-Module/           # OPC-UA-Module (NodeMaps, Topologien, zukünftig)

/vendor/
└── fischertechnik/          # Submodul: Originalquellen Fischertechnik
    ├── *.ft                 # TXT-Controller Programme
    ├── *.zap18              # RoboPro Programme
    └── *.PNG                # Bilder und Dokumentation
```

### Dokumentation (Markdown)

```bash
/docs/
├── 01-strategy/         # Vision, Roadmap, Discover/Prepare
├── 02-architecture/     # Systemarchitektur, Layer-Modelle
├── 03-decision-records/ # ADRs – technische Entscheidungen
├── 04-howto/            # Technische Anleitungen
├── 05-reference/        # Datenformate, externe Links, Schnittstellen
├── 06-integrations/     # Beschreibung technischer Schnittstellen und Logik
│   ├── APS-CCU/     # APS-CCU Dokumentation
│   ├── APS-NodeRED/ # APS-NodeRED Dokumentation
│   ├── TXT-DPS/     # TXT-DPS Dokumentation
│   ├── TXT-FTS/     # TXT-FTS Dokumentation
│   ├── TXT-AIQS/    # TXT-AIQS Dokumentation
│   ├── mosquitto/   # MQTT-Broker Dokumentation
├── 07-analysis/         # Funktionale Analysen + CHAT-Aktivitäten
├── 08-extensions/       # Erweiterungen wie DSP, AI, Cloud, etc.
├── sprints/             # Sprint-Dokumentation (sprint_A.md, sprint_B.md, etc.)
├── releases/            # Release Notes und Versionshistorie
├── helper_apps/         # Helper Apps Dokumentation
├── _shared/             # Geteilte Ressourcen (Mermaid-Diagramme, etc.)
├── archive/             # Archivierte Dokumentation
├── analysis/            # Legacy: Wird nach 07-analysis migriert
├── credentials.md       # Credentials und Secrets
├── generate_index.py    # Index-Generator
├── INDEX.html           # HTML-Index
├── INDEX.json           # JSON-Index
├── PROJECT_OVERVIEW.md  # Projekt-Übersicht
├── PROJECT_STATUS.md    # Projekt-Status
└── 99-glossary.md       # Glossar
```

---

## 🔍 Inhalt von `/docs/07-analysis/` (neu!)

Dieser Ordner dient zur funktionalen und blackboxartigen Analyse bestehender Komponenten, z. B.:

### **Funktionale Analysen:**
| Datei                           | Inhalt |
|----------------------------------|--------|
| `functional-analysis/aps-ccu-analysis.md`           | APS-CCU Funktionalität und Konfiguration |
| `functional-analysis/aps-nodered-analysis.md`       | APS-NodeRED Flows und MQTT-Integration |
| `functional-analysis/txt-dps-analysis.md`           | TXT-DPS Verhalten und Steuerlogik |
| `functional-analysis/txt-fts-analysis.md`           | TXT-FTS Verhalten und Steuerlogik |
| `functional-analysis/txt-aiqs-analysis.md`          | TXT-AIQS Verhalten und Steuerlogik |
| `06-integrations/mosquitto/log-analysis-2025-09-24.md` | MQTT-Broker Log-Analyse und Topics |
| `functional-analysis/docker-setup-analysis.md`     | Docker-Container Umgebung auf dem RPi |
| `functional-analysis/opcua-module-analysis.md`      | OPC-UA-Module NodeMaps und Topologien |

### **CHAT-Aktivitäten (Protokollierung):**
| Datei                           | Inhalt |
|----------------------------------|--------|
| `chat-activities/chat-a-architecture-YYYY-MM-DD.md` | Chat-A: Architektur & Dokumentation Aktivitäten |
| `chat-activities/chat-b-implementation-YYYY-MM-DD.md` | Chat-B: Code & Implementation Aktivitäten |
| `chat-activities/chat-c-testing-YYYY-MM-DD.md` | Chat-C: Testing & Validation Aktivitäten |

---

## ✅ Aufgaben & ToDos

### **Struktur aufbauen:**
- [ ] Ordner `/docs/07-analysis/` anlegen
- [ ] Unterordner `functional-analysis/` und `chat-activities/` erstellen
- [ ] Bestehende Analysen aus `/docs/06-integrations/` ggf. verschieben

### **CHAT-Aktivitäten protokollieren:**
- [ ] Jeder Chat erstellt täglich eine Aktivitäts-Datei
- [ ] Format: `chat-activities/chat-{a|b|c}-{bereich}-YYYY-MM-DD.md`
- [ ] Inhalt: Was gemacht wurde, was funktioniert, was nicht, nächste Schritte
- [ ] Bezug zu Dateien aus `/integrations/` und `/vendor/` dokumentieren

### **Regeln für Cursor-Agenten:**
- [ ] Bei neuen Analysen → Inhalte in `/07-analysis/functional-analysis/` ablegen
- [ ] Bei jeder Chat-Aktivität → Protokoll in `/07-analysis/chat-activities/` erstellen
- [ ] PROJECT_STATUS.md als zentrale Koordination verwenden
- [ ] Chat-Bereiche respektieren - nicht in andere Bereiche eingreifen

---

## 🧭 Hinweise für den CURSOR-Agent

### **Verbindliche Regeln:**
- ✅ **Diese Struktur ist verbindlich** - Keine Abweichungen ohne Absprache
- ✅ **`07-analysis/`** ist für *funktionale Analyse* + *CHAT-Aktivitäten*
- ✅ **`06-integrations/`** ist für *technische Schnittstellen*
- ✅ **`integrations/`** ist für *Sourcen und Scripte*

### **Multi-Cursor-Koordination:**
- ✅ **PROJECT_STATUS.md** als zentrale Koordination verwenden
- ✅ **Chat-Bereiche respektieren** - Nicht in andere Bereiche eingreifen
- ✅ **Realistische Status-Updates** - Implementiert ≠ Funktioniert
- ✅ **Testing-Priorität** - Immer testen bevor "abgeschlossen" markieren
- ✅ **CHAT-Aktivitäten protokollieren** - Jede Aktivität dokumentieren

### **Bewährte Vorgehensweise:**
- ✅ **Sourcen & Scripte** → `/integrations/{KOMPONENTE}/` (z.B. APS-CCU, TXT-DPS)
- ✅ **Technische Schnittstellen** → `/docs/06-integrations/{KOMPONENTE}/`
- ✅ **Funktionale Analysen** → `/docs/06-integrations/{komponente}/README.md`
- ✅ **CHAT-Aktivitäten** → `/docs/07-analysis/chat-activities/`
- ✅ **APS/OMF Namenskonvention** - APS (As-Is), OMF (To-Be), Groß-Schreibweise mit Bindestrich
- ✅ **Komponenten-Namen** - Überall identisch: APS-CCU, TXT-DPS, mosquitto, etc.

### **Sprint-Vorgehensweise:**
- ✅ **Sprint-Dokumentation** → `/docs/sprints/` (sprint_A.md, sprint_B.md, etc.)
- ✅ **Release Notes** → `/docs/releases/` (Versionshistorie und Features)
- ✅ **Helper Apps** → `/docs/helper_apps/` (Separate Anwendungen)
- ✅ **Legacy Migration** → `/docs/analysis/` → `/docs/07-analysis/` (Schrittweise)

### **Bei Unklarheiten:**
- **Zuerst nachfragen** oder `07-analysis/unsorted.md` nutzen
- **Chat-Bereiche prüfen** in PROJECT_STATUS.md
- **Bestehende Struktur respektieren** - Nicht willkürlich ändern

### **🚨 WICHTIG: Virtual Environment aktivieren (KRITISCH)**
- **Vor JEDEM pip install:** `source .venv/bin/activate` (Linux/Mac) oder `.venv\Scripts\activate` (Windows)
- **Vor JEDEM Python-Befehl:** Virtual Environment muss aktiviert sein
- **Pre-commit Hooks:** Benötigen aktivierte venv für Dependencies (pyyaml, etc.)
- **Fehlerquelle:** Alle Chat-Agenten vergessen venv-Aktivierung → ModuleNotFoundError

### **Korrekte Reihenfolge:**
1. **Virtual Environment aktivieren:** `source .venv/bin/activate`
2. **Dependencies prüfen:** `pip list | grep yaml`
3. **Falls fehlend:** `pip install pyyaml`
4. **Dann erst:** `git commit` (ohne --no-verify)
