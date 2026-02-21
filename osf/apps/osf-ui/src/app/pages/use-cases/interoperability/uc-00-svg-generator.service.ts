import { Injectable } from '@angular/core';
import { getAssetPath } from '../../../assets/detail-asset-map';
import { createUc00Structure, type Uc00Structure, type Uc00Chip, type Uc00Lane, type Uc00Column } from './uc-00-structure.config';
import { ORBIS_COLORS } from '../../../assets/color-palette';

/**
 * Service for generating UC-00 SVG dynamically with I18n support
 * Uses improved visual design with ORBIS-CI colors
 */
@Injectable({ providedIn: 'root' })
export class Uc00SvgGeneratorService {
  generateSvg(i18nTexts: Record<string, string>): string {
    const structure = createUc00Structure();
    const getText = (key: string): string => i18nTexts[key] || key;
    
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${structure.viewBox.width}" height="${structure.viewBox.height}" viewBox="0 0 ${structure.viewBox.width} ${structure.viewBox.height}">`;
    svg += this.generateDefs();
    svg += '<g id="uc00_root">';
    svg += `<defs>
      <linearGradient id="frameGradient" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" style="stop-color:#fafbfc;stop-opacity:1" />
        <stop offset="100%" style="stop-color:#ffffff;stop-opacity:1" />
      </linearGradient>
    </defs>`;
    svg += `<rect class="frame" x="0" y="0" width="${structure.viewBox.width}" height="${structure.viewBox.height}" fill="url(#frameGradient)"/>`;
    svg += `<g id="uc00_title"><text x="${structure.title.x}" y="${structure.title.y}" text-anchor="middle" class="title">${this.escapeXml(getText(structure.title.key))}</text></g>`;
    svg += `<g id="uc00_subtitle"><text x="${structure.subtitle.x}" y="${structure.subtitle.y}" text-anchor="middle" class="subtitle">${this.escapeXml(getText(structure.subtitle.key))}</text></g>`;
    const sd = structure.stepDescription;
    const highlightGreenStrong = ORBIS_COLORS.highlightGreen.strong;
    svg += `<g id="uc00_step_description" class="step-description-overlay" style="display: none;">`;
    svg += `<rect x="${sd.x - sd.width / 2}" y="${sd.y}" width="${sd.width}" height="${sd.height}" rx="8" ry="8" fill="${highlightGreenStrong}" opacity="0.95" class="step-description__bg"/>`;
    svg += `<text id="uc00_step_description_title" x="${sd.x}" y="${sd.y + 28}" text-anchor="middle" font-size="24" font-weight="700" fill="#ffffff" class="step-description__title"></text>`;
    svg += `<text id="uc00_step_description_text" x="${sd.x}" y="${sd.y + 58}" text-anchor="middle" font-size="16" font-weight="400" fill="#ffffff" class="step-description__text"></text>`;
    svg += '</g>';
    svg += '<g id="uc00_columns">';
    svg += this.generateSourcesColumn(structure.columns.sources, getText);
    svg += `<g id="uc00_arrow_sources_to_dsp">`;
    const sourcesCol = structure.columns.sources;
    const dspCol = structure.columns.dsp.column;
    const orbisBlueStrong = ORBIS_COLORS.orbisBlue.strong;
    svg += `<line x1="${sourcesCol.x + sourcesCol.width}" y1="${sourcesCol.y + sourcesCol.height / 2}" x2="${dspCol.x}" y2="${dspCol.y + dspCol.height / 2}" stroke="${orbisBlueStrong}" stroke-width="4" stroke-dasharray="8 4" opacity="0.6" marker-end="url(#arrow-down)"/>`;
    svg += '</g>';
    svg += this.generateDspColumn(structure.columns.dsp, getText);
    svg += this.generateTargetsColumn(structure.columns.targets, getText);
    svg += '</g>';
    svg += '</g>';
    svg += '</svg>';
    return svg;
  }
  
