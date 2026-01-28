import { Injectable } from '@angular/core';
import { getAssetPath } from '../../../assets/detail-asset-map';
import { createUc06Structure, type Uc06Structure, type Uc06Chip, type Uc06Lane } from './uc-06-structure.config';
import { ICONS } from '../../../shared/icons/icon.registry';

/**
 * Enhanced Service for generating UC-06 SVG with improved visual design
 * This is a copy for EN version with visual improvements
 */
@Injectable({ providedIn: 'root' })
export class Uc06SvgGeneratorEnhancedService {
  /**
   * Generate SVG string from structure with I18n text replacements
   */
  generateSvg(i18nTexts: Record<string, string>): string {
    const structure = createUc06Structure();
    const getText = (key: string): string => i18nTexts[key] || key;
    
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${structure.viewBox.width}" height="${structure.viewBox.height}" viewBox="0 0 ${structure.viewBox.width} ${structure.viewBox.height}">`;
    
    // Defs
    svg += this.generateDefs();
    
    // Root group
    svg += '<g id="uc06_root">';
    
    // Frame with subtle gradient
    svg += `<defs>
      <linearGradient id="frameGradient" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" style="stop-color:#fafbfc;stop-opacity:1" />
        <stop offset="100%" style="stop-color:#ffffff;stop-opacity:1" />
      </linearGradient>
    </defs>`;
    svg += `<rect class="frame" x="0" y="0" width="${structure.viewBox.width}" height="${structure.viewBox.height}" fill="url(#frameGradient)"/>`;
    
    // Title
    svg += `<g id="uc06_title"><text x="${structure.title.x}" y="${structure.title.y}" text-anchor="middle" class="title">${this.escapeXml(getText(structure.title.key))}</text></g>`;
    
    // Subtitle
    svg += `<g id="uc06_subtitle"><text x="${structure.subtitle.x}" y="${structure.subtitle.y}" text-anchor="middle" class="subtitle">${this.escapeXml(getText(structure.subtitle.key))}</text></g>`;
    
    // Columns
    svg += '<g id="uc06_columns">';
    
    // Sources Column
    svg += this.generateSourcesColumn(structure.columns.sources, getText);
    
    // DSP Column
    svg += this.generateDspColumn(structure.columns.dsp, getText);
    
    // Targets Column
    svg += this.generateTargetsColumn(structure.columns.targets, getText);
    
    svg += '</g>'; // uc06_columns
    
    // Footer
    svg += `<g id="uc06_footer"><text x="${structure.footer.x}" y="${structure.footer.y}" text-anchor="middle" class="subtitle">${this.escapeXml(getText(structure.footer.key))}</text></g>`;
    
    svg += '</g>'; // uc06_root
    svg += '</svg>';
    
    return svg;
  }
  
