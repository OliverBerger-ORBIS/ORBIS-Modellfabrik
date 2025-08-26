# TXT Controller Template Analysis Report
Generated: 2025-08-26 16:36:12

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
  "ts": "<timestamp>",
  "stockItems": "<stockItems>"
}
```
- **Variable Fields:** ts

### /j1/txt/1/f/i/order
- **Messages:** 558
- **Sessions:** 34
- **Template:** ```json
{
  "ts": "<timestamp>",
  "state": "<status>"
}
```
- **Variable Fields:** type, state, ts

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
- **Messages:** 15
- **Sessions:** 9
- **Template:** ```json
{
  "type": "<workpieceType>",
  "ts": "<timestamp>"
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
