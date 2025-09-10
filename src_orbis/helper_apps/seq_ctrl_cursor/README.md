# ORBIS Sequenzsteuerung Cursor

Dieses Modul ist eine Helper-App für die Sequenz-Steuerung, die von Cursor AI erstellt wurde.
Es basiert auf dem OMF Tools Sequence System und nutzt die gleichen Komponenten wie das Haupt-Dashboard.

## Struktur

- **sequence_control_dashboard.py**  
  Streamlit-basierte Benutzeroberfläche für die Sequenz-Steuerung (Test-Anwendung)

## Abhängigkeiten

Diese Helper-App nutzt die OMF Tools aus `src_orbis/omf/tools/`:
- `sequence_definition.py` - Sequenz-Definitionen (YML/Python)
- `sequence_ui.py` - Streamlit UI-Komponenten
- `sequence_executor.py` - Sequenz-Ausführung
- `workflow_order_manager.py` - ID-Management

## Schnelleinstieg

1. Streamlit-App starten:
    ```bash
    streamlit run src_orbis/helper_apps/seq_ctrl_cursor/sequence_control_dashboard.py
    ```
2. Sequenz im Dashboard auswählen und ausführen

## Hinweise

- **Keine Code-Duplikation** - Nutzt die Original-OMF Tools
- **Wartungsrisiko** - Änderungen in OMF Tools können diese App beeinträchtigen
- **Test-Anwendung** - Für Entwicklung und Tests gedacht

## Kontakt & Hilfe

Fragen, Vorschläge oder Bugs bitte als GitHub Issue melden.

---

**Herkunft:** Cursor AI  
**Basiert auf:** OMF Tools Sequence System  
**Status:** Helper-App (nicht produktiv)
