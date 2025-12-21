/**
 * Generate DSP Architecture SVG diagrams from TypeScript config files.
 * 
 * This script reads the layout configuration files and generates static SVG
 * diagrams for documentation purposes. The diagrams show:
 * - Functional View: All containers and connections in functional mode
 * - Edge Functions: dsp-edge with its 9 function icons
 * - MC Functions: dsp-mc with its 3 function icons and 3 edge instances
 * - Component View: dsp-edge with its 8 internal components
 * - Deployment View: dsp-edge with its 4 deployment pipeline steps
 * 
 * Usage:
 *   npx tsx scripts/generate-dsp-svg-diagrams.ts
 * 
 * Output: SVG files are generated as *_v1.svg for testing before overwriting originals.
 */

import * as fs from 'fs';
import * as path from 'path';

// Mock Angular's $localize for config execution
(global as any).$localize = (messageParts: TemplateStringsArray, ...expressions: any[]) => {
  return messageParts.reduce((result, part, i) => {
    const expression = expressions[i] !== undefined ? expressions[i] : '';
    return result + part + expression;
  }, '');
};

// Import config functions after mocking $localize
// We need to use require/dynamic import because of the way TypeScript handles Angular code
const repoRoot = path.resolve(__dirname, '..');

// IconKey to SVG filename mapping (without .svg extension for display)
const ICON_TO_SVG_FILE: Record<string, string> = {
  // Business Process
  'erp-application': 'erp-application',
  'mes-application': 'mes-application',
  'bp-cloud-apps': 'cloud-application',
  'bp-analytics': 'analytics-application',
  'bp-data-lake': 'data-lake-application',
  // DSP (central icons)
  'ux-box': 'dsp-ux-box',
  'logo-edge': 'dsp-edge-box',
  'logo-mc': 'dsp-mc-box',
  // Systems
  'shopfloor-systems': 'any-system',
  'shopfloor-fts': 'agv-system',
  'shopfloor-warehouse': 'warehouse-system',
  'shopfloor-factory': 'factory-system',
  'any-system': 'any-system',
  'agv-system': 'agv-system',
  // Devices
  'device-mill': 'mill-station',
  'device-drill': 'drill-station',
  'device-aiqs': 'aiqs-station',
  'device-hbw': 'hbw-station',
  'device-dps': 'dps-station',
  'device-chrg': 'chrg-station',
};

/**
 * Extract SVG filename from container ID or iconKey (without .svg extension)
 */
function getSvgFilename(containerId: string, iconKey?: string): string | null {
  // Try iconKey first
  if (iconKey && ICON_TO_SVG_FILE[iconKey]) {
    return ICON_TO_SVG_FILE[iconKey];
  }
  
  // Extract from container ID
  if (containerId.startsWith('bp-')) {
    const suffix = containerId.replace('bp-', '');
    if (suffix === 'erp') return 'erp-application';
    if (suffix === 'mes') return 'mes-application';
    if (suffix === 'cloud') return 'cloud-application';
    if (suffix === 'analytics') return 'analytics-application';
    if (suffix === 'data-lake') return 'data-lake-application';
  }
  
  if (containerId.startsWith('dsp-')) {
    if (containerId === 'dsp-ux') return 'dsp-ux-box';
    if (containerId === 'dsp-edge') return 'dsp-edge-box';
    if (containerId === 'dsp-mc') return 'dsp-mc-box';
  }
  
  if (containerId.startsWith('sf-system-')) {
    const suffix = containerId.replace('sf-system-', '');
    if (suffix === 'any') return 'any-system';
    if (suffix === 'fts') return 'agv-system';
    if (suffix === 'warehouse') return 'warehouse-system';
    if (suffix === 'factory') return 'factory-system';
  }
  
  if (containerId.startsWith('sf-device-')) {
    const suffix = containerId.replace('sf-device-', '');
    return `${suffix}-station`;
  }
  
  return null;
}

/**
 * Break label at last hyphen for better readability
 * Example: "sf-system-any" -> ["sf-system", "-any"]
 */
function breakLabelAtHyphen(label: string): string[] {
  const lastHyphenIndex = label.lastIndexOf('-');
  if (lastHyphenIndex === -1) {
    return [label];
  }
  
  // Split at last hyphen
  const first = label.substring(0, lastHyphenIndex);
  const rest = label.substring(lastHyphenIndex); // includes the hyphen
  
  return [first, rest];
}

/**
 * Escape XML text
 */
function escapeXml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

/**
 * Generate SVG text element with centered label, optionally with line break at hyphen, and SVG filename
 */
function generateCenteredLabel(
  x: number,
  y: number,
  containerId: string,
  options: {
    fontSize?: number;
    fontWeight?: string;
    fill?: string;
    iconKey?: string;
    breakAtHyphen?: boolean; // Only apply hyphen-break for shopfloor layer
    showSvgFilename?: boolean; // Whether to show SVG filename (default: true, except for semantic keys)
  } = {}
): string {
  // Reduce fontSize by 20% (multiply by 0.8)
  const baseFontSize = (options.fontSize || 18) * 0.8;
  const {
    fontWeight = '500',
    fill = '#163494',
    iconKey,
    breakAtHyphen = false, // Default: no hyphen break (for BP and DSP layers)
    showSvgFilename = true, // Default: show SVG filename
  } = options;
  
  const labelParts = breakAtHyphen ? breakLabelAtHyphen(containerId) : [containerId];
  const svgFilename = getSvgFilename(containerId, iconKey);
  
  const lineHeight = baseFontSize * 1.2;
  let result = `<text x="${x}" y="${y}" font-family="Arial, sans-serif" font-size="${baseFontSize}" fill="${fill}" text-anchor="middle" dominant-baseline="middle" font-weight="${fontWeight}">`;
  
  // First line (before hyphen if breaking, otherwise full label)
  result += `<tspan x="${x}" dy="${labelParts.length > 1 ? '-0.6em' : '0'}">${escapeXml(labelParts[0])}</tspan>`;
  
  // Second line (after hyphen, if exists)
  if (labelParts.length > 1) {
    result += `<tspan x="${x}" dy="1.2em">${escapeXml(labelParts[1])}</tspan>`;
  }
  
  // SVG filename (if available and should be shown)
  if (svgFilename && showSvgFilename) {
    result += `<tspan x="${x}" dy="1.2em" font-size="${Math.round(baseFontSize * 0.6)}" fill="#666">(${escapeXml(svgFilename)})</tspan>`;
  }
  
  result += '</text>';
  return result;
}

/**
 * Break label at first hyphen (for edge-function labels)
 */
