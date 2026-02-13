import { Injectable } from '@angular/core';
import {
  createUc03Structure,
  UC03_SHOPFLOOR_ICONS,
  type Uc03Structure,
  type Uc03ProcessStep,
  type Uc03DspBox,
  type Uc03ShopfloorBox,
} from './uc-03-structure.config';
import { ICONS } from '../../../shared/icons/icon.registry';
import { ORBIS_COLORS } from '../../../assets/color-palette';

/**
 * SVG Generator for UC-03 AI Lifecycle
 * 3 horizontal lanes: Process (top) → DSP (middle) → Shopfloor (bottom)
 * Lane labels: Process=right, DSP=top, Shopfloor=right, central title top
 */
@Injectable({ providedIn: 'root' })
export class Uc03SvgGeneratorService {
  generateSvg(i18nTexts: Record<string, string>): string {
    const s = createUc03Structure();
    const t = (key: string): string => i18nTexts[key] || key;
    const D = ORBIS_COLORS.diagram;

    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${s.viewBox.width}" height="${s.viewBox.height}" viewBox="0 0 ${s.viewBox.width} ${s.viewBox.height}">`;

    svg += this.defs();
    svg += '<g id="uc03_root">';

    svg += `<rect x="0" y="0" width="${s.viewBox.width}" height="${s.viewBox.height}" fill="url(#uc03_bgGrad)"/>`;

    // Central title top
    svg += `<g id="uc03_title"><text x="${s.title.x}" y="${s.title.y}" text-anchor="middle" class="uc03-title">${this.esc(t(s.title.key))}</text></g>`;
    svg += `<g id="uc03_subtitle"><text x="${s.subtitle.x}" y="${s.subtitle.y}" text-anchor="middle" class="uc03-subtitle">${this.esc(t(s.subtitle.key))}</text></g>`;

    // Lane 1: Process (top) – label left-top, animation-compatible ID
    svg += `<g id="uc03_col_process">`;
    svg += `<rect id="uc03_lanes_layer_process" x="${s.laneProcess.x}" y="${s.laneProcess.y}" width="${s.laneProcess.width}" height="${s.laneProcess.height}" rx="10" fill="url(#uc03_processGrad)" stroke="${D.laneBusinessStroke}" stroke-width="2"/>`;
    svg += `<text x="${s.laneProcess.x + 16}" y="${s.laneProcess.y + 32}" text-anchor="start" class="uc03-lane-label">${this.esc(t('uc03.lane.process'))}</text>`;
    for (const step of s.processSteps) {
      svg += this.processStepBox(step, t, D);
    }
    svg += '</g>';

    // Lane 2: DSP (middle) – label left-top, animation-compatible ID
    svg += `<g id="uc03_container_dsp">`;
    svg += `<rect id="uc03_lanes_layer_dsp" x="${s.laneDsp.x}" y="${s.laneDsp.y}" width="${s.laneDsp.width}" height="${s.laneDsp.height}" rx="10" fill="url(#uc03_dspGrad)" stroke="${D.laneTraceStroke}" stroke-width="2"/>`;
    svg += `<text x="${s.laneDsp.x + 16}" y="${s.laneDsp.y + 28}" text-anchor="start" class="uc03-lane-label">${this.esc(t('uc03.lane.dsp'))}</text>`;
    for (const box of s.dspBoxes) {
      svg += this.dspBox(box, t, D);
    }
    svg += '</g>';

    // Lane 3: Shopfloor (bottom) – label center-top, animation-compatible ID
    svg += `<g id="uc03_col_shopfloor">`;
    svg += `<rect id="uc03_lanes_layer_shopfloor" x="${s.laneShopfloor.x}" y="${s.laneShopfloor.y}" width="${s.laneShopfloor.width}" height="${s.laneShopfloor.height}" rx="10" fill="url(#uc03_shopfloorGrad)" stroke="${D.laneShopfloorStroke}" stroke-width="2"/>`;
    svg += `<text x="${s.laneShopfloor.x + s.laneShopfloor.width / 2}" y="${s.laneShopfloor.y + 28}" text-anchor="middle" class="uc03-lane-label">${this.esc(t('uc03.lane.shopfloor'))}</text>`;
    for (const box of s.shopfloorBoxes) {
      svg += this.shopfloorBox(box, t, D);
    }
    svg += '</g>';

    svg += this.connections(s, t, D);
    svg += this.feedbackConnection(s, t, D);

    // Step description overlay (for animation, hidden initially like UC-02)
    const sd = s.stepDescription;
    const hlGreen = ORBIS_COLORS.highlightGreen.strong;
    svg += `<g id="uc03_step_description" style="display: none;">`;
    svg += `<rect x="${sd.x - sd.width / 2}" y="${sd.y}" width="${sd.width}" height="${sd.height}" rx="8" ry="8" fill="${hlGreen}" opacity="0.95"/>`;
    svg += `<text id="uc03_step_description_title" x="${sd.x}" y="${sd.y + 28}" text-anchor="middle" font-size="24" font-weight="700" fill="#ffffff"></text>`;
    svg += `<text id="uc03_step_description_text" x="${sd.x}" y="${sd.y + 58}" text-anchor="middle" font-size="16" font-weight="400" fill="#ffffff"></text>`;
    svg += '</g>';

    svg += '</g></svg>';
    return svg;
  }

