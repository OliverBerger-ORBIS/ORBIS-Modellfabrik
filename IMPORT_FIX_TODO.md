# Import-Pfad-Probleme systematisch lösen

## Problem
- Black formatiert relative Imports zurück, aber die Module existieren nicht an den erwarteten Orten
- `ModuleNotFoundError` bei Tests und Imports
- Pre-commit Hooks schlagen fehl wegen Import-Problemen

## Lösung: Projekt als installierbares Paket konfigurieren

### ✅ Schritt 1: pyproject.toml erweitert
- setuptools-Konfiguration hinzugefügt
- Pytest-Konfiguration hinzugefügt
- isort known_first_party konfiguriert

### 🔄 Schritt 2: Editable Installation
```bash
pip install -e .
```
**Zweck:** Macht `src_orbis` als Top-Level-Package verfügbar, damit `import src_orbis.omf...` überall funktioniert

### 🔄 Schritt 3: pre-commit-config.yaml anpassen
```yaml
- id: pytest
  name: pytest
  entry: python -m pytest -q
  language: system
  pass_filenames: false     # ⬅️ kritisch!
  stages: [pre-commit]
```
**Zweck:** Pytest läuft ohne Dateiliste, importiert nicht versehentlich Streamlit-Dateien

### 🔄 Schritt 4: sys.path Manipulationen entfernen
- Suche nach `sys.path.append` in allen Dateien
- Entferne diese, da sie nach `pip install -e .` nicht mehr nötig sind

### 🔄 Schritt 5: Streamlit-Start anpassen
```bash
# Statt:
streamlit run src_orbis/omf/dashboard/omf_dashboard.py

# Verwende:
python -m streamlit run src_orbis/omf/dashboard/omf_dashboard.py
```

### 🔄 Schritt 6: Tests prüfen
- Alle aiqs_sequence Tests sollten funktionieren
- Keine `ModuleNotFoundError` mehr
- Pre-commit Hooks laufen durch

### 🔄 Schritt 7: IDE-Konfiguration
- Python-Interpreter auf venv setzen (wo `pip install -e .` ausgeführt wurde)
- Optional: `"python.testing.pytestArgs": ["-q", "tests_orbis"]` in VS Code/Cursor

## Erwartetes Ergebnis
- ✅ Alle Imports funktionieren überall
- ✅ Black/Ruff/isort harmonieren
- ✅ Pre-commit Hooks laufen durch
- ✅ Tests funktionieren
- ✅ Streamlit startet stabil
- ✅ Keine `sys.path` Manipulationen mehr nötig

## Debugging
Falls `ModuleNotFoundError` trotz `pip install -e .`:
```bash
python -c "import sys, pkgutil; print(sys.executable); print([m.name for m in pkgutil.iter_modules() if m.name.startswith('src_orbis')][:5])"
```
→ `src_orbis` muss gelistet sein

## Wichtige Dateien
- `pyproject.toml` - Package-Konfiguration
- `.pre-commit-config.yaml` - Hook-Konfiguration
- `src_orbis/__init__.py` - Muss existieren
- Kein `__init__.py` im Repo-Root
