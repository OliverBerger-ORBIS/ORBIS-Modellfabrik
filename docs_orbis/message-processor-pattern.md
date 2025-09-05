# Message-Processor Pattern - Dashboard Architecture

## 🎯 **Übersicht**

Das **Message-Processor Pattern** ist eine zentrale Architektur-Komponente für die Verarbeitung von MQTT-Nachrichten im OMF Dashboard. Es löst die Probleme von MQTT-Loops und redundanter Nachrichten-Verarbeitung.

## 🚨 **Gelöste Probleme**

### **Problem 1: MQTT Subscribe-Loop**
- **Symptom**: `client.subscribe("#", qos=1)` wurde bei jedem `st.rerun()` aufgerufen
- **Ursache**: Keine Session-State-Verfolgung der Subscription-Status
- **Lösung**: Broker-spezifische Session-State-Flags

### **Problem 2: MQTT Processing-Loop**
- **Symptom**: Overview-Komponenten verarbeiteten alle Nachrichten bei jedem `st.rerun()`
- **Ursache**: Keine Verfolgung bereits verarbeiteter Nachrichten
- **Lösung**: `last_processed_count` pro Komponente

## 🏗️ **Architektur**

### **MessageProcessor Klasse**
```python
@dataclass
class MessageProcessor:
    component_name: str
    message_filter: Callable[[Dict], bool]
    processor_function: Callable[[List[Dict]], None]
    _last_processed_count: int = field(init=False, default=0)
```

### **Factory-Funktion**
```python
def get_message_processor(
    component_name: str,
    message_filter: Optional[Callable[[Dict], bool]] = None,
    processor_function: Optional[Callable[[List[Dict]], None]] = None
) -> MessageProcessor
```

## 📋 **Verwendung**

### **1. Einfache Topic-Filterung**
```python
from .message_processor import get_message_processor, create_topic_filter

# Message-Processor erstellen
processor = get_message_processor(
    component_name="overview_inventory",
    message_filter=create_topic_filter("module/v1/ff/SVR3QA0022/state"),
    processor_function=process_inventory_messages
)

# Nachrichten verarbeiten (nur neue)
messages = processor.process_messages(mqtt_client)
```

### **2. Mehrere Topics**
```python
processor = get_message_processor(
    component_name="overview_module_status",
    message_filter=create_topic_filter([
        "module/v1/ff/+/state",
        "module/v1/ff/+/connection", 
        "ccu/pairing/state"
    ]),
    processor_function=lambda msgs: _process_module_messages(msgs, store)
)
```

### **3. Regex-Filter**
```python
from .message_processor import create_regex_filter

processor = get_message_processor(
    component_name="custom_component",
    message_filter=create_regex_filter(r"module/v1/ff/.*/state"),
    processor_function=process_custom_messages
)
```

## 🔧 **Helper-Funktionen**

### **create_topic_filter**
```python
def create_topic_filter(topics: Union[str, List[str]]) -> Callable[[Dict], bool]:
    """Erstellt einen Filter für spezifische Topics"""
```

### **create_regex_filter**
```python
def create_regex_filter(pattern: str) -> Callable[[Dict], bool]:
    """Erstellt einen Regex-basierten Filter"""
```

## 📊 **Performance-Verbesserungen**

### **Vorher (ohne Pattern):**
- ❌ **15+ Zeilen Code** pro Komponente
- ❌ **Alle Nachrichten** werden bei jedem `st.rerun()` verarbeitet
- ❌ **Redundante Verarbeitung** bereits verarbeiteter Nachrichten
- ❌ **MQTT-Loops** durch wiederholte Subscriptions

### **Nachher (mit Pattern):**
- ✅ **3 Zeilen Code** pro Komponente
- ✅ **Nur neue Nachrichten** werden verarbeitet
- ✅ **Automatische Filterung** vor Verarbeitung
- ✅ **Keine MQTT-Loops** durch Session-State-Management

## 🎯 **Migrierte Komponenten**

### **✅ Abgeschlossen:**
1. **`overview_inventory.py`** - Lagerbestand
2. **`overview_customer_order.py`** - Kundenaufträge  
3. **`overview_purchase_order.py`** - Rohmaterial-Bestellungen
4. **`overview_module_status.py`** - Modul-Status

### **📈 Code-Reduktion:**
- **Vorher**: 15+ Zeilen pro Komponente
- **Nachher**: 3 Zeilen pro Komponente
- **Reduktion**: ~80% weniger Code

## 🚀 **Zukünftige Erweiterungen**

### **Neue Komponenten hinzufügen:**
```python
# 1. Message-Processor erstellen
processor = get_message_processor(
    component_name="new_component",
    message_filter=create_topic_filter("your/topic"),
    processor_function=your_processing_function
)

# 2. Nachrichten verarbeiten
messages = processor.process_messages(mqtt_client)
```

### **Erweiterte Filter:**
- **Payload-basierte Filter**: Nachrichten nach Inhalt filtern
- **Zeit-basierte Filter**: Nur Nachrichten aus bestimmten Zeiträumen
- **Kombinierte Filter**: Mehrere Filter-Kriterien kombinieren

## 🔍 **Debugging**

### **Session-State überprüfen:**
```python
# Alle Message-Processor anzeigen
for name, processor in _message_processors.items():
    st.write(f"{name}: {processor._last_processed_count} verarbeitet")
```

### **Nachrichten-Monitoring:**
```python
# Verarbeitete Nachrichten anzeigen
messages = processor.process_messages(mqtt_client)
st.write(f"Verarbeitet: {len(messages)} neue Nachrichten")
```

## 📝 **Best Practices**

1. **Komponenten-spezifische Namen**: Eindeutige `component_name` verwenden
2. **Spezifische Filter**: So spezifisch wie möglich filtern
3. **Fehlerbehandlung**: Try-catch in `processor_function` implementieren
4. **Session-State**: Nicht manuell manipulieren
5. **Testing**: Unit-Tests für `processor_function` schreiben

## ⚠️ **WICHTIGE REGEL: OrderManager Session-State**

### **❌ FALSCH:**
```python
# Jede Komponente erstellt ihre eigene OrderManager-Instanz
order_manager = OrderManager()  # FALSCH!
```

### **✅ RICHTIG:**
```python
# OrderManager aus Session-State holen oder erstellen
if "order_manager" not in st.session_state:
    st.session_state["order_manager"] = OrderManager()
order_manager = st.session_state["order_manager"]
```

### **Warum diese Regel wichtig ist:**
- **Datenkonsistenz**: Alle Komponenten teilen sich die gleichen Lagerbestandsdaten
- **Performance**: Keine redundanten OrderManager-Instanzen
- **Synchronisation**: Änderungen in einer Komponente sind in allen anderen sichtbar
- **Session-Persistenz**: Daten bleiben über `st.rerun()` erhalten

### **Betroffene Komponenten:**
- ✅ `overview_inventory.py`
- ✅ `overview_customer_order.py` 
- ✅ `overview_purchase_order.py`
- ✅ Alle zukünftigen OrderManager-basierten Komponenten

## 🎉 **Ergebnis**

Das Message-Processor Pattern bietet:
- ✅ **Skalierbare Architektur** für zukünftige Komponenten
- ✅ **Performance-Optimierung** durch nur neue Nachrichten-Verarbeitung
- ✅ **Code-Reduktion** von 80% pro Komponente
- ✅ **Keine MQTT-Loops** mehr
- ✅ **Konsistente Session-State** Verwaltung
- ✅ **Einfache Integration** neuer Komponenten

---

*Implementiert: Januar 2025*
*Status: Alle Overview-Komponenten migriert*