  private generateDefs(): string {
    const orbisBlueStrong = ORBIS_COLORS.orbisBlue.strong;
    return `
  <defs>
    <marker id="arrow-down" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto">
      <polygon points="0,0 12,6 0,12" fill="${orbisBlueStrong}"/>
    </marker>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
      <feOffset dx="2" dy="2" result="offsetblur"/>
      <feComponentTransfer><feFuncA type="linear" slope="0.15"/></feComponentTransfer>
      <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="shadow-light" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="2"/>
      <feOffset dx="1" dy="1" result="offsetblur"/>
      <feComponentTransfer><feFuncA type="linear" slope="0.1"/></feComponentTransfer>
      <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      :root { --stroke: var(--orbis-blue-strong); --muted: var(--orbis-grey-medium); --bg: #ffffff; --panel: var(--orbis-grey-light); --accent: var(--highlight-green-medium);
        --uc-col-dsp-bg: rgba(var(--orbis-blue-strong-rgb), 0.1); --uc-col-dsp-border: rgba(var(--orbis-blue-strong-rgb), 0.2);
        --uc-col-sources-bg: #ffffff; --uc-col-targets-bg: #ffffff; --uc-col-border: rgba(var(--orbis-blue-strong-rgb), 0.1);
        --uc-panel-bg: rgba(var(--orbis-grey-light-rgb), 0.9); --uc-panel-border: rgba(var(--orbis-grey-medium-rgb), 0.1);
        --uc-lane-bg: rgba(255, 255, 255, 0.6); --uc-lane-border: rgba(var(--orbis-blue-strong-rgb), 0.08); }
      .frame { fill: var(--bg); }
      .panel { fill: var(--panel); stroke: var(--orbis-grey-light); stroke-width: 1.5; filter: url(#shadow-light); }
      .panel-dsp { fill: var(--uc-col-dsp-bg); stroke: var(--uc-col-dsp-border); stroke-width: 1.5; filter: url(#shadow-light); }
      .title { font: 700 40px "Segoe UI", Arial, sans-serif; fill: var(--orbis-nightblue); letter-spacing: -0.3px; }
      .subtitle { font: 400 22px "Segoe UI", Arial, sans-serif; fill: var(--muted); }
      .h2 { font: 700 26px "Segoe UI", Arial, sans-serif; fill: var(--orbis-nightblue); letter-spacing: -0.3px; }
      .p { font: 400 20px "Segoe UI", Arial, sans-serif; fill: var(--orbis-nightblue); }
      .small { font: 400 18px "Segoe UI", Arial, sans-serif; fill: var(--orbis-nightblue); }
      .chipText { font: 400 16px "Segoe UI", Arial, sans-serif; fill: var(--orbis-nightblue); }
      .muted { fill: var(--muted); }
      .chip { fill: #ffffff; stroke: var(--orbis-grey-light); stroke-width: 1.5; filter: url(#shadow-light); }
      .lane { fill: var(--uc-lane-bg); stroke: var(--uc-lane-border); stroke-width: 1; }
      .statusDot { r: 5; }
      .statusRunning { fill: var(--status-success-strong); }
      .statusIdle { fill: var(--status-warning-medium); }
      .statusFail { fill: var(--status-error-strong); }
      .badgePass { fill: rgba(var(--status-success-strong-rgb), 0.1); stroke: var(--status-success-strong); stroke-width: 1.5; }
      .badgeFail { fill: rgba(var(--status-error-strong-rgb), 0.1); stroke: var(--status-error-strong); stroke-width: 1.5; }
      .stepBox { fill: #ffffff; stroke: var(--orbis-grey-light); stroke-width: 1.5; filter: url(#shadow-light); }
      .stepBar { fill: #ffffff; stroke: var(--orbis-grey-light); stroke-width: 1.5; }
      .hl { opacity: 1; filter: drop-shadow(0 4px 12px rgba(var(--orbis-blue-strong-rgb), 0.2)); }
      .dim { opacity: 0.5; }
      .hidden { display: none; }
    </style>
  </defs>`;
  }
  
