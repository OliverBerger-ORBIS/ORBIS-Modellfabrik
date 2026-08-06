# Test Coverage Status

**Letzte Aktualisierung:** 2026-08-06 (Option D: Gates + Shopfloor/UC-Rest)  
**Quelle:** `npm run test:coverage` → `coverage/osf-ui/index.html`  
**Tests:** 81 Suites passed / 2 skipped · 1416 passed / 16 skipped  
**Jest-Thresholds:** branches **42**, functions **52**, lines **58**, statements **58** — alle erfüllt

---

## Aktuelle Test-Abdeckung (osf-ui)

| Metrik | Aktuell | Absolutzahlen | Jest-Threshold | Langziel | Status |
|--------|---------|---------------|----------------|----------|--------|
| **Lines** | **66.67 %** | 9528 / 14291 | 58 % ✅ | 60 %+ | Ziel erreicht |
| **Statements** | **65.58 %** | 9915 / 15117 | 58 % ✅ | ~60 % | Ziel erreicht |
| **Functions** | **61.25 %** | 1614 / 2635 | 52 % ✅ | ~60 % | Ziel erreicht |
| **Branches** | **49.75 %** | 5630 / 11315 | 42 % ✅ | 40 %+ | Ziel erreicht |

Trend heute: Sprint-27-Ende 52.66 % Lines → UC-Smokes 64.65 % → Option D **66.67 %**.

---

## Hotspots (Lines)

| Bereich | Lines | Bemerkung |
|---------|-------|-----------|
| `shopfloor-tab` | ~50 % | DPS/Preview-Helfer ergänzt (vorher ~43 %) |
| UC Track&Trace-Shell | **100 %** | |
| `three-data-pools` | ~84 % | inkl. Lanes-Generator |
| DSP-/Customer-Pages | oft **0 %** | optionaler Hebel |

---

## Nächste Schritte (optional)

1. Weitere Shopfloor-Zweige nur bei Bugfix/Feature.
2. DSP-Pages nur bei Bedarf.
3. Gates nur anheben, wenn Ist-Margins stabil >5 pp bleiben.
