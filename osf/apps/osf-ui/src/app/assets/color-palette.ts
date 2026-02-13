/**
 * ORBIS Corporate Identity Color Palette
 * 
 * This file contains the official ORBIS CI color definitions based on the
 * corporate style guide. All colors are defined with their HEX, RGB, and
 * semantic names for consistent usage across the application.
 * 
 * Usage in TypeScript:
 *   import { ORBIS_COLORS } from '@app/assets/color-palette';
 *   const primaryBlue = ORBIS_COLORS.orbisBlue.strong;
 * 
 * Usage in SCSS:
 *   Use the CSS variables from _color-palette.scss instead:
 *   color: var(--orbis-blue-strong);
 */

export const ORBIS_COLORS = {
  // ========== ORBIS Blue (Primary Corporate Color) ==========
  orbisBlue: {
    strong: '#154194',   // Pantone 287 C, RGB: 22, 65, 148
    medium: '#5071af',   // Pantone 7683 C, RGB: 80, 113, 175
    light: '#8aa0ca',   // Pantone 7681 C, RGB: 138, 160, 202
  },

  // ========== ORBIS Grey (Complementary Neutral) ==========
  orbisGrey: {
    strong: '#a7a8aa',   // Cool Gray 6, RGB: 167, 168, 170
    medium: '#bbbcbc',   // Cool Gray 4, RGB: 187, 188, 188
    light: '#d0d0ce',   // Cool Gray 2, RGB: 208, 208, 206
  },

  // ========== ORBIS Special Colors ==========
  orbisNightBlue: '#16203b',   // Pantone 289 C, RGB: 22, 32, 59
  orbisDarkGrey: '#1c1c1c',   // RGB: 28, 28, 28

  // ========== SAP Blue (SAP Area Branding) ==========
  sapBlue: {
    strong: '#298fc2',   // Pantone 7689 C, RGB: 41, 143, 194
    medium: '#40b8e7',  // Pantone 298 C, RGB: 64, 184, 231
    light: '#80d0ef',   // Pantone 2905 C, RGB: 128, 208, 239
  },

  // ========== Microsoft Orange (Microsoft Area Branding) ==========
  microsoftOrange: {
    strong: '#fc4c02',  // Pantone 1655 C, RGB: 252, 76, 2
    medium: '#ff7f41',  // Pantone 164 C, RGB: 255, 127, 65
    light: '#ffa06a',   // Pantone 1565 C, RGB: 255, 160, 106
  },

  // ========== Shopfloor Highlight Orange (Shopfloor Layout Highlighting) ==========
  shopfloorHighlight: {
    strong: '#f97316',  // RGB: 249, 115, 22 - Primary highlight color for shopfloor elements
    medium: '#fb923c',  // RGB: 251, 146, 60 - Medium highlight for secondary elements
    light: '#fdba74',   // RGB: 253, 186, 116 - Light highlight for subtle accents
  },

  // ========== Solution Petrol (Solution Highlighting) ==========
  solutionPetrol: {
    strong: '#009681',  // Pantone 3285 C, RGB: 0, 150, 129
    medium: '#56b2a7',  // Pantone 7472 C, RGB: 86, 178, 167
    light: '#8fccc4',  // Pantone 564 C, RGB: 143, 204, 196
  },

  // ========== Highlight Green (Accent Color) ==========
  highlightGreen: {
    strong: '#64a70b',  // Pantone 369 C, RGB: 100, 167, 11
    medium: '#99cd57',  // Pantone 367 C, RGB: 153, 205, 87
    light: '#bbde8f',   // Pantone 7486 C, RGB: 187, 222, 143
  },

  // ========== Neutral Additional Colors ==========
  neutralDarkGrey: '#555555',  // 80% K, RGB: 86, 86, 85
  neutralLightGrey: '#eeeeee', // 10% K, RGB: 238, 238, 238

  // ========== Status Colors (Error, Success, Warning) ==========
  statusError: {
    strong: '#dc2626',  // RGB: 220, 38, 38 - Error states, critical alerts
    medium: '#ef4444',  // RGB: 239, 68, 68 - Medium error emphasis
    light: '#fca5a5',   // RGB: 252, 165, 165 - Light error background
  },
  statusSuccess: {
    strong: '#047857',  // RGB: 4, 120, 87 - Success states, positive feedback
    medium: '#10b981',  // RGB: 16, 185, 129 - Medium success emphasis
    light: '#86efac',   // RGB: 134, 239, 172 - Light success background
  },
  statusWarning: {
    strong: '#b45309',  // RGB: 180, 83, 9 - Warning states, caution
    medium: '#f59e0b',  // RGB: 245, 158, 11 - Medium warning emphasis
    light: '#fde68a',   // RGB: 253, 230, 138 - Light warning background
  },

  // ========== Diagram Colors (UC SVG Diagrams, DSP Architecture Views) ==========
  // Shared palette for all programmatically generated SVG diagrams.
  // When a UC diagram needs a lane, node, connection, or box color it should
  // reference ORBIS_COLORS.diagram.* so that a single change here propagates
  // consistently to every diagram (UC-01, UC-06, etc.).
  diagram: {
    // Lane backgrounds (semantic per domain area)
    laneBusinessFill: '#d5e8d4',     // RGB: 213, 232, 212 — Light Green for Business Context lanes
    laneBusinessStroke: '#82b366',   // RGB: 130, 179, 102 — Green border for Business lanes
    laneTraceFill: '#dae8fc',        // RGB: 218, 232, 252 — Light Blue for Trace & Genealogy lanes
    laneTraceStroke: '#6c8ebf',      // RGB: 108, 142, 191 — Blue border for Trace lanes
    laneShopfloorFill: '#f5f5f5',    // RGB: 245, 245, 245 — Light Grey for Shopfloor lanes
    laneShopfloorStroke: '#666666',  // RGB: 102, 102, 102 — Grey border for Shopfloor lanes
    laneEnvironmentFill: '#e1d5e7',  // RGB: 225, 213, 231 — Light Purple for Environment/Sensor lanes
    laneEnvironmentStroke: '#9673a6', // RGB: 150, 115, 166 — Purple border for Environment lanes
    targetAnalyticsFill: '#ffe6cc',  // RGB: 255, 230, 204 — Light Orange for Analytics/Outcome boxes
    targetAnalyticsStroke: '#d79b00', // RGB: 215, 155, 0 — Orange border for target boxes
    // Station node colors
    nodeDefault: '#ffffff',           // White — Standard station nodes
    nodeParallel: '#f8cecc',          // RGB: 248, 206, 204 — Light Red for parallel/dimmed nodes
    nodeStroke: '#1f1f1f',            // RGB: 31, 31, 31 — Dark Grey for node borders
    // Connection colors
    connectionStroke: '#1f1f1f',      // RGB: 31, 31, 31 — Standard connection/join lines
    connectionAlert: '#b85450',       // RGB: 184, 84, 80 — Red for parallel/alert connections
    // Thread colors
    threadCyan: '#00bcd4',            // RGB: 0, 188, 212 — Cyan for NFC/data thread lines
    // Box colors (business boxes, enrichment boxes)
    boxFill: '#ffffff',               // White — Standard box background
    boxStroke: '#1f1f1f',             // RGB: 31, 31, 31 — Standard box border
    // SVG background gradient
    bgGradientStart: '#fafbfc',       // RGB: 250, 251, 252 — Background gradient top
    bgGradientEnd: '#ffffff',         // White — Background gradient bottom
  },

  // ========== Track & Trace Event Colors (osf-weit) ==========
  // Used for Pick, Process, Drop events and Order types in Track & Trace components
  trackTrace: {
    pick: {
      main: '#9c27b0',  // RGB: 156, 39, 176 - Pick events, Storage Orders
      rgb: [156, 39, 176] as const,
      background: 'rgba(156, 39, 176, 0.05)',
    },
    process: {
      main: '#f97316',  // RGB: 249, 115, 22 - Process events (uses shopfloor-highlight-strong)
      background: 'rgba(249, 115, 22, 0.08)',
    },
    drop: {
      main: '#4caf50',  // RGB: 76, 175, 80 - Drop events, Production Orders
      rgb: [76, 175, 80] as const,
      background: 'rgba(76, 175, 80, 0.05)',
    },
    storageOrder: {
      main: '#9c27b0',  // RGB: 156, 39, 176 - Storage Order highlighting
      rgb: [156, 39, 176] as const,
      background: 'rgba(156, 39, 176, 0.05)',
    },
    productionOrder: {
      main: '#4caf50',  // RGB: 76, 175, 80 - Production Order highlighting
      rgb: [76, 175, 80] as const,
      background: 'rgba(76, 175, 80, 0.05)',
    },
    timeline: {
      dock: '#4caf50',  // RGB: 76, 175, 80 - Dock timeline marker
      turn: '#f97316',  // RGB: 249, 115, 22 - Turn timeline marker
      pass: '#5071af',  // RGB: 80, 113, 175 - Pass timeline marker (orbis-blue-medium)
      pick: '#9c27b0',  // RGB: 156, 39, 176 - Pick timeline marker
      drop: '#e91e63',  // RGB: 233, 30, 99 - Drop timeline marker
    },
  },
} as const;

