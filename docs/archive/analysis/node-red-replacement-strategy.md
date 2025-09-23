# APS-NodeRED Ersatz-Strategie: OMF Dashboard übernimmt Produktionssteuerung

## 📋 Übersicht

**Ziel:** APS-NodeRED Flows schrittweise deaktivieren und durch OMF Dashboard ersetzen, um die komplette Produktionssteuerung zu übernehmen.

**Status:** 🚀 **IN IMPLEMENTIERUNG** - ModuleStateManager funktional, Logging-System implementiert

## 🎯 Aktuelle Architektur

### **Fischertechnik APS (192.168.0.100):**
```
Raspberry Pi (192.168.0.100)
├── MQTT-Broker (Port 1883)
├── APS-NodeRED (Port 1880) ← ZU ERSETZEN
├── Zentrale Steuereinheit (CCU)
└── Web-Interface (Port 80)
```

### **Unsere Entwicklungsumgebung:**
```
OMF Dashboard (localhost)
├── MQTT-Client (Verbindung zu 192.168.0.100:1883)
├── Session Manager (Testing/Validation)
└── DSP RPI (OPC-UA Integration)
```

## 🔍 APS-NodeRED Flows Analyse

### **Gefundene Komponenten:**
- **25 Tabs:** 1 Init + 24 Modul-Tabs (MILL, DRILL, OVEN, AIQS, HBW, DPS)
- **402 Function Nodes:** Zentrale Logik in JavaScript
- **12 MQTT Nodes:** Meist mit dynamischen Topics
- **Order Handling:** 4567 Zeilen Code - zentrale Steuerungslogik

### **Kritische Node-RED Funktionen:**
1. **Order Handling Engine** (4567 Zeilen)
   - Modul-Status-Management (IDLE → PICKBUSY → WAITING_AFTER_PICK → MILLBUSY → etc.)
   - Command-Validierung (PICK, DROP, MILL, DRILL, CHECK_QUALITY)
   - OPC-UA Write-Operations (ns=4;i=5 = pick, ns=4;i=6 = drop, ns=4;i=4 = mill)

2. **VDA5050 Status Publishing**
   - vda_status_RUNNING, vda_status_FAILED, vda_status_finished
   - Action-State-Tracking (PENDING → RUNNING → FINISHED/FAILED)

3. **Modul-spezifische Logik**
   - 24 Modul-Tabs mit spezifischer Steuerungslogik
   - Workflow-Sequenzen (PICK → MILL → DROP)
   - Timing-Abhängigkeiten zwischen Modulen

## ✅ OMF Dashboard - Bereits vorhandene Komponenten

### **1. Modul-Status-Management:**
- **Datei:** `overview_module_status.py`
- **Funktion:** Status-Anzeige mit Icons und Modul-spezifischen Mappings
- **Status:** ✅ **VOLLSTÄNDIG FUNKTIONAL**

### **2. WorkflowOrderManager:**
- **Datei:** `workflow_order_manager.py`
- **Funktion:** orderId/orderUpdateId Management, Workflow-Status-Tracking
- **Status:** ✅ **VOLLSTÄNDIG IMPLEMENTIERT**

### **3. MQTT-Gateway:**
- **Datei:** `mqtt_gateway.py`
- **Funktion:** Sauberes MQTT-Publishing mit Message-Generator Integration
- **Status:** ✅ **VOLLSTÄNDIG FUNKTIONAL**

### **4. Modul-Konfiguration:**
- **Datei:** `module_config.yml`
- **Funktion:** Verfügbare Commands, Status, ENUM-Werte
- **Status:** ✅ **VOLLSTÄNDIG KONFIGURIERT**

### **5. Bereits funktionierende Commands:**
- **Factory-Reset** ✅
- **FTS-Steuerung** ✅ (dock, laden, laden beenden)
- **Modul-Sequenzen** ✅ (PICK-<PROCESS>-DROP für AIQS, MILL, DRILL)
- **Bestellungen** ✅ (ROT, WEISS, BLAU)
- **FTS-Navigation** ✅ (DPS → HBW)