function breakLabelAtFirstHyphen(label: string): string[] {
  const firstHyphenIndex = label.indexOf('-');
  if (firstHyphenIndex === -1 || firstHyphenIndex === 0 || firstHyphenIndex === label.length - 1) {
    return [label];
  }
  
  const first = label.substring(0, firstHyphenIndex);
  const rest = label.substring(firstHyphenIndex); // Includes the hyphen
  
  return [first, rest];
}

/**
 * Break label at second hyphen (for edge-component labels)
 */
function breakLabelAtSecondHyphen(label: string): string[] {
  const firstHyphenIndex = label.indexOf('-');
  if (firstHyphenIndex === -1) {
    return [label];
  }
  
  const secondHyphenIndex = label.indexOf('-', firstHyphenIndex + 1);
  if (secondHyphenIndex === -1 || secondHyphenIndex === label.length - 1) {
    return [label];
  }
  
  const first = label.substring(0, secondHyphenIndex);
  const rest = label.substring(secondHyphenIndex); // Includes the hyphen
  
  return [first, rest];
}

/**
 * Generate Edge Functions SVG label (breaks at first hyphen, no SVG filename)
 */
function generateEdgeFunctionLabel(
  x: number,
  y: number,
  functionKey: string,
  options: {
    fontSize?: number;
    fontWeight?: string;
    fill?: string;
    breakAtSecondHyphen?: boolean; // If true, break at second hyphen instead of first
  } = {}
): string {
  const baseFontSize = (options.fontSize || 18) * 0.8;
  const {
    fontWeight = '500',
    fill = '#163494',
    breakAtSecondHyphen = false,
  } = options;
  
  const labelParts = breakAtSecondHyphen 
    ? breakLabelAtSecondHyphen(functionKey)
    : breakLabelAtFirstHyphen(functionKey);
  
  let result = `<text x="${x}" y="${y}" font-family="Arial, sans-serif" font-size="${baseFontSize}" fill="${fill}" text-anchor="middle" dominant-baseline="middle" font-weight="${fontWeight}">`;
  
  // First line (before hyphen)
  result += `<tspan x="${x}" dy="${labelParts.length > 1 ? '-0.6em' : '0'}">${escapeXml(labelParts[0])}</tspan>`;
  
  // Second line (after hyphen, if exists)
  if (labelParts.length > 1) {
    result += `<tspan x="${x}" dy="1.2em">${escapeXml(labelParts[1])}</tspan>`;
  }
  
  result += '</text>';
  return result;
}

/**
 * Calculate function icon position on a circle
 */
function getFunctionIconPosition(
  containerX: number,
  containerY: number,
  containerWidth: number,
  containerHeight: number,
  index: number,
  total: number,
  isMc: boolean,
  iconSize: number = 48,
  radius: number = 160
): { x: number; y: number } {
  const startDeg = isMc ? 300 : 90; // MC starts at 300°, Edge at 90°
  const spanDeg = isMc ? 120 : 360; // MC spans 120°, Edge spans 360°
  
  const step = total > 1 ? spanDeg / (total - 1) : 0;
  const angleDeg = startDeg + index * step;
  const angleRad = (angleDeg * Math.PI) / 180;
  
  const cx = containerX + containerWidth / 2;
  const cy = containerY + containerHeight / 2;
  
  const maxRadius = Math.max(0, Math.min(radius, Math.min(containerWidth, containerHeight) / 2 - iconSize / 2 - 4));
  
  const iconX = cx + maxRadius * Math.cos(angleRad);
  const iconY = cy + maxRadius * Math.sin(angleRad);
  
  return { x: iconX, y: iconY };
}

/**
 * Calculate connection path (L-shaped)
 */
function calculateConnectionPath(
  from: { x: number; y: number; width: number; height: number },
  to: { x: number; y: number; width: number; height: number },
  fromSide: string = 'bottom',
  toSide: string = 'top'
): string {
  const getAnchorPoint = (
    container: { x: number; y: number; width: number; height: number },
    side: string
  ) => {
    switch (side) {
      case 'top':
        return { x: container.x + container.width / 2, y: container.y };
      case 'bottom':
        return { x: container.x + container.width / 2, y: container.y + container.height };
      case 'left':
        return { x: container.x, y: container.y + container.height / 2 };
      case 'right':
        return { x: container.x + container.width, y: container.y + container.height / 2 };
      default:
        return { x: container.x + container.width / 2, y: container.y + container.height / 2 };
    }
  };
  
  const fromPoint = getAnchorPoint(from, fromSide);
  const toPoint = getAnchorPoint(to, toSide);
  
  // For horizontal connections (same Y), use horizontal line
  if (Math.abs(fromPoint.y - toPoint.y) < 1) {
    return `M ${fromPoint.x} ${fromPoint.y} L ${toPoint.x} ${toPoint.y}`;
  }
  
  // For vertical connections (same X), use vertical line
  if (Math.abs(fromPoint.x - toPoint.x) < 1) {
    return `M ${fromPoint.x} ${fromPoint.y} L ${toPoint.x} ${toPoint.y}`;
  }
  
  // For diagonal connections, use L-shaped path
  const midY = (fromPoint.y + toPoint.y) / 2;
  return `M ${fromPoint.x} ${fromPoint.y} L ${fromPoint.x} ${midY} L ${toPoint.x} ${midY} L ${toPoint.x} ${toPoint.y}`;
}

/**
 * Generate Functional View SVG
 */
