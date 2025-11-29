/**
 * Configuration and layout data for the DSP Architecture diagram.
 * Defines default containers, connections, and animation steps based on PowerPoint reference.
 */
import type { ContainerConfig, ConnectionConfig, StepConfig, DiagramConfig } from './dsp-architecture.types';

/** SVG viewBox dimensions */
export const VIEWBOX_WIDTH = 1200;
export const VIEWBOX_HEIGHT = 700;

/** Layout constants */
export const LAYOUT = {
  // Title area
  TITLE_Y: 30,
  SUBTITLE_Y: 55,

  // Business Processes layer
  BUSINESS_Y: 90,
  BUSINESS_HEIGHT: 80,
  BUSINESS_BOX_WIDTH: 140,
  BUSINESS_BOX_HEIGHT: 60,

  // DSP layer
  DSP_LAYER_Y: 220,
  DSP_LAYER_HEIGHT: 180,
  DSP_BOX_Y: 260,
  DSP_BOX_HEIGHT: 120,

  // Shopfloor layer
  SHOPFLOOR_Y: 520,
  SHOPFLOOR_HEIGHT: 100,

  // Margins and spacing
  MARGIN_LEFT: 180,
  MARGIN_RIGHT: 50,
  CONTENT_WIDTH: 970,
  BOX_GAP: 20,
};

/**
 * Default containers for the DSP Architecture diagram.
 * Container IDs are used for connections and animation steps.
 */
