# 🔧 Funktionierende MQTT-Sequenzen aus Commit 807c29a

## 📋 Übersicht

**Commit:** `807c29a` - "Sequence Control for Mill Drill and AIQS"  
**Datum:** 20. August 2025  
**Status:** Alle Hauptmodule funktionsfähig, FTS/DPS noch nicht implementiert

## 🎯 Funktionierende Module

### ✅ Vollständig funktionsfähig:

| Modul | Seriennummer | IP-Adresse | Status |
|-------|--------------|------------|---------|
| **AIQS** | SVR4H76530 | 192.168.0.70 | ✅ Vollständige Sequenz |
| **MILL** | SVR3QA2098 | 192.168.0.40 | ✅ Vollständige Sequenz |
| **DRILL** | SVR4H76449 | 192.168.0.50 | ✅ Vollständige Sequenz |
| **HBW** | SVR3QA0022 | 192.168.0.80 | ✅ Teilweise (DROP funktioniert) |

### ❌ Nicht implementiert (spätere Version):

| Modul | Seriennummer | IP-Adresse | Status |
|-------|--------------|------------|---------|
| **FTS** | 5iO4 | - | ❌ Noch nicht implementiert |
| **DPS** | SVR4H73275 | 192.168.0.90 | ❌ Noch nicht implementiert |
| **Ladestation** | CHRG0 | - | ❌ Passiv, keine Befehle |

## 📡 MQTT Topic-Struktur

```
module/v1/ff/{serial_number}/order
```

**Beispiele:**
- AIQS: `module/v1/ff/SVR4H76530/order`
- MILL: `module/v1/ff/SVR3QA2098/order`
- DRILL: `module/v1/ff/SVR4H76449/order`
- HBW: `module/v1/ff/SVR3QA0022/order`

## 🎯 Funktionierende Sequenzen

### 1. AIQS-Sequenz (SVR4H76530)

**Sequenz:** `PICK → CHECK_QUALITY → DROP`

