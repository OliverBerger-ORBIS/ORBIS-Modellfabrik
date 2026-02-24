import { Injectable } from '@angular/core';
import {
  createUc01Structure,
  UC01_COLORS,
  type Uc01Structure,
  type Uc01Lane,
  type Uc01StationNode,
  type Uc01Badge,
  type Uc01Box,
  type Uc01Connection,
  type Uc01Phase,
} from './uc-01-structure.config';
import { ORBIS_COLORS } from '../../../assets/color-palette';

/**
 * Service for generating UC-01 Track & Trace Genealogy SVG (Partiture layout)
 *
 * Generates a 1920×1080 SVG based on the Draw.io Partiture design:
 *   3 horizontal lanes, NFC thread, station nodes, business/enrichment boxes,
 *   join/AGV connections, phase brackets, legend, abbreviations.
 *
 * All text keys are resolved via I18n at generation time.
 * SVG element IDs use uc01_ prefix for animation targeting.
 */
@Injectable({ providedIn: 'root' })
export class Uc01SvgGeneratorService {

  generateSvg(i18nTexts: Record<string, string>): string {
    const s = createUc01Structure();
    const t = (key: string): string => i18nTexts[key] || key;

    let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${s.viewBox.width} ${s.viewBox.height}" width="${s.viewBox.width}" height="${s.viewBox.height}">`;

    svg += this.defs();
    svg += '<g id="uc01_root">';

    // Frame
    svg += `<rect x="0" y="0" width="${s.viewBox.width}" height="${s.viewBox.height}" fill="url(#uc01_bgGrad)" rx="0"/>`;

    // Title
    svg += `<g id="uc01_title"><text x="${s.title.x}" y="${s.title.y}" text-anchor="middle" class="uc01-title">${this.esc(t(s.title.key))}</text></g>`;

    // Subtitle (shown in step 0, replaced by step description later)
    svg += `<g id="uc01_subtitle"><text x="${s.subtitle.x}" y="${s.subtitle.y}" text-anchor="middle" class="uc01-subtitle">${this.esc(t(s.subtitle.key))}</text></g>`;

    // Outcome (shown constantly)
    const highlightGreenStrong = ORBIS_COLORS.highlightGreen.strong;
    svg += `<g id="uc01_outcome"><text x="${s.outcome.x}" y="${s.outcome.y}" text-anchor="middle" font-family="Segoe UI" font-weight="600" font-size="16" fill="${highlightGreenStrong}">${this.esc(t(s.outcome.key))}</text></g>`;

    // Footer (Disclaimer)
    svg += `<g id="uc01_footer"><text x="${s.footer.x}" y="${s.footer.y}" text-anchor="middle" class="uc01-footer">${this.esc(t(s.footer.key))}</text></g>`;


    // Step description overlay
    svg += this.stepDescriptionOverlay(s);

    // Lanes (backgrounds + titles)
    svg += this.lanes(s, t);

    // Time arrow
    svg += `<g id="uc01_time_arrow"><text x="${s.timeArrow.x}" y="${s.timeArrow.y}" class="uc01-lane-title" font-style="italic">${this.esc(t(s.timeArrow.key))}</text></g>`;

    // Phase brackets
    svg += this.phases(s, t);

    // Connections (behind nodes)
    svg += this.connections(s);

    // NFC Thread
    svg += this.thread(s, t);

    // Station Nodes
    svg += this.stationNodes(s, t);

    // Badges
    svg += this.badges(s);

    // Business Boxes
    svg += this.boxes(s.businessBoxes, 'uc01_business', 'uc01_biz', t);

    // Enrichment Boxes
    svg += this.boxes(s.enrichmentBoxes, 'uc01_enrichment', 'uc01_enrich', t);

    // Legend
    svg += this.legend(s, t);

    // Abbreviations
    svg += this.abbreviations(s, t);

    svg += '</g></svg>';
    return svg;
  }

  // ───── Defs ─────