## ❌ Was fehlt für Node-RED Ersatz

### **1. Timing-Management (KRITISCH):**
**Problem:** Aktuell manuelle Sichtkontrolle für `<PROCESS>`-Commands

**Lösung:** Automatisches Timing-Management
```python
class ModuleStateManager:
    def __init__(self):
        self.module_states = {
            "AIQS": "IDLE",
            "MILL": "IDLE", 
            "DRILL": "IDLE"
        }
    
    def execute_sequence(self, module_name, sequence):
        # PICK → warten auf PICKBUSY → PROCESS → warten auf WAITING_AFTER_PICK → DROP
        pass
```

### **2. OPC-UA Integration über DSP:**
**Problem:** Node-RED macht OPC-UA Write-Operations

**Lösung:** DSP (Distributed Shopfloor Processing) nutzen
```python
class OPCUAManager:
    def write_to_sps(self, module_id, node_id, value, datatype):
        # Über DSP RPI an SPS schreiben
        # ns=4;i=5 = pick, ns=4;i=6 = drop, ns=4;i=4 = mill
        pass
```

### **3. Status-Subscription (Erweitern):**
**Problem:** Node-RED überwacht Modul-Status

**Lösung:** MQTT-Status-Subscription erweitern
```python
class StatusMonitor:
    def subscribe_to_module_states(self):
        # module/v1/ff/*/state
        # module/v1/ff/*/connection
        pass
```

### **4. Workflow-Engine (Erweitern):**
**Problem:** Node-RED koordiniert komplexe Workflows

**Lösung:** Workflow-Engine im OMF Dashboard erweitern
```python
class WorkflowEngine:
    def execute_production_order(self, order_type, color):
        # ROT: HBW → MILL → AIQS → DPS
        # WEISS: HBW → DRILL → AIQS → DPS  
        # BLAU: HBW → DRILL → MILL → AIQS → DPS
        pass
```

## 🚀 Implementierungs-Strategie

### **Phase 1: Parallel-Entwicklung (AKTUELL)**
**Ziel:** OMF Dashboard erweitern, ohne Node-RED zu deaktivieren

#### **Schritt 1.1: Timing-Management implementieren**
- **ModuleStateManager** erstellen
- **Status-Subscription** für alle Module
- **Automatische Sequenz-Ausführung** mit Timing

#### **Schritt 1.2: MQTT-Command-Vergleich**
- **Node-RED Commands** aufzeichnen (Session Manager)
- **OMF Dashboard Commands** generieren
- **Vergleich** der Message-Formate

#### **Schritt 1.3: DSP Integration vorbereiten**
- **OPC-UA Client** auf DSP RPI implementieren
- **MQTT-Bridge** zwischen OMF Dashboard und DSP
- **Node-ID Mapping** implementieren

### **Phase 2: Schrittweise Node-RED Deaktivierung**
**Ziel:** Node-RED Flows schrittweise deaktivieren und durch OMF Dashboard ersetzen

#### **Schritt 2.1: Backup und Vorbereitung**
- **Node-RED Flows** vollständig sichern
- **Test-Umgebung** einrichten
- **Rollback-Plan** definieren

#### **Schritt 2.2: Einzelne Modul-Tabs deaktivieren**
- **MILL #1** Tab deaktivieren
- **OMF Dashboard** übernimmt MILL #1 Steuerung
- **Testing** und Validierung

#### **Schritt 2.3: Weitere Module übernehmen**
- **DRILL #1, AIQS #1** etc. schrittweise
- **Komplette Workflows** testen
- **Performance** überwachen

### **Phase 3: Vollständige Übernahme**
**Ziel:** OMF Dashboard übernimmt komplette Produktionssteuerung

