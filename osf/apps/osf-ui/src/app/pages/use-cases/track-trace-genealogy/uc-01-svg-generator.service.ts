import { Injectable } from '@angular/core';
import { getAssetPath } from '../../../assets/detail-asset-map';
import { createUc01Structure, type Uc01Structure, type Uc01Chip, type Uc01Lane, type Uc01Column } from './uc-01-structure.config';
import { ORBIS_COLORS } from '../../../assets/color-palette';

/**
 * Service for generating UC-01 Track & Trace Genealogy SVG dynamically with I18n support
 * Uses Track & Trace colors from centralized palette
 */
@Injectable({ providedIn: 'root' })
export class Uc01SvgGeneratorService {
  /**
   * Generate SVG string from structure with I18n text replacements
   */
  generateSvg(i18nTexts: Record<string, string>): string {
    const structure = createUc01Structure();
    const getText = (key: string): string => {
      const text = i18nTexts[key] || key;
      // Debug: Log missing translations
      if (text === key && !key.startsWith('uc01.')) {
        // Only log if it's not a valid key pattern (to avoid spam)
        console.warn(`[UC-01 SVG] Missing translation for key: ${key}`);
      }
      return text;
    };
    
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${structure.viewBox.width}" height="${structure.viewBox.height}" viewBox="0 0 ${structure.viewBox.width} ${structure.viewBox.height}">`;
    
    // Defs
    svg += this.generateDefs();
    
    // Root group
    svg += '<g id="uc01_root">';
    
    // Frame
    svg += `<defs>
      <linearGradient id="frameGradient" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" style="stop-color:#fafbfc;stop-opacity:1" />
        <stop offset="100%" style="stop-color:#ffffff;stop-opacity:1" />
      </linearGradient>
    </defs>`;
    svg += `<rect class="frame" x="0" y="0" width="${structure.viewBox.width}" height="${structure.viewBox.height}" fill="url(#frameGradient)"/>`;
    
    // Title
    svg += `<g id="uc01_title"><text x="${structure.title.x}" y="${structure.title.y}" text-anchor="middle" class="title">${this.escapeXml(getText(structure.title.key))}</text></g>`;
    
    // Subtitle (only shown in step 0)
    svg += `<g id="uc01_subtitle"><text x="${structure.subtitle.x}" y="${structure.subtitle.y}" text-anchor="middle" class="subtitle">${this.escapeXml(getText(structure.subtitle.key))}</text></g>`;
    
    // Step description overlay
    const sd = structure.stepDescription;
    const highlightGreenStrong = ORBIS_COLORS.highlightGreen.strong;
    svg += `<g id="uc01_step_description" class="step-description-overlay" style="display: none;">`;
    svg += `<rect x="${sd.x - sd.width / 2}" y="${sd.y}" width="${sd.width}" height="${sd.height}" rx="8" ry="8" fill="${highlightGreenStrong}" opacity="0.95" class="step-description__bg"/>`;
    svg += `<text id="uc01_step_description_title" x="${sd.x}" y="${sd.y + 30}" text-anchor="middle" font-size="24" font-weight="700" fill="#ffffff" class="step-description__title"></text>`;
    svg += `<text id="uc01_step_description_text" x="${sd.x}" y="${sd.y + 70}" text-anchor="middle" font-size="16" font-weight="400" fill="#ffffff" class="step-description__text"></text>`;
    svg += '</g>';
    
    // Columns
    svg += '<g id="uc01_columns">';
    
    // All columns now use the same lane-based structure
    svg += this.generateColumn(structure.columns.businessEvents, getText);
    svg += this.generateColumn(structure.columns.productionPlan, getText);
    svg += this.generateColumn(structure.columns.actualPath, getText);
    svg += this.generateColumn(structure.columns.correlatedTimeline, getText);
    
    svg += '</g>'; // uc01_columns
    
    // Connections (L-shaped paths between columns)
    svg += '<g id="uc01_connections">';
    structure.connections.forEach((conn) => {
      const strokeColor = '#5071af'; // ORBIS blue medium (direct hex)
      const strokeDash = conn.dashed ? 'stroke-dasharray="5,5"' : '';
      
      // Create L-shaped path: horizontal first, then vertical (or vice versa)
      // Calculate midpoint for L-shape
      const midX = (conn.fromX + conn.toX) / 2;
      const midY = (conn.fromY + conn.toY) / 2;
      
      // Determine L-shape direction: if horizontal distance > vertical, go horizontal first
      const dx = Math.abs(conn.toX - conn.fromX);
      const dy = Math.abs(conn.toY - conn.fromY);
      
      let pathD = '';
      if (dx > dy) {
        // Horizontal first, then vertical
        pathD = `M ${conn.fromX} ${conn.fromY} L ${midX} ${conn.fromY} L ${midX} ${conn.toY} L ${conn.toX} ${conn.toY}`;
      } else {
        // Vertical first, then horizontal
        pathD = `M ${conn.fromX} ${conn.fromY} L ${conn.fromX} ${midY} L ${conn.toX} ${midY} L ${conn.toX} ${conn.toY}`;
      }
      
      svg += `<path id="uc01_conn_${conn.id}" d="${pathD}" stroke="${strokeColor}" stroke-width="2" ${strokeDash} fill="none" opacity="0.6" marker-end="url(#arrow-right)"/>`;
    });
    svg += '</g>';
    
    svg += '</g>'; // uc01_root
    svg += '</svg>';
    
    return svg;
  }
  