  private defs(): string {
    const D = ORBIS_COLORS.diagram;
    const nightBlue = ORBIS_COLORS.orbisNightBlue;

    return `<defs>
      <marker id="uc03_arrow" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
        <polygon points="0,0 10,5 0,10" fill="${D.connectionStroke}"/>
      </marker>
      <marker id="uc03_arrow_start" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
        <polygon points="10,0 0,5 10,10" fill="${D.connectionStroke}"/>
      </marker>
      <linearGradient id="uc03_bgGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="${D.bgGradientStart}"/>
        <stop offset="100%" stop-color="${D.bgGradientEnd}"/>
      </linearGradient>
      <linearGradient id="uc03_processGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="100%" stop-color="${D.laneBusinessFill}"/>
      </linearGradient>
      <linearGradient id="uc03_dspGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="100%" stop-color="${D.laneTraceFill}"/>
      </linearGradient>
      <linearGradient id="uc03_shopfloorGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="100%" stop-color="${D.laneShopfloorFill}"/>
      </linearGradient>
      <style>
        .uc03-title { font: 700 40px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc03-subtitle { font: 400 22px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc03-lane-label { font: 700 18px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc03-step-title { font: 700 18px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc03-step-bullet { font: 400 13px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc03-dsp-title { font: 700 16px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc03-dsp-bullet { font: 400 12px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc03-sf-title { font: 700 16px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc03-sf-bullet { font: 400 12px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
      </style>
    </defs>`;
  }

  /** 6-corner step (arrow shape): like UC-02 DSP step but scaled for larger content */
  private arrowStepPathHex(x: number, y: number, w: number, h: number): string {
    const tipSize = Math.min(h * 0.35, w * 0.18);
    const leftTipX = x + 2 * tipSize;
    return `M ${x + tipSize} ${y} L ${x + w - tipSize} ${y} L ${x + w} ${y + h / 2} L ${x + w - tipSize} ${y + h} L ${x + tipSize} ${y + h} L ${leftTipX} ${y + h / 2} Z`;
  }

  private stepTipSize(w: number, h: number): number {
    return Math.min(h * 0.35, w * 0.18);
  }

  private processStepBox(step: Uc03ProcessStep, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const bullets = (t(step.bulletsKey) || '').split(/\n/).filter(Boolean);
    const titleY = step.y + 32;
    const lineH = 18;
    let out = `<g id="uc03_${step.id}">`;
    out += `<path d="${this.arrowStepPathHex(step.x, step.y, step.width, step.height)}" fill="${D.laneBusinessFill}" stroke="${D.laneBusinessStroke}" stroke-width="1.5"/>`;
    out += `<text x="${step.x + step.width / 2}" y="${titleY}" text-anchor="middle" class="uc03-step-title">${this.esc(t(step.titleKey))}</text>`;
    bullets.slice(0, 4).forEach((b, i) => {
      out += `<text x="${step.x + step.width / 2}" y="${titleY + 22 + i * lineH}" text-anchor="middle" class="uc03-step-bullet">${this.esc(b.replace(/^[•\-\*]\s*/, ''))}</text>`;
    });
    out += '</g>';
    return out;
  }

