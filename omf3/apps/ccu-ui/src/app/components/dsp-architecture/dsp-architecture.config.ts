/**
 * Configuration and layout data for the DSP Architecture diagram.
 * Defines default containers, connections, and animation steps based on PowerPoint reference.
 */
import type { ContainerConfig, ConnectionConfig, StepConfig, DiagramConfig } from './dsp-architecture.types';
import type { IconKey } from '../../assets/icon-registry';

/** SVG viewBox dimensions - increased height for better screen fit */
export const VIEWBOX_WIDTH = 1200;
export const VIEWBOX_HEIGHT = 860;

/** Layout constants - three equal-height layers with increased size */
export const LAYOUT = {
  // Title area
  TITLE_Y: 30,
  SUBTITLE_Y: 55,

  // Layer dimensions (equal height for all three - increased to accommodate top-aligned labels)
  LAYER_HEIGHT: 260,  // Increased from 230 to 260 to accommodate 18px font + padding at top
  LAYER_START_Y: 80,

  // Labels inside layers (left edge)
  LABEL_X: 10,
  LABEL_WIDTH: 90,  // Reduced to allow more content space

  // Business Process layer (top - white)
  BUSINESS_Y: 80,

  // DSP layer (middle - blue)
  DSP_LAYER_Y: 340,  // Adjusted: 80 + 260

  // Shopfloor layer (bottom - gray)
  SHOPFLOOR_Y: 600,  // Adjusted: 80 + 260 + 260

  // Box dimensions - increased heights for larger icons
  BUSINESS_BOX_WIDTH: 200,
  BUSINESS_BOX_HEIGHT: 140,
  DSP_BOX_HEIGHT: 165,  // Increased for larger icons

  // Margins and spacing (content starts after label area) - maximized horizontal space
  CONTENT_START_X: 100,  // Reduced for more content space
  MARGIN_RIGHT: 30,
  CONTENT_WIDTH: 1090,  // Increased content width
  BOX_GAP: 25,
};

/**
 * Default containers for the DSP Architecture diagram.
 * Container IDs are used for connections and animation steps.
 */
