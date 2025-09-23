# APS Modules Tab - Detaillierte Analyse

**Datum:** 22.09.2025  
**Chat-B Assistent:** Code & Implementation  
**Status:** 📋 Analyse abgeschlossen - Bereit für Implementierung

## 🎯 **Modules Tab Struktur**

### **Haupt-Tab: Modules**
- **Zweck:** Modul-Übersicht und -Steuerung
- **Status:** ✅ Bereits vorhanden (`overview_module_status.py`)
- **Implementierung:** Anpassen/Integrieren

## 📊 **Module Overview - Tabellen-Struktur**

### **Tabellen-Header:**
- **ID** - Modul-Identifikation
- **Name** - Modul-Name
- **Connected** - Verbindungsstatus (Wi-Fi Icon)
- **Availability status** - Verfügbarkeitsstatus
- **Configured** - Konfigurationsstatus und Aktionen

### **Verfügbare Module:**

#### **1. High-Bay Warehouse**
- **Icon:** Blaue gestapelte Kisten/Regale
- **ID:** `SVR3QA0022`
- **Name:** `High-Bay Warehouse`
- **Connected:** ✅ Wi-Fi Signal (blau)
- **Availability status:** `Available`
- **Configured:** ✅ Grid Icon + **"Calibrate" Button**

#### **2. Drilling Station**
- **Icon:** Blaue Bohrer-Icon
- **ID:** `SVR4H76449`
- **Name:** `Drilling Station`
- **Connected:** ✅ Wi-Fi Signal (blau)
- **Availability status:** `Available`
- **Configured:** ✅ Grid Icon

#### **3. Milling Station**
- **Icon:** Blaue Fräser-Icon
- **ID:** `SVR3QA2098`
- **Name:** `Milling Station`
- **Connected:** ✅ Wi-Fi Signal (blau)
- **Availability status:** `Available`
- **Configured:** ✅ Grid Icon

#### **4. Delivery and Pickup Station**
- **Icon:** Blaue Lieferwagen-Icon
- **ID:** `SVR4H73275`
- **Name:** `Delivery and Pickup Station`
- **Connected:** ✅ Wi-Fi Signal (blau)
- **Availability status:** `Available`
- **Configured:** ✅ Grid Icon + **"Calibrate" Button**

#### **5. Quality Control with AI**
- **Icon:** Blaue Qualitätskontrolle mit "AI" Symbol
- **ID:** `SVR4H76530`
- **Name:** `Quality Control with AI`
- **Connected:** ✅ Wi-Fi Signal (blau)
- **Availability status:** `Available`
- **Configured:** ✅ Grid Icon + **"Calibrate" Button**

#### **6. Charging Station**
- **Icon:** Blaue Batterie mit Blitz
- **ID:** `CHRGO`
- **Name:** `Charging Station`
- **Connected:** ✅ Wi-Fi Signal (blau)
- **Availability status:** `Busy`
- **Configured:** ✅ Grid Icon

#### **7. Automated Guided Vehicle (AGV)**
- **Icon:** Blaue AGV/Robot-Car Icon
- **ID:** `5iO4`
- **Name:** `Automated Guided Vehicle (AGV)`
- **Connected:** ✅ Wi-Fi Signal (blau)
- **Availability status:** `Blocked`
- **Configured:** ✅ Location Pin Icon + **"Finish charging" Button**

## 🎨 **UI-Elemente**

### **Status-Icons:**
- **Wi-Fi Signal (blau)** - Verbunden
- **Grid Icon (blau)** - Konfiguriert
- **Location Pin Icon** - Positioniert (nur AGV)

### **Status-Werte:**
- **Available** - Verfügbar
- **Busy** - Beschäftigt
- **Blocked** - Blockiert

### **Aktions-Buttons:**
- **"Calibrate" Button** - Kalibrierung (weiß mit Kalibrierungs-Icon)
- **"Finish charging" Button** - Ladevorgang beenden (weiß mit Batterie-Icon)

## 🔗 **Mapping zu bestehenden OMF-Komponenten**

### **Modules Tab → OMF Overview Module Status**
- **Bestehende Komponente:** `overview_module_status.py`
- **Status:** ✅ Bereits vorhanden
- **Implementierung:** Anpassen/Integrieren
- **Datei:** `omf/dashboard/components/overview_module_status.py`

## 🎯 **Implementierungs-Plan**

### **Phase 1: Bestehende Komponente analysieren**
- **Aktuelle Funktionalität** von `overview_module_status.py` verstehen
- **Gaps identifizieren** - Was fehlt im Vergleich zum Original?

### **Phase 2: APS-Module Tab anpassen**
- **Tabellen-Layout** implementieren
- **Status-Icons** hinzufügen
- **Aktions-Buttons** implementieren
- **7 Module** korrekt anzeigen

### **Phase 3: Funktionalität erweitern**
- **Calibrate-Buttons** funktional machen
- **Finish charging-Button** implementieren
- **Status-Updates** real-time

## 🔧 **Technische Implementierung**

### **Bestehende Datei anpassen:**
```
omf/dashboard/components/
└── overview_module_status.py    # Modules Tab (bereits vorhanden)
```

### **Neue Funktionalität:**
- **Tabellen-Layout** - Streamlit DataTable oder Custom Table
- **Status-Icons** - Wi-Fi, Grid, Location Pin Icons
- **Aktions-Buttons** - Calibrate, Finish charging
- **Real-time Updates** - MQTT-basierte Status-Updates

### **Dashboard-Integration:**
```
omf/dashboard/omf_dashboard.py
└── Modules Tab (overview_module_status.py)
```

## 📊 **Modul-Daten aus Registry**

### **Verfügbare Module:**
- **SVR3QA0022** - High-Bay Warehouse
- **SVR3QA2098** - Milling Station
- **SVR4H76530** - Quality Control with AI
- **SVR4H73275** - Delivery and Pickup Station
- **SVR4H76449** - Drilling Station
- **CHRGO** - Charging Station
- **5iO4** - Automated Guided Vehicle (AGV)

### **Registry-Templates:**
- **Module States:** `module.svr*.state.yml`
- **Module Factsheets:** `module.svr*.factsheet.yml`
- **Module Connections:** `module.svr*.connection.yml`

## 🎯 **Nächste Schritte**

1. **Bestehende Komponente analysieren** - `overview_module_status.py` verstehen
2. **Tabellen-Layout implementieren** - APS-ähnliche Tabelle
3. **Status-Icons hinzufügen** - Wi-Fi, Grid, Location Pin
4. **Aktions-Buttons implementieren** - Calibrate, Finish charging
5. **Real-time Updates** - MQTT-basierte Status-Updates
6. **Integration und Testing** - Mit realer Fabrik testen

## 📚 **Ressourcen**

### **Bestehende Komponenten:**
- **Overview Module Status:** `omf/dashboard/components/overview_module_status.py`
- **Registry Manager:** `omf/dashboard/tools/registry_manager.py`
- **MQTT Client:** `omf/dashboard/tools/omf_mqtt_client.py`

### **Registry-Templates:**
- **Module Templates:** `registry/model/v1/templates/module.*.yml`
- **Module States:** `registry/model/v1/templates/module.svr*.state.yml`

---

**Status:** Analyse abgeschlossen - Bereit für Implementierung 🚀