  private dspBox(box: Uc03DspBox, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const bullets = (t(box.bulletsKey) || '').split(/\n/).filter(Boolean);
    const cx = box.x + box.width / 2;
    const titleY = box.y + 26;
    const lineH = 16;
    const bulletH = titleY + 22 + bullets.slice(0, 2).length * lineH;
    const iconSize = 76; // ~35% larger than 56
    const iconPad = 10;
    const iconY = bulletH + iconPad;
    const toAbs = (p: string) => (p.startsWith('/') ? p : '/' + p);
    let out = `<g id="uc03_${box.id}">`;
    out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" ry="10" fill="${D.laneTraceFill}" stroke="${D.laneTraceStroke}" stroke-width="1.5"/>`;
    out += `<text x="${cx}" y="${titleY}" text-anchor="middle" class="uc03-dsp-title">${this.esc(t(box.titleKey))}</text>`;
    bullets.slice(0, 2).forEach((b, i) => {
      out += `<text x="${cx}" y="${titleY + 22 + i * lineH}" text-anchor="middle" class="uc03-dsp-bullet">${this.esc(b.replace(/^[•\-\*]\s*/, ''))}</text>`;
    });
    if (box.iconKey) {
      const path = toAbs(ICONS.dsp.architecture[box.iconKey]);
      out += `<image href="${path}" x="${cx - iconSize / 2}" y="${iconY}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet" opacity="0.95"/>`;
    }
    out += '</g>';
    return out;
  }

