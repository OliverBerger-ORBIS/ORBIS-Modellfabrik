# Development Workflow Guide

**Zielgruppe:** Entwickler  
**Letzte Aktualisierung:** 20.09.2025

## 🚨 **MANDATORY: Agent Development Methodology**

### **⚠️ KRITISCH: Jeder neue Agent MUSS diese Vorgehensweise befolgen**

**Bevor JEDE Implementierung beginnt, MUSS der Agent:**

1. **📖 DIESES DOKUMENT LESEN** - `docs/04-howto/development/workflow.md`
2. **📋 DIE METHODOLOGIE VERSTEHEN** - Analyse → Planung → Absprache → **TESTS ZUERST** → Implementierung → UI-Test → Dokumentation → Commit
3. **🔒 TEST-FIRST DEVELOPMENT VERSTEHEN** - **NIEMALS Code schreiben ohne vorherige Tests**
4. **✅ BESTÄTIGEN** dass er die Vorgehensweise verstanden hat

**NIEMALS direkt mit Implementierung beginnen ohne diese Schritte!**
**NIEMALS Code schreiben ohne vorherige Unit-Tests!**

---

## 🎯 **Standard Development Methodology**

### **Phase 1: Analyse**
- **Codebase durchsuchen** - Bestehende Komponenten verstehen
- **Requirements analysieren** - Was genau soll implementiert werden?
- **Dependencies identifizieren** - Welche Komponenten sind betroffen?
- **Architektur verstehen** - Wie passt es in das Gesamtsystem?

### **Phase 2: Planung**
- **Detaillierte Zusammenfassung** der geplanten Änderungen
- **Technische Lösung** skizzieren
- **Dateien identifizieren** die geändert werden müssen
- **Risiken bewerten** und Lösungsansätze definieren

### **Phase 3: Absprache**
- **Zusammenfassung präsentieren** - Kurze Übersicht der geplanten Änderungen
- **Auf explizite Bestätigung warten** - User muss "ja" oder "go" sagen
- **KEINE direkte Implementierung** ohne vorherige Freigabe
- **Bei Unsicherheit nachfragen** - Nicht raten oder annehmen

### **Phase 4: Implementierung**
- **🚨 MANDATORY: Test-First Development** - **TESTS ZUERST, DANN IMPLEMENTIERUNG**
- **Unit-Tests schreiben** - Vor jeder Implementierung Tests erstellen
- **Test-Driven Development** - Tests definieren das gewünschte Verhalten
- **Regeln befolgen** - Import-Standards, Pfad-Standards, Logging-System
- **Code-Qualität** - Black, Ruff, Pre-commit Hooks
- **Inkrementell vorgehen** - Kleine, testbare Schritte

#### **🔒 Test-First Development Regeln (NIEMALS IGNORIEREN):**
1. **TESTS ZUERST:** Jede neue Funktion/Feature MUSS zuerst getestet werden
2. **KEINE IMPLEMENTIERUNG ohne Tests:** Niemals Code schreiben ohne vorherige Tests
3. **Test-Datei erstellen:** `tests/test_omf2/test_<component>.py` für neue Komponenten
4. **Test-Coverage:** Mindestens 80% Code-Coverage für neue Features
5. **Test-Ausführung:** `python -m pytest tests/test_omf2/` vor jeder Implementierung

#### **🎨 UI-Symbol Regeln (NIEMALS IGNORIEREN):**
1. **UISymbols verwenden:** NIEMALS hardcodierte Icons (`🔌`, `🏗️`, etc.)
2. **Zentrale Definition:** Immer `UISymbols.STATUS_ICONS['key']` verwenden
3. **Icon-Konsistenz:** Gleiche Icons für gleiche Status in allen Komponenten
4. **Dokumentation prüfen:** `omf2/ui/common/symbols.py` vor Icon-Verwendung lesen
5. **Tests aktualisieren:** Bei Icon-Änderungen Tests entsprechend anpassen

### **Phase 5: UI-Test-Kontrolle**
- **Manuelle UI-Tests** - User führt Tests durch
- **Funktionalität verifizieren** - Features funktionieren wie erwartet
- **Performance prüfen** - Keine Memory-Leaks oder Performance-Probleme
- **User-Feedback einarbeiten** - Verbesserungen umsetzen

### **Phase 6: Dokumentation**
- **Code dokumentieren** - Docstrings, Kommentare, Type Hints
- **Architektur aktualisieren** - Decision Records, HowTos
- **README aktualisieren** - Neue Features dokumentieren
- **Veraltete Dokumentation entfernen** - Aufräumen und konsolidieren

### **Phase 7: Plan-Update & Commit**
- **plan.md aktualisieren** - Task-Status, Erfolgs-Kriterien
- **Pre-commit Tests** - pytest, black, ruff
- **Commit vorbereiten** - Temporäre Dateien aufräumen
- **User-Freigabe** - Explizite Bestätigung vor Commit
- **Push** - Änderungen übertragen

---

## 🚨 Critical Development Rules

### **KEINE COMMITS VOR TESTS**
- **NIEMALS** Commits durchführen bevor alle Implementierungen vollständig getestet wurden
- Jede neue Funktionalität muss erst funktional getestet werden:
  - Dashboard startet ohne Fehler
  - Features funktionieren wie erwartet
  - Keine Runtime-Fehler
  - UI ist bedienbar
