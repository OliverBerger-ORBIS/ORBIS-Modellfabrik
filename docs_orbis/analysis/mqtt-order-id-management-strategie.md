# 🚨 MQTT ORDER-ID Management Strategie

## 📋 **Kritisches Problem identifiziert**

### **🚨 ROOT CAUSE: `"OrderUpdateId not valid"`**
```
Fehler in MQTT Response:
{
  "actionState": {
    "state": "FAILED",
    "command": "PICK"
  },
  "errors": [
    {
      "errorType": "Validation",
      "errorMessage": "OrderUpdateId not valid"
    }
  ]
}
```

### **🔍 Problem-Analyse:**
1. **ORDER-ID**: Wird korrekt generiert (UUID)
2. **orderUpdateId**: Bleibt immer `1` für alle Commands
3. **Workflow-Sequenz**: PICK → PROCESS → DROP benötigt inkrementelle orderUpdateId
4. **APS-Erwartung**: orderUpdateId muss für sequenzielle Commands steigen (1, 2, 3...)

---

## 🎯 **Lösungsstrategie: WorkflowOrderManager**

### **1. WorkflowOrderManager Klasse**
```python
import uuid
from datetime import datetime
from typing import Dict, List, Optional

class WorkflowOrderManager:
    def __init__(self):
        self.active_workflows: Dict[str, Dict] = {}
        self.workflow_history: List[Dict] = []
    
    def start_workflow(self, module: str, commands: List[str], workpiece_type: str = "WHITE") -> str:
        """Startet einen neuen Workflow und gibt orderId zurück"""
        order_id = str(uuid.uuid4())
        
        self.active_workflows[order_id] = {
            'orderId': order_id,
            'orderUpdateId': 0,
            'module': module,
            'commands': commands,
            'workpiece_type': workpiece_type,
            'status': 'active',
            'start_time': datetime.now(),
            'executed_commands': []
        }
        
        return order_id
    
    def get_next_order_update_id(self, order_id: str) -> int:
        """Gibt die nächste orderUpdateId für einen Workflow zurück"""
        if order_id in self.active_workflows:
            self.active_workflows[order_id]['orderUpdateId'] += 1
            return self.active_workflows[order_id]['orderUpdateId']
        return 1
    
    def execute_command(self, order_id: str, command: str) -> Dict:
        """Führt einen Command im Workflow aus"""
        if order_id not in self.active_workflows:
            raise ValueError(f"Workflow {order_id} nicht gefunden")
        
        workflow = self.active_workflows[order_id]
        order_update_id = self.get_next_order_update_id(order_id)
        
        # Command ausführen
        workflow['executed_commands'].append({
            'command': command,
            'orderUpdateId': order_update_id,
            'timestamp': datetime.now()
        })
        
        return {
            'orderId': order_id,
            'orderUpdateId': order_update_id,
            'command': command,
            'module': workflow['module']
        }
    
    def complete_workflow(self, order_id: str) -> Dict:
        """Schließt einen Workflow ab"""
        if order_id not in self.active_workflows:
            raise ValueError(f"Workflow {order_id} nicht gefunden")
        
        workflow = self.active_workflows[order_id]
        workflow['status'] = 'completed'
        workflow['end_time'] = datetime.now()
        
        # Zur Historie hinzufügen
        self.workflow_history.append(workflow.copy())
        del self.active_workflows[order_id]
        
        return workflow
    
    def get_active_workflows(self) -> Dict[str, Dict]:
        """Gibt alle aktiven Workflows zurück"""
        return self.active_workflows
    
    def get_workflow_status(self, order_id: str) -> Optional[Dict]:
        """Gibt den Status eines Workflows zurück"""
        return self.active_workflows.get(order_id)
```

### **2. Workflow-Templates mit ORDER-ID Tracking**
```python
class WorkflowTemplateManager:
    def __init__(self, order_manager: WorkflowOrderManager):
        self.order_manager = order_manager
        self.message_library = MQTTMessageLibrary()
    
    def create_pick_process_drop_workflow(self, module: str, workpiece_type: str = "WHITE") -> str:
        """Erstellt einen PICK → PROCESS → DROP Workflow"""
        commands = ['PICK', 'PROCESS', 'DROP']
        order_id = self.order_manager.start_workflow(module, commands, workpiece_type)
        return order_id
    
    def execute_workflow_step(self, order_id: str, step: str) -> Dict:
        """Führt einen Workflow-Schritt aus"""
        workflow_info = self.order_manager.execute_command(order_id, step)
        
        # MQTT-Nachricht erstellen
        message = self.message_library.create_order_message(
            workflow_info['module'],
            workflow_info['command'],
            {
                'orderId': workflow_info['orderId'],
                'orderUpdateId': workflow_info['orderUpdateId'],
                'type': self.order_manager.active_workflows[order_id]['workpiece_type']
            }
        )
        
        return {
            'message': message,
            'topic': f"module/v1/ff/{self.get_module_serial(workflow_info['module'])}/order",
            'workflow_info': workflow_info
        }
    
    def get_module_serial(self, module_name: str) -> str:
        """Gibt die Seriennummer für ein Modul zurück"""
        module_serials = {
            'MILL': 'SVR3QA2098',
            'DRILL': 'SVR4H76449',
            'AIQS': 'SVR4H76530',
            'HBW': 'SVR3QA0022',
            'DPS': 'SVR4H73275'
        }
        return module_serials.get(module_name, '')
```

