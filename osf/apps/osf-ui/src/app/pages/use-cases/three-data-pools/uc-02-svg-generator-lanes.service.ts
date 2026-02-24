import { Injectable } from '@angular/core';
import {
  createUc02LanesStructure,
  type Uc02LanesStructure,
  type Uc02LanesSource,
  type Uc02LanesDspStep,
  type Uc02LanesTarget,
} from './uc-02-structure-lanes.config';
import { ORBIS_COLORS } from '../../../assets/color-palette';

/**
 * SVG Generator for UC-02 Architecture Lanes view
 * 3 horizontal lanes: Analytics (top) → DSP (middle) → Data (bottom)
 */
@Injectable({ providedIn: 'root' })
export class Uc02SvgGeneratorLanesService {
  generateSvg(i18nTexts: Record<string, string>): string {
    const s = createUc02LanesStructure();
    const t = (key: string): string => i18nTexts[key] || key;
    const D = ORBIS_COLORS.diagram;

    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${s.viewBox.width}" height="${s.viewBox.height}" viewBox="0 0 ${s.viewBox.width} ${s.viewBox.height}">`;

    svg += this.defs();
    svg += '<g id="uc02_root">';

    svg += `<rect x="0" y="0" width="${s.viewBox.width}" height="${s.viewBox.height}" fill="url(#uc02_bgGrad)"/>`;

    svg += `<g id="uc02_title"><text x="${s.title.x}" y="${s.title.y}" text-anchor="middle" class="uc02-title">${this.esc(t(s.title.key))}</text></g>`;
    svg += `<g id="uc02_subtitle"><text x="${s.subtitle.x}" y="${s.subtitle.y}" text-anchor="middle" class="uc02-subtitle">${this.esc(t(s.subtitle.key))}</text></g>`;

    // Outcome (shown constantly)
    const highlightGreenStrong = ORBIS_COLORS.highlightGreen.strong;
    svg += `<g id="uc02_outcome"><text x="${s.outcome.x}" y="${s.outcome.y}" text-anchor="middle" font-family="Segoe UI" font-weight="600" font-size="16" fill="${highlightGreenStrong}">${this.esc(t(s.outcome.key))}</text></g>`;

    // Lane 1: Analytics & Value (top) - uc02_col_targets
    svg += `<g id="uc02_col_targets">`;
    svg += `<rect id="uc02_lanes_layer_analytics" x="${s.laneAnalytics.x}" y="${s.laneAnalytics.y}" width="${s.laneAnalytics.width}" height="${s.laneAnalytics.height}" rx="10" fill="url(#uc02_analyticsGrad)" stroke="${D.targetAnalyticsStroke}" stroke-width="2"/>`;
    svg += `<text x="${s.laneAnalytics.x + 16}" y="${s.laneAnalytics.y + 32}" class="uc02-lane-label">${this.esc(t('uc02.lane.analytics'))}</text>`;
    for (const tgt of s.targets) {
      svg += this.targetBox(tgt, t, D);
    }
    svg += '</g>';

    // Lane 2: DSP (middle) - uc02_container_dsp
    svg += `<g id="uc02_container_dsp">`;
    svg += `<rect id="uc02_lanes_layer_dsp" x="${s.laneDsp.x}" y="${s.laneDsp.y}" width="${s.laneDsp.width}" height="${s.laneDsp.height}" rx="10" fill="url(#uc02_dspGrad)" stroke="${D.laneTraceStroke}" stroke-width="2"/>`;
    svg += `<text x="${s.laneDsp.x + 16}" y="${s.laneDsp.y + 32}" class="uc02-lane-label">${this.esc(t('uc02.lane.dsp'))}</text>`;
    for (const step of s.dspSteps) {
      svg += this.dspStepBox(step, t, D);
    }
    svg += this.noteBox(s.note, t, D);
    svg += '</g>';

    // Lane 3: Data (bottom) - uc02_col_sources
    svg += `<g id="uc02_col_sources">`;
    svg += `<rect id="uc02_lanes_layer_data" x="${s.laneData.x}" y="${s.laneData.y}" width="${s.laneData.width}" height="${s.laneData.height}" rx="10" fill="url(#uc02_dataLaneGrad)" stroke="${D.laneShopfloorStroke}" stroke-width="2"/>`;
    svg += `<text x="${s.laneData.x + 16}" y="${s.laneData.y + 32}" class="uc02-lane-label">${this.esc(t('uc02.lane.data'))}</text>`;
    for (const src of s.sources) {
      svg += this.sourceBox(src, t, D);
    }
    svg += '</g>';

    // Connections and feedback
    svg += this.connections(s, D);
    svg += this.feedbackConnection(s, t, D);

    // Step description overlay (drawn last so it appears on top; hidden initially)
    const sd = s.stepDescription;
    const hlGreen = ORBIS_COLORS.highlightGreen.strong;
    svg += `<g id="uc02_step_description" style="display: none;">`;
    svg += `<rect x="${sd.x - sd.width / 2}" y="${sd.y}" width="${sd.width}" height="${sd.height}" rx="8" ry="8" fill="${hlGreen}" opacity="0.95"/>`;
    svg += `<text id="uc02_step_description_title" x="${sd.x}" y="${sd.y + 28}" text-anchor="middle" font-size="24" font-weight="700" fill="#ffffff"></text>`;
    svg += `<text id="uc02_step_description_text" x="${sd.x}" y="${sd.y + 58}" text-anchor="middle" font-size="16" font-weight="400" fill="#ffffff"></text>`;
    svg += '</g>';

    svg += '</g></svg>';
    return svg;
  }

