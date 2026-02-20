# Architektur: Mehrere MQTT-Clients für OSF-UI-Komponenten

## Motivation

Im Rahmen der Steuerung der APS-Fabrik mit der OSF-UI sollen verschiedene Systemrollen (Operator, Supervisor, Admin etc.) klar abgegrenzt Nachrichten senden und empfangen können.  
Um Wartbarkeit, Sicherheit und Erweiterbarkeit zu gewährleisten, favorisieren wir eine **Trennung pro Rolle**, d.h. für jede Rolle wird ein eigener MQTT-Client als Singleton implementiert.

**Vorteile dieses Ansatzes:**
- Klare funktionale Trennung nach Systemrolle
- Bessere Testbarkeit und Debugging
- Security/ACLs können rollenbasiert vergeben werden
- Leichtes Monitoring und Logging pro Komponente
- Entspricht Best Practices im IIoT- und Microservices-Umfeld

---

## Architekturüberblick

### Komponenten

- **Zentrale Registry (YAML-basiert)**:  
  Templates, Topics und Mappings werden im Projekt-Root unter `registry/model/v1/` als YAML gepflegt (z.B. `templates.yml`, `topics.yml`).
- **MQTT-Clients (Singleton, pro Rolle)**:  
  Für jede Rolle (z.B. Operator, Supervisor, Admin) existiert ein eigener MQTT-Client, der nur die für ihn relevanten Topics abonniert und publiziert.
- **Gateway pro Rolle**:  
  Jede Komponente (z.B. Operator-Gateway) nutzt ihren eigenen Client und die Registry für Message-Generierung und -Validierung.

---

## Registry-Beispiel (YAML)

```yaml
# registry/model/v1/templates.yml
status:
  type: status
  fields: [module, state]

command:
  type: command
  fields: [action, params]

audit:
  type: audit
  fields: [event, by]
```

```yaml
# registry/model/v1/topics.yml
operator_status: aps/operator/status
supervisor_command: aps/supervisor/command
admin_audit: aps/admin/audit
```

---

## Registry-Loader (Python)

```python
import yaml
from pathlib import Path

class Registry:
    def __init__(self, base_path):
        self.templates = self._load_yaml(Path(base_path) / "templates.yml")
        self.topics = self._load_yaml(Path(base_path) / "topics.yml")
    def _load_yaml(self, path):
        with open(path, "r") as f:
            return yaml.safe_load(f)
    def get_template(self, name):
        return self.templates.get(name)
    def get_topic(self, name):
        return self.topics.get(name)
```

---

## MQTT-Client (vereinfachtes Beispiel)

```python
class OmfMqttClient:
    def __init__(self, client_id, sub_topics, pub_topics):
        self.client_id = client_id
        self.sub_topics = sub_topics
        self.pub_topics = pub_topics
    def connect(self):
        print(f"[{self.client_id}] MQTT connected")
    def subscribe(self):
        for topic in self.sub_topics:
            print(f"[{self.client_id}] Subscribed to: {topic}")
    def publish(self, topic, payload):
        print(f"[{self.client_id}] Publishing to {topic}: {payload}")
```

---

## MQTT-Client Factory

```python
def create_mqtt_client(role, registry):
    if role == "operator":
        return OmfMqttClient(
            client_id="operator",
            sub_topics=[registry.get_topic("operator_status")],
            pub_topics=[registry.get_topic("operator_status")]
        )
    elif role == "supervisor":
        return OmfMqttClient(
            client_id="supervisor",
            sub_topics=[registry.get_topic("supervisor_command")],
            pub_topics=[registry.get_topic("supervisor_command")]
        )
    elif role == "admin":
        return OmfMqttClient(
            client_id="admin",
            sub_topics=[registry.get_topic("admin_audit")],
            pub_topics=[registry.get_topic("admin_audit")]
        )
    else:
        raise ValueError("Unknown role")
```

---

## Gateways pro Rolle

```python
class OperatorGateway:
    def __init__(self, mqtt_client, registry):
        self.client = mqtt_client
        self.registry = registry
    def send_status(self, data):
        template = self.registry.get_template("status")
        payload = {k: data.get(k) for k in template["fields"]}
        self.client.publish(self.registry.get_topic("operator_status"), payload)

class SupervisorGateway:
    def __init__(self, mqtt_client, registry):
        self.client = mqtt_client
        self.registry = registry
    def send_command(self, data):
        template = self.registry.get_template("command")
        payload = {k: data.get(k) for k in template["fields"]}
        self.client.publish(self.registry.get_topic("supervisor_command"), payload)

class AdminGateway:
    def __init__(self, mqtt_client, registry):
        self.client = mqtt_client
        self.registry = registry
    def audit(self, data):
        template = self.registry.get_template("audit")
        payload = {k: data.get(k) for k in template["fields"]}
        self.client.publish(self.registry.get_topic("admin_audit"), payload)
```

---

## Beispielhafte Nutzung

```python
from registry.model.v1.registry_loader import Registry
# aus omf/dashboard/tools importieren:
from omf.dashboard.tools.omf_mqtt_factory import create_mqtt_client
from omf.dashboard.tools.mqtt_gateway import OperatorGateway, SupervisorGateway, AdminGateway

# Registry laden
registry = Registry("registry/model/v1")

# Operator
operator_client = create_mqtt_client("operator", registry)
operator_gateway = OperatorGateway(operator_client, registry)
operator_client.connect()
operator_client.subscribe()
operator_gateway.send_status({"module": "Bohrstation", "state": "running"})

# Supervisor
supervisor_client = create_mqtt_client("supervisor", registry)
supervisor_gateway = SupervisorGateway(supervisor_client, registry)
supervisor_client.connect()
supervisor_client.subscribe()
supervisor_gateway.send_command({"action": "start", "params": {"module": "Frässtation"}})

# Admin
admin_client = create_mqtt_client("admin", registry)
admin_gateway = AdminGateway(admin_client, registry)
admin_client.connect()
admin_client.subscribe()
admin_gateway.audit({"event": "command_sent", "by": "operator"})
```

---

## Fazit

Mit dieser Struktur ist eine **klare Trennung der Verantwortlichkeiten** möglich, die Lösung bleibt flexibel und erweiterbar.  
Die Registry kann zentral gepflegt und von allen Rollen genutzt werden.  
Die MQTT-Clients und Gateways sind einfach testbar und können problemlos für neue Rollen oder Themen erweitert werden.

---

**Diskussionsgrundlage für das Team – Anpassungen und Erweiterungen sind jederzeit möglich!**