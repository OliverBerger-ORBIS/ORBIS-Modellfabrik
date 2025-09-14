# Template Reference & Migration Mapping

Version: 1.0  
Last updated: 2025-01-15  
Author: OMF Development Team  

---

## 📋 Template Migration Overview

Dieses Dokument zeigt die vollständige Migration von den alten Templates zu den neuen Registry-Templates im "Code as Doc" Ansatz.

---

## 🔄 Migration Mapping

### Module Templates (PRIO 1-2)

| **Alte Templates** | **Neue Registry Templates** | **Status** | **Serial Numbers** |
|-------------------|---------------------------|------------|-------------------|
| `module/connection.yml` | `module.connection.hbw.yml`<br>`module.connection.mill.yml`<br>`module.connection.drill.yml`<br>`module.connection.dps.yml`<br>`module.connection.aiqs.yml` | ✅ **Aufgeteilt** | SVR3QA0022, SVR4H76449, SVR4H76450, SVR4H73275, SVR4H76530 |
| `module/order.yml` | `module.order.hbw.yml`<br>`module.order.mill.yml`<br>`module.order.drill.yml`<br>`module.order.dps.yml`<br>`module.order.aiqs.yml` | ✅ **Aufgeteilt** | SVR3QA0022, SVR4H76449, SVR4H76450, SVR4H73275, SVR4H76530 |
| `module/factsheet.yml` | `module.factsheet.hbw.yml`<br>`module.factsheet.mill.yml`<br>`module.factsheet.drill.yml`<br>`module.factsheet.dps.yml`<br>`module.factsheet.aiqs.yml` | ✅ **Aufgeteilt** | SVR3QA0022, SVR4H76449, SVR4H76450, SVR4H73275, SVR4H76530 |
| `ccu/control.yml` | `ccu.control.yml` | ✅ **Migriert** | - |

### State Templates (bereits vorhanden)

| **Alte Templates** | **Neue Registry Templates** | **Status** | **Serial Numbers** |
|-------------------|---------------------------|------------|-------------------|
| `module.state.hbw.yml` | `module.state.hbw.yml` | ✅ **Bereits vorhanden** | SVR3QA0022 |
| `module.state.drill.yml` | `module.state.drill.yml` | ✅ **Bereits vorhanden** | SVR4H76449 |
| `module.state.mill.yml` | `module.state.mill.yml` | ✅ **Bereits vorhanden** | SVR4H76450 |
| `module.state.dps.yml` | `module.state.dps.yml` | ✅ **Bereits vorhanden** | SVR4H73275 |
| `module.state.aiqs.yml` | `module.state.aiqs.yml` | ✅ **Bereits vorhanden** | SVR4H76530 |

### TXT Controller Templates (PRIO 3-5)

| **Alte Templates** | **Neue Registry Templates** | **Status** | **Controller ID** |
|-------------------|---------------------------|------------|------------------|
| `txt/order_input.yml` | `txt.controller1.order_input.yml` | ✅ **Migriert** | Controller #1 |
| `txt/stock_input.yml` | `txt.controller1.stock_input.yml` | ✅ **Migriert** | Controller #1 |
| `txt/function_input.yml` | `txt.controller1.function_input.bme680.yml`<br>`txt.controller1.function_input.broadcast.yml`<br>`txt.controller1.function_input.cam.yml`<br>`txt.controller1.function_input.ldr.yml` | ✅ **Aufgeteilt** | Controller #1 |
| `txt/function_output.yml` | `txt.controller1.function_output.broadcast.yml` | ✅ **Migriert** | Controller #1 |
| `txt/input.yml` | `txt.controller1.input.config_hbw.yml` | ✅ **Migriert** | Controller #1 |
| `txt/output.yml` | `txt.controller1.output.order.yml` | ✅ **Migriert** | Controller #1 |

### Node-RED Templates (PRIO 5)

