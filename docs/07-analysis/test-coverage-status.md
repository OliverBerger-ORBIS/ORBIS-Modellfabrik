# Test Coverage Status

**Letzte Aktualisierung:** 2026-08-24 (Sprint 29, Gate-Bump + Shopfloor-Tests)  
**Quelle:** `npm run test:coverage` → `coverage/osf-ui/index.html`  
**Tests:** 84 Suites passed / 2 skipped · 1451 passed / 16 skipped  
**Jest-Thresholds:** branches **48**, functions **59**, lines **64**, statements **63** — alle erfüllt

---

## Aktuelle Test-Abdeckung (osf-ui)

| Metrik | Aktuell | Jest-Threshold | Langziel | Status |
|--------|---------|----------------|----------|--------|
| **Lines** | **67.8 %** | 64 % ✅ | 60 %+ | Ziel erreicht |
| **Statements** | **66.7 %** | 63 % ✅ | ~60 % | Ziel erreicht |
| **Functions** | **62.8 %** | 59 % ✅ | ~60 % | Ziel erreicht |
| **Branches** | **51.2 %** | 48 % ✅ | 40 %+ | Ziel erreicht |

Trend: Sprint-28-Ende **66.5 / 49.8 / 61.3 / 65.5** (L/B/F/S) → 24.08. **67.8 / 51.2 / 62.8 / 66.7**. Gates von `42 / 52 / 58 / 58` auf `48 / 59 / 64 / 63`.

---

## Hotspots (Lines)

| Bereich | Bemerkung |
|---------|-----------|
| `shopfloor-preview` | nach Tests ~78 % Lines; Rest vor allem Route/SVG-Zweige |
| `shopfloor-tab` / `agv-tab` | weiter große Dateien, Kernpfade besser abgedeckt |
| DSP-/Customer-Pages | oft niedrig / 0 % — optional |

---

## Nächste Schritte (optional)

1. Weitere Shopfloor-/AGV-Zweige nur bei Bugfix/Feature.
2. DSP-Pages nur bei Bedarf.
3. Gates erneut anheben, wenn Ist-Margins wieder stabil >5 pp liegen.