- **Tests haben absolute Priorität vor Commits**

### **🚨 MANDATORY: Test-First Development**
1. **TESTS ZUERST** → Implementierung → Fix → Test → Commit
2. **NIEMALS Code schreiben ohne vorherige Unit-Tests**
3. **Test-Driven Development:** Tests definieren das gewünschte Verhalten
4. **Nur bei 100% funktionierenden Features** committen
5. **Bei Fehlern:** Fix implementieren, erneut testen

## 🔄 Git Workflow

### **Branching Strategy**
- **main:** Stabil, nur getestete Features
- **feature/***: Entwicklung neuer Features
- **sprint/***: Größere Umbauten

### **Commit-Strategie**
```bash
# Feature-Entwicklung
git checkout -b feature/aps-integration
# ... Entwicklung ...
# ... Tests ...
git add .
git commit -m "feat: APS Dashboard Integration"
git push origin feature/aps-integration
```

### **Commit-Messages**
- **feat:** Neue Features
- **fix:** Bug-Fixes
- **docs:** Dokumentation
- **refactor:** Code-Refactoring
- **test:** Tests

## 🧪 Testing Workflow

### **Test-Kategorien**
1. **Unit-Tests:** Automatische Tests für einzelne Funktionen
2. **Integration-Tests:** Tests für Komponenten-Interaktion
3. **UI-Tests:** Manuelle Tests der Benutzeroberfläche

### **UI-Tests (KRITISCH)**
- **Session Manager:** Graph-Visualisierung, alle Tabs funktional
- **OMF-Dashboard:** Module Control, alle Komponenten laden
- **Logging-System:** Keine Spam-Logs, saubere Ausgabe
- **UI-Tests werden vom Benutzer durchgeführt**

### **Test-Checkliste**
- [ ] **Unit-Tests:** Alle Funktionen getestet
- [ ] **Integration-Tests:** Komponenten-Interaktion funktioniert
- [ ] **UI-Tests:** Benutzeroberfläche vollständig bedienbar
- [ ] **Performance-Tests:** Keine Memory-Leaks oder Performance-Probleme

## 🔧 Development Tools

### **Pre-commit Hooks**
```bash
# Automatische Code-Formatierung
black --line-length 120 .

# Linting
ruff check .

# Tests
python -m pytest tests_orbis/
```

### **Import-Check Scripts**
```bash
# Alle relativen Imports finden
grep -r "from \.\." omf/

# Alle sys.path.append finden
grep -r "sys.path.append" omf/

# Alle lokalen Imports finden
grep -r "from [a-zA-Z_][a-zA-Z0-9_]* import" omf/ | grep -v "omf"
```

### **Validation Tools**
```bash
# Schema-Validierung
make validate-mapping

# Mapping Collision Detection
make check-mapping-collisions

# Template Resolver
python -m omf.tools.template_resolver
```

## 📋 Session Recording & Replay

### **Session Recording**
- **Recorder:** Speichert Nachrichtenströme (SQLite, Logs)
- **Thread-sichere Sammlung** von MQTT-Nachrichten
- **Strukturierte Logs** für Analyse

### **Session Replay**
- **Replay Station:** Befeuert OMF-Dashboard mit gespeicherten Sessions
- **Test-Umgebung** für Dashboard-Entwicklung
- **Offline-Entwicklung** möglich

### **Session Analyse**
- **Timeline-Visualisierung** mit Plotly
- **Topic-Filterung** und Kategorisierung
- **Template-Analyse** für Message-Struktur

## 🎯 Development Patterns

### **Wrapper Pattern (Dashboard-Komponenten)**
```python
def show_steering():
    """Hauptfunktion für die Steuerung mit Untertabs"""
    st.header("🎮 Steuerung")
    st.markdown("Alle Steuerungsfunktionen der ORBIS Modellfabrik")
    
    # Untertabs für verschiedene Steuerungsarten
    steering_tab1, steering_tab2, steering_tab3 = st.tabs(
        ["🏭 Factory-Steuerung", "🔧 Generische Steuerung", "🎯 Sequenz-Steuerung"]
    )
```

### **Manager Pattern (Business Logic)**
```python
class OrderManager:
    """Manager für Order-Verwaltung"""
    
    def __init__(self):
        self.orders = []
        self.logger = get_logger("OrderManager")
    
    def create_order(self, order_data):
        """Erstellt eine neue Order"""
        # Business Logic hier
        pass
```

### **Singleton Pattern (MQTT-Client)**
```python
# MQTT-Client als Singleton
mqtt_client = st.session_state.get("mqtt_client")
if not mqtt_client:
    mqtt_client = OmfMqttClient()
    st.session_state["mqtt_client"] = mqtt_client
```

## 📚 Dokumentation

### **Code-Dokumentation**
- **Docstrings** für alle Funktionen und Klassen
- **Type Hints** für bessere Code-Verständlichkeit
- **Kommentare** für komplexe Logik

### **Architektur-Dokumentation**
- **Decision Records** für wichtige Entscheidungen
- **HowTos** für praktische Anleitungen
- **Sprint-Dokumentation** für Projektverfolgung

---

*Teil der OMF-Dokumentation | [Zurück zur README](../../README.md)*