function generateFunctionalViewSvg(containers: any[], connections: any[]): string {
  const VIEWBOX_WIDTH = 1200;
  const VIEWBOX_HEIGHT = 1140;
  
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}" style="background: #f5f5f5;">\n`;
  
  // Layer backgrounds
  svg += `  <!-- Layer Backgrounds -->\n`;
  svg += `  <!-- Business Process Layer (white) -->\n`;
  svg += `  <rect x="0" y="80" width="${VIEWBOX_WIDTH}" height="260" fill="#ffffff" stroke="rgba(22, 65, 148, 0.1)" stroke-width="1"/>\n`;
  svg += `  <text x="20" y="100" font-family="Arial, sans-serif" font-size="18" fill="#163494" font-weight="600">Business Process Layer (layer-bp)</text>\n`;
  svg += `  \n`;
  svg += `  <!-- DSP Layer (blue) -->\n`;
  svg += `  <rect x="0" y="340" width="${VIEWBOX_WIDTH}" height="540" fill="rgba(207, 230, 255, 0.5)" stroke="rgba(22, 65, 148, 0.15)" stroke-width="1"/>\n`;
  svg += `  <text x="20" y="360" font-family="Arial, sans-serif" font-size="18" fill="#163494" font-weight="600">DSP Layer (layer-dsp)</text>\n`;
  svg += `  \n`;
  svg += `  <!-- Shopfloor Layer (gray) -->\n`;
  svg += `  <rect x="0" y="880" width="${VIEWBOX_WIDTH}" height="260" fill="rgba(241, 243, 247, 0.8)" stroke="rgba(31, 54, 91, 0.12)" stroke-width="1"/>\n`;
  svg += `  <text x="20" y="900" font-family="Arial, sans-serif" font-size="18" fill="#163494" font-weight="600">Shopfloor Layer (layer-sf)</text>\n`;
  svg += `  \n`;
  
  // Business Process containers
  svg += `  <!-- Business Process Containers -->\n`;
  svg += `  <g id="business-layer">\n`;
  const bpContainers = containers.filter(c => c.id?.startsWith('bp-') && !c.id.includes('group'));
  for (const container of bpContainers) {
    svg += `    <!-- ${container.id} -->\n`;
    svg += `    <rect x="${container.x}" y="${container.y}" width="${container.width}" height="${container.height}" fill="#ffffff" stroke="rgba(22, 65, 148, 0.25)" stroke-width="2" rx="8"/>\n`;
    const centerY = container.y + container.height / 2;
    const centerX = container.x + container.width / 2;
    // No hyphen break for BP layer
    svg += `    ${generateCenteredLabel(centerX, centerY, container.id, { fontSize: 28, fontWeight: '600', iconKey: (container as any).logoIconKey, breakAtHyphen: false })}\n`;
    svg += `    \n`;
  }
  svg += `  </g>\n`;
  svg += `  \n`;
  
  // DSP Layer containers
  svg += `  <!-- DSP Layer Containers -->\n`;
  svg += `  <g id="dsp-layer">\n`;
  const dspContainers = containers.filter(c => c.id?.startsWith('dsp-'));
  for (const container of dspContainers) {
    svg += `    <!-- ${container.id} -->\n`;
    svg += `    <rect x="${container.x}" y="${container.y}" width="${container.width}" height="${container.height}" fill="rgba(255, 255, 255, 0.95)" stroke="#163494" stroke-width="2" rx="8"/>\n`;
    const centerY = container.y + 36; // Keep at top for DSP containers
    const centerX = container.x + container.width / 2;
    // No hyphen break for DSP layer, use centerIconKey for SVG filename
    svg += `    ${generateCenteredLabel(centerX, centerY, container.id, { fontSize: 32, fontWeight: '600', iconKey: (container as any).centerIconKey || (container as any).logoIconKey, breakAtHyphen: false })}\n`;
    svg += `    \n`;
  }
  svg += `  </g>\n`;
  svg += `  \n`;
  
  // Shopfloor Layer
  svg += `  <!-- Shopfloor Layer -->\n`;
  svg += `  <g id="shopfloor-layer">\n`;
  
  // Systems Group
  const systemsGroup = containers.find(c => c.id === 'sf-systems-group');
  if (systemsGroup) {
    svg += `    <!-- Systems Group -->\n`;
    svg += `    <rect x="${systemsGroup.x}" y="${systemsGroup.y}" width="${systemsGroup.width}" height="${systemsGroup.height}" fill="#ffffff" stroke="rgba(0, 0, 0, 0.08)" stroke-width="1" rx="16"/>\n`;
    svg += `    <text x="${systemsGroup.x + systemsGroup.width / 2}" y="${systemsGroup.y + systemsGroup.height - 10}" font-family="Arial, sans-serif" font-size="28" fill="#163494" text-anchor="middle" font-weight="600">sf-systems-group</text>\n`;
    svg += `    \n`;
  }
  
  // Systems
  const systemContainers = containers.filter(c => c.id?.startsWith('sf-system-') && !c.id.includes('group'));
  for (const container of systemContainers) {
    svg += `    <!-- ${container.id} -->\n`;
    svg += `    <rect x="${container.x}" y="${container.y}" width="${container.width}" height="${container.height}" fill="url(#shopfloor-gradient)" stroke="rgba(0, 0, 0, 0.12)" stroke-width="1" rx="2"/>\n`;
    const centerY = container.y + container.height / 2;
    const centerX = container.x + container.width / 2;
    // Hyphen break for shopfloor layer
    svg += `    ${generateCenteredLabel(centerX, centerY, container.id, { fontSize: 20, iconKey: (container as any).logoIconKey, breakAtHyphen: true })}\n`;
    svg += `    \n`;
  }
  
  // Devices Group
  const devicesGroup = containers.find(c => c.id === 'sf-devices-group');
  if (devicesGroup) {
    svg += `    <!-- Devices Group -->\n`;
    svg += `    <rect x="${devicesGroup.x}" y="${devicesGroup.y}" width="${devicesGroup.width}" height="${devicesGroup.height}" fill="#ffffff" stroke="rgba(0, 0, 0, 0.08)" stroke-width="1" rx="16"/>\n`;
    svg += `    <text x="${devicesGroup.x + devicesGroup.width / 2}" y="${devicesGroup.y + devicesGroup.height - 10}" font-family="Arial, sans-serif" font-size="28" fill="#163494" text-anchor="middle" font-weight="600">sf-devices-group</text>\n`;
    svg += `    \n`;
  }
  
  // Devices
  const deviceContainers = containers.filter(c => c.id?.startsWith('sf-device-'));
  for (const container of deviceContainers) {
    svg += `    <!-- ${container.id} -->\n`;
    svg += `    <rect x="${container.x}" y="${container.y}" width="${container.width}" height="${container.height}" fill="url(#shopfloor-gradient)" stroke="rgba(0, 0, 0, 0.12)" stroke-width="1" rx="2"/>\n`;
    const centerY = container.y + container.height / 2;
    const centerX = container.x + container.width / 2;
    // Hyphen break for shopfloor layer
    svg += `    ${generateCenteredLabel(centerX, centerY, container.id, { fontSize: 18, iconKey: (container as any).logoIconKey, breakAtHyphen: true })}\n`;
    svg += `    \n`;
  }
  
  svg += `  </g>\n`;
  svg += `  \n`;
  
  // Connections
  svg += `  <!-- Connections from Business Process to Edge (L-form, bidirectional, no labels) -->\n`;
  svg += `  <g id="connections-bp" stroke="#666" stroke-width="2" fill="none" marker-start="url(#arrowhead-reverse)" marker-end="url(#arrowhead)">\n`;
  const bpConnections = connections.filter(c => c.fromId?.startsWith('bp-') && c.toId === 'dsp-edge');
  for (const conn of bpConnections) {
    const fromContainer = containers.find(c => c.id === conn.fromId);
    const toContainer = containers.find(c => c.id === conn.toId);
    if (fromContainer && toContainer) {
      const path = calculateConnectionPath(fromContainer, toContainer, conn.fromSide, conn.toSide);
      svg += `    <!-- ${conn.id} -->\n`;
      svg += `    <path d="${path}"/>\n`;
      svg += `    \n`;
    }
  }
  svg += `  </g>\n`;
  svg += `  \n`;
  
  svg += `  <!-- Connections in DSP Layer (L-form, bidirectional, no labels) -->\n`;
  svg += `  <g id="connections-dsp" stroke="#666" stroke-width="2" fill="none" marker-start="url(#arrowhead-reverse)" marker-end="url(#arrowhead)">\n`;
  const dspConnections = connections.filter(c => c.fromId?.startsWith('dsp-') && c.toId?.startsWith('dsp-'));
  for (const conn of dspConnections) {
    const fromContainer = containers.find(c => c.id === conn.fromId);
    const toContainer = containers.find(c => c.id === conn.toId);
    if (fromContainer && toContainer) {
      const path = calculateConnectionPath(fromContainer, toContainer, conn.fromSide, conn.toSide);
      svg += `    <!-- ${conn.id} -->\n`;
      svg += `    <path d="${path}"/>\n`;
      svg += `    \n`;
    }
  }
  svg += `  </g>\n`;
  svg += `  \n`;
  
  svg += `  <!-- Connections from Edge to Shopfloor (L-form, bidirectional, no labels) -->\n`;
  svg += `  <g id="connections-sf" stroke="#666" stroke-width="2" fill="none" marker-start="url(#arrowhead-reverse)" marker-end="url(#arrowhead)">\n`;
  const sfConnections = connections.filter(c => c.fromId === 'dsp-edge' && (c.toId?.startsWith('sf-system-') || c.toId?.startsWith('sf-device-')));
  for (const conn of sfConnections) {
    const fromContainer = containers.find(c => c.id === conn.fromId);
    const toContainer = containers.find(c => c.id === conn.toId);
    if (fromContainer && toContainer) {
      const path = calculateConnectionPath(fromContainer, toContainer, conn.fromSide, conn.toSide);
      svg += `    <!-- ${conn.id} -->\n`;
      svg += `    <path d="${path}"/>\n`;
      svg += `    \n`;
    }
  }
  svg += `  </g>\n`;
  svg += `  \n`;
  
  // Arrow markers and gradients
  svg += `  <!-- Arrow marker definition -->\n`;
  svg += `  <defs>\n`;
  svg += `    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">\n`;
  svg += `      <polygon points="0 0, 10 3, 0 6" fill="#666"/>\n`;
  svg += `    </marker>\n`;
  svg += `    <marker id="arrowhead-reverse" markerWidth="10" markerHeight="10" refX="1" refY="3" orient="auto">\n`;
  svg += `      <polygon points="10 0, 0 3, 10 6" fill="#666"/>\n`;
  svg += `    </marker>\n`;
  svg += `    <linearGradient id="shopfloor-gradient" x1="0%" y1="0%" x2="0%" y2="100%">\n`;
  svg += `      <stop offset="0%" style="stop-color:#f1f3f7;stop-opacity:1" />\n`;
  svg += `      <stop offset="100%" style="stop-color:#e0e4ea;stop-opacity:1" />\n`;
  svg += `    </linearGradient>\n`;
  svg += `  </defs>\n`;
  
  // Legend (right top)
  const legendWidth = 350;
  const legendHeight = 70;
  const legendX = VIEWBOX_WIDTH - legendWidth - 20; // Right aligned with 20px margin
  const legendY = 20; // Top with 20px margin
  svg += `  <!-- Legend -->\n`;
  svg += `  <g id="legend" transform="translate(${legendX}, ${legendY})">\n`;
  svg += `    <rect x="0" y="0" width="${legendWidth}" height="${legendHeight}" fill="rgba(255, 255, 255, 0.95)" stroke="#163494" stroke-width="1" rx="4"/>\n`;
  svg += `    <text x="10" y="22" font-family="Arial, sans-serif" font-size="14" fill="#163494" font-weight="600">Legende:</text>\n`;
  svg += `    <text x="10" y="42" font-family="Arial, sans-serif" font-size="12" fill="#666">• Container Key (z.B. <tspan fill="#163494">bp-erp</tspan>, <tspan fill="#163494">sf-system-any</tspan>)</text>\n`;
  svg += `    <text x="10" y="58" font-family="Arial, sans-serif" font-size="12" fill="#666">• SVG Dateiname (z.B. <tspan fill="#666">(erp-application)</tspan>)</text>\n`;
  svg += `  </g>\n`;
  
  svg += `</svg>\n`;
  
  return svg;
}

