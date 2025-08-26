# TXT Controller Template Analysis Report
Generated: 2025-08-26 16:35:26

## 📊 Summary
- **Total Topics Analyzed:** 13
- **Active Topics:** 4
- **Total Messages:** 850

## 📥 Function Input Topics (f/i)
### /j1/txt/1/f/i/stock
- **Messages:** 237
- **Sessions:** 34
- **Template:** ```json
{
  "ts": "<ts>",
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
- **Variable Fields:** ts

### /j1/txt/1/f/i/order
- **Messages:** 558
- **Sessions:** 34
- **Template:** ```json
{
  "ts": "<ts>",
  "state": "<status>"
}
```
- **Variable Fields:** ts, type, state

### /j1/txt/1/f/i/status
- **Messages:** 0
- **Sessions:** 0

### /j1/txt/1/f/i/error
- **Messages:** 0
- **Sessions:** 0

### /j1/txt/1/f/i/config/hbw
- **Messages:** 40
- **Sessions:** 34
- **Template:** ```json
{
  "ts": "<ts>",
  "warehouses": [
    "SVR3QA0022"
  ]
}
```
- **Variable Fields:** ts

### /j1/txt/1/f/i/config/dps
- **Messages:** 0
- **Sessions:** 0

### /j1/txt/1/f/i/config/aiqs
- **Messages:** 0
- **Sessions:** 0

### /j1/txt/1/f/i/config/mill
- **Messages:** 0
- **Sessions:** 0

### /j1/txt/1/f/i/config/drill
- **Messages:** 0
- **Sessions:** 0

## 📤 Function Output Topics (f/o)
### /j1/txt/1/f/o/order
- **Messages:** 15
- **Sessions:** 9
- **Template:** ```json
{
  "type": "<workpieceType>",
  "ts": "<ts>"
}
```
- **Variable Fields:** type, ts

### /j1/txt/1/f/o/stock
- **Messages:** 0
- **Sessions:** 0

### /j1/txt/1/f/o/status
- **Messages:** 0
- **Sessions:** 0

### /j1/txt/1/f/o/error
- **Messages:** 0
- **Sessions:** 0
