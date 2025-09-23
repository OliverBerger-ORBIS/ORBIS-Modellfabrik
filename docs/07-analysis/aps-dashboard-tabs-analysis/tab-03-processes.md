# APS Processes Tab - Detaillierte Analyse

**Datum:** 22.09.2025  
**Chat-B Assistent:** Code & Implementation  
**Status:** 📋 Analyse abgeschlossen - Bereit für Implementierung

## 🎯 **Processes Tab Struktur**

### **Haupt-Tab: Processes**
- **Zweck:** Produktionsplanung und Workflow-Definition
- **Entspricht:** `production_order.product_planning`
- **Status:** ⏳ Neu zu implementieren
- **Implementierung:** Workflow-Diagramm mit Drag & Drop

## 🔄 **Processing Steps - Workflow-Diagramm**

### **Workflow-Struktur:**
```
[Retrieve via high-bay warehouse]
           ↓
    [Parallel Processing]
    ┌─────┬─────┬─────┐
    │Blue │Red  │White│
    │     │     │     │
    └─────┴─────┴─────┘
           ↓
[Delivery via Goods Outgoing]
```

### **Start-Punkt:**
- **"Retrieve via high-bay warehouse"** - Material-Entnahme
- **Icon:** Breites hellblaues Rechteck mit weißem Rand
- **Text:** Zentriert in blau

### **End-Punkt:**
- **"Delivery via Goods Outgoing"** - Warenausgang
- **Icon:** Breites hellblaues Rechteck mit weißem Rand
- **Text:** Zentriert in blau

## 🎨 **Parallel Processing - 3 Produkttypen**

### **1. Blue Product (Links)**
- **Icon:** 3D blauer Zylinder
- **Label:** "Blue"
- **Status:** 3 Verarbeitungsschritte
- **Processing Steps:**
  1. **Drilling Station** - Bohrer-Icon + Papierkorb-Icon
  2. **Milling Station** - Fräser-Icon + Papierkorb-Icon
  3. **Quality Control with AI** - Qualitätskontrolle-Icon + Papierkorb-Icon

### **2. Red Product (Mitte)**
- **Icon:** 3D roter Zylinder
- **Label:** "Red"
- **Status:** 2 Verarbeitungsschritte
- **Processing Steps:**
  1. **Milling Station** - Fräser-Icon + Papierkorb-Icon
  2. **Quality Control with AI** - Qualitätskontrolle-Icon + Papierkorb-Icon

### **3. White Product (Rechts)**
- **Icon:** 3D weißer Zylinder
- **Label:** "White"
- **Status:** 2 Verarbeitungsschritte
- **Processing Steps:**
  1. **Drilling Station** - Bohrer-Icon + Papierkorb-Icon
  2. **Quality Control with AI** - Qualitätskontrolle-Icon + Papierkorb-Icon

## 🛠️ **Processing Steps Controls**

### **Top-Left Controls:**
- **Plus Button (+)** - Neuen Verarbeitungsschritt hinzufügen
- **Save Button (💾)** - Workflow speichern
- **Refresh Button (🔄)** - Workflow zurücksetzen/aktualisieren
- **Toggle Switch:** "Activate advanced processing steps"

### **UI-Elemente:**
- **Kreisförmige Buttons** mit Icons
- **Toggle Switch** für erweiterte Funktionen
- **Papierkorb-Icons** zum Löschen von Schritten

## 🔗 **Mapping zu bestehenden OMF-Komponenten**

### **Processes Tab → OMF Production Order Planning**
- **Bestehende Komponente:** `production_order.product_planning`
- **Status:** ⏳ Zu implementieren
- **Implementierung:** Workflow-Diagramm mit Drag & Drop
- **Datei:** `omf/dashboard/components/production_order.py`

## 🎯 **Implementierungs-Plan**

### **Phase 1: Workflow-Diagramm erstellen**
- **Start/End-Punkte** implementieren
- **Parallel Processing** Layout
- **3 Produkttypen** (Blue, Red, White)

### **Phase 2: Drag & Drop Funktionalität**
- **Verarbeitungsschritte** hinzufügen/entfernen
- **Workflow-Editor** mit Drag & Drop
- **Speichern/Laden** von Workflows

### **Phase 3: Erweiterte Funktionen**
- **Advanced Processing Steps** Toggle
- **Real-time Updates** - MQTT-basierte Status-Updates
- **Workflow-Validierung**

## 🔧 **Technische Implementierung**

### **Neue Datei erstellen:**
```
omf/dashboard/components/
└── aps_processes.py    # Processes Tab (neu zu erstellen)
```

### **Workflow-Diagramm:**
- **Streamlit Graphviz** oder **Custom Canvas**
- **Drag & Drop** - Streamlit-Extras oder Custom Components
- **Workflow-Editor** - Interaktive Diagramm-Erstellung

### **Verarbeitungsschritte:**
- **Drilling Station** - Bohrer-Icon
- **Milling Station** - Fräser-Icon
- **Quality Control with AI** - Qualitätskontrolle-Icon
- **Papierkorb-Icon** - Löschen-Funktion

### **Dashboard-Integration:**
```
omf/dashboard/omf_dashboard.py
└── Processes Tab (aps_processes.py)
```

## 📊 **Produkttypen und Verarbeitungsschritte**

### **Blue Product:**
1. **Drilling Station** - Bohren
2. **Milling Station** - Fräsen
3. **Quality Control with AI** - Qualitätskontrolle

### **Red Product:**
1. **Milling Station** - Fräsen
2. **Quality Control with AI** - Qualitätskontrolle

### **White Product:**
1. **Drilling Station** - Bohren
2. **Quality Control with AI** - Qualitätskontrolle

## 🎯 **Nächste Schritte**

1. **Workflow-Diagramm implementieren** - Start/End-Punkte + Parallel Processing
2. **3 Produkttypen** - Blue, Red, White mit Icons
3. **Drag & Drop Funktionalität** - Verarbeitungsschritte hinzufügen/entfernen
4. **Controls implementieren** - Plus, Save, Refresh, Toggle
5. **Workflow-Editor** - Interaktive Diagramm-Erstellung
6. **Integration und Testing** - Mit realer Fabrik testen

## 📚 **Ressourcen**

### **Bestehende Komponenten:**
- **Production Order:** `omf/dashboard/components/production_order.py`
- **Registry Manager:** `omf/dashboard/tools/registry_manager.py`
- **MQTT Client:** `omf/dashboard/tools/omf_mqtt_client.py`

### **Technische Bibliotheken:**
- **Streamlit Graphviz** - Für Workflow-Diagramme
- **Streamlit-Extras** - Für Drag & Drop
- **Custom Components** - Für erweiterte UI

### **Registry-Templates:**
- **Production Templates:** `registry/model/v1/templates/production.*.yml`
- **Workflow Templates:** `registry/model/v1/templates/workflow.*.yml`

---

**Status:** Analyse abgeschlossen - Bereit für Implementierung 🚀
