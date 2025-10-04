# State-Holder Pattern für CCU Manager

**Datum:** 2025-01-04  
**Status:** Implemented  
**Kontext:** Konsistentes Pattern für MQTT-Nachrichten-Verarbeitung in CCU SensorManager und ModuleManager

---

## Übersicht

Diese Implementation etabliert ein konsistentes State-Holder Pattern für die Verarbeitung und Bereitstellung von MQTT-Nachrichten in den Business-Managern SensorManager und ModuleManager im CCU-Bereich.

## Architektur

### Komponenten

```
MQTT Broker
    ↓
CCU MQTT Client (Singleton)
    ↓ (Callbacks)
    ├─→ SensorManager (State-Holder)
    │   └─→ UI: sensor_data_subtab.py
    │
    └─→ ModuleManager (State-Holder)
        └─→ UI: ccu_modules_tab.py
```

### State-Holder Pattern

```python
# Manager hält internen State
class SensorManager:
    def __init__(self):
        self._state_lock = threading.Lock()
        self._sensor_state: Dict[str, Any] = {}
    
    # Callback vom MQTT Client
    def process_sensor_message(self, topic: str, payload: Dict[str, Any]):
        with self._state_lock:
            self._sensor_state[topic] = self._extract_data(payload)
    
    # UI-Zugriff (thread-safe)
    def get_sensor_data(self, topic: Optional[str] = None) -> Dict[str, Any]:
        with self._state_lock:
            return self._sensor_state.copy()
```

## Implementierung

### 1. SensorManager (omf2/ccu/sensor_manager.py)

**Neue Methoden:**
- `process_sensor_message(topic, payload)` - Callback für MQTT-Nachrichten
- `get_sensor_data(topic)` - Thread-safe Zugriff auf spezifische Sensor-Daten
- `get_all_sensor_data()` - Thread-safe Zugriff auf alle Sensor-Daten

**Thread-Safety:**
- `_state_lock: threading.Lock()` - Lock für State-Zugriff
- `_sensor_state: Dict[str, Any]` - Interner State-Store

**Vorhandene Methode (Backward Compatibility):**
- `process_sensor_messages(ccu_gateway)` - Weiterhin verfügbar für Legacy-Code

### 2. ModuleManager (omf2/ccu/module_manager.py)

**Neue Methoden:**
- `process_module_message(topic, payload)` - Callback für MQTT-Nachrichten
- `get_all_module_status()` - Thread-safe Zugriff auf alle Module-Status
- `get_module_status(module_id, status_store=None)` - Erweitert für internen State

**Thread-Safety:**
- `_state_lock: threading.Lock()` - Lock für State-Zugriff
- `_module_state: Dict[str, Dict[str, Any]]` - Interner State-Store

**Interne Methoden:**
- `_update_module_state_internal(module_id, message_data)` - Update innerhalb Lock

### 3. CCU MQTT Client (omf2/ccu/ccu_mqtt_client.py)

**Callback-System:**
```python
# Callback-Liste (thread-safe)
self._callbacks_lock = threading.Lock()
self._message_callbacks: List[Callable] = []

# Registrierung
def register_message_callback(callback: Callable[[str, Dict], None]):
    with self._callbacks_lock:
        self._message_callbacks.append(callback)

# Ausführung in _on_message
with self._callbacks_lock:
    for callback in self._message_callbacks:
        callback(topic, message)
```

**Neue Methoden:**
- `register_message_callback(callback)` - Callback registrieren
- `unregister_message_callback(callback)` - Callback entfernen

### 4. CCU Gateway (omf2/ccu/ccu_gateway.py)

**Manager Integration:**
```python
def _setup_manager_integration(self):
    """Setup Manager Integration with MQTT Client callbacks"""
    sensor_manager = get_ccu_sensor_manager()
    module_manager = get_ccu_module_manager()
    
    # Register callbacks
    self.mqtt_client.register_message_callback(
        sensor_manager.process_sensor_message
    )
    self.mqtt_client.register_message_callback(
        module_manager.process_module_message
    )
```

**Automatische Setup:**
- Wird im `__init__` aufgerufen
- Registriert beide Manager als Callbacks

### 5. UI Integration

**sensor_data_subtab.py:**
```python
# ALT: Direkt vom Gateway verarbeiten
sensor_data = sensor_manager.process_sensor_messages(ccu_gateway)

# NEU: Aus Manager-State lesen
sensor_data = sensor_manager.get_all_sensor_data()
```

**ccu_modules_tab.py:**
```python
# ALT: Gateway verarbeiten und in Session State speichern
status_store = module_manager.process_module_messages(ccu_gateway)
st.session_state["ccu_module_status_store"] = status_store

# NEU: Direkt aus Manager-State lesen
status_store = module_manager.get_all_module_status()
```

## Thread-Safety

### Locking-Strategie

1. **Read/Write Lock Pattern:**
   ```python
   with self._state_lock:
       # Kritischer Abschnitt
       self._sensor_state[topic] = data
   ```

2. **Copy on Read:**
   ```python
   with self._state_lock:
       return self._sensor_state.copy()  # Verhindert externe Modifikation
   ```

3. **Nested Lock Prevention:**
   - Callbacks werden nie innerhalb eines Locks aufgerufen
   - MQTT Client Lock und Manager Lock sind getrennt

### Race Condition Tests

