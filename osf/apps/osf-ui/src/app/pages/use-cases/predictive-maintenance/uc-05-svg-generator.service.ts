import { Injectable } from '@angular/core';
import {
  createUc05Structure,
  UC05_SHOPFLOOR_ICONS,
  type Uc05Structure,
  type Uc05ProcessStep,
  type Uc05MixedBox,
  type Uc05ShopfloorBox,
  type Uc05ShopfloorIconBox,
} from './uc-05-structure.config';
import { ICONS } from '../../../shared/icons/icon.registry';
import { ORBIS_COLORS } from '../../../assets/color-palette';

/**
 * SVG Generator for UC-05 Predictive Maintenance
 * 3 lanes: Process → Mixed (DSP Edge | ALARM | Target) → Shopfloor
 */
@Injectable({ providedIn: 'root' })
export class Uc05SvgGeneratorService {
  generateSvg(i18nTexts: Record<string, string>): string {
    const s = createUc05Structure();
    const t = (key: string): string => i18nTexts[key] || key;
    const D = ORBIS_COLORS.diagram;
    const alarmFill = D.nodeParallel;
    const alarmStroke = D.connectionAlert;

    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${s.viewBox.width}" height="${s.viewBox.height}" viewBox="0 0 ${s.viewBox.width} ${s.viewBox.height}">`;

    svg += this.defs(alarmStroke);
    svg += '<g id="uc05_root">';

    svg += `<rect x="0" y="0" width="${s.viewBox.width}" height="${s.viewBox.height}" fill="url(#uc05_bgGrad)"/>`;

    svg += `<g id="uc05_title"><text x="${s.title.x}" y="${s.title.y}" text-anchor="middle" class="uc05-title">${this.esc(t(s.title.key))}</text></g>`;
    svg += `<g id="uc05_subtitle"><text x="${s.subtitle.x}" y="${s.subtitle.y}" text-anchor="middle" class="uc05-subtitle">${this.esc(t(s.subtitle.key))}</text></g>`;

    // Process Lane
    svg += `<g id="uc05_col_process">`;
    svg += `<rect id="uc05_lanes_layer_process" x="${s.laneProcess.x}" y="${s.laneProcess.y}" width="${s.laneProcess.width}" height="${s.laneProcess.height}" rx="10" fill="url(#uc05_processGrad)" stroke="${D.laneBusinessStroke}" stroke-width="2"/>`;
    svg += `<text x="${s.laneProcess.x + 16}" y="${s.laneProcess.y + 32}" text-anchor="start" class="uc05-lane-label">${this.esc(t('uc05.lane.process'))}</text>`;
    for (const step of s.processSteps) {
      svg += this.processStepBox(step, t, D);
    }
    svg += '</g>';

    // Mixed boxes only (no lane rect – DSP Edge | ALARM | Target)
    svg += `<g id="uc05_container_mixed">`;
    for (const box of s.mixedBoxes) {
      svg += this.mixedBox(box, t, D, alarmFill, alarmStroke);
    }
    svg += '</g>';

    // Shopfloor Lane
    svg += `<g id="uc05_col_shopfloor">`;
    svg += `<rect id="uc05_lanes_layer_shopfloor" x="${s.laneShopfloor.x}" y="${s.laneShopfloor.y}" width="${s.laneShopfloor.width}" height="${s.laneShopfloor.height}" rx="10" fill="url(#uc05_shopfloorGrad)" stroke="${D.laneShopfloorStroke}" stroke-width="2"/>`;
    svg += `<text x="${s.laneShopfloor.x + 16}" y="${s.laneShopfloor.y + 32}" text-anchor="start" class="uc05-lane-label">${this.esc(t('uc05.lane.shopfloor'))}</text>`;
    svg += this.shopfloorIconBox(s.shopfloorTriggerBox, t, D);
    svg += this.signalTriangle(s.shopfloorSignalTriangle, D, alarmStroke);
    svg += this.shopfloorIconBox(s.shopfloorDetectorBox, t, D);
    svg += this.shopfloorSystemsDevicesBox(s.shopfloorSystemsDevicesBox, t, D);
    svg += '</g>';

    svg += this.connections(s, t, D);
    svg += this.feedbackConnection(s, t, D);

    const sd = s.stepDescription;
    const hlGreen = ORBIS_COLORS.highlightGreen.strong;
    svg += `<g id="uc05_step_description" style="display: none;">`;
    svg += `<rect x="${sd.x - sd.width / 2}" y="${sd.y}" width="${sd.width}" height="${sd.height}" rx="8" ry="8" fill="${hlGreen}" opacity="0.95"/>`;
    svg += `<text id="uc05_step_description_title" x="${sd.x}" y="${sd.y + 28}" text-anchor="middle" font-size="24" font-weight="700" fill="#ffffff"></text>`;
    svg += `<text id="uc05_step_description_text" x="${sd.x}" y="${sd.y + 58}" text-anchor="middle" font-size="16" font-weight="400" fill="#ffffff"></text>`;
    svg += '</g>';

    svg += '</g></svg>';
    return svg;
  }

