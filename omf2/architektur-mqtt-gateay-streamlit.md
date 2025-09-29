# Architekturvorschlag: Gekapseltes MQTT, MessageTemplates & Gateway für Streamlit-Apps

**Ziel:**  
Weggekapselte, robuste Architektur für MQTT-Kommunikation, Message-Templates und UI-Refresh in einer Streamlit-App, sodass UI- und Business-Logik möglichst einfach bleiben und typische Fehlerquellen (Threading, Race-Conditions, Deadlocks, inkonsistenter State) vermieden werden.

---

## 1. Komponenten-Überblick

- **MessageTemplates**  
  Singleton-Utility zum Laden, Rendern und Validieren von Nachrichten aus Registry-Templates.
- **MQTTClient (pro Domäne)**  
  Thread-sicherer Singleton, kapselt alle Verbindungs- und Kommunikationsdetails.
- **Gateway (pro Domäne)**  
  Fassade für Business-Operationen, nutzt MessageTemplates und MQTTClient, stellt Methoden für die UI bereit.
- **UI (Streamlit)**  
  Ruft ausschließlich Gateway-Methoden auf; Interaktion mit State/Refresh über `st.session_state`.

---

## 2. Klassendiagramm (Konzept)

```plaintext
Streamlit-UI
    │
    ▼
Gateway (z.B. CCUGateway)
    ├── nutzt → MessageTemplates (Singleton)
    └── nutzt → MQTTClient (Singleton, thread-safe)
```

---

## 3. MessageTemplates-Utility (zentral, Singleton)

- Lädt Topics, Templates und Mappings aus Registry.
- Bietet Methoden zum Rendern, Validieren, (optional Loggen) von Nachrichten.
- Keine direkte MQTT-Kommunikation!

```python
# omf2/common/message_templates.py

import logging
import yaml
import os

class MessageTemplates:
    _instance = None

    def __new__(cls, registry_path="registry/model/v2/"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_registry(registry_path)
        return cls._instance

    def _load_registry(self, registry_path):
        with open(os.path.join(registry_path, "topics.yml")) as f:
            self.topics = yaml.safe_load(f)
        with open(os.path.join(registry_path, "templates.yml")) as f:
            self.templates = yaml.safe_load(f)
        with open(os.path.join(registry_path, "topics_templates_mapping.yml")) as f:
            self.mapping = yaml.safe_load(f)

    def render_message(self, topic, params):
        template_key = self.mapping.get(topic)
        template = self.templates.get(template_key)
        if not template:
            logging.warning(f"Kein Template für Topic {topic}")
            return None
        try:
            return template.format(**params)
        except Exception as e:
            logging.error(f"Template-Fehler für {topic}: {e}")
            return None

    def validate_message(self, topic, msg):
        # Optional: Schema-Validierung
        return True

    def log_message(self, topic, message, direction):
        logging.info(f"{direction} message on topic {topic}: {message}")
```

---

## 4. Thread-sicherer MQTT-Client (Singleton)

- Eine Instanz pro Domäne.
- Alle Methoden (publish, subscribe, etc.) arbeiten thread-safe via Lock.
- Empfangene Nachrichten werden in eine threadsichere Queue geschrieben (z.B. für Streamlit-UI).

```python
# omf2/ccu/ccu_mqtt_client.py

import threading
import paho.mqtt.client as mqtt
from queue import Queue

class CCUMQTTClient:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._client = mqtt.Client()
                cls._instance._client_lock = threading.Lock()
                cls._instance._msg_queue = Queue()
                # ... weitere Initialisierung, z.B. Connect, Callback-Setup ...
            return cls._instance

    def publish(self, topic, msg):
        with self._client_lock:
            self._client.publish(topic, msg)

    def subscribe(self, topic):
        with self._client_lock:
            self._client.subscribe(topic)

    def on_message(self, client, userdata, message):
        # Callback von paho-mqtt
        self._msg_queue.put((message.topic, message.payload))

    def get_next_message(self):
        try:
            return self._msg_queue.get_nowait()
        except Exception:
            return None
```

