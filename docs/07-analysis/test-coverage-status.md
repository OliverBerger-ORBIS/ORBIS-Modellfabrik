# Test Coverage Status

**Letzte Aktualisierung:** 2026-08-06  
**Quelle:** `npm run test:coverage` → `coverage/osf-ui/index.html`  
**Tests:** 1388 passed, 16 skipped (69 Suites, 2 skipped)  
**Jest-Thresholds** (`osf/apps/osf-ui/jest.config.ts`): alle erfüllt

---

## Aktuelle Test-Abdeckung (osf-ui)

| Metrik | Aktuell | Absolutzahlen | Jest-Threshold | Langziel | Status |
|--------|---------|---------------|----------------|----------|--------|
| **Lines** | **52.66 %** | 7527 / 14291 | 47 % ✅ | 60 %+ | Gap −7.34 % |
| **Statements** | **51.78 %** | 7829 / 15117 | 46 % ✅ | ~60 % | Gap −8.22 % |
| **Functions** | **52.82 %** | 1392 / 2635 | 42 % ✅ | ~60 % | Gap −7.18 % |
| **Branches** | **46.42 %** | 5253 / 11315 | 30 % ✅ | 40 %+ | Ziel erreicht (+6.42 %) |

Vergleich zur letzten Doku (2025-11-30): Lines ~+8.8 pp, Branches ~+22.4 pp.

---

## Hotspots (Lines, 2026-08-06)

| Bereich | Lines | Bemerkung |
|---------|-------|-----------|
| `app/services` | ~80 % | stark abgedeckt |
| `workpiece-history.service` | ~81 % | Track & Trace Kernlogik |
| `track-trace.component` | ~75 % | UI-Komponente |
| `app/tabs` | ~59 % | gemischt |
| `shopfloor-preview` | ~55 % | |
| Use-Case-Pages / viele DSP-SVG-Pages | oft **0 %** | ziehen den Globalwert spürbar runter |

---

## Verbleibende Lücke zum Langziel

### Lines / Statements / Functions → 60 %
- Größter Hebel: bisher ungetestete Use-Case- und DSP-Pages (viele Dateien bei 0 % Lines).
- Alternativ: Thresholds und Langziel für „Marketing/SVG-Pages“ von Kern-Shopfloor trennen (Coverage-Scope), statt alles auf 60 % zu pushen.

### Branches → 40 %+
- **Erreicht** (46.42 %). Nächster sinnvoller Schritt: Jest-Threshold von 30 % schrittweise anheben (z. B. 40–45 %), damit Regressionen greifen.

---

## Nächste Schritte (Empfehlung für Sprint 28+)

1. **Thresholds nachziehen** – Jest `coverageThreshold` an den Ist-Stand annähern (z. B. Lines 50, Branches 40), ohne den Build unnötig fragil zu machen.
2. **Kernpfade halten** – Track & Trace / Services / Shopfloor nicht unter die heutigen Hotspot-Werte fallen lassen.
3. **Optional Coverage heben** – gezielte Specs für ungetestete UC-/DSP-Pages **oder** `collectCoverageFrom`-Ausschluss für reine Präsentationsseiten (Entscheidung nötig).

---

## Historie (Phasen 1–4, bis 2025-11-30)

Archiv – Ausgangslage der früheren Coverage-Kampagne; Zahlen unten sind **nicht** der aktuelle Stand.

### Abgeschlossene Phasen
- **Phase 1:** Memory Leaks / Build Issues
- **Phase 2:** Service-, View- und Tab-Tests
- **Phase 3:** MessageMonitor-Refactor, Fixtures aus Production, Lazy Loading
- **Phase 4:** Edge Cases + Integration Tests (~134 Edge-Case-Tests)

### Stand damals (2025-11-30)
| Metrik | Wert |
|--------|------|
| Lines | 43.84 % |
| Branches | 24.04 % |
| Statements | 43.88 % |
| Functions | 40.81 % |
