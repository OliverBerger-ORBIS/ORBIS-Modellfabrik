/**
 * UC-01 Track & Trace Genealogy - Structure Configuration
 * 
 * Hierarchische Struktur:
 * 1. Columns (4 Columns: Business Events, Production Plan, Actual Path, Correlated Timeline)
 * 2. Lanes innerhalb der Columns (mit Überschrift, Icon, Höhe aus Inhalt, gleichmäßige Spacing-Verteilung)
 * 3. Chips/Elements innerhalb der Lanes
 * 
 * Alle Texte verwenden I18n-Keys, die zur Laufzeit ersetzt werden.
 */

export interface Uc01Chip {
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
  // Timeline synchronization
  timeIndex?: number; // Index in the global timeline (0, 1, 2, ...)
}

export interface Uc01Lane {
  id: string;
  titleKey: string;
  iconPath?: string;
  iconX?: number;
  iconY?: number;
  iconWidth?: number;
  iconHeight?: number;
  chips: Uc01Chip[];
  // Calculated properties (will be set by layout calculator)
  x?: number;
  y?: number;
  width?: number;
  height?: number;
}

export interface Uc01Column {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  headerKey: string;
  headerX: number;
  headerY: number;
  lanes: Uc01Lane[];
  // Calculated spacing between lanes
  laneSpacing?: number;
}

export interface Uc01TimelinePoint {
  x: number;
  y: number;
  number: number; // Timeline number (1, 2, 3, ...)
  iconPath?: string;
  iconX?: number;
  iconY?: number;
  iconWidth?: number;
  iconHeight?: number;
  labelKey: string;
  labelY: number;
  timestampKey?: string; // Optional timestamp I18n key
}

export interface Uc01Connection {
  id: string;
  fromId: string; // ID of source element
  toId: string; // ID of target element
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
  dashed?: boolean; // Use dashed line
}

/**
 * Timeline definition for synchronizing events across columns
 * Each time point represents a moment in the process flow
 */
export interface Uc01Timeline {
  timePoints: Uc01TimePoint[];
  timeStep: number; // Vertical spacing between time points (in pixels)
  baseY: number; // Base Y coordinate for the first time point
}

export interface Uc01TimePoint {
  index: number; // 0, 1, 2, ... (chronological order)
  label?: string; // Optional label for debugging
  // Events that occur at this time point (across all columns)
  events: {
    column: 'businessEvents' | 'productionPlan' | 'actualPath' | 'correlatedTimeline';
    laneId: string;
    chipId: string;
  }[];
}

export interface Uc01Structure {
  // Dimensions
  viewBox: { width: number; height: number };
  
  // Title and subtitle
  title: { x: number; y: number; key: string };
  subtitle: { x: number; y: number; key: string };
  stepDescription: { x: number; y: number; width: number; height: number };
  
  // Columns (hierarchical structure)
  // All columns use Lanes as primary structure element
  // Timelines are represented vertically (top to bottom) within lanes - better for landscape format with 4 columns
  columns: {
    businessEvents: Uc01Column;
    productionPlan: Uc01Column; // Uses lanes with vertical timeline (top to bottom)
    actualPath: Uc01Column; // Uses lanes with vertical timeline (top to bottom)
    correlatedTimeline: Uc01Column; // Uses lanes (NFC-Tag, Timeline, Order Context) with vertical timeline
  };
  
  // Connections between columns (dashed lines)
  connections: Uc01Connection[];
}

/**
 * Calculates lane positions and spacing within a column
 * Ensures equal spacing between lanes
 */
