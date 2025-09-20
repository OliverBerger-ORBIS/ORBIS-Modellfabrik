# Decision Record: Wrapper-Pattern für Dashboard-Tabs

**Datum:** 2024-12-19  
**Status:** Accepted  
**Kontext:** Das OMF-Dashboard benötigt eine einheitliche Struktur für Dashboard-Tabs mit Untertabs und klarer Hierarchie.

---

## Entscheidung

Verwendung des **Wrapper-Pattern** für Dashboard-Tabs mit Untertabs und Sub-Komponenten.

```python
# Haupt-Dashboard (omf_dashboard.py)
def display_tabs():
    tab1, tab2, tab3 = st.tabs(["📊 Übersicht", "🏭 APS Overview", "📋 APS Orders"])
    
    with tab1:
        components["overview"]()  # Wrapper-Komponente
    with tab2:
        components["aps_overview"]()  # Wrapper-Komponente

# Wrapper-Komponente (overview.py)
def show_overview():
    """Wrapper für alle Overview-Funktionen"""
    st.header("📊 Übersicht")
    
    # Untertabs für verschiedene Bereiche
    tab1, tab2, tab3 = st.tabs(["Modul Status", "Kundenaufträge", "Lagerbestand"])
    
    with tab1:
        show_overview_module_status()  # Sub-Komponente
    with tab2:
        show_overview_customer_orders()  # Sub-Komponente
```

## Konsequenzen

### Positiv:
- **Einheitlichkeit:** Alle Tabs folgen dem gleichen Muster
- **Hierarchie:** Klare Struktur mit Haupt- und Untertabs
- **Modularität:** Sub-Komponenten einfach austauschbar
- **Wartbarkeit:** Logische Gruppierung verwandter Funktionen
- **Skalierbarkeit:** Neue Tabs einfach hinzufügbar

### Negativ:
- **Komplexität:** Mehr Abstraktionsebenen
- **Dateien:** Viele kleine Komponenten-Dateien

## Implementierung

- [x] Wrapper-Komponenten für alle Haupt-Tabs
- [x] Untertabs für spezifische Funktionsbereiche
- [x] Sub-Komponenten für einzelne Funktionen
- [x] Einheitliche Namenskonvention (`show_*`)
- [x] Klare Import-Struktur

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*
