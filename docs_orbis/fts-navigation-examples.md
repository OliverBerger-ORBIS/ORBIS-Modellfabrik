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

## 🔍 **Session-Analyse: Konstant vs. Änderbar**

### **KONSTANT (immer gleich):**
- **Topic:** `fts/v1/ff/5iO4/order`
- **serialNumber:** `"5iO4"`
- **Grid-Struktur:** nodes, edges, linkedNodes, linkedEdges
- **Edge-Längen:** 380cm (Module-Intersection), 360cm (Intersection-Intersection)
- **Action-Typen:** `PASS`, `DOCK`, `TURN`
- **Node-IDs:** `SVR4H73275` (DPS), `SVR3QA0022` (HBW), `1`, `2`, `3`, `4` (Intersections)

### **ÄNDERBAR (pro Auftrag):**
- **timestamp:** Aktueller Zeitstempel
- **orderId:** Eindeutige UUID pro Auftrag
- **orderUpdateId:** Sequenzielle Nummer (0, 2, 6...)
- **action.id:** Eindeutige UUID pro Action
- **loadId:** NFC-Code des Werkstücks
- **loadType:** `RED`, `BLUE`, `WHITE`
- **loadPosition:** `"1"`, `"2"`, `"3"`

### **Route-spezifisch:**
- **Node-Reihenfolge:** Abhängig von Start/Ziel
- **Action-Metadaten:** `direction` bei TURN-Actions
- **Edge-Verbindungen:** Abhängig von Route

## 📊 **Echte Session-Beispiele:**

### **1. DPS-HBW (Wareneingang) - end2end_W1B1R1:**
```json
{
  "timestamp": "2025-08-26T06:25:29.935Z",
  "orderId": "da5d4e77-6bb7-450e-9345-d05db2cd52b9",
  "orderUpdateId": 2,
  "nodes": [
    {"id": "SVR4H73275", "linkedEdges": ["SVR4H73275-2"]},
    {"id": "2", "linkedEdges": ["SVR4H73275-2", "2-1"], "action": {"id": "59caaed5-5205-41dc-abf3-51dc3abe4b73", "type": "PASS"}},
    {"id": "1", "linkedEdges": ["2-1", "1-SVR3QA0022"], "action": {"id": "4037045c-d195-44e5-b3a7-417ef98f2316", "type": "PASS"}},
    {"id": "SVR3QA0022", "linkedEdges": ["1-SVR3QA0022"], "action": {"type": "DOCK", "id": "ca0c9b50-547c-4c9a-be27-084f5b219cc4", "metadata": {"loadId": "04798eca341290", "loadType": "WHITE", "loadPosition": "1"}}}
  ],
  "edges": [
    {"id": "SVR4H73275-2", "length": 380, "linkedNodes": ["SVR4H73275", "2"]},
    {"id": "2-1", "length": 360, "linkedNodes": ["2", "1"]},
    {"id": "1-SVR3QA0022", "length": 380, "linkedNodes": ["1", "SVR3QA0022"]}
  ],
  "serialNumber": "5iO4"
}
```

### **2. HBW-DPS (Rückweg) - wareneingang-rot_2:**
```json
{
  "timestamp": "2025-08-19T08:52:14.739Z",
  "orderId": "e2a4ea34-e7eb-4c97-b0e4-3a8003dcc2c5",
  "orderUpdateId": 0,
  "nodes": [
    {"id": "SVR3QA0022", "linkedEdges": ["SVR3QA0022-1"]},
    {"id": "1", "linkedEdges": ["SVR3QA0022-1", "1-2"], "action": {"id": "c05d4b37-0bd9-4c1a-b5bc-492597f7a43e", "type": "PASS"}},
    {"id": "2", "linkedEdges": ["1-2", "2-SVR4H73275"], "action": {"id": "ab20d3b2-ed10-47db-a184-0108cd348a4f", "type": "PASS"}},
    {"id": "SVR4H73275", "linkedEdges": ["2-SVR4H73275"], "action": {"type": "DOCK", "id": "0bd37113-bd94-497f-ab20-7ed803977652", "metadata": {"loadId": "047f8cca341290", "loadType": "RED", "loadPosition": "1"}}}
  ],
  "edges": [
    {"id": "SVR3QA0022-1", "length": 380, "linkedNodes": ["SVR3QA0022", "1"]},
    {"id": "1-2", "length": 360, "linkedNodes": ["1", "2"]},
    {"id": "2-SVR4H73275", "length": 380, "linkedNodes": ["2", "SVR4H73275"]}
  ],
  "serialNumber": "5iO4"
}
```

### **3. Produktions-Route (ROT) - auftrag-rot_1:**
```json
{
  "timestamp": "2025-08-19T09:16:14.654Z",
  "orderId": "8ae07a6e-d058-48de-9b4d-8d0176622abc",
  "orderUpdateId": 0,
  "nodes": [
    {"id": "SVR4H73275", "linkedEdges": ["SVR4H73275-2"]},
    {"id": "2", "linkedEdges": ["SVR4H73275-2", "2-1"], "action": {"id": "245ca75e-d51f-4f3e-8f44-ccf1881a5a60", "type": "PASS"}},
    {"id": "1", "linkedEdges": ["2-1", "1-SVR3QA0022"], "action": {"id": "fb3b8c84-377e-472d-ad8c-f14521112dac", "type": "PASS"}},
    {"id": "SVR3QA0022", "linkedEdges": ["1-SVR3QA0022"], "action": {"type": "DOCK", "id": "4d1d27e4-db1c-42e0-a01f-8631818bd9b6", "metadata": {"loadType": "RED", "loadPosition": "1"}}}
  ],
  "edges": [
    {"id": "SVR4H73275-2", "length": 380, "linkedNodes": ["SVR4H73275", "2"]},
    {"id": "2-1", "length": 360, "linkedNodes": ["2", "1"]},
    {"id": "1-SVR3QA0022", "length": 380, "linkedNodes": ["1", "SVR3QA0022"]}
  ],
  "serialNumber": "5iO4"
}
```

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