  private defs(): string {
    const nightBlue = ORBIS_COLORS.orbisNightBlue;
    const blueStrong = ORBIS_COLORS.orbisBlue.strong;
    const D = ORBIS_COLORS.diagram;
    const C = UC01_COLORS;

    return `<defs>
  <linearGradient id="uc01_bgGrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="${D.bgGradientStart}"/>
    <stop offset="100%" stop-color="${D.bgGradientEnd}"/>
  </linearGradient>
  <filter id="uc01_shadow" x="-4%" y="-4%" width="108%" height="108%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="2"/>
    <feOffset dx="1" dy="1"/>
    <feComponentTransfer><feFuncA type="linear" slope="0.12"/></feComponentTransfer>
    <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <style>
    .uc01-title { font: 700 28px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-subtitle { font: 400 18px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.orbisGrey.medium}; }
    .uc01-lane-title { font: 700 15px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-node-label { font: 700 12px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-box-text { font: 700 12px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-badge-text { font: 700 11px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-phase-text { font: 600 13px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-legend-text { font: 400 11px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-legend-title { font: 700 12px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-abbr-text { font: 400 11px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-thread-label { font: 700 12px "Segoe UI",Arial,sans-serif; fill: ${C.threadCyan}; }
    .uc01-step-title { font: 700 22px "Segoe UI",Arial,sans-serif; fill: #ffffff; }
    .uc01-step-text { font: 400 14px "Segoe UI",Arial,sans-serif; fill: #ffffff; }
    /* Animation classes */
    .hl { opacity: 1; filter: drop-shadow(0 3px 8px rgba(21,65,148,0.18)); transition: opacity 0.3s, filter 0.3s; }
    .dim { opacity: 0.5; transition: opacity 0.3s; }
    .hidden { display: none; }
  </style>
</defs>`;
  }

  // ───── Step Description Overlay ─────

  private stepDescriptionOverlay(s: Uc01Structure): string {
    const sd = s.stepDescription;
    const bg = ORBIS_COLORS.highlightGreen.strong;
    return `<g id="uc01_step_description" style="display:none;">
  <rect x="${sd.x - sd.width / 2}" y="${sd.y}" width="${sd.width}" height="${sd.height}" rx="8" fill="${bg}" opacity="0.92"/>
  <text id="uc01_step_description_title" x="${sd.x}" y="${sd.y + 28}" text-anchor="middle" class="uc01-step-title"></text>
  <text id="uc01_step_description_text" x="${sd.x}" y="${sd.y + 58}" text-anchor="middle" class="uc01-step-text"></text>
</g>`;
  }

  // ───── Lanes ─────

  private lanes(s: Uc01Structure, t: (k: string) => string): string {
    let svg = '<g id="uc01_lanes">';
    s.lanes.forEach((lane: Uc01Lane) => {
      svg += `<g id="uc01_lane_${lane.id}">`;
      svg += `<rect x="${lane.x}" y="${lane.y}" width="${lane.width}" height="${lane.height}" rx="${lane.rx}" fill="${lane.fill}" stroke="${lane.stroke}" stroke-width="1.5" filter="url(#uc01_shadow)"/>`;
      svg += `<text x="${lane.titleX}" y="${lane.titleY}" class="uc01-lane-title">${this.esc(t(lane.titleKey))}</text>`;
      svg += '</g>';
    });
    svg += '</g>';
    return svg;
  }

  // ───── Phases ─────

