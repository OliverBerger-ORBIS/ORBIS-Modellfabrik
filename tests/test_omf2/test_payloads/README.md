# Test Payloads

## 📋 **Übersicht**

Diese Test-Payloads basieren auf echten Daten aus `data/aps-data/` aber sind für Tests optimiert:

### 🎯 **Verfügbare Test-Payloads:**

1. **`module_state_payload.json`** - Module State mit Loads und ActionState
2. **`ccu_order_request_payload.json`** - CCU Order Request mit WorkpieceId
3. **`txt_sensor_payload.json`** - TXT BME680 Sensor-Daten
4. **`module_connection_payload.json`** - Module Connection Status
5. **`ccu_global_payload.json`** - CCU Global System Status

### 🔧 **Verwendung in Tests:**

```python
import json
from pathlib import Path

# Test-Payload laden
payload_path = Path("tests/test_omf2/test_payloads/module_state_payload.json")
with open(payload_path, 'r') as f:
    test_data = json.load(f)

topic = test_data["topic"]
payload = test_data["payload"]

# Schema-Validation testen
registry_manager = get_registry_manager()
is_valid = registry_manager.validate_topic_payload(topic, payload)
```

### 📊 **Payload-Typen:**

- **Module Topics:** State, Connection, Order, Factsheet
- **CCU Topics:** Global, Order Request/Response, State
- **TXT Topics:** Sensor-Daten (BME680, CAM, LDR)
- **FTS Topics:** Connection, State, Order
- **NodeRed Topics:** Status, Connection

### 🎯 **Test-Integration:**

Diese Payloads können in folgenden Tests verwendet werden:
- Schema-Validation Tests
- Payload-Structure Tests  
- Topic-Mapping Tests
- Registry-Integration Tests
