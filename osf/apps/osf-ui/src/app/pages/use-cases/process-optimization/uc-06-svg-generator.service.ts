import { Injectable } from '@angular/core';
import {
  createUc06Structure,
  type Uc06Structure,
  type Uc06ProcessStep,
  type Uc06MixedBox,
  type Uc06ShopfloorBox,
  type Uc06ShopfloorTargetsBox,
} from './uc-06-structure.config';
import { ICONS } from '../../../shared/icons/icon.registry';
import { ORBIS_COLORS } from '../../../assets/color-palette';

const UC06_SHOPFLOOR_ICONS = {
  systems: ['agv', 'scada'] as const,
  devices: ['mill', 'drill', 'aiqs', 'hbw'] as const,
} as const;

/**
 * SVG Generator for UC-07 Process Optimization
 * Layout: Process Lane → Mixed (DSP | Recommend | Target) → Shopfloor (Sources | Optimization Target)
 * Beide Shopfloor-Boxen zeigen Systems & Devices; links als Datenquelle, rechts als Optimierungsziel.
 * Connection Mixed Target → Shopfloor Target endet am oberen Rand der zweiten Box.
 */
@Injectable({ providedIn: 'root' })
export class Uc06SvgGeneratorService {
  generateSvg(i18nTexts: Record<string, string>): string {
    const s = createUc06Structure();
    const t = (key: string): string => i18nTexts[key] || key;
    const D = ORBIS_COLORS.diagram;
    const recFill = D.laneTraceFill;
    const recStroke = D.targetAnalyticsStroke;

    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${s.viewBox.width}" height="${s.viewBox.height}" viewBox="0 0 ${s.viewBox.width} ${s.viewBox.height}">`;

    svg += this.defs(recStroke);
    svg += '<g id="uc06_root">';

    svg += `<rect x="0" y="0" width="${s.viewBox.width}" height="${s.viewBox.height}" fill="url(#uc06_bgGrad)"/>`;

    svg += `<g id="uc06_title"><text x="${s.title.x}" y="${s.title.y}" text-anchor="middle" class="uc06-title">${this.esc(t(s.title.key))}</text></g>`;
    svg += `<g id="uc06_subtitle"><text x="${s.subtitle.x}" y="${s.subtitle.y}" text-anchor="middle" class="uc06-subtitle">${this.esc(t(s.subtitle.key))}</text></g>`;

    // Outcome (shown constantly)
    const highlightGreenStrong = ORBIS_COLORS.highlightGreen.strong;
    svg += `<g id="uc06_outcome"><text x="${s.outcome.x}" y="${s.outcome.y}" text-anchor="middle" font-family="Segoe UI" font-weight="600" font-size="16" fill="${highlightGreenStrong}">${this.esc(t(s.outcome.key))}</text></g>`;

    // Footer (Disclaimer)
    svg += `<g id="uc06_footer"><text x="${s.footer.x}" y="${s.footer.y}" text-anchor="middle" class="uc06-footer">${this.esc(t(s.footer.key))}</text></g>`;


    svg += `<g id="uc06_col_process">`;
    svg += `<rect id="uc06_lane_process" x="${s.laneProcess.x}" y="${s.laneProcess.y}" width="${s.laneProcess.width}" height="${s.laneProcess.height}" rx="10" fill="url(#uc06_processGrad)" stroke="${D.laneBusinessStroke}" stroke-width="2"/>`;
    svg += `<text x="${s.laneProcess.x + 16}" y="${s.laneProcess.y + 32}" text-anchor="start" class="uc06-lane-label">${this.esc(t('uc06.lane.process'))}</text>`;
    for (const step of s.processSteps) {
      svg += this.processStepBox(step, t, D);
    }
    svg += '</g>';

    svg += `<g id="uc06_container_mixed">`;
    for (const box of s.mixedBoxes) {
      svg += this.mixedBox(box, t, D, recFill, recStroke);
    }
    svg += '</g>';

    svg += `<g id="uc06_col_shopfloor">`;
    svg += `<rect id="uc06_lane_shopfloor" x="${s.laneShopfloor.x}" y="${s.laneShopfloor.y}" width="${s.laneShopfloor.width}" height="${s.laneShopfloor.height}" rx="10" fill="url(#uc06_shopfloorGrad)" stroke="${D.laneShopfloorStroke}" stroke-width="2"/>`;
    svg += `<text x="${s.laneShopfloor.x + s.laneShopfloor.width / 2}" y="${s.laneShopfloor.y + 32}" text-anchor="middle" class="uc06-lane-label">${this.esc(t('uc06.lane.shopfloor'))}</text>`;
    svg += this.shopfloorSourcesBox(s.shopfloorSourcesBox, t, D);
    svg += this.shopfloorTargetsBox(s.shopfloorTargetsBox, t, D);
    svg += '</g>';

    svg += this.connections(s, t, D);
    svg += this.feedbackConnection(s, t, D);

    const sd = s.stepDescription;
    const hlGreen = ORBIS_COLORS.highlightGreen.strong;
    svg += `<g id="uc06_step_description" style="display: none;">`;
    svg += `<rect x="${sd.x - sd.width / 2}" y="${sd.y}" width="${sd.width}" height="${sd.height}" rx="8" ry="8" fill="${hlGreen}" opacity="0.95"/>`;
    svg += `<text id="uc06_step_description_title" x="${sd.x}" y="${sd.y + 28}" text-anchor="middle" font-size="24" font-weight="700" fill="#ffffff"></text>`;
    svg += `<text id="uc06_step_description_text" x="${sd.x}" y="${sd.y + 58}" text-anchor="middle" font-size="16" font-weight="400" fill="#ffffff"></text>`;
    svg += '</g>';

    svg += '</g></svg>';
    return svg;
  }