  private defs(): string {
    const D = ORBIS_COLORS.diagram;
    const nightBlue = ORBIS_COLORS.orbisNightBlue;

    return `<defs>
      <marker id="uc02_arrow" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
        <polygon points="0,0 10,5 0,10" fill="${D.connectionStroke}"/>
      </marker>
      <linearGradient id="uc02_bgGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="${D.bgGradientStart}"/>
        <stop offset="100%" stop-color="${D.bgGradientEnd}"/>
      </linearGradient>
      <linearGradient id="uc02_dspGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="100%" stop-color="${D.laneTraceFill}"/>
      </linearGradient>
      <linearGradient id="uc02_analyticsGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="100%" stop-color="${D.targetAnalyticsFill}"/>
      </linearGradient>
      <linearGradient id="uc02_dataLaneGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="100%" stop-color="#e6e6e6"/>
      </linearGradient>
      <style>
        .uc02-title { font: 700 40px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc02-subtitle { font: 400 22px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc02-source-title { font: 700 18px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc02-source-sub { font: 400 14px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; font-style: italic; }
        .uc02-step-title { font: 700 22px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc02-step-sub { font: 400 12px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc02-target { font: 700 16px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc02-note { font: 400 12px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc02-footer { font: 400 16px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc02-lane-label { font: 700 18px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
      </style>
    </defs>`;
  }

  /** Database cylinder: body path. Lanes: height +50%, radius -30% -> ry = h*0.14, rx = (w/2-3)*0.7 */
  private cylinderBodyPath(x: number, y: number, w: number, h: number): string {
    const ry = Math.min(h * 0.14, 16);
    const rx = (w / 2 - 3) * 0.7;
    const cx = x + w / 2;
    const left = cx - rx;
    const right = cx + rx;
    return (
      `M ${left} ${y + ry} A ${rx} ${ry} 0 0 0 ${right} ${y + ry}` +
      ` L ${right} ${y + h - ry} A ${rx} ${ry} 0 0 1 ${left} ${y + h - ry} Z`
    );
  }

  private cylinderTopEllipse(x: number, y: number, w: number, h: number): { cx: number; cy: number; rx: number; ry: number } {
    const ry = Math.min(h * 0.14, 16);
    const rx = (w / 2 - 3) * 0.7;
    return { cx: x + w / 2, cy: y + ry, rx, ry };
  }

