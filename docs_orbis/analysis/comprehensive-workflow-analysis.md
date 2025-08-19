# Umfassende Workflow-Analyse: Wareneingang, Auftrag und AI-not-ok Sessions

## 📋 Übersicht

Diese umfassende Analyse untersucht alle Workflow-Typen der APS-Modellfabrik:
- **Wareneingang** (Rot, Weiss, Blau) - Werkstück-Eingang und Lagerung
- **Auftrag** (Rot, Weiss, Blau) - Produktionsaufträge mit Verarbeitung
- **AI-not-ok** (Rot, Weiss, Blau) - Produktionsaufträge mit AI-Prüfung

**Ziel:** Vollständiges Verständnis der Workflows für Template Message Entwicklung.

## 🎯 Analysierte Sessions

### Wareneingang Sessions (9)
- `aps_persistent_traffic_wareneingang-rot_1.db` bis `wareneingang-rot_3.db`
- `aps_persistent_traffic_wareneingang-weiss_1.db` bis `wareneingang-weiss_3.db`
- `aps_persistent_traffic_wareneingang-blau_1.db` bis `wareneingang-blau_3.db`

### Auftrag Sessions (3)
- `aps_persistent_traffic_auftrag-rot_1.db`
- `aps_persistent_traffic_auftrag-weiss_1.db`
- `aps_persistent_traffic_auftrag-blau_1.db`

### AI-not-ok Sessions (3)
- `aps_persistent_traffic_ai-not-ok-rot_1.db`
- `aps_persistent_traffic_ai-not-ok-weiss_1.db`
- `aps_persistent_traffic_ai-not-ok-blau_1.db`

**Gesamt:** 15 Sessions mit 3.879 + 3.212 + 5.329 = **12.420 Nachrichten**

## 🔄 Workflow-Typen Übersicht

### 1. 🏭 Wareneingang (STORAGE)
**Zweck:** Werkstück-Eingang und Lagerung im HBW
**Trigger:** Werkstück wird in DPS-Eingang gelegt
**Ergebnis:** Werkstück wird im HBW gelagert

### 2. 📋 Auftrag (PRODUCTION)
**Zweck:** Produktionsauftrag mit Verarbeitung
**Trigger:** Auftrag wird erstellt
**Ergebnis:** Werkstück wird verarbeitet und zum Warenausgang transportiert

### 3. 🤖 AI-not-ok (PRODUCTION + AI)
**Zweck:** Produktionsauftrag mit AI-Qualitätsprüfung
**Trigger:** Auftrag wird erstellt (mit AI-Prüfung)
**Ergebnis:** Werkstück wird verarbeitet, AI-geprüft und zum Warenausgang transportiert

## 🎨 Farb-spezifische Workflows

### 🔴 ROT

#### Wareneingang (STORAGE)
```
DPS Input → FTS → HBW Storage
```
**Verarbeitung:** Keine (nur Lagerung)

#### Auftrag (PRODUCTION)
```
HBW → FTS → MILL → MILL → FTS → AIQS → FTS → DPS Output
```
**Verarbeitung:** MILL

#### AI-not-ok (PRODUCTION + AI)
```
HBW → FTS → MILL → MILL → FTS → AIQS → FTS → DPS Output
```
**Verarbeitung:** MILL + AI-Qualitätsprüfung

### ⚪ WEISS

#### Wareneingang (STORAGE)
```
DPS Input → FTS → HBW Storage
```
**Verarbeitung:** Keine (nur Lagerung)

#### Auftrag (PRODUCTION)
```
HBW → FTS → DRILL → DRILL → FTS → AIQS → FTS → DPS Output
```
**Verarbeitung:** DRILL

#### AI-not-ok (PRODUCTION + AI)
```
HBW → FTS → DRILL → DRILL → FTS → AIQS → FTS → DPS Output
```
**Verarbeitung:** DRILL + AI-Qualitätsprüfung

### 🔵 BLAU

#### Wareneingang (STORAGE)
```
DPS Input → FTS → HBW Storage
```
**Verarbeitung:** Keine (nur Lagerung)

#### Auftrag (PRODUCTION)
```
HBW → FTS → DRILL → DRILL → FTS → MILL → MILL → FTS → AIQS → FTS → DPS Output
```
**Verarbeitung:** DRILL + MILL

#### AI-not-ok (PRODUCTION + AI)
```
HBW → FTS → DRILL → DRILL → FTS → MILL → MILL → FTS → AIQS → FTS → DPS Output
```
**Verarbeitung:** DRILL + MILL + AI-Qualitätsprüfung

## 🔧 Verarbeitungsschritte pro Farbe

