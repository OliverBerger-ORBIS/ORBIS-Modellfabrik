# Production Order Flow Analysis - Zusammenfassung

> ⚠️ **VERIFIKATION AUSSTEHEND**: Diese Analyse basiert auf Log-Dateien und wurde noch nicht vollständig verifiziert. Die beschriebenen Message-Flows und Komponenten-Interaktionen müssen noch getestet und validiert werden.

## 🎯 Zentrale Erkenntnisse

### 1. OrderId-Generierung und -Verarbeitung

**Wichtige Erkenntnis**: Beide Dashboards (OMF Dashboard und Fischertechnik Dashboard) senden `ccu/order/request` **ohne** `orderId`. Falls eine `orderId` vorhanden ist, wird sie überschrieben.

#### Message-Flow (Chronologisch):
1. **Position 0**: [Kunde] → [Dashboard/FT] → [sendet `ccu/order/request` OHNE `orderId`]
2. **Position 1**: [CCU] → [abonniert `ccu/order/request`] → [erstellt `orderId`] → [sendet `fts/v1/ff/5iO4/order`]
3. **Position 2**: [FTS] → [abonniert `fts/v1/ff/5iO4/order`] → [überschreibt `orderId` mit UUID] → [führt Transport aus]
4. **Position 3**: [CCU] → [sendet `/j1/txt/1/f/i/order`] → [TXT Controller verarbeitet Order]

### 2. Beteiligte Komponenten

| Komponente | Rolle | Verantwortlichkeiten |
|------------|-------|---------------------|
| **Dashboard/FT** | Order-Initiation | Sendet Production Order Request ohne `orderId` |
| **CCU** | Order-Processing | Erstellt `orderId`, koordiniert FTS und TXT |
| **FTS** | Transport-Execution | Überschreibt `orderId` mit UUID, führt Transport aus |
| **TXT Controller** | Station-Control | Verarbeitet Station-spezifische Orders |

### 3. Message-Patterns

#### Production Order Request Pattern:
**Topic:** `ccu/order/request` (CCU abonniert, Dashboard/FT sendet)
```json
{
  "type": "RED|WHITE|BLUE",
  "orderType": "PRODUCTION",
  "timestamp": "2025-08-19T09:16:14.336Z"
  // KEINE orderId!
}
```

#### OrderId Enrichment Pattern:
**Topic:** `fts/v1/ff/5iO4/order` (FTS abonniert, CCU sendet)
```json
{
  "orderId": "8ae07a6e-d058-48de-9b4d-8d0176622abc",
  "timestamp": "2025-08-19T09:16:14.654Z",
  "action": {
    "command": "PICK|PLACE|MOVE",
    "metadata": {
      "type": "RED|WHITE|BLUE",
      "workpieceId": "04c489ca341290"
    }
  }
}
```

#### TXT Controller Order Pattern:
**Topic:** `/j1/txt/1/f/i/order` (TXT Controller abonniert, CCU sendet)
```json
{
  "orderId": "8ae07a6e-d058-48de-9b4d-8d0176622abc",
  "timestamp": "2025-08-19T09:16:14.679Z",
  "type": "RED",
  "state": "IN_PROCESS"
}
```

### 4. CCU (Node-RED) Topic-Mapping

#### CCU abonniert (Inbound):
- `ccu/order/request` - Production Order Requests von Dashboard/FT
- `module/v1/ff/*/state` - Module Status Updates (HBW, DRILL, MILL, AIQS, DPS, CHRG)
- `module/v1/ff/*/connection` - Module Connection Status
- `module/v1/ff/*/factsheet` - Module Konfiguration/Metadaten

#### CCU sendet (Outbound):
- `fts/v1/ff/5iO4/order` - FTS Transport Orders
- `/j1/txt/1/f/i/order` - TXT Controller Orders
- `module/v1/ff/*/order` - Module-spezifische Orders

#### Template Direction Mapping (aus CCU-Sicht):
| Topic Pattern | CCU Richtung | Zweck | Module |
|---------------|--------------|-------|--------|
| `module/v1/ff/*/connection` | **INBOUND** | Connection Status empfangen | HBW, DRILL, MILL, AIQS, DPS, CHRG |
| `module/v1/ff/*/state` | **INBOUND** | State Updates empfangen | HBW, DRILL, MILL, AIQS, DPS, CHRG |
| `module/v1/ff/*/order` | **OUTBOUND** | Orders an Module senden | HBW, DRILL, MILL, AIQS, DPS, CHRG |
| `module/v1/ff/*/factsheet` | **INBOUND** | Module-Konfiguration empfangen | HBW, DRILL, MILL, AIQS, DPS, CHRG |

> **Hinweis**: Registry verwendet `template_direction: bidirectional`, aber für CCU-Übernahme ist die Komponenten-Sicht relevant. Siehe [Observation](../../registry/observations/2025-01-15_template_direction_component_perspective.yml).

### 5. Topic-Hierarchie

