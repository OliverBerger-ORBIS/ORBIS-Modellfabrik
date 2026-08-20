# Test Coverage Status

**Letzte Aktualisierung:** 2026-08-20 (Sprint-28-Endmessung)  
**Quelle:** `npm run test:coverage` → `coverage/osf-ui/index.html`  
**Tests:** 82 Suites passed / 2 skipped · 1425 passed / 16 skipped  
**Jest-Thresholds:** branches **42**, functions **52**, lines **58**, statements **58** — alle erfüllt

---

## Aktuelle Test-Abdeckung (osf-ui)

| Metrik | Aktuell | Jest-Threshold | Langziel | Status |
|--------|---------|----------------|----------|--------|
| **Lines** | **66.5 %** | 58 % ✅ | 60 %+ | Ziel erreicht |
| **Statements** | **65.5 %** | 58 % ✅ | ~60 % | Ziel erreicht |
| **Functions** | **61.3 %** | 52 % ✅ | ~60 % | Ziel erreicht |
| **Branches** | **49.8 %** | 42 % ✅ | 40 %+ | Ziel erreicht |

Trend: Sprint-27-Ende 52.66 % Lines → Option D (06.08.) **66.67 %** → Sprint-28-Ende (20.08.) **66.5 %** (praktisch flat; Gates unverändert).

---

## Hotspots (Lines)

| Bereich | Bemerkung |
|---------|-----------|
| `shopfloor-tab` / `shopfloor-preview` | weiter größter Hebel |
| `agv-tab` / `workpiece-history` | große Restzweige |
| DSP-/Customer-Pages | oft niedrig / 0 % — optional |

---

## Nächste Schritte (optional)

1. Weitere Shopfloor-/AGV-Zweige nur bei Bugfix/Feature.
2. DSP-Pages nur bei Bedarf.
3. Gates nur anheben, wenn Ist-Margins stabil >5 pp bleiben (aktuell ok; Bump bewusst nicht vor Sprintwechsel).