/**
 * Generate combined Edge and MC Functions SVG (compact, DSP Layer only)
 */
function generateEdgeMcFunctionsSvg(): string {
  const VIEWBOX_WIDTH = 1200;
  const VIEWBOX_HEIGHT = 480; // Compact: only DSP Layer
  
  // Adjusted positions for compact view (centered vertically)
  const edgeX = 325;
  const edgeY = 40; // Start at top after layer label
  const edgeWidth = 480;
  const edgeHeight = 400;
  const edgeCenterX = edgeX + edgeWidth / 2;
  const edgeCenterY = edgeY + edgeHeight / 2;
  
  // MC container dimensions
  const mcX = 855;
  const mcY = 40; // Start at top after layer label
  const mcWidth = 315;
  const mcHeight = 400;
  const mcCenterX = mcX + mcWidth / 2;
  const mcCenterY = mcY + mcHeight / 2;
  
  // Edge function icons (9 icons)
  const edgeFunctionIcons = [
    'edge-interoperability',
    'edge-network',
    'edge-event-driven',
    'edge-choreography',
    'edge-digital-twin',
    'edge-best-of-breed',
    'edge-analytics',
    'edge-ai-enablement',
    'edge-autonomous-enterprise',
  ];
  
  // MC function icons (3 MC functions + 3 Edge instances)
  const mcFunctionIcons = [
    'mc-hierarchical-structure',
    'mc-orchestration',
    'mc-governance',
  ];
  
  const edgeInstanceIcons = [
    'logo-edge-a',
    'logo-edge-b',
    'logo-edge-c',
  ];
  
  // Circle positioning parameters for Edge
  const edgeStartDeg = 90; // Start at 90° (top)
  const edgeSpanDeg = 360; // Full circle
  const edgeTotal = edgeFunctionIcons.length;
  const edgeStep = edgeSpanDeg / edgeTotal; // 40° per icon
  const edgeIconRadius = 160; // Radius for icon positions
  const circleRadius = 36; // 50% larger than original (24 * 1.5 = 36)
  
  // Circle positioning parameters for MC Functions (right side, 120° segment starting at 300°)
  const mcStartDeg = 300; // Start at 300° (right side)
  const mcSpanDeg = 120; // 120° span for MC functions
  const mcTotal = mcFunctionIcons.length;
  const mcStep = mcSpanDeg / (mcTotal - 1); // Distribute evenly over 120° (60° per icon)
  const mcIconRadius = 112; // Radius for icon positions
  
  // Circle positioning parameters for Edge Instances (left side, 120° segment starting at 120°)
  const edgeInstanceStartDeg = 120; // Start at 120° (left side)
  const edgeInstanceSpanDeg = 120; // 120° span for Edge instances
  const edgeInstanceTotal = edgeInstanceIcons.length;
  const edgeInstanceStep = edgeInstanceSpanDeg / (edgeInstanceTotal - 1); // Distribute evenly over 120° (60° per icon)
  const edgeInstanceIconRadius = 112; // Radius for icon positions
  
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}" style="background: #f5f5f5;">\n`;
  
  // DSP Layer Background (compact)
  svg += `  <!-- DSP Layer Background -->\n`;
  svg += `  <rect x="0" y="0" width="${VIEWBOX_WIDTH}" height="${VIEWBOX_HEIGHT}" fill="rgba(207, 230, 255, 0.5)" stroke="rgba(22, 65, 148, 0.15)" stroke-width="1"/>\n`;
  svg += `  <text x="20" y="20" font-family="Arial, sans-serif" font-size="18" fill="#163494" font-weight="600">DSP Layer (layer-dsp)</text>\n`;
  svg += `  \n`;
  
  // Use original positions (no offset needed)
  const adjustedEdgeY = edgeY;
  const adjustedMcY = mcY;
  
  // dsp-edge Container
  svg += `  <!-- dsp-edge Container -->\n`;
  svg += `  <rect x="${edgeX}" y="${adjustedEdgeY}" width="${edgeWidth}" height="${edgeHeight}" fill="rgba(255, 255, 255, 0.95)" stroke="#163494" stroke-width="2" rx="8"/>\n`;
  // dsp-edge label removed (overlapped by function icons)
  svg += `  \n`;
  
  // Center Icon placeholder (logo-edge)
  svg += `  <!-- Center Icon placeholder (logo-edge) -->\n`;
  const adjustedEdgeCenterY = adjustedEdgeY + edgeHeight / 2;
  svg += `  <circle cx="${edgeCenterX}" cy="${adjustedEdgeCenterY}" r="42" fill="none" stroke="#163494" stroke-width="1" stroke-dasharray="4 4"/>\n`;
  svg += `  <text x="${edgeCenterX}" y="${adjustedEdgeCenterY + 5}" font-family="Arial, sans-serif" font-size="10" fill="#999" text-anchor="middle">logo-edge</text>\n`;
  svg += `  \n`;
  
  // Edge Function Icons (9 icons in circle, startDeg=90°, spanDeg=360°)
  svg += `  <!-- Edge Function Icons (9 icons in circle, startDeg=90°, spanDeg=360°) -->\n`;
  svg += `  <g id="edge-functions">\n`;
  
  edgeFunctionIcons.forEach((iconKey, index) => {
    const angleDeg = edgeStartDeg + index * edgeStep;
    const angleRad = (angleDeg * Math.PI) / 180;
    
    // Icon position (center of circle) - adjusted for new edgeCenterY
    const adjustedEdgeCenterY = adjustedEdgeY + edgeHeight / 2;
    const iconX = edgeCenterX + edgeIconRadius * Math.cos(angleRad);
    const iconY = adjustedEdgeCenterY + edgeIconRadius * Math.sin(angleRad);
    
    // Label position (centered in circle)
    const labelY = iconY; // Center the label in the circle
    
    svg += `    <!-- ${iconKey} (${angleDeg.toFixed(1)}°) -->\n`;
    svg += `    <circle cx="${iconX}" cy="${iconY}" r="${circleRadius}" fill="#ffffff" stroke="#163494" stroke-width="1"/>\n`;
    svg += `    ${generateEdgeFunctionLabel(iconX, labelY, iconKey, { fontSize: 18 })}\n`;
    svg += `    \n`;
  });
  
  svg += `  </g>\n`;
  svg += `  \n`;
  
  // dsp-mc Container
  svg += `  <!-- dsp-mc Container -->\n`;
  svg += `  <rect x="${mcX}" y="${adjustedMcY}" width="${mcWidth}" height="${mcHeight}" fill="rgba(255, 255, 255, 0.95)" stroke="#163494" stroke-width="2" rx="8"/>\n`;
  // dsp-mc label removed (overlapped by function icons)
  svg += `  \n`;
  
  // Center Icon placeholder (logo-mc)
  svg += `  <!-- Center Icon placeholder (logo-mc) -->\n`;
  const adjustedMcCenterY = adjustedMcY + mcHeight / 2;
  svg += `  <circle cx="${mcCenterX}" cy="${adjustedMcCenterY}" r="42" fill="none" stroke="#163494" stroke-width="1" stroke-dasharray="4 4"/>\n`;
  svg += `  <text x="${mcCenterX}" y="${adjustedMcCenterY + 5}" font-family="Arial, sans-serif" font-size="10" fill="#999" text-anchor="middle">logo-mc</text>\n`;
  svg += `  \n`;
  
  // MC Function Icons (3 icons in arc, right side, startDeg=300°, spanDeg=120°)
  svg += `  <!-- MC Function Icons (3 icons in arc, right side, startDeg=300°, spanDeg=120°) -->\n`;
  svg += `  <g id="mc-functions">\n`;
  
  mcFunctionIcons.forEach((iconKey, index) => {
    const angleDeg = mcStartDeg + index * mcStep;
    const angleRad = (angleDeg * Math.PI) / 180;
    
    // Icon position (center of circle) - adjusted for new mcCenterY
    const adjustedMcCenterY = adjustedMcY + mcHeight / 2;
    const iconX = mcCenterX + mcIconRadius * Math.cos(angleRad);
    const iconY = adjustedMcCenterY + mcIconRadius * Math.sin(angleRad);
    
    // Label position (centered in circle)
    const labelY = iconY; // Center the label in the circle
    
    svg += `    <!-- ${iconKey} (${angleDeg.toFixed(1)}°) -->\n`;
    svg += `    <circle cx="${iconX}" cy="${iconY}" r="${circleRadius}" fill="#ffffff" stroke="#163494" stroke-width="1"/>\n`;
    svg += `    ${generateEdgeFunctionLabel(iconX, labelY, iconKey, { fontSize: 18 })}\n`;
    svg += `    \n`;
  });
  
  svg += `  </g>\n`;
  svg += `  \n`;
  
  // Edge Instance Icons (3 icons in arc, left side, startDeg=120°, spanDeg=120°)
  svg += `  <!-- Edge Instance Icons (3 icons in arc, left side, startDeg=120°, spanDeg=120°) -->\n`;
  svg += `  <g id="edge-instances">\n`;
  
  edgeInstanceIcons.forEach((iconKey, index) => {
    const angleDeg = edgeInstanceStartDeg + index * edgeInstanceStep;
    const angleRad = (angleDeg * Math.PI) / 180;
    
    // Icon position (center of circle) - adjusted for new mcCenterY
    const adjustedMcCenterY = adjustedMcY + mcHeight / 2;
    const iconX = mcCenterX + edgeInstanceIconRadius * Math.cos(angleRad);
    const iconY = adjustedMcCenterY + edgeInstanceIconRadius * Math.sin(angleRad);
    
    // Label position (centered in circle)
    const labelY = iconY; // Center the label in the circle
    
    svg += `    <!-- ${iconKey} (${angleDeg.toFixed(1)}°) -->\n`;
    svg += `    <circle cx="${iconX}" cy="${iconY}" r="${circleRadius}" fill="#ffffff" stroke="#163494" stroke-width="1"/>\n`;
    svg += `    ${generateEdgeFunctionLabel(iconX, labelY, iconKey, { fontSize: 18 })}\n`;
    svg += `    \n`;
  });
  
  svg += `  </g>\n`;
  svg += `</svg>\n`;
  
  return svg;
}

