# Black/Ruff Loop Problem - Pre-commit Hooks

## **Problem: Black/Ruff Loop bei Pre-commit Hooks**

### **Symptom:**
- Pre-commit Hooks laufen in einer Endlosschleife
- Black formatiert immer wieder die gleiche Datei: `src_orbis/omf/config/sequence_definitions/aiqs_sequence.py`
- Ruff zeigt "All checks passed!" aber Black formatiert trotzdem

### **Aktuelle Ausgaben:**

**Black Output:**
```
black....................................................................Failed
- hook id: black
- files were modified by this hook

reformatted src_orbis/omf/config/sequence_definitions/aiqs_sequence.py
```

**Ruff Output:**
```
ruff.....................................................................Passed
```

**Pytest Output:**
```
413 passed, 18 warnings in 23.45s
```

### **Problem-Datei:**
`src_orbis/omf/config/sequence_definitions/aiqs_sequence.py`

**Aktueller Inhalt (Zeilen 6-8):**
```python
# fmt: off
from src_orbis.omf.tools.sequence_executor import SequenceDefinition, SequenceStep
# fmt: on
```

### **Was passiert:**
1. Black formatiert die Datei und entfernt die `fmt: off/on` Kommentare
2. Beim nächsten Commit versucht Black wieder zu formatieren
3. Endlosschleife

### **Frage an ChatGPT:**
**Warum ignoriert Black die `# fmt: off` und `# fmt: on` Kommentare und formatiert trotzdem die Datei? Wie kann ich das beheben?**

### **Kontext:**
- Python-Projekt mit Pre-commit Hooks
- Black 23.x, Ruff, Pytest
- Die Datei enthält einen absoluten Import, der vor Black-Formatierung geschützt werden soll
- Andere Dateien werden korrekt von Black ignoriert

### **Pre-commit Konfiguration:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: python -m pytest -q
        language: system
        pass_filenames: false
        always_run: true
```

### **pyproject.toml Black Konfiguration:**
```toml
[tool.black]
line-length = 120
target-version = ['py38']
skip-string-normalization = true
```

**Bitte um Lösung für diesen Black-Formatierungs-Loop!**
