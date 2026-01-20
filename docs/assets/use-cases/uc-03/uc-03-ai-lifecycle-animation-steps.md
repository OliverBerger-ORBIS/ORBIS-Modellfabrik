# UC-03 — Animation Steps (SVG)

## Grundprinzip
- Ein SVG
- Default: alle Elemente sichtbar, aber „gedimmt“
- Step steuert: Highlight (Opacity/Stroke/Glow) + Pfeile ein-/ausblenden

## Element-Gruppen (IDs Vorschlag)
- layer_process
  - proc_capture
  - proc_train
  - proc_monitor
  - arrow_proc_forward (capture→train→monitor)
  - arrow_proc_feedback (monitor→capture)
- layer_dsp
  - dsp_edge_1
  - dsp_cockpit
  - dsp_edge_2
  - arrow_train_to_cockpit
  - arrow_cockpit_to_edge1
  - arrow_cockpit_to_edge2
- layer_shopfloor
  - sf_stations_edge1 (stack group)
  - sf_stations_edge2 (stack group)
  - arrow_edge1_to_sf
  - arrow_edge2_to_sf
  - arrow_sf_to_capture (optional, wenn Feedback aus Shopfloor gezeigt wird)

## Steps
Step 0: Overview
- alle Layer sichtbar
- nur Container leicht betont

Step 1: Data Capture & Context
- proc_capture highlight
- Pfeil Shopfloor → DSP Edge (Edge1/Edge2) highlight
- optional: kleine "event dots" als Motion-Path (wenn ihr das im DSP-Style habt)

Step 2: Train & Validate (Cloud)
- proc_train highlight
- Pfeil DSP Edge → Cockpit/Cloud highlight
- Label "Train centrally" sichtbar

Step 3: Rollout / Deploy to multiple stations
- dsp_cockpit highlight
- Pfeile Cockpit → Edge1 und Cockpit → Edge2 highlight
- Label "Deploy to multiple stations" sichtbar
- sf_stations_edge1 + sf_stations_edge2 highlight (kurz pulsen)

Step 4: Inference at stations
- dsp_edge_1 + sf_stations_edge1 highlight
- dsp_edge_2 + sf_stations_edge2 highlight
- optional: kleiner Badge "Model vX.Y" an Stationen

Step 5: Monitor & Feedback
- proc_monitor highlight
- Pfeil Shopfloor → DSP Edge → Cockpit highlight
- Rückpfeil proc_feedback (monitor→capture) highlight
