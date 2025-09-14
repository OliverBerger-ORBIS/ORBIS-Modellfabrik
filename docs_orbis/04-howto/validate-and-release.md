# Validate and Release - Registry Workflow

## 🚀 Make-Befehle für Registry-Validierung

### Basis-Validierung
```bash
# Alle Registry-Checks ausführen
make validate-registry

# Einzelne Checks
make validate-mapping          # Topic-Template-Mappings prüfen
make check-mapping-collisions  # Duplikate vermeiden
make check-templates-no-topics # Topic-freie Templates prüfen
```

### Template-Validierung
```bash
# Template gegen Schema validieren
make validate-templates

# Spezifisches Template testen
make render-template TOPIC="module/v1/ff/SVR4H76449/state"
# Erwarteter Output: "module.state.drill"
```

### Collision-Detection
```bash
# Prüft auf doppelte Topic-Mappings
make check-mapping-collisions

# Beispiel-Output:
# ✅ No mapping collisions found
# ❌ Collision: module/v1/ff/SVR4H76449/state mapped to both:
#    - module.state.drill (exact)
#    - module.state (pattern)
```

## 📋 Release-Workflow

### 1. Pre-Release-Validierung
```bash
# Vollständige Validierung vor Release
make validate-all

# Inkludiert:
# - Registry-Schema-Validierung
# - Mapping-Collision-Check
# - Template-Topic-Check
# - JSON-Schema-Validierung
```

### 2. Registry-Version bumpen
```yaml
# registry/model/v1/manifest.yml
version: 1.2.0
model_version: "1.2"
last_updated: "2025-01-15"
compatibility:
  min_omf_version: "3.3.0"
  breaking_changes: []
```

### 3. CHANGELOG aktualisieren
```markdown
# registry/CHANGELOG.md
## [1.2.0] - 2025-01-15

### Added
- module.connection.* templates für alle Module
- module.order.* templates für DRILL, MILL, AIQS

### Changed
- Registry-Model erweitert um Connection-Templates

### Breaking Changes
- Keine (Minor-Release)
```

### 4. Git-Tag erstellen
```bash
# Registry-Version taggen
git tag registry-v1.2.0
git push origin registry-v1.2.0

# OMF-Dashboard prüft Kompatibilität
git tag omf-v3.3.1
git push origin omf-v3.3.1
```

## 🔍 Validierung im Detail

### Mapping-Validierung
```bash
make validate-mapping
```

**Prüft:**
- Alle Topics haben gültige Template-Referenzen
- Template-Keys existieren in Registry
- Direction ist korrekt (inbound/outbound/bidirectional)
- Pattern-Syntax ist gültig

### Template-Validierung
```bash
make validate-templates
```

**Prüft:**
- YAML-Syntax ist gültig
- Required-Felder sind definiert
- Examples entsprechen Structure
- Validation-Rules sind konsistent

### Collision-Check
```bash
make check-mapping-collisions
```

**Prüft:**
- Kein Topic wird mehrfach gemappt
- Exact-Mappings haben Priorität vor Patterns
- Pattern-Konflikte werden erkannt

## 🚨 Fehlerbehandlung

### Registry-Version-Mismatch
```python
# OMF Dashboard zeigt Fehler
def check_registry_compatibility():
    registry_version = load_manifest()["model_version"]
    if not is_compatible(registry_version, OMF_VERSION):
        st.error("""
        Registry Version Mismatch!
        
        Registry: {registry_version}
        OMF: {omf_version}
        
        See: docs_orbis/04-howto/validate-and-release.md
        """)
```

### Template-Validierungsfehler
```bash
# Beispiel-Fehler-Output
❌ Template validation failed:
   - module.state.drill.yml: Missing required field 'structure'
   - ccu.state.pairing.yml: Invalid enum value 'INVALID' in connectionState
```

### Mapping-Collision-Fehler
```bash
❌ Mapping collision detected:
   Topic: module/v1/ff/SVR4H76449/state
   Mapped to:
     - module.state.drill (exact mapping)
     - module.state (pattern mapping)
   
   Solution: Remove pattern mapping or make it more specific
```

## 🔧 CI/CD-Integration

### Pre-commit Hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
make validate-registry
if [ $? -ne 0 ]; then
    echo "❌ Registry validation failed"
    exit 1
fi
```

### GitHub Actions
```yaml
# .github/workflows/registry-validation.yml
name: Registry Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Registry
        run: make validate-all
```

## 📊 Release-Checkliste

### Vor jedem Release
- [ ] `make validate-all` erfolgreich
- [ ] `make check-mapping-collisions` erfolgreich
- [ ] Alle Tests bestehen (`make test`)
- [ ] CHANGELOG.md aktualisiert
- [ ] manifest.yml version gebumpt

### Nach jedem Release
- [ ] Git-Tag erstellt (`registry-v1.2.0`)
- [ ] OMF-Dashboard Kompatibilität getestet
- [ ] Dokumentation aktualisiert
- [ ] Team über Breaking Changes informiert

## 🎯 Best Practices

### Template-Entwicklung
1. **Immer topic-frei** - Keine Topic-Strings in Templates
2. **Semantische Keys** - `domain.object.variant` Schema
3. **Vollständige Examples** - Alle Felder mit realistischen Werten
4. **Validation-Rules** - Required fields und Enums definieren

### Mapping-Entwicklung
1. **Exact vor Pattern** - Spezifische Mappings zuerst
2. **Collision-Check** - Vor jedem Commit prüfen
3. **Direction korrekt** - inbound/outbound/bidirectional
4. **Friendly Names** - Für UI-Darstellung

### Release-Management
1. **Semantische Versionierung** - Major.Minor.Patch
2. **Breaking Changes** - Dokumentieren und kommunizieren
3. **Kompatibilität** - OMF-Dashboard prüft Registry-Version
4. **Rollback-Plan** - Bei Problemen schnell zurück

---

**"Validierung ist der Schlüssel zu stabilen Releases - Automatisierung verhindert menschliche Fehler."**