export function createDefaultContainers(): ContainerConfig[] {
  const containers: ContainerConfig[] = [];

  // ========== LABELS (always visible) ==========
  containers.push({
    id: 'label-business',
    label: '',  // Will be set via i18n
    x: 20,
    y: LAYOUT.BUSINESS_Y + 20,
    width: 140,
    height: 60,
    type: 'label',
    state: 'normal',
    fontSize: 14,
  });

  containers.push({
    id: 'label-dsp',
    label: '',
    x: 20,
    y: LAYOUT.DSP_LAYER_Y + 10,
    width: 140,
    height: 30,
    type: 'label',
    state: 'normal',
    fontSize: 14,
  });

  containers.push({
    id: 'label-shopfloor',
    label: '',
    x: 20,
    y: LAYOUT.SHOPFLOOR_Y + 20,
    width: 140,
    height: 60,
    type: 'label',
    state: 'normal',
    fontSize: 14,
  });

  // ========== DSP LAYER BACKGROUND ==========
  containers.push({
    id: 'dsp-layer-bg',
    x: LAYOUT.MARGIN_LEFT - 10,
    y: LAYOUT.DSP_LAYER_Y,
    width: LAYOUT.CONTENT_WIDTH + 20,
    height: LAYOUT.DSP_LAYER_HEIGHT,
    type: 'layer',
    state: 'hidden',
    backgroundColor: 'rgba(207, 230, 255, 0.3)',
    borderColor: 'transparent',
    isGroup: true,
  });

  // ========== DSP LAYER LABELS ==========
  containers.push({
    id: 'dsp-label-onpremise',
    label: '',  // "On Premise"
    x: LAYOUT.MARGIN_LEFT + 160,
    y: LAYOUT.DSP_LAYER_Y + 10,
    width: 100,
    height: 20,
    type: 'label',
    state: 'hidden',
    fontSize: 12,
  });

  containers.push({
    id: 'dsp-label-cloud',
    label: '',  // "Cloud"
    x: LAYOUT.MARGIN_LEFT + LAYOUT.CONTENT_WIDTH - 200,
    y: LAYOUT.DSP_LAYER_Y + 10,
    width: 60,
    height: 20,
    type: 'label',
    state: 'hidden',
    fontSize: 12,
  });

  // ========== UX BOX (SmartFactory Dashboard) ==========
  containers.push({
    id: 'ux',
    label: '',  // "SmartFactory Dashboard" or just icon
    x: LAYOUT.MARGIN_LEFT - 70,
    y: LAYOUT.DSP_BOX_Y + 10,
    width: 100,
    height: 100,
    type: 'ux',
    state: 'hidden',
    logoIconKey: 'DSP_UX_MONITOR',
    borderColor: 'rgba(31, 84, 178, 0.3)',
    backgroundColor: '#ffffff',
  });

  // ========== DSP EDGE BOX ==========
  containers.push({
    id: 'edge',
    label: '',  // "EDGE"
    x: LAYOUT.MARGIN_LEFT + 80,
    y: LAYOUT.DSP_BOX_Y,
    width: 400,
    height: LAYOUT.DSP_BOX_HEIGHT,
    type: 'dsp-edge',
    state: 'hidden',
    logoIconKey: 'DSP_LOGO_ORBIS',
    logoPosition: 'top-left',
    borderColor: '#009B77',
    backgroundColor: 'rgba(0, 155, 119, 0.03)',
    functionIcons: [
      { iconKey: 'DSP_EDGE_DATABASE', size: 40 },
      { iconKey: 'DSP_EDGE_DIGITAL_TWIN', size: 40 },
      { iconKey: 'DSP_EDGE_NETWORK', size: 40 },
      { iconKey: 'DSP_EDGE_WORKFLOW', size: 40 },
    ],
  });

  // ========== DSP MANAGEMENT COCKPIT BOX ==========
  containers.push({
    id: 'management',
    label: '',  // "Management Cockpit"
    x: LAYOUT.MARGIN_LEFT + 520,
    y: LAYOUT.DSP_BOX_Y,
    width: 280,
    height: LAYOUT.DSP_BOX_HEIGHT,
    type: 'dsp-cloud',
    state: 'hidden',
    logoIconKey: 'DSP_LOGO_ORBIS',
    logoPosition: 'top-left',
    secondaryLogoIconKey: 'DSP_LOGO_AZURE',
    secondaryLogoPosition: 'top-right',
    borderColor: '#0078D4',
    backgroundColor: 'rgba(0, 120, 212, 0.03)',
  });

  // ========== BUSINESS PROCESSES ==========
  const businessStartX = LAYOUT.MARGIN_LEFT + 50;
  const businessBoxWidth = 150;
  const businessGap = 30;

  containers.push({
    id: 'bp-sap-shopfloor',
    label: '',  // "SAP Shopfloor"
    x: businessStartX,
    y: LAYOUT.BUSINESS_Y + 10,
    width: businessBoxWidth,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    logoIconKey: 'DSP_BUSINESS_SAP',
    logoPosition: 'top-left',
    borderColor: 'rgba(31, 84, 178, 0.25)',
    backgroundColor: '#fdfefe',
  });

  containers.push({
    id: 'bp-cloud-apps',
    label: '',  // "Cloud Anwendungen"
    x: businessStartX + businessBoxWidth + businessGap,
    y: LAYOUT.BUSINESS_Y + 10,
    width: businessBoxWidth,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    borderColor: 'rgba(31, 84, 178, 0.25)',
    backgroundColor: '#fdfefe',
  });

  containers.push({
    id: 'bp-analytics',
    label: '',  // "Analytische Anwendungen"
    x: businessStartX + (businessBoxWidth + businessGap) * 2,
    y: LAYOUT.BUSINESS_Y + 10,
    width: businessBoxWidth + 20,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    borderColor: 'rgba(31, 84, 178, 0.25)',
    backgroundColor: '#fdfefe',
  });

  containers.push({
    id: 'bp-data-lake',
    label: '',  // "Data Lake"
    x: businessStartX + (businessBoxWidth + businessGap) * 3 + 20,
    y: LAYOUT.BUSINESS_Y + 10,
    width: businessBoxWidth - 20,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    borderColor: 'rgba(31, 84, 178, 0.25)',
    backgroundColor: '#fdfefe',
  });

  // ========== SHOPFLOOR LAYER ==========
  containers.push({
    id: 'shopfloor-strip',
    x: LAYOUT.MARGIN_LEFT,
    y: LAYOUT.SHOPFLOOR_Y,
    width: LAYOUT.CONTENT_WIDTH,
    height: LAYOUT.SHOPFLOOR_HEIGHT,
    type: 'shopfloor',
    state: 'normal',
    borderColor: 'rgba(31, 54, 91, 0.12)',
    backgroundColor: 'linear-gradient(180deg, #fbfbfd 0%, #f1f3f7 100%)',
    isGroup: true,
  });

  // Shopfloor Systems box
  containers.push({
    id: 'shopfloor-systems',
    label: '',  // "Shopfloor Systeme"
    x: LAYOUT.MARGIN_LEFT + 20,
    y: LAYOUT.SHOPFLOOR_Y + 30,
    width: 160,
    height: 50,
    type: 'shopfloor',
    state: 'normal',
    borderColor: 'rgba(31, 84, 178, 0.2)',
    backgroundColor: '#ffffff',
  });

  // Shopfloor devices
  const deviceStartX = LAYOUT.MARGIN_LEFT + 200;
  const deviceWidth = 60;
  const deviceGap = 15;

  const deviceIcons = ['device-plc', 'device-plc-2', 'device-scanner', 'device-printer'];
  deviceIcons.forEach((iconId, index) => {
    containers.push({
      id: `shopfloor-device-${index + 1}`,
      x: deviceStartX + (deviceWidth + deviceGap) * index,
      y: LAYOUT.SHOPFLOOR_Y + 25,
      width: deviceWidth,
      height: 60,
      type: 'device',
      state: 'normal',
      logoIconKey: `SHOPFLOOR_${iconId.toUpperCase().replace('-', '_')}`,
      borderColor: 'rgba(31, 84, 178, 0.2)',
      backgroundColor: '#ffffff',
    });
  });

  // Geräte label
  containers.push({
    id: 'shopfloor-devices-label',
    label: '',  // "Geräte"
    x: LAYOUT.MARGIN_LEFT + LAYOUT.CONTENT_WIDTH - 100,
    y: LAYOUT.SHOPFLOOR_Y + 45,
    width: 80,
    height: 20,
    type: 'label',
    state: 'normal',
    fontSize: 12,
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
      id: 'conn-cloud-management',
      fromId: 'bp-cloud-apps',
      toId: 'management',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
    },
    {
      id: 'conn-analytics-management',
      fromId: 'bp-analytics',
      toId: 'management',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
    },
    {
      id: 'conn-datalake-management',
      fromId: 'bp-data-lake',
      toId: 'management',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
    },

    // DSP to Shopfloor connections
    {
      id: 'conn-edge-shopfloor',
      fromId: 'edge',
      toId: 'shopfloor-strip',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
  ];
}

/**
 * Default animation steps based on PowerPoint slides.
 * Order: 1, 2, 4, 5, 6, 3 (as specified)
 */
export function createDefaultSteps(): StepConfig[] {
  return [
    // Step 1: Shopfloor Overview (Screenshot 1)
    {
      id: 'step-1',
      label: '',  // Will be set via i18n
      visibleContainerIds: [
        'label-business',
        'label-shopfloor',
        'shopfloor-strip',
        'shopfloor-systems',
        'shopfloor-device-1',
        'shopfloor-device-2',
        'shopfloor-device-3',
        'shopfloor-device-4',
        'shopfloor-devices-label',
      ],
      highlightedContainerIds: [],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
    },

    // Step 2: DSP Layer appears (Screenshot 2)
    {
      id: 'step-2',
      label: '',
      visibleContainerIds: [
        'label-business',
        'label-dsp',
        'label-shopfloor',
        'dsp-layer-bg',
        'dsp-label-onpremise',
        'dsp-label-cloud',
        'edge',
        'management',
        'shopfloor-strip',
        'shopfloor-systems',
        'shopfloor-device-1',
        'shopfloor-device-2',
        'shopfloor-device-3',
        'shopfloor-device-4',
        'shopfloor-devices-label',
      ],
      highlightedContainerIds: ['edge', 'management'],
      visibleConnectionIds: ['conn-edge-management'],
      highlightedConnectionIds: ['conn-edge-management'],
    },

    // Step 3: Edge with more function icons (Screenshot 4)
    {
      id: 'step-3',
      label: '',
      visibleContainerIds: [
        'label-business',
        'label-dsp',
        'label-shopfloor',
        'dsp-layer-bg',
        'dsp-label-onpremise',
        'dsp-label-cloud',
        'edge',
        'management',
        'shopfloor-strip',
        'shopfloor-systems',
        'shopfloor-device-1',
        'shopfloor-device-2',
        'shopfloor-device-3',
        'shopfloor-device-4',
        'shopfloor-devices-label',
      ],
      highlightedContainerIds: ['edge'],
      visibleConnectionIds: ['conn-edge-management'],
      highlightedConnectionIds: [],
    },

    // Step 4: SAP Shopfloor appears with connection (Screenshot 5)
    {
      id: 'step-4',
      label: '',
      visibleContainerIds: [
        'label-business',
        'label-dsp',
        'label-shopfloor',
        'dsp-layer-bg',
        'dsp-label-onpremise',
        'dsp-label-cloud',
        'edge',
        'management',
        'bp-sap-shopfloor',
        'shopfloor-strip',
        'shopfloor-systems',
        'shopfloor-device-1',
        'shopfloor-device-2',
        'shopfloor-device-3',
        'shopfloor-device-4',
        'shopfloor-devices-label',
      ],
      highlightedContainerIds: ['bp-sap-shopfloor'],
      visibleConnectionIds: ['conn-edge-management', 'conn-sap-edge', 'conn-edge-shopfloor'],
      highlightedConnectionIds: ['conn-sap-edge', 'conn-edge-shopfloor'],
    },

    // Step 5: More business processes appear (Screenshot 6)
    {
      id: 'step-5',
      label: '',
      visibleContainerIds: [
        'label-business',
        'label-dsp',
        'label-shopfloor',
        'dsp-layer-bg',
        'dsp-label-onpremise',
        'dsp-label-cloud',
        'edge',
        'management',
        'bp-sap-shopfloor',
        'bp-cloud-apps',
        'bp-analytics',
        'bp-data-lake',
        'shopfloor-strip',
        'shopfloor-systems',
        'shopfloor-device-1',
        'shopfloor-device-2',
        'shopfloor-device-3',
        'shopfloor-device-4',
        'shopfloor-devices-label',
      ],
      highlightedContainerIds: ['bp-cloud-apps', 'bp-analytics', 'bp-data-lake'],
      visibleConnectionIds: [
        'conn-edge-management',
        'conn-sap-edge',
        'conn-edge-shopfloor',
        'conn-cloud-management',
        'conn-analytics-management',
        'conn-datalake-management',
      ],
      highlightedConnectionIds: ['conn-cloud-management', 'conn-analytics-management', 'conn-datalake-management'],
    },

    // Step 6: Final state with UX (Screenshot 3)
    {
      id: 'step-6',
      label: '',
      visibleContainerIds: [
        'label-business',
        'label-dsp',
        'label-shopfloor',
        'dsp-layer-bg',
        'dsp-label-onpremise',
        'dsp-label-cloud',
        'ux',
        'edge',
        'management',
        'bp-sap-shopfloor',
        'bp-cloud-apps',
        'bp-analytics',
        'bp-data-lake',
        'shopfloor-strip',
        'shopfloor-systems',
        'shopfloor-device-1',
        'shopfloor-device-2',
        'shopfloor-device-3',
        'shopfloor-device-4',
        'shopfloor-devices-label',
      ],
      highlightedContainerIds: ['ux'],
      visibleConnectionIds: [
        'conn-ux-edge',
        'conn-edge-management',
        'conn-sap-edge',
        'conn-edge-shopfloor',
        'conn-cloud-management',
        'conn-analytics-management',
        'conn-datalake-management',
      ],
      highlightedConnectionIds: ['conn-ux-edge'],
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