  private defs(recStroke: string): string {
    const D = ORBIS_COLORS.diagram;
    const nightBlue = ORBIS_COLORS.orbisNightBlue;

    return `<defs>
      <marker id="uc06_arrow" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
        <polygon points="0,0 10,5 0,10" fill="${D.connectionStroke}"/>
      </marker>
      <marker id="uc06_arrow_feedback" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
        <polygon points="0,0 10,5 0,10" fill="${D.laneTraceStroke}"/>
      </marker>
      <linearGradient id="uc06_bgGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="${D.bgGradientStart}"/>
        <stop offset="100%" stop-color="${D.bgGradientEnd}"/>
      </linearGradient>
      <linearGradient id="uc06_processGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="100%" stop-color="${D.laneBusinessFill}"/>
      </linearGradient>
      <linearGradient id="uc06_shopfloorGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="100%" stop-color="${D.laneShopfloorFill}"/>
      </linearGradient>
      <style>
        .uc06-title { font: 700 40px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc06-subtitle { font: 400 22px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc06-footer { font: 400 14px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc06-lane-label { font: 700 18px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc06-step-title { font: 700 22px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc06-step-bullet { font: 400 13px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc06-mixed-title { font: 700 16px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
        .uc06-rec-title { font: 700 18px "Segoe UI",Arial,sans-serif; fill: ${recStroke}; }
        .uc06-sf-title { font: 700 16px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
      </style>
    </defs>`;
  }

  private arrowStepPathHex(x: number, y: number, w: number, h: number): string {
    const tipSize = Math.min(h * 0.35, w * 0.18);
    const leftTipX = x + 2 * tipSize;
    return `M ${x + tipSize} ${y} L ${x + w - tipSize} ${y} L ${x + w} ${y + h / 2} L ${x + w - tipSize} ${y + h} L ${x + tipSize} ${y + h} L ${leftTipX} ${y + h / 2} Z`;
  }