  private generateDefs(): string {
    return `
  <defs>
    <marker id="arrow-down" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto">
      <polygon points="0,0 12,6 0,12" fill="#154194"/>
    </marker>
    <!-- Subtle shadows for depth -->
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
        --stroke: #154194;
        --muted: #6b7a8f;
        --bg: #ffffff;
        --panel: #f8f9fa;
        --accent: #7fbf7a;
        --uc-col-dsp-bg: rgba(232, 240, 254, 0.6);
        --uc-col-dsp-border: rgba(22, 65, 148, 0.2);
        --uc-col-sources-bg: #ffffff;
        --uc-col-targets-bg: #ffffff;
        --uc-col-border: rgba(22, 65, 148, 0.12);
        --uc-panel-bg: rgba(248, 249, 251, 0.9);
        --uc-panel-border: rgba(31, 54, 91, 0.1);
        --uc-lane-bg: rgba(255, 255, 255, 0.6);
        --uc-lane-border: rgba(22, 65, 148, 0.08);
      }
      .frame { fill: var(--bg); }
      .panel { fill: var(--panel); stroke: #e1e6ed; stroke-width: 1.5; rx: 20; ry: 20; filter: url(#shadow-light); }
      .panel-dsp { fill: var(--uc-col-dsp-bg); stroke: var(--uc-col-dsp-border); stroke-width: 1.5; rx: 20; ry: 20; filter: url(#shadow-light); }
      .title { font: 700 56px "Segoe UI", Arial, sans-serif; fill:#0f1e3d; letter-spacing: -0.5px; }
      .subtitle { font: 400 24px "Segoe UI", Arial, sans-serif; fill: var(--muted); }
      .h2 { font: 700 26px "Segoe UI", Arial, sans-serif; fill:#1a2b3c; letter-spacing: -0.3px; }
      .p { font: 400 20px "Segoe UI", Arial, sans-serif; fill:#1a2b3c; }
      .small { font: 400 18px "Segoe UI", Arial, sans-serif; fill:#1a2b3c; }
      .chipText { font: 400 16px "Segoe UI", Arial, sans-serif; fill:#1a2b3c; }
      .muted { fill: var(--muted); }
      .chip { fill:#ffffff; stroke:#d0d7e0; stroke-width:1.5; rx:12; ry:12; filter: url(#shadow-light); }
      .lane { fill: var(--uc-lane-bg); stroke: var(--uc-lane-border); stroke-width:1; rx:14; ry:14; }
      .statusDot { r:5; }
      .statusRunning { fill:#4caf50; }
      .statusIdle { fill:#ff9800; }
      .statusFail { fill:#f44336; }
      .badgePass { fill:#e8f5e9; stroke:#4caf50; stroke-width:1.5; rx:8; ry:8; }
      .badgeFail { fill:#ffebee; stroke:#f44336; stroke-width:1.5; rx:8; ry:8; }
      .arrow { fill:none; stroke:#154194; stroke-width:12; stroke-linecap:round; }
      .stepBox { fill:#ffffff; stroke:#c8d4e0; stroke-width:1.5; rx:14; ry:14; filter: url(#shadow-light); }
      .stepBar { fill:#ffffff; stroke:#d0d7e0; stroke-width:1.5; rx:12; ry:12; }
      .check { fill:#e8f5e9; stroke:#a5d6a7; stroke-width:1.5; rx:12; ry:12; }
    </style>
  </defs>`;
  }
  
  private generateSourcesColumn(column: any, getText: (key: string) => string): string {
    let svg = `<g id="uc06_col_sources">`;
    svg += `<rect class="panel" x="${column.x}" y="${column.y}" width="${column.width}" height="${column.height}" rx="20" ry="20"/>`;
    svg += `<text x="${column.headerX}" y="${column.headerY}" class="h2">${this.escapeXml(getText(column.headerKey))}</text>`;
    
    column.lanes.forEach((lane: Uc06Lane) => {
      svg += this.generateLane(lane, getText);
    });
    
    svg += '</g>';
    return svg;
  }
  
