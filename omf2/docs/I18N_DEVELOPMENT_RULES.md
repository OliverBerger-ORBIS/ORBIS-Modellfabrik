# i18n Development Rules für OMF2

**Datum:** 2024-12-19  
**Status:** Implemented  
**Kontext:** OMF2 benötigt einheitliche i18n-Standards für mehrsprachige UI-Komponenten.

---

## 🎯 Ziele

- **Konsistente Mehrsprachigkeit:** Alle UI-Texte über i18n-System
- **Wartbarkeit:** Flache YAML-Struktur, keine tiefen Verschachtelungen
- **Performance:** Lazy Loading, Session State Integration
- **Entwicklerfreundlichkeit:** Automatische Validierung via Pre-commit Hooks

---

## ✅ Korrekte i18n-Implementierung

### 1. I18n-Manager aus Session State verwenden

```python
# ✅ Korrekt: Zentrale Instanz aus Session State
i18n = st.session_state.get("i18n_manager")
if i18n:
    title = i18n.t("ccu_overview.title")
    st.header(f"{UISymbols.get_functional_icon('ccu')} {title}")

# ❌ Falsch: Lokale Instanz erstellen
i18n = I18nManager("de")  # Verursacht Sprachinkonsistenzen
```

### 2. Hardcodierte Texte durch i18n.t() ersetzen

```python
# ✅ Korrekt: Übersetzte Texte
workpieces_text = i18n.t("ccu_overview.purchase_orders.workpieces").format(workpiece_type=workpiece_type)
st.markdown(f"#### {icons.get(workpiece_type, '📦')} {workpieces_text}")

# ❌ Falsch: Hardcodierte deutsche Texte
st.markdown("#### 📦 {workpiece_type} Werkstücke")
st.button("📤 Rohstoff bestellen")
```

### 3. Icons bleiben universal (UISymbols)

```python
# ✅ Korrekt: Icons sind universal, nur Text wird übersetzt
st.button(f"{UISymbols.get_status_icon('send')} {i18n.t('common.buttons.order')}")

# ❌ Falsch: Icons übersetzen
st.button(f"{i18n.t('icons.send')} {i18n.t('common.buttons.order')}")
```

### 4. Flache YAML-Keys verwenden

```yaml
# ✅ Korrekt: Flache Keys (domain.section.key)
common.buttons.order: "Rohstoff bestellen"
common.status.success: "Erfolgreich gesendet"
ccu_overview.purchase_orders.workpieces: "{workpiece_type} Werkstücke"

# ❌ Falsch: Tiefe Verschachtelung
common:
  buttons:
    order: "Rohstoff bestellen"
  status:
    success: "Erfolgreich gesendet"
```

### 5. String-Interpolation für dynamische Werte

```python
# ✅ Korrekt: String-Interpolation
workpieces_text = i18n.t("ccu_overview.purchase_orders.workpieces").format(workpiece_type=workpiece_type)
need_text = i18n.t("ccu_overview.purchase_orders.need_of_max").format(need=need, max_capacity=max_capacity)

# ❌ Falsch: String-Konkatenation
workpieces_text = i18n.t("ccu_overview.purchase_orders.workpieces_prefix") + workpiece_type + i18n.t("ccu_overview.purchase_orders.workpieces_suffix")
```

---

## 📁 YAML-Dateistruktur

### Ordnerstruktur
```
omf2/config/translations/
├── de/
│   ├── common.yml          # Gemeinsame Übersetzungen (Buttons, Status, Forms)
│   ├── ccu_overview.yml    # CCU Overview spezifische Übersetzungen
│   ├── admin.yml           # Admin-Tab Übersetzungen
│   └── nodered.yml         # NodeRED-Tab Übersetzungen
├── en/
│   ├── common.yml
│   ├── ccu_overview.yml
│   ├── admin.yml
│   └── nodered.yml
└── fr/
    ├── common.yml
    ├── ccu_overview.yml
    ├── admin.yml
    └── nodered.yml
```

### Key-Konventionen

- **Domain-basiert:** `common.*`, `ccu_overview.*`, `admin.*`
- **Flache Struktur:** Maximal 2 Punkte (`domain.section.key`)
- **String-Interpolation:** `{variable}` für dynamische Werte
- **Konsistente Namensgebung:** Snake_case für Keys

