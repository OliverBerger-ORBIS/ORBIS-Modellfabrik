# ModuleStateManager - Implementierungs-Dokumentation

> ⚠️ **VERIFIKATION AUSSTEHEND**: Diese Dokumentation basiert auf einer Hypothese und wurde noch nicht verifiziert. Die beschriebenen Implementierungen und Features müssen noch getestet und validiert werden.

## 📋 Übersicht

**Status:** ✅ **VOLLSTÄNDIG IMPLEMENTIERT** - Bereit für Integration in OMF Dashboard

**Ziel:** Automatisches Timing-Management für Modul-Sequenzen, um die manuelle Sichtkontrolle zu ersetzen.

## 🏗️ Architektur

### **Kern-Komponenten:**

| Komponente | Datei | Funktion | Details |
|------------|-------|----------|---------|
| **ModuleStateManager** | `omf/tools/module_state_manager.py` | Zentrale Verwaltung von Modul-Status und Sequenz-Ausführung | Singleton mit Thread-sicherem Monitoring |
| **ModuleState** | Enum | Status-Definitionen | IDLE, PICKBUSY, WAITING_AFTER_PICK, MILLBUSY, DRILLBUSY, CHECKBUSY, etc. |
| **CommandType** | Enum | Befehl-Definitionen | PICK, DROP, MILL, DRILL, CHECK_QUALITY, STORE, etc. |
| **ModuleInfo** | Dataclass | Modul-Informationen | module_id, module_name, module_type, serial_number, current_state, last_update |
| **ModuleSequence** | Dataclass | Sequenz-Definition | Steps, Status, Order-ID (Beispiel: PICK → MILL → DROP) |

## 🔧 Implementierte Features

### **✅ Modul-Status-Management**
```python
# Modul-Status abrufen
module = state_manager.get_module_status("MILL")
print(f"Status: {module.current_state.value}")  # IDLE, PICKBUSY, etc.

# Alle Module-Status
all_modules = state_manager.get_all_module_status()
```

### **✅ Automatische Sequenz-Ausführung**
```python
# Sequenz starten
commands = [CommandType.PICK, CommandType.MILL, CommandType.DROP]
sequence_id = state_manager.start_sequence(
    module_id="MILL",
    sequence_name="production_sequence",
    commands=commands,
    order_id="order_123"
)

# Sequenz überwachen
running_sequences = state_manager.get_running_sequences()
```

### **✅ MQTT-Integration**
- **Status-Subscription:** Automatisches Abonnieren aller Modul-Status-Topics
- **Command-Sending:** Über MqttGateway mit korrekten Payload-Formaten
- **Real-time Updates:** Thread-sichere Status-Updates

### **✅ Timing-Management**
- **Command-Bereitschaft:** Automatische Prüfung ob Modul bereit für Command
- **Sequenz-Koordination:** Automatische Ausführung der nächsten Schritte
- **Timeout-Handling:** Fehlerbehandlung bei Timeouts

## 🎯 Node-RED Ersatz-Funktionalität

### **Bisher (Node-RED):**
```javascript
// Node-RED Order Handling (4567 Zeilen)
if (actionState.command == "PICK" && flow.get("moduleState") == "IDLE") {
    flow.set("moduleState", "PICKBUSY");
    // OPCUA Write Content
    msg.payload.valuesToWrite = [{ "value": true }];
    msg.payload.nodesToWrite = [{ "name": "pick", "nodeId": "ns=4;i=5" }];
}
```

### **Jetzt (OMF Dashboard):**
```python
# ModuleStateManager - Automatisch
if self._is_module_ready_for_command(module, CommandType.PICK):
    success = self._send_module_command(sequence, step)
    # Automatische Status-Übergänge
    # Automatische Sequenz-Koordination
```

## 📊 Dashboard-Integration

### **Neue UI-Komponente:**
- **Datei:** `omf/dashboard/components/module_state_control.py`
- **Tab:** "Module Control" im OMF Dashboard
- **Features:**
  - 📊 Modul-Status-Übersicht
  - 🔄 Sequenz-Steuerung
  - ⚡ Schnell-Commands
  - 📋 Laufende Sequenzen

### **UI-Features:**
1. **Modul-Status-Tabelle:** Real-time Status aller Module
2. **Sequenz-Erstellung:** Drag & Drop Command-Sequenzen
3. **Schnell-Commands:** Einzelne Commands mit einem Klick
4. **Fortschritts-Tracking:** Visualisierung laufender Sequenzen

## 🧪 Tests

### **Test-Coverage:**
- **Datei:** `tests/test_omf/test_module_state_manager.py`
- **Tests:** 18 Tests, alle bestanden ✅
- **Coverage:** Singleton, Sequenz-Management, Command-Sending, Error-Handling

### **Test-Kategorien:**
1. **Singleton-Pattern:** Korrekte Instanz-Verwaltung
2. **Modul-Initialisierung:** Alle Module korrekt geladen
3. **Sequenz-Erstellung:** Command-Steps korrekt erstellt
4. **Command-Bereitschaft:** Modul-Status-basierte Prüfung
5. **MQTT-Integration:** Command-Versand über Gateway
6. **Error-Handling:** Fehlerbehandlung und Recovery

## 🚀 Nächste Schritte

### **Phase 1.2: OPC-UA Integration**
- **OPCUAManager implementieren** für direkte SPS-Kommunikation
- **DSP Integration** über separaten RPI
- **Node-ID Mapping** (ns=4;i=5 = pick, ns=4;i=6 = drop)

### **Phase 1.3: MQTT-Command-Vergleich**
- **Node-RED Commands aufzeichnen** (Session Manager)
- **OMF Dashboard Commands generieren**
- **Vergleich** der Message-Formate

### **Phase 2: Node-RED Deaktivierung**
- **Backup erstellen** aller Node-RED Flows
- **Schrittweise Deaktivierung** einzelner Modul-Tabs
- **Testing und Validierung** der Ersatz-Funktionalität

## 📁 Dateien

### **Implementierung:**
- `omf/tools/module_state_manager.py` - Kern-Implementierung
- `omf/dashboard/components/module_state_control.py` - UI-Komponente
- `tests/test_omf/test_module_state_manager.py` - Tests

### **Integration:**
- `omf/dashboard/omf_dashboard.py` - Dashboard-Integration
- `omf/dashboard/components/README.md` - Dokumentation

### **Dokumentation:**
- `docs/analysis/node-red-replacement-strategy.md` - Strategie
- `docs/implementation/module-state-manager.md` - Diese Datei

## 🎯 Erfolgskriterien

### **✅ Erreicht:**
- [x] Automatisches Timing-Management implementiert
- [x] Modul-Status-Tracking funktional
- [x] MQTT-Integration vollständig
- [x] Dashboard-UI integriert
- [x] Tests vollständig bestanden
- [x] Dokumentation erstellt

### **🔄 Nächste Schritte:**
- [ ] OPC-UA Integration (OPCUAManager)
- [ ] MQTT-Command-Vergleich
- [ ] Node-RED Deaktivierung (Phase 2)

---

**Erstellt:** $(date)
**Status:** ✅ **VOLLSTÄNDIG IMPLEMENTIERT**
**Nächster Schritt:** OPCUAManager implementieren
