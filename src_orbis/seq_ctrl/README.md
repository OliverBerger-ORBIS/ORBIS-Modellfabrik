# ORBIS Sequenzsteuerung github-copilot

Dieses Modul ermöglicht die Verwaltung und Ausführung von Arbeitssequenzen (Workflows) für die ORBIS-Modellfabrik.
Konzeption und DEsign by guthub-copilot.

## Struktur

- **sequence_control_orbis.py**  
  Kernlogik für die Verwaltung von Sequenzen (Start, Weiter, Abbruch, Status).
- **ui_sequence_orbis.py**  
  Streamlit-basierte Benutzeroberfläche für die Steuerung und Visualisierung von Sequenzen.
- **recipes_orbis.py**  
  Laden von Sequenz-Rezepten aus YAML-Dateien.
- **mqtt_orbis.py**  
  (Optional) Anbindung an MQTT für die Kommunikation mit physischen Komponenten.

## Tests

Tests liegen im Ordner `tests_orbis/seq_ctrl` und können mit `pytest` ausgeführt werden:
```bash
$env:PYTHONPATH = "."
pytest .\tests_orbis\seq_ctrl\
```

## Schnelleinstieg

1. Rezepte in `src_orbis/recipes.yml` anlegen.
2. Streamlit-App starten:
    ```bash
    streamlit run src_orbis/seq_ctrl/ui_sequence_orbis.py
    ```
3. Sequenz im Dashboard auswählen und ausführen.

## Erweiterung

- Neue Sequenzen können einfach als YAML-Rezepte oder direkt im Code hinzugefügt werden.
- Die UI kann um weitere Funktionen wie Statusanzeigen oder Visualisierungen erweitert werden.

## Kontakt & Hilfe

Fragen, Vorschläge oder Bugs bitte als GitHub Issue melden.

---

## Sequenz im Code anlegen

Du kannst eine Sequenz auch direkt im Python-Code anlegen und starten, ohne ein YAML-Rezept zu verwenden.

### Beispiel

```python
from src_orbis.seq_ctrl.sequence_control_orbis import WorkflowOrderManager

# Sequenz als Liste von Schritten anlegen
custom_sequence = [
    {"name": "Vorbereiten", "topic": "prep", "payload": {"step": "prep"}},
    {"name": "Ausführen", "topic": "execute", "payload": {"step": "run"}},
    {"name": "Abschließen", "topic": "finish", "payload": {"step": "done"}}
]

# Sequenzmanager holen (Singleton)
manager = WorkflowOrderManager.get_instance()

# Sequenz unter einer eindeutigen ID starten
manager.start_sequence("my_custom_order", custom_sequence)

# Aktuellen Schritt abrufen
current_step = manager.get_current_step("my_custom_order")
print("Aktueller Schritt:", current_step)
```

Du kannst beliebig viele Sequenzen auf diese Weise starten und mit den Methoden des `WorkflowOrderManager` verwalten.

---