  private generateSourcesColumn(column: Uc00Column, getText: (key: string) => string): string {
    const sourcesFill = ORBIS_COLORS.diagram.laneShopfloorFill;
    let svg = `<g id="uc00_col_sources">`;
    svg += `<rect x="${column.x}" y="${column.y}" width="${column.width}" height="${column.height}" rx="20" ry="20" fill="${sourcesFill}" stroke="${ORBIS_COLORS.orbisGrey.light}" stroke-width="1.5"/>`;
    svg += `<text x="${column.headerX}" y="${column.headerY}" class="h2">${this.escapeXml(getText(column.headerKey))}</text>`;
    column.lanes.forEach((lane: Uc00Lane) => { svg += this.generateLane(lane, getText); });
    svg += '</g>';
    return svg;
  }
  
  private generateLane(lane: Uc00Lane, getText: (key: string) => string): string {
    let svg = `<g id="uc00_lane_${lane.id}">`;
    svg += `<rect class="lane" x="${lane.x}" y="${lane.y}" width="${lane.width}" height="${lane.height}" rx="14" ry="14"/>`;
    svg += `<text x="${lane.x! + 50}" y="${lane.y! + 30}" class="p" font-weight="600">${this.escapeXml(getText(lane.titleKey))}</text>`;
    const iconPath = getAssetPath(lane.iconPath.replace(/^\//, ''));
    const iconX = lane.x! + lane.width! - lane.iconWidth - 10;
    const iconY = lane.y! + 28;
    svg += `<g id="uc00_lane_${lane.id}_icon" transform="translate(${iconX},${iconY})">`;
    svg += `<rect width="${lane.iconWidth}" height="${lane.iconHeight}" rx="12" ry="12" fill="#ffffff" stroke="${ORBIS_COLORS.orbisGrey.light}" stroke-width="1.5"/>`;
    svg += `<image href="${iconPath}" x="10" y="10" width="${lane.iconWidth - 20}" height="${lane.iconHeight - 20}" preserveAspectRatio="xMidYMid meet" opacity="0.9"/>`;
    svg += '</g>';
    svg += `<g id="uc00_lane_${lane.id}_events">`;
    lane.chips.forEach((chip) => { svg += this.generateChip(chip, lane, getText); });
    svg += '</g></g>';
    return svg;
  }
  
  private generateChip(chip: Uc00Chip, lane: Uc00Lane, getText: (key: string) => string): string {
    let svg = `<g id="uc00_chip_${chip.id}">`;
    const chipX = chip.x;
    const chipY = chip.y;
    if (chip.fill && chip.stroke) {
      const fillClass = chip.fill === '#e8f5e9' ? 'badgePass' : 'badgeFail';
      svg += `<rect class="${fillClass}" x="${chipX}" y="${chipY}" width="${chip.width}" height="${chip.height}"/>`;
      svg += `<text x="${chipX + chip.width / 2}" y="${chipY + chip.height / 2 + 5}" text-anchor="middle" class="chipText" fill="${chip.fill === '#e8f5e9' ? ORBIS_COLORS.statusSuccess.strong : ORBIS_COLORS.statusError.strong}">${this.escapeXml(getText(chip.textKey))}</text>`;
      svg += '</g>';
      return svg;
    }
    if (chip.width === 0 && chip.height === 0) {
      svg += `<text x="${chipX}" y="${chipY}" class="chipText">${this.escapeXml(getText(chip.textKey))}</text></g>`;
      return svg;
    }
    svg += `<rect class="chip" x="${chipX}" y="${chipY}" width="${chip.width}" height="${chip.height}" rx="12" ry="12"/>`;
    if (chip.statusDots && chip.statusLabels && chip.statusLabels.length > 0) {
      svg += `<text x="${chipX + 10}" y="${chipY + 17}" class="chipText" font-weight="600">${this.escapeXml(getText(chip.textKey))}</text>`;
      chip.statusDots.forEach((dot, index) => {
        if (index < chip.statusLabels!.length) {
          const dotY = chipY + 40 + (index * 25);
          const colorClass = `status${dot.color.charAt(0).toUpperCase() + dot.color.slice(1)}`;
          svg += `<circle class="statusDot ${colorClass}" cx="${chipX + 40}" cy="${dotY}" r="5"/>`;
          svg += `<text x="${chipX + 50}" y="${chipY + 47 + (index * 25)}" class="chipText">${this.escapeXml(getText(chip.statusLabels![index]))}</text>`;
        }
      });
    } else {
      if (chip.multiline && chip.textLines) {
        chip.textLines.forEach((lineKey, index) => {
          const lineY = chipY + 17 + (index * 20);
          const textX = index === 0 ? chipX + 10 : chipX + 30;
          const textContent = this.escapeXml(getText(lineKey));
          svg += `<text x="${textX}" y="${lineY}" class="chipText" ${index === 0 ? 'font-weight="600"' : ''}>${textContent}</text>`;
          if (chip.operationIcons) {
            const op = chip.operationIcons.find(i => i.lineIndex === index + 1);
            if (op) {
              const ip = getAssetPath(op.iconPath.replace(/^\//, ''));
              const iconX = textX + textContent.length * 5 + op.offsetX;
              svg += `<image href="${ip}" x="${iconX}" y="${lineY + op.offsetY}" width="${op.iconWidth}" height="${op.iconHeight}" preserveAspectRatio="xMidYMid meet" opacity="0.9"/>`;
            }
          }
        });
      } else {
        svg += `<text x="${chipX + 10}" y="${chipY + 20}" class="chipText">${this.escapeXml(getText(chip.textKey))}</text>`;
      }
    }
    if (chip.iconPath && chip.iconX !== undefined && chip.iconY !== undefined) {
      const ip = getAssetPath(chip.iconPath.replace(/^\//, ''));
      const iconOffsetX = chip.iconX - chip.x;
      const iconOffsetY = chip.iconY - chip.y;
      svg += `<image href="${ip}" x="${chipX + iconOffsetX}" y="${chipY + iconOffsetY}" width="${chip.iconWidth}" height="${chip.iconHeight}" preserveAspectRatio="xMidYMid meet" opacity="0.85"/>`;
    }
    svg += '</g>';
    return svg;
  }
  
  private generateDspColumn(dsp: { column: { x: number; y: number; width: number; height: number; headerX: number; headerY: number; headerKey: string }; steps: Array<{ id: string; x: number; y: number; width: number; height: number; titleKey: string; descriptionKey: string }>; bars: Array<{ id: string; x: number; y: number; width: number; height: number; textKey: string; textLines?: string[]; multiline?: boolean }> }, getText: (key: string) => string): string {
    let svg = `<g id="uc00_col_dsp">`;
    svg += `<rect class="panel-dsp" x="${dsp.column.x}" y="${dsp.column.y}" width="${dsp.column.width}" height="${dsp.column.height}" rx="20" ry="20"/>`;
    svg += `<text x="${dsp.column.headerX}" y="${dsp.column.headerY}" class="h2">${this.escapeXml(getText(dsp.column.headerKey))}</text>`;
    dsp.steps.forEach((step, stepIndex) => {
      svg += `<g id="uc00_step_${step.id}">`;
      svg += `<rect class="stepBox" x="${step.x}" y="${step.y}" width="${step.width}" height="${step.height}" rx="14" ry="14"/>`;
      svg += `<text x="${step.x + step.width / 2}" y="${step.y + 50}" text-anchor="middle" class="p"><tspan font-weight="700">${this.escapeXml(getText(step.titleKey))}</tspan></text>`;
      svg += `<text x="${step.x + step.width / 2}" y="${step.y + 85}" text-anchor="middle" class="small muted">${this.escapeXml(getText(step.descriptionKey))}</text></g>`;
      if (stepIndex < dsp.steps.length - 1) {
        const next = dsp.steps[stepIndex + 1];
        const arrowX = step.x + step.width / 2;
        const arrowTopY = step.y + step.height + 5;
        const arrowBottomY = next.y - 5;
        const arrowheadBaseWidth = (arrowBottomY - arrowTopY) * 1.4;
        svg += `<polygon points="${arrowX},${arrowBottomY} ${arrowX - arrowheadBaseWidth / 2},${arrowTopY} ${arrowX + arrowheadBaseWidth / 2},${arrowTopY}" fill="${ORBIS_COLORS.orbisBlue.strong}" opacity="0.9"/>`;
      }
    });
    (dsp.bars || []).forEach((bar) => { svg += this.generateBar(bar, getText); });
    svg += '</g>';
    return svg;
  }
  
  private generateBar(bar: { id: string; x: number; y: number; width: number; height: number; textKey: string; textLines?: string[]; multiline?: boolean }, getText: (key: string) => string): string {
    const barId = bar.id === 'foundation' ? 'basis' : bar.id;
    let svg = `<g id="uc00_bar_${barId}">`;
    svg += `<rect class="stepBar" x="${bar.x}" y="${bar.y}" width="${bar.width}" height="${bar.height}" rx="12" ry="12"/>`;
    if (bar.multiline && bar.textLines) {
      bar.textLines.forEach((lineKey, index) => {
        svg += `<text x="${bar.x + bar.width / 2}" y="${bar.y + 27 + (index * 30)}" text-anchor="middle" class="small">${this.escapeXml(getText(lineKey))}</text>`;
      });
    } else {
      svg += `<text x="${bar.x + bar.width / 2}" y="${bar.y + bar.height / 2 + 5}" text-anchor="middle" class="small">${this.escapeXml(getText(bar.textKey))}</text>`;
    }
    svg += '</g>';
    return svg;
  }
  
  private generateTargetsColumn(targets: any, getText: (key: string) => string): string {
    const targetsFill = ORBIS_COLORS.diagram.targetAnalyticsFill;
    const targetsStroke = ORBIS_COLORS.diagram.targetAnalyticsStroke;
    let svg = `<g id="uc00_col_targets">`;
    svg += `<rect x="${targets.column.x}" y="${targets.column.y}" width="${targets.column.width}" height="${targets.column.height}" rx="20" ry="20" fill="${targetsFill}" stroke="${targetsStroke}" stroke-width="1.5"/>`;
    (targets.sectionHeaders || []).forEach((h: { key: string; x: number; y: number }, i: number) => {
      const ids = ['uc00_section_process_view', 'uc00_section_target_systems', 'uc00_section_use_cases'];
      svg += `<g id="${ids[i] || `uc00_section_${i}`}"><text x="${h.x}" y="${h.y}" text-anchor="start" class="p" font-weight="600">${this.escapeXml(getText(h.key))}</text></g>`;
    });
    const pv = targets.processViewBox;
    svg += `<g id="uc00_process_view_box">`;
    svg += `<rect class="stepBox" x="${pv.x}" y="${pv.y}" width="${pv.width}" height="${pv.height}" rx="14" ry="14" fill="#ffffff"/>`;
    svg += `<text x="${pv.x + pv.width / 2}" y="${pv.y + 35}" text-anchor="middle" class="p" font-weight="700">${this.escapeXml(getText(pv.titleKey))}</text>`;
    svg += `<g id="uc00_process_timeline">`;
    svg += `<line x1="${pv.timeline.lineX1}" y1="${pv.timeline.lineY}" x2="${pv.timeline.lineX2}" y2="${pv.timeline.lineY}" stroke="${ORBIS_COLORS.orbisGrey.light}" stroke-width="10" stroke-linecap="round" opacity="0.6"/>`;
    svg += `<g id="uc00_process_icons">`;
    pv.timeline.points.forEach((point: any) => {
      const ip = getAssetPath(point.iconPath.replace(/^\//, ''));
      svg += `<circle cx="${point.x}" cy="${point.y}" r="10" fill="${ORBIS_COLORS.highlightGreen.medium}" opacity="0.9"/>`;
      svg += `<image href="${ip}" x="${point.iconX}" y="${point.iconY}" width="${point.iconWidth}" height="${point.iconHeight}" preserveAspectRatio="xMidYMid meet" opacity="0.9"/>`;
      svg += `<text x="${point.x}" y="${point.labelY}" text-anchor="middle" class="small">${this.escapeXml(getText(point.labelKey))}</text>`;
    });
    svg += '</g></g></g>';
    const targetBoxFill = 'rgba(255,255,255,0.7)';
    const targetBoxStroke = 'rgba(0,0,0,0.12)';
    svg += `<g id="uc00_targets_systems">`;
    targets.targets.forEach((target: any) => {
      const ip = getAssetPath(target.iconPath.replace(/^\//, ''));
      svg += `<g id="uc00_target_${target.id}">`;
      svg += `<rect x="${target.x}" y="${target.y}" width="${target.width}" height="${target.height}" rx="14" ry="14" fill="${targetBoxFill}" stroke="${targetBoxStroke}" stroke-width="1"/>`;
      svg += `<image href="${ip}" x="${target.iconX}" y="${target.iconY}" width="${target.iconWidth}" height="${target.iconHeight}" preserveAspectRatio="xMidYMid meet" opacity="0.85"/>`;
      svg += `<text x="${target.x + target.width / 2}" y="${target.labelY}" text-anchor="middle" class="p">${this.escapeXml(getText(target.labelKey))}</text></g>`;
    });
    svg += `<text id="uc00_target_note_best_of_breed" x="${targets.noteX}" y="${targets.noteY}" class="small muted">${this.escapeXml(getText(targets.noteKey))}</text></g>`;
    const outcomeFill = ORBIS_COLORS.highlightGreen.light;
    const outcomeStroke = ORBIS_COLORS.highlightGreen.medium;
    svg += `<g id="uc00_outcomes">`;
    (targets.outcomeBoxes || []).forEach((box: { id: string; x: number; y: number; width: number; height: number; iconPath: string; iconSize: number; titleKey: string; titleLine2Key?: string }) => {
      const ip = getAssetPath(box.iconPath.replace(/^\//, ''));
      const topPadding = 10;
      const titleLineHeight = 18;
      const titleLines = box.titleLine2Key ? 2 : 1;
      const titleHeight = topPadding + titleLines * titleLineHeight + 8;
      const iconX = box.x + (box.width - box.iconSize) / 2;
      const iconAreaHeight = box.height - titleHeight;
      const iconY = box.y + titleHeight + (iconAreaHeight - box.iconSize) / 2;
      svg += `<g id="uc00_outcome_${box.id}">`;
      svg += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="12" ry="12" fill="${outcomeFill}" stroke="${outcomeStroke}" stroke-width="1.5"/>`;
      svg += `<text x="${box.x + box.width / 2}" y="${box.y + topPadding + 14}" text-anchor="middle" class="small" font-weight="600">`;
      svg += `<tspan x="${box.x + box.width / 2}" dy="0">${this.escapeXml(getText(box.titleKey))}</tspan>`;
      if (box.titleLine2Key) {
        svg += `<tspan x="${box.x + box.width / 2}" dy="${titleLineHeight}">${this.escapeXml(getText(box.titleLine2Key))}</tspan>`;
      }
      svg += '</text>';
      svg += `<image href="${ip}" x="${iconX}" y="${iconY}" width="${box.iconSize}" height="${box.iconSize}" preserveAspectRatio="xMidYMid meet" opacity="0.9"/>`;
      svg += '</g>';
    });
    svg += '</g></g>';
    return svg;
  }
  
  private escapeXml(text: string): string {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');
  }
}
