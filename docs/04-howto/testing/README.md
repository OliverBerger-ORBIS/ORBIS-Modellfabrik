# Testing How-To Guides

**Zielgruppe:** Entwickler  
**Letzte Aktualisierung:** 2025-12-13

---

## 📚 Verfügbare Guides

### 1. [Testing Strategy](testing-strategy.md)
**Test-Philosophie und Best Practices**

- Test-First Development
- Test-Kategorien (Unit, Integration, E2E)
- Test-Ausführung
- Test-Policy für Produktionscode

### 2. [Coverage Monitoring](coverage-monitoring.md) ⭐ **NEU**
**Test Coverage Monitoring Setup**

- Coverage-Schwellenwerte konfigurieren
- Coverage Reports generieren
- CI/CD Integration
- Schrittweise Erhöhung der Schwellenwerte

**Status:** ✅ Aktiv seit 2025-12-13

### 3. [Integration Testing Workflow](integration-testing-workflow.md)
**Integration Tests für Component-Service Integration**

- Integration Test Patterns
- Component-Service Integration Tests
- Test-Setup für komplexe Komponenten

---

## 🚀 Quick Start

### Tests ausführen

```bash
# Alle Tests
npm test

# Nur ccu-ui Tests
npm run test:ccu-ui

# Mit Coverage Report
npm run test:coverage

# Coverage Check (mit Thresholds)
npm run test:coverage:check
```

### Coverage Report anzeigen

```bash
# Coverage Report generieren
npm run test:coverage

# HTML Report öffnen (macOS)
open coverage/ccu-ui/index.html
```

---

## 📊 Aktuelle Test-Coverage

**Stand:** 2025-12-13

| Metrik | Aktuell | Ziel | Status |
|--------|---------|------|--------|
| **Lines** | 29.09% | 60%+ | 🟡 48% erreicht |
| **Branches** | 16.34% | 40%+ | 🟡 41% erreicht |
| **Functions** | 23.65% | 60%+ | 🟡 39% erreicht |
| **Statements** | 28.39% | 60%+ | 🟡 47% erreicht |

**Test-Dateien:** 32 spec.ts Dateien von 71 TypeScript-Dateien (45%)

---

## 🎯 Test-Philosophie

### Test-First Development
1. **Implementierung** → Test → Fix → Test → Commit
2. **Nur bei 100% funktionierenden Features** committen
3. **Tests haben absolute Priorität vor Commits**

### KEINE COMMITS VOR TESTS
- **NIEMALS** Commits durchführen bevor alle Implementierungen vollständig getestet wurden
- Jede neue Funktionalität muss erst funktional getestet werden
- **UI-Tests** werden vom Benutzer durchgeführt

---

## 🔗 Verwandte Dokumentation

- [Test Coverage Plan](../../analysis/code-optimization-test-coverage-plan.md)
- [Test Coverage Status](../../analysis/test-coverage-status.md)
- [Test Coverage Summary](../../analysis/test-coverage-summary.md)

---

**Letzte Aktualisierung:** 2025-12-13