  private phases(s: Uc01Structure, t: (k: string) => string): string {
    let svg = '<g id="uc01_phases">';
    s.phases.forEach((phase: Uc01Phase) => {
      const x1 = phase.bracketX;
      const x2 = phase.bracketX + phase.bracketWidth;
      const y = phase.bracketY;
      const mid = x1 + phase.bracketWidth / 2;

      svg += `<g id="uc01_${phase.id}">`;
      const bracketColor = ORBIS_COLORS.neutralDarkGrey;
      // Horizontal bracket line
      svg += `<line x1="${x1}" y1="${y + 10}" x2="${x2}" y2="${y + 10}" stroke="${bracketColor}" stroke-width="1" opacity="0.5"/>`;
      // End ticks
      svg += `<line x1="${x1}" y1="${y + 5}" x2="${x1}" y2="${y + 15}" stroke="${bracketColor}" stroke-width="1" opacity="0.5"/>`;
      svg += `<line x1="${x2}" y1="${y + 5}" x2="${x2}" y2="${y + 15}" stroke="${bracketColor}" stroke-width="1" opacity="0.5"/>`;
      // Center tick
      svg += `<line x1="${mid}" y1="${y + 10}" x2="${mid}" y2="${y + 18}" stroke="${bracketColor}" stroke-width="1" opacity="0.5"/>`;
      // Label
      svg += `<text x="${mid}" y="${y + 1}" text-anchor="middle" class="uc01-phase-text">${this.esc(t(phase.textKey))}</text>`;
      svg += '</g>';
    });
    svg += '</g>';
    return svg;
  }

  // ───── Connections ─────

  private connections(s: Uc01Structure): string {
    let svg = '<g id="uc01_connections">';

    // Join connections (business → stations)
    svg += '<g id="uc01_joins">';
    s.joinConnections.forEach((c) => {
      svg += this.pathEl(`uc01_${c.id}`, c);
    });
    svg += '</g>';

    // Enrichment connections
    svg += '<g id="uc01_enrich_conns">';
    s.enrichConnections.forEach((c) => {
      svg += this.pathEl(`uc01_${c.id}`, c);
    });
    svg += '</g>';

    // AGV connections (normal)
    svg += '<g id="uc01_agv_conns">';
    s.agvConnections.forEach((c) => {
      svg += this.pathEl(`uc01_${c.id}`, c);
    });
    svg += '</g>';

    // AGV parallel connections (red)
    svg += '<g id="uc01_agv_par_conns">';
    s.agvParallelConnections.forEach((c) => {
      svg += this.pathEl(`uc01_${c.id}`, c);
    });
    svg += '</g>';

    svg += '</g>';
    return svg;
  }

  private pathEl(id: string, c: Uc01Connection): string {
    const dash = c.dashed ? ` stroke-dasharray="${c.dashPattern || '5,5'}"` : '';
    return `<path id="${id}" d="${c.path}" fill="none" stroke="${c.color}" stroke-width="${c.strokeWidth}"${dash} opacity="0.6"/>`;
  }

  // ───── NFC Thread ─────

  private thread(s: Uc01Structure, t: (k: string) => string): string {
    const th = s.thread;
    let svg = `<g id="uc01_thread">`;
    svg += `<line x1="${th.x1}" y1="${th.y1}" x2="${th.x2}" y2="${th.y2}" stroke="${th.color}" stroke-width="${th.strokeWidth}" stroke-linecap="round"/>`;
    svg += '</g>';

    svg += `<g id="uc01_thread_label">`;
    svg += `<rect x="${th.labelX}" y="${th.labelY}" width="${th.labelWidth}" height="${th.labelHeight}" rx="6" fill="${ORBIS_COLORS.diagram.boxFill}" stroke="${th.color}" stroke-width="1.5"/>`;
    svg += `<text x="${th.labelX + th.labelWidth / 2}" y="${th.labelY + 20}" text-anchor="middle" class="uc01-thread-label">${this.esc(t(th.labelKey))}</text>`;
    svg += '</g>';

    return svg;
  }

  // ───── Station Nodes ─────

  private stationNodes(s: Uc01Structure, t: (k: string) => string): string {
    let svg = '<g id="uc01_nodes">';
    s.stationNodes.forEach((node: Uc01StationNode) => {
      svg += `<g id="uc01_node_${node.id}">`;
      svg += `<circle cx="${node.cx}" cy="${node.cy}" r="${node.r}" fill="${node.fill}" stroke="${node.stroke}" stroke-width="1.5"/>`;
      svg += `<text x="${node.cx}" y="${node.cy + 4}" text-anchor="middle" class="uc01-node-label">${this.esc(t(node.labelKey))}</text>`;
      svg += '</g>';
    });
    svg += '</g>';
    return svg;
  }

