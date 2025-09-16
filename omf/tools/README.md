# OMF Tools Documentation

## Overview

Das `tools` Verzeichnis enthält alle Werkzeuge für die OMF Dashboard-Funktionalität, einschließlich Message-Generierung, Template-Management und MQTT-Integration.

## Components

### TopicMappingManager

**Datei:** `topic_mapping_manager.py`

Verwaltet das Mapping zwischen MQTT-Topics und Message-Templates für semantische Nachrichten.

#### Features:
- **Topic-Template Mapping:** Verknüpft MQTT-Topics mit entsprechenden Templates
- **Kategorisierung:** Gruppiert Topics nach Funktionsbereichen (CCU, Module, TXT, Node-RED)
- **Variable Auflösung:** Löst `{module_id}` in Topic-Patterns auf
- **YAML-basiert:** Konfiguration über `topic_message_mapping.yml`

#### Usage:
```python
from topic_mapping_manager import get_omf_topic_mapping_manager

manager = get_omf_topic_mapping_manager()
topics = manager.get_available_topics()
template = manager.get_template_for_topic("module/v1/ff/{module_id}/order")
```

#### Key Methods:
- `get_available_topics()`: Alle verfügbaren Topics
- `get_template_for_topic(topic)`: Template für Topic finden
- `resolve_topic_variables(topic_pattern, **variables)`: Variable auflösen
- `get_topic_categories()`: Alle Topic-Kategorien

### WorkflowOrderManager

**Datei:** `workflow_order_manager.py`

Verwaltet `orderId` und `orderUpdateId` für sequentielle Modul-Befehle.

#### Features:
- **Order Tracking:** Verwaltet aktive Workflows pro Modul
- **Sequential Updates:** Inkrementiert `orderUpdateId` (1, 2, 3...)
- **Workflow History:** Speichert abgeschlossene Workflows
- **Singleton Pattern:** Globale Workflow-Verwaltung

#### Usage:
```python
from workflow_order_manager import get_workflow_order_manager

manager = get_workflow_order_manager()
order_id = manager.start_workflow("MILL", ["PICK", "PROCESS", "DROP"])
update_id = manager.get_next_order_update_id(order_id)
```

#### Key Methods:
- `start_workflow(module, commands)`: Neuen Workflow starten
- `get_next_order_update_id(order_id)`: Nächste Update-ID
- `execute_command(order_id, command)`: Befehl ausführen
- `get_active_workflows()`: Aktive Workflows abrufen

### MessageGenerator

**Datei:** `message_generator.py`

Generiert MQTT-Nachrichten basierend auf semantischen Template-Definitionen.

#### Features:
- **Template-basierte Generierung:** Verwendet semantische Templates
- **Topic-spezifische Parameter:** Automatische Parameter-Anpassung
- **Workflow-Integration:** Unterstützt `WorkflowOrderManager`
- **Fallback-Mechanismen:** Robuste Fehlerbehandlung

#### Usage:
```python
from message_generator import get_omf_message_generator

generator = get_omf_message_generator()
message = generator.generate_module_sequence_message("MILL", "PICK", 1, order_id)
```

#### Key Methods:
- `generate_factory_reset_message(with_storage, clear_storage)`: Factory Reset
- `generate_module_sequence_message(module, step, step_number, order_id)`: Modul-Befehle
- `generate_ccu_order_request_message(color, order_type, workpiece_id)`: Bestellungen
- `generate_message(template_name, **params)`: Generische Nachrichten

## Integration

### Dashboard Integration

Alle Tools sind in das OMF Dashboard integriert:

1. **TopicMappingManager:** Wird im Message-Generator für Topic-Auswahl verwendet
2. **WorkflowOrderManager:** Verwaltet sequentielle Modul-Befehle
3. **MessageGenerator:** Generiert alle MQTT-Nachrichten im Dashboard

### Configuration

#### Topic-Message Mapping (`topic_message_mapping.yml`):
```yaml
topic_mappings:
  "module/v1/ff/{module_id}/order":
    template: "module/order"
    direction: "outbound"
    description: "Modul-Befehle senden"
    variable_fields:
      module_id: "<module_serial_number>"
```

#### Template Categories:
- **CCU:** Zentrale Steuerung und Status
- **Module:** Modul-spezifische Befehle und Status
- **TXT:** Fischertechnik TXT-Integration
- **Node-RED:** Node-RED Dashboard-Integration

## Testing

### Unit Tests

Alle Tools haben umfassende Unit Tests:

- `tests_orbis/test_topic_mapping_manager.py`: TopicMappingManager Tests
- `tests_orbis/test_message_generator.py`: MessageGenerator Tests

### Test Coverage:
- ✅ Template-Mapping-Funktionalität
- ✅ Variable-Auflösung
- ✅ Workflow-Management
- ✅ Message-Generierung
- ✅ Fehlerbehandlung
- ✅ Edge Cases

## Error Handling

Alle Tools implementieren robuste Fehlerbehandlung:

- **Graceful Degradation:** Fallback bei fehlenden Komponenten
- **Exception Handling:** Try-except Blöcke mit spezifischen Exceptions
- **User Feedback:** Benutzerfreundliche Fehlermeldungen
- **Logging:** Detaillierte Logs für Debugging

## Future Enhancements

### Geplante Erweiterungen:
- **Dynamic Templates:** Runtime Template-Generierung
- **Advanced Workflows:** Komplexe Workflow-Definitionen
- **Template Validation:** Automatische Template-Validierung
- **Performance Optimization:** Caching für bessere Performance
