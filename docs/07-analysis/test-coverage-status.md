# Test Coverage Status

**Letzte Aktualisierung:** 2026-08-27 (Sprint 29, Coverage D Tab→Utils Extraktion)  
**Quelle:** `npm run test:coverage` → `coverage/osf-ui/index.html`  
**Tests:** 91 Suites passed / 2 skipped · 1532 passed / 16 skipped  
**Jest-Thresholds:** branches **48**, functions **59**, lines **64**, statements **63** — alle erfüllt

---

## Aktuelle Test-Abdeckung (osf-ui)

| Metrik | Aktuell | Jest-Threshold | Langziel | Status |
|--------|---------|----------------|----------|--------|
| **Lines** | **72.06 %** | 64 % ✅ | 60 %+ | Ziel erreicht |
| **Statements** | **70.96 %** | 63 % ✅ | ~60 % | Ziel erreicht |
| **Functions** | **66.76 %** | 59 % ✅ | ~60 % | Ziel erreicht |
| **Branches** | **54.79 %** | 48 % ✅ | 40 %+ | Ziel erreicht |

Trend: Sprint-28-Ende **66.5 / 49.8 / 61.3 / 65.5** (L/B/F/S) → 24.08. **67.8 / 51.2 / 62.8 / 66.7** → 26.08. **68.26 / 51.69 / 63.34 / 67.15** → A **70.56 / 51.83 / 65.34 / 69.49** → B **71.51 / 54.19 / 66.17 / 70.41** → C **71.98 / 54.59 / 66.70 / 70.87** → D **72.06 / 54.79 / 66.76 / 70.96**. Gates unverändert `48 / 59 / 64 / 63` (Margin ~6–7 pp).

---

## Hotspots (Lines)

| Bereich | Bemerkung |
|---------|-----------|
| `shopfloor-preview` | nach Coverage C: Highlight/Current-Position, Viewport-Emit, Follow-Scroll-Wiring |
| `shopfloor-tab` / `agv-tab` | Logik teilweise in `utils/` extrahiert (Message-Count, HBW-Stock, AGV-Route-Overlay) |
| DSP-/Customer-Pages | nach Coverage A: `dsp-page` + Sections + UC-01/02/03/04/06/07 Smokes abgedeckt |

---

## Nächste Schritte (optional)

1. Weitere Shopfloor-/AGV-Zweige nur bei Bugfix/Feature.
2. DSP-Pages nur bei Bedarf.
3. Gates erneut anheben, wenn Ist-Margins wieder stabil >5 pp liegen.
