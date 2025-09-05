# FTS Navigation Examples

## 🗺️ **FTS Grid-Layout (4x3 Raster):**

```
[EMPTY]    [MILL]    [AIQS]    [EMPTY]
              |         |
[HBW] ------[1]-------[2]-------[DPS]
              |         |
[DRILL] -----[3]-------[4]-------[CHRG0]
```

### **📊 Grid-Details:**

#### **Module-Positionen (6):**
- **HBW:** Links unten
- **DRILL:** Links unten (zweite Reihe)
- **MILL:** Oben Mitte
- **AIQS:** Oben rechts
- **DPS:** Rechts Mitte
- **CHRG0:** Rechts unten

#### **Kreuzungspunkte/Intersections (4):**
- **1:** Mitte links (HBW ↔ MILL)
- **2:** Mitte rechts (MILL ↔ AIQS ↔ DPS)
- **3:** Unten links (DRILL ↔ HBW)
- **4:** Unten rechts (DRILL ↔ CHRG0 ↔ DPS)

### **🎯 Navigation-Logik:**
- **Navigation:** Position → Position
- **Kreuzungspunkte:** LINKS, RECHTS, PASS-THROUGH je nach Ziel
- **Grid-basierte Navigation** mit 10 Positionen (6 Module + 4 Intersections)

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
2. **Knoten 2:** PASS (durch Kreuzungspunkt 2)
3. **Knoten 1:** PASS (durch Kreuzungspunkt 1)
4. **Ziel:** SVR3QA0022 (HBW)

### **🗺️ Route im Grid:**
```
DPS → [2] → [1] → HBW
```
- **DPS** (Rechts Mitte)
- **Kreuzungspunkt 2** (PASS - durchfahren)
- **Kreuzungspunkt 1** (PASS - durchfahren)
- **HBW** (Links unten)

## 📋 **Wichtige Erkenntnisse:**
- **FTS-Steuerung erfolgt über:** `fts/v1/ff/5iO4/order`
- **Grid-basierte Navigation** mit 10 Positionen (6 Module + 4 Intersections)
- **Kreuzungspunkte:** LINKS, RECHTS, PASS-THROUGH je nach Ziel
- **Route basiert auf:** Session "wareneingang-weiss" (Zeile 250)
- **Funktioniert zuverlässig** für DPS → HBW Navigation
- **Befehle sind zuverlässig** - es geht um korrekte Grid-Navigation

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

## 🗺️ **Weitere Navigationsbeispiele:**

### **Route: HBW → DRILL**
```
HBW → [1] → [3] → DRILL
```
- **HBW** (Links unten)
- **Kreuzungspunkt 1** (PASS - durchfahren)
- **Kreuzungspunkt 3** (PASS - durchfahren)
- **DRILL** (Links unten, zweite Reihe)

### **Route: DRILL → AIQS**
```
DRILL → [3] → [1] → [2] → AIQS
```
- **DRILL** (Links unten, zweite Reihe)
- **Kreuzungspunkt 3** (PASS - durchfahren)
- **Kreuzungspunkt 1** (PASS - durchfahren)
- **Kreuzungspunkt 2** (PASS - durchfahren)
- **AIQS** (Oben rechts)

### **Route: MILL → DPS**
```
MILL → [2] → DPS
```
- **MILL** (Oben Mitte)
- **Kreuzungspunkt 2** (PASS - durchfahren)
- **DPS** (Rechts Mitte)

## 🎯 **Navigation-Regeln:**
- **Direkte Verbindungen:** Module zu benachbarten Kreuzungspunkten
- **Kreuzungspunkte:** Verbinden Module über das Grid
- **PASS:** Durchfahren ohne Richtungsänderung
- **LINKS/RECHTS:** Richtungsänderung an Kreuzungspunkten (je nach Ziel)

## 📅 **Erstellt:** 2025-01-19
## ✅ **Status:** Getestet und funktionsfähig