  // ───── Badges ─────

  private badges(s: Uc01Structure): string {
    let svg = '<g id="uc01_badges">';
    s.badges.forEach((b: Uc01Badge) => {
      svg += `<g id="uc01_${b.id}">`;
      svg += `<circle cx="${b.cx}" cy="${b.cy}" r="${b.r}" fill="${ORBIS_COLORS.diagram.nodeDefault}" stroke="${UC01_COLORS.nodeStroke}" stroke-width="1"/>`;
      svg += `<text x="${b.cx}" y="${b.cy + 4}" text-anchor="middle" class="uc01-badge-text">${b.text}</text>`;
      svg += '</g>';
    });
    svg += '</g>';
    return svg;
  }

  // ───── Boxes (business + enrichment) ─────

  private boxes(items: Uc01Box[], groupId: string, prefix: string, t: (k: string) => string): string {
    let svg = `<g id="${groupId}">`;
    items.forEach((box: Uc01Box) => {
      svg += `<g id="${prefix}_${box.id}">`;
      svg += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="${box.rx}" fill="${box.fill}" stroke="${box.stroke}" stroke-width="1"/>`;
      svg += `<text x="${box.x + box.width / 2}" y="${box.y + box.height / 2 + 4}" text-anchor="middle" class="uc01-box-text">${this.esc(t(box.textKey))}</text>`;
      svg += '</g>';
    });
    svg += '</g>';
    return svg;
  }

  // ───── Legend ─────

  private legend(s: Uc01Structure, t: (k: string) => string): string {
    const { x, y, width, height } = s.legend;
    const lineH = 18;
    const padX = 14;
    const startY = y + 28;

    // Legend lines (hardcoded since they contain icons/colors, not just text)
    const lines = [
      { text: t('uc01.legend.title'),        cls: 'uc01-legend-title' },
      { text: `━━ ${t('uc01.legend.cyan')}`, cls: 'uc01-legend-text', color: UC01_COLORS.threadCyan },
      { text: `▬▬ ${t('uc01.legend.red')}`,  cls: 'uc01-legend-text', color: UC01_COLORS.agvParallelStroke },
      { text: `┈┈ ${t('uc01.legend.dashed')}`, cls: 'uc01-legend-text' },
      { text: t('uc01.legend.abbr'),          cls: 'uc01-legend-text' },
      { text: `① ${t('uc01.legend.parallel')}`, cls: 'uc01-legend-text' },
    ];

    let svg = `<g id="uc01_legend">`;
    svg += `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="6" fill="${ORBIS_COLORS.diagram.boxFill}" stroke="${ORBIS_COLORS.diagram.boxStroke}" stroke-width="1"/>`;
    lines.forEach((line, i) => {
      const ly = startY + i * lineH;
      const fill = line.color || UC01_COLORS.textDark;
      svg += `<text x="${x + padX}" y="${ly}" class="${line.cls}" fill="${fill}">${this.esc(line.text)}</text>`;
    });
    svg += '</g>';
    return svg;
  }

  // ───── Abbreviations ─────

  private abbreviations(s: Uc01Structure, t: (k: string) => string): string {
    const { x, y, width, height } = s.abbreviations;
    let svg = `<g id="uc01_abbreviations">`;
    svg += `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="6" fill="${ORBIS_COLORS.diagram.boxFill}" stroke="${ORBIS_COLORS.diagram.boxStroke}" stroke-width="1"/>`;
    svg += `<text x="${x + width / 2}" y="${y + 20}" text-anchor="middle" class="uc01-abbr-text">${this.esc(t(s.abbreviations.textKey))}</text>`;
    svg += '</g>';
    return svg;
  }

  // ───── Helpers ─────

  private esc(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  }
}
