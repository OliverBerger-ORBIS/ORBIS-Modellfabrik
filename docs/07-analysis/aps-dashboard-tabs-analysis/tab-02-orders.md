# APS Orders Tab - Detaillierte Analyse

**Datum:** 22.09.2025  
**Chat-B Assistent:** Code & Implementation  
**Status:** 📋 Analyse abgeschlossen - Bereit für Implementierung

## 🎯 **Orders Tab Struktur**

### **Haupt-Tab: Orders**
- **Zweck:** Fertigungsaufträge und laufende Produktionsschritte
- **Entspricht:** `Fertigungsaufträge.laufende Fertigungsaufträge`
- **Status:** ✅ Bereits vorhanden (`aps_orders.py`)
- **Implementierung:** Erweitern/Verbessern

## 📋 **Orders Tab - 2-Spalten-Layout**

### **Linke Spalte: Orders & Production Steps**
- **Ongoing orders** - Laufende Aufträge
- **Production steps** - Produktionsschritte mit Status

### **Rechte Spalte: Visualisierung & Order Info**
- **Current production step** - Grafische Fabrik-Darstellung
- **Order information** - Auftragsdetails

## 🏭 **Ongoing Orders - Tabellen-Struktur**

### **Tabellen-Header:**
- **Order** - Auftragsnummer/Zeitstempel
- **Color** - Werkstück-Farbe (WHITE, BLUE, RED)
- **Timestamp** - Zeitstempel mit Play-Icon

### **Beispiel-Entry:**
- **Order:** `05:34`
- **Color:** `WHITE`
- **Timestamp:** `9/22/25, 5:34 PM` (mit Play-Icon)

## 🔄 **Production Steps - Status-System**

### **Status-Icons:**
- **✅ Grüner Haken** - Abgeschlossen
- **▶️ Schwarzer Punkt** - Aktueller Schritt
- **⏰ Graue Uhr** - Ausstehend

### **Production Steps Sequenz:**

#### **Abgeschlossene Schritte (✅):**
1. **Automated Guided Vehicle (AGV) > High-Bay Warehouse**
2. **High-Bay Warehouse: Load AGV**
3. **Automated Guided Vehicle (AGV) > Drilling Station**

#### **Aktueller Schritt (▶️):**
4. **Drilling Station: Unload AGV**

#### **Ausstehende Schritte (⏰):**
5. **Drilling Station: Drilling**
6. **Drilling Station: Load AGV**
7. **Automated Guided Vehicle (AGV) > Quality Control with AI**
8. **Quality Control with AI: Unload AGV**
9. **Quality Control with AI: Quality check**
10. **Quality Control with AI: Load AGV**
11. **Automated Guided Vehicle (AGV) > Delivery and Pickup Station**
12. **Delivery and Pickup Station: Unload AGV**

## 🏭 **Current Production Step - Fabrik-Layout**

### **Grid-Layout (2x3):**
```
[High-Bay Warehouse] [Milling Station] [Quality Control with AI] [Delivery Station]
[Drilling Station]   [Charging Station] [                        ] [                ]
```

### **Stationen mit IDs:**
- **High-Bay Warehouse:** `SVR3QA0022` (gestapelte Kisten)
- **Milling Station:** `SVR3QA2098` (Fräser)
- **Quality Control with AI:** `SVR4H73275` (Lupe + AI)
- **Delivery and Pickup Station:** `SVR4H76449` (2 Lieferwagen)
- **Drilling Station:** `SVR4H76530` (Bohrer) - **AKTIV (gelber Rahmen)**
- **Charging Station:** `CHRGO` (Batterie)

### **Verbindungen:**
- **Nummerierte Linien:** 1, 2, 3, 4
- **AGV-Pfade** zwischen Stationen

## 📊 **Order Information - Auftragsdetails**

### **Order Details:**
- **Order number:** `765F2294-9273-4390-885c-150a40490e91`
- **Order status:** `Processing`
- **Order date:** `9/22/25, 5:34 PM`
- **Order receipt:** `9/22/25, 5:34 PM`
- **Start of processing:** `9/22/25, 5:34 PM`

## 🔗 **Mapping zu bestehenden OMF-Komponenten**