  private generateDefs(): string {
    const orbisBlueStrong = ORBIS_COLORS.orbisBlue.strong;
    const orbisGreyMedium = ORBIS_COLORS.orbisGrey.medium;
    const orbisGreyLight = ORBIS_COLORS.orbisGrey.light;
    const trackTracePick = ORBIS_COLORS.trackTrace.pick.main;
    const trackTraceProcess = ORBIS_COLORS.trackTrace.process.main;
    const trackTraceDrop = ORBIS_COLORS.trackTrace.drop.main;
    const trackTraceStorageOrder = ORBIS_COLORS.trackTrace.storageOrder.main;
    const trackTraceProductionOrder = ORBIS_COLORS.trackTrace.productionOrder.main;
    
    return `
  <defs>
    <marker id="arrow-right" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto">
      <polygon points="0,0 12,6 0,12" fill="${ORBIS_COLORS.orbisGrey.medium}"/>
    </marker>
    <marker id="arrow-down" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto">
      <polygon points="0,0 6,12 12,0" fill="${ORBIS_COLORS.orbisGrey.medium}"/>
    </marker>
    <!-- Subtle shadows -->
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
      <feOffset dx="2" dy="2" result="offsetblur"/>
      <feComponentTransfer>
        <feFuncA type="linear" slope="0.15"/>
      </feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="shadow-light" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="2"/>
      <feOffset dx="1" dy="1" result="offsetblur"/>
      <feComponentTransfer>
        <feFuncA type="linear" slope="0.1"/>
      </feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <style>
      :root {
        --stroke: var(--orbis-blue-strong);
        --muted: var(--orbis-grey-medium);
        --bg: #ffffff;
        --panel: var(--orbis-grey-light);
        --uc-col-border: rgba(var(--orbis-blue-strong-rgb), 0.1);
        --uc-lane-bg: rgba(255, 255, 255, 0.6);
        --uc-lane-border: rgba(var(--orbis-blue-strong-rgb), 0.08);
        --track-trace-pick: ${trackTracePick};
        --track-trace-process: ${trackTraceProcess};
        --track-trace-drop: ${trackTraceDrop};
        --track-trace-storage-order: ${trackTraceStorageOrder};
        --track-trace-production-order: ${trackTraceProductionOrder};
      }
      .frame { fill: var(--bg); }
      .panel { fill: var(--bg); stroke: var(--uc-col-border); stroke-width: 1.5; filter: url(#shadow-light); }
      .title { font: 700 56px "Segoe UI", Arial, sans-serif; fill: var(--orbis-nightblue); letter-spacing: -0.5px; }
      .subtitle { font: 400 24px "Segoe UI", Arial, sans-serif; fill: var(--muted); }
      .h2 { font: 700 26px "Segoe UI", Arial, sans-serif; fill: var(--orbis-nightblue); letter-spacing: -0.3px; }
      .p { font: 400 20px "Segoe UI", Arial, sans-serif; fill: var(--orbis-nightblue); }
      .small { font: 400 18px "Segoe UI", Arial, sans-serif; fill: var(--orbis-nightblue); }
      .chipText { font: 400 16px "Segoe UI", Arial, sans-serif; fill: var(--orbis-nightblue); }
      .muted { fill: var(--muted); }
      .chip { fill: #ffffff; stroke: var(--orbis-grey-light); stroke-width: 1.5; filter: url(#shadow-light); }
      .lane { fill: var(--uc-lane-bg); stroke: var(--uc-lane-border); stroke-width: 1; }
      .nfcTag { fill: var(--highlight-green-strong); stroke: var(--highlight-green-strong); stroke-width: 3; filter: url(#shadow); }
      .timelineMarker { fill: #ffffff; stroke: var(--orbis-blue-medium); stroke-width: 2; }
      .timelineNumber { font: 700 18px "Segoe UI", Arial, sans-serif; fill: var(--orbis-nightblue); }
      /* Animation classes */
      .hl { opacity: 1; filter: drop-shadow(0 4px 12px rgba(var(--orbis-blue-strong-rgb), 0.2)); }
      .dim { opacity: 0.3; }
      .hidden { display: none; }
    </style>
  </defs>`;
  }
  
