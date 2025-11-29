/**
 * Configuration and layout data for the DSP Architecture diagram.
 * Defines default containers, connections, and animation steps based on PowerPoint reference.
 */
import type { ContainerConfig, ConnectionConfig, StepConfig, DiagramConfig } from './dsp-architecture.types';
import type { IconKey } from '../../assets/icon-registry';

/** SVG viewBox dimensions */
export const VIEWBOX_WIDTH = 1200;
export const VIEWBOX_HEIGHT = 700;

/** Layout constants - three equal-height layers */
export const LAYOUT = {
  // Title area
  TITLE_Y: 30,
  SUBTITLE_Y: 55,

  // Layer dimensions (equal height for all three)
  LAYER_HEIGHT: 180,
  LAYER_START_Y: 80,

  // Business Process layer (top - white)
  BUSINESS_Y: 80,

  // DSP layer (middle - blue)
  DSP_LAYER_Y: 260,

  // Shopfloor layer (bottom - gray)
  SHOPFLOOR_Y: 440,

  // Box dimensions
  BUSINESS_BOX_WIDTH: 150,
  BUSINESS_BOX_HEIGHT: 70,
  DSP_BOX_HEIGHT: 120,

  // Margins and spacing
  LABEL_WIDTH: 120,
  MARGIN_LEFT: 150,
  MARGIN_RIGHT: 50,
  CONTENT_WIDTH: 1000,
  BOX_GAP: 20,
};

/**
 * Default containers for the DSP Architecture diagram.
 * Container IDs are used for connections and animation steps.
 */
