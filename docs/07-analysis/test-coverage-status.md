# Test Coverage Status

**Letzte Aktualisierung:** 2026-08-26 (Sprint 29, Coverage A DSP/Use-Case Smokes)  
**Quelle:** `npm run test:coverage` → `coverage/osf-ui/index.html`  
**Tests:** 87 Suites passed / 2 skipped · 1487 passed / 16 skipped  
**Jest-Thresholds:** branches **48**, functions **59**, lines **64**, statements **63** — alle erfüllt

---

## Aktuelle Test-Abdeckung (osf-ui)

| Metrik | Aktuell | Jest-Threshold | Langziel | Status |
|--------|---------|----------------|----------|--------|
| **Lines** | **70.56 %** | 64 % ✅ | 60 %+ | Ziel erreicht |
| **Statements** | **69.49 %** | 63 % ✅ | ~60 % | Ziel erreicht |
| **Functions** | **65.34 %** | 59 % ✅ | ~60 % | Ziel erreicht |
| **Branches** | **51.83 %** | 48 % ✅ | 40 %+ | Ziel erreicht |

Trend: Sprint-28-Ende **66.5 / 49.8 / 61.3 / 65.5** (L/B/F/S) → 24.08. **67.8 / 51.2 / 62.8 / 66.7** → 26.08. **68.26 / 51.69 / 63.34 / 67.15** → Coverage A **70.56 / 51.83 / 65.34 / 69.49**. Gates unverändert `48 / 59 / 64 / 63` (Margin ~5–6 pp).

---

## Hotspots (Lines)

| Bereich | Bemerkung |
|---------|-----------|
| `shopfloor-preview` | nach Tests ~78 % Lines; Rest vor allem Route/SVG-Zweige |
| `shopfloor-tab` / `agv-tab` | weiter große Dateien, Kernpfade besser abgedeckt |
| DSP-/Customer-Pages | nach Coverage A: `dsp-page` + Sections + UC-01/02/03/04/06/07 Smokes abgedeckt |

---

## Nächste Schritte (optional)

1. Weitere Shopfloor-/AGV-Zweige nur bei Bugfix/Feature.
2. DSP-Pages nur bei Bedarf.
3. Gates erneut anheben, wenn Ist-Margins wieder stabil >5 pp liegen.
