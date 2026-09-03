# Test Coverage Status

**Letzte Aktualisierung:** 2026-09-03 (Sprint 29 Ende / Sprint 30 Baseline)  
**Quelle:** `npm run test:coverage` → `coverage/osf-ui/index.html`  
**Tests:** 92 Suites passed / 2 skipped · 1548 passed / 16 skipped  
**Jest-Thresholds:** branches **48**, functions **59**, lines **64**, statements **63** — alle erfüllt

---

## Aktuelle Test-Abdeckung (osf-ui)

| Metrik | Aktuell | Jest-Threshold | Langziel | Status |
|--------|---------|----------------|----------|--------|
| **Lines** | **71.97 %** | 64 % ✅ | 60 %+ | Ziel erreicht |
| **Statements** | **70.89 %** | 63 % ✅ | ~60 % | Ziel erreicht |
| **Functions** | **66.87 %** | 59 % ✅ | ~60 % | Ziel erreicht |
| **Branches** | **54.77 %** | 48 % ✅ | 40 %+ | Ziel erreicht |

Trend: Sprint-28-Ende **66.5 / 49.8 / 61.3 / 65.5** (L/B/F/S) → 27.08. Coverage D **72.06 / 54.79 / 66.76 / 70.96** → **Sprint-29-Ende 03.09.** **71.97 / 54.77 / 66.87 / 70.89** (flat; Dual-AGV-Code + Specs Language/NFC-first). Gates unverändert `48 / 59 / 64 / 63` (Margin ~7 pp).

---

## Hotspots (Lines)

| Bereich | Bemerkung |
|---------|-----------|
| `shopfloor-tab` / `agv-tab` / `shopfloor-preview` | weiter größte absolute Gaps |
| DSP-/UC SVG-Generatoren | oft 0 % — nur bei Bedarf |
| `workpiece-history` / `track-trace` | Dual-AGV Serial-/NFC-first Specs ergänzt (03.09.) |

---

## Nächste Schritte (optional)

1. Weitere Shopfloor-/AGV-Zweige nur bei Bugfix/Feature.
2. Gates erneut anheben, wenn Ist-Margins stabil >8 pp liegen.
3. Sprint 30: T&T Language-Reload-Lösung (Live) — Tests mitziehen.
