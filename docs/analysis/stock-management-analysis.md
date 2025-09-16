# Lagerbestand-Management Analyse

> ⚠️ **VERIFIKATION AUSSTEHEND**: Diese Analyse basiert auf einer Session-Datei und wurde noch nicht vollständig verifiziert. Die beschriebenen Patterns und Message-Flows müssen noch in verschiedenen Szenarien getestet werden.

## 🎯 Forschungsfrage

**Wie funktioniert das Lagerbestand-Management im APS-System?**
- Wird das HBW abgefragt oder sendet es zyklisch Updates?
- Wie wird sichergestellt, dass nur bei verfügbarer Roh-Ware Aufträge erstellt werden?

## 📊 Analyse-Ergebnisse

### **Antwort: Zyklisches PUSH-Pattern**

Das APS-System verwendet **kein Pull-Pattern** (Abfragen), sondern ein **PUSH-Pattern** (zyklische Updates):

1. **HBW sendet zyklisch** den kompletten Lagerbestand
2. **CCU aggregiert** und verteilt die Daten zentral
3. **Alle Systeme** haben Zugriff auf den aktuellen Bestand
4. **State-Änderungen** werden sofort propagiert

### **Message-Flow Pattern**

```
HBW Module → TXT Controller → CCU → Alle Systeme
     ↓              ↓          ↓         ↓
  Stock Data   Factory Input  Central   Dashboard
  (Sensors)    (Aggregation)  State     (Display)
```

## 🔍 Beweise aus der Session-Datei

### **1. HBW Stock Updates (Factory Input)**
- **Topic:** `/j1/txt/1/f/i/stock`
- **Zeitstempel:** `2025-08-19T09:13:34.583Z` → `2025-08-19T09:16:14.686Z`
- **Inhalt:** Vollständiger Lagerbestand mit allen Positionen (A1-C3)

### **2. CCU Stock Aggregation (Central State)**
- **Topic:** `ccu/state/stock`
- **Zeitstempel:** Identisch mit HBW-Update
- **Inhalt:** Gleiche Stock-Daten, aber zentral verfügbar

### **3. Keine Abfrage-Messages gefunden**
- ❌ Kein `ccu/stock/request`
- ❌ Kein `module/v1/ff/SVR3QA0022/stock/request`
- ❌ Kein Pull-Pattern erkennbar

## 📈 Stock-Data Struktur

### **Initial State (vor Order)**
```json
{
  "ts": "2025-08-19T09:13:34.583Z",
  "stockItems": [
    {"workpiece": {"id": "040a8dca341291", "type": "RED", "state": "RAW"}, "location": "A1"},
    {"workpiece": {"id": "04798eca341290", "type": "WHITE", "state": "RAW"}, "location": "B1"},
    {"workpiece": {"id": "047389ca341291", "type": "BLUE", "state": "RAW"}, "location": "C1"}
  ]
}
```

### **After Order (nach Order)**
```json
{
  "ts": "2025-08-19T09:16:14.686Z",
  "stockItems": [
    {"workpiece": {"id": "040a8dca341291", "type": "RED", "state": "RESERVED"}, "location": "A1"}
  ]
}
```

## 🏗️ System-Architektur

### **Komponenten**
- **HBW Module (SVR3QA0022):** Physischer Lagerbestand
- **TXT Controller (/j1/txt/1):** Factory-Level Aggregation
- **CCU:** Zentrale State-Verwaltung
- **Dashboard:** Visualisierung und Monitoring

### **Message-Topics**
- **Factory Input:** `/j1/txt/1/f/i/stock`
- **Central State:** `ccu/state/stock`
- **Module State:** `module/v1/ff/SVR3QA0022/state`

## 🎯 Vorteile des PUSH-Patterns

1. **Echtzeit-Updates:** Sofortige Verfügbarkeit von Stock-Änderungen
2. **Zentrale Verfügbarkeit:** Alle Systeme haben Zugriff auf aktuellen Bestand
3. **Einfache Architektur:** Keine komplexen Abfrage-Logiken
4. **Zuverlässigkeit:** Weniger Network-Traffic, weniger Fehlerquellen

## 🔗 Verwandte Dokumentation

- [APS Data Flow](../02-architecture/aps-data-flow.md)
- [System Context](../02-architecture/system-context.md)
- [Message Flow](../02-architecture/message-flow.md)
- [Registry Model](../02-architecture/registry-model.md)

## 📝 Fazit

Das APS-System verwendet ein **zyklisches PUSH-Pattern** für das Lagerbestand-Management. Das HBW-Modul sendet kontinuierlich Stock-Updates an den TXT-Controller, der diese an die CCU weiterleitet. Die CCU macht den aktuellen Bestand zentral verfügbar, sodass alle Systeme (inklusive Order-Management) auf die aktuellen Lagerdaten zugreifen können.

**Keine Abfragen erforderlich** - das System ist **reaktiv** und **proaktiv** informiert.
