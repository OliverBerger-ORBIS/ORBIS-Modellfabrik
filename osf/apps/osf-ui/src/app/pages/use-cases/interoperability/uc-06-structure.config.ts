/**
 * UC-06 Interoperability: Event-to-Process Map - Structure Configuration
 * 
 * Hierarchische Struktur:
 * 1. Columns (3 Columns: Sources, DSP, Targets)
 * 2. Lanes innerhalb der Columns (mit Überschrift, Icon, Höhe aus Inhalt, gleichmäßige Spacing-Verteilung)
 * 3. Chips innerhalb der Lanes
 * 
 * Alle Texte verwenden I18n-Keys, die zur Laufzeit ersetzt werden.
 */

export interface Uc06Chip {
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

export interface Uc06Lane {
  id: string;
  titleKey: string;
  iconPath: string;
  iconX: number;
  iconY: number;
  iconWidth: number;
  iconHeight: number;
  chips: Uc06Chip[];
  // Calculated properties (will be set by layout calculator)
  x?: number;
  y?: number;
  width?: number;
  height?: number;
}

export interface Uc06Column {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  headerKey: string;
  headerX: number;
  headerY: number;
  lanes: Uc06Lane[];
  // Calculated spacing between lanes
  laneSpacing?: number;
}

export interface Uc06Step {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  descriptionKey: string;
}

export interface Uc06Bar {
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

export interface Uc06TimelinePoint {
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

export interface Uc06Target {
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

export interface Uc06Outcome {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  textKey: string;
  multiline?: boolean;
  textLines?: string[];
}

export interface Uc06Structure {
  // Dimensions
  viewBox: { width: number; height: number };
  
  // Title and subtitle
  title: { x: number; y: number; key: string };
  subtitle: { x: number; y: number; key: string };
  
