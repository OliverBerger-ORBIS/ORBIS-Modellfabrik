<!-- 2993b5b8-13ee-4df3-b0e6-16ba737e5183 5e1b17cd-8a6e-4374-85e4-62a74a1f6a4e -->
# CCU Messe-Readiness (EN Default, i18n, UI-Aufräumen, Icons, Patterns)

## Scope und Vorgehen

- English als Default; DE/FR wählbar. Kein globaler „Messe-Mode“ – stattdessen pro-Widget ausblenden/entfernen.
- Reihenfolge: 0) Tab-Namen umbenennen → 1) Overview → 2) Orders → 3) Process → 4) Modules → 5) Configuration.
- Architektur-Patterns: MessageManager-Validation, Registry QoS/retain, request_refresh(), MQTT-Singleton, Logging via get_logger.

## 0) Tab-Namen umbenennen (ERSTER TASK)

- Datei: `omf2/ui/main_dashboard.py` (und ggf. weitere Top-Level Tab-Wrapper)
- Schritte:
  - Alle Tab-Bezeichnungen vollständig i18n (EN-Strings als Standard) und konsistent benennen.
  - Fehlende Keys in i18n hinzufügen; keine DE-Reste in UI.
  - Tab-Order prüfen und an Messe-Narrativ anpassen (CCU zuerst).
- Beispiel:
```python
st.tabs([
    i18n.t("tabs.ccu_dashboard"),
    i18n.t("tabs.ccu_orders"),
    i18n.t("tabs.ccu_process"),
    i18n.t("tabs.ccu_modules"),
    i18n.t("tabs.ccu_configuration"),
])
```

- Abnahme: Alle sichtbaren Tab-Namen EN, i18n-Keys vorhanden, keine harten Strings.

## 1) CCU Overview

- Dateien: `ccu_overview_tab.py`, Subtabs: `purchase_order_subtab.py`, `customer_order_subtab.py`, `inventory_subtab.py`.
- Aktionen: i18n-Literals ersetzen; SVG/Icon-Darstellung über Asset-Manager vereinheitlichen; pro-Widget unfertiges ausblenden/entfernen; Refresh-Hook auf `/j1/txt/1/f/i/stock` via `request_refresh()`.

## 2) CCU Orders (Production + Storage)

- Dateien: `production_orders_subtab.py`, `storage_orders_subtab.py`, `order_manager.py`.
- Aktionen: i18n-Abdeckung; Status-/Step-Icons konsistent; Shopfloor-Highlighting nur wenn stabil – sonst ausblenden.

## 3) CCU Process

- Dateien: `ccu_process_tab.py`, `ccu_production_plan_subtab.py`.
- Aktionen: i18n; nur unterstützte Views zeigen; Refresh bei `fts/v1/ff/*/state`.

## 4) CCU Modules

- Dateien: `ccu_modules_tab.py`, `common/shopfloor_layout.py`.
- Aktionen: i18n; konsistente Status-Icons; Caching wo vorhanden; Spaltenüberschriften i18n.

## 5) CCU Configuration

- Dateien: `ccu_configuration/*` (Factory/Parameter Subtabs).
- Aktionen: i18n; SVGs konsistent im Factory-Layout; riskante/fortgeschrittene Configs für die Messe ausblenden.

## Architektur-Compliance Pass

- CCU Gateway publish: MessageManager.validate + Registry QoS/retain.
- UI-Refresh: `request_refresh()` statt `st.rerun()`-Loops.
- Imports und Logging gemäß Projektregeln.

## Tests & Validierung

- Pro Schritt gezielte Tests anpassen/erweitern; dann Gesamtlauf `python -m pytest tests/` (mit venv).
- Development Rules validieren: `python omf/scripts/validate_development_rules.py`.

## Abnahmekriterien

- Alle sichtbaren Strings i18n; EN als Default aktiv; keine DE-Reste.
- Konsistente SVG/Icons; keine defekten Renderings.
- Unfertige Widgets sind verborgen/entfernt (pro-Widget Entscheidung).
- Tests grün; keine Regressionen.

### To-dos

- [x] Top-Level Tab-Namen auf EN umstellen und i18n-Keys sichern
- [x] Overview: i18n, SVG vereinheitlichen, pro-Widget aufräumen, Refresh-Hook
- [x] Orders: i18n, Steps/Icons konsistent, Highlighting nur wenn stabil
- [x] Process: i18n, nur unterstützte Views, FTS Refresh-Hook
- [x] Modules: i18n, Status-Icons konsistent, Caching, Spalten i18n
- [x] Configuration: i18n, Factory-Layout SVGs, riskante Optionen ausblenden
- [x] MessageManager+Registry QoS, request_refresh, Imports/Logging prüfen
- [x] SVG/Icon Nutzung über Asset-Manager konsolidieren
- [x] Tests je Schritt anpassen; Gesamtlauf und Rules-Validation


