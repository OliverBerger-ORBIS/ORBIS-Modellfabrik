/**
 * UC-00 Interoperability: Event-to-Process Map - Structure Configuration
 * 
 * Hierarchische Struktur:
 * 1. Columns (3 Columns: Sources, DSP, Targets)
 * 2. Lanes innerhalb der Columns (mit Überschrift, Icon, Höhe aus Inhalt, gleichmäßige Spacing-Verteilung)
 * 3. Chips innerhalb der Lanes
 * 
 * Alle Texte verwenden I18n-Keys, die zur Laufzeit ersetzt werden.
 */

export interface Uc00Chip {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  textKey: string;
  iconPath?: string;
  iconX?: number;
  iconY?: number;
  iconWidth?: number;
  iconHeight?: number;
  multiline?: boolean;
  textLines?: string[];
  // Special properties for badges
  fill?: string;
  stroke?: string;
  // Special properties for state chips
  statusDots?: Array<{ cx: number; cy: number; color: 'running' | 'idle' | 'fail' }>;
  statusLabels?: string[]; // Labels for status dots (without the heading)
  // Special properties for operation chip (icons per line)
  // offsetX: horizontal offset from text end (positive = right of text)
  // offsetY: vertical offset from text baseline (positive = below baseline, negative = above)
  operationIcons?: Array<{ lineIndex: number; iconPath: string; offsetX: number; offsetY: number; iconWidth: number; iconHeight: number }>;
}

export interface Uc00Lane {
  id: string;
  titleKey: string;
  iconPath: string;
  iconX: number;
  iconY: number;
  iconWidth: number;
  iconHeight: number;
  chips: Uc00Chip[];
  // Calculated properties (will be set by layout calculator)
  x?: number;
  y?: number;
  width?: number;
  height?: number;
}

export interface Uc00Column {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  headerKey: string;
  headerX: number;
  headerY: number;
  lanes: Uc00Lane[];
  // Calculated spacing between lanes
  laneSpacing?: number;
}

export interface Uc00Step {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  descriptionKey: string;
}

export interface Uc00Bar {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  textKey: string;
  multiline?: boolean;
  textLines?: string[];
  fill?: string;
  stroke?: string;
}

export interface Uc00TimelinePoint {
  x: number;
  y: number;
  iconPath: string;
  iconX: number;
  iconY: number;
  iconWidth: number;
  iconHeight: number;
  labelKey: string;
  labelY: number;
}

export interface Uc00Target {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  iconPath: string;
  iconX: number;
  iconY: number;
  iconWidth: number;
  iconHeight: number;
  labelKey: string;
  labelY: number;
}

export interface Uc00Outcome {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  textKey: string;
  multiline?: boolean;
  textLines?: string[];
}

export interface Uc00Structure {
  // Dimensions
  viewBox: { width: number; height: number };
  
  // Title and subtitle
  title: { x: number; y: number; key: string };
  subtitle: { x: number; y: number; key: string };
  
  // Columns (hierarchical structure)
  columns: {
    sources: Uc00Column;
    dsp: {
      column: Omit<Uc00Column, 'lanes'>;
      steps: Uc00Step[];
      arrows: Array<{ x1: number; y1: number; x2: number; y2: number }>;
      bars: Uc00Bar[];
    };
    targets: {
      column: Omit<Uc00Column, 'lanes'>;
      processViewBox: {
        x: number;
        y: number;
        width: number;
        height: number;
        titleKey: string;
        timeline: {
          lineX1: number;
          lineY: number;
          lineX2: number;
          points: Uc00TimelinePoint[];
        };
      };
      targets: Uc00Target[];
      noteKey: string;
      noteX: number;
      noteY: number;
      outcomes: Uc00Outcome[];
    };
  };
  
  stepDescription: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  
  footer: {
    x: number;
    y: number;
    key: string;
  };
}

/**
 * Calculates lane positions and spacing within a column
 * Ensures equal spacing between lanes
 * Chips have relative positions within their lane (y relative to lane start)
 */
