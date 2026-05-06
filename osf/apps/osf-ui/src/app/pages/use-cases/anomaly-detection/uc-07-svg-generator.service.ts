import { Injectable } from '@angular/core';
import {
  createUc07Structure,
  type Uc07Structure,
  type Uc07ProcessStep,
  type Uc07MixedBox,
  type Uc07ShopfloorBox,
  type Uc07ShopfloorIconBox,
} from './uc-07-structure.config';
import { ICONS } from '../../../shared/icons/icon.registry';
import { ORBIS_COLORS } from '../../../assets/color-palette';

@Injectable({ providedIn: 'root' })
export class Uc07SvgGeneratorService {
  generateSvg(i18nTexts: Record<string, string>): string {
    const s = createUc07Structure();
    const t = (key: string): string => i18nTexts[key] || key;
    const D = ORBIS_COLORS.diagram;
    const alarmFill = D.nodeParallel;
    const alarmStroke = D.connectionAlert;

    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${s.viewBox.width}" height="${s.viewBox.height}" viewBox="0 0 ${s.viewBox.width} ${s.viewBox.height}">`;
    svg += this.defs(alarmStroke);
    svg += '<g id="uc07_root">';
    svg += `<rect x="0" y="0" width="${s.viewBox.width}" height="${s.viewBox.height}" fill="url(#uc07_bgGrad)"/>`;
    svg += `<g id="uc07_title"><text x="${s.title.x}" y="${s.title.y}" text-anchor="middle" class="uc07-title">${this.esc(t(s.title.key))}</text></g>`;
    svg += `<g id="uc07_subtitle"><text x="${s.subtitle.x}" y="${s.subtitle.y}" text-anchor="middle" class="uc07-subtitle">${this.esc(t(s.subtitle.key))}</text></g>`;
    svg += `<g id="uc07_outcome"><text x="${s.outcome.x}" y="${s.outcome.y}" text-anchor="middle" font-family="Segoe UI" font-weight="600" font-size="16" fill="${ORBIS_COLORS.highlightGreen.strong}">${this.esc(t(s.outcome.key))}</text></g>`;
    svg += `<g id="uc07_footer"><text x="${s.footer.x}" y="${s.footer.y}" text-anchor="middle" class="uc07-footer">${this.esc(t(s.footer.key))}</text></g>`;

    svg += `<g id="uc07_col_process">`;
    svg += `<rect id="uc07_lanes_layer_process" x="${s.laneProcess.x}" y="${s.laneProcess.y}" width="${s.laneProcess.width}" height="${s.laneProcess.height}" rx="10" fill="url(#uc07_processGrad)" stroke="${D.laneBusinessStroke}" stroke-width="2"/>`;
    svg += `<text x="${s.laneProcess.x + 16}" y="${s.laneProcess.y + 32}" text-anchor="start" class="uc07-lane-label">${this.esc(t('uc07.lane.process'))}</text>`;
    for (const step of s.processSteps) svg += this.processStepBox(step, t, D);
    svg += '</g>';

    svg += `<g id="uc07_container_mixed">`;
    for (const box of s.mixedBoxes) svg += this.mixedBox(box, t, D, alarmFill, alarmStroke);
    svg += '</g>';

    svg += `<g id="uc07_col_shopfloor">`;
    svg += `<rect id="uc07_lanes_layer_shopfloor" x="${s.laneShopfloor.x}" y="${s.laneShopfloor.y}" width="${s.laneShopfloor.width}" height="${s.laneShopfloor.height}" rx="10" fill="url(#uc07_shopfloorGrad)" stroke="${D.laneShopfloorStroke}" stroke-width="2"/>`;
    svg += `<text x="${s.laneShopfloor.x + 16}" y="${s.laneShopfloor.y + 32}" text-anchor="start" class="uc07-lane-label">${this.esc(t('uc07.lane.shopfloor'))}</text>`;
    svg += this.shopfloorIconBox(s.shopfloorTriggerBox, t);
    svg += this.signalTriangle(s.shopfloorSignalTriangle, alarmStroke);
    svg += this.shopfloorIconBox(s.shopfloorDetectorBox, t);
    svg += this.shopfloorSystemsDevicesBox(s.shopfloorSystemsDevicesBox, t, D);
    svg += '</g>';

    svg += this.connections(s, t, D);
    svg += this.feedbackConnection(s, t, D);

    const sd = s.stepDescription;
    svg += `<g id="uc07_step_description" style="display: none;">`;
    svg += `<rect x="${sd.x - sd.width / 2}" y="${sd.y}" width="${sd.width}" height="${sd.height}" rx="8" ry="8" fill="${ORBIS_COLORS.highlightGreen.strong}" opacity="0.95"/>`;
    svg += `<text id="uc07_step_description_title" x="${sd.x}" y="${sd.y + 28}" text-anchor="middle" font-size="24" font-weight="700" fill="#ffffff"></text>`;
    svg += `<text id="uc07_step_description_text" x="${sd.x}" y="${sd.y + 58}" text-anchor="middle" font-size="16" font-weight="400" fill="#ffffff"></text>`;
    svg += '</g>';
    svg += '</g></svg>';
    return svg;
  }

