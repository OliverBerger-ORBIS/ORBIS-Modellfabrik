# OSF-UI: SVG label text and line breaks

**Purpose:** Single reference for how **multi-line SVG text** is produced in the dashboard, why **three different approaches** exist, and how to **visually verify** diagrams after changes.  
**Related:** [DSP Architecture component spec](../02-architecture/dsp-architecture-component-spec.md) (layout); customer labels: [HOWTO_ADD_CUSTOMER.md](../../osf/apps/osf-ui/src/app/components/dsp-animation/configs/HOWTO_ADD_CUSTOMER.md).

---

## 1. Why SVG text is special

SVG `<text>` does not auto-wrap like HTML. Line breaks are implemented with multiple `<tspan>` elements and/or by **splitting strings into lines** in TypeScript. Character width is always **approximate** (proportional fonts); different features use slightly different factors on purpose.

---

## 2. Three contexts (do not merge into one algorithm)

### 2.1 DSP-Architecture (presentation / architecture views)

**Code:** `dsp-architecture.component.ts` — `getWrappedLabelLines`, `shouldWrapLabel`, label Y adjustments.

**Behaviour:**

- Wrapping applies mainly to **device** containers (`type === 'device'`).
- **Word boundaries** (spaces only). Long single words are not German-compound-split.
- **At most two lines** (`lines.slice(0, 2)`).
- Character estimate: `fontSize * 0.6` for `maxCharsPerLine` from container width minus padding.

**Use case:** Short station/device labels (often one word). Keep this layer **simple** to avoid layout regressions.

---

### 2.2 DSP-Animation (shopfloor diagram, customer configs)

**Code:** `dsp-animation.component.ts` — `getWrappedLabelLines` (different rules than DSP-Architecture).

**Behaviour:**

- **Manual break hints:** use ` / ` (space-slash-space) in i18n labels so editors can suggest where a line may break.
- If the full label fits **one** line (after normalising break hints), it is shown as **one** line (e.g. compound words without spaces).
- If wrapping is needed: up to **three** lines; hyphenation rules when breaking mid-part — see implementation and **HOWTO_ADD_CUSTOMER.md** § “Wichtige Hinweise zu Labels”.

**Use case:** Shopfloor device/system boxes with curated `$localize` strings.

---

### 2.3 Use-case SVG generators (UC-00 … UC-01 …)

**UC-00 Interoperability — DSP column steps:** `uc-00-svg-generator.service.ts` — `buildDspStepTexts`: **two explicit i18n keys** per title (`titleLine1` / `titleLine2`); description uses `wrapWordsToLinesSimple` with `maxCharsPerLineFromInnerWidth` (factor `~0.52`, **max 2** lines). Baseline gap between title block and description **≥** title line height; body class `uc00-dsp-step-desc` uses `neutralDarkGrey`. Block **vertically centered** in the **130×520** step boxes.

**Example (richest logic):** `uc-01-svg-generator.service.ts` — `wrapParagraph`, `trySemanticCompoundSplit`, `renderFittedBoxLines`.

**Behaviour:**

- Long **DE/EN** copy inside fixed boxes; **multiple lines** as needed for box height.
- **German compounds:** optional split at known suffixes; otherwise syllable-style hyphen breaks for overflow.
- Narrower character estimate (`~0.52 * fontSize`) and `<tspan>` stacking for vertical centering.

**Use case:** Narrative / genealogy diagrams, not icon labels.

---

## 3. Design decision: no “UC-01 everywhere”

**DSP-Architecture** should **not** adopt the full UC-01 wrapping pipeline: different text lengths, risk of visual regressions, and little benefit for short labels. **Shared documentation** and optional **small shared utilities** (Phase 2) are enough.

---

## 4. Visual regression checklist (manual)

Run **Mock** where possible; check **EN** and **DE** for at least one long string each. Resize the browser (narrow ~1280px and wide) once per area.

| # | Area | Where to open | What to check |
|---|------|----------------|---------------|
| 1 | DSP-Animation | DSP tab → customer / animated shopfloor diagram | Labels with ` / ` break sensibly; no clipped text; single-line when space allows. |
| 2 | DSP-Architecture | Presentation or DSP → architecture views (functional / component / deployment) | Device labels: max two lines; text inside boxes; no overlap with icons. |
| 3 | UC-00 … UC-06 | `dsp/use-case/...` → **Concept** tab (SVG) | Titles and box text fit; no overflow on exported-style layout. |
| 4 | UC-01 | `dsp/use-case/track-trace` → **Concept** (Partitur) | Long German compounds wrap readably; legend readable. |
| 5 | Optional | Same routes on **GitHub Pages** build | Parity with local production build. |

---

## 5. Shared utilities (Phase 2)

**Module:** `osf/apps/osf-ui/src/app/utils/svg-text-utils.ts` (Jest: `svg-text-utils.spec.ts`)

| Export | Use |
|--------|-----|
| `escapeXmlForSvgText` | Safe text inside generated SVG markup (used by **UC-01** `esc()`). |
| `DSP_ARCHITECTURE_LABEL_CHAR_WIDTH_FACTOR` | `0.6` — device label width estimate for **DSP-Architecture**. |
| `DSP_ANIMATION_LABEL_CHAR_WIDTH_FACTOR` | `0.58` — shopfloor box label width estimate for **DSP-Animation**. |
| `maxCharsPerLineFromInnerWidth` | `floor(innerWidth / (fontSize * factor))`, minimum `1`. |
| `wrapWordsToLinesSimple` | Space-only wrapping + `maxLines` cap (**DSP-Architecture** device labels). |

**Not** moved here: DSP-Animation ` / ` break hints, hyphen rules, “station” hard-wrap, or UC-01 compound splitting — by design (see §3).

**Optional later:** other `*-svg-generator.service.ts` files that emit raw SVG strings can call `escapeXmlForSvgText` to avoid duplicating escape rules.

---

## 6. Source file index

| Feature | Primary file(s) |
|---------|-------------------|
| **Shared utils** | `osf/apps/osf-ui/src/app/utils/svg-text-utils.ts` |
| DSP-Architecture | `osf/apps/osf-ui/src/app/components/dsp-architecture/dsp-architecture.component.ts` |
| DSP-Animation | `osf/apps/osf-ui/src/app/components/dsp-animation/dsp-animation.component.ts` |
| UC-01 | `osf/apps/osf-ui/src/app/pages/use-cases/track-trace-genealogy/uc-01-svg-generator.service.ts` |
| UC-00 / others | `osf/apps/osf-ui/src/app/pages/use-cases/*/*-svg-generator.service.ts` |
| Diagram colours | `osf/apps/osf-ui/src/app/assets/color-palette.ts` (`ORBIS_COLORS.diagram.*`) |

---

*Last updated: 2026-03-31*
