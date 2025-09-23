# APS Dashboard Tabs - Analyse und Implementierungsplan

**Datum:** 22.09.2025  
**Chat-B Assistent:** Code & Implementation  
**Status:** 📋 Analyse abgeschlossen - Implementierung geplant

## 🎯 **Original APS Dashboard Tabs**

### **Zu implementierende Tabs (5 von 7):**

1. **Overview** - Systemübersicht und Status
2. **Orders** - Auftragsverwaltung und -steuerung  
3. **Processes** - Prozesssteuerung und -überwachung
4. **Configuration** - Systemkonfiguration
5. **Modules** - Modulstatus und -steuerung

### **Nicht zu implementierende Tabs:**
6. **Simulation game** - Für uns nicht interessant
7. **Messages** - Entspricht unserem `message_center.py` (nur weniger umfangreich)

## 📊 **Mapping zu bestehenden OMF-Komponenten**

| APS Tab | OMF Komponente | Status | Implementierung |
|---------|----------------|--------|-----------------|
| **Overview** | - | ❌ Fehlt | Neu implementieren |
| **Orders** | `aps_orders.py` | ✅ Vorhanden | Erweitern/Anpassen |
| **Processes** | - | ❌ Fehlt | Neu implementieren |
| **Configuration** | - | ❌ Fehlt | Neu implementieren |
| **Modules** | `overview_module_status.py` | ✅ Vorhanden | Anpassen/Integrieren |

## 🎯 **Implementierungs-Prioritäten**

### **Phase 1: Fehlende Tabs implementieren**
1. **Configuration Tab** - Systemkonfiguration (höchste Priorität)
2. **Overview Tab** - Systemübersicht und Status
3. **Processes Tab** - Prozesssteuerung

### **Phase 2: Bestehende Tabs anpassen**
4. **Orders Tab** - `aps_orders.py` erweitern
5. **Modules Tab** - `overview_module_status.py` integrieren

## 📋 **Detaillierte Tab-Analyse**

### **Tab 1: Overview**
- **Zweck:** Systemübersicht und Status
- **Status:** ❌ Fehlt komplett
- **Implementierung:** Neu erstellen
- **Komponente:** `aps_overview.py`

### **Tab 2: Orders** 
- **Zweck:** Auftragsverwaltung und -steuerung
- **Status:** ✅ Vorhanden (`aps_orders.py`)
- **Implementierung:** Erweitern/Anpassen
- **Komponente:** `aps_orders.py` (bereits vorhanden)

### **Tab 3: Processes**
- **Zweck:** Prozesssteuerung und -überwachung
- **Status:** ❌ Fehlt komplett
- **Implementierung:** Neu erstellen
- **Komponente:** `aps_processes.py`

### **Tab 4: Configuration**
- **Zweck:** Systemkonfiguration
- **Status:** ❌ Fehlt komplett
- **Implementierung:** Neu erstellen (höchste Priorität)
- **Komponente:** `aps_configuration.py`

### **Tab 5: Modules**
- **Zweck:** Modulstatus und -steuerung
- **Status:** ✅ Vorhanden (`overview_module_status.py`)
- **Implementierung:** Anpassen/Integrieren
- **Komponente:** `overview_module_status.py` (bereits vorhanden)

## 🔧 **Technische Implementierung**

### **Neue Komponenten zu erstellen:**
- `omf/dashboard/components/aps_overview.py`
- `omf/dashboard/components/aps_processes.py`
- `omf/dashboard/components/aps_configuration.py`

### **Bestehende Komponenten zu erweitern:**
- `omf/dashboard/components/aps_orders.py` (bereits vorhanden)
- `omf/dashboard/components/overview_module_status.py` (bereits vorhanden)

### **Dashboard-Integration:**
- Alle 5 Tabs in `omf_dashboard.py` einbinden
- Tab-Navigation implementieren
- Konsistente UI/UX

## 📚 **Ressourcen**

### **Original APS-Dashboard:**
- **URL:** `http://192.168.0.100/de/aps/`
- **Sourcen:** `integrations/ff-central-control-unit/aps-dashboard-source/`
- **Angular-App:** `main.3c3283515fab30fd.js`

### **Bestehende OMF-Komponenten:**
- **Orders:** `omf/dashboard/components/aps_orders.py`
- **Modules:** `omf/dashboard/components/overview_module_status.py`
- **Message Center:** `omf/dashboard/components/message_center.py`

## 🎯 **Nächste Schritte**

1. **Configuration Tab implementieren** - Höchste Priorität
2. **Overview Tab implementieren** - Systemübersicht
3. **Processes Tab implementieren** - Prozesssteuerung
4. **Bestehende Tabs anpassen** - Orders und Modules
5. **Dashboard-Integration** - Alle Tabs einbinden

---

**Status:** Analyse abgeschlossen - Bereit für Implementierung 🚀
