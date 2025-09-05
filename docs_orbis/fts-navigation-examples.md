# FTS Navigation Examples

## 🚛 **Funktionierende FTS-Navigation: DPS → HBW**

### **Topic:**
```
fts/v1/ff/5iO4/order
```

### **Payload:**
```json
{
  "timestamp": "2025-01-19T10:00:00.000Z",
  "orderId": "test-navigation-dps-to-hbw-wareneingang-001",
  "orderUpdateId": 0,
  "nodes": [
    {
      "id": "SVR4H73275",
      "linkedEdges": ["SVR4H73275-2"]
    },
    {
      "id": "2",
      "linkedEdges": ["SVR4H73275-2", "2-1"],
      "action": {
        "id": "pass-through-2-001",
        "type": "PASS"
      }
    },
    {
      "id": "1",
      "linkedEdges": ["2-1", "1-SVR3QA0022"],
      "action": {
        "id": "pass-through-1-001",
        "type": "PASS"
      }
    },
    {
      "id": "SVR3QA0022",
      "linkedEdges": ["1-SVR3QA0022"],
      "action": {
        "type": "DOCK",
        "id": "dock-at-hbw-wareneingang-001",
        "metadata": {
          "loadId": "04798eca341290",
          "loadType": "WHITE",
          "loadPosition": "1"
        }
      }
    }
  ],
  "edges": [
    {
      "id": "SVR4H73275-2",
      "length": 380,
      "linkedNodes": ["SVR4H73275", "2"]
    },
    {
      "id": "2-1",
      "length": 360,
      "linkedNodes": ["2", "1"]
    },
    {
      "id": "1-SVR3QA0022",
      "length": 380,
      "linkedNodes": ["1", "SVR3QA0022"]
    }
  ],
  "serialNumber": "5iO4"
}
```

## 🎯 **Route-Details:**
1. **Start:** SVR4H73275 (DPS)
2. **Knoten 2:** PASS (durchfahren)
3. **Knoten 1:** PASS (durchfahren)
4. **Ziel:** SVR3QA0022 (HBW)

## 📋 **Wichtige Erkenntnisse:**
- **FTS-Steuerung erfolgt über:** `fts/v1/ff/5iO4/order`
- **Beide Zwischenknoten sind PASS** (keine TURN-Befehle)
- **Route basiert auf:** Session "wareneingang-weiss" (Zeile 250)
- **Funktioniert zuverlässig** für DPS → HBW Navigation

## 🔄 **FTS-Reset-Befehle:**

### **Topic:**
```
fts/v1/ff/5iO4/instantAction
```

### **Payload (clearLoadHandler):**
```json
{
  "serialNumber": "5iO4",
  "timestamp": "2025-01-19T10:00:00.000Z",
  "actions": [
    {
      "actionId": "reset-clear-load-001",
      "actionType": "clearLoadHandler",
      "metadata": {
        "loadDropped": true,
        "loadType": "WHITE",
        "loadId": "reset-workpiece-001",
        "loadPosition": "1"
      }
    }
  ]
}
```

## 📅 **Erstellt:** 2025-01-19
## ✅ **Status:** Getestet und funktionsfähig
