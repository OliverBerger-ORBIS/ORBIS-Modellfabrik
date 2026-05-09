# Edge Persistence Stack - Architekturueberblick (Mermaid)

Diese Seite gibt einen kompakten Ueberblick ueber den neuen OSF Edge Persistence Stack aus [DR-28](../03-decision-records/28-edge-persistence-stack-and-metrics-model.md).

---

## 1) Deployment-Topologie (Modi + Zielplattformen)

```mermaid
flowchart LR
  subgraph APS["APS / RPi (operativ)"]
    CCU["CCU / Steuerung"]
    NR["Node-RED"]
    MB["Mosquitto Broker :1883"]
  end

  subgraph LOCAL["local-dev (MacBook)"]
    LB["Local Mosquitto\n:1883 + :9001"]
    SM["Session Manager\nReplay Station"]
    EP_REPLAY["Edge Persistence Stack\n(REPLAY mode)\nMQTT_HOST=host.docker.internal"]
  end

  subgraph DEPLOY["Deploy targets"]
    EP_LIVE["Edge Persistence Stack\n(LIVE mode)\nMQTT_HOST=192.168.0.100"]
    EP_RPI["rpi-pilot (optional)"]
    EP_EDGE["edge-prod (Zielzustand)\nDSP-Edge-Knoten"]
  end

  CCU --> MB
  NR --> MB

  MB --> EP_LIVE
  MB --> EP_RPI
  MB --> EP_EDGE

  SM -->|Replay publish| LB
  LB --> EP_REPLAY
```

Hinweis:
- Default-Profil ist **LIVE** (`env.live`): Persistence-Service liest vom APS-Broker.
- Test-Profil ist **REPLAY** (`env.replay`): Replay-Station publisht auf lokalen Broker; Persistence-Service liest lokal.
- Zielzustand bleibt **edge-prod**.

---

## 2) Datenfluss (Live und Replay)

```mermaid
sequenceDiagram
  participant APS as APS Topics (ccu/module/fts/txt)
  participant R as Replay Station (session_manager)
  participant MQTT_APS as APS Broker :1883
  participant MQTT_LOCAL as Local Broker :1883/:9001
  participant PS as Persistence Service (read-only, mode-aware)
  participant DB as Postgres + Timescale
  participant G as Grafana

  rect rgb(235, 248, 255)
  note over APS,MQTT_APS: LIVE mode (default / env.live)
  APS->>MQTT_APS: publish (ccu/*, module/*, fts/*, /j1/txt/*)
  PS->>MQTT_APS: subscribe only (no command publish)
  MQTT_APS-->>PS: incoming MQTT messages
  end

  rect rgb(240, 255, 240)
  note over R,MQTT_LOCAL: REPLAY mode (tests / env.replay)
  R->>MQTT_LOCAL: publish replay messages from session logs
  PS->>MQTT_LOCAL: subscribe only (no command publish)
  MQTT_LOCAL-->>PS: replay MQTT messages
  end

  PS->>PS: parse + normalize + dedup + reason logic
  PS->>DB: upsert/insert\n(shopfloor_event, production_*, workpiece,\nsensor_snapshot, mqtt_raw_message)
  G->>DB: SQL queries
  DB-->>G: time series + relational context
```

Kernprinzipien:
- Persistence Service ist **read-only** auf MQTT.
- Moduswahl erfolgt ueber Profil (`env.live` vs `env.replay`) und damit ueber `MQTT_HOST`.
- Kamera-Topic (`/j1/txt/1/i/cam`) wird standardmaessig nicht in Kernpersistenz uebernommen.
- Sensorik nutzt ein generisches Metrikmodell (`sensor_snapshot`).

---

## 3) Logisches Datenmodell (vereinfacht)

```mermaid
erDiagram
  PRODUCTION_ORDER ||--o{ PRODUCTION_STEP : has
  PRODUCTION_ORDER ||--o{ SHOPFLOOR_EVENT : correlates
  WORKPIECE ||--o{ SHOPFLOOR_EVENT : appears_in
  WORKPIECE ||--o{ SENSOR_SNAPSHOT : context
  SHOPFLOOR_EVENT ||--o{ SENSOR_SNAPSHOT : related_event

  PRODUCTION_ORDER {
    string order_id PK
    string order_type
    string state
    datetime started_at
    datetime stopped_at
  }

  PRODUCTION_STEP {
    int id PK
    string dedup_key UK
    string order_id FK
    string step_type
    string module_type
    string state
    datetime started_at
    datetime stopped_at
  }

  WORKPIECE {
    string workpiece_id PK
    string type
    string current_state
    string last_location
    datetime first_seen_at
    datetime last_seen_at
  }

  SHOPFLOOR_EVENT {
    int id PK
    datetime ts
    string dedup_key UK
    string topic
    string source
    string order_id
    string workpiece_id
    json payload_json
  }

  SENSOR_SNAPSHOT {
    int id PK
    datetime ts
    string source
    string station_id
    string sensor_type
    string metric_name
    float value_numeric
    string value_text
    string reason
    string order_id
    string workpiece_id
    json payload_json
  }
```

---

## 4) Topic-Familien im Stack

- Process/Shopfloor:
  - `ccu/order/active`, `ccu/order/completed`
  - `ccu/state/*`, `ccu/pairing/state`
  - `module/v1/ff/+/state|connection`
  - `fts/v1/ff/+/state|connection`
- Sensorik:
  - `/j1/txt/1/i/bme680`, `/j1/txt/1/i/ldr`
  - `osf/arduino/<sensorType>/<deviceId>/<action>` (DR-18 kompatibel)
- Ausschluss (default):
  - `/j1/txt/1/i/cam`
