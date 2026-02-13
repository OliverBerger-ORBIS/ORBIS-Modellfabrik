import { Injectable } from '@angular/core';
import { createUc02Structure, type Uc02Structure, type Uc02Source, type Uc02DspStep, type Uc02Target } from './uc-02-structure.config';
import { ORBIS_COLORS } from '../../../assets/color-palette';

/**
 * Service for generating UC-02 Three Data Pools SVG dynamically
 * Based on UC-02_3-Data-Pools_Concept.drawio
 */
@Injectable({ providedIn: 'root' })
export class Uc02SvgGeneratorService {
  /**
   * Generate SVG string from structure with I18n text replacements
   */
  generateSvg(i18nTexts: Record<string, string>): string {
    const s = createUc02Structure();
    const t = (key: string): string => i18nTexts[key] || key;
    const D = ORBIS_COLORS.diagram;

    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${s.viewBox.width}" height="${s.viewBox.height}" viewBox="0 0 ${s.viewBox.width} ${s.viewBox.height}">`;

    // Defs
    svg += this.defs();

    // Root group
    svg += '<g id="uc02_root">';

    // Background
    svg += `<rect x="0" y="0" width="${s.viewBox.width}" height="${s.viewBox.height}" fill="url(#uc02_bgGrad)"/>`;

    // Title
    svg += `<g id="uc02_title"><text x="${s.title.x}" y="${s.title.y}" text-anchor="middle" class="uc02-title">${this.esc(t(s.title.key))}</text></g>`;

    // Subtitle (step 0 only)
    svg += `<g id="uc02_subtitle"><text x="${s.subtitle.x}" y="${s.subtitle.y}" text-anchor="middle" class="uc02-subtitle">${this.esc(t(s.subtitle.key))}</text></g>`;

    // Sources column
    svg += '<g id="uc02_col_sources">';
    for (const src of s.sources) {
      svg += this.sourceBox(src, t, D);
    }
    svg += '</g>';

    // DSP container and steps
    svg += `<g id="uc02_container_dsp">`;
    svg += `<rect id="uc02_container_dsp_rect" x="${s.containerDsp.x}" y="${s.containerDsp.y}" width="${s.containerDsp.width}" height="${s.containerDsp.height}" rx="10" fill="url(#uc02_dspGrad)" stroke="${D.laneTraceStroke}" stroke-width="2"/>`;
    svg += `<text x="${s.containerDsp.x + s.containerDsp.width / 2}" y="${s.containerDsp.y + 35}" text-anchor="middle" class="uc02-panel-title">${this.esc(t('uc02.dsp.header'))}</text>`;
    for (const step of s.dspSteps) {
      svg += this.dspStepBox(step, t, D);
    }
    svg += '</g>';

    // Note (context model) - rectangle with folded upper-right corner, 3 lines
    svg += this.noteBox(s.note, t, D);

    // Targets column
    svg += '<g id="uc02_col_targets">';
    for (const tgt of s.targets) {
      svg += this.targetBox(tgt, t, D);
    }
    svg += '</g>';

    // Connections (drawn last so they appear on top and stay visible)
    svg += this.connections(s);
    svg += this.feedbackConnection(s, t);

    // Step description overlay (drawn last so it appears on top; hidden initially)
    const sd = s.stepDescription;
    const hlGreen = ORBIS_COLORS.highlightGreen.strong;
    svg += `<g id="uc02_step_description" style="display: none;">`;
    svg += `<rect x="${sd.x - sd.width / 2}" y="${sd.y}" width="${sd.width}" height="${sd.height}" rx="8" ry="8" fill="${hlGreen}" opacity="0.95"/>`;
    svg += `<text id="uc02_step_description_title" x="${sd.x}" y="${sd.y + 28}" text-anchor="middle" font-size="24" font-weight="700" fill="#ffffff"></text>`;
    svg += `<text id="uc02_step_description_text" x="${sd.x}" y="${sd.y + 58}" text-anchor="middle" font-size="16" font-weight="400" fill="#ffffff"></text>`;
    svg += '</g>';

    svg += '</g>';
    svg += '</svg>';

    return svg;
  }

  private defs(): string {
    const D = ORBIS_COLORS.diagram;
    const nightBlue = ORBIS_COLORS.orbisNightBlue;

    return `<defs>
      <linearGradient id="uc02_bgGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="${D.bgGradientStart}"/>
        <stop offset="100%" stop-color="${D.bgGradientEnd}"/>
      </linearGradient>
      <linearGradient id="uc02_dspGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="100%" stop-color="${D.laneTraceFill}"/>
      </linearGradient>
      <marker id="uc02_arrow" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
        <polygon points="0,0 10,5 0,10" fill="${D.connectionStroke}"/>
      </marker>
      <style>
        .uc02-title { font: 700 40px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc02-subtitle { font: 400 22px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc02-panel-title { font: 700 22px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc02-source-title { font: 700 20px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc02-source-sub { font: 400 16px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; font-style: italic; }
        .uc02-step-title { font: 700 18px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc02-step-sub { font: 400 14px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc02-target { font: 700 18px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc02-note { font: 400 14px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc02-footer { font: 400 16px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
      </style>
    </defs>`;
  }