#### Chronologische Reihenfolge der Topics:
1. `ccu/order/request` - Initial Order Request (ohne `orderId`)
2. `fts/v1/ff/5iO4/order` - FTS Order mit `orderId`
3. `/j1/txt/1/f/i/order` - TXT Controller Order
4. Weitere Module-spezifische Topics

### 6. CCU Business Logic (zu implementieren)

#### 1. Lagerbestand-Verwaltung:
- **Input:** `module/v1/ff/SVR3QA0022/state` (HBW Stock Updates)
- **Logik:** Stock-Positionen verwalten (A1-C3), Verfügbarkeit prüfen
- **Output:** Stock-Status für Order-Processing

#### 2. Bestellungs-Verwaltung:
- **Input:** `ccu/order/request` (Production Orders)
- **Logik:** OrderId generieren, Module-Zuweisung, Sequenz-Planung
- **Output:** Module-spezifische Orders

#### 3. Modul-Status-Überwachung:
- **Input:** `module/v1/ff/*/state` (Module Status)
- **Logik:** Activity Status prüfen, Fehlerbehandlung, Retry-Logik
- **Output:** Status-basierte Order-Freigabe

### 7. Stock Management Pattern

**Erkenntnis**: HBW (Hochregallager) verwendet ein **PUSH-Pattern**:
- HBW sendet zyklische Updates an CCU
- CCU wird **nicht** aktiv abgefragt
- Keine zentrale Stock-Management-Entität

#### Stock Update Pattern:
```json
{
  "topic": "module/v1/ff/SVR3QA0022/state",
  "payload": {
    "serialNumber": "SVR3QA0022",
    "state": "IDLE|BUSY|ERROR",
    "stock": {
      "A1": "RED|WHITE|BLUE|EMPTY",
      "A2": "RED|WHITE|BLUE|EMPTY",
      // ... alle 9 Positionen
    }
  }
}
```

## 🔍 Analyse-Methodik

### Verwendete Tools:
- `ProductionOrderFlowAnalyzer` - Analysiert Message-Flows
- `StockManagementAnalyzer` - Analysiert Stock-Patterns
- Mermaid-Diagramme - Visualisierung der Flows

### Analysierte Sessions:
- `auftrag-rot_1.log` - Fischertechnik Dashboard Order
- `auftrag-rot-omf_ts.log` - OMF Dashboard Order

### Key Metrics:
- **Message Count**: ~1000+ Messages pro Session
- **OrderId Generation Time**: ~300ms nach Order Request
- **Stock Update Frequency**: Zyklisch alle 1-5 Sekunden

## 📊 Visualisierungen

### Erstellte Diagramme:
1. **Production Order Flow Schema** (`production-order-flow-schema.md`)
2. **OrderId Generation Flow** (`order-id-generation-flow.mermaid`)
3. **OrderId Generation Timeline** (`order-id-generation-timeline.mermaid`)
4. **Stock Management Flow** (`stock-management-flow.mermaid`)
5. **Stock Message Timeline** (`stock-message-timeline.mermaid`)

### Session Manager Integration:
- **Production Order Filter** - Filtert Messages nach `orderId`
- **Involved Topics Table** - Zeigt alle beteiligten Topics
- **Mermaid Diagram Export** - Download für externe Analyse

## 🚨 Offene Fragen

### 1. OrderId-Konflikte:
- Was passiert, wenn mehrere Orders gleichzeitig verarbeitet werden?
- Wie wird sichergestellt, dass `orderId` eindeutig sind?

### 2. Error Handling:
- Wie werden fehlgeschlagene Orders behandelt?
- Gibt es Retry-Mechanismen?

### 3. Performance:
- Wie skaliert das System bei vielen gleichzeitigen Orders?
- Gibt es Bottlenecks in der CCU?

### 4. Stock Consistency:
- Wie wird Stock-Konsistenz zwischen HBW und CCU sichergestellt?
- Was passiert bei Stock-Updates während Order-Processing?

## 🔗 Verwandte Dokumentation

- [Production Order Flow Schema](production-order-flow-schema.md)
- [Stock Management Analysis](stock-management-analysis.md)
- [OrderId Generation Flow](order-id-generation-flow.mermaid)
- [OrderId Generation Timeline](order-id-generation-timeline.mermaid)

## 📝 Nächste Schritte

### 1. Verifikation:
- [ ] Test mit verschiedenen Order-Typen (RED, WHITE, BLUE)
- [ ] Verifikation der Message-Chronologie
- [ ] Test der Error-Szenarien

### 2. Erweiterte Analyse:
- [ ] Performance-Analyse bei hoher Order-Last
- [ ] Stock-Consistency-Analyse
- [ ] Error-Pattern-Analyse

### 3. Dokumentation:
- [ ] API-Dokumentation der beteiligten Topics
- [ ] Error-Code-Dokumentation
- [ ] Performance-Benchmarks

---

**Erstellt**: 2025-01-15  
**Basierend auf**: Log-Analyse der Sessions `auftrag-rot_1.log` und `auftrag-rot-omf_ts.log`  
**Status**: Analyse abgeschlossen, Verifikation ausstehend