  /** 6-corner step: rectangle with right triangle + left notch. Left x-diff = right x-diff (= tipSize). */
  private arrowStepPathHex(x: number, y: number, w: number, h: number): string {
    const tipSize = Math.min(h * 0.35, w * 0.18);
    const leftTipX = x + 2 * tipSize; // same offset from base (x+tipSize) as right tip from (x+w-tipSize)
    return `M ${x + tipSize} ${y} L ${x + w - tipSize} ${y} L ${x + w} ${y + h / 2} L ${x + w - tipSize} ${y + h} L ${x + tipSize} ${y + h} L ${leftTipX} ${y + h / 2} Z`;
  }

  private cloudPath(x: number, y: number, w: number, h: number): string {
    const cx = x + w / 2;
    const cy = y + h / 2;
    const rw = w * 0.4;
    const rh = h * 0.35;
    return `M ${cx - rw} ${cy} ` +
      `C ${cx - rw * 1.2} ${cy - rh} ${cx - rw * 0.5} ${cy - rh * 1.2} ${cx} ${cy - rh} ` +
      `C ${cx + rw * 0.5} ${cy - rh * 1.2} ${cx + rw * 1.2} ${cy - rh} ${cx + rw} ${cy} ` +
      `C ${cx + rw * 1.1} ${cy + rh} ${cx + rw * 0.4} ${cy + rh * 1.1} ${cx} ${cy + rh} ` +
      `C ${cx - rw * 0.4} ${cy + rh * 1.1} ${cx - rw * 1.1} ${cy + rh} ${cx - rw} ${cy} Z`;
  }

  private noteBox(note: { x: number; y: number; width: number; height: number; textKey: string }, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    // Ref 100x40: main (0,0)-(90,0)-(100,10)-(100,40)-(0,40)-(0,0). Fold: (90,0)-(90,10)-(100,10)
    const sx = note.width / 100;
    const sy = note.height / 40;
    const p1 = { x: note.x, y: note.y };
    const p2 = { x: note.x + 90 * sx, y: note.y };
    const p3 = { x: note.x + note.width, y: note.y + 10 * sy };
    const p4 = { x: note.x + note.width, y: note.y + note.height };
    const p5 = { x: note.x, y: note.y + note.height };
    const p2b = { x: note.x + 90 * sx, y: note.y + 10 * sy };
    const path = `M ${p1.x} ${p1.y} L ${p2.x} ${p2.y} L ${p3.x} ${p3.y} L ${p4.x} ${p4.y} L ${p5.x} ${p5.y} Z`;
    const foldTri = `M ${p2.x} ${p2.y} L ${p2b.x} ${p2b.y} L ${p3.x} ${p3.y} Z`;
    const parts = (t(note.textKey) || '').split(/\s*↔\s*/).map((p) => p.trim()).filter(Boolean);
    const cx = note.x + note.width / 2;
    const lh = 14;
    return `<g id="uc02_note_context">
      <path d="${path}" fill="${D.laneTraceFill}" stroke="${D.laneTraceStroke}" stroke-width="1"/>
      <path d="${foldTri}" fill="${D.laneTraceFill}" stroke="${D.laneTraceStroke}" stroke-width="1"/>
      <text x="${cx}" y="${note.y + 22}" text-anchor="middle" class="uc02-note">${this.esc(parts[0] ? parts[0] + ' ↔' : '')}</text>
      <text x="${cx}" y="${note.y + 22 + lh}" text-anchor="middle" class="uc02-note">${this.esc(parts[1] ? parts[1] + ' ↔' : '')}</text>
      <text x="${cx}" y="${note.y + 22 + lh * 2}" text-anchor="middle" class="uc02-note">${this.esc(parts[2] || '')}</text>
    </g>`;
  }

