## Agenten-Testpolicy: Produktionscode nicht für Alt-Tests verbiegen

Wenn ein Test nach einer beabsichtigten Änderung am produktiven Verhalten (z. B. Icon-Mapping im Asset-Manager) rot wird, gilt:

- Passe die betroffenen Tests an das neue, gewollte Verhalten an.
- Ändere NICHT den produktiven Code nur, um bestehende (veraltete) Tests grün zu bekommen.
- Dokumentiere die Testanpassung im PR kurz (Was/Warum), verweise auf die zugehörige Änderung (z. B. Guide/ADR).

Begründung: Tests spiegeln das gewünschte Verhalten wider. Wenn sich die fachliche Entscheidung ändert (z. B. neue SVGs), müssen die Tests diese neue Wahrheit abbilden – nicht umgekehrt.

# Testing Strategy Guide

**Zielgruppe:** Entwickler  
**Letzte Aktualisierung:** 20.09.2025

**Verwandte Dokumentation:**
- [Coverage Monitoring](coverage-monitoring.md) - Test Coverage Monitoring Setup
- Integration Tests: siehe Testing-Strategie und Projekt-spezifische Patterns
- [Replay vs. Test-Framework](../../07-analysis/test-framework-replay-comparison-2026-03.md) – OSF-UI: Session-Replay vs. automatisierte Fixture-Tests

## 🎯 Test-Philosophie

### **Test-First Development**
1. **Implementierung** → Test → Fix → Test → Commit
2. **Nur bei 100% funktionierenden Features** committen
3. **Tests haben absolute Priorität vor Commits**

### **KEINE COMMITS VOR TESTS**
- **NIEMALS** Commits durchführen bevor alle Implementierungen vollständig getestet wurden
- Jede neue Funktionalität muss erst funktional getestet werden
- **UI-Tests** werden vom Benutzer durchgeführt und Ergebnisse mitgeteilt

## 🧪 Test-Kategorien

### **1. Unit-Tests**
- **Ziel:** Automatische Tests für einzelne Funktionen
- **Tools:** pytest, unittest
- **Coverage:** Mindestens 80% Code-Coverage
- **Ausführung:** `python -m pytest tests_orbis/`

### **2. Integration-Tests**
- **Ziel:** Tests für Komponenten-Interaktion
- **Fokus:** MQTT-Integration, Manager-Interaktion
- **Mocking:** MQTT-Client, Session State
- **Ausführung:** `python -m pytest tests_orbis/test_omf/`

### **3. UI-Tests (KRITISCH)**
- **Ziel:** Manuelle Tests der Benutzeroberfläche
- **Durchführung:** Vom Benutzer durchgeführt
- **Kriterien:**
  - Dashboard startet ohne Fehler
  - Features funktionieren wie erwartet
  - Keine Runtime-Fehler
  - UI ist bedienbar

### **4. Performance-Tests**
- **Ziel:** Memory-Leaks und Performance-Probleme erkennen
- **Tools:** memory_profiler, cProfile
- **Kriterien:** Keine Memory-Leaks, akzeptable Response-Zeiten

## 🔧 Test-Tools

### **pytest Configuration**
```python
# pytest.ini
[tool:pytest]
testpaths = tests_orbis
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=omf --cov-report=html --cov-report=term
```

### **Test-Directory Structure**
```
session_manager/
└── tests/                       # Session Manager Python-Tests
    ├── test_session_manager_logging.py
    ├── test_session_logger.py
    └── test_logging_cleanup.py

osf/                             # OSF Angular/Jest-Tests
└── apps/osf-ui/.../__tests__/   # Component/Service-Tests
```

### **Mock-Objekte**
```python
# conftest.py
@pytest.fixture
def mock_mqtt_client():
    """Mock MQTT-Client für Tests"""
    client = Mock()
    client.subscribe_many = Mock()
    client.get_buffer = Mock(return_value=[])
    client.publish = Mock(return_value=True)
    return client

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit für UI-Tests"""
    with patch('streamlit.container'), \
         patch('streamlit.columns') as mock_columns:
        mock_columns.return_value = [Mock(), Mock()]
        yield
```

