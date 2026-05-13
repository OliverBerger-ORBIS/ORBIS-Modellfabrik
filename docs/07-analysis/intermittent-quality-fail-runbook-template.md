# Intermittent Quality-Fail Runbook Template

Stand: 2026-05-13

Purpose: Document timing-sensitive standstill behavior without claiming strict causality.  
Use this template when `CHECK_QUALITY=FAILED` correlates with partial flow stop in parallel orders.

---

## 1) Run Matrix (1 row per session)

| Run | Session | Chain | RED NOK | Outcome | Manual recovery needed | Notes |
|-----|---------|-------|---------|---------|------------------------|-------|
| R1 | `<session-name>` | `<A|B|C|none>` | `<yes/no>` | `<ok/stall>` | `<none / AGV->HBW / clearLoadHandler / both>` | `<short context>` |
| R2 | `<session-name>` | `<A|B|C|none>` | `<yes/no>` | `<ok/stall>` | `<...>` | `<...>` |
| R3 | `<session-name>` | `<A|B|C|none>` | `<yes/no>` | `<ok/stall>` | `<...>` | `<...>` |
| R4 | `<session-name>` | `<A|B|C|none>` | `<yes/no>` | `<ok/stall>` | `<...>` | `<...>` |

---

## 2) Event Signature (minimal, stable markers)

Document only the critical markers and relative timing windows:

1. `CHECK_QUALITY` result (`PASSED` / `FAILED`) at AIQS
2. `ccu/order/cancel` observed (`yes/no`)
3. FTS state indicates standstill (`waitingForLoadHandling=true`, blocked module, no progress)
4. Expected follow-up missing (e.g. no `DROP FINISHED` within window)
5. Manual recovery command(s) and effect

Recommended format:

| Marker | Timestamp | Delta to FAIL | Observed value | Comment |
|--------|-----------|---------------|----------------|---------|
| Quality fail | `<ts>` | `0s` | `FAILED` | AIQS order `<id>` |
| Cancel publish | `<ts>` | `+<n>s` | `<topic/payload summary>` | optional |
| FTS blocked | `<ts>` | `+<n>s` | `<state summary>` | module/fts serial |
| Recovery sent | `<ts>` | `+<n>s` | `<AGV->HBW / clearLoadHandler>` | |
| Recovery effect | `<ts>` | `+<n>s` | `<flow resumed / still blocked>` | |

---

## 3) Hypothesis Log (no hard causality)

| Hypothesis | Evidence | Counter-evidence | Confidence |
|------------|----------|------------------|------------|
| `<e.g. cancel timing can deadlock parallel flow>` | `<1/4 stalls, signature overlap>` | `<3/4 completed with same business scenario>` | `<low/medium/high>` |
| `<e.g. non-deterministic clear target affects recovery>` | `<different target modules in logs>` | `<manual HBW clear often works>` | `<low/medium/high>` |

Rules:
- Always state frequency (`x/y runs`).
- Distinguish *observed* vs *inferred*.
- Keep confidence conservative for intermittent cases.

---

## 4) Track&Trace Linkage

For each run, link storage and production context:
- `trackTraceChain` from session meta (`A/B/C`)
- workpiece IDs / NFC IDs sampled at storage and downstream module
- explicit note if IDs are continuous across session boundaries

---

## 5) Reproduction Envelope

Capture only factors that may alter timing/interleaving:
- active AGVs and initial positions
- order submission pattern (single vs burst, spacing)
- retained/no_retained profile
- sensor/cam topic load profile (`fulltopics` vs `no_cam`)
- recovery commands used

---

## 6) Exit Criteria for CCU Fix Validation

A candidate fix is considered stable when:
- no unresolved standstill in at least `N>=10` comparable runs
- `CHECK_QUALITY=FAILED` no longer blocks unrelated parallel orders
- no manual recovery (`AGV->HBW`, `clearLoadHandler`) required in nominal test set
- run matrix and event signatures show no regression in throughput
