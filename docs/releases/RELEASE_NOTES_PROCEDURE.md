# Release Notes Verfahren

## 📋 Einheitliches Format

### **Dateiname-Konvention:**
```
dashboardvX.Y.Z-release-notes.md
```

**Beispiele:**
- `dashboardv3.4.0-release-notes.md`
- `dashboardv3.3.1-release-notes.md`
- `dashboardv3.2.0-release-notes.md`

### **Header-Format:**
```markdown
# OMF Dashboard vX.Y.Z - Release Notes

**Datum:** DD. Monat YYYY  
**Version:** X.Y.Z  
**Codename:** "Kurze Beschreibung"  
**Status:** ✅ Released / 🚧 In Development / 🚨 Critical Fix
```

## 🔄 Standardisierte Sektionen

### **1. Obligatorische Sektionen:**
- 🎯 **Übersicht** - Kurze Beschreibung der wichtigsten Änderungen
- ✨ **Neue Features** - Neue Funktionalitäten
- 🐛 **Bug Fixes** - Behobene Probleme
- 🧪 **Testing & Quality Assurance** - Tests und Qualitätssicherung

### **2. Optionale Sektionen:**
- 🔄 **Verbesserungen** - Performance, UI/UX Verbesserungen
- 📚 **Dokumentation** - Neue/aktualisierte Dokumentation
- 🚀 **Deployment** - Installation und Konfiguration
- 🎯 **Nächste Schritte** - Geplante Features und bekannte Issues
- 📊 **Technische Details** - Architektur, API, Dependencies

## 📝 Schreibregeln

### **Emojis verwenden:**
- 🎯 Übersicht
- ✨ Neue Features
- 🐛 Bug Fixes
- 🔄 Verbesserungen
- 🧪 Testing
- 📚 Dokumentation
- 🚀 Deployment
- 🎯 Nächste Schritte
- 📊 Technische Details

### **Status-Indikatoren:**
- ✅ **Released** - Version ist veröffentlicht
- 🚧 **In Development** - Version wird entwickelt
- 🚨 **Critical Fix** - Kritische Bug-Fix Version

### **Prioritäts-Indikatoren:**
- 🚨 **Critical** - Kritische Probleme
- ⚠️ **Important** - Wichtige Probleme
- 🔧 **Minor** - Kleinere Probleme

## 🔄 Migration bestehender Release-Notes

### **Zu migrieren:**
1. `dashboardv3.3.0-release-notes.md` ✅ (bereits korrekt)
2. `dashboardv3.2.0-release-notes.md` 🔄 (Header anpassen)
3. `release-notes-dashboardv3.1.2.md` 🔄 (Dateiname + Header)

### **Neue Dateinamen:**
- `release-notes-dashboardv3.1.2.md` → `dashboardv3.1.2-release-notes.md`

## 🔄 Automatische Release-Notes Updates

### **Regel: Release-Notes bei Dashboard-Änderungen aktualisieren**

**Wann Release-Notes aktualisiert werden müssen:**
- ✅ **Neue Features** hinzugefügt
- ✅ **Bug Fixes** implementiert
- ✅ **UI/UX Änderungen** vorgenommen
- ✅ **Performance-Verbesserungen** gemacht
- ✅ **Breaking Changes** eingeführt
- ✅ **Dependencies** aktualisiert
- ✅ **Konfiguration** geändert

**Wann Release-Notes NICHT aktualisiert werden müssen:**
- ❌ **Nur Dokumentation** geändert
- ❌ **Nur Tests** hinzugefügt
- ❌ **Nur Kommentare** geändert
- ❌ **Nur Code-Formatierung** (Black, Isort)

### **Workflow:**
1. **Dashboard-Änderung** vornehmen
2. **Release-Notes prüfen** - ist eine neue Version nötig?
3. **Version erhöhen** (Patch: 3.3.0 → 3.3.1, Minor: 3.3.0 → 3.4.0, Major: 3.3.0 → 4.0.0)
4. **Release-Notes aktualisieren** mit den Änderungen
5. **Status** entsprechend setzen (🚧 In Development → ✅ Released)

## 📋 Checkliste für neue Release-Notes

- [ ] Dateiname folgt Konvention `dashboardvX.Y.Z-release-notes.md`
- [ ] Header enthält alle obligatorischen Felder
- [ ] Emojis werden konsistent verwendet
- [ ] Status-Indikator ist korrekt gesetzt
- [ ] Alle relevanten Sektionen sind ausgefüllt
- [ ] Code-Blöcke sind korrekt formatiert
- [ ] Links funktionieren
- [ ] Datum ist korrekt
- [ ] **Alle Dashboard-Änderungen** sind dokumentiert
- [ ] **Version** ist korrekt erhöht
