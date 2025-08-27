# 🏭 Module Configuration Guide

## 📋 Overview

Die **zentrale Modul-Konfiguration** wurde erfolgreich implementiert und ersetzt die veraltete `module_mapping.json` durch eine moderne YAML-basierte Lösung mit erweiterten Funktionen.

## ✅ Neue Features

### **1. Zentrale YAML-Konfiguration**
- **Datei**: `src_orbis/mqtt/config/module_config.yml`
- **Format**: YAML für bessere Lesbarkeit und Wartung
- **Struktur**: Hierarchische Organisation nach Modul-Typen

### **2. ModuleManager Klasse**
- **Datei**: `src_orbis/mqtt/tools/module_manager.py`
- **Funktionen**: Einheitliche Verwaltung für alle Tools
- **Backward Compatibility**: Bestehende Funktionen bleiben verfügbar

### **3. Dashboard Integration**
- **Neuer Tab**: "🏭 Module" unter "Einstellungen"
- **Anzeige**: Tabellarische Darstellung nach Modul-Typen
- **IP-Ranges**: Vollständige IP-Adressen-Übersicht

## 🏭 Modul-Übersicht

### **Vollständige Modul-Konfiguration:**

| Modul | Serial Number | Typ | IP-Range | IP-Adressen | Befehle |
|-------|---------------|-----|----------|-------------|---------|
| **HBW** | `SVR3QA0022` | **Storage** | `192.168.0.80-83` | 4 IPs | PICK, DROP, STORE |
| **DRILL** | `SVR4H76449` | **Processing** | `192.168.0.50-55` | 6 IPs | PICK, DRILL, DROP |
| **MILL** | `SVR3QA2098` | **Processing** | `192.168.0.40-45` | 6 IPs | PICK, MILL, DROP |
| **AIQS** | `SVR4H76530` | **Quality-Control** | `192.168.0.70-75` | 6 IPs | PICK, DROP, CHECK_QUALITY |
| **DPS** | `SVR4H73275` | **Input/Output** | `192.168.0.90` | 1 IP | PICK, DROP, INPUT_RGB, RGB_NFC |
| **CHRG** | `CHRG0` | **Charging** | `192.168.0.65` | 1 IP | start_charging, stop_charging, get_status |
| **FTS** | `5iO4` | **Transport** | `192.168.0.100` | 1 IP | NAVIGATE, PICK, DROP |

### **Modul-Typen:**
- **⚙️ Processing**: DRILL, MILL (Bearbeitungsmodule)
- **🔍 Quality-Control**: AIQS (Qualitätsprüfung)
- **📦 Storage**: HBW (Lagerung)
- **🚪 Input/Output**: DPS (Warenein- und Ausgang)
- **🔋 Charging**: CHRG (Ladestation)
- **🚗 Transport**: FTS (Fahrerloses Transportsystem)

## 📁 Datei-Struktur

### **Konfigurationsdatei:**
```yaml
# src_orbis/mqtt/config/module_config.yml
metadata:
  version: "2.0"
  description: "Modul Mapping mit erweiterten Informationen"

modules:
  "SVR3QA0022":  # HBW
    id: "SVR3QA0022"
    name: "HBW"
    name_lang_en: "High Bay Warehouse"
    name_lang_de: "Hochregallager"
    type: "Storage"
    ip_range: "192.168.0.80-83"
    ip_addresses: ["192.168.0.80", "192.168.0.81", "192.168.0.82", "192.168.0.83"]
    description: "Hochregallager für Werkstück-Lagerung und -Entnahme"
    commands: ["PICK", "DROP", "STORE"]
    sub_type: "HBW"

# ... weitere Module

enums:
  workpiece_types: {"RED": "Rotes Werkstück", ...}
  workpiece_states: {"RAW": "Rohling", ...}
  # ... weitere ENUM-Werte
```

### **ModuleManager Klasse:**
```python
# src_orbis/mqtt/tools/module_manager.py
from module_manager import get_module_manager

# Verwendung
manager = get_module_manager()
module_info = manager.get_module_info("SVR3QA0022")
ip_addresses = manager.get_module_ip_addresses("SVR3QA0022")
```

## 🔧 Verwendung

### **1. In Analysatoren:**
```python
from src_orbis.mqtt.tools.module_manager import get_module_manager

class TemplateAnalyzer:
    def __init__(self):
        self.module_mapping = get_module_manager()
    
    def analyze_module(self, module_id):
        module_info = self.module_mapping.get_module_info(module_id)
        module_type = self.module_mapping.get_module_type(module_id)
        # ... weitere Analyse
```

### **2. Im Dashboard:**
```python
# Automatisch integriert in aps_dashboard.py
def show_module_settings(self):
    module_manager = self.module_mapping
    all_modules = module_manager.get_all_modules()
    # ... Anzeige der Module
```

### **3. ENUM-Werte verwenden:**
```python
# Backward Compatibility
enum_values = module_mapping.get_enum_values('workpieceTypes')
workpiece_types = module_mapping.get_workpiece_types()
locations = module_mapping.get_locations()
```

## 📊 Dashboard Features

### **Neuer "Overview" Tab:**
- **Hauptnavigation**: "🏭 Overview" (vorher "Module Overview")
- **Tab-Name**: "ORBIS Modellfabrik Overview"
- **Logo-Titel**: "Modellfabrik-Dashboard" (vorher "APS Dashboard")
- **Unter-Tabs**: 4 Unter-Tabs für verschiedene Übersichten
- **Modul-Übersicht**: Alle Module in einer übersichtlichen Tabelle
- **IP-Adressen**: Erste verfügbare IP-Adresse pro Modul (ToBeDone: aus MQTT-Nachrichten)
- **Statistiken**: Anzahl Module pro Typ
- **Detaillierte Informationen**: Name, Beschreibung, Befehle