function calculateLaneLayout(column: Uc01Column): void {
  const headerHeight = 50;
  const startY = column.y + headerHeight;
  const availableHeight = column.height - headerHeight;
  
  // Calculate lane heights from chips
  const laneHeights: number[] = [];
  column.lanes.forEach((lane) => {
    const baseChipY = Math.min(...lane.chips.map(c => c.y));
    const maxChipBottom = Math.max(...lane.chips.map(c => c.y + c.height), baseChipY);
    const laneHeight = maxChipBottom - baseChipY + 80; // Add padding
    laneHeights.push(laneHeight);
    lane.height = laneHeight;
  });
  
  // Calculate total height
  const totalLaneHeight = laneHeights.reduce((sum, h) => sum + h, 0);
  
  // Calculate spacing
  const nLanes = column.lanes.length;
  const nGaps = nLanes + 1;
  const totalGapSpace = availableHeight - totalLaneHeight;
  const gapSize = totalGapSpace / nGaps;
  column.laneSpacing = gapSize;
  
  // Position lanes and adjust chip positions
  let currentY = startY + gapSize;
  column.lanes.forEach((lane, laneIndex) => {
    lane.x = column.x + 30;
    lane.y = currentY;
    lane.width = column.width - 60;
    
    if (!lane.height) {
      lane.height = laneHeights[laneIndex];
    }
    
    // Adjust chip positions to be relative to lane
    // If chips have timeIndex (timeline-synchronized), preserve their absolute Y coordinates
    const hasTimelineSync = lane.chips.some(c => c.timeIndex !== undefined);
    let offsetY: number | undefined;
    
    if (hasTimelineSync) {
      // For timeline-synchronized lanes, Y coordinates are absolute (from timeline)
      // Don't adjust Y coordinates, they are already synchronized across columns
      // Only ensure lane position encompasses all chips
      const minChipY = Math.min(...lane.chips.map(c => c.y));
      const maxChipY = Math.max(...lane.chips.map(c => c.y + c.height));
      
      // Adjust lane Y to start at the first chip (with some padding)
      lane.y = Math.min(lane.y, minChipY - 60);
      lane.height = Math.max(lane.height, maxChipY - lane.y + 80);
    } else {
      // For non-timeline lanes, use original behavior (relative positioning)
      const baseChipY = Math.min(...lane.chips.map(c => c.y));
      offsetY = currentY - baseChipY + 60;
      
      lane.chips.forEach((chip) => {
        chip.y = chip.y + offsetY!;
        if (chip.iconY !== undefined) {
          chip.iconY = chip.iconY + offsetY!;
        }
      });
    }
    
    // Adjust lane icon position (only if offsetY was calculated)
    if (lane.iconY !== undefined && offsetY !== undefined) {
      lane.iconY = lane.iconY + offsetY;
    }
    
    currentY += lane.height + gapSize;
  });
}

/**
 * Creates the global timeline definition
 * This timeline synchronizes events across all columns
 * Y coordinates are calculated to fit within column boundaries
 */