export function createDefaultContainers(): ContainerConfig[] {
  const containers: ContainerConfig[] = [];

  // ========== LAYER BACKGROUNDS ==========

  // Business Process layer background (white)
  containers.push({
    id: 'layer-business',
    x: LAYOUT.MARGIN_LEFT,
    y: LAYOUT.BUSINESS_Y,
    width: LAYOUT.CONTENT_WIDTH,
    height: LAYOUT.LAYER_HEIGHT,
    type: 'layer',
    state: 'hidden',
    backgroundColor: '#ffffff',
    borderColor: 'rgba(31, 84, 178, 0.1)',
    isGroup: true,
  });

  // DSP layer background (blue)
  containers.push({
    id: 'layer-dsp',
    x: LAYOUT.MARGIN_LEFT,
    y: LAYOUT.DSP_LAYER_Y,
    width: LAYOUT.CONTENT_WIDTH,
    height: LAYOUT.LAYER_HEIGHT,
    type: 'layer',
    state: 'hidden',
    backgroundColor: 'rgba(207, 230, 255, 0.5)',
    borderColor: 'rgba(31, 84, 178, 0.15)',
    isGroup: true,
  });

  // Shopfloor layer background (gray)
  containers.push({
    id: 'layer-shopfloor',
    x: LAYOUT.MARGIN_LEFT,
    y: LAYOUT.SHOPFLOOR_Y,
    width: LAYOUT.CONTENT_WIDTH,
    height: LAYOUT.LAYER_HEIGHT,
    type: 'layer',
    state: 'normal',
    backgroundColor: 'rgba(241, 243, 247, 0.8)',
    borderColor: 'rgba(31, 54, 91, 0.12)',
    isGroup: true,
  });

  // ========== LAYER LABELS (left-aligned, vertically centered) ==========
  containers.push({
    id: 'label-business',
    label: '',  // "Business Process"
    x: 10,
    y: LAYOUT.BUSINESS_Y + (LAYOUT.LAYER_HEIGHT / 2) - 10,
    width: LAYOUT.LABEL_WIDTH,
    height: 30,
    type: 'label',
    state: 'hidden',
    fontSize: 14,
  });

  containers.push({
    id: 'label-dsp',
    label: '',  // "DSP"
    x: 10,
    y: LAYOUT.DSP_LAYER_Y + (LAYOUT.LAYER_HEIGHT / 2) - 10,
    width: LAYOUT.LABEL_WIDTH,
    height: 30,
    type: 'label',
    state: 'hidden',
    fontSize: 14,
  });

  containers.push({
    id: 'label-shopfloor',
    label: '',  // "Shopfloor"
    x: 10,
    y: LAYOUT.SHOPFLOOR_Y + (LAYOUT.LAYER_HEIGHT / 2) - 10,
    width: LAYOUT.LABEL_WIDTH,
    height: 30,
    type: 'label',
    state: 'normal',
    fontSize: 14,
  });

  // ========== DSP LAYER LABELS ("On Premise" and "Cloud") ==========
  containers.push({
    id: 'dsp-label-onpremise',
    label: '',  // "On Premise"
    x: LAYOUT.MARGIN_LEFT + 160,
    y: LAYOUT.DSP_LAYER_Y + 8,
    width: 100,
    height: 20,
    type: 'label',
    state: 'hidden',
    fontSize: 12,
  });

  containers.push({
    id: 'dsp-label-cloud',
    label: '',  // "Cloud"
    x: LAYOUT.MARGIN_LEFT + LAYOUT.CONTENT_WIDTH - 220,
    y: LAYOUT.DSP_LAYER_Y + 8,
    width: 60,
    height: 20,
    type: 'label',
    state: 'hidden',
    fontSize: 12,
  });

  // ========== DSP EDGE BOX ==========
  containers.push({
    id: 'edge',
    label: '',  // "EDGE"
    x: LAYOUT.MARGIN_LEFT + 100,
    y: LAYOUT.DSP_LAYER_Y + 35,
    width: 450,
    height: LAYOUT.DSP_BOX_HEIGHT,
    type: 'dsp-edge',
    state: 'hidden',
    logoIconKey: 'logo-dsp' as IconKey,
    logoPosition: 'top-left',
    borderColor: '#009B77',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    functionIcons: [
      { iconKey: 'edge-data-storage' as IconKey, size: 40 },
      { iconKey: 'edge-digital-twin' as IconKey, size: 40 },
      { iconKey: 'edge-network' as IconKey, size: 40 },
      { iconKey: 'edge-workflow' as IconKey, size: 40 },
    ],
  });

  // ========== UX BOX (Shopfloor Dashboard) ==========
  containers.push({
    id: 'ux',
    label: '',  // "UX" with monitor icon
    x: LAYOUT.MARGIN_LEFT + 10,
    y: LAYOUT.DSP_LAYER_Y + 45,
    width: 80,
    height: 100,
    type: 'ux',
    state: 'hidden',
    logoIconKey: 'ux-monitor' as IconKey,
    borderColor: 'rgba(31, 84, 178, 0.3)',
    backgroundColor: '#ffffff',
  });

  // ========== DSP MANAGEMENT COCKPIT BOX ==========
  containers.push({
    id: 'management',
    label: '',  // "Management Cockpit"
    x: LAYOUT.MARGIN_LEFT + 600,
    y: LAYOUT.DSP_LAYER_Y + 35,
    width: 350,
    height: LAYOUT.DSP_BOX_HEIGHT,
    type: 'dsp-cloud',
    state: 'hidden',
    logoIconKey: 'logo-dsp' as IconKey,
    logoPosition: 'top-left',
    secondaryLogoIconKey: 'logo-azure' as IconKey,
    secondaryLogoPosition: 'top-right',
    borderColor: '#0078D4',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
  });

  // ========== BUSINESS PROCESSES ==========
  const businessStartX = LAYOUT.MARGIN_LEFT + 50;
  const businessBoxWidth = 160;
  const businessGap = 30;
  const businessBoxY = LAYOUT.BUSINESS_Y + 55;

  containers.push({
    id: 'bp-sap-shopfloor',
    label: '',  // "SAP Shopfloor"
    x: businessStartX,
    y: businessBoxY,
    width: businessBoxWidth,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    logoIconKey: 'bp-sap-shopfloor' as IconKey,
    logoPosition: 'top-left',
    borderColor: 'rgba(31, 84, 178, 0.25)',
    backgroundColor: '#ffffff',
  });

  containers.push({
    id: 'bp-cloud-apps',
    label: '',  // "Cloud Anwendungen"
    x: businessStartX + businessBoxWidth + businessGap,
    y: businessBoxY,
    width: businessBoxWidth + 10,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    borderColor: 'rgba(31, 84, 178, 0.25)',
    backgroundColor: '#ffffff',
  });

  containers.push({
    id: 'bp-analytics',
    label: '',  // "Analytische Anwendungen"
    x: businessStartX + (businessBoxWidth + businessGap) * 2 + 10,
    y: businessBoxY,
    width: businessBoxWidth + 30,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    borderColor: 'rgba(31, 84, 178, 0.25)',
    backgroundColor: '#ffffff',
  });

  containers.push({
    id: 'bp-data-lake',
    label: '',  // "Data Lake"
    x: businessStartX + (businessBoxWidth + businessGap) * 3 + 40,
    y: businessBoxY,
    width: businessBoxWidth - 30,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    borderColor: 'rgba(31, 84, 178, 0.25)',
    backgroundColor: '#ffffff',
  });

  // ========== SHOPFLOOR LAYER CONTENT ==========

  // Shopfloor Systeme group (left)
  containers.push({
    id: 'shopfloor-systems-group',
    label: '',  // "Shopfloor Systeme"
    x: LAYOUT.MARGIN_LEFT + 20,
    y: LAYOUT.SHOPFLOOR_Y + 30,
    width: 250,
    height: 120,
    type: 'shopfloor',
    state: 'hidden',
    borderColor: 'rgba(31, 84, 178, 0.2)',
    backgroundColor: '#ffffff',
  });

  // Shopfloor System icons (inside group)
  containers.push({
    id: 'shopfloor-system-bp',
    x: LAYOUT.MARGIN_LEFT + 40,
    y: LAYOUT.SHOPFLOOR_Y + 60,
    width: 60,
    height: 60,
    type: 'device',
    state: 'hidden',
    logoIconKey: 'bp-business-process' as IconKey,
    borderColor: 'transparent',
    backgroundColor: 'transparent',
  });

  containers.push({
    id: 'shopfloor-system-fts',
    x: LAYOUT.MARGIN_LEFT + 120,
    y: LAYOUT.SHOPFLOOR_Y + 60,
    width: 60,
    height: 60,
    type: 'device',
    state: 'hidden',
    logoIconKey: 'device-conveyor' as IconKey,
    borderColor: 'transparent',
    backgroundColor: 'transparent',
  });

  // Geräte group (right)
  containers.push({
    id: 'shopfloor-devices-group',
    label: '',  // "Geräte"
    x: LAYOUT.MARGIN_LEFT + 300,
    y: LAYOUT.SHOPFLOOR_Y + 30,
    width: 650,
    height: 120,
    type: 'shopfloor',
    state: 'normal',
    borderColor: 'rgba(31, 84, 178, 0.2)',
    backgroundColor: '#ffffff',
  });

  // Device icons - representing various shopfloor equipment
  // Icons are mapped to available assets from the icon registry
  const deviceStartX = LAYOUT.MARGIN_LEFT + 330;
  const deviceWidth = 70;
  const deviceGap = 25;
  const deviceY = LAYOUT.SHOPFLOOR_Y + 55;

  const deviceIconKeys: IconKey[] = [
    'device-plc' as IconKey,
    'device-conveyor' as IconKey,
    'device-sensor' as IconKey,
    'device-camera' as IconKey,
    'device-robot-arm' as IconKey,
    'device-printer' as IconKey,
  ];

  deviceIconKeys.forEach((iconKey, index) => {
    containers.push({
      id: `shopfloor-device-${index + 1}`,
      x: deviceStartX + (deviceWidth + deviceGap) * index,
      y: deviceY,
      width: deviceWidth,
      height: 70,
      type: 'device',
      state: 'normal',
      logoIconKey: iconKey,
      borderColor: 'rgba(31, 84, 178, 0.15)',
      backgroundColor: '#ffffff',
    });
  });

  return containers;
}

