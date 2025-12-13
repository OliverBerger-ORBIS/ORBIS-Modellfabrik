# 📨 MQTT Message Examples - Module Control

**Quelle:** Verifizierte Tests mit Fischertechnik APS  
**Datum:** 2025-11-17  
**Status:** Single Source of Truth für MQTT Message-Formate

---

## 🎯 Übersicht

Dieses Dokument enthält **verifizierte MQTT Message-Beispiele** für die direkte Steuerung der APS-Module. Alle Beispiele wurden erfolgreich getestet und funktionieren mit dem APS-System.

---

## 📋 Module Control Commands

### Verfügbare Commands pro Modul

| Module | Serial Number | Working Commands | Status |
|--------|---------------|------------------|--------|
| **MILL** | `SVR3QA2098` | `PICK`, `MILL`, `DROP` | ✅ **WORKING** |
| **DRILL** | `SVR4H76449` | `PICK`, `DRILL`, `DROP` | ✅ **WORKING** |
| **AIQS** | `SVR4H76530` | `PICK`, `DROP`, `CHECK_QUALITY` | ✅ **WORKING** |
| **HBW** | `SVR3QA0022` | `PICK`, `DROP`, `STORE` | ✅ **WORKING** |
| **DPS** | `SVR4H73275` | `PICK`, `DROP`, `INPUT_RGB`, `RGB_NFC` | ✅ **WORKING** |

---

## 🔧 Message Format

### Topic Pattern
```
module/v1/ff/{serialNumber}/order
```

**Beispiele:**
- `module/v1/ff/SVR4H76449/order` - DRILL Module
- `module/v1/ff/SVR4H76530/order` - AIQS Module
- `module/v1/ff/SVR3QA2098/order` - MILL Module

### Base Message Structure
```json
{
  "serialNumber": "<module-serial-number>",
  "orderId": "<uuid-v4>",
  "orderUpdateId": <integer>,
  "action": {
    "id": "<uuid-v4>",
    "command": "<COMMAND>",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "<WHITE|BLUE|RED>"
    }
  }
}
```

---

## 📨 Message Examples

### 1. DRILL Module - PICK Command (VERIFIED ✅)

**Topic:** `module/v1/ff/SVR4H76449/order`