  private sourceBox(src: Uc02LanesSource, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const fills: Record<string, string> = {
      src_business: D.laneBusinessFill,
      src_shopfloor: D.laneShopfloorFill,
      src_env: D.laneEnvironmentFill,
    };
    const strokes: Record<string, string> = {
      src_business: D.laneBusinessStroke,
      src_shopfloor: D.laneShopfloorStroke,
      src_env: D.laneEnvironmentStroke,
    };
    const fill = fills[src.id] ?? D.boxFill;
    const stroke = strokes[src.id] ?? D.boxStroke;

    const ry = Math.min(src.height * 0.14, 16);
    const bodyH = src.height - 2 * ry;
    const titleY = src.y + ry + bodyH * 0.35;
    const subtitleY = src.y + ry + bodyH * 0.65;

    const top = this.cylinderTopEllipse(src.x, src.y, src.width, src.height);

    let out = `<g id="uc02_${src.id}">`;
    out += `<path d="${this.cylinderBodyPath(src.x, src.y, src.width, src.height)}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`;
    out += `<ellipse cx="${top.cx}" cy="${top.cy}" rx="${top.rx}" ry="${top.ry}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`;
    out += `<text x="${src.x + src.width / 2}" y="${titleY + 8}" text-anchor="middle" class="uc02-source-title">${this.esc(t(src.titleKey))}</text>`;
    out += `<text x="${src.x + src.width / 2}" y="${subtitleY + 6}" text-anchor="middle" class="uc02-source-sub">${this.esc(t(src.subtitleKey))}</text>`;
    out += '</g>';
    return out;
  }

  private dspStepBox(step: Uc02LanesDspStep, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const tipSize = Math.min(step.height * 0.35, step.width * 0.18);
    const innerLeft = step.x + 2 * tipSize;
    const innerRight = step.x + step.width - tipSize;
    const innerCenterX = (innerLeft + innerRight) / 2;
    const titleY = step.y + 42;
    const subtitleY = titleY + 22;
    let out = `<g id="uc02_${step.id}">`;
    out += `<path d="${this.arrowStepPathHex(step.x, step.y, step.width, step.height)}" fill="${D.laneTraceFill}" stroke="${D.laneTraceStroke}" stroke-width="1.5"/>`;
    out += `<text x="${innerCenterX}" y="${titleY}" text-anchor="middle" class="uc02-step-title">${this.esc(t(step.titleKey))}</text>`;
    out += `<text x="${innerCenterX}" y="${subtitleY}" text-anchor="middle" class="uc02-step-sub">${this.esc(t(step.subtitleKey))}</text>`;
    out += '</g>';
    return out;
  }

  private stepTipSize(w: number, h: number): number {
    return Math.min(h * 0.35, w * 0.18);
  }

  /** Target boxes incl. BI/Data Lake: rounded rect (no cloud). */
  private targetBox(tgt: Uc02LanesTarget, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const fill = D.targetAnalyticsFill;
    const stroke = D.targetAnalyticsStroke;
    const cx = tgt.x + tgt.width / 2;
    const cy = tgt.y + tgt.height / 2;
    let out = `<g id="uc02_${tgt.id}">`;
    out += `<rect x="${tgt.x}" y="${tgt.y}" width="${tgt.width}" height="${tgt.height}" rx="10" ry="10" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`;
    out += `<text x="${cx}" y="${cy + 8}" text-anchor="middle" class="uc02-target">${this.esc(t(tgt.textKey))}</text>`;
    out += '</g>';
    return out;
  }