  private defs(alarmStroke: string): string {
    const D = ORBIS_COLORS.diagram;
    const nightBlue = ORBIS_COLORS.orbisNightBlue;

    return `<defs>
      <marker id="uc05_arrow" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
        <polygon points="0,0 10,5 0,10" fill="${D.connectionStroke}"/>
      </marker>
      <marker id="uc05_arrow_start" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
        <polygon points="10,0 0,5 10,10" fill="${D.connectionStroke}"/>
      </marker>
      <marker id="uc05_arrow_feedback" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
        <polygon points="0,0 10,5 0,10" fill="${D.laneTraceStroke}"/>
      </marker>
      <linearGradient id="uc05_bgGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="${D.bgGradientStart}"/>
        <stop offset="100%" stop-color="${D.bgGradientEnd}"/>
      </linearGradient>
      <linearGradient id="uc05_processGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="100%" stop-color="${D.laneBusinessFill}"/>
      </linearGradient>
      <linearGradient id="uc05_mixedGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="100%" stop-color="${D.laneTraceFill}"/>
      </linearGradient>
      <linearGradient id="uc05_shopfloorGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="100%" stop-color="${D.laneShopfloorFill}"/>
      </linearGradient>
      <style>
        .uc05-title { font: 700 40px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc05-subtitle { font: 400 22px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc05-lane-label { font: 700 18px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc05-step-title { font: 700 22px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc05-step-bullet { font: 400 13px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc05-mixed-title { font: 700 16px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc05-alarm-title { font: 700 18px "Segoe UI",Arial,sans-serif; fill: ${alarmStroke}; }
        .uc05-sf-title { font: 700 16px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
      </style>
    </defs>`;
  }

  private arrowStepPathHex(x: number, y: number, w: number, h: number): string {
    const tipSize = Math.min(h * 0.35, w * 0.18);
    const leftTipX = x + 2 * tipSize;
    return `M ${x + tipSize} ${y} L ${x + w - tipSize} ${y} L ${x + w} ${y + h / 2} L ${x + w - tipSize} ${y + h} L ${x + tipSize} ${y + h} L ${leftTipX} ${y + h / 2} Z`;
  }

  private processStepBox(step: Uc05ProcessStep, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const bullets = (t(step.bulletsKey) || '').split(/\n/).filter(Boolean);
    const tipSize = Math.min(step.height * 0.35, step.width * 0.18);
    const innerLeft = step.x + 2 * tipSize;
    const innerRight = step.x + step.width - tipSize;
    const innerCenterX = (innerLeft + innerRight) / 2;
    const bulletPad = 8;
    const titleY = step.y + 42;
    const lineH = 16;
    const bulletStartY = titleY + 24;
    let out = `<g id="uc05_${step.id}">`;
    out += `<path d="${this.arrowStepPathHex(step.x, step.y, step.width, step.height)}" fill="${D.laneBusinessFill}" stroke="${D.laneBusinessStroke}" stroke-width="1.5"/>`;
    out += `<text x="${innerCenterX}" y="${titleY}" text-anchor="middle" class="uc05-step-title">${this.esc(t(step.titleKey))}</text>`;
    bullets.slice(0, 3).forEach((b, i) => {
      out += `<text x="${innerLeft + bulletPad}" y="${bulletStartY + i * lineH}" text-anchor="start" class="uc05-step-bullet">${this.esc(b.replace(/^[•\-\*]\s*/, ''))}</text>`;
    });
    out += '</g>';
    return out;
  }