| **Alte Templates** | **Neue Registry Templates** | **Status** | **Serial Numbers** |
|-------------------|---------------------------|------------|-------------------|
| `nodered/connection.yml` | `nodered.connection.dps.yml`<br>`nodered.connection.aiqs.yml` | ✅ **Aufgeteilt** | SVR4H73275, SVR4H76530 |
| `nodered/state.yml` | `nodered.state.dps.yml`<br>`nodered.state.aiqs.yml` | ✅ **Aufgeteilt** | SVR4H73275, SVR4H76530 |
| `nodered/factsheet.yml` | `nodered.factsheet.dps.yml`<br>`nodered.factsheet.aiqs.yml` | ✅ **Aufgeteilt** | SVR4H73275, SVR4H76530 |

### FTS Templates (PRIO 4)

| **Alte Templates** | **Neue Registry Templates** | **Status** | **FTS ID** |
|-------------------|---------------------------|------------|------------|
| `fts/order.yml` | `fts.order.yml` | ✅ **Migriert** | 5iO4 |
| `fts/state.yml` | `fts.state.yml` | ✅ **Migriert** | 5iO4 |
| `fts/connection.yml` | `fts.connection.yml` | ✅ **Migriert** | 5iO4 |
| `fts/factsheet.yml` | `fts.factsheet.yml` | ✅ **Migriert** | 5iO4 |

---

## 📊 Migration Statistics

- **Gesamt Templates**: 25 neue Registry-Templates
- **Aufgeteilte Templates**: 8 (von generisch zu modul-spezifisch)
- **Direkt migriert**: 17
- **Neue Namenskonvention**: 
  - `module.connection.{module}` statt `module.connection`
  - `txt.controller1.{function}.{sensor}` statt `txt/{function}`
  - `nodered.{type}.{module}` statt `nodered/{type}`

---

## 🔧 Topic Mapping Examples

### Module Topics
```yaml
# Alte Topics → Neue Template Keys
module/v1/ff/SVR3QA0022/connection → module.connection.hbw
module/v1/ff/SVR4H76449/state → module.state.drill
module/v1/ff/SVR4H73275/order → module.order.dps
```

### TXT Controller Topics
```yaml
# Alte Topics → Neue Template Keys
/j1/txt/1/f/i/order → txt.controller1.order_input
/j1/txt/1/i/bme680 → txt.controller1.function_input.bme680
/j1/txt/1/f/o/order → txt.controller1.output.order
```

### Node-RED Topics
```yaml
# Alte Topics → Neue Template Keys
module/v1/ff/NodeRed/SVR4H73275/connection → nodered.connection.dps
module/v1/ff/NodeRed/SVR4H76530/state → nodered.state.aiqs
```

### FTS Topics
```yaml
# Alte Topics → Neue Template Keys
fts/v1/ff/5iO4/connection → fts.connection
fts/v1/ff/5iO4/order → fts.order
```

---

## 🎯 Key Changes

### 1. Modul-spezifische Templates
- **Vorher**: Ein generisches `module.connection.yml` für alle Module
- **Nachher**: Spezifische Templates pro Modul mit eindeutigen Serial Numbers

### 2. Controller-spezifische Templates
- **Vorher**: Generische `txt/` Templates
- **Nachher**: `txt.controller1.*` Templates basierend auf Topic-Pattern

### 3. Topic-Mapping
- **Vorher**: Pattern-basierte Mappings
- **Nachher**: Exakte Mappings mit Fallback-Patterns

### 4. Validierung
- **Vorher**: Basis-Validierung
- **Nachher**: Erweiterte Validierung mit Range-Checks und Enum-Validierung

### 5. Registry-Struktur
- **Vorher**: Verstreute Template-Dateien
- **Nachher**: Zentralisierte Struktur in `registry/model/v1/templates/`

---

## 🔗 Related Documentation

- [Registry Model](../02-architecture/registry-model.md) - Registry-Prinzipien & Versionierung
- [System Context](../02-architecture/system-context.md) - Überblick über Hauptkomponenten
- [How-To: Add a New Module](../04-howto/add-a-new-module.md) - Template → Mapping → Tests

---

**"Alle alten Templates sind erfolgreich in das neue Registry-System migriert!"** 🎉
