# Test Coverage Monitoring

**Status:** ✅ Aktiv  
**Datum:** 2026-08-06  
**Ziel:** Automatisches Monitoring der Test-Abdeckung

---

## Übersicht

Das Coverage Monitoring System überwacht automatisch die Test-Abdeckung und stellt sicher, dass die Coverage-Schwellenwerte eingehalten werden.

**Ist-Stand (Messung 2026-08-24, `--runInBand`):** siehe [test-coverage-status.md](../../07-analysis/test-coverage-status.md) — Lines **67.8 %**, Branches **51.2 %**, Statements **66.7 %**, Functions **62.8 %**.

---

## Aktuelle Coverage-Schwellenwerte

**Konfiguration:** `osf/apps/osf-ui/jest.config.ts`

```typescript
coverageThreshold: {
  global: {
    branches: 48, // Ist 24.08.2026: 51.2%; ~3 pp Puffer
    functions: 59, // Ist: 62.8%
    lines: 64, // Ist: 67.8%
    statements: 63, // Ist: 66.7%
  },
}
```

**Hinweis:** Jest-Schwellen mit Puffer unter dem Ist-Stand. Coverage-Läufe standardmäßig mit **`--runInBand`**. Details: [test-coverage-status.md](../../07-analysis/test-coverage-status.md).

---

## Verwendung

### Coverage Report generieren

```bash
# Coverage Report mit HTML-Output (runInBand — Standard)
npm run test:coverage

# Coverage Report mit Threshold-Check (schlägt fehl wenn Thresholds nicht erreicht)
npm run test:coverage:check
```

**Warum `--runInBand`:** Ein Jest-Worker statt vieler paralleler — schonender für CPU/RAM, stabilere Hooks unter Last. Länger in der Wanduhr, dafür weniger Maschinenlast und weniger Flakes.

### Coverage Report anzeigen

Nach `npm run test:coverage`:
- **HTML Report:** `coverage/osf-ui/index.html`
- **JSON Report:** `coverage/osf-ui/coverage-final.json`
- **LCOV Report:** `coverage/osf-ui/lcov.info`

**HTML Report öffnen:**
```bash
# macOS
open coverage/osf-ui/index.html

# Linux
xdg-open coverage/osf-ui/index.html

# Windows
start coverage/osf-ui/index.html
```

---

## 📋 Coverage-Konfiguration

### Erfasste Dateien

**Included:**
- ✅ `src/app/**/*.ts` - Alle TypeScript-Dateien

**Excluded:**
- ❌ `src/app/**/*.spec.ts` - Test-Dateien
- ❌ `src/app/**/*.mock.ts` - Mock-Dateien
- ❌ `src/app/**/__tests__/**` - Test-Verzeichnisse
- ❌ `src/app/**/*.interface.ts` - Interfaces
- ❌ `src/app/**/*.type.ts` - Type-Definitionen
- ❌ `src/app/**/*.enum.ts` - Enums
- ❌ `src/app/**/index.ts` - Barrel-Exports
- ❌ `src/app/**/test-setup.ts` - Test-Setup
- ❌ `src/app/**/main.ts` - Entry Point

---

## 🔄 CI/CD Integration

### GitHub Actions

**Workflow:** `.github/workflows/ci.yml`

```yaml
- name: Test Coverage Check
  run: |
    npm run test:coverage:check || echo "⚠️ Coverage thresholds not met"
  continue-on-error: true

- name: Upload Coverage
  uses: codecov/codecov-action@v4
  if: always()
  continue-on-error: true
  with:
    files: |
      ./coverage/osf-ui/coverage-final.json
      ./coverage/mqtt-client/coverage-final.json
      ./coverage/gateway/coverage-final.json
      ./coverage/business/coverage-final.json
    flags: osf
    name: osf-coverage
    fail_ci_if_error: false
```

**Features:**
- ✅ Coverage Check in CI/CD
- ✅ Coverage Report Upload (Codecov)
- ✅ Non-blocking (warnet nur, blockiert nicht den Build)

### Codecov.io (Projekt-Einstellungen)