  private connections(s: Uc02LanesStructure, D: typeof ORBIS_COLORS.diagram): string {
    const stroke = D.connectionStroke;
    let out = '<g id="uc02_connections">';

    const srcs = s.sources;
    const steps = s.dspSteps;
    const tgts = s.targets;
    const stepCorr = steps[2];
    const cy = (y: number, h: number) => y + h / 2;

    // Data: all 3 sources -> all 3 steps (L-shaped, horizontal segment at vertical midpoint)
    const ids = ['shopfloor', 'business', 'env'];
    const stepNames = ['norm', 'enrich', 'corr'];
    for (let si = 0; si < 3; si++) {
      for (let di = 0; di < 3; di++) {
        const src = srcs[si];
        const step = steps[di];
        const startY = src.y;
        const endY = step.y + step.height;
        const midY = (startY + endY) / 2;
        const id = `uc02_conn_${ids[si]}_${stepNames[di]}`;
        out += `<path id="${id}" d="M ${src.x + src.width / 2} ${startY} L ${src.x + src.width / 2} ${midY} L ${step.x + step.width / 2} ${midY} L ${step.x + step.width / 2} ${endY}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc02_arrow)"/>`;
      }
    }

    // DSP chain: exact middle points of step polygon (right tip -> left notch tip)
    const ts = (st: Uc02LanesDspStep) => this.stepTipSize(st.width, st.height);
    const rightMid = (st: Uc02LanesDspStep) => ({ x: st.x + st.width, y: cy(st.y, st.height) });
    const leftMid = (st: Uc02LanesDspStep) => ({ x: st.x + 2 * ts(st), y: cy(st.y, st.height) });
    const r0 = rightMid(steps[0]);
    const l1 = leftMid(steps[1]);
    const r1 = rightMid(steps[1]);
    const l2 = leftMid(steps[2]);
    out += `<line id="uc02_conn_norm_enrich" x1="${r0.x}" y1="${r0.y}" x2="${l1.x}" y2="${l1.y}" stroke="${stroke}" stroke-width="2" marker-end="url(#uc02_arrow)"/>`;
    out += `<line id="uc02_conn_enrich_corr" x1="${r1.x}" y1="${r1.y}" x2="${l2.x}" y2="${l2.y}" stroke="${stroke}" stroke-width="2" marker-end="url(#uc02_arrow)"/>`;

    // Analytics: start at midpoint of top two points (x+tipSize,y) and (x+w-tipSize,y)
    const corrTopMidX = stepCorr.x + stepCorr.width / 2;
    const corrTopY = stepCorr.y;
    for (let i = 0; i < 3; i++) {
      const tgt = tgts[i];
      const tgtCx = tgt.x + tgt.width / 2;
      const tgtBottom = tgt.y + tgt.height;
      const midY = (corrTopY + tgtBottom) / 2;
      const connId = ['uc02_conn_corr_analytics', 'uc02_conn_corr_bi', 'uc02_conn_corr_closed'][i];
      out += `<path id="${connId}" d="M ${corrTopMidX} ${corrTopY} L ${corrTopMidX} ${midY} L ${tgtCx} ${midY} L ${tgtCx} ${tgtBottom}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc02_arrow)"/>`;
    }

    out += '</g>';
    return out;
  }

  private feedbackConnection(s: Uc02LanesStructure, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const vbW = s.viewBox.width;
    const vbH = s.viewBox.height;
    const tgtC = s.targets[2];
    const srcB = s.sources[1];
    const exitX = tgtC.x + tgtC.width;
    const exitY = tgtC.y + tgtC.height / 2;
    const extendRight = 45;
    const wayY = vbH - 60;
    const entryCenterX = srcB.x + srcB.width / 2;
    const entryBottomY = srcB.y + srcB.height;
    const path = `M ${exitX} ${exitY} L ${exitX + extendRight} ${exitY} L ${exitX + extendRight} ${wayY} L ${entryCenterX} ${wayY} L ${entryCenterX} ${entryBottomY}`;
    const lblX = entryCenterX - 80;
    const lblY = wayY - 12;
    return `<g id="uc02_edge_feedback">
      <path d="${path}" stroke="${D.connectionStroke}" stroke-width="2" stroke-dasharray="8 4" fill="none" marker-end="url(#uc02_arrow)"/>
      <text x="${lblX}" y="${lblY}" text-anchor="middle" font-size="12" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc02.feedback'))}</text>
    </g>`;
  }

  private esc(str: string): string {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
}
