# Shopfloor route & AGV overlay – visual gate (mandatory)

**Audience:** Developers and AI agents working on `app-shopfloor-preview` and related tabs.

## Rule

**Any change** that affects **route rendering** (orange line segments, trim/inset behaviour), **stacking / z-index** of route vs modules vs FTS icons, or **AGV overlay** appearance **must not be merged** until a **successful manual visual check** has been done on a running UI (localhost or agreed target).

Automated unit tests and lint **do not** replace this check: SVG/CSS regressions can leave routes **invisible** while tests still pass.

## Minimum visual checklist (before merge)

Run the OSF UI in **mock** mode with fixtures:

1. **Order tab – route visible**  
   - Fixture: **White Step-3** (`order-white-step3` / `white_step3`).  
   - Expect: **Orange** route line for the active **NAVIGATION** step (e.g. HBW → DRILL), with shortened ends (not full cell depth).  
   - Expect: Active step highlight (green) on modules as designed (DR-24).

2. **AGV tab – route visible**  
   - Load a fixture where the FTS shows a **driving** route (segments from MQTT / replay).  
   - Expect: **Same** orange route lines visible; FTS icons sit **above** the shopfloor cells, not hidden behind them.

3. **Optional (RPi / demo):** Repeat on the **Raspberry Pi** deployment if the change touches paths that differ from dev (base href, asset loading).

If any item **fails**, fix or revert before merge—**do not** iterate only on z-index numbers without re-checking the checklist.

## Background (why this exists)

A **v0.9.3** change introduced `.preview__fts-layer` for AGV z-order. Route `<line>` styles were accidentally nested under the wrong selector, so **no `stroke`** was applied to route lines → routes disappeared **in all tabs** using the preview. Subsequent z-index-only experiments (8, 15, 100) did not fix the root cause.

**Fix pattern:** Styles for `.preview__route-overlay` / `.preview__route-overlay--active` must target the **route SVG** in the template; FTS overlays stay in `.preview__fts-layer`.

## References

- Component: `osf/apps/osf-ui/src/app/components/shopfloor-preview/`
- Sprint context: [sprint_18.md](../sprints/sprint_18.md)
- Smoke checklist: [osf-ui-logimat-smoke-checklist.md](osf-ui-logimat-smoke-checklist.md)
