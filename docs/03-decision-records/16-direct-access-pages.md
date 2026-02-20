# 16 – Direct-access pages outside tab navigation

## Status
Accepted

## Context
- For presentation / video mode we need some routes reachable directly via URL, without adding more items to the tab navigation.
- Current examples:
  - `/#/en/presentation` (FTS route & shopfloor layout)
  - `/#/en/dsp-animation` (refactored DSP architecture view)
  - `/#/en/dsp-action` (DSP Action page)
  - `/#/en/dsp/customer` (Customer selector page - central entry point for customer-specific DSP architecture pages)
  - `/#/en/dsp/customer/fmf` (FMF customer-specific DSP architecture)
  - `/#/en/dsp/customer/ecme` (ECME customer-specific DSP architecture)
- These links should be discoverable in the app, but not clutter the main navigation.

## Decision
- Document all non-tab routes in the Settings tab under a dedicated "Direct-access pages" section.
- Keep the list maintained there whenever new direct pages are added.
- Do not add these routes to the tab bar unless explicitly requested.

## Consequences
- Users can quickly find shareable/presentation URLs without overloading navigation.
- Adding a new direct page requires updating the Settings tab list and this record.