/**
 * Default connections between containers.
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

    // Edge to shopfloor systems
    {
      id: 'conn-edge-systems',
      fromId: 'edge',
      toId: 'shopfloor-systems-group',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },

    // Business to DSP connections
    {
      id: 'conn-sap-edge',
      fromId: 'bp-sap-shopfloor',
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
    },
    {
      id: 'conn-analytics-edge',
      fromId: 'bp-analytics',
      toId: 'edge',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
    },
    {
      id: 'conn-datalake-edge',
      fromId: 'bp-data-lake',
      toId: 'edge',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
    },
  ];
}

/**
 * Default animation steps based on PowerPoint slides.
 * 8 animation steps as specified:
 * 1. Shopfloor layer with device icons
 * 2. Shopfloor systems added
 * 3. DSP layer (blue) with Edge container, "On Premise" label
 * 4. Edge function icons
 * 5. Arrows from Edge to all Shopfloor icons (bidirectional)
 * 6. Shopfloor Dashboard and Management Cockpit with arrows to Edge, "Cloud" label
 * 7. Business Process layer with SAP Shopfloor → Edge arrow
 * 8. Remaining BP components with arrows to Edge
 */
export function createDefaultSteps(): StepConfig[] {
  return [
    // Step 1: Shopfloor layer with device icons only
    {
      id: 'step-1',
      label: '',
      visibleContainerIds: [
        'layer-shopfloor',
        'label-shopfloor',
        'shopfloor-devices-group',
        'shopfloor-device-1',
        'shopfloor-device-2',
        'shopfloor-device-3',
        'shopfloor-device-4',
        'shopfloor-device-5',
        'shopfloor-device-6',
      ],
      highlightedContainerIds: [],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
    },

    // Step 2: Shopfloor systems added
    {
      id: 'step-2',
      label: '',
      visibleContainerIds: [
        'layer-shopfloor',
        'label-shopfloor',
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
      ],
      highlightedContainerIds: ['shopfloor-systems-group', 'shopfloor-system-bp', 'shopfloor-system-fts'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
    },

    // Step 3: DSP layer with Edge container
    {
      id: 'step-3',
      label: '',
      visibleContainerIds: [
        'layer-dsp',
        'layer-shopfloor',
        'label-dsp',
        'label-shopfloor',
        'dsp-label-onpremise',
        'edge',
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
      ],
      highlightedContainerIds: ['layer-dsp', 'edge'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
    },

    // Step 4: Edge function icons
    {
      id: 'step-4',
      label: '',
      visibleContainerIds: [
        'layer-dsp',
        'layer-shopfloor',
        'label-dsp',
        'label-shopfloor',
        'dsp-label-onpremise',
        'edge',
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
      ],
      highlightedContainerIds: ['edge'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
    },

    // Step 5: Arrows from Edge to all Shopfloor icons
    {
      id: 'step-5',
      label: '',
      visibleContainerIds: [
        'layer-dsp',
        'layer-shopfloor',
        'label-dsp',
        'label-shopfloor',
        'dsp-label-onpremise',
        'edge',
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
      ],
      highlightedContainerIds: [],
      visibleConnectionIds: [
        'conn-edge-systems',
        'conn-edge-device-1',
        'conn-edge-device-2',
        'conn-edge-device-3',
        'conn-edge-device-4',
        'conn-edge-device-5',
        'conn-edge-device-6',
      ],
      highlightedConnectionIds: [
        'conn-edge-systems',
        'conn-edge-device-1',
        'conn-edge-device-2',
        'conn-edge-device-3',
        'conn-edge-device-4',
        'conn-edge-device-5',
        'conn-edge-device-6',
      ],
    },

    // Step 6: Shopfloor Dashboard and Management Cockpit
    {
      id: 'step-6',
      label: '',
      visibleContainerIds: [
        'layer-dsp',
        'layer-shopfloor',
        'label-dsp',
        'label-shopfloor',
        'dsp-label-onpremise',
        'dsp-label-cloud',
        'ux',
        'edge',
        'management',
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
      ],
      highlightedContainerIds: ['ux', 'management'],
      visibleConnectionIds: [
        'conn-ux-edge',
        'conn-edge-management',
        'conn-edge-systems',
        'conn-edge-device-1',
        'conn-edge-device-2',
        'conn-edge-device-3',
        'conn-edge-device-4',
        'conn-edge-device-5',
        'conn-edge-device-6',
      ],
      highlightedConnectionIds: ['conn-ux-edge', 'conn-edge-management'],
    },

    // Step 7: Business Process layer with SAP Shopfloor
    {
      id: 'step-7',
      label: '',
      visibleContainerIds: [
        'layer-business',
        'layer-dsp',
        'layer-shopfloor',
        'label-business',
        'label-dsp',
        'label-shopfloor',
        'dsp-label-onpremise',
        'dsp-label-cloud',
        'bp-sap-shopfloor',
        'ux',
        'edge',
        'management',
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
      ],
      highlightedContainerIds: ['layer-business', 'bp-sap-shopfloor'],
      visibleConnectionIds: [
        'conn-ux-edge',
        'conn-edge-management',
        'conn-sap-edge',
        'conn-edge-systems',
        'conn-edge-device-1',
        'conn-edge-device-2',
        'conn-edge-device-3',
        'conn-edge-device-4',
        'conn-edge-device-5',
        'conn-edge-device-6',
      ],
      highlightedConnectionIds: ['conn-sap-edge'],
    },

    // Step 8: All remaining BP components
    {
      id: 'step-8',
      label: '',
      visibleContainerIds: [
        'layer-business',
        'layer-dsp',
        'layer-shopfloor',
        'label-business',
        'label-dsp',
        'label-shopfloor',
        'dsp-label-onpremise',
        'dsp-label-cloud',
        'bp-sap-shopfloor',
        'bp-cloud-apps',
        'bp-analytics',
        'bp-data-lake',
        'ux',
        'edge',
        'management',
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
      ],
      highlightedContainerIds: ['bp-cloud-apps', 'bp-analytics', 'bp-data-lake'],
      visibleConnectionIds: [
        'conn-ux-edge',
        'conn-edge-management',
        'conn-sap-edge',
        'conn-cloud-edge',
        'conn-analytics-edge',
        'conn-datalake-edge',
        'conn-edge-systems',
        'conn-edge-device-1',
        'conn-edge-device-2',
        'conn-edge-device-3',
        'conn-edge-device-4',
        'conn-edge-device-5',
        'conn-edge-device-6',
      ],
      highlightedConnectionIds: ['conn-cloud-edge', 'conn-analytics-edge', 'conn-datalake-edge'],
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