  private processStepBox(step: Uc06ProcessStep, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const bullets = (t(step.bulletsKey) || '').split(/\n/).filter(Boolean);
    const tipSize = Math.min(step.height * 0.35, step.width * 0.18);
    // Innenliegendes Rechteck: links = mittlere Spitze (leftTipX), rechts = oberer/unterer rechter Punkt
    const innerLeft = step.x + 2 * tipSize;
    const innerRight = step.x + step.width - tipSize;
    const innerCenterX = (innerLeft + innerRight) / 2;
    const bulletPad = 8; // Abstand nach der mittleren Spitze
    const titleY = step.y + 42;
    const lineH = 16;
    const bulletStartY = titleY + 24;
    let out = `<g id="uc06_${step.id}">`;
    out += `<path d="${this.arrowStepPathHex(step.x, step.y, step.width, step.height)}" fill="${D.laneBusinessFill}" stroke="${D.laneBusinessStroke}" stroke-width="1.5"/>`;
    out += `<text x="${innerCenterX}" y="${titleY}" text-anchor="middle" class="uc06-step-title">${this.esc(t(step.titleKey))}</text>`;
    bullets.slice(0, 3).forEach((b, i) => {
      out += `<text x="${innerLeft + bulletPad}" y="${bulletStartY + i * lineH}" text-anchor="start" class="uc06-step-bullet">${this.esc(b.replace(/^[•\-\*]\s*/, ''))}</text>`;
    });
    out += '</g>';
    return out;
  }

