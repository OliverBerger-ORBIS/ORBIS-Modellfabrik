# TXT Controller Template Analysis Report
Generated: 2025-08-27 10:18:42

## 📊 Summary
- **Total Topics Analyzed:** 13
- **Active Topics:** 4
- **Total Messages:** 1062

## 📥 Function Input Topics (f/i)
### /j1/txt/1/f/i/stock
- **Messages:** 295
- **Sessions:** 35
- **Description:** Verwenden für Status-Anzeige Lagerbestand. Nur was im Lager ist kann bestellt werden
- **Usage:** Fertigungsschritt-Tracking: Lagerbestand prüfen vor Auftragsstart
- **Critical for:** Fertigungsschritte, Auftragsvalidierung, Lagerstatus
- **Workflow step:** HBW PICK/DROP Status
- **Template Structure:**
```json
{
  "ts": "<timestamp>",
  "stockItems": [
    {
      "workpiece": {
        "id": "<nfcCode>",
        "type": "[RED, WHITE, BLUE]",
        "state": "[RAW]"
      },
      "location": "[A1, A2, A3, B1, B2, B3, C1, C2, C3]",
      "hbw": "<hbwId>"
    }
  ]
}
```
- **Example Messages:**
  **Example 1:**
  - Session: auftrag-rot_1
  - Timestamp: 2025-08-19T11:15:49.927909
  - Payload: ```json
{
  "ts": "2025-08-19T09:13:34.583Z",
  "stockItems": [
    {
      "workpiece": {
        "id": "",
        "type": "",
        "state": "RAW"
      },
      "location": "A3",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "",
        "type": "",
        "state": "RAW"
      },
      "location": "B3",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "",
        "type": "",
        "state": "RAW"
      },
      "location": "C3",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "040a8dca341291",
        "type": "RED",
        "state": "RAW"
      },
      "location": "A1",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "04798eca341290",
        "type": "WHITE",
        "state": "RAW"
      },
      "location": "B1",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "047389ca341291",
        "type": "BLUE",
        "state": "RAW"
      },
      "location": "C1",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "047f8cca341290",
        "type": "RED",
        "state": "RAW"
      },
      "location": "A2",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "04808dca341291",
        "type": "RED",
        "state": "RAW"
      },
      "location": "B2",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "04ab8bca341290",
        "type": "WHITE",
        "state": "RAW"
      },
      "location": "C2",
      "hbw": "SVR3QA0022"
    }
  ]
}
```
  **Example 2:**
  - Session: auftrag-rot_1
  - Timestamp: 2025-08-19T11:16:14.692854
  - Payload: ```json
{
  "ts": "2025-08-19T09:16:14.686Z",
  "stockItems": [
    {
      "workpiece": {
        "id": "",
        "type": "",
        "state": "RAW"
      },
      "location": "A3",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "",
        "type": "",
        "state": "RAW"
      },
      "location": "B3",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "",
        "type": "",
        "state": "RAW"
      },
      "location": "C3",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "040a8dca341291",
        "type": "RED",
        "state": "RESERVED"
      },
      "location": "A1",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "04798eca341290",
        "type": "WHITE",
        "state": "RAW"
      },
      "location": "B1",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "047389ca341291",
        "type": "BLUE",
        "state": "RAW"
      },
      "location": "C1",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "047f8cca341290",
        "type": "RED",
        "state": "RAW"
      },
      "location": "A2",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "04808dca341291",
        "type": "RED",
        "state": "RAW"
      },
      "location": "B2",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "04ab8bca341290",
        "type": "WHITE",
        "state": "RAW"
      },
      "location": "C2",
      "hbw": "SVR3QA0022"
    }
  ]
}
```
  **Example 3:**
  - Session: auftrag-rot_1
  - Timestamp: 2025-08-19T11:16:26.885435
  - Payload: ```json
{
  "ts": "2025-08-19T09:16:26.880Z",
  "stockItems": [
    {
      "workpiece": {
        "id": "",
        "type": "",
        "state": "RAW"
      },
      "location": "A3",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "",
        "type": "",
        "state": "RAW"
      },
      "location": "B3",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "",
        "type": "",
        "state": "RAW"
      },
      "location": "C3",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "040a8dca341291",
        "type": "RED",
        "state": "RESERVED"
      },
      "location": "A1",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "04798eca341290",
        "type": "WHITE",
        "state": "RAW"
      },
      "location": "B1",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "047389ca341291",
        "type": "BLUE",
        "state": "RAW"
      },
      "location": "C1",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "047f8cca341290",
        "type": "RED",
        "state": "RAW"
      },
      "location": "A2",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "04808dca341291",
        "type": "RED",
        "state": "RAW"
      },
      "location": "B2",
      "hbw": "SVR3QA0022"
    },
    {
      "workpiece": {
        "id": "04ab8bca341290",
        "type": "WHITE",
        "state": "RAW"
      },
      "location": "C2",
      "hbw": "SVR3QA0022"
    }
  ]
}
```

