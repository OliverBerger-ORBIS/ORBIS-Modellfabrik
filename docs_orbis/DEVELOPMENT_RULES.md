# **OMF Modellfabrik - Entwicklungsregeln**

> **📍 Position:** `docs_orbis/DEVELOPMENT_RULES.md`  
> **🤖 Cursor AI:** Siehe `.cursorrules` für KI-spezifische Regeln

## **🎯 Grundprinzipien**

### **1. Einfaches Grundgerüst**
- **Keine Überladung** mit nicht notwendiger Funktionalität
- **Minimaler Code** für maximale Übersichtlichkeit
- **Schritt-für-Schritt** Entwicklung
- **Tests nach jeder Änderung**

### **2. Sichere Vorgehensweise**
- **DASHBOARD_MIGRATION_PLAN** befolgen
- **Häufige Commits** nach jedem erfolgreichen Schritt
- **Rollback bei Fehlern** möglich
- **Immer funktionierenden Stand** haben

### **3. Saubere Architektur**
- **Trennung:** Aktive Sourcen vs. Helper-Apps
  - **Aktive Sourcen:** `src_orbis/omf/dashboard/` (Produktiv-Dashboard)
  - **Helper-Apps:** `src_orbis/helper_apps/`, `src_orbis/analysis_tools/` (Separate Anwendungen)
- **Modulare Komponenten** in separaten Dateien
- **Klare Import-Pfade** und Abhängigkeiten
- **Zweisprachigkeit:** Source-Namen EN, UI-Namen DE

### **4. Import-Standards (ZENTRALE ENTWICKLUNGSREGEL)**
- **NUR absolute Imports verwenden:** `from src_orbis.omf.module import Class`
- **KEINE relativen Imports:** `from ..module import Class` ❌
- **KEINE sys.path.append Hacks:** `sys.path.append(...)` ❌
- **KEINE lokalen Imports:** `from module import Class` ❌
- **Immer vollständige Pfade:** `from src_orbis.omf.tools.sequence_executor import SequenceExecutor`
- **Konsistente Namenskonvention:** Alle Imports beginnen mit `src_orbis.`

### **5. Datenstruktur**
- **Neue `data/`** Struktur verwenden
- **Session-Daten:** `data/mqtt-data/sessions/` (SQLite + Log-Dateien)
- **Log-Dateien:** `data/logs/` (nicht mehr ins Projekt-Root)
- **Git-freundlich** (große Dateien ignorieren)

## **📋 Dashboard-Tab-Struktur (Aktuell)**

### **Produktiv-Dashboard (OMF)**
1. **Übersicht**
   - Modul-Status
   - Lagerbestand
   - Kundenaufträge
   - Rohmaterial-Bestellungen
2. **Fertigungsaufträge**
   - Fertigungsauftrags-Verwaltung
   - Laufende Fertigungsaufträge
3. **Nachrichtenzentrale**
   - MQTT-Messages anzeigen
4. **Steuerung**
   - Factory-Steuerung
   - Generic-Steuerung
5. **Einstellungen**
   - Dashboard-Settings
   - Modul-Config
   - NFC-Config
   - MQTT-Config
   - Topic-Config
   - Messages-Templates

### **Helper-Apps (Separate Anwendungen)**
- **`src_orbis/helper_apps/`** - Replay-Station, Test-Apps, Sequenz-Systeme
  - **`seq_ctrl_copilot/`** - GitHub Copilot Sequenz-System
  - **`sequence_control_vscode/`** - VSCode KI Sequenz-System
  - **`seq_ctrl_cursor/`** - Cursor AI Sequenz-System (nutzt OMF Tools)
- **`src_orbis/analysis_tools/`** - Session-Analyse, Template-Analyse

## **🔧 Entwicklungsphasen**

### **Phase 1: Grundgerüst** ✅
- [x] Verzeichnisstruktur erstellen
- [x] Dokumentation erstellen
- [x] Einfaches Dashboard-Grundgerüst
- [x] Basis-Tab-Struktur
- [x] Konfiguration

### **Phase 2: Komponenten-Migration** ✅
- [x] Module Status aus V2.0.0 übernehmen
- [x] MessageTemplate Manager integrieren
- [x] MQTT-Integration
- [x] Dashboard2 → Dashboard Migration

### **Phase 3: Neue Features** ✅
- [x] Overview Components (Lagerbestand, Kundenaufträge, Rohmaterial-Bestellungen)
- [x] Production Order Components (Auftragsverwaltung, Laufende Aufträge)
- [x] HTML Templates für visuelle Darstellung
- [x] Namenskonvention (Customer/Purchase/Production Orders)

### **Phase 4: Aktuelle Entwicklung** 🔄
- [x] Production Order Management vollständig implementieren
- [x] Production Order Current vollständig implementieren
- [x] Shopfloor 3x4-Grid System implementiert
- [x] FTS Route Generator implementiert
- [x] Produktkatalog-System implementiert
- [x] Sequenz-Systeme in helper_apps verschieben
- [ ] Windows allUppercase Dateinamen-Problem lösen
- [ ] Helper-Apps Struktur optimieren

## **🧪 Test-Strategie**

### **Test-Verzeichnis-Struktur**
```
tests_orbis/
├── test_omf/                    # Dashboard-Tests
│   ├── test_dashboard/
│   ├── test_components/
│   └── test_tools/
├── test_helper_apps/            # Helper-App-Tests
│   ├── test_session_manager/
│   └── test_replay_station/
└── run_all_tests.py            # Test-Runner
```

