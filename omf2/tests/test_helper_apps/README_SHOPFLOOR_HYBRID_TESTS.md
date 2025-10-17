# Shopfloor Layout Hybrid - Tests

## Übersicht

Diese Tests stellen sicher, dass die `shopfloor_layout_hybrid` Komponente korrekt funktioniert und mit allen CCU Orders Tabs kompatibel ist.

## Test-Dateien

### 1. `omf2/tests/test_helper_apps/hybrid_shopfloor_test.py`
**Zweck:** Streamlit Test-App für Hybrid Shopfloor Layout

**Features:**
- ✅ Interactive Shopfloor Grid mit SVG-Icons
- ✅ Active Module Highlighting (Orange Füllung)
- ✅ Clickable Module mit Event-Handling
- ✅ Split-Cells (0,0) und (0,3) mit ORBIS-Logo
- ✅ Asset Manager Integration
- ✅ Debug Information und Event History

### 2. `tests/test_ccu_orders_integration.py`
**Zweck:** Integration der `shopfloor_layout_hybrid` in CCU Orders Tabs

**Tests:**
- ✅ Production Orders Subtab Import
- ✅ Storage Orders Subtab Import
- ✅ shopfloor_layout_hybrid Import
- ✅ Parameter-Kompatibilität für beide Orders Tabs

## Ausführung

```bash
# Hybrid Test-App starten
streamlit run omf2/tests/test_helper_apps/hybrid_shopfloor_test.py --server.port 8503

# Integration Tests
python tests/test_ccu_orders_integration.py

# Mit pytest
python -m pytest tests/test_ccu_orders_integration.py -v
```

## Behobene Probleme

### ❌ Vorher: Parameter-Fehler
```
show_shopfloor_layout_hybrid() got an unexpected keyword argument 'show_controls'
```

### ❌ Vorher: Key-Konflikt
```
There are multiple elements with the same key='factory_events'
```

### ✅ Nachher: Vollständige Kompatibilität
```python
def show_shopfloor_layout_hybrid(
    active_module_id: Optional[str] = None,
    active_intersections: Optional[list] = None,
    title: str = "Shopfloor Layout",
    show_controls: bool = True,  # ← NEU: show_controls Parameter hinzugefügt
    unique_key: Optional[str] = None  # ← NEU: unique_key Parameter hinzugefügt
) -> None:
```

## Verwendung in CCU Orders

### Production Orders Subtab
```python
show_shopfloor_layout_hybrid(
    active_module_id=active_module,
    active_intersections=active_intersections,
    show_controls=False,  # ← Funktioniert jetzt!
    unique_key="production_orders_shopfloor"  # ← Eindeutiger Key!
)
```

### Storage Orders Subtab
```python
show_shopfloor_layout_hybrid(
    active_module_id=active_module,
    active_intersections=active_intersections,
    show_controls=False,  # ← Funktioniert jetzt!
    unique_key="storage_orders_shopfloor"  # ← Eindeutiger Key!
)
```

## Wichtige Erkenntnisse

1. **Parameter-Kompatibilität ist kritisch** - Tests verhindern solche Fehler
2. **Legacy-Support** - Alte Parameter-Strukturen müssen weiterhin funktionieren
3. **CCU Orders Integration** - Beide Orders Tabs verwenden `show_controls=False`
4. **Eindeutige Keys** - Jeder Tab braucht einen eindeutigen `unique_key` für Streamlit-Komponenten
5. **Orange Highlighting** - Aktive Module werden mit orange Füllung hervorgehoben (aktuell Füllung, Umrandung gewünscht)

## Nächste Schritte

- ✅ Parameter-Fehler behoben
- ✅ Key-Konflikt behoben (eindeutige Keys für jeden Tab)
- ✅ Highlighting implementiert (orange Füllung funktioniert)
- ✅ Padding-Problem behoben (padding = 4px)
- ✅ Test-App in korrekte Projekt-Struktur verschoben
- ✅ CCU Orders Integration getestet
- ❌ **FTS Navigation Display** - Noch nicht implementiert
- ❌ **Highlighting als Umrandung** - Aktuell Füllung, Umrandung gewünscht
