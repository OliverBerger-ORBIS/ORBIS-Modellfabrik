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
 *   join/AGV connections, phase brackets, legend.
 *
 * All text keys are resolved via I18n at generation time.
 * SVG element IDs use uc01_ prefix for animation targeting.
 */
@Injectable({ providedIn: 'root' })
export class Uc01SvgGeneratorService {
  /** Single font size for all business/enrichment box labels (no per-box scaling). */
  private static readonly UC01_BOX_FONT_PX = 18;
  private static readonly UC01_BOX_LINE_HEIGHT_FACTOR = 1.2;

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
    svg += `<g id="uc01_outcome"><text x="${s.outcome.x}" y="${s.outcome.y}" text-anchor="middle" font-family="Segoe UI" font-weight="600" font-size="32" fill="${highlightGreenStrong}">${this.esc(t(s.outcome.key))}</text></g>`;

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
    svg += this.connections(s, t);

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
    .uc01-lane-title { font: 700 22px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-node-label { font: 700 24px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-box-text { font: 700 18px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-badge-text { font: 700 22px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-phase-text { font: 600 20px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-legend-text { font: 400 17px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-legend-title { font: 700 20px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-thread-label { font: 700 20px "Segoe UI",Arial,sans-serif; fill: ${C.threadCyan}; }
    .uc01-thread-label-sub { font: 600 17px "Segoe UI",Arial,sans-serif; fill: ${C.threadCyan}; }
    .uc01-join-id { font: 600 13px "Segoe UI",Arial,sans-serif; fill: ${nightBlue}; }
    .uc01-step-title { font: 700 44px "Segoe UI",Arial,sans-serif; fill: #ffffff; }
    .uc01-step-text { font: 400 28px "Segoe UI",Arial,sans-serif; fill: #ffffff; }
    .uc01-footer { font: 400 18px "Segoe UI",Arial,sans-serif; fill: ${ORBIS_COLORS.orbisGrey.medium}; }
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
  <text id="uc01_step_description_title" x="${sd.x}" y="${sd.y + 48}" text-anchor="middle" class="uc01-step-title"></text>
  <text id="uc01_step_description_text" x="${sd.x}" y="${sd.y + 100}" text-anchor="middle" class="uc01-step-text"></text>
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
      svg += `<text x="${mid}" y="${y - 6}" text-anchor="middle" class="uc01-phase-text">${this.esc(t(phase.textKey))}</text>`;
      svg += '</g>';
    });
    svg += '</g>';
    return svg;
  }

  // ───── Connections ─────

  private connections(s: Uc01Structure, t: (k: string) => string): string {
    let svg = '<g id="uc01_connections">';

    // Join connections (business → stations) + correlation ID labels
    svg += '<g id="uc01_joins">';
    s.joinConnections.forEach((c) => {
      svg += this.pathEl(`uc01_${c.id}`, c);
    });
    s.joinConnections.forEach((c) => {
      if (c.labelKey !== undefined && c.labelX !== undefined && c.labelY !== undefined) {
        svg += `<text x="${c.labelX}" y="${c.labelY}" text-anchor="middle" class="uc01-join-id">${this.esc(t(c.labelKey))}</text>`;
      }
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
    const tcx = th.labelX + th.labelWidth / 2;
    const y1 = th.labelY + 26;
    const y2 = th.labelY + 48;
    svg += `<text text-anchor="middle"><tspan x="${tcx}" y="${y1}" class="uc01-thread-label">${this.esc(t(th.labelLine1Key))}</tspan><tspan x="${tcx}" y="${y2}" class="uc01-thread-label-sub">${this.esc(t(th.labelLine2Key))}</tspan></text>`;
    svg += '</g>';

    return svg;
  }

  // ───── Station Nodes ─────

  private stationNodes(s: Uc01Structure, t: (k: string) => string): string {
    let svg = '<g id="uc01_nodes">';
    s.stationNodes.forEach((node: Uc01StationNode) => {
      svg += `<g id="uc01_node_${node.id}">`;
      svg += `<circle cx="${node.cx}" cy="${node.cy}" r="${node.r}" fill="${node.fill}" stroke="${node.stroke}" stroke-width="2"/>`;
      svg += `<text x="${node.cx}" y="${node.cy + 8}" text-anchor="middle" class="uc01-node-label">${this.esc(t(node.labelKey))}</text>`;
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
      svg += `<circle cx="${b.cx}" cy="${b.cy}" r="${b.r}" fill="${ORBIS_COLORS.diagram.nodeDefault}" stroke="${UC01_COLORS.nodeStroke}" stroke-width="1.5"/>`;
      svg += `<text x="${b.cx}" y="${b.cy + 8}" text-anchor="middle" class="uc01-badge-text">${b.text}</text>`;
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
      svg += `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" rx="${box.rx}" fill="${box.fill}" stroke="${box.stroke}" stroke-width="1.5"/>`;
      svg += this.fitBoxText(t(box.textKey), box);
      svg += '</g>';
    });
    svg += '</g>';
    return svg;
  }

  /**
   * Fixed font size for all boxes; word-wrap at spaces; long German compounds prefer `Teil - teil`
   * at known suffixes, else syllable-style `Teil-` + remainder.
   */
  private fitBoxText(resolved: string, box: Uc01Box): string {
    const raw = resolved.trim();
    if (!raw) {
      return '';
    }
    const padX = 6;
    const padY = 6;
    const innerW = Math.max(8, box.width - padX * 2);
    const fs = Uc01SvgGeneratorService.UC01_BOX_FONT_PX;
    const lineH = fs * Uc01SvgGeneratorService.UC01_BOX_LINE_HEIGHT_FACTOR;
    const lines = this.splitTextIntoLines(raw, innerW, fs);
    return this.renderFittedBoxLines(lines, box, fs, lineH);
  }

  /**
   * Wrap at spaces. Long German compounds: prefer `prefix - suffix` at morpheme boundaries when the
   * joined form would wrap anyway; otherwise syllable-style `prefix-` + remainder (Option A).
   */
  private wrapParagraph(paragraph: string, maxWidthPx: number, fontSize: number): string[] {
    const avgCharW = fontSize * 0.52;
    const maxChars = Math.max(4, Math.floor(maxWidthPx / avgCharW));
    const words = paragraph.split(/\s+/).filter(Boolean);
    const lines: string[] = [];
    let line = '';

    const flushLine = (): void => {
      if (line) {
        lines.push(line);
        line = '';
      }
    };

    const pushHyphenatedFallback = (word: string): void => {
      let rest = word;
      while (rest.length > maxChars) {
        const prefixLen = maxChars - 1;
        lines.push(rest.slice(0, prefixLen) + '-');
        rest = rest.slice(prefixLen);
      }
      if (rest.length) {
        line = rest;
      }
    };

    for (const w of words) {
      if (w.length > maxChars) {
        flushLine();
        const compound = this.trySemanticCompoundSplit(w);
        if (compound && compound.prefix.length <= maxChars && compound.suffix.length <= maxChars) {
          const joined = `${compound.prefix} - ${compound.suffix}`;
          if (joined.length <= maxChars) {
            const test = line ? `${line} ${joined}` : joined;
            if (test.length <= maxChars) {
              line = test;
            } else {
              flushLine();
              line = joined;
            }
          } else {
            lines.push(`${compound.prefix} -`);
            line = compound.suffix;
          }
          continue;
        }
        pushHyphenatedFallback(w);
        continue;
      }

      const test = line ? `${line} ${w}` : w;
      if (test.length <= maxChars) {
        line = test;
      } else {
        flushLine();
        line = w;
      }
    }
    flushLine();
    return lines;
  }

  /**
   * Split common German compounds into two morphemes (longest suffix match first).
   * Used only when the full word exceeds the line budget (caller).
   */
  private trySemanticCompoundSplit(word: string): { prefix: string; suffix: string } | null {
    const suffixes = [
      'verarbeitung',
      'effektivität',
      'konfiguration',
      'bestellung',
      'auftrag',
      'qualität',
    ].sort((a, b) => b.length - a.length);
    const lw = word.toLowerCase();
    for (const suf of suffixes) {
      if (!lw.endsWith(suf)) {
        continue;
      }
      if (word.length <= suf.length + 2) {
        continue;
      }
      const cut = word.length - suf.length;
      const prefix = word.slice(0, cut);
      const suffix = word.slice(cut);
      if (prefix.length < 2 || suffix.length < 3) {
        continue;
      }
      return { prefix, suffix };
    }
    return null;
  }

  private splitTextIntoLines(text: string, innerW: number, fontSize: number): string[] {
    const parts = text.split(/\n/).map((p) => p.trim()).filter((p) => p.length > 0);
    const lines: string[] = [];
    for (const part of parts) {
      lines.push(...this.wrapParagraph(part, innerW, fontSize));
    }
    return lines;
  }

  private renderFittedBoxLines(lines: string[], box: Uc01Box, fontSize: number, lineHeight: number): string {
    const cx = box.x + box.width / 2;
    const fill = UC01_COLORS.textDark;
    const fontFamily = `'Segoe UI', Arial, sans-serif`;
    const totalH = lines.length * lineHeight;
    const topY = box.y + (box.height - totalH) / 2;
    const firstBaseline = topY + fontSize * 0.85;
    let inner = `<text text-anchor="middle" style="font-size:${fontSize}px;font-weight:700;font-family:${fontFamily};fill:${fill}">`;
    lines.forEach((line, i) => {
      if (i === 0) {
        inner += `<tspan x="${cx}" y="${firstBaseline}">${this.esc(line)}</tspan>`;
      } else {
        inner += `<tspan x="${cx}" dy="${lineHeight}">${this.esc(line)}</tspan>`;
      }
    });
    inner += '</text>';
    return inner;
  }

  // ───── Legend ─────

  private legend(s: Uc01Structure, t: (k: string) => string): string {
    const { x, y, width, height } = s.legend;
    const padX = 14;
    const padTop = 28;
    // Legend lines (no duplicate station abbreviations — those appear on nodes only)
    const lines = [
      { text: t('uc01.legend.title'), cls: 'uc01-legend-title' },
      { text: `━━ ${t('uc01.legend.cyan')}`, cls: 'uc01-legend-text', color: UC01_COLORS.threadCyan },
      { text: `▬▬ ${t('uc01.legend.red')}`, cls: 'uc01-legend-text', color: UC01_COLORS.agvParallelStroke },
      { text: `┈┈ ${t('uc01.legend.dashed')}`, cls: 'uc01-legend-text' },
      { text: `① ${t('uc01.legend.parallel')}`, cls: 'uc01-legend-text' },
    ];

    const lineH = Math.max(22, (height - padTop - 14) / lines.length);
    const startY = y + padTop;

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
