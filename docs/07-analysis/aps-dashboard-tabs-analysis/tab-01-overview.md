# APS Overview Tab - Detaillierte Analyse

**Datum:** 22.09.2025  
**Chat-B Assistent:** Code & Implementation  
**Status:** 📋 Analyse abgeschlossen - Bereit für Implementierung

## 🎯 **Overview Tab Struktur**

### **Haupt-Tab: Overview**
- **Zweck:** APS-Übersicht mit Bestellungen, Lagerbestand und Sensordaten
- **Status:** ⏳ Neu zu implementieren
- **Implementierung:** Bestehende OMF-Komponenten anpassen

## 📊 **APS-Overview - 4 Haupt-Panels**

### **1. APS: Bestellung (Kundenaufträge)**
- **Entspricht:** `omf_overview` - Kundenaufträge
- **Status:** ✅ Bereits vorhanden
- **Implementierung:** Anpassen/Integrieren

#### **3 Werkstück-Typen:**
- **Werkstück blau** - Blaue Zylinder-Icon
- **Werkstück rot** - Rote Zylinder-Icon  
- **Werkstück weiß** - Weiße Zylinder-Icon

#### **Pro Werkstück-Typ:**
- **Verfügbarkeit:** "auf Lager" (grüner Punkt)
- **Lagerbestand:** "3" (Anzahl)
- **Bestellen-Button** - "bestellen"

### **2. APS: Bestellung Rohware (Rohmaterial-Bestellung)**
- **Entspricht:** `omf_overview` - Rohmaterial_bestellung
- **Status:** ✅ Bereits vorhanden
- **Implementierung:** Anpassen/Integrieren

#### **3 Werkstück-Typen:**
- **Werkstück blau** - Menge: "0"
- **Werkstück rot** - Menge: "0"
- **Werkstück weiß** - Menge: "0"

### **3. APS: Lagerbestand - SVR3QA0022 (High-Bay Warehouse)**
- **Entspricht:** `omf_overview` - Lagerbestand
- **Status:** ✅ Bereits vorhanden
- **Implementierung:** Anpassen/Integrieren

#### **Grid-Layout (3x3):**
```
   1   2   3
A [R] [R] [B]
B [B] [ ] [B]
C [W] [B] [W]
```

#### **Grid-Details:**
- **Spalten:** 1, 2, 3
- **Zeilen:** A, B, C
- **Werkstücke:** R (rot), B (blau), W (weiß)
- **Leere Zellen:** Weiße Umrandung
- **Sensor-Icons:** Graue Icons neben Werkstücken

### **4. APS: NFC-Reader**
- **Status:** ⏳ Neu zu implementieren
- **Implementierung:** NFC-Funktionalität

#### **NFC-Buttons:**
- **"NFC lesen"** - NFC-Tag lesen
- **"NFC löschen"** - NFC-Tag löschen

## 🌡️ **Sensordaten-Panels (Rechte Seite)**

### **1. APS: Aktuelle Temperatur**
- **Anzeige:** Thermometer-Gauge
- **Wert:** `29.5°C`
- **Zeitstempel:** `26.8.2025, 18:30:55.535`

### **2. APS: Aktuelle Luftfeuchtigkeit**
- **Anzeige:** Kreisförmiger Gauge
- **Wert:** `26.8% r.H.`
- **Zeitstempel:** `26.8.2025, 18:30:55.535`

### **3. APS: Aktueller Luftdruck**
- **Anzeige:** Kreisförmiger Gauge
- **Wert:** `986.0 hPa`
- **Zeitstempel:** `26.8.2025, 18:30:55.535`

### **4. APS: Aktuelle Luftqualität**
- **Anzeige:** 3 Quadrate (2 grau, 1 grün)
- **Werte:** `IAQ: 41`, `Genauigkeit: 3`
- **Zeitstempel:** `26.8.2025, 18:30:55.535`

## 🔗 **Mapping zu bestehenden OMF-Komponenten**

### **Overview Tab → OMF Overview**
- **Bestehende Komponente:** `omf_overview.py`
- **Status:** ✅ Bereits vorhanden
- **Implementierung:** Anpassen/Integrieren
- **Datei:** `omf/dashboard/components/omf_overview.py`

### **Bestehende Komponenten:**
- **Kundenaufträge** ✅ - Entspricht "APS: Bestellung"
- **Rohmaterial_bestellung** ✅ - Entspricht "APS: Bestellung Rohware"
- **Lagerbestand** ✅ - Entspricht "APS: Lagerbestand - SVR3QA0022"