## 📋 Test-Checkliste

### **Vor jedem Commit**
- [ ] **Unit-Tests:** Alle Funktionen getestet
- [ ] **Integration-Tests:** Komponenten-Interaktion funktioniert
- [ ] **UI-Tests:** Benutzeroberfläche vollständig bedienbar
- [ ] **Performance-Tests:** Keine Memory-Leaks oder Performance-Probleme
- [ ] **Code-Coverage:** Mindestens 80%
- [ ] **Linting:** Black, Ruff ohne Fehler
- [ ] **Pre-commit Hooks:** Alle Hooks erfolgreich

### **UI-Test-Checkliste**
- [ ] **Session Manager:** Graph-Visualisierung, alle Tabs funktional
- [ ] **OSF-UI:** Module Control, alle Komponenten laden
- [ ] **Logging-System:** Keine Spam-Logs, saubere Ausgabe
- [ ] **MQTT-Integration:** Nachrichten werden korrekt angezeigt
- [ ] **APS-Integration:** APS-Tabs funktionieren
- [ ] **Error Handling:** Fehler werden korrekt behandelt

## 🚀 Test-Automatisierung

### **Pre-commit Hooks**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: Run Tests
        entry: python -m pytest tests_orbis/
        language: system
        files: \.py$
      
      - id: black
        name: Format Code
        entry: black --line-length 120 .
        language: system
        files: \.py$
      
      - id: ruff
        name: Lint Code
        entry: ruff check .
        language: system
        files: \.py$
```

### **CI/CD Pipeline**
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest tests_orbis/ --cov=omf
```

## 📊 Test-Metriken

### **Code-Coverage**
- **Ziel:** Mindestens 80% Code-Coverage
- **Tools:** pytest-cov, coverage.py
- **Ausführung:** `python -m pytest --cov=omf --cov-report=html`

### **Test-Performance**
- **Ziel:** Tests laufen in unter 30 Sekunden
- **Tools:** pytest-benchmark
- **Ausführung:** `python -m pytest --benchmark-only`

### **Test-Qualität**
- **Ziel:** Weniger als 5% fehlgeschlagene Tests
- **Tools:** pytest-html, pytest-xdist
- **Ausführung:** `python -m pytest --html=report.html --self-contained-html`

## 🔍 Debugging Tests

### **Test-Debugging**
```python
# Test mit Debug-Output
def test_my_function():
    result = my_function()
    print(f"Debug: result = {result}")  # Debug-Output
    assert result == expected

# Test mit PDB
def test_my_function():
    result = my_function()
    import pdb; pdb.set_trace()  # Breakpoint
    assert result == expected
```

### **Test-Logging**
```python
# Test mit Logging
def test_my_function(caplog):
    with caplog.at_level(logging.INFO):
        result = my_function()
    
    assert "Expected log message" in caplog.text
    assert result == expected
```

## 📚 Test-Dokumentation

### **Test-Dokumentation**
- **Docstrings** für alle Test-Funktionen
- **Kommentare** für komplexe Test-Logik
- **README** für Test-Setup und -Ausführung

### **Test-Examples**
```python
def test_stock_manager_inventory_update():
    """Test für StockManager.update_inventory()
    
    Testet:
    - Inventory-Update mit gültigen Daten
    - Fehlerbehandlung bei ungültigen Daten
    - Logging-Verhalten
    """
    manager = StockManager()
    
    # Test gültige Inventory-Update
    inventory_data = {"A1": "RED", "B2": "BLUE"}
    result = manager.update_inventory(inventory_data)
    
    assert result == True
    assert len(manager.orders) == 1
    assert manager.orders[0]["id"] == "test-001"
```

---

*Teil der OSF-Dokumentation | [Zurück zur README](../../README.md)*