### **Anzeige-Features:**
- **Einheitliche Tabelle**: Alle Module in einer sortierbaren Tabelle
- **Spalten-Reihenfolge**: Name (mit Icon) → ID → Type → IP → Connected → Activity Status → Recent Messages
- **Modul-Type Spalte**: Neue Spalte für Modul-Typ (Processing, Storage, etc.)
- **IP-Adressen**: Erste verfügbare IP-Adresse pro Modul (ToBeDone: aus MQTT-Nachrichten)
- **Befehle**: Verfügbare MQTT-Befehle pro Modul
- **Icon + Modul**: Kombinierte Anzeige von Icon und Modul-Name in der ersten Spalte

### **Unter-Tabs:**
- **📋 Module Status**: Aktuelle Module-Informationen mit IP-Adressen
- **📦 Bestellung**: Bestellungs-Funktionalität (Platzhalter)
- **📋 Bestellung Rohware**: Rohware-Bestellungs-Funktionalität (Platzhalter)
- **📊 Lagerbestand**: Lagerbestands-Funktionalität (Platzhalter)

## 🔄 Migration

### **Migrierte Dateien:**
1. ✅ `src_orbis/mqtt/dashboard/aps_dashboard.py`
2. ✅ `src_orbis/mqtt/tools/txt_template_analyzer.py`
3. ✅ `src_orbis/mqtt/tools/ccu_template_analyzer.py`
4. ✅ `src_orbis/mqtt/tools/unified_type_recognition.py`
5. ✅ `src_orbis/mqtt/tools/test_unified_type_recognition.py`

### **Gelöschte Dateien:**
- ❌ `src_orbis/mqtt/tools/module_mapping.json` (ersetzt durch YAML)
- ❌ `src_orbis/mqtt/tools/module_mapping_utils.py` (ersetzt durch ModuleManager)
- ❌ `src_orbis/mqtt/tools/test_unified_type_recognition.py` (verschoben)
- ❌ `src_orbis/mqtt/dashboard/config/settings.py` (obsolet - doppelt zur YAML-Konfiguration)
- ❌ `src_orbis/mqtt/tools/mqtt_message_library.py` (obsolet - doppelt zur YAML-Konfiguration)
- ❌ `docs_orbis/mqtt/working-mqtt-messages.md` (obsolet - doppelt zur YAML-Konfiguration)
- ❌ `docs_orbis/mqtt/dashboard-extensions.md` (obsolet - doppelt zur YAML-Konfiguration)
- ❌ `tests_orbis/test_dashboard_functionality.py` (obsolet - testete APS_MODULES_EXTENDED)
- ❌ `tests_orbis/test_dashboard_imports.py` (obsolet - testete APS_MODULES_EXTENDED)
- ❌ `tests_orbis/test_streamlit_startup.py` (obsolet - testete APS_MODULES_EXTENDED)

## 🧪 Tests

### **Unit-Tests:**
```bash
# ModuleManager Tests
python tests_orbis/test_module_manager.py

# Unified Type Recognition Tests
python src_orbis/mqtt/tools/test_unified_type_recognition.py

# Template Analyzer Tests
python src_orbis/mqtt/tools/txt_template_analyzer.py
python src_orbis/mqtt/tools/ccu_template_analyzer.py

# Dashboard Tests (bereinigt)
python -c "from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard; print('Dashboard import successful')"
```

### **Dashboard Test:**
```bash
# Dashboard starten
streamlit run src_orbis/mqtt/dashboard/aps_dashboard.py

# Neuen "Module" Tab unter "Einstellungen" testen
```

## 📈 Vorteile

### **1. Zentrale Verwaltung:**
- **Eine Konfigurationsdatei** für alle Module
- **Konsistente Daten** in allen Tools
- **Einfache Wartung** und Updates

### **2. Erweiterte Informationen:**
- **Vollständige IP-Ranges** (10 Adressen pro Modul)
- **Mehrsprachige Namen** (DE/EN)
- **Detaillierte Beschreibungen**
- **Verfügbare Befehle**

### **3. Backward Compatibility:**
- **Bestehende Code** funktioniert weiterhin
- **Schrittweise Migration** möglich
- **Keine Breaking Changes**

### **4. Dashboard Integration:**
- **Benutzerfreundliche Anzeige** aller Module
- **IP-Range Übersicht** für Netzwerk-Administration
- **Statistiken** und Metriken

## 🔮 Zukünftige Erweiterungen

### **Geplante Features:**
1. **OVEN-Modul**: Integration des neu entdeckten Moduls
2. **VDA5050**: FTS-Kommunikation erweitern
3. **Cloud-Integration**: Remote-Steuerung
4. **Performance-Monitoring**: Live-Status der Module

### **Mögliche Verbesserungen:**
1. **Web-Interface**: Online-Konfiguration
2. **Versionierung**: Konfigurations-Historie
3. **Backup/Restore**: Automatische Sicherung
4. **API**: REST-Interface für externe Tools

## 📚 Weitere Ressourcen

### **Verwandte Dokumentation:**
- [NFC Code Configuration Guide](./nfc-code-configuration-guide.md)
- [MQTT Control Summary](./mqtt/mqtt-control-summary.md)
- [Dashboard Extensions](./mqtt/dashboard-extensions.md)

### **Technische Details:**
- **YAML Format**: https://yaml.org/
- **Fischertechnik APS**: https://www.fischertechnik.de/agile-production-simulation
- **VDA5050 Standard**: https://www.vda5050.de/

---

**Status**: ✅ **VOLLSTÄNDIG IMPLEMENTIERT**
**Letzte Aktualisierung**: 2025-08-27
**Version**: 2.0
