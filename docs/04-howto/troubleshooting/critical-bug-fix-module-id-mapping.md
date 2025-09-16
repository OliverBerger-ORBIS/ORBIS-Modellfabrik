# Critical Bug Fix: Module-ID Mapping Error

## 🚨 **Kritischer Bug behoben**

**Datum:** 2025-01-19  
**Betroffene Versionen:** dashboardv3.1.0, dashboardv3.1.1  
**Schweregrad:** KRITISCH  

## 📋 **Problem-Beschreibung:**

### **Was passierte:**
- **Befehl:** DRILL-PICK ausgeführt
- **Tatsächlich ausgelöst:** AIQS-PICK
- **Ursache:** Falsche Module-ID-Zuordnung in `steering_factory.py`

### **Betroffene Module:**
- **DRILL** bekam fälschlicherweise **AIQS-Seriennummer** (SVR4H76530)
- **AIQS** bekam fälschlicherweise **MILL-Seriennummer** (SVR3QA2098)  
- **MILL** bekam fälschlicherweise **DRILL-Seriennummer** (SVR4H76449)

## 🔧 **Behobene Datei:**

**Datei:** `omf/omf/dashboard/components/steering_factory.py`  
**Funktion:** `_get_module_serial()` (Zeile 198)

### **❌ Vorher (FALSCH):**
```python
def _get_module_serial(module_name: str) -> str:
    """Hilfsfunktion um Module-Serials zu bekommen"""
    module_serials = {"AIQS": "SVR3QA2098", "MILL": "SVR4H76449", "DRILL": "SVR4H76530"}
    return module_serials.get(module_name, "UNKNOWN")
```

### **✅ Nachher (KORREKT):**
```python
def _get_module_serial(module_name: str) -> str:
    """Hilfsfunktion um Module-Serials zu bekommen"""
    module_serials = {"AIQS": "SVR4H76530", "MILL": "SVR3QA2098", "DRILL": "SVR4H76449"}
    return module_serials.get(module_name, "UNKNOWN")
```

## 📊 **Korrekte Module-Zuordnung:**

| Modul | Seriennummer | IP-Bereich | Beschreibung |
|-------|--------------|------------|--------------|
| **DRILL** | SVR4H76449 | 192.168.0.50-55 | Bohrmodul |
| **AIQS** | SVR4H76530 | 192.168.0.70-75 | Qualitätsprüfung |
| **MILL** | SVR3QA2098 | 192.168.0.40-45 | Fräsmodul |
| **HBW** | SVR3QA0022 | 192.168.0.80-83 | Hochregallager |
| **DPS** | SVR4H73275 | 192.168.0.90-95 | Warenein-/ausgang |

## 🎯 **Auswirkungen:**

### **Vor dem Fix:**
- DRILL-PICK → AIQS-PICK (falsches Modul)
- AIQS-PICK → MILL-PICK (falsches Modul)
- MILL-PICK → DRILL-PICK (falsches Modul)

### **Nach dem Fix:**
- DRILL-PICK → DRILL-PICK ✅
- AIQS-PICK → AIQS-PICK ✅
- MILL-PICK → MILL-PICK ✅

## 🔍 **Root Cause Analysis:**

### **Warum passierte das:**
1. **Copy-Paste-Fehler** bei der Initialisierung der `module_serials` Dictionary
2. **Fehlende Validierung** der Module-ID-Zuordnung
3. **Keine Unit-Tests** für Module-ID-Mapping

### **Präventionsmaßnahmen:**
1. **Unit-Tests** für Module-ID-Mapping hinzufügen
2. **Validierung** gegen `topic_config.yml` implementieren
3. **Code-Review** für kritische Mapping-Funktionen

## 📝 **Lektionen gelernt:**

1. **Module-ID-Mapping** ist kritisch für die Fabrik-Steuerung
2. **Copy-Paste-Fehler** können schwerwiegende Folgen haben
3. **Unit-Tests** sind essentiell für Mapping-Funktionen
4. **Validierung** gegen Konfigurationsdateien verhindert solche Fehler

## ✅ **Status:**
**BEHOBEN** - Module-Sequenz PICK → PROCESS → DROP funktioniert jetzt korrekt

## 🏷️ **Betroffene Tags:**
- dashboardv3.1.0 (fehlerhaft)
- dashboardv3.1.1 (fehlerhaft)
- dashboardv3.1.2 (geplant - mit Fix)