export function createDefaultContainers(): ContainerConfig[] {
  const containers: ContainerConfig[] = [];

  // ========== LAYER BACKGROUNDS (with labels inside, extending to left edge) ==========

  // Business Process layer background (white) - label "Business\nProzesse" inside
  containers.push({
    id: 'layer-business',
    label: '',  // "Business\nProzesse" - set via i18n, two lines
    x: 0,  // Extends to left edge
    y: LAYOUT.BUSINESS_Y,
    width: VIEWBOX_WIDTH,
    height: LAYOUT.LAYER_HEIGHT,
    type: 'layer',
    state: 'hidden',
    backgroundColor: '#ffffff',
    borderColor: 'rgba(22, 65, 148, 0.1)', // ORBIS Blue Strong RGB
    isGroup: true,
    labelPosition: 'left',  // Label on left side
  });

  // DSP layer background (blue) - label "DSP" inside
  containers.push({
    id: 'layer-dsp',
    label: '',  // "DSP"
    x: 0,
    y: LAYOUT.DSP_LAYER_Y,
    width: VIEWBOX_WIDTH,
    height: LAYOUT.LAYER_HEIGHT,
    type: 'layer',
    state: 'hidden',
    backgroundColor: 'rgba(207, 230, 255, 0.5)',
    borderColor: 'rgba(22, 65, 148, 0.15)', // ORBIS Blue Strong RGB
    isGroup: true,
    labelPosition: 'left',
  });

  // Shopfloor layer background (gray) - label "Shopfloor" inside (without "Systeme und Geräte")
  containers.push({
    id: 'layer-shopfloor',
    label: '',  // "Shopfloor" - single line now
    x: 0,
    y: LAYOUT.SHOPFLOOR_Y,
    width: VIEWBOX_WIDTH,
    height: LAYOUT.LAYER_HEIGHT,
    type: 'layer',
    state: 'normal',
    backgroundColor: 'rgba(241, 243, 247, 0.8)',
    borderColor: 'rgba(31, 54, 91, 0.12)',
    isGroup: true,
    labelPosition: 'left',
  });

  // ========== DSP LAYER LABELS ("On Premise" and "Cloud") ==========
  containers.push({
    id: 'dsp-label-onpremise',
    label: '',  // "On Premise"
    x: LAYOUT.CONTENT_START_X + 200,
    y: LAYOUT.DSP_LAYER_Y + 32,  // Moved down by 20px to accommodate top-aligned layer label
    width: 100,
    height: 20,
    type: 'label',
    state: 'hidden',
    fontSize: 14,  // Increased font size
  });

  containers.push({
    id: 'dsp-label-cloud',
    label: '',  // "Cloud"
    x: LAYOUT.CONTENT_START_X + 850,
    y: LAYOUT.DSP_LAYER_Y + 32,  // Moved down by 20px to accommodate top-aligned layer label
    width: 60,
    height: 20,
    type: 'label',
    state: 'hidden',
    fontSize: 14,  // Increased font size
  });

  // ========== DSP UX BOX (SmartFactory Dashboard) - larger box, two-line label ==========
  // Calculate available width for DSP boxes (maximize horizontal space)
  const dspAvailableWidth = VIEWBOX_WIDTH - LAYOUT.CONTENT_START_X - LAYOUT.MARGIN_RIGHT;
  const dspBoxGap = 50;  // Increased gap between boxes for better visibility of arrows

  // UX box width calculated for optimal space usage
  const uxBoxWidth = 175;  // Slightly larger
  const edgeBoxWidth = 480;  // Wider for more icons
  const managementBoxWidth = dspAvailableWidth - uxBoxWidth - edgeBoxWidth - (dspBoxGap * 2);

  containers.push({
    id: 'ux',
    label: '',  // "SmartFactory\nDashboard" - two-line label at top, centered
    x: LAYOUT.CONTENT_START_X,
    y: LAYOUT.DSP_LAYER_Y + 55,  // Moved down by 20px to accommodate top-aligned layer label
    width: uxBoxWidth,
    height: LAYOUT.DSP_BOX_HEIGHT,
    type: 'ux',
    state: 'hidden',
    logoIconKey: 'ux-dashboard' as IconKey,  // dsp/dashboard.svg - now centered like Edge
    borderColor: '#009681',  // Solution Petrol (ORBIS CI)
    backgroundColor: '#ffffff',
    labelPosition: 'top-center',
    fontSize: 20,  // Increased font size for DSP layer (16 + 4pt)
    url: '/dashboard',  // Default URL for SmartFactory Dashboard
  });

  // ========== DSP EDGE BOX - wider for larger icons ==========
  containers.push({
    id: 'edge',
    label: '',  // "EDGE" - label at top center
    x: LAYOUT.CONTENT_START_X + uxBoxWidth + dspBoxGap,
    y: LAYOUT.DSP_LAYER_Y + 55,  // Moved down by 20px to accommodate top-aligned layer label
    width: edgeBoxWidth,
    height: LAYOUT.DSP_BOX_HEIGHT,
    type: 'dsp-edge',
    state: 'hidden',
    logoIconKey: 'logo-dsp' as IconKey,
    logoPosition: 'top-left',
    borderColor: '#009681',  // Solution Petrol (ORBIS CI)
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    labelPosition: 'top-center',
    fontSize: 20,  // Increased font size for DSP layer (16 + 4pt)
    functionIcons: [
      { iconKey: 'edge-data-storage' as IconKey, size: 60 },  // Larger icon size
      { iconKey: 'edge-network' as IconKey, size: 60 },
      { iconKey: 'edge-digital-twin' as IconKey, size: 60 },
      { iconKey: 'edge-workflow' as IconKey, size: 60 },
      { iconKey: 'edge-analytics' as IconKey, size: 60 },
    ],
    url: '/edge',  // Default URL for DSP Edge
  });

  // ========== DSP MANAGEMENT COCKPIT BOX - ORBIS logo top-left like Edge, Azure icon top-right, 2 function icons ==========
  containers.push({
    id: 'management',
    label: '',  // "Management Cockpit" - label at top center
    x: LAYOUT.CONTENT_START_X + uxBoxWidth + dspBoxGap + edgeBoxWidth + dspBoxGap,
    y: LAYOUT.DSP_LAYER_Y + 55,  // Moved down by 20px to accommodate top-aligned layer label
    width: managementBoxWidth,
    height: LAYOUT.DSP_BOX_HEIGHT,
    type: 'dsp-cloud',
    state: 'hidden',
    logoIconKey: 'logo-dsp' as IconKey,  // ORBIS logo - top-left like Edge
    logoPosition: 'top-left',
    secondaryLogoIconKey: 'logo-azure' as IconKey,  // Azure logo - top-right corner
    secondaryLogoPosition: 'top-right',
    borderColor: '#009681',  // Solution Petrol (ORBIS CI)
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    labelPosition: 'top-center',
    fontSize: 20,  // Increased font size for DSP layer (16 + 4pt)
    functionIcons: [
      { iconKey: 'logo-distributed' as IconKey, size: 60 },  // distributed.svg icon - larger
      { iconKey: 'shopfloor-it' as IconKey, size: 60 },  // Information technology icon - larger
    ],
    url: '/management-cockpit',  // Default URL for Management Cockpit
  });

  // ========== BUSINESS PROCESSES (equal-sized boxes, labels at top centered, with icons) ==========
  const businessAvailableWidth = VIEWBOX_WIDTH - LAYOUT.CONTENT_START_X - LAYOUT.MARGIN_RIGHT;
  const businessBoxCount = 4;
  const businessGap = 30;  // Increased gap for better visibility
  const businessBoxWidth = (businessAvailableWidth - (businessBoxCount - 1) * businessGap) / businessBoxCount;
  const businessBoxY = LAYOUT.BUSINESS_Y + 65;  // Moved down by 20px to accommodate top-aligned layer label
  const businessStartX = LAYOUT.CONTENT_START_X;

  containers.push({
    id: 'erp-application',
    label: '',  // "ERP Applications" - label at top center
    x: businessStartX,
    y: businessBoxY,
    width: businessBoxWidth,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    logoIconKey: 'erp-application' as IconKey,  // Generic ERP application icon, centered
    secondaryLogoIconKey: 'logo-sap' as IconKey,  // SAP logo in top-right corner
    secondaryLogoPosition: 'top-right',
    borderColor: 'rgba(22, 65, 148, 0.25)', // ORBIS Blue Strong RGB
    backgroundColor: '#ffffff',
    labelPosition: 'top-center',
    fontSize: 20,  // Increased font size for BP layer (16 + 4pt)
  });

  containers.push({
    id: 'bp-cloud-apps',
    label: '',  // "Cloud Anwendungen" - label at top center
    x: businessStartX + (businessBoxWidth + businessGap),
    y: businessBoxY,
    width: businessBoxWidth,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    logoIconKey: 'bp-cloud-apps' as IconKey,  // dsp/cloud-computing.svg
    borderColor: 'rgba(22, 65, 148, 0.25)', // ORBIS Blue Strong RGB
    backgroundColor: '#ffffff',
    labelPosition: 'top-center',
    fontSize: 20,  // Increased font size for BP layer (16 + 4pt)
  });

  containers.push({
    id: 'bp-analytics',
    label: '',  // "Analytische\nAnwendungen" - label at top center
    x: businessStartX + (businessBoxWidth + businessGap) * 2,
    y: businessBoxY,
    width: businessBoxWidth,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    logoIconKey: 'bp-analytics' as IconKey,  // dsp/dashboard.svg
    borderColor: 'rgba(22, 65, 148, 0.25)', // ORBIS Blue Strong RGB
    backgroundColor: '#ffffff',
    labelPosition: 'top-center',
    fontSize: 20,  // Increased font size for BP layer (16 + 4pt)
    url: '/analytics',  // Default URL for Analytische Anwendungen
  });

  containers.push({
    id: 'bp-data-lake',
    label: '',  // "Data Lake" - label at top center
    x: businessStartX + (businessBoxWidth + businessGap) * 3,
    y: businessBoxY,
    width: businessBoxWidth,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    logoIconKey: 'bp-data-lake' as IconKey,  // dsp/data-lake.svg
    borderColor: 'rgba(22, 65, 148, 0.25)', // ORBIS Blue Strong RGB
    backgroundColor: '#ffffff',
    labelPosition: 'top-center',
    fontSize: 20,  // Increased font size for BP layer (16 + 4pt)
  });

  // ========== SHOPFLOOR LAYER CONTENT ==========

  // Calculate shopfloor available width (maximize horizontal space)
  const shopfloorAvailableWidth = VIEWBOX_WIDTH - LAYOUT.CONTENT_START_X - LAYOUT.MARGIN_RIGHT;
  const shopfloorGap = 40;  // Gap between systems and devices groups
  const shopfloorGroupHeight = 175;
  const shopfloorGroupY = LAYOUT.SHOPFLOOR_Y + 48;  // Moved down by 20px to accommodate top-aligned layer label

  // Systems group takes ~30% of available width
  const systemsGroupWidth = 300;
  // Devices group takes remaining width
  const devicesGroupWidth = shopfloorAvailableWidth - systemsGroupWidth - shopfloorGap;

  containers.push({
    id: 'shopfloor-systems-group',
    label: '',  // "Systeme" - label at bottom center
    x: LAYOUT.CONTENT_START_X,
    y: shopfloorGroupY,
    width: systemsGroupWidth,
    height: shopfloorGroupHeight,
    type: 'shopfloor',
    state: 'hidden',
    borderColor: 'rgba(22, 65, 148, 0.2)', // ORBIS Blue Strong RGB
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 18,  // Same font size as DSP and BP layers
  });

  // Shopfloor System icons with labels below - larger icons
  const systemIconY = shopfloorGroupY + 15;
  const systemIconWidth = 110;  // Increased
  const systemIconHeight = 115;  // Increased
  const systemIconGap = 35;

  containers.push({
    id: 'shopfloor-system-bp',
    label: 'FTS',  // Label below icon
    x: LAYOUT.CONTENT_START_X + 25,
    y: systemIconY,
    width: systemIconWidth,
    height: systemIconHeight,
    type: 'device',
    state: 'hidden',
    logoIconKey: 'shopfloor-fts' as IconKey,
    borderColor: 'rgba(128, 128, 128, 0.25)',  // Dezenter grauer Rahmen
    backgroundColor: '#f8f9fa',  // Leichte graue Füllung
    labelPosition: 'bottom',
    fontSize: 13,  // Increased font size
  });

  containers.push({
    id: 'shopfloor-system-fts',
    label: 'any',  // Label below icon
    x: LAYOUT.CONTENT_START_X + 25 + systemIconWidth + systemIconGap,
    y: systemIconY,
    width: systemIconWidth,
    height: systemIconHeight,
    type: 'device',
    state: 'hidden',
    logoIconKey: 'shopfloor-mes' as IconKey,
    borderColor: 'rgba(128, 128, 128, 0.25)',  // Dezenter grauer Rahmen
    backgroundColor: '#f8f9fa',  // Leichte graue Füllung
    labelPosition: 'bottom',
    fontSize: 13,  // Increased font size
  });

  // Geräte container (right) - label at bottom, horizontally centered
  containers.push({
    id: 'shopfloor-devices-group',
    label: '',  // "Geräte" - label at bottom center
    x: LAYOUT.CONTENT_START_X + systemsGroupWidth + shopfloorGap,
    y: shopfloorGroupY,
    width: devicesGroupWidth,
    height: shopfloorGroupHeight,
    type: 'shopfloor',
    state: 'normal',
    borderColor: 'rgba(22, 65, 148, 0.2)', // ORBIS Blue Strong RGB
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 18,  // Same font size as DSP and BP layers
  });

  // Device icons with labels below (DRILL, HBW, MILL, AIQS, DPS, CHRG) using shopfloor/*.svg
  // Calculate device dimensions to fill available space
  const deviceCount = 6;
  const deviceGap = 15;
  const deviceGroupPadding = 20;
  const deviceWidth = (devicesGroupWidth - (deviceCount - 1) * deviceGap - deviceGroupPadding * 2) / deviceCount;
  const deviceStartX = LAYOUT.CONTENT_START_X + systemsGroupWidth + shopfloorGap + deviceGroupPadding;
  const deviceY = shopfloorGroupY + 12;
  const deviceHeight = 120;  // Increased height for larger icons

  const deviceConfigs = [
    { iconKey: 'device-drill' as IconKey, label: 'DRILL' },
    { iconKey: 'device-hbw' as IconKey, label: 'HBW' },
    { iconKey: 'device-mill' as IconKey, label: 'MILL' },
    { iconKey: 'device-aiqs' as IconKey, label: 'AIQS' },
    { iconKey: 'device-dps' as IconKey, label: 'DPS' },
    { iconKey: 'device-chrg' as IconKey, label: 'CHRG' },
  ];

  deviceConfigs.forEach((config, index) => {
    containers.push({
      id: `shopfloor-device-${index + 1}`,
      label: config.label,  // Label below icon
      x: deviceStartX + (deviceWidth + deviceGap) * index,
      y: deviceY,
      width: deviceWidth,
      height: deviceHeight,
      type: 'device',
      state: 'normal',
      logoIconKey: config.iconKey,
      borderColor: 'rgba(128, 128, 128, 0.25)',  // Dezenter grauer Rahmen
      backgroundColor: '#f8f9fa',  // Leichte graue Füllung
      labelPosition: 'bottom',
      fontSize: 10,  // Reduced font size for better fit with long labels
    });
  });

  return containers;
}