  private mixedBox(box: Uc06MixedBox, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram, recFill: string, recStroke: string): string {
    const cx = box.x + box.width / 2;
    const toAbs = (p: string) => p;

    if (box.type === 'recommendation') {
      const iconSize = Math.min(56, box.width / 3, box.height / 2);
      const iconY = box.y + (box.height - iconSize) / 2;
      let out = `<g id="uc06_${box.id}">`;
      out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="${recFill}" stroke="${recStroke}" stroke-width="2"/>`;
      const iconPath = toAbs(ICONS.dsp.functions.analytics);
      if (iconPath) {
        out += `<image href="${iconPath}" x="${cx - iconSize / 2}" y="${iconY}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet" opacity="0.9"/>`;
      }
      out += `<text x="${cx}" y="${box.y + 18}" text-anchor="middle" class="uc06-rec-title">${this.esc(t(box.titleKey))}</text>`;
      out += `<text x="${cx}" y="${box.y + box.height - 10}" text-anchor="middle" font-size="11" fill="${recStroke}">${this.esc(t('uc06.mixed.recommend.sub'))}</text>`;
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

    let out = `<g id="uc06_${box.id}">`;
    out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="${fill}" stroke="${stroke}" stroke-width="1.5"/>`;
    out += `<text x="${cx}" y="${titleY}" text-anchor="middle" class="uc06-mixed-title">${this.esc(t(box.titleKey))}</text>`;
    bullets.slice(0, 4).forEach((b, i) => {
      out += `<text x="${cx}" y="${titleY + 22 + i * lineH}" text-anchor="middle" font-size="12" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(b.replace(/^[•\-\*]\s*/, ''))}</text>`;
    });
    const iconPath = toAbs(ICONS.dsp.architecture.edgeBox);
    if (iconPath) {
      const iconSize = Math.min(96, box.width - 24, box.height - 40);
      const iconY = box.y + (box.height - iconSize) / 2;
      out += `<image href="${iconPath}" x="${cx - iconSize / 2}" y="${iconY}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet" opacity="0.9"/>`;
    }
    out += '</g>';
    return out;
  }

  private targetBoxWithSubBoxes(box: Uc06MixedBox, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram, toAbs: (p: string) => string): string {
    const subGap = 12;
    const pad = 14;
    const titleH = 26;
    const subW = 160;
    const totalSubW = 3 * subW + 2 * subGap;
    const subH = box.height - titleH - pad * 2 - 24;
    const subStartX = box.x + (box.width - totalSubW) / 2;
    const iconSize = Math.min(64, subW - 16, subH - 40);

    const subs = [
      { key: 'uc06.mixed.target.mes', icon: ICONS.business.mes },
      { key: 'uc06.mixed.target.erp', icon: ICONS.business.erp },
      { key: 'uc06.mixed.target.planning', icon: ICONS.ui.processFlow },
    ];

    let out = `<g id="uc06_${box.id}">`;
    out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="${D.targetAnalyticsFill}" stroke="${D.targetAnalyticsStroke}" stroke-width="1.5"/>`;
    out += `<text x="${box.x + box.width / 2}" y="${box.y + titleH - 4}" text-anchor="middle" class="uc06-mixed-title">${this.esc(t(box.titleKey))}</text>`;

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

  /** Shopfloor Sources (links): wiederverwendbares Systems & Devices Element wie UC-04 */
  private shopfloorSourcesBox(box: Uc06ShopfloorBox, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
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

    const sysPaths = UC06_SHOPFLOOR_ICONS.systems.map(
      (k) => toAbs((ICONS.shopfloor.systems as Record<string, string>)[k] ?? '')
    );
    const devPaths = UC06_SHOPFLOOR_ICONS.devices.map(
      (k) => toAbs((ICONS.shopfloor.stations as Record<string, string>)[k] ?? '')
    );
    const sysLabels = ['AGV', 'SCADA'];
    const devLabels = ['MILL', 'DRILL', 'AIQS', 'HBW'];

    const figStroke = 'rgba(0,0,0,0.12)';
    const figFill = 'rgba(255,255,255,0.6)';
    const captionPad = 6;

    let out = `<g id="uc06_${box.id}">`;
    out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="${D.laneShopfloorFill}" stroke="${D.laneShopfloorStroke}" stroke-width="1.5"/>`;
    out += `<text x="${box.x + titlePad}" y="${box.y + 26}" text-anchor="start" class="uc06-sf-title">${this.esc(t(box.titleKey))}</text>`;

    const sysCount = sysPaths.filter(Boolean).length;
    const devCount = devPaths.filter(Boolean).length;
    const figGap = 6;
    const innerPad = 10;
    const sysFigW = sysCount > 0 ? (sysBoxW - innerPad * 2 - (sysCount - 1) * figGap) / sysCount : 0;
    const devFigW = devCount > 0 ? (devBoxW - innerPad * 2 - (devCount - 1) * figGap) / devCount : 0;
    const sysFigH = sysCount > 0 ? sysFigW * (5 / 4) : 0;
    const devFigH = devCount > 0 ? devFigW * (5 / 4) : 0;
    const sysIconSize = sysCount > 0 ? Math.min(sysFigW - 8, sysFigH - 18 - captionPad * 2) : 0;
    const devIconSize = devCount > 0 ? Math.min(devFigW - 8, devFigH - 18 - captionPad * 2) : 0;

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
    out += `<text x="${sysBoxX + sysBoxW / 2}" y="${stripY + stripH - 6}" text-anchor="middle" font-size="11" font-weight="600" fill="${ORBIS_COLORS.orbisNightBlue}">${this.esc(t('uc06.sf.systemsLabel'))}</text>`;

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
    out += `<text x="${devBoxX + devBoxW / 2}" y="${stripY + stripH - 6}" text-anchor="middle" font-size="11" font-weight="600" fill="${ORBIS_COLORS.orbisNightBlue}">${this.esc(t('uc06.sf.devicesLabel'))}</text>`;

    out += '</g>';
    return out;
  }

  /** Shopfloor Targets (rechts): Systems & Devices als Optimierungsziel – dieselben Icons wie Sources, gleiche Farbe */
  private shopfloorTargetsBox(box: Uc06ShopfloorTargetsBox, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
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

    const sysPaths = UC06_SHOPFLOOR_ICONS.systems.map(
      (k) => toAbs((ICONS.shopfloor.systems as Record<string, string>)[k] ?? '')
    );
    const devPaths = UC06_SHOPFLOOR_ICONS.devices.map(
      (k) => toAbs((ICONS.shopfloor.stations as Record<string, string>)[k] ?? '')
    );
    const sysLabels = ['AGV', 'SCADA'];
    const devLabels = ['MILL', 'DRILL', 'AIQS', 'HBW'];

    const figStroke = 'rgba(0,0,0,0.12)';
    const figFill = 'rgba(255,255,255,0.6)';
    const captionPad = 6;

    let out = `<g id="uc06_${box.id}">`;
    out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="${D.laneShopfloorFill}" stroke="${D.laneShopfloorStroke}" stroke-width="1.5"/>`;
    out += `<text x="${box.x + box.width / 2}" y="${box.y + 26}" text-anchor="middle" class="uc06-sf-title">${this.esc(t(box.titleKey))}</text>`;

    const sysCount = sysPaths.filter(Boolean).length;
    const devCount = devPaths.filter(Boolean).length;
    const figGap = 6;
    const innerPad = 10;
    const sysFigW = sysCount > 0 ? (sysBoxW - innerPad * 2 - (sysCount - 1) * figGap) / sysCount : 0;
    const devFigW = devCount > 0 ? (devBoxW - innerPad * 2 - (devCount - 1) * figGap) / devCount : 0;
    const sysFigH = sysCount > 0 ? sysFigW * (5 / 4) : 0;
    const devFigH = devCount > 0 ? devFigW * (5 / 4) : 0;
    const sysIconSize = sysCount > 0 ? Math.min(sysFigW - 8, sysFigH - 18 - captionPad * 2) : 0;
    const devIconSize = devCount > 0 ? Math.min(devFigW - 8, devFigH - 18 - captionPad * 2) : 0;

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
    out += `<text x="${sysBoxX + sysBoxW / 2}" y="${stripY + stripH - 6}" text-anchor="middle" font-size="11" font-weight="600" fill="${ORBIS_COLORS.orbisNightBlue}">${this.esc(t('uc06.sf.systemsLabel'))}</text>`;

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
    out += `<text x="${devBoxX + devBoxW / 2}" y="${stripY + stripH - 6}" text-anchor="middle" font-size="11" font-weight="600" fill="${ORBIS_COLORS.orbisNightBlue}">${this.esc(t('uc06.sf.devicesLabel'))}</text>`;

    out += '</g>';
    return out;
  }

  /**
   * Connections an Kanten der Boxen – keine Durchkreuzung.
   * Jeder Pfad startet/endet an der Kante, zu der die Verbindung zeigt.
   */
  private connections(s: Uc06Structure, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const stroke = D.connectionStroke;
    let out = '<g id="uc06_connections">';

    const steps = s.processSteps;
    const mixed = s.mixedBoxes;
    const dsp = mixed[0];
    const recommend = mixed[1];
    const target = mixed[2];
    const sourcesBox = s.shopfloorSourcesBox;
    const targetsBox = s.shopfloorTargetsBox;
    const cy = (y: number, h: number) => y + h / 2;
    const cx = (x: number, w: number) => x + w / 2;

    // Sources Top → DSP Bottom: Kante oben (Shopfloor Sources) zu Kante unten (DSP)
    const sourcesTopCx = sourcesBox.x + sourcesBox.width / 2;
    const sourcesTop = sourcesBox.y;
    const dspBottom = dsp.y + dsp.height;
    const dspCx = cx(dsp.x, dsp.width);
    const wayY1 = (sourcesTop + dspBottom) / 2;
    out += `<path id="uc06_conn_sources_dsp" d="M ${sourcesTopCx} ${sourcesTop} L ${sourcesTopCx} ${wayY1} L ${dspCx} ${wayY1} L ${dspCx} ${dspBottom}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc06_arrow)"/>`;
    out += `<text x="${(sourcesTopCx + dspCx) / 2}" y="${wayY1 + 14}" text-anchor="middle" font-size="11" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc06.conn.kpis'))}</text>`;

    // DSP Right → Recommend Left: Kante rechts (DSP) zu Kante links (Recommend)
    const dspRight = dsp.x + dsp.width;
    const recLeft = recommend.x;
    const recCy = cy(recommend.y, recommend.height);
    out += `<path id="uc06_conn_dsp_recommend" d="M ${dspRight} ${cy(dsp.y, dsp.height)} L ${recLeft} ${recCy}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc06_arrow)"/>`;

    // Recommend Right → Target Left: Kante rechts (Recommend) zu Kante links (Target)
    const recRight = recommend.x + recommend.width;
    const targetLeft = target.x;
    out += `<path id="uc06_conn_recommend_target" d="M ${recRight} ${recCy} L ${targetLeft} ${cy(target.y, target.height)}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc06_arrow)"/>`;
    out += `<text x="${(recRight + targetLeft) / 2}" y="${recCy - 8}" text-anchor="middle" font-size="11" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc06.conn.recommendation'))}</text>`;

    // Recommend Top → Execute Bottom: Kante oben (Recommend) zu Kante unten (Execute)
    const recTop = recommend.y;
    const recCx = cx(recommend.x, recommend.width);
    const executeStep = steps[4];
    const executeBottom = executeStep.y + executeStep.height;
    const executeCx = cx(executeStep.x, executeStep.width);
    const middleY = (recTop + executeBottom) / 2;
    out += `<path id="uc06_conn_recommend_execute" d="M ${recCx} ${recTop} L ${recCx} ${middleY} L ${executeCx} ${middleY} L ${executeCx} ${executeBottom}" stroke="${stroke}" stroke-width="2" stroke-dasharray="8 4" fill="none" marker-end="url(#uc06_arrow)"/>`;

    // Target Bottom → Targets Top: Kante unten (Mixed Target) bis Oberkante der zweiten Shopfloor-Box
    const targetBottom = target.y + target.height;
    const targetCx = cx(target.x, target.width);
    const targetsTopCx = targetsBox.x + targetsBox.width / 2;
    const targetsTopY = targetsBox.y;
    const wayY = (targetBottom + targetsTopY) / 2;
    out += `<path id="uc06_conn_target_targets" d="M ${targetCx} ${targetBottom} L ${targetCx} ${wayY} L ${targetsTopCx} ${wayY} L ${targetsTopCx} ${targetsTopY}" stroke="${stroke}" stroke-width="2" fill="none" marker-end="url(#uc06_arrow)"/>`;
    out += `<text x="${(targetCx + targetsTopCx) / 2}" y="${wayY - 10}" text-anchor="middle" font-size="11" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc06.conn.action'))}</text>`;

    out += '</g>';
    return out;
  }

  private feedbackConnection(s: Uc06Structure, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const steps = s.processSteps;
    const mixed = s.mixedBoxes;
    const target = mixed[2];
    const feedbackStep = steps[5];
    const targetTop = target.y;
    const targetCx = target.x + target.width / 2;
    const feedbackBottom = feedbackStep.y + feedbackStep.height;
    const feedbackCx = feedbackStep.x + feedbackStep.width / 2;
    const wayY = (targetTop + feedbackBottom) / 2;
    const path = `M ${targetCx} ${targetTop} L ${targetCx} ${wayY} L ${feedbackCx} ${wayY} L ${feedbackCx} ${feedbackBottom}`;
    const lblX = (targetCx + feedbackCx) / 2;
    const lblY = wayY + 16;
    return `<g id="uc06_feedback">
      <path d="${path}" stroke="${D.laneTraceStroke}" stroke-width="2" stroke-dasharray="8 4" fill="none" marker-end="url(#uc06_arrow_feedback)"/>
      <text x="${lblX}" y="${lblY}" text-anchor="middle" font-size="11" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc06.feedback'))}</text>
    </g>`;
  }

  private esc(str: string): string {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
}