---

## 🛠️ **Dashboard Integration**

### **1. WorkflowOrderManager im Dashboard**
```python
# In aps_dashboard.py
class APSDashboard:
    def __init__(self, db_file, verbose_mode=False):
        # ... existing code ...
        self.workflow_manager = WorkflowOrderManager()
        self.workflow_templates = WorkflowTemplateManager(self.workflow_manager)
    
    def start_workflow(self, module: str, workpiece_type: str = "WHITE"):
        """Startet einen neuen Workflow"""
        order_id = self.workflow_templates.create_pick_process_drop_workflow(module, workpiece_type)
        st.session_state.active_workflow = order_id
        return order_id
    
    def execute_workflow_step(self, step: str):
        """Führt einen Workflow-Schritt aus"""
        order_id = st.session_state.get('active_workflow')
        if not order_id:
            st.error("Kein aktiver Workflow")
            return
        
        result = self.workflow_templates.execute_workflow_step(order_id, step)
        
        # MQTT-Nachricht senden
        success, response = self.send_mqtt_message_direct(result['topic'], result['message'])
        
        if success:
            st.success(f"✅ {step} ausgeführt (orderUpdateId: {result['workflow_info']['orderUpdateId']})")
        else:
            st.error(f"❌ {step} fehlgeschlagen: {response}")
```

### **2. Workflow-UI im Dashboard**
```python
def show_workflow_control(self):
    """Zeigt Workflow-Steuerung im Dashboard"""
    st.subheader("🔄 Workflow Control")
    
    # Workflow starten
    col1, col2, col3 = st.columns(3)
    
    with col1:
        module = st.selectbox("Modul:", ["MILL", "DRILL", "AIQS"])
    
    with col2:
        workpiece_type = st.selectbox("Workpiece:", ["WHITE", "RED", "BLUE"])
    
    with col3:
        if st.button("🚀 Workflow starten"):
            order_id = self.start_workflow(module, workpiece_type)
            st.success(f"Workflow gestartet: {order_id[:8]}...")
    
    # Workflow-Schritte ausführen
    if st.session_state.get('active_workflow'):
        st.markdown("**Workflow-Schritte:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 PICK"):
                self.execute_workflow_step("PICK")
        
        with col2:
            if st.button("⚙️ PROCESS"):
                self.execute_workflow_step("PROCESS")
        
        with col3:
            if st.button("📤 DROP"):
                self.execute_workflow_step("DROP")
        
        # Workflow-Status anzeigen
        workflow_status = self.workflow_manager.get_workflow_status(st.session_state.active_workflow)
        if workflow_status:
            st.info(f"**Aktiver Workflow:** {workflow_status['orderId'][:8]}... | "
                   f"**Schritte:** {len(workflow_status['executed_commands'])}/{len(workflow_status['commands'])}")
```

---

## 📊 **Implementierungsplan**

### **Phase 1: Core Implementation (Tag 1)**
- [ ] **WorkflowOrderManager** implementieren
- [ ] **WorkflowTemplateManager** implementieren
- [ ] **Unit Tests** für ORDER-ID Management

### **Phase 2: Dashboard Integration (Tag 2)**
- [ ] **WorkflowOrderManager** in Dashboard integrieren
- [ ] **Workflow-UI** implementieren
- [ ] **MQTT-Integration** mit ORDER-ID Tracking

### **Phase 3: Testing & Validation (Tag 3)**
- [ ] **PICK → PROCESS → DROP** Workflows testen
- [ ] **ORDER-ID Tracking** validieren
- [ ] **Fehlerbehandlung** implementieren

### **Phase 4: Optimization (Tag 4)**
- [ ] **Performance-Optimierung**
- [ ] **UI-Verbesserungen**
- [ ] **Dokumentation** aktualisieren

---

## 🎯 **Erwartete Ergebnisse**

### **✅ Nach Implementierung:**
1. **ORDER-ID Tracking**: Korrekte orderUpdateId Sequenz (1, 2, 3...)
2. **Workflow-Templates**: PICK → PROCESS → DROP funktioniert
3. **Fehlerbehandlung**: `"OrderUpdateId not valid"` behoben
4. **Dashboard-Integration**: Workflow-Steuerung verfügbar

### **⚠️ Zu beachtende Punkte:**
1. **Workpiece-Dependencies**: FTS muss gedockt sein, Workpiece vorhanden
2. **Module-Status**: Module müssen verfügbar sein
3. **Timing**: Zwischen Commands Pausen einhalten
4. **Error-Handling**: Workflow-Status bei Fehlern

---

## 📝 **Nächste Schritte**

### **Sofort:**
1. **WorkflowOrderManager** implementieren
2. **WorkflowTemplateManager** erstellen
3. **Dashboard-Integration** vorbereiten

### **Diese Woche:**
1. **Vollständige Implementierung** abschließen
2. **Systematisches Testing** durchführen
3. **Dokumentation** aktualisieren

### **Nächste Woche:**
1. **Erweiterte Features** (Monitoring, Analytics)
2. **Performance-Optimierung**
3. **Integration** mit anderen Systemen

---

**Status**: 🚨 **KRITISCH** - ORDER-ID Management ist essentiell für funktionierende Workflows