function calculateLaneLayout(column: Uc00Column): void {
  const headerHeight = 50; // Space for header
  const startY = column.y + headerHeight;
  const availableHeight = column.height - headerHeight;
  
  // Calculate lane heights from chips (chips have absolute y positions in original structure)
  const laneHeights: number[] = [];
  column.lanes.forEach((lane, laneIndex) => {
    const baseChipY = Math.min(...lane.chips.map(c => c.y));
    const maxChipBottom = Math.max(...lane.chips.map(c => c.y + c.height), baseChipY);
    const laneHeight = maxChipBottom - baseChipY + 80;
    laneHeights.push(laneHeight);
    lane.height = laneHeight;
  });
  
  const totalLaneHeight = laneHeights.reduce((sum, h) => sum + h, 0);
  const nLanes = column.lanes.length;
  const nGaps = nLanes + 1;
  const totalGapSpace = availableHeight - totalLaneHeight;
  const gapSize = totalGapSpace / nGaps;
  column.laneSpacing = gapSize;
  
  let currentY = startY + gapSize;
  column.lanes.forEach((lane, laneIndex) => {
    lane.x = column.x + 30;
    lane.y = currentY;
    lane.width = column.width - 60;
    if (!lane.height) {
      lane.height = laneHeights[laneIndex];
    }
    const baseChipY = Math.min(...lane.chips.map(c => c.y));
    const offsetY = currentY - baseChipY + 60;
    
    lane.chips.forEach((chip) => {
      chip.y = chip.y + offsetY;
      if (chip.iconY !== undefined) {
        chip.iconY = chip.iconY + offsetY;
      }
    });
    const baseIconY = lane.iconY;
    lane.iconY = baseIconY + offsetY;
    currentY += lane.height + gapSize;
  });
}

/** Content starts after step description (y 20–120); einheitlich mit UC-01 bis UC-05 */
const UC00_COLUMN_START_Y = 130;

/** ViewBox 1920x1080 – einheitlich mit allen anderen Use-Cases */
const UC00_VIEWBOX = { width: 1920, height: 1080 };

/** Column layout: 3 columns, gleichverteilt breiter für Target-Systeme wie UC-04 (subW 160) */
const UC00_COLUMN_WIDTH = 600;
const UC00_COLUMN_GAP = 40;
const UC00_SOURCES_X = 20;
const UC00_DSP_X = UC00_SOURCES_X + UC00_COLUMN_WIDTH + UC00_COLUMN_GAP;
const UC00_TARGETS_X = UC00_DSP_X + UC00_COLUMN_WIDTH + UC00_COLUMN_GAP;

/**
 * Creates the UC-00 structure configuration with all positions and I18n keys
 */