  private defs(alarmStroke: string): string {
    const D = ORBIS_COLORS.diagram;
    return `<defs>
      <marker id="uc07_arrow" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><polygon points="0,0 10,5 0,10" fill="${D.connectionStroke}"/></marker>
      <marker id="uc07_arrow_feedback" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><polygon points="0,0 10,5 0,10" fill="${D.laneTraceStroke}"/></marker>
      <linearGradient id="uc07_bgGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${D.bgGradientStart}"/><stop offset="100%" stop-color="${D.bgGradientEnd}"/></linearGradient>
      <linearGradient id="uc07_processGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#ffffff"/><stop offset="100%" stop-color="${D.laneBusinessFill}"/></linearGradient>
      <linearGradient id="uc07_shopfloorGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#ffffff"/><stop offset="100%" stop-color="${D.laneShopfloorFill}"/></linearGradient>
      <style>
        .uc07-title { font: 700 40px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.orbisNightBlue}; }
        .uc07-subtitle { font: 400 22px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc07-lane-label { font: 700 18px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.orbisNightBlue}; }
        .uc07-step-title { font: 700 22px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.orbisNightBlue}; }
        .uc07-step-bullet { font: 400 13px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .uc07-mixed-title { font: 700 16px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.orbisNightBlue}; }
        .uc07-alarm-title { font: 700 18px "Segoe UI",Arial,sans-serif; fill: ${alarmStroke}; }
        .uc07-sf-title { font: 700 16px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.orbisNightBlue}; }
        .uc07-footer { font: 400 16px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.neutralDarkGrey}; }
        .hl { opacity: 1 !important; filter: drop-shadow(0 4px 12px rgba(10, 56, 117, 0.2)); transition: opacity 0.3s ease, filter 0.3s ease; }
        .dim { opacity: 0.5 !important; transition: opacity 0.3s ease; }
        .dim-conn { opacity: 0.35 !important; transition: opacity 0.3s ease; }
        .hidden { display: none !important; }
      </style>
    </defs>`;
  }

  private arrowStepPathHex(x: number, y: number, w: number, h: number): string {
    const tip = Math.min(h * 0.35, w * 0.18);
    return `M ${x + tip} ${y} L ${x + w - tip} ${y} L ${x + w} ${y + h / 2} L ${x + w - tip} ${y + h} L ${x + tip} ${y + h} L ${x + 2 * tip} ${y + h / 2} Z`;
  }