/**
 * Default connections between containers.
 * All arrows are bidirectional as per requirements.
 */
export function createDefaultConnections(): ConnectionConfig[] {
  return [
    // DSP internal connections
    {
      id: 'conn-ux-edge',
      fromId: 'ux',
      toId: 'edge',
      fromSide: 'right',
      toSide: 'left',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    {
      id: 'conn-edge-management',
      fromId: 'edge',
      toId: 'management',
      fromSide: 'right',
      toSide: 'left',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },

    // Edge to all shopfloor devices (bidirectional)
    {
      id: 'conn-edge-device-1',
      fromId: 'edge',
      toId: 'shopfloor-device-1',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    {
      id: 'conn-edge-device-2',
      fromId: 'edge',
      toId: 'shopfloor-device-2',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    {
      id: 'conn-edge-device-3',
      fromId: 'edge',
      toId: 'shopfloor-device-3',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    {
      id: 'conn-edge-device-4',
      fromId: 'edge',
      toId: 'shopfloor-device-4',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    {
      id: 'conn-edge-device-5',
      fromId: 'edge',
      toId: 'shopfloor-device-5',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    {
      id: 'conn-edge-device-6',
      fromId: 'edge',
      toId: 'shopfloor-device-6',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },

    // Edge to shopfloor system icons (not to group - arrows go to individual icons)
    {
      id: 'conn-edge-system-bp',
      fromId: 'edge',
      toId: 'shopfloor-system-bp',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    {
      id: 'conn-edge-system-fts',
      fromId: 'edge',
      toId: 'shopfloor-system-fts',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },

    // Business to DSP connections (all bidirectional)
    {
      id: 'conn-erp-edge',
      fromId: 'erp-application',
      toId: 'edge',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    {
      id: 'conn-cloud-edge',
      fromId: 'bp-cloud-apps',
      toId: 'edge',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,  // All bidirectional now
    },
    {
      id: 'conn-analytics-edge',
      fromId: 'bp-analytics',
      toId: 'edge',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,  // All bidirectional now
    },
    {
      id: 'conn-datalake-edge',
      fromId: 'bp-data-lake',
      toId: 'edge',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,  // All bidirectional now
    },
  ];
}

/**
 * Default animation steps - Extended to 12 steps for comprehensive DSP story.
 * 1. Shopfloor Devices - heterogeneous devices
 * 2. Shopfloor Systems - AGVs, warehouses, custom controllers
 * 3. DSP Edge Core - local runtime appears
 * 4. Edge Connectivity - OPC UA, MQTT, REST
 * 5. Digital Twin & Data Modeling - normalization and twin
 * 6. Process Logic / Choreography - decentralized processes
 * 7. Analytics / AI Preparation - KPIs, OEE, ML prep
 * 8. Connections Shopfloor ↔ Edge - bidirectional communication
 * 9. Management Cockpit - cloud-based orchestration
 * 10. Business Integration - ERP, Cloud, Analytics, Data Lake
 * 11. SmartFactory Dashboard - visualization layer
 * 12. Autonomous & Adaptive Enterprise (Phase 5) - autonomous optimization highlight
 */
export function createDefaultSteps(): StepConfig[] {
  const baseShopfloorContainers = [
    'layer-shopfloor',
    'shopfloor-systems-group',
    'shopfloor-system-bp',
    'shopfloor-system-fts',
    'shopfloor-devices-group',
    'shopfloor-device-1',
    'shopfloor-device-2',
    'shopfloor-device-3',
    'shopfloor-device-4',
    'shopfloor-device-5',
    'shopfloor-device-6',
  ];

  const baseShopfloorConnections = [
    'conn-edge-system-bp',
    'conn-edge-system-fts',
    'conn-edge-device-1',
    'conn-edge-device-2',
    'conn-edge-device-3',
    'conn-edge-device-4',
    'conn-edge-device-5',
    'conn-edge-device-6',
  ];

  return [
    // Step 1: Shopfloor Devices - DSP vernetzt heterogene Geräte
    {
      id: 'step-1',
      label: '',
      visibleContainerIds: [
        'layer-shopfloor',
        'shopfloor-devices-group',
        'shopfloor-device-1',
        'shopfloor-device-2',
        'shopfloor-device-3',
        'shopfloor-device-4',
        'shopfloor-device-5',
        'shopfloor-device-6',
      ],
      highlightedContainerIds: ['shopfloor-devices-group', 'shopfloor-device-1', 'shopfloor-device-2', 'shopfloor-device-3', 'shopfloor-device-4', 'shopfloor-device-5', 'shopfloor-device-6'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
    },

    // Step 2: Shopfloor Systems - DSP integriert komplette Systeme (AGVs, Lager, etc.)
    {
      id: 'step-2',
      label: '',
      visibleContainerIds: baseShopfloorContainers,
      highlightedContainerIds: ['shopfloor-systems-group', 'shopfloor-system-bp', 'shopfloor-system-fts'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
    },

    // Step 3: DSP Edge Core erscheint - lokale Runtime
    {
      id: 'step-3',
      label: '',
      visibleContainerIds: [
        'layer-dsp',
        'dsp-label-onpremise',
        'edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['layer-dsp', 'edge'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
      showFunctionIcons: false,
    },

    // Step 4: Edge Connectivity - OPC UA, MQTT, REST
    {
      id: 'step-4',
      label: '',
      visibleContainerIds: [
        'layer-dsp',
        'dsp-label-onpremise',
        'edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['edge'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
      showFunctionIcons: true,
    },

    // Step 5: Digital Twin & Data Modeling - Edge normalisiert Datenströme
    {
      id: 'step-5',
      label: '',
      visibleContainerIds: [
        'layer-dsp',
        'dsp-label-onpremise',
        'edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['edge'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
      showFunctionIcons: true,
    },

    // Step 6: Process Logic / Choreography - Prozessobjekte, dezentral
    {
      id: 'step-6',
      label: '',
      visibleContainerIds: [
        'layer-dsp',
        'dsp-label-onpremise',
        'edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['edge'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
      showFunctionIcons: true,
    },

    // Step 7: Analytics / AI Preparation - Edge verdichtet Daten für KPIs, ML
    {
      id: 'step-7',
      label: '',
      visibleContainerIds: [
        'layer-dsp',
        'dsp-label-onpremise',
        'edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['edge'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
      showFunctionIcons: true,
    },

    // Step 8: Connections Shopfloor ↔ Edge - bidirektionale Kommunikation
    {
      id: 'step-8',
      label: '',
      visibleContainerIds: [
        'layer-dsp',
        'dsp-label-onpremise',
        'edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: [],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: baseShopfloorConnections,
      showFunctionIcons: true,
    },

    // Step 9: Management Cockpit - zentral in der Cloud
    {
      id: 'step-9',
      label: '',
      visibleContainerIds: [
        'layer-dsp',
        'dsp-label-onpremise',
        'dsp-label-cloud',
        'edge',
        'management',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['management'],
      visibleConnectionIds: [
        'conn-edge-management',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: ['conn-edge-management'],
      showFunctionIcons: true,
    },

    // Step 10: Business Integration - ERP, Cloud, Analytics, Data Lake
    {
      id: 'step-10',
      label: '',
      visibleContainerIds: [
        'layer-business',
        'layer-dsp',
        'dsp-label-onpremise',
        'dsp-label-cloud',
        'erp-application',
        'bp-cloud-apps',
        'bp-analytics',
        'bp-data-lake',
        'edge',
        'management',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['layer-business', 'erp-application', 'bp-cloud-apps', 'bp-analytics', 'bp-data-lake'],
      visibleConnectionIds: [
        'conn-edge-management',
        'conn-erp-edge',
        'conn-cloud-edge',
        'conn-analytics-edge',
        'conn-datalake-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: ['conn-erp-edge', 'conn-cloud-edge', 'conn-analytics-edge', 'conn-datalake-edge'],
      showFunctionIcons: true,
    },

    // Step 11: SmartFactory Dashboard - Visualisierung
    {
      id: 'step-11',
      label: '',
      visibleContainerIds: [
        'layer-business',
        'layer-dsp',
        'dsp-label-onpremise',
        'dsp-label-cloud',
        'erp-application',
        'bp-cloud-apps',
        'bp-analytics',
        'bp-data-lake',
        'ux',
        'edge',
        'management',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['ux'],
      visibleConnectionIds: [
        'conn-ux-edge',
        'conn-edge-management',
        'conn-erp-edge',
        'conn-cloud-edge',
        'conn-analytics-edge',
        'conn-datalake-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: ['conn-ux-edge'],
      showFunctionIcons: true,
    },

    // Step 12: Autonomous & Adaptive Enterprise (Phase 5) - alle Ebenen hervorgehoben
    {
      id: 'step-12',
      label: '',
      visibleContainerIds: [
        'layer-business',
        'layer-dsp',
        'dsp-label-onpremise',
        'dsp-label-cloud',
        'erp-application',
        'bp-cloud-apps',
        'bp-analytics',
        'bp-data-lake',
        'ux',
        'edge',
        'management',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: [
        'layer-business',
        'layer-dsp',
        'ux',
        'edge',
        'management',
        'erp-application',
        'bp-cloud-apps',
        'bp-analytics',
        'bp-data-lake',
      ],
      visibleConnectionIds: [
        'conn-ux-edge',
        'conn-edge-management',
        'conn-erp-edge',
        'conn-cloud-edge',
        'conn-analytics-edge',
        'conn-datalake-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [],
      showFunctionIcons: true,
    },
  ];
}

/**
 * Creates the complete diagram configuration.
 */
export function createDiagramConfig(): DiagramConfig {
  return {
    containers: createDefaultContainers(),
    connections: createDefaultConnections(),
    steps: createDefaultSteps(),
    viewBox: {
      width: VIEWBOX_WIDTH,
      height: VIEWBOX_HEIGHT,
    },
  };
}