  private generateLane(lane: Uc06Lane, getText: (key: string) => string): string {
    let svg = `<g id="uc06_lane_${lane.id}">`;
    
    // Lane box (with rounded corners and subtle background)
    svg += `<rect class="lane" x="${lane.x}" y="${lane.y}" width="${lane.width}" height="${lane.height}" rx="14" ry="14"/>`;
    
    // Lane title (shifted 10px down)
    svg += `<text x="${lane.x! + 50}" y="${lane.y! + 30}" class="p" font-weight="600">${this.escapeXml(getText(lane.titleKey))}</text>`;
    
    // Lane icon (position relative to lane, shifted 10px down with title)
    const iconPath = getAssetPath(lane.iconPath.replace(/^\//, ''));
    const iconX = lane.x! + lane.width! - lane.iconWidth - 10; // Right side with padding
    const iconY = lane.y! + 28; // Align with title (shifted 10px down)
    svg += `<g id="uc06_lane_${lane.id}_icon" transform="translate(${iconX},${iconY})">`;
    svg += `<rect width="${lane.iconWidth}" height="${lane.iconHeight}" rx="12" ry="12" fill="#ffffff" stroke="#d0d7e0" stroke-width="1.5"/>`;
    svg += `<image href="${iconPath}" x="10" y="10" width="${lane.iconWidth - 20}" height="${lane.iconHeight - 20}" preserveAspectRatio="xMidYMid meet" opacity="0.9"/>`;
    svg += '</g>';
    
    // Chips
    svg += `<g id="uc06_lane_${lane.id}_events">`;
    lane.chips.forEach((chip) => {
      svg += this.generateChip(chip, lane, getText);
    });
    svg += '</g>';
    
    svg += '</g>';
    return svg;
  }
  
  private generateChip(chip: Uc06Chip, lane: Uc06Lane, getText: (key: string) => string): string {
    let svg = '';
    
    // Chip positions are already relative to lane after calculateLaneLayout
    // But chip.x is absolute from original structure, so we need to adjust
    const chipX = chip.x; // x is already correct (relative to column)
    const chipY = chip.y; // y is already adjusted to be relative to lane
    
    // Special handling for badges (quality lane)
    if (chip.fill && chip.stroke) {
      const fillClass = chip.fill === '#e8f5e9' ? 'badgePass' : 'badgeFail';
      svg += `<rect class="${fillClass}" x="${chipX}" y="${chipY}" width="${chip.width}" height="${chip.height}"/>`;
      svg += `<text x="${chipX + chip.width / 2}" y="${chipY + chip.height / 2 + 5}" text-anchor="middle" class="chipText" fill="${chip.fill === '#e8f5e9' ? '#4caf50' : '#f44336'}">${this.escapeXml(getText(chip.textKey))}</text>`;
      return svg;
    }
    
    // Label-only chips (like CHECK_QUALITY)
    if (chip.width === 0 && chip.height === 0) {
      svg += `<text x="${chipX}" y="${chipY}" class="chipText">${this.escapeXml(getText(chip.textKey))}</text>`;
      return svg;
    }
    
    // Regular chips (with rounded corners)
    svg += `<rect class="chip" x="${chipX}" y="${chipY}" width="${chip.width}" height="${chip.height}" rx="12" ry="12"/>`;
    
    // Status dots (for state chip) - special handling: only show heading + dots with labels
    if (chip.statusDots && chip.statusLabels && chip.statusLabels.length > 0) {
      // Show heading only (not the regular chip text)
      svg += `<text x="${chipX + 10}" y="${chipY + 17}" class="chipText" font-weight="600">${this.escapeXml(getText(chip.textKey))}</text>`;
      // Show dots with labels (indented by 20px)
      chip.statusDots.forEach((dot, index) => {
        if (index < chip.statusLabels!.length) {
          const dotY = chipY + 40 + (index * 25);
          const colorClass = `status${dot.color.charAt(0).toUpperCase() + dot.color.slice(1)}`;
          svg += `<circle class="statusDot ${colorClass}" cx="${chipX + 40}" cy="${dotY}" r="5"/>`; // Indented: 20 + 20 = 40px
          const labelY = chipY + 47 + (index * 25);
          svg += `<text x="${chipX + 50}" y="${labelY}" class="chipText">${this.escapeXml(getText(chip.statusLabels![index]))}</text>`; // Indented: 30 + 20 = 50px
        }
      });
    } else {
      // Regular chip text (multiline or single line) - only if not statusDots
      if (chip.multiline && chip.textLines) {
        chip.textLines.forEach((lineKey, index) => {
          const lineY = chipY + 17 + (index * 20);
          const fontWeight = index === 0 ? 'font-weight="600"' : '';
          // First line (heading) not indented, subsequent lines indented by 20px
          const textX = index === 0 ? chipX + 10 : chipX + 30;
          const textContent = this.escapeXml(getText(lineKey));
          svg += `<text x="${textX}" y="${lineY}" class="chipText" ${fontWeight}>${textContent}</text>`;
          
          // Add operation icons if defined (for operation chip)
          // Icons are positioned relative to text using offsetX and offsetY from structure config
          if (chip.operationIcons) {
            const operationIcon = chip.operationIcons.find(icon => icon.lineIndex === index + 1);
            if (operationIcon) {
              const iconPath = getAssetPath(operationIcon.iconPath.replace(/^\//, ''));
              // Estimate text width: approximate 5px per character for chipText (16px font)
              const estimatedTextWidth = textContent.length * 5;
              // Position icon relative to text end: textX + textWidth + offsetX
              const iconXAligned = textX + estimatedTextWidth + operationIcon.offsetX;
              // Position icon relative to text baseline: lineY + offsetY
              // offsetY is relative to baseline (positive = below, negative = above)
              // For vertical centering: offsetY should be negative (e.g., -8) to move icon up to text center
              const iconYAligned = lineY + operationIcon.offsetY;
              svg += `<image href="${iconPath}" x="${iconXAligned}" y="${iconYAligned}" width="${operationIcon.iconWidth}" height="${operationIcon.iconHeight}" preserveAspectRatio="xMidYMid meet" opacity="0.9"/>`;
            }
          }
        });
      } else {
        svg += `<text x="${chipX + 10}" y="${chipY + 20}" class="chipText">${this.escapeXml(getText(chip.textKey))}</text>`;
      }
    }
    
    // Chip icon (position relative to chip)
    if (chip.iconPath && chip.iconX !== undefined && chip.iconY !== undefined) {
      const iconPath = getAssetPath(chip.iconPath.replace(/^\//, ''));
      // Icon position: iconX is absolute, but we need it relative to chip
      // Calculate relative position: iconX - chipX gives offset from chip left
      const iconOffsetX = chip.iconX - chipX;
      const iconOffsetY = chip.iconY - chipY;
      svg += `<image href="${iconPath}" x="${chipX + iconOffsetX}" y="${chipY + iconOffsetY}" width="${chip.iconWidth}" height="${chip.iconHeight}" preserveAspectRatio="xMidYMid meet" opacity="0.85"/>`;
    }
    
    // Badges (for quality chip)
    if (chip.fill && chip.stroke) {
      // Badge is already rendered as chip with special fill/stroke
    }
    
    svg += '</g>';
    return svg;
  }
  
  private generateDspColumn(dsp: any, getText: (key: string) => string): string {
    let svg = `<g id="uc06_col_dsp">`;
    svg += `<rect class="panel-dsp" x="${dsp.column.x}" y="${dsp.column.y}" width="${dsp.column.width}" height="${dsp.column.height}" rx="20" ry="20"/>`;
    svg += `<text x="${dsp.column.headerX}" y="${dsp.column.headerY}" class="h2">${this.escapeXml(getText(dsp.column.headerKey))}</text>`;
    
    // Steps with arrows between them
    dsp.steps.forEach((step: any, stepIndex: number) => {
      svg += `<g id="uc06_step_${step.id}">`;
      svg += `<rect class="stepBox" x="${step.x}" y="${step.y}" width="${step.width}" height="${step.height}" rx="14" ry="14"/>`;
      svg += `<text x="${step.x + step.width / 2}" y="${step.y + 50}" text-anchor="middle" class="p"><tspan font-weight="700">${this.escapeXml(getText(step.titleKey))}</tspan></text>`;
      svg += `<text x="${step.x + step.width / 2}" y="${step.y + 85}" text-anchor="middle" class="small muted">${this.escapeXml(getText(step.descriptionKey))}</text>`;
      svg += '</g>';
      
      // Draw arrow between steps (only between steps, not after last)
      // Arrow: only triangle arrowhead, no shaft, with 5px spacing from lanes
      if (stepIndex < dsp.steps.length - 1) {
        const nextStep = dsp.steps[stepIndex + 1];
        const arrowStartY = step.y + step.height; // Bottom of current step
        const arrowEndY = nextStep.y; // Top of next step
        const arrowGap = arrowEndY - arrowStartY; // Gap height
        const arrowX = step.x + step.width / 2; // Center of steps
        
        // Spacing: exactly 5px from each lane
        const spacing = 5;
        const arrowTopY = arrowStartY + spacing; // Top of arrow (5px below current step)
        const arrowBottomY = arrowEndY - spacing; // Bottom of arrow (5px above next step)
        
        // Arrowhead size: use all available space between the two spacing points
        const arrowHeight = arrowBottomY - arrowTopY;
        const arrowheadSize = arrowHeight; // Use full height for maximum visibility
        const arrowheadBaseWidth = arrowheadSize * 1.4; // Base width 1.4x the height (wider for visibility)
        
        // Draw triangle arrowhead (pointing down)
        // Triangle tip at bottom (arrowBottomY), base at top (arrowTopY)
        svg += `<polygon points="${arrowX},${arrowBottomY} ${arrowX - arrowheadBaseWidth / 2},${arrowTopY} ${arrowX + arrowheadBaseWidth / 2},${arrowTopY}" fill="#154194" opacity="0.9"/>`;
      }
    });
    
    // Summary bars
    if (dsp.bars) {
      dsp.bars.forEach((bar: any) => {
        svg += this.generateBar(bar, getText);
      });
    }
    
    svg += '</g>';
    return svg;
  }
  
  private generateBar(bar: any, getText: (key: string) => string): string {
    let svg = `<g id="uc06_bar_${bar.id}">`;
    svg += `<rect class="stepBar" x="${bar.x}" y="${bar.y}" width="${bar.width}" height="${bar.height}" rx="12" ry="12"/>`;
    svg += `<text x="${bar.x + bar.width / 2}" y="${bar.y + bar.height / 2 + 5}" text-anchor="middle" class="small">${this.escapeXml(getText(bar.textKey))}</text>`;
    svg += '</g>';
    return svg;
  }
  
  private generateTargetsColumn(targets: any, getText: (key: string) => string): string {
    let svg = `<g id="uc06_col_targets">`;
    svg += `<rect class="panel" x="${targets.column.x}" y="${targets.column.y}" width="${targets.column.width}" height="${targets.column.height}" rx="20" ry="20"/>`;
    svg += `<text x="${targets.column.headerX}" y="${targets.column.headerY}" class="h2">${this.escapeXml(getText(targets.column.headerKey))}</text>`;
    
    // Process view box
    const pv = targets.processViewBox;
    svg += `<g id="uc06_process_view_box">`;
    svg += `<rect class="stepBox" x="${pv.x}" y="${pv.y}" width="${pv.width}" height="${pv.height}" rx="14" ry="14"/>`;
    svg += `<text x="${pv.x + pv.width / 2}" y="${pv.y + 35}" text-anchor="middle" class="p" font-weight="700">${this.escapeXml(getText(pv.titleKey))}</text>`;
    
    // Timeline
    svg += `<g id="uc06_process_timeline">`;
    svg += `<line x1="${pv.timeline.lineX1}" y1="${pv.timeline.lineY}" x2="${pv.timeline.lineX2}" y2="${pv.timeline.lineY}" stroke="#c2cbd8" stroke-width="10" stroke-linecap="round" opacity="0.6"/>`;
    pv.timeline.points.forEach((point: any) => {
      const iconPath = getAssetPath(point.iconPath.replace(/^\//, ''));
      svg += `<circle cx="${point.x}" cy="${point.y}" r="10" fill="#7fbf7a" opacity="0.9"/>`;
      svg += `<image href="${iconPath}" x="${point.iconX}" y="${point.iconY}" width="${point.iconWidth}" height="${point.iconHeight}" preserveAspectRatio="xMidYMid meet" opacity="0.9"/>`;
      svg += `<text x="${point.x}" y="${point.labelY}" text-anchor="middle" class="small">${this.escapeXml(getText(point.labelKey))}</text>`;
    });
    svg += '</g>';
    svg += '</g>'; // process_view_box
    
    // Targets
    svg += `<g id="uc06_targets_systems">`;
      targets.targets.forEach((target: any) => {
        const iconPath = getAssetPath(target.iconPath.replace(/^\//, ''));
        svg += `<g id="uc06_target_${target.id}">`;
        svg += `<rect class="stepBox" x="${target.x}" y="${target.y}" width="${target.width}" height="${target.height}" rx="14" ry="14"/>`;
      svg += `<image href="${iconPath}" x="${target.iconX}" y="${target.iconY}" width="${target.iconWidth}" height="${target.iconHeight}" preserveAspectRatio="xMidYMid meet" opacity="0.85"/>`;
      svg += `<text x="${target.x + target.width / 2}" y="${target.labelY}" text-anchor="middle" class="p">${this.escapeXml(getText(target.labelKey))}</text>`;
      svg += '</g>';
    });
    svg += `<text x="${targets.noteX}" y="${targets.noteY}" class="small muted">${this.escapeXml(getText(targets.noteKey))}</text>`;
    svg += '</g>';
    
    // Outcomes - fix text overflow by using proper text wrapping
    svg += `<g id="uc06_outcomes">`;
      targets.outcomes.forEach((outcome: any) => {
        svg += `<g id="uc06_outcome_${outcome.id}">`;
        svg += `<rect class="check" x="${outcome.x}" y="${outcome.y}" width="${outcome.width}" height="${outcome.height}" rx="12" ry="12"/>`;
        // Checkmark icon
        svg += `<path d="M ${outcome.x + 15} ${outcome.y + outcome.height / 2 - 3} L ${outcome.x + 18} ${outcome.y + outcome.height / 2} L ${outcome.x + 23} ${outcome.y + outcome.height / 2 - 6}" stroke="#4caf50" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
        
        // Text with proper wrapping - leave padding on left (60px for checkmark) and right (20px)
        const textStartX = outcome.x + 60;
        const textWidth = outcome.width - 80; // 60px left padding + 20px right padding
        const maxCharsPerLine = Math.floor(textWidth / 8); // Approximate 8px per character
        
        if (outcome.multiline && outcome.textLines) {
          outcome.textLines.forEach((lineKey: string, index: number) => {
            const lineY = outcome.y + 35 + (index * 30);
            const text = this.escapeXml(getText(lineKey));
            // Wrap long text if needed
            if (text.length > maxCharsPerLine) {
              const words = text.split(' ');
              let currentLine = '';
              let lineIndex = 0;
              words.forEach((word: string) => {
                const testLine = currentLine ? `${currentLine} ${word}` : word;
                if (testLine.length > maxCharsPerLine && currentLine) {
                  svg += `<text x="${textStartX}" y="${outcome.y + 35 + (lineIndex * 30)}" class="p">${currentLine}</text>`;
                  currentLine = word;
                  lineIndex++;
                } else {
                  currentLine = testLine;
                }
              });
              if (currentLine) {
                svg += `<text x="${textStartX}" y="${outcome.y + 35 + (lineIndex * 30)}" class="p">${currentLine}</text>`;
              }
            } else {
              svg += `<text x="${textStartX}" y="${lineY}" class="p">${text}</text>`;
            }
          });
        } else {
          const text = this.escapeXml(getText(outcome.textKey));
          // Wrap long text if needed
          if (text.length > maxCharsPerLine) {
            const words = text.split(' ');
            let currentLine = '';
            let lineIndex = 0;
            words.forEach((word: string) => {
              const testLine = currentLine ? `${currentLine} ${word}` : word;
              if (testLine.length > maxCharsPerLine && currentLine) {
                svg += `<text x="${textStartX}" y="${outcome.y + 35 + (lineIndex * 30)}" class="p">${currentLine}</text>`;
                currentLine = word;
                lineIndex++;
              } else {
                currentLine = testLine;
              }
            });
            if (currentLine) {
              svg += `<text x="${textStartX}" y="${outcome.y + 35 + (lineIndex * 30)}" class="p">${currentLine}</text>`;
            }
          } else {
            svg += `<text x="${textStartX}" y="${outcome.y + 45}" class="p">${text}</text>`;
          }
        }
      svg += '</g>';
    });
    svg += '</g>';
    
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
