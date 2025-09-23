# APS Configuration Tab - Detaillierte Analyse

**Datum:** 22.09.2025  
**Chat-B Assistent:** Code & Implementation  
**Status:** 📋 Analyse abgeschlossen - Bereit für Implementierung

## 🎯 **Configuration Tab Struktur**

### **Haupt-Tab: Configuration**
- **Zweck:** Systemkonfiguration und Fabrik-Layout
- **Status:** ❌ Fehlt komplett
- **Implementierung:** Neu erstellen

### **Untertabs:**
1. **Factory Configuration** - Fabrik-Layout und Modul-Anordnung
2. **Configuration** - Systemkonfiguration

## 🏭 **Untertab 1: Factory Configuration**

### **Funktionalität:**
- **Grid-basierte Modul-Anordnung** - Visuelle Darstellung der Fabrik
- **Modul-Positionierung** - Drag & Drop oder Grid-Positionierung
- **Pfad-Verbindungen** - Nummerierte Verbindungen zwischen Modulen
- **Modul-Verwaltung** - Hinzufügen, Löschen, Konfigurieren von Modulen

### **UI-Elemente:**
- **Toolbar:** Plus (+), Speichern (💾), Aktualisieren (🔄), Löschen (✂️), Zoom (🔍+/-)
- **Grid-Layout:** Raster-basierte Anordnung
- **Modul-Karten:** Icons, Namen, IDs
- **Verbindungslinien:** Nummerierte Pfade (1, 2, 3, 4)

### **Modul-Karten:**
1. **High-Bay Warehouse** - ID: SVR3QA0022
2. **Milling Station** - ID: SVR3QA2098  
3. **Quality Control with AI** - ID: SVR4H76530
4. **Delivery and Pickup Station** - ID: SVR4H73275
5. **Drilling Station** - ID: SVR4H76449
6. **Charging Station** - ID: CHRG0

### **Modul-Karten UI:**
- **Icon:** Modul-spezifisches Symbol
- **Name:** Modul-Name
- **ID:** Modul-Identifikation
- **Löschen:** Papierkorb-Icon (oben rechts)
- **Optionen:** Refresh (🔄) und More (⋯) Icons

## ⚙️ **Untertab 2: Configuration**

### **Funktionalität:**
- **Einfache Parameter** - Grundlegende Systemkonfiguration
- **Parameter-Verwaltung** - Konfigurationswerte setzen/ändern
- **Einstellungen** - System-spezifische Optionen

### **UI-Elemente:**
- **Einfache Formulare** - Parameter-Eingabefelder
- **Einstellungs-Formulare** - Konfigurationsoptionen
- **Speichern-Button** - Änderungen persistieren

### **Parameter-Typen:**
- **Numerische Parameter** - Sekunden (Total Duration)
- **Ganzzahl-Parameter** - Anzahl (Production Settings)
- **Prozent-Parameter** - Prozentwerte (Transport Settings)
- **Farbige Kategorien** - Workpiece-Typen (White, Blue, Red)

### **Spezifische Parameter:**

#### **1. Total Duration (Gesamtdauer)**
- **White Workpiece:** 580 Sekunden
- **Blue Workpiece:** 550 Sekunden  
- **Red Workpiece:** 560 Sekunden
- **UI:** Farbige Zylinder-Icons + Eingabefelder

#### **2. Production Settings (Produktionseinstellungen)**
- **Number of simultaneously producible workpieces:** 4
- **UI:** Eingabefeld für Anzahl

#### **3. Transport Settings (Transporteinstellungen)**
- **Charging threshold for AGV:** 10%
- **UI:** Eingabefeld für Prozentwert

### **UI-Elemente:**
- **Save Button** - Unten rechts für Speichern
- **Eingabefelder** - Für alle Parameter
- **Farbige Icons** - Für Workpiece-Typen (White, Blue, Red)
- **Kategorisierte Bereiche** - Total Duration, Production Settings, Transport Settings

## 🔗 **Mapping zu bestehenden OMF-Komponenten**

### **Factory Configuration → OMF Shopfloor Layout**
- **Bestehende Komponente:** `omf_shopfloor.py` / `shopfloor_layout.py`
- **Status:** ✅ Bereits nachgebaut
- **Implementierung:** Anpassen/Integrieren
- **Datei:** `omf/dashboard/components/shopfloor_layout.py`

### **Configuration → Neue Komponente**
- **Status:** ❌ Fehlt komplett
- **Implementierung:** Neu erstellen
- **Datei:** `omf/dashboard/components/aps_configuration.py`

## 🎯 **Implementierungs-Plan**

### **Phase 1: Factory Configuration**
- **Bestehende Komponente nutzen:** `shopfloor_layout.py`
- **Anpassungen:** APS-spezifische Modul-Karten
- **Integration:** In Configuration Tab einbinden

### **Phase 2: Configuration**
- **Neue Komponente erstellen:** `aps_system_configuration.py`
- **Funktionalität:** 3 Parameter-Bereiche (Total Duration, Production Settings, Transport Settings)
- **UI:** Eingabefelder mit farbigen Icons und Save-Button

### **Phase 3: Tab-Integration**
- **Haupt-Tab:** Configuration
- **Untertabs:** Factory Configuration + Configuration
- **Navigation:** Tab-System implementieren

## 🔧 **Technische Implementierung**

### **Neue Dateien:**
```
omf/dashboard/components/
├── aps_configuration.py           # Haupt-Tab: Configuration (Wrapper)
└── aps_system_configuration.py    # Untertab: Configuration (einfache Parameter)
```

### **Bestehende Dateien nutzen:**
```
omf/dashboard/components/
└── shopfloor_layout.py            # Factory Configuration (bereits vorhanden)
```

### **Dashboard-Integration:**
```
omf/dashboard/omf_dashboard.py
└── Configuration Tab (aps_configuration.py)
    ├── Factory Configuration (shopfloor_layout.py)
    └── Configuration (aps_system_configuration.py)
```

## 📊 **Modul-Daten aus Registry**

### **Verfügbare Module:**
- **SVR3QA0022** - High-Bay Warehouse
- **SVR3QA2098** - Milling Station
- **SVR4H76530** - Quality Control with AI
- **SVR4H73275** - Delivery and Pickup Station
- **SVR4H76449** - Drilling Station
- **CHRG0** - Charging Station

### **Registry-Templates:**
- **Module States:** `module.svr*.state.yml`
- **Module Factsheets:** `module.svr*.factsheet.yml`
- **Module Connections:** `module.svr*.connection.yml`

## 🎯 **Nächste Schritte**

1. **Configuration Tab erstellen** - `aps_configuration.py` (Wrapper mit Untertabs)
2. **System Configuration implementieren** - `aps_system_configuration.py` (einfache Parameter)
3. **Factory Configuration integrieren** - `shopfloor_layout.py` einbinden
4. **Untertab-Navigation** - Tab-System implementieren
5. **Integration und Testing** - Mit realer Fabrik testen

## 📚 **Ressourcen**

### **Bestehende Komponenten:**
- **Shopfloor Layout:** `omf/dashboard/components/shopfloor_layout.py`
- **Registry Manager:** `omf/dashboard/tools/registry_manager.py`

### **Registry-Templates:**
- **Module Templates:** `registry/model/v1/templates/module.*.yml`
- **Layout Templates:** `registry/model/v1/templates/ccu.state.layout.yml`

---

**Status:** Analyse abgeschlossen - Bereit für Implementierung 🚀
