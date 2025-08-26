# TXT Controller Template Analysis Report
Generated: 2025-08-26 17:26:29

## 📊 Summary
- **Total Topics Analyzed:** 13
- **Active Topics:** 4
- **Total Messages:** 1062

## 📥 Function Input Topics (f/i)
### /j1/txt/1/f/i/stock
- **Messages:** 295
- **Sessions:** 35
- **Template:** ```json
{
  "ts": "<timestamp>",
  "stockItems": "<stockItems>"
}
```
- **Variable Fields:** ts

### /j1/txt/1/f/i/order
- **Messages:** 706
- **Sessions:** 35
- **Template:** ```json
{
  "ts": "<timestamp>",
  "state": "<status: IN_PROCESS, WAITING_FOR_ORDER>"
}
```
- **Variable Fields:** state, ts, type

### /j1/txt/1/f/i/status
- **Messages:** 0
- **Sessions:** 0

### /j1/txt/1/f/i/error
- **Messages:** 0
- **Sessions:** 0

### /j1/txt/1/f/i/config/hbw
- **Messages:** 41
- **Sessions:** 35
- **Template:** ```json
{
  "ts": "<timestamp>",
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
- **Messages:** 20
- **Sessions:** 10
- **Template:** ```json
{
  "type": "<workpieceType: BLUE, RED, WHITE>",
  "ts": "<timestamp>"
}
```
- **Variable Fields:** ts, type

### /j1/txt/1/f/o/stock
- **Messages:** 0
- **Sessions:** 0

### /j1/txt/1/f/o/status
- **Messages:** 0
- **Sessions:** 0

### /j1/txt/1/f/o/error
- **Messages:** 0
- **Sessions:** 0
