# Examples - Git References für Wiederherstellung

**Datum:** 2025-12-13  
**Status:** Examples gelöscht, aber in Git-Historie verfügbar

---

## 📋 Gelöschte Examples

Die folgenden Examples wurden gelöscht, da sie bereits in OMF3 integriert wurden oder veraltet sind:

1. ✅ `examples/shopfloor-angular/` - **Integriert in OMF3**
2. ✅ `examples/fts-analysis-angular/` - **Features integriert in OMF3**
3. ✅ `examples/shopfloor_test_app/` - **Veraltet (OMF2/Streamlit)**

---

## 🔄 Wiederherstellung aus Git

Falls die Examples wiederhergestellt werden müssen, können sie aus der Git-Historie wiederhergestellt werden:

### Shopfloor Angular Example

```bash
# Letzte bekannte Version wiederherstellen
git checkout <commit-hash> -- examples/shopfloor-angular/

# Oder spezifischen Commit auschecken
git show <commit-hash>:examples/shopfloor-angular/README.md
```

**Wichtige Commits:**
- `8826386` - Add FTS Analysis Angular example application
- `908b668` - feat(example): complete Angular Shopfloor example with all features tested
- `c465c6a` - refactor(example): adopt OMF3 shopfloor layout architecture
- `ea6b83d` - feat(example): add Angular Shopfloor example structure and components
- Suche mit: `git log --oneline --all -- examples/shopfloor-angular/`

**Features:**
- Shopfloor Layout mit JSON-Konfiguration
- ORBIS/DSP Special Cells
- Details Sidebar Component
- Incremental Phases Component
- Mock MQTT Service

**Integration Status:**
- ✅ Shopfloor-Preview in OMF3 integriert
- ⚠️ Details Sidebar: Nicht integriert (kann aus Git wiederhergestellt werden)
- ⚠️ Incremental Component: Nicht integriert (kann aus Git wiederhergestellt werden)

---

### FTS Analysis Angular Example

```bash
# Letzte bekannte Version wiederherstellen
git checkout <commit-hash> -- examples/fts-analysis-angular/

# Oder spezifischen Commit auschecken
git show <commit-hash>:examples/fts-analysis-angular/README.md
```

**Wichtige Commits:**
- `8826386` - Add FTS Analysis Angular example application with battery, route, loads and track-trace components
- `a258645` - feat: FTS Tab integration with route animation and I18n support
- `432c591` - Extract constants for station IDs, timing, and event types
- `3ba6658` - Add station-grouped manufacturing tasks in Track & Trace
- Suche mit: `git log --oneline --all -- examples/fts-analysis-angular/`

**Features:**
- FTS Battery Status Component
- FTS Status Component
- FTS Loads Component
- FTS Route Component
- Track & Trace Component
- FTS Mock Service

**Integration Status:**
- ✅ Track & Trace in OMF3 integriert (`track-trace.component.ts`)
- ✅ FTS Tab in OMF3 vorhanden (`fts-tab.component.ts`)
- ✅ Workpiece History Service in OMF3 (`workpiece-history.service.ts`)
- ⚠️ FTS Analysis Components: Teilweise integriert (kann aus Git wiederhergestellt werden)

---

### Shopfloor Test App (Streamlit)

```bash
# Letzte bekannte Version wiederherstellen
git checkout <commit-hash> -- examples/shopfloor_test_app/

# Oder spezifischen Commit auschecken
git show <commit-hash>:examples/shopfloor_test_app/README.md
```

**Wichtige Commits:**
- Suche mit: `git log --oneline --all -- examples/shopfloor_test_app/`
- **Hinweis:** Streamlit-basiert, OMF2-spezifisch, veraltet

**Hinweis:** Diese App war OMF2/Streamlit-basiert und ist veraltet. Die Funktionalität ist in OMF3 `shopfloor-preview` integriert.

---

## 🔍 Git-Historie durchsuchen

### Alle Commits zu Examples finden

```bash
# Alle Commits zu gelöschten Examples
git log --oneline --all -- examples/shopfloor-angular examples/fts-analysis-angular examples/shopfloor_test_app

# Detaillierte Historie
git log --all --stat -- examples/shopfloor-angular examples/fts-analysis-angular examples/shopfloor_test_app

# Letzte Änderungen
git log --oneline --all -10 -- examples/shopfloor-angular examples/fts-analysis-angular examples/shopfloor_test_app
```

### Spezifische Dateien wiederherstellen

```bash
# README wiederherstellen
git show <commit-hash>:examples/shopfloor-angular/README.md > examples/shopfloor-angular/README.md

# Komponente wiederherstellen
git show <commit-hash>:examples/shopfloor-angular/src/app/details-sidebar/details-sidebar.component.ts > examples/shopfloor-angular/src/app/details-sidebar/details-sidebar.component.ts

# Komplettes Verzeichnis wiederherstellen
git checkout <commit-hash> -- examples/shopfloor-angular/
```

---

## 📝 Warum wurden sie gelöscht?

### `examples/shopfloor-angular/`
- ✅ Shopfloor-Preview bereits in OMF3 integriert
- ✅ JSON Layout Format kompatibel
- ⚠️ Details Sidebar und Incremental Component nicht integriert (können bei Bedarf aus Git wiederhergestellt werden)

### `examples/fts-analysis-angular/`
- ✅ Track & Trace in OMF3 integriert
- ✅ FTS Tab in OMF3 vorhanden
- ✅ Workpiece History Service in OMF3 vorhanden
- ⚠️ Einzelne FTS Analysis Components können bei Bedarf aus Git wiederhergestellt werden

### `examples/shopfloor_test_app/`
- ❌ OMF2/Streamlit-basiert (veraltet)
- ✅ Funktionalität in OMF3 `shopfloor-preview` integriert

---

## 🎯 Empfehlung für zukünftige Integration

Falls Features aus den Examples benötigt werden:

1. **Details Sidebar** (`examples/shopfloor-angular/src/app/details-sidebar/`)
   - Aus Git wiederherstellen
   - In OMF3 `shopfloor-preview` integrieren

2. **Incremental Component** (`examples/shopfloor-angular/src/app/incremental/`)
   - Aus Git wiederherstellen
   - In OMF3 integrieren (z.B. in DSP Tab)

3. **FTS Analysis Components** (`examples/fts-analysis-angular/src/app/components/`)
   - Aus Git wiederherstellen
   - In OMF3 `fts-tab` integrieren

---

**Hinweis:** Alle Examples sind in der Git-Historie verfügbar und können jederzeit wiederhergestellt werden.