  /** Shopfloor box: title left-top; Systems/Devices labels bottom; icon figures 4:5 (w:h), square icon + caption */
  private shopfloorBox(box: Uc03ShopfloorBox, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const toAbs = (p: string) => (p.startsWith('/') ? p : '/' + p);
    const titlePad = 14;
    const stripPad = 14;
    const stripY = box.y + 44;
    const stripH = box.height - 50;
    const groupGap = 16;
    const contentW = box.width - stripPad * 2 - groupGap;
    const sysBoxW = (contentW * 2) / 6;
    const devBoxW = (contentW * 4) / 6;
    const sysBoxX = box.x + stripPad;
    const devBoxX = box.x + stripPad + sysBoxW + groupGap;

    const sysPaths = UC03_SHOPFLOOR_ICONS.systems.map(
      (k) => toAbs((ICONS.shopfloor.systems as Record<string, string>)[k] ?? '')
    );
    const devPaths = UC03_SHOPFLOOR_ICONS.devices.map(
      (k) => toAbs((ICONS.shopfloor.stations as Record<string, string>)[k] ?? '')
    );
    const sysLabels = ['AGV', 'SCADA'];
    const devLabels = ['MILL', 'DRILL', 'AIQS', 'HBW'];

    const figStroke = 'rgba(0,0,0,0.12)';
    const figFill = 'rgba(255,255,255,0.6)';
    const captionH = 18;
    const captionPad = 6;

    let out = `<g id="uc03_${box.id}">`;
    out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" ry="10" fill="${D.laneShopfloorFill}" stroke="${D.laneShopfloorStroke}" stroke-width="1.5"/>`;
    out += `<text x="${box.x + titlePad}" y="${box.y + 26}" text-anchor="start" class="uc03-sf-title">${this.esc(t(box.titleKey))}</text>`;

    const sysCount = sysPaths.filter(Boolean).length;
    const devCount = devPaths.filter(Boolean).length;
    const figGap = 6;
    const innerPad = 10;
    const sysFigW = sysCount > 0 ? (sysBoxW - innerPad * 2 - (sysCount - 1) * figGap) / sysCount : 0;
    const devFigW = devCount > 0 ? (devBoxW - innerPad * 2 - (devCount - 1) * figGap) / devCount : 0;
    const sysFigH = sysCount > 0 ? sysFigW * (5 / 4) : 0;
    const devFigH = devCount > 0 ? devFigW * (5 / 4) : 0;
    const sysIconSize = sysCount > 0 ? Math.min(sysFigW - 8, sysFigH - captionH - captionPad * 2) : 0;
    const devIconSize = devCount > 0 ? Math.min(devFigW - 8, devFigH - captionH - captionPad * 2) : 0;

    // Systems sub-box (2/6 width), label "Systems" at bottom
    out += `<rect x="${sysBoxX}" y="${stripY}" width="${sysBoxW}" height="${stripH}" rx="8" fill="rgba(255,255,255,0.5)" stroke="${figStroke}" stroke-width="1"/>`;
    sysPaths.forEach((path, i) => {
      const fx = sysBoxX + innerPad + i * (sysFigW + figGap);
      const fy = stripY + innerPad;
      if (path) {
        out += `<rect x="${fx}" y="${fy}" width="${sysFigW}" height="${sysFigH}" rx="6" fill="${figFill}" stroke="${figStroke}" stroke-width="1"/>`;
        out += `<image href="${path}" x="${fx + (sysFigW - sysIconSize) / 2}" y="${fy + captionPad}" width="${sysIconSize}" height="${sysIconSize}" preserveAspectRatio="xMidYMid meet"/>`;
        out += `<text x="${fx + sysFigW / 2}" y="${fy + sysFigH - captionPad}" text-anchor="middle" font-size="10" font-weight="600" fill="#1e2d3d">${this.esc(sysLabels[i] ?? '')}</text>`;
      }
    });
    out += `<text x="${sysBoxX + sysBoxW / 2}" y="${stripY + stripH - 6}" text-anchor="middle" font-size="11" font-weight="600" fill="${ORBIS_COLORS.orbisNightBlue}">${this.esc(t('uc03.sf.systemsLabel'))}</text>`;

    // Devices sub-box (4/6 width), label "Devices" at bottom
    out += `<rect x="${devBoxX}" y="${stripY}" width="${devBoxW}" height="${stripH}" rx="8" fill="rgba(255,255,255,0.5)" stroke="${figStroke}" stroke-width="1"/>`;
    devPaths.forEach((path, i) => {
      const fx = devBoxX + innerPad + i * (devFigW + figGap);
      const fy = stripY + innerPad;
      if (path) {
        out += `<rect x="${fx}" y="${fy}" width="${devFigW}" height="${devFigH}" rx="6" fill="${figFill}" stroke="${figStroke}" stroke-width="1"/>`;
        out += `<image href="${path}" x="${fx + (devFigW - devIconSize) / 2}" y="${fy + captionPad}" width="${devIconSize}" height="${devIconSize}" preserveAspectRatio="xMidYMid meet"/>`;
        out += `<text x="${fx + devFigW / 2}" y="${fy + devFigH - captionPad}" text-anchor="middle" font-size="10" font-weight="600" fill="#1e2d3d">${this.esc(devLabels[i] ?? '')}</text>`;
      }
    });
    out += `<text x="${devBoxX + devBoxW / 2}" y="${stripY + stripH - 6}" text-anchor="middle" font-size="11" font-weight="600" fill="${ORBIS_COLORS.orbisNightBlue}">${this.esc(t('uc03.sf.devicesLabel'))}</text>`;

    out += '</g>';
    return out;
  }

