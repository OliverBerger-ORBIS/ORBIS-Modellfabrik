# CCU Topic Mapping für OMF-Übernahme

> ⚠️ **VERIFIKATION AUSSTEHEND**: Diese Analyse basiert auf Log-Dateien und wurde noch nicht vollständig verifiziert. Die beschriebenen Topic-Mappings müssen noch getestet und validiert werden.

## 🎯 Ziel

Dokumentation der Topics, die OMF abonnieren und senden muss, um die CCU (Node-RED) zu ersetzen.

## 📥 OMF muss abonnieren (Inbound Topics)

### 1. Production Order Requests
| Topic | Zweck | Payload Pattern |
|-------|-------|-----------------|
| `ccu/order/request` | Production Order Requests von Dashboard/FT | `{"type": "RED|WHITE|BLUE", "orderType": "PRODUCTION"}` |

### 2. Module Status Updates
| Topic Pattern | Modul | Zweck | Payload Pattern |
|---------------|-------|-------|-----------------|
| `module/v1/ff/SVR3QA0022/state` | HBW | Lagerbestand Status | `{"serialNumber": "SVR3QA0022", "state": "IDLE|BUSY|ERROR", "stock": {...}}` |
| `module/v1/ff/SVR4H76449/state` | DRILL | Bearbeitungsstatus | `{"serialNumber": "SVR4H76449", "state": "IDLE|BUSY|ERROR"}` |
| `module/v1/ff/SVR3QA2098/state` | MILL | Bearbeitungsstatus | `{"serialNumber": "SVR3QA2098", "state": "IDLE|BUSY|ERROR"}` |
| `module/v1/ff/SVR4H76530/state` | AIQS | Qualitätsprüfung Status | `{"serialNumber": "SVR4H76530", "state": "IDLE|BUSY|ERROR"}` |
| `module/v1/ff/SVR4H73275/state` | DPS | Entladestation Status | `{"serialNumber": "SVR4H73275", "state": "IDLE|BUSY|ERROR"}` |
| `module/v1/ff/CHRG0/state` | CHRG | Ladezustand | `{"serialNumber": "CHRG0", "state": "IDLE|BUSY|ERROR"}` |

### 3. Module Connection Status
| Topic Pattern | Modul | Zweck | Payload Pattern |
|---------------|-------|-------|-----------------|
| `module/v1/ff/*/connection` | Alle Module | Verbindungsstatus | `{"serialNumber": "...", "connected": true/false}` |

### 4. Module Konfiguration
| Topic Pattern | Modul | Zweck | Payload Pattern |
|---------------|-------|-------|-----------------|
| `module/v1/ff/*/factsheet` | Alle Module | Module-Metadaten | `{"serialNumber": "...", "capabilities": {...}}` |

## 📤 OMF muss senden (Outbound Topics)

### 1. FTS Transport Orders
| Topic | Zweck | Payload Pattern |
|-------|-------|-----------------|
| `fts/v1/ff/5iO4/order` | FTS Transport Aufträge | `{"orderId": "uuid", "action": {"command": "PICK|PLACE|MOVE", "metadata": {...}}}` |

### 2. TXT Controller Orders
| Topic | Zweck | Payload Pattern |
|-------|-------|-----------------|
| `/j1/txt/1/f/i/order` | TXT Station Orders | `{"orderId": "uuid", "type": "RED|WHITE|BLUE", "state": "IN_PROCESS"}` |

### 3. Module-spezifische Orders
| Topic Pattern | Modul | Zweck | Payload Pattern |
|---------------|-------|-------|-----------------|
| `module/v1/ff/SVR3QA0022/order` | HBW | Lager-Operationen | `{"orderId": "uuid", "action": {"command": "PICK|PLACE"}, "metadata": {...}}` |
| `module/v1/ff/SVR4H76449/order` | DRILL | Bohr-Operationen | `{"orderId": "uuid", "action": {"command": "DRILL"}, "metadata": {...}}` |
| `module/v1/ff/SVR3QA2098/order` | MILL | Fräs-Operationen | `{"orderId": "uuid", "action": {"command": "MILL"}, "metadata": {...}}` |
| `module/v1/ff/SVR4H76530/order` | AIQS | Qualitätsprüfung | `{"orderId": "uuid", "action": {"command": "CHECK"}, "metadata": {...}}` |
| `module/v1/ff/SVR4H73275/order` | DPS | Entlade-Operationen | `{"orderId": "uuid", "action": {"command": "UNLOAD"}, "metadata": {...}}` |
| `module/v1/ff/CHRG0/order` | CHRG | Lade-Operationen | `{"orderId": "uuid", "action": {"command": "CHARGE"}, "metadata": {...}}` |

## 🔄 Business Logic Implementation

### 1. Order Processing Pipeline
```
1. Empfange ccu/order/request (ohne orderId)
2. Generiere orderId (UUID)
3. Prüfe Module-Verfügbarkeit (module/*/state)
4. Plane Sequenz basierend auf Stock (module/SVR3QA0022/state)
5. Sende Module-Orders (module/*/order)
6. Sende FTS-Order (fts/v1/ff/5iO4/order)
7. Sende TXT-Order (/j1/txt/1/f/i/order)
```

### 2. Stock Management
```
1. Empfange HBW Stock Updates (module/SVR3QA0022/state)
2. Verwalte Stock-Positionen (A1-C3)
3. Prüfe Verfügbarkeit für Orders
4. Aktualisiere Stock nach Order-Abschluss
```

### 3. Module Status Monitoring
```
1. Empfange Module Status (module/*/state)
2. Empfange Connection Status (module/*/connection)
3. Überwache Activity Status
4. Implementiere Error Handling
5. Implementiere Retry-Logik
```

## 📊 Topic Direction Summary

| Kategorie | Inbound Topics | Outbound Topics |
|-----------|----------------|-----------------|
| **Production Orders** | `ccu/order/request` | - |
| **Module Control** | - | `module/*/order` |
| **Transport** | - | `fts/v1/ff/5iO4/order` |
| **Station Control** | - | `/j1/txt/1/f/i/order` |
| **Status Monitoring** | `module/*/state` | - |
| **Connection Monitoring** | `module/*/connection` | - |
| **Configuration** | `module/*/factsheet` | - |

## 🚨 Kritische Abhängigkeiten

### 1. OrderId-Generierung
- **Muss implementiert werden**: UUID-Generierung für alle Orders
- **Timing**: OrderId muss vor ersten Module-Orders generiert werden

### 2. Stock-Konsistenz
- **HBW Stock Updates**: Zyklische Updates alle 1-5 Sekunden
- **Stock-Verfügbarkeit**: Muss vor Order-Processing geprüft werden

### 3. Module-Status-Synchronisation
- **Activity Status**: Module müssen verfügbar sein vor Order-Send
- **Error Handling**: Retry-Logik bei Module-Fehlern

### 4. Sequenz-Planung
- **Order-Abhängigkeiten**: Module-Orders müssen in korrekter Reihenfolge
- **FTS-Integration**: Transport muss mit Module-Operations synchronisiert werden

## 🔗 Verwandte Dokumentation

- [Production Order Analysis Summary](production-order-analysis-summary.md)
- [Stock Management Analysis](stock-management-analysis.md)
- [Registry Observation: Template Direction](../../registry/observations/2025-01-15_template_direction_component_perspective.yml)

---

**Erstellt**: 2025-01-15  
**Zweck**: CCU-Übernahme durch OMF  
**Status**: Analyse abgeschlossen, Implementation ausstehend