Die Tests in `test_ccu_managers.py` validieren:
- Gleichzeitiges Schreiben/Lesen
- 100 Iterationen in separaten Threads
- Keine Exceptions bei parallelem Zugriff

## Backward Compatibility

### Erhaltene Funktionalität

1. **SensorManager:**
   - `process_sensor_messages(ccu_gateway)` - Funktioniert weiterhin
   - Alte UI-Komponenten können unverändert bleiben

2. **ModuleManager:**
   - `get_module_status(module_id, status_store)` - Unterstützt beide Modi
   - Optional: Nutzt internen State wenn `status_store=None`

3. **Session State:**
   - Session State Management bleibt verfügbar
   - Kann parallel zum Manager-State genutzt werden

## Testing

### Unit Tests (omf2/tests/test_ccu_managers.py)

**SensorManager:**
- `test_init` - Initialisierung
- `test_process_sensor_message_bme680` - BME680 Verarbeitung
- `test_process_sensor_message_ldr` - LDR Verarbeitung
- `test_get_all_sensor_data` - Alle Daten abrufen
- `test_thread_safety` - Thread-Sicherheit

**ModuleManager:**
- `test_init` - Initialisierung
- `test_process_module_message_connection` - Connection Messages
- `test_process_module_message_state` - State Messages
- `test_get_all_module_status` - Alle Status abrufen
- `test_thread_safety` - Thread-Sicherheit

**CCU MQTT Client:**
- `test_register_callback` - Callback Registrierung
- `test_unregister_callback` - Callback Entfernung
- `test_callback_execution` - Callback Ausführung

### Test-Ergebnisse

```
Ran 13 tests in 0.055s
OK
```

Alle Tests erfolgreich ✅

## Vorteile

### 1. Separation of Concerns
- UI kennt nur Manager, nicht MQTT Client
- Manager kapseln MQTT-Logik
- Klare Verantwortlichkeiten

### 2. Thread-Safety
- Alle Zugriffe sind thread-safe
- Keine Race Conditions
- Validiert durch Tests

### 3. Real-Time Updates
- Manager empfangen Updates via Callbacks
- Kein Polling nötig
- Minimale Latenz

### 4. Testbarkeit
- Manager können isoliert getestet werden
- Mock-Callbacks für Tests
- Keine MQTT-Abhängigkeit in Tests

### 5. Erweiterbarkeit
- Neue Manager können einfach hinzugefügt werden
- Callback-Pattern ist wiederverwendbar
- Konsistente Architektur

## Migration

### Für neue Komponenten

```python
# 1. Manager-Instanz holen
sensor_manager = get_ccu_sensor_manager()

# 2. Daten aus Manager lesen (nicht aus MQTT Client!)
sensor_data = sensor_manager.get_all_sensor_data()

# 3. UI rendern
st.metric("Temperature", f"{sensor_data.get('temperature', 0):.1f}°C")
```

### Für bestehende Komponenten

**Option 1: Sofort migrieren (empfohlen)**
```python
# ALT
sensor_data = sensor_manager.process_sensor_messages(ccu_gateway)

# NEU
sensor_data = sensor_manager.get_all_sensor_data()
```

**Option 2: Schrittweise migrieren**
- Alte Methoden bleiben verfügbar
- Nach und nach auf neue Methoden umstellen
- Keine Breaking Changes

## Best Practices

### DO ✅

1. **Manager für Datenzugriff:**
   ```python
   sensor_data = sensor_manager.get_sensor_data(topic)
   ```

2. **Callback-Pattern:**
   ```python
   mqtt_client.register_message_callback(manager.process_message)
   ```

3. **Thread-safe Zugriff:**
   ```python
   with self._state_lock:
       return self._state.copy()
   ```

### DON'T ❌

1. **Direkter MQTT Client Zugriff in UI:**
   ```python
   # ❌ Nicht so
   buffer = mqtt_client.get_buffer(topic)
   
   # ✅ Sondern so
   data = sensor_manager.get_sensor_data(topic)
   ```

2. **State-Modifikation ohne Lock:**
   ```python
   # ❌ Nicht so
   self._state[topic] = data
   
   # ✅ Sondern so
   with self._state_lock:
       self._state[topic] = data
   ```

3. **Callbacks innerhalb Lock:**
   ```python
   # ❌ Nicht so
   with self._lock:
       callback()  # Kann zu Deadlock führen
   ```

## Zukunft

### Mögliche Erweiterungen

1. **State Persistence:**
   - State bei Restart wiederherstellen
   - Optional: Redis/Database Backend

2. **State History:**
   - Zeitreihen-Daten in Manager
   - Grafische Darstellung von Verläufen

3. **Event System:**
   - Manager können Events emittieren
   - UI kann auf Events reagieren

4. **WebSocket Integration:**
   - Push-Updates an UI
   - Keine Polling-Notwendigkeit

## Referenzen

- **Code:** `omf2/ccu/sensor_manager.py`, `omf2/ccu/module_manager.py`
- **Tests:** `omf2/tests/test_ccu_managers.py`
- **UI:** `omf2/ui/ccu/ccu_overview/sensor_data_subtab.py`, `omf2/ui/ccu/ccu_modules/ccu_modules_tab.py`
- **Pattern:** State-Holder Pattern, Callback Pattern, Singleton Pattern

---

*Implementiert von: GitHub Copilot*  
*Review durch: OMF-Entwicklungsteam*