### /j1/txt/1/f/i/order
- **Messages:** 706
- **Sessions:** 35
- **Description:** Auftragsstatus und -informationen vom TXT Controller
- **Usage:** Fertigungsschritt-Tracking: Auftragsfortschritt verfolgen
- **Critical for:** Fertigungsschritte, Auftragsstatus, Workflow-Tracking
- **Workflow step:** Auftragsausführung
- **Enum Fields:**
  - `state`: IN_PROCESS, WAITING_FOR_ORDER
  - `type`: BLUE, RED, WHITE
- **Template Structure:**
```json
{
  "ts": "<timestamp>",
  "state": "[IN_PROCESS, WAITING_FOR_ORDER]"
}
```
- **Example Messages:**
  **Example 1:**
  - Session: auftrag-rot_1
  - Timestamp: 2025-08-19T11:15:49.928020
  - Payload: ```json
{
  "ts": "2025-08-19T09:13:09.366Z",
  "state": "WAITING_FOR_ORDER"
}
```
  **Example 2:**
  - Session: auftrag-rot_1
  - Timestamp: 2025-08-19T11:16:14.683397
  - Payload: ```json
{
  "ts": "2025-08-19T09:16:14.679Z",
  "type": "RED",
  "state": "IN_PROCESS"
}
```
  **Example 3:**
  - Session: auftrag-rot_1
  - Timestamp: 2025-08-19T11:16:26.714977
  - Payload: ```json
{
  "ts": "2025-08-19T09:16:26.708Z",
  "type": "RED",
  "state": "IN_PROCESS"
}
```

### /j1/txt/1/f/i/config/hbw
- **Messages:** 41
- **Sessions:** 35
- **Description:** Konfiguration der Hochregallager (HBW) Module
- **Usage:** System-Initialisierung und Modul-Status
- **Critical for:** System-Setup, Modul-Konfiguration
- **Workflow step:** System-Start
- **Enum Fields:**
  - `ts`: 2025-08-14T05:27:49.795Z, 2025-08-19T07:04:57.566Z, 2025-08-19T09:08:26.191Z, 2025-08-20T07:12:20.229Z, 2025-08-25T06:46:39.746Z, 2025-08-26T06:07:08.450Z, 2025-08-26T09:16:21.502Z
- **Template Structure:**
```json
{
  "ts": "<timestamp>",
  "warehouses": [
    "SVR3QA0022"
  ]
}
```
- **Example Messages:**
  **Example 1:**
  - Session: auftrag-rot_1
  - Timestamp: 2025-08-19T11:15:49.927802
  - Payload: ```json
{
  "ts": "2025-08-19T09:08:26.191Z",
  "warehouses": [
    "SVR3QA0022"
  ]
}
```
  **Example 2:**
  - Session: auftrag-B1B2B3
  - Timestamp: 2025-08-20T11:57:37.329609
  - Payload: ```json
{
  "ts": "2025-08-20T07:12:20.229Z",
  "warehouses": [
    "SVR3QA0022"
  ]
}
```
  **Example 3:**
  - Session: custom_20250825_093826
  - Timestamp: 2025-08-25T09:38:46.232364
  - Payload: ```json
{
  "ts": "2025-08-25T06:46:39.746Z",
  "warehouses": [
    "SVR3QA0022"
  ]
}
```

## 📤 Function Output Topics (f/o)
### /j1/txt/1/f/o/order
- **Messages:** 20
- **Sessions:** 10
- **Description:** Auftragsausgabe vom TXT Controller an andere Module
- **Usage:** Fertigungsschritt-Tracking: Auftragsweiterleitung an Module
- **Critical for:** Fertigungsschritte, Modul-Steuerung, Workflow-Orchestration
- **Workflow step:** Auftragsverteilung
- **Enum Fields:**
  - `type`: BLUE, RED, WHITE
- **Template Structure:**
```json
{
  "type": "[BLUE, RED, WHITE]",
  "ts": "<timestamp>"
}
```
- **Example Messages:**
  **Example 1:**
  - Session: auftrag-rot_1
  - Timestamp: 2025-08-19T11:16:14.525342
  - Payload: ```json
{
  "type": "RED",
  "ts": "2025-08-19T09:16:14.336Z"
}
```
  **Example 2:**
  - Session: auftrag-B1B2B3
  - Timestamp: 2025-08-20T11:57:51.325138
  - Payload: ```json
{
  "type": "BLUE",
  "ts": "2025-08-20T09:57:51.319Z"
}
```
  **Example 3:**
  - Session: auftrag-B1B2B3
  - Timestamp: 2025-08-20T11:57:56.414477
  - Payload: ```json
{
  "type": "BLUE",
  "ts": "2025-08-20T09:57:56.397Z"
}
```