  private generateColumn(column: Uc01Column, getText: (key: string) => string): string {
    let svg = `<g id="uc01_col_${column.id}">`;
    // Use direct colors instead of CSS variables
    const panelFill = '#ffffff';
    const panelStroke = '#e0e0e0';
    const headerColor = '#172b4d'; // ORBIS nightblue
    svg += `<rect x="${column.x}" y="${column.y}" width="${column.width}" height="${column.height}" rx="18" ry="18" fill="${panelFill}" stroke="${panelStroke}" stroke-width="1.5"/>`;
    const headerText = getText(column.headerKey);
    svg += `<text x="${column.headerX}" y="${column.headerY}" font-size="26" font-weight="700" fill="${headerColor}">${this.escapeXml(headerText)}</text>`;
    
    column.lanes.forEach((lane: Uc01Lane) => {
      svg += this.generateLane(lane, getText);
    });
    
    svg += '</g>';
    return svg;
  }
  
  private generateLane(lane: Uc01Lane, getText: (key: string) => string): string {
    let svg = `<g id="uc01_lane_${lane.id}">`;
    
    // Lane box (use direct colors)
    const laneFill = 'rgba(255, 255, 255, 0.6)';
    const laneStroke = 'rgba(23, 43, 77, 0.08)';
    svg += `<rect x="${lane.x}" y="${lane.y}" width="${lane.width}" height="${lane.height}" rx="16" ry="16" fill="${laneFill}" stroke="${laneStroke}" stroke-width="1"/>`;
    
    // Lane title (use direct colors and ensure text is replaced)
    const titleColor = '#172b4d'; // ORBIS nightblue
    const titleText = getText(lane.titleKey);
    svg += `<text x="${lane.x! + 50}" y="${lane.y! + 30}" font-size="20" font-weight="600" fill="${titleColor}">${this.escapeXml(titleText)}</text>`;
    
    // Lane icon (if present)
    if (lane.iconPath && lane.iconX !== undefined && lane.iconY !== undefined) {
      const iconPath = getAssetPath(lane.iconPath.replace(/^\//, ''));
      const iconX = lane.x! + lane.width! - (lane.iconWidth || 50) - 10;
      const iconY = lane.y! + 28;
      svg += `<g id="uc01_lane_${lane.id}_icon" transform="translate(${iconX},${iconY})">`;
      const iconBgStroke = '#e0e0e0'; // ORBIS grey light
      svg += `<rect width="${lane.iconWidth || 50}" height="${lane.iconHeight || 50}" rx="12" ry="12" fill="#ffffff" stroke="${iconBgStroke}" stroke-width="1.5"/>`;
      svg += `<image href="${iconPath}" x="10" y="10" width="${(lane.iconWidth || 50) - 20}" height="${(lane.iconHeight || 50) - 20}" preserveAspectRatio="xMidYMid meet" opacity="0.9"/>`;
      svg += '</g>';
    }
    
    // Check if this is a timeline lane (vertical timeline from top to bottom)
    const isTimelineLane = lane.id === 'plan-sequence' || lane.id === 'fts-route' || lane.id === 'event-timeline';
    
    if (isTimelineLane && lane.chips.length > 0) {
      // Timeline line should be LEFT of chips, not in the middle
      // Calculate timeline line position (left side of chips, with some margin)
      const firstChip = lane.chips[0];
      const lastChip = lane.chips[lane.chips.length - 1];
      // Timeline line is 30px left of chip start (chip.x)
      const timelineX = firstChip.x - 30;
      const lineY1 = firstChip.y + firstChip.height / 2;
      const lineY2 = lastChip.y + lastChip.height / 2;
      
      // Determine stroke color based on lane type (use direct hex values)
      let strokeColor: string = '#5071af'; // ORBIS blue medium
      let strokeDash = '';
      if (lane.id === 'plan-sequence') {
        strokeColor = '#bbbcbc'; // ORBIS grey medium
        strokeDash = 'stroke-dasharray="3,3"';
      } else if (lane.id === 'fts-route') {
        strokeColor = '#f97316'; // Track & Trace process main
      } else if (lane.id === 'event-timeline') {
        strokeColor = '#5071af'; // ORBIS blue medium
      }
      
      // Draw vertical timeline line (behind chips)
      svg += `<line x1="${timelineX}" y1="${lineY1}" x2="${timelineX}" y2="${lineY2}" stroke="${strokeColor}" stroke-width="3" ${strokeDash}/>`;
      
      // Draw timeline circles/markers for each chip (on the timeline line)
      lane.chips.forEach((chip, index) => {
        const circleY = chip.y + chip.height / 2;
        const circleRadius = 12;
        const circleFill = '#ffffff';
        const circleStroke = strokeColor;
        svg += `<circle cx="${timelineX}" cy="${circleY}" r="${circleRadius}" fill="${circleFill}" stroke="${circleStroke}" stroke-width="2"/>`;
        // Add number inside circle for event-timeline
        if (lane.id === 'event-timeline') {
          svg += `<text x="${timelineX}" y="${circleY + 4}" text-anchor="middle" font-size="12" font-weight="600" fill="${circleStroke}">${index + 1}</text>`;
        }
      });
      
      // Draw arrows between timeline markers (vertical, pointing down)
      for (let i = 0; i < lane.chips.length - 1; i++) {
        const currentChip = lane.chips[i];
        const nextChip = lane.chips[i + 1];
        const arrowY1 = currentChip.y + currentChip.height / 2 + 12; // Below circle
        const arrowY2 = nextChip.y + nextChip.height / 2 - 12; // Above next circle
        svg += `<line x1="${timelineX}" y1="${arrowY1}" x2="${timelineX}" y2="${arrowY2}" stroke="${strokeColor}" stroke-width="2" marker-end="url(#arrow-down)"/>`;
      }
    }
    
    // Chips (drawn after timeline so they appear on top)
    svg += `<g id="uc01_lane_${lane.id}_chips">`;
    lane.chips.forEach((chip) => {
      svg += this.generateChip(chip, lane, getText, isTimelineLane);
    });
    svg += '</g>';
    
    svg += '</g>';
    return svg;
  }
  
  private generateChip(chip: Uc01Chip, lane: Uc01Lane, getText: (key: string) => string, isTimelineChip: boolean = false): string {
    let svg = `<g id="uc01_chip_${chip.id}">`;
    
    const chipX = chip.x;
    const chipY = chip.y;
    
    // Determine chip colors (use direct hex values, not CSS variables)
    const chipFill = chip.fill || '#ffffff';
    const chipStroke = chip.stroke || '#e0e0e0';
    const textColor = '#172b4d'; // ORBIS nightblue
    
    // Chip with rounded corners (use direct colors)
    svg += `<rect x="${chipX}" y="${chipY}" width="${chip.width}" height="${chip.height}" rx="14" ry="14" fill="${chipFill}" stroke="${chipStroke}" stroke-width="1.5"/>`;
    
    // Chip text (ensure text is replaced)
    const textX = chipX + 10;
    if (chip.multiline && chip.textLines) {
      chip.textLines.forEach((lineKey, index) => {
        const lineY = chipY + 17 + (index * 20);
        const fontWeight = index === 0 ? '600' : '400';
        const fontSize = index === 0 ? '14' : '12';
        const text = getText(lineKey);
        svg += `<text x="${textX}" y="${lineY}" font-size="${fontSize}" font-weight="${fontWeight}" fill="${textColor}">${this.escapeXml(text)}</text>`;
      });
    } else {
      const text = getText(chip.textKey);
      const centerY = chipY + chip.height / 2;
      svg += `<text x="${textX}" y="${centerY + 5}" font-size="14" fill="${textColor}">${this.escapeXml(text)}</text>`;
    }
    
    // Chip icon (if present) - position relative to chip
    if (chip.iconPath && chip.iconX !== undefined && chip.iconY !== undefined) {
      const iconPath = getAssetPath(chip.iconPath.replace(/^\//, ''));
      const iconOffsetX = chip.iconX - chipX;
      const iconOffsetY = chip.iconY - chipY;
      svg += `<image href="${iconPath}" x="${chipX + iconOffsetX}" y="${chipY + iconOffsetY}" width="${chip.iconWidth || 20}" height="${chip.iconHeight || 20}" preserveAspectRatio="xMidYMid meet" opacity="0.85"/>`;
    }
    
    svg += '</g>';
    return svg;
  }
  
  
  private escapeXml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  }
}