function createTimeline(columnY: number, columnHeight: number, headerHeight: number = 50): Uc01Timeline {
  // Calculate available height for timeline (within column bounds)
  const paddingTop = 60;
  const paddingBottom = 40;
  const availableHeight = columnHeight - headerHeight - paddingTop - paddingBottom;
  
  // baseY will be set after we know the number of time points
  let baseY = columnY + headerHeight + paddingTop;
  
  // Define time points in chronological order
  // Each time point contains events that occur simultaneously across columns
  const timePoints: Uc01TimePoint[] = [
    {
      index: 0,
      label: 'Purchase Order Created',
      events: [
        { column: 'businessEvents', laneId: 'purchase-order', chipId: 'purchase-order-chip' },
      ],
    },
    {
      index: 1,
      label: 'Storage Order: Goods Receipt (DPS)',
      events: [
        { column: 'productionPlan', laneId: 'storage-order', chipId: 'storage-plan-dps' },
      ],
    },
    {
      index: 2,
      label: 'Storage Order: NFC Read',
      events: [
        { column: 'productionPlan', laneId: 'storage-order', chipId: 'storage-plan-nfc' },
      ],
    },
    {
      index: 3,
      label: 'Storage Order: Order Created',
      events: [
        { column: 'productionPlan', laneId: 'storage-order', chipId: 'storage-plan-order' },
      ],
    },
    {
      index: 4,
      label: 'Storage Order: Transport to Warehouse',
      events: [
        { column: 'productionPlan', laneId: 'storage-order', chipId: 'storage-plan-transport' },
        { column: 'correlatedTimeline', laneId: 'event-timeline', chipId: 'timeline-1' }, // START TRANSFER
      ],
    },
    {
      index: 5,
      label: 'Storage Order: Warehouse Storage',
      events: [
        { column: 'productionPlan', laneId: 'storage-order', chipId: 'storage-plan-warehouse' },
        { column: 'actualPath', laneId: 'fts-route', chipId: 'actual-warehouse' },
        { column: 'correlatedTimeline', laneId: 'event-timeline', chipId: 'timeline-2' }, // WAREHOUSE MOVE
      ],
    },
    {
      index: 6,
      label: 'Customer Order Created',
      events: [
        { column: 'businessEvents', laneId: 'customer-order', chipId: 'customer-order-id' },
      ],
    },
    {
      index: 7,
      label: 'Production Order: Warehouse',
      events: [
        { column: 'productionPlan', laneId: 'production-order', chipId: 'production-plan-warehouse' },
      ],
    },
    {
      index: 8,
      label: 'Production Order: Drill - PICK',
      events: [
        { column: 'productionPlan', laneId: 'production-order', chipId: 'production-plan-drill' },
        { column: 'actualPath', laneId: 'fts-route', chipId: 'actual-drill' },
        { column: 'correlatedTimeline', laneId: 'event-timeline', chipId: 'timeline-3' }, // DRILL PICK
      ],
    },
    {
      index: 9,
      label: 'Production Order: Drill - PROCESS',
      events: [
        { column: 'correlatedTimeline', laneId: 'event-timeline', chipId: 'timeline-4' }, // DRILL PROCESS
      ],
    },
    {
      index: 10,
      label: 'Production Order: Drill - DROP',
      events: [
        { column: 'correlatedTimeline', laneId: 'event-timeline', chipId: 'timeline-5' }, // DRILL DROP
      ],
    },
    {
      index: 11,
      label: 'Production Order: Quality - PICK',
      events: [
        { column: 'productionPlan', laneId: 'production-order', chipId: 'production-plan-quality' },
        { column: 'actualPath', laneId: 'fts-route', chipId: 'actual-quality' },
        { column: 'correlatedTimeline', laneId: 'event-timeline', chipId: 'timeline-6' }, // QUALITY PICK
      ],
    },
    {
      index: 12,
      label: 'Production Order: Quality - PROCESS',
      events: [
        { column: 'correlatedTimeline', laneId: 'event-timeline', chipId: 'timeline-7' }, // QUALITY PROCESS
      ],
    },
    {
      index: 13,
      label: 'Production Order: Quality - DROP',
      events: [
        { column: 'correlatedTimeline', laneId: 'event-timeline', chipId: 'timeline-8' }, // QUALITY DROP
      ],
    },
    {
      index: 14,
      label: 'Production Order: DPS',
      events: [
        { column: 'productionPlan', laneId: 'production-order', chipId: 'production-plan-dps' },
        { column: 'actualPath', laneId: 'fts-route', chipId: 'actual-dps' },
      ],
    },
  ];
  
  // Calculate timeStep to fit all time points within available height
  const numTimePoints = timePoints.length;
  const numGaps = Math.max(1, numTimePoints - 1); // Number of gaps between time points
  const timeStep = availableHeight / numGaps; // Distribute available height evenly
  
  return {
    timePoints,
    timeStep,
    baseY,
  };
}

/**
 * Applies timeline synchronization to structure
 * Sets timeIndex on chips and calculates Y coordinates based on timeline
 */