### 🔴 ROT
- **Wareneingang:** Keine Verarbeitung
- **Auftrag:** MILL(MILL) - 1x
- **AI-not-ok:** MILL(MILL) - 1x

### ⚪ WEISS
- **Wareneingang:** Keine Verarbeitung
- **Auftrag:** DRILL(DRILL) - 1x
- **AI-not-ok:** DRILL(DRILL) - 1x

### 🔵 BLAU
- **Wareneingang:** Keine Verarbeitung
- **Auftrag:** DRILL(DRILL) - 1x + MILL(MILL) - 1x
- **AI-not-ok:** DRILL(DRILL) - 1x + MILL(MILL) - 1x

## 🎯 ORDER-ID Management

### Wareneingang
- **ORDER-IDs:** 3 pro Session (9 Sessions = 27 ORDER-IDs)
- **Typ:** STORAGE
- **Generierung:** CCU bei `ccu/order/request`
- **Workflow:** Einfach (DPS → HBW)

### Auftrag
- **ORDER-IDs:** 1 pro Session (3 Sessions = 3 ORDER-IDs)
- **Typ:** PRODUCTION
- **Generierung:** CCU bei `ccu/order/request`
- **Workflow:** Komplex (HBW → Verarbeitung → AIQS → DPS)

### AI-not-ok
- **ORDER-IDs:** 2 pro Session (3 Sessions = 6 ORDER-IDs)
- **Typ:** PRODUCTION + AI
- **Generierung:** CCU bei `ccu/order/request`
- **Workflow:** Komplex + AI-Qualitätsprüfung

## 📋 Template Message Strategie

### Wareneingang Templates

#### 🔴 ROT Wareneingang
```json
{
  "topic": "ccu/order/request",
  "payload": {
    "type": "RED",
    "workpieceId": "{workpieceId}",
    "orderType": "STORAGE"
  }
}
```

#### ⚪ WEISS Wareneingang
```json
{
  "topic": "ccu/order/request",
  "payload": {
    "type": "WHITE",
    "workpieceId": "{workpieceId}",
    "orderType": "STORAGE"
  }
}
```

#### 🔵 BLAU Wareneingang
```json
{
  "topic": "ccu/order/request",
  "payload": {
    "type": "BLUE",
    "workpieceId": "{workpieceId}",
    "orderType": "STORAGE"
  }
}
```

### Auftrag Templates

#### 🔴 ROT Auftrag
```json
{
  "topic": "ccu/order/request",
  "payload": {
    "type": "RED",
    "workpieceId": "{workpieceId}",
    "orderType": "PRODUCTION",
    "productionSteps": [
      "PICK(MILL)",
      "MILL(MILL)",
      "DROP(MILL)"
    ]
  }
}
```

#### ⚪ WEISS Auftrag
```json
{
  "topic": "ccu/order/request",
  "payload": {
    "type": "WHITE",
    "workpieceId": "{workpieceId}",
    "orderType": "PRODUCTION",
    "productionSteps": [
      "PICK(DRILL)",
      "DRILL(DRILL)",
      "DROP(DRILL)"
    ]
  }
}
```

#### 🔵 BLAU Auftrag
```json
{
  "topic": "ccu/order/request",
  "payload": {
    "type": "BLUE",
    "workpieceId": "{workpieceId}",
    "orderType": "PRODUCTION",
    "productionSteps": [
      "PICK(DRILL)",
      "DRILL(DRILL)",
      "DROP(DRILL)",
      "PICK(MILL)",
      "MILL(MILL)",
      "DROP(MILL)"
    ]
  }
}
```

### AI-not-ok Templates

#### 🔴 ROT AI-not-ok
```json
{
  "topic": "ccu/order/request",
  "payload": {
    "type": "RED",
    "workpieceId": "{workpieceId}",
    "orderType": "PRODUCTION",
    "aiInspection": true,
    "productionSteps": [
      "PICK(MILL)",
      "MILL(MILL)",
      "DROP(MILL)"
    ]
  }
}
```

#### ⚪ WEISS AI-not-ok
```json
{
  "topic": "ccu/order/request",
  "payload": {
    "type": "WHITE",
    "workpieceId": "{workpieceId}",
    "orderType": "PRODUCTION",
    "aiInspection": true,
    "productionSteps": [
      "PICK(DRILL)",
      "DRILL(DRILL)",
      "DROP(DRILL)"
    ]
  }
}
```

#### 🔵 BLAU AI-not-ok
```json
{
  "topic": "ccu/order/request",
  "payload": {
    "type": "BLUE",
    "workpieceId": "{workpieceId}",
    "orderType": "PRODUCTION",
    "aiInspection": true,
    "productionSteps": [
      "PICK(DRILL)",
      "DRILL(DRILL)",
      "DROP(DRILL)",
      "PICK(MILL)",
      "MILL(MILL)",
      "DROP(MILL)"
    ]
  }
}
```