  private mixedBox(box: Uc05MixedBox, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram, alarmFill: string, alarmStroke: string): string {
    const cx = box.x + box.width / 2;
    const toAbs = (p: string) => p;

    if (box.type === 'alarm') {
      const iconSize = Math.min(56, box.width / 3, box.height / 2);
      const iconGap = 12;
      const totalIconsW = iconSize * 2 + iconGap;
      const iconStartX = cx - totalIconsW / 2;
      const iconY = box.y + (box.height - iconSize) / 2;
      let out = `<g id="uc05_${box.id}">`;
      out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="${alarmFill}" stroke="${alarmStroke}" stroke-width="2"/>`;
      out += `<image href="${toAbs(ICONS.shopfloor.shared.alarm)}" x="${iconStartX}" y="${iconY}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet"/>`;
      out += `<image href="${toAbs(ICONS.shopfloor.shared.bellAlarm)}" x="${iconStartX + iconSize + iconGap}" y="${iconY}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet"/>`;
      out += `<text x="${cx}" y="${box.y + 18}" text-anchor="middle" class="uc05-alarm-title">${this.esc(t(box.titleKey))}</text>`;
      out += `<text x="${cx}" y="${box.y + box.height - 10}" text-anchor="middle" font-size="11" fill="${alarmStroke}">${this.esc(t('uc05.mixed.alarm.sub'))}</text>`;
      out += '</g>';
      return out;
    }

    if (box.type === 'target') {
      return this.targetBoxWithSubBoxes(box, t, D, toAbs);
    }

    const bullets = (box.bulletsKey ? t(box.bulletsKey) : '').split(/\n/).filter(Boolean);
    const fill = D.laneTraceFill;
    const stroke = D.laneTraceStroke;
    const titleY = box.y + 28;
    const lineH = 14;

    let out = `<g id="uc05_${box.id}">`;
    out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="${fill}" stroke="${stroke}" stroke-width="1.5"/>`;
    out += `<text x="${cx}" y="${titleY}" text-anchor="middle" class="uc05-mixed-title">${this.esc(t(box.titleKey))}</text>`;
    bullets.slice(0, 4).forEach((b, i) => {
      out += `<text x="${cx}" y="${titleY + 22 + i * lineH}" text-anchor="middle" font-size="12" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(b.replace(/^[•\-\*]\s*/, ''))}</text>`;
    });

    if (box.type === 'dsp-edge') {
      const iconPath = toAbs(ICONS.dsp.architecture.edgeBox);
      const iconSize = Math.min(96, box.width - 24, box.height - 40);
      const iconY = box.y + (box.height - iconSize) / 2;
      out += `<image href="${iconPath}" x="${cx - iconSize / 2}" y="${iconY}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet" opacity="0.9"/>`;
    }

    out += '</g>';
    return out;
  }

  /** Target box with 3 sub-boxes: MES, ERP, Analytics (gleichmäßig verteilt, ca +40px Breite) */
  private targetBoxWithSubBoxes(
    box: Uc05MixedBox,
    t: (k: string) => string,
    D: typeof ORBIS_COLORS.diagram,
    toAbs: (p: string) => string
  ): string {
    const subGap = 12;
    const pad = 14;
    const titleH = 26;
    const subW = 160;
    const totalSubW = 3 * subW + 2 * subGap;
    const subH = box.height - titleH - pad * 2 - 24;
    const subStartX = box.x + (box.width - totalSubW) / 2;
    const iconSize = Math.min(64, subW - 16, subH - 40);

    const subs = [
      { key: 'uc05.mixed.target.mes', icon: ICONS.business.mes },
      { key: 'uc05.mixed.target.erp', icon: ICONS.business.erp },
      { key: 'uc05.mixed.target.analytics', icon: ICONS.business.analytics },
    ];

    let out = `<g id="uc05_${box.id}">`;
    out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="${D.targetAnalyticsFill}" stroke="${D.targetAnalyticsStroke}" stroke-width="1.5"/>`;
    out += `<text x="${box.x + box.width / 2}" y="${box.y + titleH - 4}" text-anchor="middle" class="uc05-mixed-title">${this.esc(t(box.titleKey))}</text>`;

    subs.forEach((sub, i) => {
      const sx = subStartX + i * (subW + subGap);
      const sy = box.y + titleH + pad;
      const iconY = sy + (subH - iconSize) / 2;
      out += `<rect x="${sx}" y="${sy}" width="${subW}" height="${subH}" rx="8" fill="rgba(255,255,255,0.7)" stroke="rgba(0,0,0,0.12)" stroke-width="1"/>`;
      out += `<image href="${toAbs(sub.icon)}" x="${sx + (subW - iconSize) / 2}" y="${iconY}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet"/>`;
      out += `<text x="${sx + subW / 2}" y="${sy + subH - 8}" text-anchor="middle" font-size="15" font-weight="600" fill="${ORBIS_COLORS.orbisNightBlue}">${this.esc(t(sub.key))}</text>`;
    });

    out += '</g>';
    return out;
  }

  /** Vertical lines – 10px→20px→30px…→150px, Mittelpunkt auf gedachter Linie (signal Trigger→Detector) */
  private signalTriangle(
    area: { x: number; y: number; width: number; height: number },
    D: typeof ORBIS_COLORS.diagram,
    lineColor: string
  ): string {
    // Verlauf: 10, 20, 30, … bis ~150px (Höhe Detector-Box)
    const barCount = 15;
    const minH = 10;
    const maxH = 150;
    const barGap = 3;
    const barTotalW = area.width - (barCount - 1) * barGap;
    const barW = Math.max(2, barTotalW / barCount);

    // Mittelpunkt aller Linien auf gedachter horizontaler Linie (Mitte der Box)
    const centerY = area.y + area.height / 2;

    let out = `<g id="uc05_sf_signal_triangle">`;
    out += `<rect x="${area.x}" y="${area.y}" width="${area.width}" height="${area.height}" fill="none" stroke="none"/>`;
    for (let i = 0; i < barCount; i++) {
      if (i % 2 !== 0) continue; // Nur jede zweite Linie darstellen
      const h = minH + (i / (barCount - 1)) * (maxH - minH);
      const x = area.x + i * (barW + barGap);
      const barY = centerY - h / 2;
      out += `<rect x="${x}" y="${barY}" width="${barW}" height="${h}" rx="2" fill="${lineColor}" stroke="none"/>`;
    }
    out += '</g>';
    return out;
  }

  /** Single icon box for Trigger; Detector shows vibration + tilt-sensor side by side */
  private shopfloorIconBox(box: Uc05ShopfloorIconBox, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const toAbs = (p: string) => p;
    const label = box.iconKey === 'trigger' ? t('uc05.sf.trigger') : t('uc05.sf.vibrationSensor');
    const figStroke = 'rgba(0,0,0,0.12)';
    let out = `<g id="uc05_${box.id}">`;
    out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="rgba(255,255,255,0.7)" stroke="${figStroke}" stroke-width="1.5"/>`;

    if (box.iconKey === 'trigger') {
      const path = toAbs(ICONS.shopfloor.shared.tuningFork);
      const iconSize = Math.min(64, box.width - 24, box.height - 44);
      out += `<image href="${path}" x="${box.x + (box.width - iconSize) / 2}" y="${box.y + 20}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet"/>`;
    } else {
      // Detector: zwei Icons nebeneinander (vibration, tilt-sensor)
      const iconGap = 14;
      const iconSize = Math.min(80, (box.width - iconGap - 24) / 2, box.height - 44);
      const totalW = iconSize * 2 + iconGap;
      const startX = box.x + (box.width - totalW) / 2;
      const iconY = box.y + (box.height - iconSize - 24) / 2;
      out += `<image href="${toAbs(ICONS.shopfloor.shared.vibrationSensor)}" x="${startX}" y="${iconY}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet"/>`;
      out += `<image href="${toAbs(ICONS.shopfloor.shared.tiltSensor)}" x="${startX + iconSize + iconGap}" y="${iconY}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet"/>`;
    }

    out += `<text x="${box.x + box.width / 2}" y="${box.y + box.height - 14}" text-anchor="middle" font-size="12" font-weight="600" fill="${ORBIS_COLORS.orbisNightBlue}">${this.esc(label)}</text>`;
    out += '</g>';
    return out;
  }

  /** Systems+Devices box – same layout as UC-03 Shopfloor 2 (700x220) */
  private shopfloorSystemsDevicesBox(box: Uc05ShopfloorBox, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const toAbs = (p: string) => p;
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

    const sysPaths = UC05_SHOPFLOOR_ICONS.systems.map(
      (k) => toAbs((ICONS.shopfloor.systems as Record<string, string>)[k] ?? '')
    );
    const devPaths = UC05_SHOPFLOOR_ICONS.devices.map(
      (k) => toAbs((ICONS.shopfloor.stations as Record<string, string>)[k] ?? '')
    );
    const sysLabels = ['AGV', 'SCADA'];
    const devLabels = ['MILL', 'DRILL', 'AIQS', 'HBW'];

    const figStroke = 'rgba(0,0,0,0.12)';
    const figFill = 'rgba(255,255,255,0.6)';
    const captionH = 18;
    const captionPad = 6;

    let out = `<g id="uc05_${box.id}">`;
    out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="${D.laneShopfloorFill}" stroke="${D.laneShopfloorStroke}" stroke-width="1.5"/>`;
    out += `<text x="${box.x + titlePad}" y="${box.y + 26}" text-anchor="start" class="uc05-sf-title">${this.esc(t(box.titleKey))}</text>`;

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
    out += `<text x="${sysBoxX + sysBoxW / 2}" y="${stripY + stripH - 6}" text-anchor="middle" font-size="11" font-weight="600" fill="${ORBIS_COLORS.orbisNightBlue}">${this.esc(t('uc05.sf.systemsLabel'))}</text>`;

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
    out += `<text x="${devBoxX + devBoxW / 2}" y="${stripY + stripH - 6}" text-anchor="middle" font-size="11" font-weight="600" fill="${ORBIS_COLORS.orbisNightBlue}">${this.esc(t('uc05.sf.devicesLabel'))}</text>`;

    out += '</g>';
    return out;
  }

  private connections(s: Uc05Structure, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const stroke = D.connectionStroke;
    let out = '<g id="uc05_connections">';

    const steps = s.processSteps;
    const mixed = s.mixedBoxes;
    const dsp = mixed[0];
    const alarm = mixed[1];
    const target = mixed[2];
    const detectorBox = s.shopfloorDetectorBox;
    const cy = (y: number, h: number) => y + h / 2;
    const cx = (x: number, w: number) => x + w / 2;

    // Detector box → DSP Edge: up, then right, then up (toward DSP Edge icon)
    const detectorTopCx = detectorBox.x + detectorBox.width / 2;
    const detectorTop = detectorBox.y;
    const dspBottom = dsp.y + dsp.height;
    const dspCx = cx(dsp.x, dsp.width);
    const wayY1 = (detectorTop + dspBottom) / 2;
    out += `<path id="uc05_conn_sensor_dsp" d="M ${detectorTopCx} ${detectorTop} L ${detectorTopCx} ${wayY1} L ${dspCx} ${wayY1} L ${dspCx} ${dspBottom}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc05_arrow)"/>`;
    out += `<text x="${(detectorTopCx + dspCx) / 2}" y="${wayY1 + 14}" text-anchor="middle" font-size="11" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc05.conn.signals'))}</text>`;

    // DSP Edge → ALARM
    const dspRight = dsp.x + dsp.width;
    const alarmLeft = alarm.x;
    const alarmCy = cy(alarm.y, alarm.height);
    out += `<path id="uc05_conn_dsp_alarm" d="M ${dspRight} ${cy(dsp.y, dsp.height)} L ${alarmLeft} ${alarmCy}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc05_arrow)"/>`;

    // ALARM → Target
    const alarmRight = alarm.x + alarm.width;
    const targetLeft = target.x;
    out += `<path id="uc05_conn_alarm_target" d="M ${alarmRight} ${alarmCy} L ${targetLeft} ${cy(target.y, target.height)}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc05_arrow)"/>`;
    out += `<text x="${(alarmRight + targetLeft) / 2}" y="${alarmCy - 8}" text-anchor="middle" font-size="11" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc05.conn.alarmEvent'))}</text>`;

    // ALARM → Process step Alarm (nur gepunktete Linie)
    const alarmStep = steps[2];
    const alarmStepBottom = alarmStep.y + alarmStep.height;
    const alarmStepCx = cx(alarmStep.x, alarmStep.width);
    const wayY = (alarm.y + alarm.height / 2 + alarmStepBottom) / 2;
    const alarmProcessPath = `M ${cx(alarm.x, alarm.width)} ${alarm.y} L ${cx(alarm.x, alarm.width)} ${wayY} L ${alarmStepCx} ${wayY} L ${alarmStepCx} ${alarmStepBottom}`;
    out += `<path id="uc05_conn_alarm_process" d="${alarmProcessPath}" stroke="${stroke}" stroke-width="2" stroke-dasharray="8 4" fill="none" marker-end="url(#uc05_arrow)"/>`;

    // ALARM → Systems & Devices: L-förmig (unten, dann rechts), Mitte zu Mitte, Rand zu Rand
    const sfBox = s.shopfloorSystemsDevicesBox;
    const alarmBottom = alarm.y + alarm.height;
    const alarmCx = cx(alarm.x, alarm.width);
    const sfLeft = sfBox.x;
    const sfCy = sfBox.y + sfBox.height / 2;
    out += `<path id="uc05_conn_alarm_systems" d="M ${alarmCx} ${alarmBottom} L ${alarmCx} ${sfCy} L ${sfLeft} ${sfCy}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc05_arrow)"/>`;
    out += `<text x="${(alarmCx + sfLeft) / 2}" y="${sfCy - 10}" text-anchor="middle" font-size="11" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc05.conn.productionPause'))}</text>`;

    out += '</g>';
    return out;
  }

  /** Feedback: Target → Process Feedback step (dashed, less prominent) */
  private feedbackConnection(s: Uc05Structure, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const steps = s.processSteps;
    const mixed = s.mixedBoxes;
    const target = mixed[2];
    const feedbackStep = steps[4];
    const targetTop = target.y;
    const targetCx = target.x + target.width / 2;
    const feedbackBottom = feedbackStep.y + feedbackStep.height;
    const feedbackCx = feedbackStep.x + feedbackStep.width / 2;
    const wayY = (targetTop + feedbackBottom) / 2;
    const path = `M ${targetCx} ${targetTop} L ${targetCx} ${wayY} L ${feedbackCx} ${wayY} L ${feedbackCx} ${feedbackBottom}`;
    const lblX = (targetCx + feedbackCx) / 2;
    const lblY = wayY + 16;
    return `<g id="uc05_feedback">
      <path d="${path}" stroke="${D.laneTraceStroke}" stroke-width="2" stroke-dasharray="8 4" fill="none" marker-end="url(#uc05_arrow_feedback)"/>
      <text x="${lblX}" y="${lblY}" text-anchor="middle" font-size="11" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc05.feedback'))}</text>
    </g>`;
  }

  private esc(str: string): string {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
}