function applyTimelineSync(structure: Uc01Structure, timeline: Uc01Timeline): void {
  // First pass: Set timeIndex on chips based on timeline
  timeline.timePoints.forEach((timePoint) => {
    timePoint.events.forEach((event) => {
      const column = structure.columns[event.column];
      const lane = column.lanes.find((l) => l.id === event.laneId);
      if (lane) {
        const chip = lane.chips.find((c) => c.id === event.chipId);
        if (chip) {
          chip.timeIndex = timePoint.index;
        }
      }
    });
  });
  
  // Second pass: Calculate Y coordinates based on timeIndex
  Object.values(structure.columns).forEach((column) => {
    column.lanes.forEach((lane) => {
      lane.chips.forEach((chip) => {
        if (chip.timeIndex !== undefined) {
          // Calculate Y coordinate based on timeline
          const newY = timeline.baseY + (chip.timeIndex * timeline.timeStep);
          
          // Preserve relative icon offset
          if (chip.iconY !== undefined) {
            const iconOffset = chip.iconY - chip.y;
            chip.y = newY;
            chip.iconY = newY + iconOffset;
          } else {
            chip.y = newY;
          }
        }
      });
    });
  });
}

/**
 * Creates the UC-01 structure configuration
 */
export function createUc01Structure(): Uc01Structure {
  const structure: Uc01Structure = {
    viewBox: { width: 1920, height: 1300 },
    
    title: { x: 960, y: 110, key: 'uc01.title' },
    subtitle: { x: 960, y: 155, key: 'uc01.subtitle' },
    stepDescription: { x: 960, y: 155, width: 1400, height: 100 },
    
    columns: {
      businessEvents: {
        id: 'business-events',
        x: 80,
        y: 300,
        width: 400,
        height: 900,
        headerX: 120,
        headerY: 350,
        headerKey: 'uc01.column.business_events',
        lanes: [
          {
            id: 'purchase-order',
            titleKey: 'uc01.lane.purchase_order',
            iconPath: '/assets/svg/shopfloor/shared/customer.svg', // TODO: Use purchase order icon if available
            iconX: 420,
            iconY: 380,
            iconWidth: 50,
            iconHeight: 50,
            chips: [
              { id: 'purchase-order-chip', x: 120, y: 400, width: 300, height: 50, textKey: 'uc01.chip.purchase_order', multiline: true, textLines: ['uc01.chip.purchase_order.line1', 'uc01.chip.purchase_order.line2'] },
              { id: 'purchase-order-id', x: 120, y: 460, width: 300, height: 40, textKey: 'uc01.chip.purchase_order_id' },
              { id: 'supplier-id', x: 120, y: 510, width: 300, height: 40, textKey: 'uc01.chip.supplier_id' },
              { id: 'material-batch', x: 120, y: 560, width: 300, height: 40, textKey: 'uc01.chip.material_batch' },
              { id: 'erp-id-purchase', x: 120, y: 610, width: 300, height: 40, textKey: 'uc01.chip.erp_id' },
            ],
          },
          {
            id: 'customer-order',
            titleKey: 'uc01.lane.customer_order',
            iconPath: '/assets/svg/shopfloor/shared/customer.svg',
            iconX: 420,
            iconY: 880,
            iconWidth: 50,
            iconHeight: 50,
            chips: [
              { id: 'customer-order-id', x: 120, y: 900, width: 300, height: 40, textKey: 'uc01.chip.customer_order_id' },
              { id: 'customer-id', x: 120, y: 950, width: 300, height: 40, textKey: 'uc01.chip.customer_id' },
              { id: 'production-order-id', x: 120, y: 1000, width: 300, height: 40, textKey: 'uc01.chip.production_order_id' },
              { id: 'erp-id-customer', x: 120, y: 1050, width: 300, height: 40, textKey: 'uc01.chip.erp_id' },
            ],
          },
        ],
      },
      productionPlan: {
        id: 'production-plan',
        x: 520,
        y: 300,
        width: 400,
        height: 900,
        headerX: 560,
        headerY: 350,
        headerKey: 'uc01.column.production_plan',
        lanes: [
          {
            id: 'storage-order',
            titleKey: 'uc01.lane.storage_order',
            iconPath: '/assets/svg/shopfloor/stations/hbw-station.svg',
            iconX: 870,
            iconY: 380,
            iconWidth: 50,
            iconHeight: 50,
            // Timeline points as chips (vertical, top to bottom)
            // Storage Order Flow: DPS (Wareneingang) → NFC-Tag/Farbe → Storage Order → Transport DPS→Lager → Einlagerung
            chips: [
              { id: 'storage-plan-dps', x: 650, y: 420, width: 200, height: 80, textKey: 'uc01.plan.goods_receipt', iconPath: '/assets/svg/shopfloor/stations/dps-station.svg', iconX: 720, iconY: 440, iconWidth: 40, iconHeight: 40 },
              { id: 'storage-plan-nfc', x: 650, y: 520, width: 200, height: 80, textKey: 'uc01.plan.nfc_read', iconPath: '/assets/svg/shopfloor/shared/nfc-tag.svg', iconX: 720, iconY: 540, iconWidth: 40, iconHeight: 40 },
              { id: 'storage-plan-order', x: 650, y: 620, width: 200, height: 80, textKey: 'uc01.plan.storage_order', iconPath: '/assets/svg/ui/process-flow.svg', iconX: 720, iconY: 640, iconWidth: 40, iconHeight: 40 },
              { id: 'storage-plan-transport', x: 650, y: 720, width: 200, height: 80, textKey: 'uc01.plan.transport', iconPath: '/assets/svg/shopfloor/shared/agv-vehicle.svg', iconX: 720, iconY: 740, iconWidth: 40, iconHeight: 40 },
              { id: 'storage-plan-warehouse', x: 650, y: 820, width: 200, height: 80, textKey: 'uc01.plan.warehouse', iconPath: '/assets/svg/shopfloor/stations/hbw-station.svg', iconX: 720, iconY: 840, iconWidth: 40, iconHeight: 40 },
            ],
          },
          {
            id: 'production-order',
            titleKey: 'uc01.lane.production_order',
            iconPath: '/assets/svg/ui/process-flow.svg',
            iconX: 870,
            iconY: 880,
            iconWidth: 50,
            iconHeight: 50,
            // Timeline points as chips (vertical, top to bottom)
            chips: [
              { id: 'production-plan-warehouse', x: 650, y: 920, width: 200, height: 80, textKey: 'uc01.plan.warehouse', iconPath: '/assets/svg/shopfloor/stations/hbw-station.svg', iconX: 720, iconY: 940, iconWidth: 40, iconHeight: 40 },
              { id: 'production-plan-drill', x: 650, y: 1020, width: 200, height: 80, textKey: 'uc01.plan.drill', iconPath: '/assets/svg/shopfloor/stations/drill-station.svg', iconX: 720, iconY: 1040, iconWidth: 40, iconHeight: 40 },
              { id: 'production-plan-quality', x: 650, y: 1120, width: 200, height: 80, textKey: 'uc01.plan.quality', iconPath: '/assets/svg/shopfloor/stations/aiqs-station.svg', iconX: 720, iconY: 1140, iconWidth: 40, iconHeight: 40 },
              { id: 'production-plan-dps', x: 650, y: 1220, width: 200, height: 80, textKey: 'uc01.plan.dps', iconPath: '/assets/svg/shopfloor/stations/dps-station.svg', iconX: 720, iconY: 1240, iconWidth: 40, iconHeight: 40 },
            ],
          },
        ],
      },
      actualPath: {
        id: 'actual-path',
        x: 960,
        y: 300,
        width: 400,
        height: 900,
        headerX: 1000,
        headerY: 350,
        headerKey: 'uc01.column.actual_path',
        lanes: [
          {
            id: 'fts-route',
            titleKey: 'uc01.lane.fts_route',
            iconPath: '/assets/svg/shopfloor/shared/agv-vehicle.svg',
            iconX: 1310,
            iconY: 380,
            iconWidth: 50,
            iconHeight: 50,
            // Actual Path: FTS transparent (no station), stations with PICK/Process/DROP, MILL without events
            // Events are only shown in Column 4 (Correlated Timeline)
            chips: [
              { id: 'actual-warehouse', x: 1090, y: 420, width: 200, height: 80, textKey: 'uc01.actual.warehouse', iconPath: '/assets/svg/shopfloor/stations/hbw-station.svg', iconX: 1160, iconY: 440, iconWidth: 40, iconHeight: 40 },
              { id: 'actual-drill', x: 1090, y: 520, width: 200, height: 80, textKey: 'uc01.actual.drill', iconPath: '/assets/svg/shopfloor/stations/drill-station.svg', iconX: 1160, iconY: 540, iconWidth: 40, iconHeight: 40 },
              { id: 'actual-mill', x: 1090, y: 620, width: 200, height: 80, textKey: 'uc01.actual.mill', iconPath: '/assets/svg/shopfloor/stations/mill-station.svg', iconX: 1160, iconY: 640, iconWidth: 40, iconHeight: 40 },
              { id: 'actual-quality', x: 1090, y: 720, width: 200, height: 80, textKey: 'uc01.actual.quality', iconPath: '/assets/svg/shopfloor/stations/aiqs-station.svg', iconX: 1160, iconY: 740, iconWidth: 40, iconHeight: 40 },
              { id: 'actual-dps', x: 1090, y: 820, width: 200, height: 80, textKey: 'uc01.actual.dps', iconPath: '/assets/svg/shopfloor/stations/dps-station.svg', iconX: 1160, iconY: 840, iconWidth: 40, iconHeight: 40 },
            ],
          },
        ],
      },
      correlatedTimeline: {
        id: 'correlated-timeline',
        x: 1400,
        y: 300,
        width: 480,
        height: 900,
        headerX: 1440,
        headerY: 350,
        headerKey: 'uc01.column.correlated_timeline',
        lanes: [
          {
            id: 'nfc-tag',
            titleKey: 'uc01.lane.nfc_tag',
            chips: [
              { id: 'nfc-tag-chip', x: 1440, y: 400, width: 400, height: 80, textKey: 'uc01.nfc_tag.label', multiline: true, textLines: ['uc01.nfc_tag.label', 'A5873A2-A4525'] },
            ],
          },
          {
            id: 'event-timeline',
            titleKey: 'uc01.lane.event_timeline',
            // Timeline points as chips (vertical, top to bottom)
            // Events show PICK/Process/DROP at stations (correlated from Column 3)
            chips: [
              { id: 'timeline-1', x: 1490, y: 520, width: 280, height: 80, textKey: 'uc01.timeline.start_transfer' },
              { id: 'timeline-2', x: 1490, y: 620, width: 280, height: 80, textKey: 'uc01.timeline.warehouse_move', iconPath: '/assets/svg/shopfloor/stations/hbw-station.svg', iconX: 1560, iconY: 640, iconWidth: 40, iconHeight: 40 },
              { id: 'timeline-3', x: 1490, y: 720, width: 280, height: 80, textKey: 'uc01.timeline.drill_pick', iconPath: '/assets/svg/shopfloor/stations/drill-station.svg', iconX: 1560, iconY: 740, iconWidth: 40, iconHeight: 40 },
              { id: 'timeline-4', x: 1490, y: 820, width: 280, height: 80, textKey: 'uc01.timeline.drill_process', iconPath: '/assets/svg/shopfloor/stations/drill-station.svg', iconX: 1560, iconY: 840, iconWidth: 40, iconHeight: 40 },
              { id: 'timeline-5', x: 1490, y: 920, width: 280, height: 80, textKey: 'uc01.timeline.drill_drop', iconPath: '/assets/svg/shopfloor/stations/drill-station.svg', iconX: 1560, iconY: 940, iconWidth: 40, iconHeight: 40 },
              { id: 'timeline-6', x: 1490, y: 1020, width: 280, height: 80, textKey: 'uc01.timeline.quality_pick', iconPath: '/assets/svg/shopfloor/stations/aiqs-station.svg', iconX: 1560, iconY: 1040, iconWidth: 40, iconHeight: 40 },
              { id: 'timeline-7', x: 1490, y: 1120, width: 280, height: 80, textKey: 'uc01.timeline.quality_process', iconPath: '/assets/svg/shopfloor/stations/aiqs-station.svg', iconX: 1560, iconY: 1140, iconWidth: 40, iconHeight: 40 },
              { id: 'timeline-8', x: 1490, y: 1220, width: 280, height: 80, textKey: 'uc01.timeline.quality_drop', iconPath: '/assets/svg/shopfloor/stations/aiqs-station.svg', iconX: 1560, iconY: 1240, iconWidth: 40, iconHeight: 40 },
            ],
          },
          {
            id: 'order-context',
            titleKey: 'uc01.lane.order_context',
            chips: [
              { id: 'order-production', x: 1440, y: 700, width: 400, height: 50, textKey: 'uc01.order_context.production_order' },
              { id: 'order-customer', x: 1440, y: 760, width: 400, height: 50, textKey: 'uc01.order_context.customer_order' },
              { id: 'order-material', x: 1440, y: 820, width: 400, height: 50, textKey: 'uc01.order_context.material_batch' },
              { id: 'order-erp', x: 1440, y: 880, width: 400, height: 50, textKey: 'uc01.order_context.erp_id' },
            ],
          },
        ],
      },
    },
    
    connections: [
      // Business Events → Production Plan
      { id: 'purchase-to-storage', fromId: 'purchase-order-chip', toId: 'storage-order', fromX: 280, fromY: 425, toX: 720, toY: 460, dashed: true },
      { id: 'customer-to-production', fromId: 'customer-order-id', toId: 'production-order', fromX: 280, fromY: 925, toX: 720, toY: 960, dashed: true },
      // Production Plan → Actual Path
      { id: 'storage-plan-to-actual', fromId: 'storage-plan-warehouse', toId: 'actual-warehouse', fromX: 850, fromY: 860, toX: 1190, toY: 460, dashed: true },
      { id: 'production-plan-to-actual', fromId: 'production-plan-warehouse', toId: 'actual-warehouse', fromX: 850, fromY: 960, toX: 1190, toY: 460, dashed: true },
      // Actual Path → Correlated Timeline
      { id: 'actual-to-timeline', fromId: 'fts-route', toId: 'event-timeline', fromX: 1280, fromY: 450, toX: 1460, toY: 560, dashed: true },
      // NFC-Tag → Correlated Timeline
      { id: 'nfc-to-timeline', fromId: 'nfc-tag-chip', toId: 'event-timeline', fromX: 1640, fromY: 480, toX: 1460, toY: 560, dashed: true },
    ],
  };
  
  // Create and apply timeline synchronization
  // Use the first column's dimensions as reference (all columns have same y and height)
  const referenceColumn = structure.columns.businessEvents;
  const timeline = createTimeline(referenceColumn.y, referenceColumn.height);
  applyTimelineSync(structure, timeline);
  
  // Calculate layout for all columns (after timeline sync)
  calculateLaneLayout(structure.columns.businessEvents);
  calculateLaneLayout(structure.columns.productionPlan);
  calculateLaneLayout(structure.columns.actualPath);
  calculateLaneLayout(structure.columns.correlatedTimeline);
  
  return structure;
}
