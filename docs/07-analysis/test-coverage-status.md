# Test Coverage Status

**Letzte Aktualisierung:** 2026-08-06 (nach UC-Specs; `npm run test:coverage` = `--runInBand`)  
**Quelle:** `npm run test:coverage` → `coverage/osf-ui/index.html`  
**Tests:** 79 Suites passed / 2 skipped (Full-Suite runInBand)  
**Jest-Thresholds** (`osf/apps/osf-ui/jest.config.ts`): alle erfüllt (deutlich unter Ist)

---

## Aktuelle Test-Abdeckung (osf-ui)

| Metrik | Aktuell | Absolutzahlen | Jest-Threshold | Langziel | Status |
|--------|---------|---------------|----------------|----------|--------|
| **Lines** | **64.65 %** | 9240 / 14291 | 47 % ✅ | 60 %+ | Ziel erreicht (+4.65 %) |
| **Statements** | **63.55 %** | 9607 / 15117 | 46 % ✅ | ~60 % | Ziel erreicht |
| **Functions** | **59.65 %** | 1572 / 2635 | 42 % ✅ | ~60 % | Gap −0.35 % |
| **Branches** | **48.42 %** | 5479 / 11315 | 30 % ✅ | 40 %+ | Ziel erreicht (+8.42 %) |

Vergleich Sprint-27-Ende (vormittag): Lines 52.66 % → **64.65 %** (~+12 pp) durch Use-Case SVG/shared Specs.

---

## Hotspots (Lines, 2026-08-06 nachmittag)

| Bereich | Lines | Bemerkung |
|---------|-------|-----------|
| UC SVG-Generatoren (01–07) / Interop | ~72–92 % | neue Smokes |
| `use-case-step-apply` | **100 %** | |
| `use-case-controls` | **100 %** | |
| `base-use-case` | ~62 % | via Interoperability-Smoke |
| `three-data-pools` | ~41 % | Lanes-Pfad noch dünn |
| `track-trace` Use-Case-Shell | **0 %** | noch offen |
| DSP-/Customer-Pages | oft **0 %** | nächster optionaler Hebel |

---

## Verbleibende Lücke

### Lines / Statements — Langziel 60 %+
- **Erreicht** für Lines/Statements. Optional: Jest-Thresholds anheben (z. B. Lines 55–60), damit Regressionen greifen.

### Functions → 60 %
- Noch ~0.4 pp; UC-Shell Track&Trace / DSP-Pages oder Threshold-Puffer.

### Branches — Langziel 40 %+
- **Erreicht** (48.42 %). Threshold 30 % → schrittweise auf ~40–45.

---

## Nächste Schritte (optional)

1. Jest `coverageThreshold` an Ist-Stand annähern (Puffer lassen).
2. Rest-Gaps: Track&Trace-UC-Shell, UC-02 Lanes, DSP-Pages — nur bei Bedarf.
3. Coverage-Läufe: `npm run test:coverage` (enthält `--runInBand`).

---

## Historie (Phasen 1–4, bis 2025-11-30)

Archiv — siehe frühere Commits / [test-coverage-summary.md](test-coverage-summary.md).