### **Test-Standards**
- **Verzeichnis:** Alle Tests in `tests_orbis/`
- **Import-Standards:** Absolute Imports auch in Tests
- **Test-Namen:** `test_*.py` oder `*_test.py`
- **Test-Ausführung:** `python -m pytest tests_orbis/`
- **Coverage:** `pytest --cov=src_orbis tests_orbis/`

### **Branch-spezifische Test-Strategie**
- **Helper-Branches:** Nur `tests_orbis/test_helper_apps/` ausführen
- **Main-Branch:** Alle Tests in `tests_orbis/` ausführen
- **Helper-Test-Befehl:** `python -m pytest tests_orbis/test_helper_apps/`
- **Vollständige Tests:** `python -m pytest tests_orbis/` (nur auf main)

### **Branch-Erkennung**

#### **Manuell:**
```bash
# Aktuellen Branch prüfen
git branch --show-current

# Helper-Branch erkannt? → Nur Helper-Tests
if [[ $(git branch --show-current) == helper/* ]]; then
    python -m pytest tests_orbis/test_helper_apps/
else
    python -m pytest tests_orbis/
fi
```

#### **Automatisch (Empfohlen):**
```bash
# Branch-spezifische Test-Ausführung
python run_tests_by_branch.py
```

Das Script erkennt automatisch den Branch und führt die entsprechenden Tests aus:
- **Helper-Branches:** `tests_orbis/test_helper_apps/`
- **Main-Branch:** `tests_orbis/`

### **Test-Beispiele**
```python
# ✅ KORREKT - Test mit absoluten Imports
import pytest
from src_orbis.omf.tools.sequence_executor import SequenceExecutor
from src_orbis.omf.config.sequence_definitions.aiqs_sequence import AIQSSequence

def test_sequence_execution():
    executor = SequenceExecutor()
    # Test-Logik hier

# ✅ KORREKT - Dashboard-Komponenten-Test
import streamlit as st
from src_orbis.omf.dashboard.components.message_center import show_message_center

def test_message_center_display():
    # Test-Logik für Message Center
    pass

# ✅ KORREKT - Helper-App-Test
from src_orbis.helper_apps.session_manager.session_manager import SessionManager

def test_session_manager():
    manager = SessionManager()
    # Test-Logik hier
```

### **Nach jeder Änderung:**

#### **Helper-Branches (z.B. helper/session-manager):**
```bash
# Syntax-Check
python -m py_compile src_orbis/helper_apps/session_manager/session_manager.py

# Nur Helper-App-Tests ausführen
python -m pytest tests_orbis/test_helper_apps/

# Helper-App testen
streamlit run src_orbis/helper_apps/session_manager/session_manager.py --server.port=8507
```

#### **Main-Branch:**
```bash
# Syntax-Check
python -m py_compile src_orbis/omf/dashboard/omf_dashboard.py

# Alle Tests ausführen
python -m pytest tests_orbis/

# Dashboard testen
streamlit run src_orbis/omf/dashboard/omf_dashboard.py --server.port=8506
```

### **Commit-Strategie**
- Häufige Commits nach jedem erfolgreichen Schritt
- Immer einen funktionierenden Stand haben
- Rollback bei Fehlern möglich

## **🔄 Entwicklungsprozess-Regeln**

### **Neue Anforderungen - 3-Phasen-Prozess**

#### **Phase 1: Analyse** 🔍
- **Codebase durchsuchen:** Bestehende Komponenten und Strukturen verstehen
- **Abhängigkeiten prüfen:** Welche Module werden benötigt?
- **Architektur verstehen:** Wie passt die neue Anforderung ins Gesamtsystem?
- **Bestehende Patterns:** Gibt es ähnliche Implementierungen?

#### **Phase 2: Zusammenfassung** 📋
- **Kurze Übersicht:** Was wird implementiert?
- **Geplante Änderungen:** Welche Dateien werden modifiziert?
- **Neue Komponenten:** Was wird neu erstellt?
- **Abhängigkeiten:** Welche Imports und Module werden benötigt?

#### **Phase 3: Implementierung** ⚡
- **Nur nach Freigabe:** Explizite Bestätigung des Users abwarten
- **Schritt-für-Schritt:** Kleine, testbare Änderungen
- **Tests parallel:** Nach jeder Änderung Tests ausführen
- **Commits:** Häufige Commits nach erfolgreichen Schritten

### **❌ Was NICHT machen bei neuen Anforderungen:**
- **Direkte Implementierung** ohne vorherige Analyse
- **Große Änderungen** ohne Verständnis der bestehenden Struktur
- **Code schreiben** ohne explizite Freigabe
- **Annahmen treffen** über bestehende Funktionalität

### **✅ Was machen bei neuen Anforderungen:**
- **Erst analysieren** und verstehen
- **Zusammenfassung erstellen** mit geplanten Änderungen
- **Auf Freigabe warten** vor Implementierung
- **Kleine Schritte** mit Tests nach jedem Schritt

## **❌ Was NICHT machen:**
- **Überladung** mit nicht notwendiger Funktionalität
- **Komplexe Abhängigkeiten** ohne Tests
- **Große Änderungen** ohne Zwischencommits
- **Helper-Apps** ins Haupt-Dashboard integrieren
- **Doppelte Systeme** parallel entwickeln

## **✅ Was machen:**
- **Einfaches Grundgerüst** erstellen
- **Schritt-für-Schritt** entwickeln
- **Tests nach jeder Änderung**
- **Saubere Komponenten-Trennung**
- **Release-Notes bei Dashboard-Änderungen** aktualisieren (siehe `docs_orbis/RELEASE_NOTES_PROCEDURE.md`)

---

**Status:** ✅ Regeln definiert und aktualisiert
**Nächster Schritt:** Production Order Management vollständig implementieren