  private connections(s: Uc03Structure, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const stroke = D.connectionStroke;
    let out = '<g id="uc03_connections">';

    const steps = s.processSteps;
    const dsp = s.dspBoxes;
    const sf = s.shopfloorBoxes;
    const cy = (y: number, h: number) => y + h / 2;

    // No connections between process steps (removed per spec)

    // Train (bottom center) → DSP Cockpit (top center); Train is steps[2]
    const train = steps[2];
    const trainBottomCx = train.x + train.width / 2;
    const trainBottomY = train.y + train.height;
    const cockpitTopCx = dsp[1].x + dsp[1].width / 2;
    const cockpitTopY = dsp[1].y;
    const midY1 = (trainBottomY + cockpitTopY) / 2;
    out += `<g id="uc03_conn_train_cockpit"><path d="M ${trainBottomCx} ${trainBottomY} L ${trainBottomCx} ${midY1} L ${cockpitTopCx} ${midY1} L ${cockpitTopCx} ${cockpitTopY}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc03_arrow)" marker-start="url(#uc03_arrow_start)"/><text x="${(trainBottomCx + cockpitTopCx) / 2}" y="${midY1 + 14}" text-anchor="middle" font-size="11" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc03.conn.dspProcess'))}</text></g>`;

    // DSP Cockpit ↔ Edge1, Cockpit ↔ Edge2 – bidirectional; connections end at MC box border
    const cockpitLeft = dsp[1].x;
    const cockpitRight = dsp[1].x + dsp[1].width;
    const cockpitCy = cy(dsp[1].y, dsp[1].height);
    const edge1Right = dsp[0].x + dsp[0].width;
    const edge1Cy = cy(dsp[0].y, dsp[0].height);
    const edge2Left = dsp[2].x;
    const edge2Cy = cy(dsp[2].y, dsp[2].height);
    const wayX1 = dsp[0].x + dsp[0].width + 40;
    const wayX2 = dsp[2].x - 40;
    out += `<path id="uc03_conn_cockpit_edge1" d="M ${cockpitLeft} ${cockpitCy} L ${wayX1} ${cockpitCy} L ${wayX1} ${edge1Cy} L ${edge1Right} ${edge1Cy}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc03_arrow)" marker-start="url(#uc03_arrow_start)"/>`;
    out += `<path id="uc03_conn_cockpit_edge2" d="M ${cockpitRight} ${cockpitCy} L ${wayX2} ${cockpitCy} L ${wayX2} ${edge2Cy} L ${edge2Left} ${edge2Cy}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc03_arrow)" marker-start="url(#uc03_arrow_start)"/>`;

    // Edge1 ↔ SF1, Edge2 ↔ SF2 – vertical, bidirectional (Shopfloor to DSP)
    const edge1Cx = dsp[0].x + dsp[0].width / 2;
    const edge2Cx = dsp[2].x + dsp[2].width / 2;
    const sf1Cx = sf[0].x + sf[0].width / 2;
    const sf2Cx = sf[1].x + sf[1].width / 2;
    out += `<path id="uc03_conn_edge1_sf1" d="M ${edge1Cx} ${dsp[0].y + dsp[0].height} L ${sf1Cx} ${sf[0].y}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc03_arrow)" marker-start="url(#uc03_arrow_start)"/>`;
    out += `<path id="uc03_conn_edge2_sf2" d="M ${edge2Cx} ${dsp[2].y + dsp[2].height} L ${sf2Cx} ${sf[1].y}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc03_arrow)" marker-start="url(#uc03_arrow_start)"/>`;

    out += '</g>';
    return out;
  }

  /** Feedback: Monitor (right tip) → L-shape → Train top center; longer vertical segments, label below */
  private feedbackConnection(s: Uc03Structure, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const steps = s.processSteps;
    const lane = s.laneProcess;
    const monitor = steps[4];
    const train = steps[2];
    const exitX = monitor.x + monitor.width;
    const exitY = monitor.y + monitor.height / 2;
    const laneRight = lane.x + lane.width - 8;
    const extendRight = Math.min(45, laneRight - exitX);
    const wayX = exitX + extendRight;
    const wayY = lane.y + 16;
    const trainTopCx = train.x + train.width / 2;
    const path = `M ${exitX} ${exitY} L ${wayX} ${exitY} L ${wayX} ${wayY} L ${trainTopCx} ${wayY} L ${trainTopCx} ${train.y}`;
    const lblX = (wayX + trainTopCx) / 2;
    const lblY = wayY + 20;
    return `<g id="uc03_feedback">
      <path d="${path}" stroke="${D.connectionStroke}" stroke-width="2" stroke-dasharray="8 4" fill="none" marker-end="url(#uc03_arrow)"/>
      <text x="${lblX}" y="${lblY}" text-anchor="middle" font-size="12" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc03.feedback'))}</text>
    </g>`;
  }

  private esc(str: string): string {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
}