/**
 * Generate Component View SVG (compact, DSP Layer only)
 */
function generateComponentViewSvg(): string {
  const VIEWBOX_WIDTH = 1200;
  const VIEWBOX_HEIGHT = 480; // Compact: only DSP Layer
  
  // Adjusted positions for compact view
  const edgeX = 325;
  const edgeY = 40; // Start at top after layer label
  const edgeBoxWidth = 480;
  const edgeBoxHeight = 400;
  
  // Use original positions (no offset needed)
  const adjustedEdgeY = edgeY;
  
  // Edge component layout parameters (from layout.shared.config.ts)
  const edgeComponentPadding = 10;
  const edgeComponentGap = 40;
  const edgeInnerWidth = edgeBoxWidth - 2 * edgeComponentPadding;
  const edgeInnerHeight = edgeBoxHeight - 2 * edgeComponentPadding;
  
  const componentColumns = 3;
  const componentWidth = (edgeInnerWidth - edgeComponentGap * (componentColumns - 1)) / componentColumns;
  const componentHeight = (edgeInnerHeight - edgeComponentGap * 2) / 3; // 3 rows, 2 vertical gaps
  
  // Position rows so that the middle row center aligns with edge box center (adjusted for new edgeY)
  const desiredMidCenterY = adjustedEdgeY + edgeBoxHeight / 2;
  const row1Y = desiredMidCenterY - (componentHeight / 2 + edgeComponentGap + componentHeight);
  const row2Y = row1Y + componentHeight + edgeComponentGap;
  const row3Y = row2Y + componentHeight + edgeComponentGap;
  
  const col1X = edgeX + edgeComponentPadding;
  const col2X = col1X + componentWidth + edgeComponentGap;
  const col3X = col2X + componentWidth + edgeComponentGap;
  
  // Row 1 specific gap so boxes are equally spaced from edges
  const row1Gap = (edgeBoxWidth - 2 * componentWidth) / 3;
  const row1Col1X = edgeX + row1Gap;
  const row1Col2X = edgeX + row1Gap * 2 + componentWidth;
  
  // Edge component definitions
  const edgeComponents = [
    // Row 1
    { id: 'edge-comp-disc', x: row1Col1X, y: row1Y, width: componentWidth, height: componentHeight },
    { id: 'edge-comp-event-bus', x: row1Col2X, y: row1Y, width: componentWidth, height: componentHeight },
    // Row 2
    { id: 'edge-comp-app-server', x: col1X, y: row2Y, width: componentWidth, height: componentHeight },
    { id: 'edge-comp-router', x: col2X, y: row2Y, width: componentWidth, height: componentHeight },
    { id: 'edge-comp-agent', x: col3X, y: row2Y, width: componentWidth, height: componentHeight },
    // Row 3
    { id: 'edge-comp-log-server', x: col1X, y: row3Y, width: componentWidth, height: componentHeight },
    { id: 'edge-comp-disi', x: col2X, y: row3Y, width: componentWidth, height: componentHeight },
    { id: 'edge-comp-database', x: col3X, y: row3Y, width: componentWidth, height: componentHeight },
  ];
  
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}" style="background: #f5f5f5;">\n`;
  
  // DSP Layer Background (compact)
  svg += `  <!-- DSP Layer Background -->\n`;
  svg += `  <rect x="0" y="0" width="${VIEWBOX_WIDTH}" height="${VIEWBOX_HEIGHT}" fill="rgba(207, 230, 255, 0.5)" stroke="rgba(22, 65, 148, 0.15)" stroke-width="1"/>\n`;
  svg += `  <text x="20" y="20" font-family="Arial, sans-serif" font-size="18" fill="#163494" font-weight="600">DSP Layer (layer-dsp)</text>\n`;
  svg += `  \n`;
  
  // dsp-edge Container (adjustedEdgeY already defined above)
  svg += `  <!-- dsp-edge Container -->\n`;
  svg += `  <rect x="${edgeX}" y="${adjustedEdgeY}" width="${edgeBoxWidth}" height="${edgeBoxHeight}" fill="rgba(255, 255, 255, 0.95)" stroke="#163494" stroke-width="2" rx="8"/>\n`;
  svg += `  <text x="${edgeX + edgeBoxWidth / 2}" y="${adjustedEdgeY + 24}" font-family="Arial, sans-serif" font-size="14" fill="#163494" text-anchor="middle" font-weight="600" dominant-baseline="middle">dsp-edge</text>\n`;
  svg += `  \n`;
  
  // Edge Components (8 components in 3x3 grid)
  svg += `  <!-- Edge Components (8 components in 3x3 grid) -->\n`;
  svg += `  <g id="edge-components">\n`;
  
  edgeComponents.forEach((comp) => {
    const centerX = comp.x + comp.width / 2;
    const centerY = comp.y + comp.height / 2;
    
    svg += `    <!-- ${comp.id} -->\n`;
    svg += `    <rect x="${comp.x}" y="${comp.y}" width="${comp.width}" height="${comp.height}" fill="#ffffff" stroke="#163494" stroke-width="1" rx="2"/>\n`;
    svg += `    ${generateEdgeFunctionLabel(centerX, centerY, comp.id, { fontSize: 18, breakAtSecondHyphen: true })}\n`;
    svg += `    \n`;
  });
  
  svg += `  </g>\n`;
  svg += `</svg>\n`;
  
  return svg;
}

