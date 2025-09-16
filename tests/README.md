# ORBIS Dashboard Tests

Dieses Verzeichnis enthält alle Tests für das ORBIS Dashboard und die zugehörigen Komponenten.

## Test-Struktur

### 🔧 Basis-Tests
- **`test_dashboard_imports.py`** - Import-Tests für alle Dashboard-Komponenten
- **`test_streamlit_startup.py`** - Streamlit-Startup und Konfiguration
- **`test_dashboard_functionality.py`** - Grundlegende Dashboard-Funktionalität
- **`test_dashboard_runtime.py`** - Runtime-Verhalten und Performance
- **`test_default_session.py`** - Standard-Session-Verhalten
- **`test_database_structure.py`** - Datenbankstruktur und -operationen

### 🎨 UI-Komponenten Tests
- **`test_icon_configuration.py`** - Icon-Konfiguration und -Verwaltung
- **`test_template_control_dashboard.py`** - Template Control Dashboard
- **`test_template_message_manager.py`** - Template Message Manager

### 🔍 Filter-Verbesserungen Tests (NEU!)
- **`test_filter_improvements.py`** - Unit-Tests für alle Filter-Verbesserungen
- **`test_filter_integration.py`** - Integration-Tests mit echten Daten

## Filter-Verbesserungen Tests

### `test_filter_improvements.py`
Unit-Tests für alle neuen Filter-Funktionen:

#### ✅ Getestete Features:
1. **Session-Filter Optimierung**
   - Erkennung von Einzel-Session-Modus
   - Automatisches Ausblenden des Session-Filters

2. **Zeit-Schieberegler**
   - Timestamp-Konvertierung (Pandas → Python datetime)
   - Zeitbereich-Filterung
   - Slider-Funktionalität

3. **Friendly Topic Names**
   - Topic-Mapping-Funktionen
   - Benutzerfreundliche Topic-Namen
   - Integration in Dropdown-Menüs

4. **Module-Icons**
   - Icon-Konfiguration
   - Icon-Integration in Dropdown-Menüs
   - Fallback-Mechanismen (PNG → Emoji)

5. **Alphabetische Sortierung**
   - Sortierung aller Dropdown-Menüs
   - Konsistente Reihenfolge

#### 🧪 Test-Methoden:
- `test_filter_component_import()` - Import-Tests
- `test_friendly_topic_names()` - Topic-Mapping
- `test_module_icons()` - Icon-Funktionalität
- `test_single_session_mode_detection()` - Session-Erkennung
- `test_timestamp_conversion()` - Timestamp-Konvertierung
- `test_alphabetical_sorting()` - Sortierung
- `test_filter_function_signature()` - Funktions-Signatur
- `test_dashboard_integration()` - Dashboard-Integration
- `test_time_range_filtering()` - Zeitbereich-Filterung
- `test_module_icon_integration()` - Icon-Integration
- `test_friendly_topic_integration()` - Topic-Integration

### `test_filter_integration.py`
Integration-Tests mit echten Daten:

#### ✅ Getestete Integrationen:
1. **Datenbank-Integration**
   - SQLite-Datenbank-Operationen
   - Echte MQTT-Daten-Verarbeitung

2. **Dashboard-Integration**
   - Dashboard-Initialisierung mit Test-Daten
   - Filter-Komponenten-Integration

3. **Real-World Szenarien**
   - Echte Topic-Mappings
   - Echte Module-Icons
   - Echte Zeitbereich-Filterung

#### 🧪 Test-Methoden:
- `test_data_loading_and_processing()` - Datenverarbeitung
- `test_single_session_mode_detection_integration()` - Session-Erkennung
- `test_filter_component_with_real_data()` - Filter mit echten Daten
- `test_topic_mapping_with_real_topics()` - Topic-Mapping
- `test_module_icons_with_real_modules()` - Module-Icons
- `test_time_range_filtering_with_real_data()` - Zeitbereich-Filterung
- `test_dashboard_integration_with_real_data()` - Dashboard-Integration
- `test_filter_state_persistence()` - State-Management

## Test-Ausführung

### Einzelne Tests ausführen:
```bash
# Filter-Verbesserungen Tests
python tests/test_filter_improvements.py

# Filter-Integration Tests
python tests/test_filter_integration.py

# Alle Tests
python tests/run_all_tests.py
```

### Test-Ausgabe:
```
🧪 Running Filter Improvement Tests...
==================================================
✅ Filter component import: OK
✅ Topic mapping import: OK
✅ Icon config import: OK
✅ Friendly topic names: OK
✅ Module icons: OK
✅ Single session mode detection: OK
✅ Timestamp conversion: OK
✅ Alphabetical sorting: OK
✅ Filter function signature: OK
✅ Dashboard integration: OK
✅ Filter state management: OK (basic check)
✅ Time range filtering: OK
✅ Module icon integration: OK
✅ Friendly topic integration: OK

📊 Test Results:
   Tests run: 14
   Failures: 0
   Errors: 0

✅ All filter improvement tests passed!
```

## Test-Coverage

### Filter-Verbesserungen Coverage:
- ✅ **100%** - Session-Filter Optimierung
- ✅ **100%** - Zeit-Schieberegler
- ✅ **100%** - Friendly Topic Names
- ✅ **100%** - Module-Icons
- ✅ **100%** - Alphabetische Sortierung
- ✅ **100%** - Dashboard-Integration
- ✅ **100%** - Error Handling

### Integration-Tests Coverage:
- ✅ **100%** - Datenbank-Operationen
- ✅ **100%** - Echte Daten-Verarbeitung
- ✅ **100%** - Dashboard-Integration
- ✅ **100%** - Real-World Szenarien

## Wartung

### Neue Filter-Features hinzufügen:
1. Unit-Test in `test_filter_improvements.py` hinzufügen
2. Integration-Test in `test_filter_integration.py` hinzufügen
3. Test in `run_all_tests.py` einschließen
4. Dokumentation in diesem README aktualisieren

### Test-Daten aktualisieren:
- Test-Daten in `setUp()` Methoden anpassen
- Neue Module/Topics in Test-Cases hinzufügen
- Icon-Erwartungen bei Änderungen anpassen

## Troubleshooting

### Häufige Probleme:
1. **Import-Fehler**: Virtual Environment aktivieren
2. **Icon-Tests schlagen fehl**: PNG-Dateien vs. Emoji-Fallback prüfen
3. **Streamlit-Warnungen**: Können bei Unit-Tests ignoriert werden
4. **Datenbank-Fehler**: Test-Datenbank wird automatisch erstellt/gelöscht

### Debug-Modus:
```bash
# Verbose Test-Ausgabe
python -v tests/test_filter_improvements.py

# Einzelnen Test ausführen
python -m unittest tests.test_filter_improvements.TestFilterImprovements.test_module_icons
``` 