export function createUc00Structure(): Uc00Structure {
  const colY = UC00_COLUMN_START_Y;
  const colH = UC00_VIEWBOX.height - colY;

  const structure: Uc00Structure = {
    viewBox: UC00_VIEWBOX,
    title: { x: 960, y: 42, key: 'uc00.title' },
    subtitle: { x: 960, y: 74, key: 'uc00.subtitle' },
    stepDescription: { x: 960, y: 20, width: 1400, height: 100 },
    columns: {
      sources: {
        id: 'sources',
        x: UC00_SOURCES_X,
        y: colY,
        width: UC00_COLUMN_WIDTH,
        height: colH,
        headerX: UC00_SOURCES_X + 40,
        headerY: colY + 40,
        headerKey: 'uc00.sources.header',
        lanes: [
          { id: 'business_context', titleKey: 'uc00.lane.business_context.title', iconPath: '/assets/svg/business/erp-application.svg', iconX: 520, iconY: 318, iconWidth: 70, iconHeight: 70, chips: [
            { id: 'production_order', x: 160, y: 420, width: 150, height: 50, textKey: 'uc00.chip.production_order', multiline: true, textLines: ['uc00.chip.production_order.line1', 'uc00.chip.production_order.line2'], iconPath: '/assets/svg/ui/heading-production.svg', iconX: 280, iconY: 430, iconWidth: 20, iconHeight: 20 },
            { id: 'storage_order', x: 330, y: 420, width: 150, height: 50, textKey: 'uc00.chip.storage_order', multiline: true, textLines: ['uc00.chip.storage_order.line1', 'uc00.chip.storage_order.line2'], iconPath: '/assets/svg/shopfloor/shared/order-tracking.svg', iconX: 450, iconY: 430, iconWidth: 20, iconHeight: 20 },
            { id: 'material', x: 160, y: 480, width: 150, height: 30, textKey: 'uc00.chip.material', iconPath: '/assets/svg/ui/heading-customer-orders.svg', iconX: 280, iconY: 485, iconWidth: 20, iconHeight: 20 },
            { id: 'customer', x: 330, y: 480, width: 150, height: 30, textKey: 'uc00.chip.customer', iconPath: '/assets/svg/shopfloor/shared/customer.svg', iconX: 450, iconY: 485, iconWidth: 20, iconHeight: 20 },
            { id: 'routing', x: 160, y: 520, width: 150, height: 30, textKey: 'uc00.chip.routing', iconPath: '/assets/svg/dsp/extra/process.svg', iconX: 280, iconY: 525, iconWidth: 20, iconHeight: 20 },
            { id: 'operation', x: 330, y: 520, width: 150, height: 30, textKey: 'uc00.chip.operation', iconPath: '/assets/svg/shopfloor/systems/bp-system.svg', iconX: 450, iconY: 525, iconWidth: 20, iconHeight: 20 },
          ]},
          { id: 'machine_station', titleKey: 'uc00.lane.machine_station.title', iconPath: '/assets/svg/shopfloor/stations/drill-station.svg', iconX: 520, iconY: 533, iconWidth: 70, iconHeight: 70, chips: [
            { id: 'operation_chip', x: 160, y: 640, width: 150, height: 70, textKey: 'uc00.chip.operation_label', multiline: true, textLines: ['uc00.chip.operation_label', 'uc00.chip.start', 'uc00.chip.stop'], operationIcons: [
              { lineIndex: 1, iconPath: '/assets/svg/shopfloor/shared/driving-status.svg', offsetX: 15, offsetY: 10, iconWidth: 16, iconHeight: 16 },
              { lineIndex: 2, iconPath: '/assets/svg/shopfloor/shared/stopped-status.svg', offsetX: 20, offsetY: 10, iconWidth: 16, iconHeight: 16 },
            ]},
            { id: 'state_chip', x: 330, y: 640, width: 150, height: 110, textKey: 'uc00.chip.state_label', multiline: false, statusDots: [
              { cx: 370, cy: 680, color: 'running' },
              { cx: 370, cy: 705, color: 'idle' },
              { cx: 370, cy: 730, color: 'fail' },
            ], statusLabels: ['uc00.chip.running', 'uc00.chip.idle', 'uc00.chip.fail']},
          ]},
          { id: 'agv_system', titleKey: 'uc00.lane.agv_system.title', iconPath: '/assets/svg/shopfloor/shared/agv-vehicle.svg', iconX: 520, iconY: 718, iconWidth: 70, iconHeight: 70, chips: [
            { id: 'pick', x: 160, y: 820, width: 150, height: 30, textKey: 'uc00.chip.pick', iconPath: '/assets/svg/shopfloor/shared/pick-event.svg', iconX: 280, iconY: 825, iconWidth: 20, iconHeight: 20 },
            { id: 'transfer', x: 330, y: 820, width: 150, height: 30, textKey: 'uc00.chip.transfer', iconPath: '/assets/svg/shopfloor/shared/pass-event.svg', iconX: 450, iconY: 825, iconWidth: 20, iconHeight: 20 },
            { id: 'drop', x: 160, y: 860, width: 150, height: 30, textKey: 'uc00.chip.drop', iconPath: '/assets/svg/shopfloor/shared/drop-event.svg', iconX: 280, iconY: 865, iconWidth: 20, iconHeight: 20 },
            { id: 'route', x: 330, y: 860, width: 150, height: 30, textKey: 'uc00.chip.route', iconPath: '/assets/svg/ui/heading-route.svg', iconX: 450, iconY: 865, iconWidth: 20, iconHeight: 20 },
          ]},
          { id: 'quality_aiqs', titleKey: 'uc00.lane.quality_aiqs.title', iconPath: '/assets/svg/shopfloor/stations/aiqs-station.svg', iconX: 520, iconY: 873, iconWidth: 70, iconHeight: 70, chips: [
            { id: 'check_quality_label', x: 170, y: 990, width: 0, height: 0, textKey: 'uc00.chip.check_quality' },
            { id: 'pass', x: 330, y: 980, width: 60, height: 24, textKey: 'uc00.chip.pass', fill: '#e8f5e9', stroke: '#4caf50' },
            { id: 'fail', x: 330, y: 1010, width: 60, height: 24, textKey: 'uc00.chip.fail', fill: '#ffebee', stroke: '#f44336' },
          ]},
          { id: 'environment_sensors', titleKey: 'uc00.lane.environment_sensors.title', iconPath: '/assets/svg/ui/heading-sensors.svg', iconX: 520, iconY: 1008, iconWidth: 70, iconHeight: 70, chips: [
            { id: 'temperature', x: 160, y: 1120, width: 150, height: 30, textKey: 'uc00.chip.temperature', iconPath: '/assets/svg/shopfloor/shared/temperature-sensor.svg', iconX: 280, iconY: 1125, iconWidth: 20, iconHeight: 20 },
            { id: 'energy', x: 330, y: 1120, width: 150, height: 30, textKey: 'uc00.chip.energy', iconPath: '/assets/svg/shopfloor/shared/battery.svg', iconX: 450, iconY: 1125, iconWidth: 20, iconHeight: 20 },
            { id: 'vibration', x: 160, y: 1160, width: 150, height: 30, textKey: 'uc00.chip.vibration', iconPath: '/assets/svg/shopfloor/shared/vibration-sensor.svg', iconX: 280, iconY: 1165, iconWidth: 20, iconHeight: 20 },
            { id: 'pressure', x: 330, y: 1160, width: 150, height: 30, textKey: 'uc00.chip.pressure', iconPath: '/assets/svg/shopfloor/shared/pressure-sensor.svg', iconX: 450, iconY: 1165, iconWidth: 20, iconHeight: 20 },
          ]},
        ],
      },
      dsp: {
        column: { id: 'dsp', x: UC00_DSP_X, y: colY, width: UC00_COLUMN_WIDTH, height: colH, headerX: UC00_DSP_X + 40, headerY: colY + 50, headerKey: 'uc00.dsp.header' },
        steps: [
          { id: 'normalize', x: UC00_DSP_X + 40, y: colY + 80, width: 520, height: 130, titleKey: 'uc00.step.normalize.title', descriptionKey: 'uc00.step.normalize.description' },
          { id: 'enrich', x: UC00_DSP_X + 40, y: colY + 250, width: 520, height: 130, titleKey: 'uc00.step.enrich.title', descriptionKey: 'uc00.step.enrich.description' },
          { id: 'correlate', x: UC00_DSP_X + 40, y: colY + 420, width: 520, height: 130, titleKey: 'uc00.step.correlate.title', descriptionKey: 'uc00.step.correlate.description' },
        ],
        arrows: [
          { x1: UC00_DSP_X + UC00_COLUMN_WIDTH / 2, y1: colY + 215, x2: UC00_DSP_X + UC00_COLUMN_WIDTH / 2, y2: colY + 225 },
          { x1: UC00_DSP_X + UC00_COLUMN_WIDTH / 2, y1: colY + 385, x2: UC00_DSP_X + UC00_COLUMN_WIDTH / 2, y2: colY + 395 },
        ],
        bars: [
          { id: 'process_ready', x: UC00_DSP_X + 80, y: colY + 610, width: 440, height: 56, textKey: 'uc00.bar.process_ready', fill: '#eaf5ea', stroke: '#bfe3bf' },
          { id: 'reusable', x: UC00_DSP_X + 80, y: colY + 700, width: 440, height: 56, textKey: 'uc00.bar.reusable' },
          { id: 'foundation', x: UC00_DSP_X + 80, y: colY + 790, width: 440, height: 70, textKey: 'uc00.bar.foundation', multiline: true, textLines: ['uc00.bar.foundation.line1', 'uc00.bar.foundation.line2'] },
        ],
      },
      targets: {
        column: { id: 'targets', x: UC00_TARGETS_X, y: colY, width: UC00_COLUMN_WIDTH, height: colH, headerX: UC00_TARGETS_X + 40, headerY: colY + 50, headerKey: 'uc00.targets.header' },
        processViewBox: {
          x: UC00_TARGETS_X + 40, y: colY + 90, width: 520, height: 200, titleKey: 'uc00.process_view.title',
          timeline: {
            lineX1: UC00_TARGETS_X + 70, lineY: colY + 200, lineX2: UC00_TARGETS_X + UC00_COLUMN_WIDTH - 50,
            points: [
              { x: UC00_TARGETS_X + 85, y: colY + 200, iconPath: '/assets/svg/shopfloor/stations/hbw-station.svg', iconX: UC00_TARGETS_X + 67.5, iconY: colY + 145, iconWidth: 35, iconHeight: 35, labelKey: 'uc00.timeline.warehouse', labelY: colY + 240 },
              { x: UC00_TARGETS_X + 163, y: colY + 200, iconPath: '/assets/svg/shopfloor/shared/agv-vehicle.svg', iconX: UC00_TARGETS_X + 145.5, iconY: colY + 145, iconWidth: 35, iconHeight: 35, labelKey: 'uc00.timeline.agv', labelY: colY + 240 },
              { x: UC00_TARGETS_X + 241, y: colY + 200, iconPath: '/assets/svg/shopfloor/stations/drill-station.svg', iconX: UC00_TARGETS_X + 223.5, iconY: colY + 145, iconWidth: 35, iconHeight: 35, labelKey: 'uc00.timeline.station', labelY: colY + 240 },
              { x: UC00_TARGETS_X + 319, y: colY + 200, iconPath: '/assets/svg/shopfloor/shared/pass-event.svg', iconX: UC00_TARGETS_X + 301.5, iconY: colY + 145, iconWidth: 35, iconHeight: 35, labelKey: 'uc00.timeline.transfer', labelY: colY + 240 },
              { x: UC00_TARGETS_X + 397, y: colY + 200, iconPath: '/assets/svg/shopfloor/stations/aiqs-station.svg', iconX: UC00_TARGETS_X + 379.5, iconY: colY + 145, iconWidth: 35, iconHeight: 35, labelKey: 'uc00.timeline.quality', labelY: colY + 240 },
              { x: UC00_TARGETS_X + 475, y: colY + 200, iconPath: '/assets/svg/shopfloor/shared/order-tracking.svg', iconX: UC00_TARGETS_X + 457.5, iconY: colY + 145, iconWidth: 35, iconHeight: 35, labelKey: 'uc00.timeline.complete', labelY: colY + 240 },
            ],
          },
        },
        targets: [
          { id: 'erp', x: UC00_TARGETS_X + 50, y: colY + 330, width: 160, height: 180, iconPath: '/assets/svg/business/erp-application.svg', iconX: UC00_TARGETS_X + 50 + 48, iconY: colY + 388, iconWidth: 64, iconHeight: 64, labelKey: 'uc00.target.erp', labelY: colY + 502 },
          { id: 'mes', x: UC00_TARGETS_X + 220, y: colY + 330, width: 160, height: 180, iconPath: '/assets/svg/business/mes-application.svg', iconX: UC00_TARGETS_X + 220 + 48, iconY: colY + 388, iconWidth: 64, iconHeight: 64, labelKey: 'uc00.target.mes', labelY: colY + 502 },
          { id: 'analytics_ai', x: UC00_TARGETS_X + 390, y: colY + 330, width: 160, height: 180, iconPath: '/assets/svg/business/analytics-application.svg', iconX: UC00_TARGETS_X + 390 + 48, iconY: colY + 388, iconWidth: 64, iconHeight: 64, labelKey: 'uc00.target.analytics_ai', labelY: colY + 502 },
        ],
        noteKey: 'uc00.targets.note',
        noteX: UC00_TARGETS_X + 40,
        noteY: colY + 525,
        outcomes: [
          { id: 'traceability', x: UC00_TARGETS_X + 40, y: colY + 590, width: 520, height: 70, textKey: 'uc00.outcome.traceability' },
          { id: 'kpi', x: UC00_TARGETS_X + 40, y: colY + 680, width: 520, height: 80, textKey: 'uc00.outcome.kpi', multiline: true, textLines: ['uc00.outcome.kpi.line1', 'uc00.outcome.kpi.line2'] },
          { id: 'closed_loop', x: UC00_TARGETS_X + 40, y: colY + 780, width: 520, height: 70, textKey: 'uc00.outcome.closed_loop' },
        ],
      },
    },
    footer: { x: 960, y: UC00_VIEWBOX.height - 30, key: 'uc00.footer' },
  };
  
  calculateLaneLayout(structure.columns.sources);
  return structure;
}