/**
 * Generate Deployment View SVG (compact, DSP Layer only)
 */
function generateDeploymentViewSvg(): string {
  const VIEWBOX_WIDTH = 1200;
  const VIEWBOX_HEIGHT = 480; // Compact: only DSP Layer
  
  // Edge container dimensions (from layout.shared.config.ts)
  const edgeX = 325;
  const edgeY = 40; // Start at top after layer label
  const edgeBoxWidth = 480;
  const edgeBoxHeight = 400;
  
  // Deployment pipeline parameters (from layout.deployment.config.ts)
  // Use original positions (no offset needed)
  const adjustedEdgeY = edgeY;
  
  const pipelineStepWidth = 180;
  const pipelineStepHeight = 60;
  const pipelineOffsetX = 90;
  const pipelineOffsetY = -80;
  const pipelineStartX = edgeX + 16;
  const pipelineStartY = adjustedEdgeY + edgeBoxHeight - pipelineStepHeight - 20;
  
  const pipelineFills = [
    'rgba(0, 150, 129, 0.18)', // very light
    'rgba(0, 150, 129, 0.32)', // light
    'rgba(0, 150, 129, 0.46)', // medium-light
    'rgba(0, 150, 129, 0.60)', // medium
  ];
  
  const pipelineBorder = '#163494'; // solution-petrol-strong
  
  const deploymentSteps = [
    { id: 'deployment-step-integration', fill: pipelineFills[0] },
    { id: 'deployment-step-transformation', fill: pipelineFills[1] },
    { id: 'deployment-step-consolidation', fill: pipelineFills[2] },
    { id: 'deployment-step-provisioning', fill: pipelineFills[3] },
  ];
  
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}" style="background: #f5f5f5;">\n`;
  
  // DSP Layer Background (compact)
  svg += `  <!-- DSP Layer Background -->\n`;
  svg += `  <rect x="0" y="0" width="${VIEWBOX_WIDTH}" height="${VIEWBOX_HEIGHT}" fill="rgba(207, 230, 255, 0.5)" stroke="rgba(22, 65, 148, 0.15)" stroke-width="1"/>\n`;
  svg += `  <text x="20" y="20" font-family="Arial, sans-serif" font-size="18" fill="#163494" font-weight="600">DSP Layer (layer-dsp)</text>\n`;
  svg += `  \n`;
  
  // dsp-edge Container (adjustedEdgeY already defined above)
  svg += `  <!-- dsp-edge Container -->\n`;
  svg += `  <rect x="${edgeX}" y="${adjustedEdgeY}" width="${edgeBoxWidth}" height="${edgeBoxHeight}" fill="rgba(255, 255, 255, 0.95)" stroke="#163494" stroke-width="2" rx="8"/>\n`;
  svg += `  <text x="${edgeX + edgeBoxWidth / 2}" y="${adjustedEdgeY + 24}" font-family="Arial, sans-serif" font-size="14" fill="#163494" text-anchor="middle" font-weight="600" dominant-baseline="middle">dsp-edge</text>\n`;
  svg += `  \n`;
  
  // Deployment Pipeline Steps (treppenförmig)
  svg += `  <!-- Deployment Pipeline Steps -->\n`;
  svg += `  <g id="deployment-steps">\n`;
  
  deploymentSteps.forEach((step, index) => {
    const stepX = pipelineStartX + index * pipelineOffsetX;
    const stepY = pipelineStartY + index * pipelineOffsetY;
    const centerX = stepX + pipelineStepWidth / 2;
    const centerY = stepY + pipelineStepHeight / 2;
    
    svg += `    <!-- ${step.id} -->\n`;
    svg += `    <rect x="${stepX}" y="${stepY}" width="${pipelineStepWidth}" height="${pipelineStepHeight}" fill="${step.fill}" stroke="${pipelineBorder}" stroke-width="1" rx="2"/>\n`;
    svg += `    ${generateEdgeFunctionLabel(centerX, centerY, step.id, { fontSize: 18, breakAtSecondHyphen: true })}\n`;
    svg += `    \n`;
  });
  
  svg += `  </g>\n`;
  svg += `</svg>\n`;
  
  return svg;
}