#### **Schritt 3.1: Alle Modul-Tabs deaktivieren**
- **Node-RED** komplett deaktivieren
- **OMF Dashboard** als einzige Steuerung
- **End-to-End Testing**

#### **Schritt 3.2: Optimierung und Monitoring**
- **Performance** optimieren
- **Error-Handling** verbessern
- **Monitoring** implementieren

## 📊 Vergleich: Node-RED vs. OMF Dashboard

### **Node-RED (Zu ersetzen):**
- **Order Handling:** 4567 Zeilen JavaScript
- **Modul-Status:** Flow-basierte Zustandsverwaltung
- **OPC-UA:** Direkte SPS-Kommunikation
- **Timing:** Automatisch (aber komplex)

### **OMF Dashboard (Zu erweitern):**
- **WorkflowOrderManager:** ✅ Bereits implementiert
- **Modul-Status:** ✅ Teilweise vorhanden
- **MQTT-Gateway:** ✅ Vollständig funktional
- **Timing:** ❌ Manuell (zu automatisieren)

## ✅ Implementierungsfortschritt

### **Abgeschlossen (Phase 1.1):**
1. ✅ **ModuleStateManager** implementiert und funktional
2. ✅ **Logging-System** implementiert (thread-sicher, JSON-Format)
3. ✅ **UI-Refresh-Mechanismus** implementiert (st.rerun() Problem gelöst)
4. ✅ **Dashboard-Integration** mit Tabs für Modul-Steuerung und Logs
5. ✅ **MQTT-Gateway-Integration** für Command-Sending

### **Aktuell (Phase 1.2):**
1. 🔄 **Logger in allen Komponenten** einbauen
2. 🔄 **Sequenz-Steuerung** weiter ausbauen
3. 🔄 **Command-Response-Testing** implementieren

## 🎯 Nächste Schritte

### **Sofort (Phase 1.2):**
1. **Logger-Integration** in alle Dashboard-Komponenten
2. **Sequenz-Testing** - Hypothese der Modul-Abfolge validieren
3. **Command-Response-Monitoring** implementieren

### **Kurzfristig (Phase 1.3):**
1. **MQTT-Command-Vergleich** Node-RED vs OMF Dashboard
2. **DSP Integration** vorbereiten
3. **Real-Factory-Testing** durchführen

## 🧪 Testing-Strategie

### **Command-Response-Validation:**
1. **Hypothese testen:** Modul-Abfolge und Rückmeldung stimmen mit realer Fabrik überein
2. **OMF-Response-Identität:** OMF Dashboard Commands = Node-RED Commands
3. **Timing-Validation:** Automatische Sequenz-Ausführung funktioniert korrekt

### **Test-Szenarien:**
- **PICK → PROCESS → DROP** Sequenzen
- **Modul-Status-Übergänge** validieren
- **MQTT-Command-Format** vergleichen
- **Error-Handling** bei Modul-Fehlern

### **Mittelfristig (Phase 2):**
1. **Node-RED Backup** erstellen
2. **Erste Modul-Tabs** deaktivieren
3. **Schrittweise Übernahme** beginnen

## 📁 Dokumentations-Integration

### **Bestehende Dokumente erweitern:**
- **`docs/PROJECT_OVERVIEW.md`** - Phase 3 aktualisieren
- **`omf/omf/dashboard/components/README.md`** - Neue Komponenten dokumentieren
- **`docs/OMF_ARCHITECTURE.md`** - Architektur-Änderungen dokumentieren

### **Neue Dokumente:**
- **`docs/analysis/node-red-replacement-strategy.md`** - Diese Datei
- **`docs/implementation/module-state-manager.md`** - Implementierungs-Details
- **`docs/testing/command-comparison.md`** - MQTT-Command-Vergleich

---

**Erstellt:** $(date)
**Status:** 📋 **STRATEGIE DEFINIERT** - Bereit für Implementierung
**Nächster Schritt:** ModuleStateManager implementieren