/**
 * Type-safe color key for accessing ORBIS_COLORS
 */
export type OrbisColorKey =
  | 'orbis-blue-strong'
  | 'orbis-blue-medium'
  | 'orbis-blue-light'
  | 'orbis-grey-strong'
  | 'orbis-grey-medium'
  | 'orbis-grey-light'
  | 'orbis-nightblue'
  | 'orbis-darkgrey'
  | 'sap-blue-strong'
  | 'sap-blue-medium'
  | 'sap-blue-light'
  | 'microsoft-orange-strong'
  | 'microsoft-orange-medium'
  | 'microsoft-orange-light'
  | 'shopfloor-highlight-strong'
  | 'shopfloor-highlight-medium'
  | 'shopfloor-highlight-light'
  | 'solution-petrol-strong'
  | 'solution-petrol-medium'
  | 'solution-petrol-light'
  | 'highlight-green-strong'
  | 'highlight-green-medium'
  | 'highlight-green-light'
  | 'neutral-darkgrey'
  | 'neutral-lightgrey'
  | 'status-error-strong'
  | 'status-error-medium'
  | 'status-error-light'
  | 'status-success-strong'
  | 'status-success-medium'
  | 'status-success-light'
  | 'status-warning-strong'
  | 'status-warning-medium'
  | 'status-warning-light'
  | 'diagram-lane-business-fill'
  | 'diagram-lane-business-stroke'
  | 'diagram-lane-trace-fill'
  | 'diagram-lane-trace-stroke'
  | 'diagram-lane-shopfloor-fill'
  | 'diagram-lane-shopfloor-stroke'
  | 'diagram-lane-environment-fill'
  | 'diagram-lane-environment-stroke'
  | 'diagram-target-analytics-fill'
  | 'diagram-target-analytics-stroke'
  | 'diagram-node-default'
  | 'diagram-node-parallel'
  | 'diagram-node-stroke'
  | 'diagram-connection-stroke'
  | 'diagram-connection-alert'
  | 'diagram-thread-cyan'
  | 'diagram-box-fill'
  | 'diagram-box-stroke'
  | 'diagram-bg-gradient-start'
  | 'diagram-bg-gradient-end'
  | 'track-trace-pick'
  | 'track-trace-process'
  | 'track-trace-drop'
  | 'track-trace-storage-order'
  | 'track-trace-production-order'
  | 'track-trace-timeline-dock'
  | 'track-trace-timeline-turn'
  | 'track-trace-timeline-pass'
  | 'track-trace-timeline-pick'
  | 'track-trace-timeline-drop';

