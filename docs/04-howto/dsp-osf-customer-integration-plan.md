# DSP OSF customer & ORBIS MES — integration plan

**Status:** Phase 1 implemented (OSF default customer, `sf-system-sensor`, MES URL, assets).  
**Audience:** OSF UI / demo alignment with ORBIS Smart Factory + ORBIS MES story.

## Goals (agreed)

1. **Default DSP customer:** `osf` (ORBIS Smart Factory demo) drives the **DSP tab** architecture sections (functional / component / deployment). **FMF** and **LogiMAT** remain in the customer list and dedicated routes.
2. **Sensor station (OSF only):** Replace generic `sf-system-any` with **`sf-system-sensor`** only in **`OSF_CONFIG`**. FMF / LogiMAT keep **`sf-system-any`** unchanged.
3. **Label:** Animation shows **“Sensor Station”** (not BME680).
4. **Icon:** `heading-sensors.svg` copied to `assets/svg/shopfloor/systems/sensor-station-system.svg`, registered as IconKey **`sensor-station-system`**.
5. **MES / EWM:** Primarily **external** — no dedicated tabs. Settings → External links: **`bpMesApplicationUrl`** (ORBIS MES), **`bpEwmApplicationUrl`** (SAP EWM); DSP animation **`bp-mes`** / **`bp-ewm`** are clickable when the respective URL is set.
6. **Navigation:** Click **Sensor Station** → **Sensor** tab (`/sensor`); click **MES** → external URL (new tab).
7. **DSP page subtitle:** Mentions **ORBIS MES** with DSP and smart manufacturing.

## Implemented (this iteration)

| Item | Location / notes |
|------|-------------------|
| `OSF_CONFIG` | `osf/.../configs/osf/osf-config.ts` — shopfloor: `sf-system-sensor` + `sf-system-fts`; BP layer from LogiMAT (MES, EWM, …). |
| Route | `/:locale/dsp/customer/osf` → `OsfDspPageComponent`. |
| Customer selector | OSF listed first; FMF, ECME, LogiMAT unchanged. |
| DSP sections default | `OSF_CONFIG` in functional / component / deployment section components. |
| `bpMesApplicationUrl` / `bpEwmApplicationUrl` | `ExternalLinksSettings`, `public/assets/config/external-links.json`, Settings → External links. |
| `updateContainerUrls` | `bp-mes` / `bp-ewm` use the respective URL when non-empty. |
| SVG asset | `sensor-station-system.svg` (copy of UI heading-sensors). |
| Docs | `DSP_Architecture_Objects_Reference.md` lists `sf-system-sensor` / `sensor-station-system`; `dsp-svg-inventory.md` links verification (no duplicate tile — asset is in the reference). |

## Backlog / follow-up

| Item | Notes |
|------|--------|
| **Configuration tab — ORBIS grid R1 C1** | Optional: bind **Sensor Station** to ORBIS cell when shopfloor layout/preset allows without breaking roles. |
| **Arduino thresholds (MQTT/API)** | Sprint 19 — separate section + topics; DAHEIM/ORBIS switch. |
| **EWM** | External URL or placeholder when product URL is fixed. |

## Verification checklist

- [x] DSP tab: architecture shows **Sensor Station** + FTS; **any system** not shown for OSF.
- [x] Settings: set **BP-MES Application URL** (`bpMesApplicationUrl`), open DSP animation, click **MES** → opens new tab.
- [x] Click **Sensor Station** → Sensor tab.
- [x] `/:locale/dsp/customer/fmf` and `/logimat` still show **any system** as before.

---

*Last updated: 2026-04-08*
