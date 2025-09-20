# Development Workflow Guide

**Zielgruppe:** Entwickler  
**Letzte Aktualisierung:** 20.09.2025

## 🚨 Critical Development Rules

### **KEINE COMMITS VOR TESTS**
- **NIEMALS** Commits durchführen bevor alle Implementierungen vollständig getestet wurden
- Jede neue Funktionalität muss erst funktional getestet werden:
  - Dashboard startet ohne Fehler
  - Features funktionieren wie erwartet
  - Keine Runtime-Fehler
  - UI ist bedienbar
- **Tests haben absolute Priorität vor Commits**

### **Test-First Development**
1. **Implementierung** → Test → Fix → Test → Commit
2. **Nur bei 100% funktionierenden Features** committen
3. **Bei Fehlern:** Fix implementieren, erneut testen

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