/**
 * Main execution
 */
async function main() {
  console.log('Generating DSP SVG diagrams...\n');
  
  // Add the osf directory to the path so we can import config files
  const configPath = path.join(repoRoot, 'osf', 'apps', 'osf-ui', 'src', 'app', 'components', 'dsp-animation');
  
  // We'll need to use a dynamic import or require with proper path resolution
  // For now, let's try to read and evaluate the config files directly
  // This is a simplified approach - in production, you might want to compile the TypeScript first
  
  try {
    // Use tsx to execute the config file and extract data
    // Since we can't easily import Angular code, we'll use a data extraction approach
    
    // For now, let's create a minimal working version that uses hardcoded data
    // extracted from the config files
    // TODO: Improve this to actually execute the config functions
    
    console.log('Note: Using hardcoded container/connection data for initial version.');
    console.log('TODO: Extract data dynamically from config files.\n');
    
    // Hardcoded container data based on createDefaultContainers()
    // This matches the structure from layout.shared.config.ts
    const containers = [
      // Business Process containers
      { id: 'bp-erp', x: 100, y: 145, width: 190, height: 140, type: 'business', logoIconKey: 'erp-application' },
      { id: 'bp-mes', x: 320, y: 145, width: 190, height: 140, type: 'business', logoIconKey: 'mes-application' },
      { id: 'bp-cloud', x: 540, y: 145, width: 190, height: 140, type: 'business', logoIconKey: 'bp-cloud-apps' },
      { id: 'bp-analytics', x: 760, y: 145, width: 190, height: 140, type: 'business', logoIconKey: 'bp-analytics' },
      { id: 'bp-data-lake', x: 980, y: 145, width: 190, height: 140, type: 'business', logoIconKey: 'bp-data-lake' },
  // DSP containers
  { id: 'dsp-ux', x: 100, y: 480, width: 175, height: 260, type: 'dsp', centerIconKey: 'ux-box' },
  { id: 'dsp-edge', x: 325, y: 410, width: 480, height: 400, type: 'dsp-edge', centerIconKey: 'logo-edge' },
  { id: 'dsp-mc', x: 855, y: 410, width: 315, height: 400, type: 'dsp-cloud', centerIconKey: 'logo-mc' },
      // Shopfloor Systems Group
      { id: 'sf-systems-group', x: 100, y: 927.5, width: 402.4, height: 165, type: 'shopfloor-group' },
      // Shopfloor Systems
      { id: 'sf-system-any', x: 120, y: 937.5, width: 83.1, height: 120, type: 'device', logoIconKey: 'shopfloor-systems' },
      { id: 'sf-system-fts', x: 213.1, y: 937.5, width: 83.1, height: 120, type: 'device', logoIconKey: 'shopfloor-fts' },
      { id: 'sf-system-warehouse', x: 306.2, y: 937.5, width: 83.1, height: 120, type: 'device', logoIconKey: 'shopfloor-warehouse' },
      { id: 'sf-system-factory', x: 399.3, y: 937.5, width: 83.1, height: 120, type: 'device', logoIconKey: 'shopfloor-factory' },
      // Shopfloor Devices Group
      { id: 'sf-devices-group', x: 562.4, y: 927.5, width: 607.6, height: 165, type: 'shopfloor-group' },
      // Shopfloor Devices
      { id: 'sf-device-mill', x: 582.4, y: 937.5, width: 86.3, height: 120, type: 'device', logoIconKey: 'device-mill' },
      { id: 'sf-device-drill', x: 678.7, y: 937.5, width: 86.3, height: 120, type: 'device', logoIconKey: 'device-drill' },
      { id: 'sf-device-aiqs', x: 774.9, y: 937.5, width: 86.3, height: 120, type: 'device', logoIconKey: 'device-aiqs' },
      { id: 'sf-device-hbw', x: 871.2, y: 937.5, width: 86.3, height: 120, type: 'device', logoIconKey: 'device-hbw' },
      { id: 'sf-device-dps', x: 967.5, y: 937.5, width: 86.3, height: 120, type: 'device', logoIconKey: 'device-dps' },
      { id: 'sf-device-chrg', x: 1063.7, y: 937.5, width: 86.3, height: 120, type: 'device', logoIconKey: 'device-chrg' },
    ];
    
    // Hardcoded connection data based on createDefaultConnections()
    const connections = [
      { id: 'conn_bp-erp_dsp-edge', fromId: 'bp-erp', toId: 'dsp-edge', fromSide: 'bottom', toSide: 'top' },
      { id: 'conn_bp-mes_dsp-edge', fromId: 'bp-mes', toId: 'dsp-edge', fromSide: 'bottom', toSide: 'top' },
      { id: 'conn_bp-cloud_dsp-edge', fromId: 'bp-cloud', toId: 'dsp-edge', fromSide: 'bottom', toSide: 'top' },
      { id: 'conn_bp-analytics_dsp-edge', fromId: 'bp-analytics', toId: 'dsp-edge', fromSide: 'bottom', toSide: 'top' },
      { id: 'conn_bp-data-lake_dsp-edge', fromId: 'bp-data-lake', toId: 'dsp-edge', fromSide: 'bottom', toSide: 'top' },
      { id: 'conn_dsp-ux_dsp-edge', fromId: 'dsp-ux', toId: 'dsp-edge', fromSide: 'right', toSide: 'left' },
      { id: 'conn_dsp-edge_dsp-mc', fromId: 'dsp-edge', toId: 'dsp-mc', fromSide: 'right', toSide: 'left' },
      { id: 'conn_dsp-edge_sf-system-any', fromId: 'dsp-edge', toId: 'sf-system-any', fromSide: 'bottom', toSide: 'top' },
      { id: 'conn_dsp-edge_sf-system-fts', fromId: 'dsp-edge', toId: 'sf-system-fts', fromSide: 'bottom', toSide: 'top' },
      { id: 'conn_dsp-edge_sf-device-mill', fromId: 'dsp-edge', toId: 'sf-device-mill', fromSide: 'bottom', toSide: 'top' },
      { id: 'conn_dsp-edge_sf-device-drill', fromId: 'dsp-edge', toId: 'sf-device-drill', fromSide: 'bottom', toSide: 'top' },
      { id: 'conn_dsp-edge_sf-device-aiqs', fromId: 'dsp-edge', toId: 'sf-device-aiqs', fromSide: 'bottom', toSide: 'top' },
      { id: 'conn_dsp-edge_sf-device-hbw', fromId: 'dsp-edge', toId: 'sf-device-hbw', fromSide: 'bottom', toSide: 'top' },
      { id: 'conn_dsp-edge_sf-device-dps', fromId: 'dsp-edge', toId: 'sf-device-dps', fromSide: 'bottom', toSide: 'top' },
      { id: 'conn_dsp-edge_sf-device-chrg', fromId: 'dsp-edge', toId: 'sf-device-chrg', fromSide: 'bottom', toSide: 'top' },
    ];
    
  // Generate functional view
  const functionalViewSvg = generateFunctionalViewSvg(containers, connections);
  
  // Write to file
  const outputDir = path.join(repoRoot, 'osf', 'apps', 'osf-ui', 'src', 'app', 'components', 'dsp-animation', 'configs', 'assets');
  const outputPath = path.join(outputDir, 'dsp-architecture-functional-view.svg');
  
  fs.writeFileSync(outputPath, functionalViewSvg, 'utf8');
  console.log(`✓ Generated: ${path.relative(repoRoot, outputPath)}`);
  
  // Generate combined edge-mc-functions SVG
  const edgeMcFunctionsSvg = generateEdgeMcFunctionsSvg();
  const edgeMcFunctionsPath = path.join(outputDir, 'dsp-architecture-edge-mc-functions.svg');
  fs.writeFileSync(edgeMcFunctionsPath, edgeMcFunctionsSvg, 'utf8');
  console.log(`✓ Generated: ${path.relative(repoRoot, edgeMcFunctionsPath)}`);
  
  // Generate component-view SVG
  const componentViewSvg = generateComponentViewSvg();
  const componentViewPath = path.join(outputDir, 'dsp-architecture-component-view.svg');
  fs.writeFileSync(componentViewPath, componentViewSvg, 'utf8');
  console.log(`✓ Generated: ${path.relative(repoRoot, componentViewPath)}`);
  
  // Generate deployment-view SVG
  const deploymentViewSvg = generateDeploymentViewSvg();
  const deploymentViewPath = path.join(outputDir, 'dsp-architecture-deployment-view.svg');
  fs.writeFileSync(deploymentViewPath, deploymentViewSvg, 'utf8');
  console.log(`✓ Generated: ${path.relative(repoRoot, deploymentViewPath)}`);
    
  } catch (error) {
    console.error('Error generating SVG diagrams:', error);
    process.exit(1);
  }
}

// Run the script
main();