### Beispiel: common.yml
```yaml
# Buttons
common.buttons.order: "Rohstoff bestellen"
common.buttons.refresh: "Aktualisieren"
common.buttons.save: "Speichern"
common.buttons.cancel: "Abbrechen"

# Status Messages
common.status.success: "Erfolgreich gesendet"
common.status.error: "Fehler beim Laden"
common.status.warning: "Warnung"
common.status.info: "Information"

# Forms
common.forms.workpiece_type: "Werkstück-Typ"
common.forms.quantity: "Anzahl"
common.forms.notes: "Notizen"

# Dashboard
dashboard.subtitle: "OMF2 Dashboard - Modellfabrik Steuerung"
dashboard.language_switch: "Sprache wechseln"

# Main Navigation Tabs
tabs.ccu_overview: "CCU Übersicht"
tabs.ccu_orders: "CCU Bestellungen"
tabs.system_logs: "System Logs"
tabs.ccu_configuration: "CCU Konfiguration"
tabs.ccu_process: "CCU Prozess"
tabs.ccu_modules: "CCU Module"
tabs.admin_settings: "Admin Einstellungen"
tabs.generic_steering: "Generische Steuerung"
tabs.message_center: "Nachrichtenzentrale"
tabs.error_warning: "Fehler & Warnungen"
tabs.nodered_processes: "NodeRED Prozesse"
tabs.nodered_overview: "NodeRED Übersicht"
```

---

## 🔧 Automatische Validierung

### Pre-commit Hook
```yaml
# .pre-commit-config.yaml
- id: validate-i18n-compliance
  name: validate-i18n-compliance
  entry: python omf2/scripts/validate_i18n_compliance.py
  language: system
  pass_filenames: false
  stages: [commit]
```

### Validierungsregeln
1. **I18n-Manager Verwendung:** Alle Streamlit UI-Komponenten müssen `st.session_state.get("i18n_manager")` verwenden
2. **Hardcodierte Texte:** Keine deutschen Texte in UI-Komponenten
3. **Icon-Übersetzung:** Icons bleiben universal (UISymbols)
4. **YAML-Struktur:** Flache Keys, keine tiefen Verschachtelungen

### Manuelle Validierung
```bash
# i18n-Compliance prüfen
python omf2/scripts/validate_i18n_compliance.py

# Alle Development Rules prüfen
python omf/scripts/validate_development_rules.py
```

---

## 🚀 Implementierungscheckliste

### Für neue UI-Komponenten:
- [ ] `i18n = st.session_state.get("i18n_manager")` am Anfang der Funktion
- [ ] Alle hardcodierten Texte durch `i18n.t("key")` ersetzen
- [ ] Icons über `UISymbols` verwenden (nicht übersetzen)
- [ ] String-Interpolation für dynamische Werte
- [ ] Neue Keys zu entsprechenden YAML-Dateien hinzufügen

### Für bestehende UI-Komponenten:
- [ ] Systematische Analyse aller hardcodierten Texte
- [ ] YAML-Keys für alle gefundenen Texte erstellen
- [ ] Komponente schrittweise auf i18n umstellen
- [ ] Testen in allen Sprachen (DE/EN/FR)

---

## 📊 Status

### ✅ Implementiert:
- **CCU Overview Tab:** Vollständig mehrsprachig (DE/EN/FR)
- **i18n-System:** Lazy Loading, Session State Integration
- **YAML-Struktur:** Flache Keys, Domain-basiert
- **Pre-commit Hook:** Automatische Validierung
- **Development Rules:** Dokumentiert und validiert

### 🔄 In Arbeit:
- **Admin-Tabs:** i18n-Umstellung
- **NodeRED-Tabs:** i18n-Umstellung
- **CCU Configuration/Process:** i18n-Umstellung

### 📋 Geplant:
- **HTML-Templates:** i18n für Template-Texte
- **Weitere UI-Komponenten:** Systematische Umstellung
- **Translation Management:** Tool für Übersetzer

---

## 🎯 Best Practices

1. **Schrittweise Umstellung:** Eine Komponente nach der anderen
2. **Testen:** Immer alle Sprachen testen
3. **Konsistenz:** Einheitliche Key-Namensgebung
4. **Performance:** Lazy Loading nutzen
5. **Wartbarkeit:** Flache YAML-Struktur beibehalten

---

*Entwickelt von: OMF2-Team*  
*Letzte Aktualisierung: 2024-12-19*