/**
 * Helper function to get a color value by key
 * @param key - The color key (e.g., 'orbis-blue-strong')
 * @returns The HEX color value
 */
export function getOrbisColor(key: OrbisColorKey): string {
  const map: Record<OrbisColorKey, string> = {
    'orbis-blue-strong': ORBIS_COLORS.orbisBlue.strong,
    'orbis-blue-medium': ORBIS_COLORS.orbisBlue.medium,
    'orbis-blue-light': ORBIS_COLORS.orbisBlue.light,
    'orbis-grey-strong': ORBIS_COLORS.orbisGrey.strong,
    'orbis-grey-medium': ORBIS_COLORS.orbisGrey.medium,
    'orbis-grey-light': ORBIS_COLORS.orbisGrey.light,
    'orbis-nightblue': ORBIS_COLORS.orbisNightBlue,
    'orbis-darkgrey': ORBIS_COLORS.orbisDarkGrey,
    'sap-blue-strong': ORBIS_COLORS.sapBlue.strong,
    'sap-blue-medium': ORBIS_COLORS.sapBlue.medium,
    'sap-blue-light': ORBIS_COLORS.sapBlue.light,
    'microsoft-orange-strong': ORBIS_COLORS.microsoftOrange.strong,
    'microsoft-orange-medium': ORBIS_COLORS.microsoftOrange.medium,
    'microsoft-orange-light': ORBIS_COLORS.microsoftOrange.light,
    'shopfloor-highlight-strong': ORBIS_COLORS.shopfloorHighlight.strong,
    'shopfloor-highlight-medium': ORBIS_COLORS.shopfloorHighlight.medium,
    'shopfloor-highlight-light': ORBIS_COLORS.shopfloorHighlight.light,
    'solution-petrol-strong': ORBIS_COLORS.solutionPetrol.strong,
    'solution-petrol-medium': ORBIS_COLORS.solutionPetrol.medium,
    'solution-petrol-light': ORBIS_COLORS.solutionPetrol.light,
    'highlight-green-strong': ORBIS_COLORS.highlightGreen.strong,
    'highlight-green-medium': ORBIS_COLORS.highlightGreen.medium,
    'highlight-green-light': ORBIS_COLORS.highlightGreen.light,
    'neutral-darkgrey': ORBIS_COLORS.neutralDarkGrey,
    'neutral-lightgrey': ORBIS_COLORS.neutralLightGrey,
    'status-error-strong': ORBIS_COLORS.statusError.strong,
    'status-error-medium': ORBIS_COLORS.statusError.medium,
    'status-error-light': ORBIS_COLORS.statusError.light,
    'status-success-strong': ORBIS_COLORS.statusSuccess.strong,
    'status-success-medium': ORBIS_COLORS.statusSuccess.medium,
    'status-success-light': ORBIS_COLORS.statusSuccess.light,
    'status-warning-strong': ORBIS_COLORS.statusWarning.strong,
    'status-warning-medium': ORBIS_COLORS.statusWarning.medium,
    'status-warning-light': ORBIS_COLORS.statusWarning.light,
    'diagram-lane-business-fill': ORBIS_COLORS.diagram.laneBusinessFill,
    'diagram-lane-business-stroke': ORBIS_COLORS.diagram.laneBusinessStroke,
    'diagram-lane-trace-fill': ORBIS_COLORS.diagram.laneTraceFill,
    'diagram-lane-trace-stroke': ORBIS_COLORS.diagram.laneTraceStroke,
    'diagram-lane-shopfloor-fill': ORBIS_COLORS.diagram.laneShopfloorFill,
    'diagram-lane-shopfloor-stroke': ORBIS_COLORS.diagram.laneShopfloorStroke,
    'diagram-lane-environment-fill': ORBIS_COLORS.diagram.laneEnvironmentFill,
    'diagram-lane-environment-stroke': ORBIS_COLORS.diagram.laneEnvironmentStroke,
    'diagram-target-analytics-fill': ORBIS_COLORS.diagram.targetAnalyticsFill,
    'diagram-target-analytics-stroke': ORBIS_COLORS.diagram.targetAnalyticsStroke,
    'diagram-node-default': ORBIS_COLORS.diagram.nodeDefault,
    'diagram-node-parallel': ORBIS_COLORS.diagram.nodeParallel,
    'diagram-node-stroke': ORBIS_COLORS.diagram.nodeStroke,
    'diagram-connection-stroke': ORBIS_COLORS.diagram.connectionStroke,
    'diagram-connection-alert': ORBIS_COLORS.diagram.connectionAlert,
    'diagram-thread-cyan': ORBIS_COLORS.diagram.threadCyan,
    'diagram-box-fill': ORBIS_COLORS.diagram.boxFill,
    'diagram-box-stroke': ORBIS_COLORS.diagram.boxStroke,
    'diagram-bg-gradient-start': ORBIS_COLORS.diagram.bgGradientStart,
    'diagram-bg-gradient-end': ORBIS_COLORS.diagram.bgGradientEnd,
    'track-trace-pick': ORBIS_COLORS.trackTrace.pick.main,
    'track-trace-process': ORBIS_COLORS.trackTrace.process.main,
    'track-trace-drop': ORBIS_COLORS.trackTrace.drop.main,
    'track-trace-storage-order': ORBIS_COLORS.trackTrace.storageOrder.main,
    'track-trace-production-order': ORBIS_COLORS.trackTrace.productionOrder.main,
    'track-trace-timeline-dock': ORBIS_COLORS.trackTrace.timeline.dock,
    'track-trace-timeline-turn': ORBIS_COLORS.trackTrace.timeline.turn,
    'track-trace-timeline-pass': ORBIS_COLORS.trackTrace.timeline.pass,
    'track-trace-timeline-pick': ORBIS_COLORS.trackTrace.timeline.pick,
    'track-trace-timeline-drop': ORBIS_COLORS.trackTrace.timeline.drop,
  };
  return map[key];
}