**Payload:**
```json
{
  "serialNumber": "SVR4H76449",
  "orderId": "993e21ec-88b5-4e50-a478-a3f64a43097b",
  "orderUpdateId": 1,
  "action": {
    "id": "5f5f2fe2-1bdd-4f0e-84c6-33c44d75f07e",
    "command": "PICK",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

### 2. MILL Module - PICK Command

**Topic:** `module/v1/ff/SVR3QA2098/order`

**Payload:**
```json
{
  "serialNumber": "SVR3QA2098",
  "orderId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "orderUpdateId": 1,
  "action": {
    "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "command": "PICK",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

### 3. MILL Module - MILL Command

**Topic:** `module/v1/ff/SVR3QA2098/order`

**Payload:**
```json
{
  "serialNumber": "SVR3QA2098",
  "orderId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "orderUpdateId": 2,
  "action": {
    "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "command": "MILL",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

### 4. DRILL Module - DRILL Command

**Topic:** `module/v1/ff/SVR4H76449/order`

**Payload:**
```json
{
  "serialNumber": "SVR4H76449",
  "orderId": "993e21ec-88b5-4e50-a478-a3f64a43097b",
  "orderUpdateId": 2,
  "action": {
    "id": "d4e5f6a7-b8c9-0123-def0-234567890123",
    "command": "DRILL",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

### 5. AIQS Module - PICK Command

**Topic:** `module/v1/ff/SVR4H76530/order`

**Payload:**
```json
{
  "serialNumber": "SVR4H76530",
  "orderId": "e5f6a7b8-c9d0-1234-ef01-345678901234",
  "orderUpdateId": 1,
  "action": {
    "id": "f6a7b8c9-d0e1-2345-f012-456789012345",
    "command": "PICK",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

### 6. AIQS Module - CHECK_QUALITY Command

**Topic:** `module/v1/ff/SVR4H76530/order`

**Payload:**
```json
{
  "serialNumber": "SVR4H76530",
  "orderId": "e5f6a7b8-c9d0-1234-ef01-345678901234",
  "orderUpdateId": 2,
  "action": {
    "id": "a7b8c9d0-e1f2-3456-0123-567890123456",
    "command": "CHECK_QUALITY",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

### 7. HBW Module - PICK Command

**Topic:** `module/v1/ff/SVR3QA0022/order`

**Payload:**
```json
{
  "serialNumber": "SVR3QA0022",
  "orderId": "b8c9d0e1-f2a3-4567-1234-678901234567",
  "orderUpdateId": 1,
  "action": {
    "id": "c9d0e1f2-a3b4-5678-2345-789012345678",
    "command": "PICK",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

### 8. HBW Module - STORE Command

**Topic:** `module/v1/ff/SVR3QA0022/order`

**Payload:**
```json
{
  "serialNumber": "SVR3QA0022",
  "orderId": "b8c9d0e1-f2a3-4567-1234-678901234567",
  "orderUpdateId": 2,
  "action": {
    "id": "d0e1f2a3-b4c5-6789-3456-890123456789",
    "command": "STORE",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

### 9. DPS Module - PICK Command

**Topic:** `module/v1/ff/SVR4H73275/order`

**Payload:**
```json
{
  "serialNumber": "SVR4H73275",
  "orderId": "e1f2a3b4-c5d6-7890-4567-901234567890",
  "orderUpdateId": 1,
  "action": {
    "id": "f2a3b4c5-d6e7-8901-5678-012345678901",
    "command": "PICK",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

### 10. DPS Module - INPUT_RGB Command

**Topic:** `module/v1/ff/SVR4H73275/order`

**Payload:**
```json
{
  "serialNumber": "SVR4H73275",
  "orderId": "e1f2a3b4-c5d6-7890-4567-901234567890",
  "orderUpdateId": 2,
  "action": {
    "id": "a3b4c5d6-e7f8-9012-6789-123456789012",
    "command": "INPUT_RGB",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

---

## 🔍 Wichtige Anforderungen

### 1. Message Format Requirements

- **Serial Numbers**: Müssen exakte Module-Serial-Numbers verwenden (siehe [Module Serial Mapping](module-serial-mapping.md))
- **Metadata**: `type` Parameter ist erforderlich für PICK/DROP (`WHITE`, `BLUE`, `RED`)
- **OrderIds**: Eindeutige UUIDs für jeden Command (UUID v4)
- **orderUpdateId**: Muss für sequenzielle Commands inkrementell sein (1, 2, 3...)
- **Topics**: Folgen dem Pattern `module/v1/ff/{serialNumber}/order`

### 2. Sequential Commands

Für sequenzielle Commands (z.B. PICK → PROCESS → DROP) muss die gleiche `orderId` verwendet werden, aber `orderUpdateId` muss inkrementiert werden:

```json
// Step 1: PICK
{
  "orderId": "same-uuid",
  "orderUpdateId": 1,
  "action": { "command": "PICK" }
}

// Step 2: PROCESS (MILL/DRILL)
{
  "orderId": "same-uuid",
  "orderUpdateId": 2,
  "action": { "command": "MILL" }
}

// Step 3: DROP
{
  "orderId": "same-uuid",
  "orderUpdateId": 3,
  "action": { "command": "DROP" }
}
```

### 3. Authentication & Connection

- **Broker**: `192.168.0.100:1883`
- **Credentials**: `default`/`default`
- **QoS**: Level 1 für zuverlässige Zustellung

---

## 🎯 Module Control Architecture

### Direct Control Commands
- **PICK**: Werkstück aufnehmen
- **DROP**: Werkstück abgeben
- **STORE**: Werkstück einlagern (HBW)
- **CHECK_QUALITY**: Qualitätsprüfung (AIQS)

### Automatic Control Commands
- **MILL**: Fräsen (wird vom APS-System automatisch verarbeitet)
- **DRILL**: Bohren (wird vom APS-System automatisch verarbeitet)

### Sequential Dependencies
- Einige Commands benötigen vorherige `orderIds` für korrekte Sequenzierung
- `orderUpdateId` muss für sequenzielle Commands korrekt inkrementiert werden

---

## ⚠️ Bekannte Einschränkungen

### Partially Working Commands
1. **PROCESS Commands**: Benötigen korrekte `orderUpdateId` Sequenz
2. **Workflow Dependencies**: PICK → PROCESS → DROP erfordert ORDER-ID Tracking
3. **ORDER-ID Management**: `"OrderUpdateId not valid"` Fehler können auftreten bei falscher Sequenzierung

### Non-Working Commands
1. **Sequential Commands**: Ohne korrektes ORDER-ID Management
2. **Workflow Templates**: Benötigen ORDER-ID Tracking Implementierung

---

## 🔗 Verwandte Dokumentation

- [Module Serial Mapping](module-serial-mapping.md) - Serial-Numbers und Hardware-Zuordnung
- [MQTT Topic Conventions](mqtt-topic-conventions.md) - Topic-Naming-Patterns
- [CCU Backend Orchestration](ccu-backend-orchestration.md) - Order-Management & Workflow
- [Component Overview](component-overview.md) - Komplett-Übersicht aller Komponenten

---

**Erstellt:** 2025-11-17  
**Status:** Verifizierte MQTT Message Examples - Single Source of Truth
