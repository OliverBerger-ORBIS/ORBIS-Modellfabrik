# 🎯 MQTT-Template Testing Strategie

## 📋 **Aktueller Stand**

### ✅ **Bereits verfügbar:**
- **MQTT-Templates** im Dashboard implementiert
- **Working Messages** dokumentiert (DRILL PICK, etc.)
- **Message Library** mit funktionierenden Templates
- **Dashboard Integration** für Template-Steuerung

### ❌ **Bekannte Probleme:**
- **ORDER-ID Eindeutigkeit** nicht gewährleistet
- **Modul-Status-Monitoring** fehlt
- **Timing-Probleme** bei Command-Ausführung
- **Error-Handling** unstrukturiert

---

## 🎯 **Testing-Strategie: ORDER-ID Fokus**

### **Phase 1: ORDER-ID Management (KRITISCH)**
**Ziel**: Grundlegende Workflow-Probleme lösen

#### **1.1 Problem-Analyse**
- **🚨 KRITISCH**: `"OrderUpdateId not valid"` Fehler identifiziert
- **🚨 KRITISCH**: PROCESS-Befehle funktionieren nicht ohne korrekte ORDER-ID Sequenz
- **🚨 KRITISCH**: PICK → PROCESS → DROP Workflows benötigen ORDER-ID Tracking

#### **1.2 ORDER-ID Manager implementieren**
```python
class WorkflowOrderManager:
    def __init__(self):
        self.active_workflows = {}  # orderId -> {orderUpdateId, module, commands}
    
    def start_workflow(self, module, commands):
        order_id = str(uuid.uuid4())
        self.active_workflows[order_id] = {
            'orderUpdateId': 0,
            'module': module,
            'commands': commands,
            'status': 'active'
        }
        return order_id
    
    def get_next_order_update_id(self, order_id):
        if order_id in self.active_workflows:
            self.active_workflows[order_id]['orderUpdateId'] += 1
            return self.active_workflows[order_id]['orderUpdateId']
        return 1
```

#### **1.3 Workflow-Templates erstellen**
- **PICK → PROCESS → DROP** Templates mit ORDER-ID Tracking
- **Automatische orderUpdateId** Inkrementierung
- **Workflow-Status** Überwachung

### **Phase 2: Template-Testing (nach ORDER-ID Fix)**
**Ziel**: Systematisches Testing der Workflow-Templates

#### **2.1 Workflow-Template-Testing**
- **MQTT Control Tab** → Module Overview
- **PICK → PROCESS → DROP** Sequenzen testen
- **ORDER-ID Tracking** validieren

#### **2.2 Erwartete Ergebnisse:**
- ✅ **Workflow-Templates** funktionieren
- ✅ **ORDER-ID Management** funktioniert
- ✅ **Sequenzielle Befehle** erfolgreich
- ⚠️ **Workpiece-Dependencies** beachten

### **Phase 3: Erweiterte Testing (Woche 3)**
**Ziel**: Systematisches Template-Testing

#### **3.1 Modul-Status-Monitoring**
- **Module-Verfügbarkeit** erkennen
- **Status-Updates** in Echtzeit
- **Command-Timing** optimieren

#### **3.2 Template-Test-Suite**
```python
# Automatisierte Template-Tests
def test_all_templates():
    templates = ["DRILL_PICK", "HBW_STORE", "AIQS_CHECK_QUALITY"]
    for template in templates:
        result = test_template(template)
        log_result(template, result)
```

### **Phase 3: Erweiterte Testing (Woche 3)**
**Ziel**: Systematisches Template-Testing

#### **3.1 Modul-Status-Monitoring**
- **Module-Verfügbarkeit** erkennen
- **Status-Updates** in Echtzeit
- **Command-Timing** optimieren

#### **3.2 Template-Test-Suite**
```python
# Automatisierte Template-Tests
def test_all_templates():
    templates = ["DRILL_PICK", "HBW_STORE", "AIQS_CHECK_QUALITY"]
    for template in templates:
        result = test_template(template)
        log_result(template, result)
```

---

## 🔍 **Node-RED Tracking (Port 1883)**

### **Aktuelle Situation:**
- **Node-RED Gateway**: Port 1880 (OPC-UA ↔ MQTT)
- **MQTT-Broker**: Port 1883 (direkte MQTT-Nachrichten)
- **Dashboard**: Empfängt von Port 1883

### **Tracking-Strategie:**

#### **Option A: Einfach (empfohlen)**
```
Vorteile:
- Schnelle Implementierung
- Direkte Beobachtung
- Weniger Komplexität

Implementierung:
- Dashboard erweitern um Node-RED Topic-Filter
- Spezielle Node-RED Nachrichten markieren
- Separate Analyse-Sektion
```

#### **Option B: Erweitert (später)**
```
Vorteile:
- Vollständige Transparenz
- Detaillierte Analyse
- Gateway-Verständnis

Implementierung:
- Node-RED Flow-Analyse
- OPC-UA ↔ MQTT Mapping
- Gateway-Monitoring
```

### **Meine Empfehlung: Option A**
- **Sofort umsetzbar**
- **Weniger Komplexität**
- **Ausreichend für Template-Testing**

---

## 📊 **Testing-Plan**

### **Woche 1: ORDER-ID Management (KRITISCH)**
- [ ] **WorkflowOrderManager** implementieren
- [ ] **Workflow-Templates** erstellen
- [ ] **ORDER-ID Tracking** im Dashboard integrieren
- [ ] **PICK → PROCESS → DROP** Workflows testen

### **Woche 2: Template-Testing**
- [ ] **Workflow-Templates** systematisch testen
- [ ] **ORDER-ID Management** validieren
- [ ] **Fehlerbehandlung** implementieren
- [ ] **Performance-Optimierung**

### **Woche 3: Erweiterte Features**
- [ ] **Modul-Status-Monitoring** implementieren
- [ ] **Template-Test-Suite** erstellen
- [ ] **Automatisierte Tests** durchführen
- [ ] **Node-RED Tracking** (optional)

---

## 🎯 **Nächste Schritte**

### **Sofort (heute):**
1. **WorkflowOrderManager** implementieren
2. **Workflow-Templates** erstellen
3. **ORDER-ID Tracking** im Dashboard integrieren
4. **PICK → PROCESS → DROP** Workflows testen

### **Diese Woche:**
1. **ORDER-ID Management** vollständig implementieren
2. **Workflow-Templates** systematisch testen
3. **Fehlerbehandlung** für ORDER-ID Probleme

### **Nächste Woche:**
1. **Erweiterte Features** (Monitoring, Test-Suite)
2. **Performance-Optimierung**
3. **Node-RED Tracking** (optional)

---

## 📝 **Fazit**

**ORDER-ID Management ist KRITISCH für funktionierende Workflows!** 

**Empfohlener Ansatz:**
1. **WorkflowOrderManager** implementieren (KRITISCH)
2. **Workflow-Templates** mit ORDER-ID Tracking erstellen
3. **PICK → PROCESS → DROP** Sequenzen systematisch testen

**Node-RED Tracking:** Optional, nach ORDER-ID Management

**Timing:** Sofort ORDER-ID Management implementieren, dann systematisch testen