  private processStepBox(step: Uc07ProcessStep, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const bullets = (t(step.bulletsKey) || '').split(/\n/).filter(Boolean);
    const tip = Math.min(step.height * 0.35, step.width * 0.18);
    const left = step.x + 2 * tip;
    const right = step.x + step.width - tip;
    const cx = (left + right) / 2;
    let out = `<g id="uc07_${step.id}">`;
    out += `<path d="${this.arrowStepPathHex(step.x, step.y, step.width, step.height)}" fill="${D.laneBusinessFill}" stroke="${D.laneBusinessStroke}" stroke-width="1.5"/>`;
    out += `<text x="${cx}" y="${step.y + 42}" text-anchor="middle" class="uc07-step-title">${this.esc(t(step.titleKey))}</text>`;
    bullets.slice(0, 3).forEach((b, i) => {
      out += `<text x="${left + 8}" y="${step.y + 66 + i * 16}" text-anchor="start" class="uc07-step-bullet">${this.esc(b.replace(/^[•*-]\s*/, ''))}</text>`;
    });
    out += '</g>';
    return out;
  }

  private mixedBox(box: Uc07MixedBox, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram, alarmFill: string, alarmStroke: string): string {
    const cx = box.x + box.width / 2;
    let out = `<g id="uc07_${box.id}">`;
    if (box.type === 'alarm') {
      const iconSize = Math.min(56, box.width / 3, box.height / 2);
      const gap = 12;
      const start = cx - (iconSize * 2 + gap) / 2;
      const y = box.y + (box.height - iconSize) / 2;
      out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="${alarmFill}" stroke="${alarmStroke}" stroke-width="2"/>`;
      out += `<image href="${ICONS.shopfloor.shared.alarm}" x="${start}" y="${y}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet"/>`;
      out += `<image href="${ICONS.shopfloor.shared.bellAlarm}" x="${start + iconSize + gap}" y="${y}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet"/>`;
      out += `<text x="${cx}" y="${box.y + 18}" text-anchor="middle" class="uc07-alarm-title">${this.esc(t(box.titleKey))}</text>`;
      out += `<text x="${cx}" y="${box.y + box.height - 10}" text-anchor="middle" font-size="11" fill="${alarmStroke}">${this.esc(t('uc07.mixed.alarm.sub'))}</text>`;
      out += '</g>';
      return out;
    }
    if (box.type === 'target') {
      const subW = 200;
      const subH = box.height - 26 - 14 * 2 - 24;
      const sx = box.x + (box.width - subW) / 2;
      const sy = box.y + 26 + 14;
      const iconSize = Math.min(64, subW - 16, subH - 40);
      out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="${D.targetAnalyticsFill}" stroke="${D.targetAnalyticsStroke}" stroke-width="1.5"/>`;
      out += `<text x="${cx}" y="${box.y + 22}" text-anchor="middle" class="uc07-mixed-title">${this.esc(t(box.titleKey))}</text>`;
      out += `<rect x="${sx}" y="${sy}" width="${subW}" height="${subH}" rx="8" fill="rgba(255,255,255,0.7)" stroke="rgba(0,0,0,0.12)" stroke-width="1"/>`;
      out += `<image href="${ICONS.business.crm}" x="${sx + (subW - iconSize) / 2}" y="${sy + (subH - iconSize) / 2}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet"/>`;
      out += `<text x="${sx + subW / 2}" y="${sy + subH - 8}" text-anchor="middle" font-size="15" font-weight="600" fill="${ORBIS_COLORS.orbisNightBlue}">${this.esc(t('uc07.mixed.target.crm'))}</text>`;
      out += '</g>';
      return out;
    }
    const bullets = (box.bulletsKey ? t(box.bulletsKey) : '').split(/\n/).filter(Boolean);
    out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="${D.laneTraceFill}" stroke="${D.laneTraceStroke}" stroke-width="1.5"/>`;
    out += `<text x="${cx}" y="${box.y + 28}" text-anchor="middle" class="uc07-mixed-title">${this.esc(t(box.titleKey))}</text>`;
    bullets.slice(0, 4).forEach((b, i) => {
      out += `<text x="${cx}" y="${box.y + 50 + i * 14}" text-anchor="middle" font-size="12" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(b.replace(/^[•*-]\s*/, ''))}</text>`;
    });
    const iconSize = Math.min(96, box.width - 24, box.height - 40);
    const y = box.y + (box.height - iconSize) / 2;
    out += `<image href="${ICONS.dsp.architecture.edgeBox}" x="${cx - iconSize / 2}" y="${y}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet" opacity="0.9"/>`;
    out += '</g>';
    return out;
  }

  private signalTriangle(area: { x: number; y: number; width: number; height: number }, lineColor: string): string {
    const barCount = 15;
    const minH = 10;
    const maxH = 150;
    const barGap = 3;
    const barW = Math.max(2, (area.width - (barCount - 1) * barGap) / barCount);
    const centerY = area.y + area.height / 2;
    let out = `<g id="uc07_sf_signal_triangle"><rect x="${area.x}" y="${area.y}" width="${area.width}" height="${area.height}" fill="none" stroke="none"/>`;
    for (let i = 0; i < barCount; i++) {
      if (i % 2 !== 0) continue;
      const h = minH + (i / (barCount - 1)) * (maxH - minH);
      const x = area.x + i * (barW + barGap);
      out += `<rect x="${x}" y="${centerY - h / 2}" width="${barW}" height="${h}" rx="2" fill="${lineColor}" stroke="none"/>`;
    }
    out += '</g>';
    return out;
  }

  private shopfloorIconBox(box: Uc07ShopfloorIconBox, t: (k: string) => string): string {
    const label = box.iconKey === 'trigger' ? t('uc07.sf.trigger') : t('uc07.sf.vibrationSensor');
    let out = `<g id="uc07_${box.id}">`;
    out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="rgba(255,255,255,0.7)" stroke="rgba(0,0,0,0.12)" stroke-width="1.5"/>`;
    if (box.iconKey === 'trigger') {
      const iconSize = Math.min(64, box.width - 24, box.height - 44);
      out += `<image href="${ICONS.shopfloor.shared.tuningFork}" x="${box.x + (box.width - iconSize) / 2}" y="${box.y + 20}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet"/>`;
    } else {
      const gap = 14;
      const iconSize = Math.min(80, (box.width - gap - 24) / 2, box.height - 44);
      const totalW = iconSize * 2 + gap;
      const startX = box.x + (box.width - totalW) / 2;
      const iconY = box.y + (box.height - iconSize - 24) / 2;
      out += `<image href="${ICONS.shopfloor.shared.vibrationSensor}" x="${startX}" y="${iconY}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet"/>`;
      out += `<image href="${ICONS.shopfloor.shared.tiltSensor}" x="${startX + iconSize + gap}" y="${iconY}" width="${iconSize}" height="${iconSize}" preserveAspectRatio="xMidYMid meet"/>`;
    }
    out += `<text x="${box.x + box.width / 2}" y="${box.y + box.height - 14}" text-anchor="middle" font-size="12" font-weight="600" fill="${ORBIS_COLORS.orbisNightBlue}">${this.esc(label)}</text>`;
    out += '</g>';
    return out;
  }

  private shopfloorSystemsDevicesBox(box: Uc07ShopfloorBox, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const figStroke = 'rgba(0,0,0,0.12)';
    const figFill = 'rgba(255,255,255,0.6)';
    const stripY = box.y + 44;
    const stripH = box.height - 50;
    const groupGap = 16;
    const contentW = box.width - 14 * 2 - groupGap;
    const sysBoxW = (contentW * 2) / 6;
    const devBoxW = (contentW * 4) / 6;
    const sysBoxX = box.x + 14;
    const devBoxX = sysBoxX + sysBoxW + groupGap;
    const sysPaths = [ICONS.shopfloor.systems.agv, ICONS.shopfloor.systems.scada];
    const devPaths = [ICONS.shopfloor.stations.mill, ICONS.shopfloor.stations.drill, ICONS.shopfloor.stations.aiqs, ICONS.shopfloor.stations.hbw];
    const sysLabels = ['AGV', 'SCADA'];
    const devLabels = ['MILL', 'DRILL', 'AIQS', 'HBW'];
    const sysFigW = (sysBoxW - 10 * 2 - 6) / 2;
    const devFigW = (devBoxW - 10 * 2 - 3 * 6) / 4;
    const sysFigH = sysFigW * (5 / 4);
    const devFigH = devFigW * (5 / 4);
    const sysIcon = Math.min(sysFigW - 8, sysFigH - 30);
    const devIcon = Math.min(devFigW - 8, devFigH - 30);
    let out = `<g id="uc07_${box.id}">`;
    out += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="10" fill="${D.laneShopfloorFill}" stroke="${D.laneShopfloorStroke}" stroke-width="1.5"/>`;
    out += `<text x="${box.x + 14}" y="${box.y + 26}" text-anchor="start" class="uc07-sf-title">${this.esc(t(box.titleKey))}</text>`;
    out += `<rect x="${sysBoxX}" y="${stripY}" width="${sysBoxW}" height="${stripH}" rx="8" fill="rgba(255,255,255,0.5)" stroke="${figStroke}" stroke-width="1"/>`;
    sysPaths.forEach((path, i) => {
      const fx = sysBoxX + 10 + i * (sysFigW + 6);
      const fy = stripY + 10;
      out += `<rect x="${fx}" y="${fy}" width="${sysFigW}" height="${sysFigH}" rx="6" fill="${figFill}" stroke="${figStroke}" stroke-width="1"/>`;
      out += `<image href="${path}" x="${fx + (sysFigW - sysIcon) / 2}" y="${fy + 6}" width="${sysIcon}" height="${sysIcon}" preserveAspectRatio="xMidYMid meet"/>`;
      out += `<text x="${fx + sysFigW / 2}" y="${fy + sysFigH - 6}" text-anchor="middle" font-size="10" font-weight="600" fill="#1e2d3d">${this.esc(sysLabels[i])}</text>`;
    });
    out += `<text x="${sysBoxX + sysBoxW / 2}" y="${stripY + stripH - 6}" text-anchor="middle" font-size="11" font-weight="600" fill="${ORBIS_COLORS.orbisNightBlue}">${this.esc(t('uc07.sf.systemsLabel'))}</text>`;
    out += `<rect x="${devBoxX}" y="${stripY}" width="${devBoxW}" height="${stripH}" rx="8" fill="rgba(255,255,255,0.5)" stroke="${figStroke}" stroke-width="1"/>`;
    devPaths.forEach((path, i) => {
      const fx = devBoxX + 10 + i * (devFigW + 6);
      const fy = stripY + 10;
      out += `<rect x="${fx}" y="${fy}" width="${devFigW}" height="${devFigH}" rx="6" fill="${figFill}" stroke="${figStroke}" stroke-width="1"/>`;
      out += `<image href="${path}" x="${fx + (devFigW - devIcon) / 2}" y="${fy + 6}" width="${devIcon}" height="${devIcon}" preserveAspectRatio="xMidYMid meet"/>`;
      out += `<text x="${fx + devFigW / 2}" y="${fy + devFigH - 6}" text-anchor="middle" font-size="10" font-weight="600" fill="#1e2d3d">${this.esc(devLabels[i])}</text>`;
    });
    out += `<text x="${devBoxX + devBoxW / 2}" y="${stripY + stripH - 6}" text-anchor="middle" font-size="11" font-weight="600" fill="${ORBIS_COLORS.orbisNightBlue}">${this.esc(t('uc07.sf.devicesLabel'))}</text>`;
    out += '</g>';
    return out;
  }

  private connections(s: Uc07Structure, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    let out = '<g id="uc07_connections">';
    const steps = s.processSteps;
    const [dsp, alarm, target] = s.mixedBoxes;
    const detector = s.shopfloorDetectorBox;
    const cy = (y: number, h: number) => y + h / 2;
    const cx = (x: number, w: number) => x + w / 2;
    const detCx = detector.x + detector.width / 2;
    const detTop = detector.y;
    const dspBottom = dsp.y + dsp.height;
    const dspCx = cx(dsp.x, dsp.width);
    const yMid = (detTop + dspBottom) / 2;
    out += `<path id="uc07_conn_sensor_dsp" d="M ${detCx} ${detTop} L ${detCx} ${yMid} L ${dspCx} ${yMid} L ${dspCx} ${dspBottom}" stroke="${D.connectionStroke}" stroke-width="2" fill="none" marker-end="url(#uc07_arrow)"/>`;
    out += `<text x="${(detCx + dspCx) / 2}" y="${yMid + 14}" text-anchor="middle" font-size="11" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc07.conn.signals'))}</text>`;
    out += `<path id="uc07_conn_dsp_alarm" d="M ${dsp.x + dsp.width} ${cy(dsp.y, dsp.height)} L ${alarm.x} ${cy(alarm.y, alarm.height)}" stroke="${D.connectionStroke}" stroke-width="2" fill="none" marker-end="url(#uc07_arrow)"/>`;
    out += `<path id="uc07_conn_alarm_target" d="M ${alarm.x + alarm.width} ${cy(alarm.y, alarm.height)} L ${target.x} ${cy(target.y, target.height)}" stroke="${D.connectionStroke}" stroke-width="2" fill="none" marker-end="url(#uc07_arrow)"/>`;
    out += `<text x="${(alarm.x + alarm.width + target.x) / 2}" y="${cy(alarm.y, alarm.height) - 8}" text-anchor="middle" font-size="11" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc07.conn.alarmEvent'))}</text>`;
    const alarmStep = steps[2];
    const alarmStepCx = cx(alarmStep.x, alarmStep.width);
    const way = (cy(alarm.y, alarm.height) + alarmStep.y + alarmStep.height) / 2;
    out += `<path id="uc07_conn_alarm_process" d="M ${cx(alarm.x, alarm.width)} ${alarm.y} L ${cx(alarm.x, alarm.width)} ${way} L ${alarmStepCx} ${way} L ${alarmStepCx} ${alarmStep.y + alarmStep.height}" stroke="${D.connectionStroke}" stroke-width="2" stroke-dasharray="8 4" fill="none" marker-end="url(#uc07_arrow)"/>`;
    const sf = s.shopfloorSystemsDevicesBox;
    const aCx = cx(alarm.x, alarm.width);
    const sfCy = sf.y + sf.height / 2;
    out += `<path id="uc07_conn_alarm_systems" d="M ${aCx} ${alarm.y + alarm.height} L ${aCx} ${sfCy} L ${sf.x} ${sfCy}" stroke="${D.connectionStroke}" stroke-width="2" fill="none" marker-end="url(#uc07_arrow)"/>`;
    out += `<text x="${(aCx + sf.x) / 2}" y="${sfCy - 10}" text-anchor="middle" font-size="11" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc07.conn.productionPause'))}</text>`;
    out += '</g>';
    return out;
  }

  private feedbackConnection(s: Uc07Structure, t: (k: string) => string, D: typeof ORBIS_COLORS.diagram): string {
    const target = s.mixedBoxes[2];
    const feedback = s.processSteps[4];
    const targetCx = target.x + target.width / 2;
    const feedbackCx = feedback.x + feedback.width / 2;
    const yMid = (target.y + feedback.y + feedback.height) / 2;
    const path = `M ${targetCx} ${target.y} L ${targetCx} ${yMid} L ${feedbackCx} ${yMid} L ${feedbackCx} ${feedback.y + feedback.height}`;
    return `<g id="uc07_feedback"><path d="${path}" stroke="${D.laneTraceStroke}" stroke-width="2" stroke-dasharray="8 4" fill="none" marker-end="url(#uc07_arrow_feedback)"/><text x="${(targetCx + feedbackCx) / 2}" y="${yMid + 16}" text-anchor="middle" font-size="11" fill="${ORBIS_COLORS.neutralDarkGrey}">${this.esc(t('uc07.feedback'))}</text></g>`;
  }

  private esc(str: string): string {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
}