#### Schritt 1: PICK
```json
{
  "serialNumber": "SVR4H76530",
  "orderId": "uuid-v4",
  "orderUpdateId": 1,
  "action": {
    "id": "uuid-v4",
    "command": "PICK",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

#### Schritt 2: CHECK_QUALITY
```json
{
  "serialNumber": "SVR4H76530",
  "orderId": "uuid-v4",
  "orderUpdateId": 2,
  "action": {
    "id": "uuid-v4",
    "command": "CHECK_QUALITY",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

#### Schritt 3: DROP
```json
{
  "serialNumber": "SVR4H76530",
  "orderId": "uuid-v4",
  "orderUpdateId": 3,
  "action": {
    "id": "uuid-v4",
    "command": "DROP",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

**Wichtige Erkenntnisse:**
- `orderId` bleibt konstant für die gesamte Sequenz
- `orderUpdateId` wird bei jedem Schritt erhöht (1→2→3)
- `action.id` ist ein neuer UUID für jeden Befehl
- **Farbe wird von AIQS erkannt und ausgewertet**

### 2. MILL-Sequenz (SVR3QA2098)

**Sequenz:** `PICK → MILL → DROP`

#### Schritt 1: PICK
```json
{
  "serialNumber": "SVR3QA2098",
  "orderId": "uuid-v4",
  "orderUpdateId": 1,
  "action": {
    "id": "uuid-v4",
    "command": "PICK",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

#### Schritt 2: MILL
```json
{
  "serialNumber": "SVR3QA2098",
  "orderId": "uuid-v4",
  "orderUpdateId": 2,
  "action": {
    "id": "uuid-v4",
    "command": "MILL",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE",
      "duration": 45
    }
  }
}
```

#### Schritt 3: DROP
```json
{
  "serialNumber": "SVR3QA2098",
  "orderId": "uuid-v4",
  "orderUpdateId": 3,
  "action": {
    "id": "uuid-v4",
    "command": "DROP",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

**Wichtige Erkenntnisse:**
- **Farbe wird ignoriert** - alle Farben (WHITE/RED/BLUE) funktionieren
- `duration: 45` Sekunden für MILL-Befehl
- Gleiche Struktur wie AIQS

### 3. DRILL-Sequenz (SVR4H76449)

**Sequenz:** `PICK → DRILL → DROP`

#### Schritt 1: PICK
```json
{
  "serialNumber": "SVR4H76449",
  "orderId": "uuid-v4",
  "orderUpdateId": 1,
  "action": {
    "id": "uuid-v4",
    "command": "PICK",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

#### Schritt 2: DRILL
```json
{
  "serialNumber": "SVR4H76449",
  "orderId": "uuid-v4",
  "orderUpdateId": 2,
  "action": {
    "id": "uuid-v4",
    "command": "DRILL",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE",
      "duration": 30
    }
  }
}
```

#### Schritt 3: DROP
```json
{
  "serialNumber": "SVR4H76449",
  "orderId": "uuid-v4",
  "orderUpdateId": 3,
  "action": {
    "id": "uuid-v4",
    "command": "DROP",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

**Wichtige Erkenntnisse:**
- **Farbe wird ignoriert** - alle Farben funktionieren
- `duration: 30` Sekunden für DRILL-Befehl
- Gleiche Struktur wie MILL

### 4. HBW-Einzelbefehl (SVR3QA0022)

**Funktionierender Befehl:** `DROP`

```json
{
  "serialNumber": "SVR3QA0022",
  "orderId": "uuid-v4",
  "orderUpdateId": 1,
  "action": {
    "id": "uuid-v4",
    "command": "DROP",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

**Wichtige Erkenntnisse:**
- HBW kann Werkstücke an FTS übergeben
- Position B2 mit weißem Werkstück funktioniert
- Weitere Befehle (PICK, STORE) wurden nicht getestet

## 🔍 Farbverhalten der Module

| Modul | Farbverhalten | Details |
|-------|---------------|---------|
| **AIQS** | ✅ Erkennt Farbe | Farbe wird ausgewertet und verarbeitet |
| **MILL** | ❌ Ignoriert Farbe | Alle Farben (WHITE/RED/BLUE) funktionieren |
| **DRILL** | ❌ Ignoriert Farbe | Alle Farben (WHITE/RED/BLUE) funktionieren |
| **HBW** | ❓ Nicht getestet | DROP funktioniert mit WHITE |

## 📊 LED-Status der Zentralen Steuerung

| LED-Farbe | Bedeutung | Status |
|-----------|-----------|---------|
| 🟠 **ORANGE** | Fabrik busy | Verarbeitet Befehle |
| 🟢 **GRÜN** | Fabrik bereit | Wartet auf Befehle |

## 🧪 Test-Empfehlungen für aktuelle Implementierung

### 1. Einfache Befehle testen:
- MILL PICK (alle Farben)
- DRILL PICK (alle Farben)
- AIQS PICK (WHITE)

### 2. Verarbeitungsbefehle testen:
- MILL MILL (45s)
- DRILL DRILL (30s)
- AIQS CHECK_QUALITY

### 3. Vollständige Sequenzen testen:
- PICK → MILL/DRILL/CHECK_QUALITY → DROP

### 4. HBW-Funktionalität testen:
- DROP mit verschiedenen Positionen
- PICK und STORE Befehle

## 📝 Nächste Schritte

1. **Unit-Tests für funktionierende Befehle erstellen**
2. **Nach Commit mit FTS und Bestellungen (ROT/WEISS/BLAU) suchen**
3. **Funktionierende Nachrichten in aktuelle Implementierung integrieren**

## 🔗 Verwandte Dokumente

- [MQTT Message Library](../src_orbis/mqtt/tools/mqtt_message_library.py)
- [Template Message Manager](../src_orbis/mqtt/tools/template_message_manager.py)
- [APS Dashboard](../src_orbis/mqtt/dashboard/aps_dashboard.py)