---

## 5. Gateway (Fassade, pro Domäne)

- Kapselt Message-Erstellung, Validierung, Logging und MQTT-Kommunikation.
- Bietet Methoden wie `send_order(params)` für die UI.
- Die UI sieht niemals Templates, MQTT, Threads oder Queue!

```python
# omf2/ccu/ccu_gateway.py

from omf2.common.message_templates import MessageTemplates
from omf2.ccu.ccu_mqtt_client import CCUMQTTClient

class CCUGateway:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CCUGateway()
        return cls._instance

    def __init__(self):
        self.mqtt_client = CCUMQTTClient()
        self.templates = MessageTemplates()

    def send_order(self, params):
        topic = "ccu/orders/send"
        msg = self.templates.render_message(topic, params)
        if msg is None:
            return False, "Nachrichtenerstellung fehlgeschlagen"
        if not self.templates.validate_message(topic, msg):
            return False, "Validierung fehlgeschlagen"
        self.templates.log_message(topic, msg, "SEND")
        self.mqtt_client.publish(topic, msg)
        return True, "Order gesendet"

    def get_last_incoming_message(self):
        return self.mqtt_client.get_next_message()
```

---

## 6. Streamlit-UI: Nur Gateway nutzen, State/Refresh per Session

```python
# Im Streamlit-Tab (z.B. ui/ccu/ccu_orders/ccu_orders_tab.py)
import streamlit as st
from omf2.ccu.ccu_gateway import CCUGateway

gateway = CCUGateway.get_instance()

if "order_refresh" not in st.session_state:
    st.session_state["order_refresh"] = 0

if st.button("Order senden"):
    ok, result = gateway.send_order({"order_id": 123, "part": "foo"})
    if ok:
        st.session_state["order_refresh"] += 1
        st.success(result)
    else:
        st.error(result)

# Polling für neue Nachrichten (optional)
msg = gateway.get_last_incoming_message()
if msg:
    topic, payload = msg
    st.info(f"Neue Nachricht: {topic}: {payload}")
```

---

## 7. UI-Refresh-Pattern (Streamlit)

- Nach Aktionen: Zähler in `st.session_state` erhöhen, z.B. `order_refresh`.
- UI-Komponenten können an diesen Zähler gekoppelt werden (z.B. mit `key=f"orders_{st.session_state['order_refresh']}"`).
- Eingehende Nachrichten werden aus Queue gelesen und angezeigt, kein expliziter Thread in Streamlit nötig.

---

## 8. Vorteile & Best Practices

- **UI bleibt einfach:** Keine Threading-Probleme, keine MQTT-Details, kein Deadlock-Risiko.
- **Gateways sind "schlanke Fassade":** Testbar, erweiterbar, keine Redundanz.
- **MQTT und Templates sind zentral und thread-safe gekapselt.**
- **UI-Refresh wird zentral gesteuert, keine Race-Conditions mit Session-State.**
- **Das Pattern ist in allen Domänen wiederverwendbar und hält die Komplexität im Griff.**

---

## 9. Erweiterungsmöglichkeiten

- Validierung per JSON Schema (in validate_message).
- Abstrakte Basisklassen für Gateway/MQTTClient, falls wirklich notwendig.
- Weitere Methoden für Subscriptions, Message-Buffering, etc.

---

**Diskussionspunkte für den Coding Agent:**
- Welche Events sollen den UI-Refresh triggern?
- Sollen eingehende Nachrichten persistent in Session-State, DB oder nur temporär (Queue)?
- Wie werden Fehler/Erfolg zentral im UI gemeldet?
- Wie werden komplexe Payloads (z.B. JSON) gemappt/gerendert?

---

**Letzte Aktualisierung:** 2025-09-29