### **Neue Komponenten:**
- **NFC-Reader** ⏳ - Neu zu implementieren
- **Sensordaten** ⏳ - Neu zu implementieren

## 🎯 **Implementierungs-Plan**

### **Phase 1: Bestehende Komponenten analysieren**
- **Aktuelle Funktionalität** von `omf_overview.py` verstehen
- **Gaps identifizieren** - Was fehlt im Vergleich zum Original?

### **Phase 2: APS-Overview Layout implementieren**
- **4 Haupt-Panels** - Bestellung, Rohware, Lagerbestand, NFC-Reader
- **Sensordaten-Panels** - Temperatur, Luftfeuchtigkeit, Luftdruck, Luftqualität
- **Responsive Layout** - Streamlit Columns

### **Phase 3: Bestehende Komponenten anpassen**
- **Kundenaufträge** - APS-Design anwenden
- **Rohmaterial_bestellung** - APS-Design anwenden
- **Lagerbestand** - APS-Design anwenden

### **Phase 4: Neue Komponenten implementieren**
- **NFC-Reader** - NFC-Funktionalität
- **Sensordaten** - Temperatur, Luftfeuchtigkeit, Luftdruck, Luftqualität

### **Phase 5: Real-time Updates**
- **MQTT-basierte Updates** - Sensordaten, Lagerbestand
- **Status-Updates** - Verfügbarkeit, Bestellungen

## 🔧 **Technische Implementierung**

### **Bestehende Datei anpassen:**
```
omf/dashboard/components/
└── omf_overview.py    # Overview Tab (bereits vorhanden, anpassen)
```

### **Layout-Struktur:**
- **Haupt-Panels** - 4 Panels (Bestellung, Rohware, Lagerbestand, NFC-Reader)
- **Sensordaten-Panels** - 4 Panels (Temperatur, Luftfeuchtigkeit, Luftdruck, Luftqualität)
- **Streamlit Columns** - Responsive Layout

### **Bestehende Komponenten:**
- **Kundenaufträge** - Anpassen an APS-Design
- **Rohmaterial_bestellung** - Anpassen an APS-Design
- **Lagerbestand** - Anpassen an APS-Design

### **Neue Komponenten:**
- **NFC-Reader** - NFC-Funktionalität
- **Sensordaten** - Gauge-Widgets für Temperatur, Luftfeuchtigkeit, Luftdruck, Luftqualität

### **Dashboard-Integration:**
```
omf/dashboard/omf_dashboard.py
└── Overview Tab (omf_overview.py)
```

## 📊 **Sensordaten-Integration**

### **MQTT-Topics für Sensordaten:**
- **Temperatur:** `sensors/temperature`
- **Luftfeuchtigkeit:** `sensors/humidity`
- **Luftdruck:** `sensors/pressure`
- **Luftqualität:** `sensors/air_quality`

### **Real-time Updates:**
- **MQTT-Subscription** - Sensordaten-Topics
- **Gauge-Widgets** - Streamlit Gauge oder Custom Components
- **Zeitstempel** - Real-time Updates

## 🎯 **Nächste Schritte**

1. **Bestehende Komponente analysieren** - `omf_overview.py` verstehen
2. **APS-Overview Layout implementieren** - 4 Haupt-Panels + Sensordaten
3. **Bestehende Komponenten anpassen** - Kundenaufträge, Rohware, Lagerbestand
4. **NFC-Reader implementieren** - NFC-Funktionalität
5. **Sensordaten implementieren** - Temperatur, Luftfeuchtigkeit, Luftdruck, Luftqualität
6. **Real-time Updates** - MQTT-basierte Updates
7. **Integration und Testing** - Mit realer Fabrik testen

## 📚 **Ressourcen**

### **Bestehende Komponenten:**
- **OMF Overview:** `omf/dashboard/components/omf_overview.py`
- **Registry Manager:** `omf/dashboard/tools/registry_manager.py`
- **MQTT Client:** `omf/dashboard/tools/omf_mqtt_client.py`

### **Technische Bibliotheken:**
- **Streamlit Columns** - Für Layout
- **Streamlit Gauge** - Für Sensordaten
- **NFC-Library** - Für NFC-Funktionalität
- **MQTT Updates** - Für Real-time Updates

### **Registry-Templates:**
- **Order Templates:** `registry/model/v1/templates/order.*.yml`
- **Inventory Templates:** `registry/model/v1/templates/inventory.*.yml`
- **Sensor Templates:** `registry/model/v1/templates/sensor.*.yml`

---

**Status:** Analyse abgeschlossen - Bereit für Implementierung 🚀