Im Repo liegt **keine** `codecov.yml` — Upload und **Flag** kommen nur aus dem Workflow (`flags: osf`, Upload-Name `osf-coverage`). Auf [codecov.io](https://app.codecov.io) beim passenden Repository prüfen:

- **Components / Flags:** Ob noch Filter oder Carryforward-Regeln auf das alte Flag **`omf3`** zeigen; ggf. auf **`osf`** umstellen oder Duplikate zusammenführen (ältere Uploads behalten historisch das Label `omf3`, neue Läufe liefern `osf`).
- **Secrets:** Bei privatem Repo oder Team-Features ggf. `CODECOV_TOKEN` unter GitHub → *Settings → Secrets*; der verwendete Workflow nutzt die Action Defaults, sobald das Repo bei Codecov verknüpft ist.

---

## 📈 Coverage-Schwellenwerte anpassen

### Schrittweise Erhöhung

Um die Schwellenwerte schrittweise zu erhöhen:

1. **Aktuelle Coverage messen:**
   ```bash
   npm run test:coverage
   ```

2. **Schwellenwerte in `jest.config.ts` anpassen:**
   ```typescript
   coverageThreshold: {
     global: {
       branches: 25,    // +1% Erhöhung
       functions: 41,   // +1% Erhöhung
       lines: 44,       // +1% Erhöhung
       statements: 44,  // +1% Erhöhung
     },
   },
   ```

3. **Testen:**
   ```bash
   npm run test:coverage:check
   ```

4. **Committen wenn erfolgreich**

### Zielwerte erreichen

**Langziel:** 60 % Lines, 40 % Branches (Branches bereits überschritten, Stand 2026-08-06)

**Empfohlene Strategie:**
- Thresholds schrittweise an den Ist-Stand heranziehen (+1–2 % Puffer unter Messung)
- Kernpfade (Services, Track & Trace, Shopfloor) priorisieren; UC/DSP-0 %-Pages bewusst entscheiden (testen vs. Scope)

---

## 🎯 Best Practices

### 1. Coverage vor jedem Commit prüfen

```bash
npm run test:coverage:check
```

### 2. Coverage Report regelmäßig prüfen

```bash
npm run test:coverage
open coverage/osf-ui/index.html
```

### 3. Uncovered Code identifizieren

Im HTML Report:
- **Rote Zeilen:** Nicht getestet
- **Gelbe Zeilen:** Teilweise getestet
- **Grüne Zeilen:** Vollständig getestet

### 4. Coverage-Schwellenwerte schrittweise erhöhen

- Nicht zu aggressiv erhöhen
- Realistische Ziele setzen
- Regelmäßig anpassen basierend auf Fortschritt

---

## 🔧 Troubleshooting

### Problem: Coverage Thresholds nicht erreicht

**Lösung:**
1. Coverage Report prüfen: `npm run test:coverage`
2. Uncovered Code identifizieren
3. Tests für uncovered Code hinzufügen
4. Oder: Schwellenwerte temporär anpassen (nur wenn nötig)

### Problem: Coverage Report nicht generiert

**Lösung:**
1. Prüfen ob Tests laufen: `npm test`
2. Prüfen ob `coverageDirectory` korrekt ist
3. Prüfen ob `collectCoverageFrom` korrekt konfiguriert ist

### Problem: CI/CD Coverage Check schlägt fehl

**Lösung:**
1. Lokal testen: `npm run test:coverage:check`
2. Coverage Report prüfen
3. Tests hinzufügen oder Schwellenwerte anpassen

---

## 📊 Coverage-Metriken

Aktuelle Zahlen und Gates: [test-coverage-status.md](../../07-analysis/test-coverage-status.md). Nicht hier duplizieren.

---

## 🔗 Verwandte Dokumentation

- [Test Coverage Status](../07-analysis/test-coverage-status.md)
- [Testing Strategy](testing-strategy.md)

---

**Letzte Aktualisierung:** 2026-08-24  
**Status:** ✅ Aktiv - Coverage Monitoring eingerichtet