  // Columns (hierarchical structure)
  columns: {
    sources: Uc06Column;
    dsp: {
      column: Omit<Uc06Column, 'lanes'>;
      steps: Uc06Step[];
      arrows: Array<{ x1: number; y1: number; x2: number; y2: number }>;
      bars: Uc06Bar[];
    };
    targets: {
      column: Omit<Uc06Column, 'lanes'>;
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
          points: Uc06TimelinePoint[];
        };
      };
      targets: Uc06Target[];
      noteKey: string;
      noteX: number;
      noteY: number;
      outcomes: Uc06Outcome[];
    };
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
function calculateLaneLayout(column: Uc06Column): void {
  const headerHeight = 50; // Space for header
  const startY = column.y + headerHeight;
  const availableHeight = column.height - headerHeight;
  
  // Calculate lane heights from chips (chips have absolute y positions in original structure)
  // We need to find the maximum y + height for each lane's chips
  const laneHeights: number[] = [];
  column.lanes.forEach((lane, laneIndex) => {
    // Find the base y position for this lane (minimum y of first chip in original structure)
    const baseChipY = Math.min(...lane.chips.map(c => c.y));
    
    // Calculate lane height from chips
    const maxChipBottom = Math.max(...lane.chips.map(c => c.y + c.height), baseChipY);
    const laneHeight = maxChipBottom - baseChipY + 80; // Add padding (increased from 40 to 80 to accommodate title)
    laneHeights.push(laneHeight);
    lane.height = laneHeight;
  });
  
  // Calculate total height
  const totalLaneHeight = laneHeights.reduce((sum, h) => sum + h, 0);
  
  // Calculate spacing
  const nLanes = column.lanes.length;
  const nGaps = nLanes + 1; // Before first, between, after last
  const totalGapSpace = availableHeight - totalLaneHeight;
  const gapSize = totalGapSpace / nGaps;
  column.laneSpacing = gapSize;
  
    // Position lanes and adjust chip positions to be relative to lane
    let currentY = startY + gapSize;
    column.lanes.forEach((lane, laneIndex) => {
      lane.x = column.x + 30; // Padding from column edge
      lane.y = currentY;
      lane.width = column.width - 60; // Padding on both sides
      
      // Ensure height is set
      if (!lane.height) {
        lane.height = laneHeights[laneIndex];
      }
      
      // Adjust chip positions to be relative to lane
      // Find the base y position (minimum y of chips in original structure)
      const baseChipY = Math.min(...lane.chips.map(c => c.y));
      // Increased padding to prevent title from being covered by chips, plus 10px shift down
      const offsetY = currentY - baseChipY + 60; // Offset to move chips to lane position (50 + 10px shift down)
      
      // Adjust each chip's y position to be relative to lane
      lane.chips.forEach((chip) => {
        chip.y = chip.y + offsetY;
        // Adjust chip icon positions if they exist
        if (chip.iconY !== undefined) {
          chip.iconY = chip.iconY + offsetY;
        }
        // Operation icons use relative offsets (offsetX, offsetY), so no adjustment needed
        // The offsets are relative to text position, which is already adjusted above
      });
      
      // Adjust lane icon position (iconX stays same, iconY adjusted)
      const baseIconY = lane.iconY;
      lane.iconY = baseIconY + offsetY;
      
      currentY += lane.height + gapSize;
    });
}

/**
 * Creates the UC-06 structure configuration with all positions and I18n keys
 */
export function createUc06Structure(): Uc06Structure {
  const structure: Uc06Structure = {
    viewBox: { width: 1920, height: 1300 },
    
    title: { x: 960, y: 110, key: 'uc06.title' },
    subtitle: { x: 960, y: 155, key: 'uc06.subtitle' },
    
    columns: {
      sources: {
        id: 'sources',
        x: 80,
        y: 220,
        width: 560,
        height: 950,
        headerX: 120,
        headerY: 270,
        headerKey: 'uc06.sources.header',
        lanes: [
          {
            id: 'business_context',
            titleKey: 'uc06.lane.business_context.title',
            iconPath: '/assets/svg/business/erp-application.svg',
            iconX: 520,
            iconY: 318,
            iconWidth: 70,
            iconHeight: 70,
            chips: [
              // Chips have relative positions: x relative to column, y relative to lane start (will be adjusted in calculateLaneLayout)
              { id: 'production_order', x: 160, y: 340, width: 150, height: 50, textKey: 'uc06.chip.production_order', multiline: true, textLines: ['uc06.chip.production_order.line1', 'uc06.chip.production_order.line2'], iconPath: '/assets/svg/ui/heading-production.svg', iconX: 280, iconY: 350, iconWidth: 20, iconHeight: 20 },
              { id: 'storage_order', x: 330, y: 340, width: 150, height: 50, textKey: 'uc06.chip.storage_order', multiline: true, textLines: ['uc06.chip.storage_order.line1', 'uc06.chip.storage_order.line2'], iconPath: '/assets/svg/shopfloor/shared/order-tracking.svg', iconX: 450, iconY: 350, iconWidth: 20, iconHeight: 20 },
              { id: 'material', x: 160, y: 400, width: 150, height: 30, textKey: 'uc06.chip.material', iconPath: '/assets/svg/ui/heading-customer-orders.svg', iconX: 280, iconY: 405, iconWidth: 20, iconHeight: 20 },
              { id: 'customer', x: 330, y: 400, width: 150, height: 30, textKey: 'uc06.chip.customer', iconPath: '/assets/svg/shopfloor/shared/customer.svg', iconX: 450, iconY: 405, iconWidth: 20, iconHeight: 20 },
              { id: 'routing', x: 160, y: 440, width: 150, height: 30, textKey: 'uc06.chip.routing', iconPath: '/assets/svg/dsp/extra/process.svg', iconX: 280, iconY: 445, iconWidth: 20, iconHeight: 20 },
              { id: 'operation', x: 330, y: 440, width: 150, height: 30, textKey: 'uc06.chip.operation', iconPath: '/assets/svg/shopfloor/systems/bp-system.svg', iconX: 450, iconY: 445, iconWidth: 20, iconHeight: 20 },
            ],
          },
          {
            id: 'machine_station',
            titleKey: 'uc06.lane.machine_station.title',
            iconPath: '/assets/svg/shopfloor/stations/drill-station.svg',
            iconX: 520,
            iconY: 533,
            iconWidth: 70,
            iconHeight: 70,
            chips: [
              { id: 'operation_chip', x: 160, y: 560, width: 150, height: 70, textKey: 'uc06.chip.operation_label', multiline: true, textLines: ['uc06.chip.operation_label', 'uc06.chip.start', 'uc06.chip.stop'], operationIcons: [
                { lineIndex: 1, iconPath: '/assets/svg/shopfloor/shared/driving-status.svg', offsetX: 15, offsetY: 10, iconWidth: 16, iconHeight: 16 },
                { lineIndex: 2, iconPath: '/assets/svg/shopfloor/shared/stopped-status.svg', offsetX: 20, offsetY: 10, iconWidth: 16, iconHeight: 16 },
              ]},
              { id: 'state_chip', x: 330, y: 560, width: 150, height: 110, textKey: 'uc06.chip.state_label', multiline: false, statusDots: [
                { cx: 370, cy: 600, color: 'running' },
                { cx: 370, cy: 625, color: 'idle' },
                { cx: 370, cy: 650, color: 'fail' },
              ], statusLabels: ['uc06.chip.running', 'uc06.chip.idle', 'uc06.chip.fail']},
            ],
          },
          {
            id: 'agv_system',
            titleKey: 'uc06.lane.agv_system.title',
            iconPath: '/assets/svg/shopfloor/shared/agv-vehicle.svg',
            iconX: 520,
            iconY: 718,
            iconWidth: 70,
            iconHeight: 70,
            chips: [
              { id: 'pick', x: 160, y: 740, width: 150, height: 30, textKey: 'uc06.chip.pick', iconPath: '/assets/svg/shopfloor/shared/pick-event.svg', iconX: 280, iconY: 745, iconWidth: 20, iconHeight: 20 },
              { id: 'transfer', x: 330, y: 740, width: 150, height: 30, textKey: 'uc06.chip.transfer', iconPath: '/assets/svg/shopfloor/shared/pass-event.svg', iconX: 450, iconY: 745, iconWidth: 20, iconHeight: 20 },
              { id: 'drop', x: 160, y: 780, width: 150, height: 30, textKey: 'uc06.chip.drop', iconPath: '/assets/svg/shopfloor/shared/drop-event.svg', iconX: 280, iconY: 785, iconWidth: 20, iconHeight: 20 },
              { id: 'route', x: 330, y: 780, width: 150, height: 30, textKey: 'uc06.chip.route', iconPath: '/assets/svg/ui/heading-route.svg', iconX: 450, iconY: 785, iconWidth: 20, iconHeight: 20 },
            ],
          },
          {
            id: 'quality_aiqs',
            titleKey: 'uc06.lane.quality_aiqs.title',
            iconPath: '/assets/svg/shopfloor/stations/aiqs-station.svg',
            iconX: 520,
            iconY: 873,
            iconWidth: 70,
            iconHeight: 70,
            chips: [
              { id: 'check_quality_label', x: 170, y: 910, width: 0, height: 0, textKey: 'uc06.chip.check_quality' },
              { id: 'pass', x: 330, y: 900, width: 60, height: 24, textKey: 'uc06.chip.pass', fill: '#e8f5e9', stroke: '#4caf50' },
              { id: 'fail', x: 330, y: 930, width: 60, height: 24, textKey: 'uc06.chip.fail', fill: '#ffebee', stroke: '#f44336' },
            ],
          },
          {
            id: 'environment_sensors',
            titleKey: 'uc06.lane.environment_sensors.title',
            iconPath: '/assets/svg/ui/heading-sensors.svg',
            iconX: 520,
            iconY: 1008,
            iconWidth: 70,
            iconHeight: 70,
            chips: [
              { id: 'temperature', x: 160, y: 1040, width: 150, height: 30, textKey: 'uc06.chip.temperature', iconPath: '/assets/svg/shopfloor/shared/temperature-sensor.svg', iconX: 280, iconY: 1045, iconWidth: 20, iconHeight: 20 },
              { id: 'energy', x: 330, y: 1040, width: 150, height: 30, textKey: 'uc06.chip.energy', iconPath: '/assets/svg/shopfloor/shared/battery.svg', iconX: 450, iconY: 1045, iconWidth: 20, iconHeight: 20 },
              { id: 'vibration', x: 160, y: 1080, width: 150, height: 30, textKey: 'uc06.chip.vibration', iconPath: '/assets/svg/shopfloor/shared/vibration-sensor.svg', iconX: 280, iconY: 1085, iconWidth: 20, iconHeight: 20 },
              { id: 'pressure', x: 330, y: 1080, width: 150, height: 30, textKey: 'uc06.chip.pressure', iconPath: '/assets/svg/shopfloor/shared/pressure-sensor.svg', iconX: 450, iconY: 1085, iconWidth: 20, iconHeight: 20 },
            ],
          },
        ],
      },
      dsp: {
        column: {
          id: 'dsp',
          x: 680,
          y: 220,
          width: 560,
          height: 950,
          headerX: 720,
          headerY: 270,
          headerKey: 'uc06.dsp.header',
        },
        steps: [
          {
            id: 'normalize',
            x: 720,
            y: 320,
            width: 480,
            height: 130,
            titleKey: 'uc06.step.normalize.title',
            descriptionKey: 'uc06.step.normalize.description',
          },
          {
            id: 'enrich',
            x: 720,
            y: 490,
            width: 480,
            height: 130,
            titleKey: 'uc06.step.enrich.title',
            descriptionKey: 'uc06.step.enrich.description',
          },
          {
            id: 'correlate',
            x: 720,
            y: 660,
            width: 480,
            height: 130,
            titleKey: 'uc06.step.correlate.title',
            descriptionKey: 'uc06.step.correlate.description',
          },
        ],
        arrows: [
          { x1: 960, y1: 450, x2: 960, y2: 480 },
          { x1: 960, y1: 620, x2: 960, y2: 650 },
        ],
        bars: [
          {
            id: 'process_ready',
            x: 760,
            y: 830,
            width: 400,
            height: 56,
            textKey: 'uc06.bar.process_ready',
            fill: '#eaf5ea',
            stroke: '#bfe3bf',
          },
          {
            id: 'reusable',
            x: 760,
            y: 920,
            width: 400,
            height: 56,
            textKey: 'uc06.bar.reusable',
          },
          {
            id: 'foundation',
            x: 760,
            y: 1010,
            width: 400,
            height: 70,
            textKey: 'uc06.bar.foundation',
            multiline: true,
            textLines: ['uc06.bar.foundation.line1', 'uc06.bar.foundation.line2'],
          },
        ],
      },
      targets: {
        column: {
          id: 'targets',
          x: 1280,
          y: 220,
          width: 560,
          height: 950,
          headerX: 1320,
          headerY: 270,
          headerKey: 'uc06.targets.header',
        },
        processViewBox: {
          x: 1320,
          y: 310,
          width: 480,
          height: 200,
          titleKey: 'uc06.process_view.title',
          timeline: {
            lineX1: 1350,
            lineY: 420,
            lineX2: 1770,
            points: [
              { x: 1365, y: 420, iconPath: '/assets/svg/shopfloor/stations/hbw-station.svg', iconX: 1347.5, iconY: 365, iconWidth: 35, iconHeight: 35, labelKey: 'uc06.timeline.warehouse', labelY: 460 },
              { x: 1443, y: 420, iconPath: '/assets/svg/shopfloor/shared/agv-vehicle.svg', iconX: 1425.5, iconY: 365, iconWidth: 35, iconHeight: 35, labelKey: 'uc06.timeline.agv', labelY: 460 },
              { x: 1521, y: 420, iconPath: '/assets/svg/shopfloor/stations/drill-station.svg', iconX: 1503.5, iconY: 365, iconWidth: 35, iconHeight: 35, labelKey: 'uc06.timeline.station', labelY: 460 },
              { x: 1599, y: 420, iconPath: '/assets/svg/shopfloor/shared/pass-event.svg', iconX: 1581.5, iconY: 365, iconWidth: 35, iconHeight: 35, labelKey: 'uc06.timeline.transfer', labelY: 460 },
              { x: 1677, y: 420, iconPath: '/assets/svg/shopfloor/stations/aiqs-station.svg', iconX: 1659.5, iconY: 365, iconWidth: 35, iconHeight: 35, labelKey: 'uc06.timeline.quality', labelY: 460 },
              { x: 1755, y: 420, iconPath: '/assets/svg/shopfloor/shared/order-tracking.svg', iconX: 1737.5, iconY: 365, iconWidth: 35, iconHeight: 35, labelKey: 'uc06.timeline.complete', labelY: 460 },
            ],
          },
        },
        targets: [
          {
            id: 'erp',
            x: 1320,
            y: 540,
            width: 150,
            height: 90,
            iconPath: '/assets/svg/business/erp-application.svg',
            iconX: 1365,
            iconY: 555,
            iconWidth: 70,
            iconHeight: 50,
            labelKey: 'uc06.target.erp',
            labelY: 625,
          },
          {
            id: 'mes',
            x: 1495,
            y: 540,
            width: 150,
            height: 90,
            iconPath: '/assets/svg/business/mes-application.svg',
            iconX: 1540,
            iconY: 555,
            iconWidth: 70,
            iconHeight: 50,
            labelKey: 'uc06.target.mes',
            labelY: 625,
          },
          {
            id: 'analytics_ai',
            x: 1670,
            y: 540,
            width: 150,
            height: 90,
            iconPath: '/assets/svg/business/analytics-application.svg',
            iconX: 1715,
            iconY: 555,
            iconWidth: 70,
            iconHeight: 50,
            labelKey: 'uc06.target.analytics_ai',
            labelY: 625,
          },
        ],
        noteKey: 'uc06.targets.note',
        noteX: 1320,
        noteY: 650,
        outcomes: [
          {
            id: 'traceability',
            x: 1320,
            y: 750,
            width: 480,
            height: 70,
            textKey: 'uc06.outcome.traceability',
          },
          {
            id: 'kpi',
            x: 1320,
            y: 840,
            width: 480,
            height: 80,
            textKey: 'uc06.outcome.kpi',
            multiline: true,
            textLines: ['uc06.outcome.kpi.line1', 'uc06.outcome.kpi.line2'],
          },
          {
            id: 'closed_loop',
            x: 1320,
            y: 940,
            width: 480,
            height: 70,
            textKey: 'uc06.outcome.closed_loop',
          },
        ],
      },
    },
    
    footer: {
      x: 960,
      y: 1250,
      key: 'uc06.footer',
    },
  };
  
  // Calculate lane layouts
  calculateLaneLayout(structure.columns.sources);
  
  return structure;
}