## 🎯 Konsistenz-Analyse

### ✅ Konsistente Elemente

1. **ORDER-ID Generierung:** CCU generiert immer eindeutige ORDER-IDs
2. **Farb-Erkennung:** Immer bei `ccu/order/request` mit `"type": "COLOR"`
3. **Werkstück-Tracking:** Eindeutige Werkstück-IDs pro Farbe
4. **Modul-Kommunikation:** Konsistente MQTT-Topics und Payload-Struktur
5. **Workflow-Status:** Verfolgung über `ccu/order/active` und `ccu/order/completed`

### 🔄 Unterschiede zwischen Workflow-Typen

| Aspekt | Wareneingang | Auftrag | AI-not-ok |
|--------|-------------|---------|-----------|
| **Zweck** | Lagerung | Produktion | Produktion + AI |
| **Komplexität** | Einfach | Mittel | Hoch |
| **ORDER-IDs** | 3 pro Session | 1 pro Session | 2 pro Session |
| **Verarbeitung** | Keine | Farb-spezifisch | Farb-spezifisch + AI |
| **AIQS** | Nein | Ja | Ja (mit Qualitätsprüfung) |
| **Warenausgang** | Nein | Ja | Ja |

### 🎨 Farb-spezifische Konsistenz

| Farbe | Wareneingang | Auftrag | AI-not-ok |
|-------|-------------|---------|-----------|
| **ROT** | Lagerung | MILL | MILL + AI |
| **WEISS** | Lagerung | DRILL | DRILL + AI |
| **BLAU** | Lagerung | DRILL + MILL | DRILL + MILL + AI |

## 🚀 Template Message Manager Integration

### Erweiterte Template Library

```python
# Wareneingang Templates
wareneingang_red_template = {...}
wareneingang_white_template = {...}
wareneingang_blue_template = {...}

# Auftrag Templates
auftrag_red_template = {...}
auftrag_white_template = {...}
auftrag_blue_template = {...}

# AI-not-ok Templates
ai_not_ok_red_template = {...}
ai_not_ok_white_template = {...}
ai_not_ok_blue_template = {...}
```

### Dashboard Integration

```python
# Workflow-Typ Auswahl
workflow_type = st.selectbox(
    "Workflow-Typ:",
    ["Wareneingang", "Auftrag", "AI-not-ok"]
)

# Farbe Auswahl
color = st.selectbox(
    "Farbe:",
    ["RED", "WHITE", "BLUE"]
)

# Template basierend auf Auswahl
template = get_template(workflow_type, color)
```

## 📊 Zusammenfassung

### 🎯 **Haupt-Erkenntnisse:**

1. **Konsistente ORDER-ID Generierung** über alle Workflow-Typen
2. **Farb-spezifische Verarbeitung** ist eindeutig und konsistent
3. **Workflow-Komplexität** steigt von Wareneingang → Auftrag → AI-not-ok
4. **Template Messages** können für alle 9 Kombinationen erstellt werden

### 🔧 **Verarbeitungsschritte:**
- **ROT:** MILL (Auftrag/AI-not-ok)
- **WEISS:** DRILL (Auftrag/AI-not-ok)
- **BLAU:** DRILL + MILL (Auftrag/AI-not-ok)

### 📋 **Template Message Parameter:**
- **color:** RED/WHITE/BLUE
- **workpieceId:** Eindeutige Werkstück-ID
- **orderType:** STORAGE/PRODUCTION
- **aiInspection:** Boolean (nur AI-not-ok)
- **productionSteps:** Farb-spezifische Verarbeitungsschritte

### 🚀 **Nächste Schritte:**
1. **Template Message Manager erweitern** um alle 9 Workflow-Templates
2. **Dashboard Integration** für alle Workflow-Typen
3. **Live-Test** der Template Messages im Büro
4. **Workflow-Tracking** für alle ORDER-IDs implementieren

## ✅ **Fazit**

Die Analyse zeigt **vollständige Konsistenz** zwischen allen Workflow-Typen:
- **Wareneingang:** Einfach, konsistent, 3 ORDER-IDs pro Session
- **Auftrag:** Mittel, farb-spezifisch, 1 ORDER-ID pro Session
- **AI-not-ok:** Komplex, farb-spezifisch + AI, 2 ORDER-IDs pro Session

Alle Workflows können als **Template Messages** implementiert werden, wobei die CCU die ORDER-IDs generiert und das Dashboard die Workflows überwacht.