### **Orders Tab → OMF APS Orders**
- **Bestehende Komponente:** `aps_orders.py`
- **Status:** ✅ Bereits vorhanden
- **Implementierung:** Erweitern/Verbessern
- **Datei:** `omf/dashboard/components/aps_orders.py`

## 🎯 **Implementierungs-Plan**

### **Phase 1: Bestehende Komponente analysieren**
- **Aktuelle Funktionalität** von `aps_orders.py` verstehen
- **Gaps identifizieren** - Was fehlt im Vergleich zum Original?

### **Phase 2: 2-Spalten-Layout implementieren**
- **Linke Spalte:** Ongoing Orders + Production Steps
- **Rechte Spalte:** Current Production Step + Order Information
- **Responsive Layout** - Streamlit Columns

### **Phase 3: Production Steps erweitern**
- **Status-System** - ✅ ▶️ ⏰ Icons
- **Sequenzielle Schritte** - 12+ Produktionsschritte
- **Real-time Updates** - MQTT-basierte Status-Updates

### **Phase 4: Fabrik-Layout implementieren**
- **Grid-Layout** - 2x3 Stationen
- **Station-Icons** - Mit IDs und Namen
- **Verbindungen** - Nummerierte Linien
- **Aktive Station** - Gelber Rahmen

### **Phase 5: Order Information erweitern**
- **Order Details** - UUID, Status, Zeitstempel
- **Real-time Updates** - MQTT-basierte Updates

## 🔧 **Technische Implementierung**

### **Bestehende Datei erweitern:**
```
omf/dashboard/components/
└── aps_orders.py    # Orders Tab (bereits vorhanden, erweitern)
```

### **2-Spalten-Layout:**
- **Streamlit Columns** - `st.columns([2, 1])`
- **Linke Spalte:** Orders + Production Steps
- **Rechte Spalte:** Fabrik-Layout + Order Info

### **Production Steps:**
- **Status-Icons** - ✅ ▶️ ⏰ (Streamlit Icons)
- **Sequenzielle Liste** - Mit Icons und Status
- **Real-time Updates** - MQTT-basierte Updates

### **Fabrik-Layout:**
- **Grid-Layout** - Custom CSS oder Streamlit Grid
- **Station-Icons** - Mit IDs und Namen
- **Verbindungen** - Nummerierte Linien
- **Aktive Station** - Gelber Rahmen

### **Dashboard-Integration:**
```
omf/dashboard/omf_dashboard.py
└── Orders Tab (aps_orders.py)
```

## 📊 **Order-Management Workflow**

### **Order-Erstellung:**
1. **Kundenbestellung** → **Fertigungsauftrag**
2. **Produkt-Planung** → **Module-Auswahl**
3. **Produktionsschritte** → **Status-Kontrolle**
4. **Grafische Repräsentation** → **Werkstück-Position**

### **OrderID als logische Klammer:**
- **OrderID:** `765F2294-9273-4390-885c-150a40490e91`
- **Verbindet:** Order, Production Steps, Status, Position

## 🎯 **Nächste Schritte**

1. **Bestehende Komponente analysieren** - `aps_orders.py` verstehen
2. **2-Spalten-Layout implementieren** - Orders + Fabrik-Layout
3. **Production Steps erweitern** - Status-System + 12+ Schritte
4. **Fabrik-Layout implementieren** - Grid + Stationen + Verbindungen
5. **Order Information erweitern** - Details + Real-time Updates
6. **Integration und Testing** - Mit realer Fabrik testen

## 📚 **Ressourcen**

### **Bestehende Komponenten:**
- **APS Orders:** `omf/dashboard/components/aps_orders.py`
- **Registry Manager:** `omf/dashboard/tools/registry_manager.py`
- **MQTT Client:** `omf/dashboard/tools/omf_mqtt_client.py`

### **Technische Bibliotheken:**
- **Streamlit Columns** - Für 2-Spalten-Layout
- **Streamlit Icons** - Für Status-Icons
- **Custom CSS** - Für Fabrik-Layout
- **MQTT Updates** - Für Real-time Status

### **Registry-Templates:**
- **Order Templates:** `registry/model/v1/templates/order.*.yml`
- **Production Templates:** `registry/model/v1/templates/production.*.yml`
- **Module Templates:** `registry/model/v1/templates/module.*.yml`

---

**Status:** Analyse abgeschlossen - Bereit für Implementierung 🚀