  private cylinderBodyPath(x: number, y: number, w: number, h: number): string {
    const ry = Math.min(h * 0.2, 22);
    const rx = w / 2 - 3;
    const left = x + 3;
    const right = x + w - 3;
    return (
      `M ${left} ${y + ry} A ${rx} ${ry} 0 0 0 ${right} ${y + ry}` +
      ` L ${right} ${y + h - ry} A ${rx} ${ry} 0 0 1 ${left} ${y + h - ry} Z`
    );
  }

  private cylinderTopEllipse(x: number, y: number, w: number, h: number): { cx: number; cy: number; rx: number; ry: number } {
    const ry = Math.min(h * 0.2, 22);
    const rx = w / 2 - 3;
    return { cx: x + w / 2, cy: y + ry, rx, ry };
  }

  /** 5-corner polygon: rectangle with triangle pointing down (blunt tip). Triangle base = rect side. */
  private arrowStepPathDown(x: number, y: number, w: number, h: number): string {
    const rectH = h * 0.6;
    const tipH = h - rectH;
    const tipW = w * 0.5;
    const cx = x + w / 2;
    return `M ${x} ${y} L ${x + w} ${y} L ${x + w} ${y + rectH} L ${cx + tipW / 2} ${y + rectH} L ${cx} ${y + h} L ${cx - tipW / 2} ${y + rectH} L ${x} ${y + rectH} Z`;
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

  private sourceBox(src: Uc02Source, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
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

    const ry = Math.min(src.height * 0.2, 22);
    const bodyH = src.height - 2 * ry;
    const titleY = src.y + ry + bodyH * 0.35;
    const subtitleY = src.y + ry + bodyH * 0.65;
    const top = this.cylinderTopEllipse(src.x, src.y, src.width, src.height);

    let out = `<g id="uc02_${src.id}">`;
    out += `<path d="${this.cylinderBodyPath(src.x, src.y, src.width, src.height)}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`;
    out += `<ellipse cx="${top.cx}" cy="${top.cy}" rx="${top.rx}" ry="${top.ry}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`;
    out += `<text x="${src.x + src.width / 2}" y="${titleY + 10}" text-anchor="middle" class="uc02-source-title">${this.esc(t(src.titleKey))}</text>`;
    out += `<text x="${src.x + src.width / 2}" y="${subtitleY + 8}" text-anchor="middle" class="uc02-source-sub">${this.esc(t(src.subtitleKey))}</text>`;
    out += '</g>';
    return out;
  }

  private dspStepBox(step: Uc02DspStep, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    let out = `<g id="uc02_${step.id}">`;
    out += `<path d="${this.arrowStepPathDown(step.x, step.y, step.width, step.height)}" fill="${D.laneTraceFill}" stroke="${D.laneTraceStroke}" stroke-width="1.5"/>`;
    out += `<text x="${step.x + step.width / 2}" y="${step.y + 32}" text-anchor="middle" class="uc02-step-title">${this.esc(t(step.titleKey))}</text>`;
    out += `<text x="${step.x + step.width / 2}" y="${step.y + 58}" text-anchor="middle" class="uc02-step-sub">${this.esc(t(step.subtitleKey))}</text>`;
    out += '</g>';
    return out;
  }

  private noteBox(note: { x: number; y: number; width: number; height: number; textKey: string }, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    // Ref 100x40: main (0,0)-(90,0)-(100,10)-(100,40)-(0,40)-(0,0). Fold triangle: (90,0)-(90,10)-(100,10)
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
    const line1 = parts[0] ? parts[0] + ' ↔' : '';
    const line2 = parts[1] ? parts[1] + ' ↔' : '';
    const line3 = parts[2] || '';
    const cx = note.x + note.width / 2;
    const lh = 16;
    return `<g id="uc02_note_context">
      <path d="${path}" fill="${D.laneTraceFill}" stroke="${D.laneTraceStroke}" stroke-width="1"/>
      <path d="${foldTri}" fill="${D.laneTraceFill}" stroke="${D.laneTraceStroke}" stroke-width="1"/>
      <text x="${cx}" y="${note.y + 28}" text-anchor="middle" class="uc02-note">${this.esc(line1)}</text>
      <text x="${cx}" y="${note.y + 28 + lh}" text-anchor="middle" class="uc02-note">${this.esc(line2)}</text>
      <text x="${cx}" y="${note.y + 28 + lh * 2}" text-anchor="middle" class="uc02-note">${this.esc(line3)}</text>
    </g>`;
  }

  /** Target boxes incl. BI/Data Lake: rounded rect (no cloud). */
  private targetBox(tgt: Uc02Target, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
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

  private connections(s: Uc02Structure): string {
    const D = ORBIS_COLORS.diagram;
    const stroke = D.connectionStroke;

    let out = '<g id="uc02_connections">';

    const srcs = s.sources;
    const steps = s.dspSteps;
    const tgts = s.targets;
    const stepCorr = steps[2];
    const cy = (y: number, h: number) => y + h / 2;

    // Data: cylinder -> step. Horizontal segments at destination use primary source Y (Business→Norm, Shopfloor→Enrich, Env→Corr)
    const ids = ['business', 'shopfloor', 'env'];
    const stepNames = ['norm', 'enrich', 'corr'];
    const primaryCyForStep = [cy(srcs[0].y, srcs[0].height), cy(srcs[1].y, srcs[1].height), cy(srcs[2].y, srcs[2].height)];
    for (let si = 0; si < 3; si++) {
      for (let di = 0; di < 3; di++) {
        const src = srcs[si];
        const step = steps[di];
        const srcCy = cy(src.y, src.height);
        const destY = primaryCyForStep[di]; // horizontal at step uses primary cylinder Y
        const id = `uc02_conn_${ids[si]}_${stepNames[di]}`;
        if (si === di) {
          // Direct: Business→Norm, Shopfloor→Enrich, Env→Corr – purely horizontal
          out += `<path id="${id}" d="M ${src.x + src.width} ${srcCy} L ${step.x} ${srcCy}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc02_arrow)"/>`;
        } else {
          // Cross: vertical at midX; horizontal at destination uses primary Y (so all arrivals at same step share Y)
          const midX = (src.x + src.width + step.x) / 2;
          out += `<path id="${id}" d="M ${src.x + src.width} ${srcCy} L ${midX} ${srcCy} L ${midX} ${destY} L ${step.x} ${destY}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc02_arrow)"/>`;
        }
      }
    }

    // DSP chain: step bottom center -> next step top center (like Lanes: sequential flow)
    out += `<line id="uc02_conn_norm_enrich" x1="${steps[0].x + steps[0].width / 2}" y1="${steps[0].y + steps[0].height}" x2="${steps[1].x + steps[1].width / 2}" y2="${steps[1].y}" stroke="${stroke}" stroke-width="2" marker-end="url(#uc02_arrow)"/>`;
    out += `<line id="uc02_conn_enrich_corr" x1="${steps[1].x + steps[1].width / 2}" y1="${steps[1].y + steps[1].height}" x2="${steps[2].x + steps[2].width / 2}" y2="${steps[2].y}" stroke="${stroke}" stroke-width="2" marker-end="url(#uc02_arrow)"/>`;

    // Analytics: from Correlate tip (bottom, max Y) -> down -> right -> up to target horizontal -> target
    const tipX = stepCorr.x + stepCorr.width / 2;
    const tipY = stepCorr.y + stepCorr.height;
    const downOffset = 50;
    const stepRight = stepCorr.x + stepCorr.width;
    const tgtLeft = tgts[0].x;
    const spineX = (stepRight + tgtLeft) / 2; // vertical segment midway between step right edge and target left edge
    for (let i = 0; i < 3; i++) {
      const tgt = tgts[i];
      const tgtCy = cy(tgt.y, tgt.height);
      const connId = ['uc02_conn_corr_analytics', 'uc02_conn_corr_bi', 'uc02_conn_corr_closed'][i];
      out += `<path id="${connId}" d="M ${tipX} ${tipY} L ${tipX} ${tipY + downOffset} L ${spineX} ${tipY + downOffset} L ${spineX} ${tgtCy} L ${tgtLeft} ${tgtCy}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc02_arrow)"/>`;
    }

    out += '</g>';
    return out;
  }

  private feedbackConnection(s: Uc02Structure, t: (k: string) => string): string {
    const D = ORBIS_COLORS.diagram;
    const tgtC = s.targets[2];
    const srcB = s.sources[0];
    const vbH = s.viewBox.height;
    const exitX = tgtC.x + tgtC.width / 2;
    const exitY = tgtC.y + tgtC.height;
    const entryX = srcB.x;
    const entryY = srcB.y + srcB.height / 2;
    const wayX = 50;
    const wayY = vbH - 70;
    const path = `M ${exitX} ${exitY} L ${exitX} ${wayY} L ${wayX} ${wayY} L ${wayX} ${entryY} L ${entryX} ${entryY}`;
    const lblX = wayX + 80;
    const lblY = wayY - 12;
    return `<g id="uc02_edge_feedback">
      <path d="${path}" stroke="${D.connectionStroke}" stroke-width="2" stroke-dasharray="8 4" fill="none" marker-end="url(#uc02_arrow)"/>
      <text x="${lblX}" y="${lblY}" text-anchor="middle" font-size="14" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc02.feedback'))}</text>
    </g>`;
  }

  private esc(str: string): string {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
}
