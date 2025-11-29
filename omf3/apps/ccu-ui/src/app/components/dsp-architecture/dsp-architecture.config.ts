/**
 * Configuration and layout data for the DSP Architecture diagram.
 * Defines default containers, connections, and animation steps based on PowerPoint reference.
 */
import type { ContainerConfig, ConnectionConfig, StepConfig, DiagramConfig } from './dsp-architecture.types';
import type { IconKey } from '../../assets/icon-registry';

/** SVG viewBox dimensions - increased height for better screen fit */
export const VIEWBOX_WIDTH = 1200;
export const VIEWBOX_HEIGHT = 850;

/** Layout constants - three equal-height layers with increased size */
export const LAYOUT = {
  // Title area
  TITLE_Y: 30,
  SUBTITLE_Y: 55,

  // Layer dimensions (equal height for all three - increased)
  LAYER_HEIGHT: 230,
  LAYER_START_Y: 80,

  // Labels inside layers (left edge)
  LABEL_X: 10,
  LABEL_WIDTH: 100,

  // Business Process layer (top - white)
  BUSINESS_Y: 80,

  // DSP layer (middle - blue)
  DSP_LAYER_Y: 310,

  // Shopfloor layer (bottom - gray)
  SHOPFLOOR_Y: 540,

  // Box dimensions
  BUSINESS_BOX_WIDTH: 200,
  BUSINESS_BOX_HEIGHT: 130,
  DSP_BOX_HEIGHT: 150,

  // Margins and spacing (content starts after label area)
  CONTENT_START_X: 120,
  MARGIN_RIGHT: 50,
  CONTENT_WIDTH: 1070,
  BOX_GAP: 30,
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
    borderColor: 'rgba(31, 84, 178, 0.1)',
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
    borderColor: 'rgba(31, 84, 178, 0.15)',
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
    x: LAYOUT.CONTENT_START_X + 180,
    y: LAYOUT.DSP_LAYER_Y + 12,
    width: 100,
    height: 20,
    type: 'label',
    state: 'hidden',
    fontSize: 12,
  });

  containers.push({
    id: 'dsp-label-cloud',
    label: '',  // "Cloud"
    x: LAYOUT.CONTENT_START_X + 780,
    y: LAYOUT.DSP_LAYER_Y + 12,
    width: 60,
    height: 20,
    type: 'label',
    state: 'hidden',
    fontSize: 12,
  });

  // ========== DSP UX BOX (Smartfactory Dashboard) - larger box, two-line label ==========
  containers.push({
    id: 'ux',
    label: '',  // "Smartfactory\nDashboard" - two-line label at top, centered
    x: LAYOUT.CONTENT_START_X,
    y: LAYOUT.DSP_LAYER_Y + 40,
    width: 140,
    height: LAYOUT.DSP_BOX_HEIGHT,
    type: 'ux',
    state: 'hidden',
    logoIconKey: 'ux-dashboard' as IconKey,  // dsp/dashboard.svg
    borderColor: 'rgba(31, 84, 178, 0.3)',
    backgroundColor: '#ffffff',
    labelPosition: 'top-center',
    url: '/dashboard',  // Default URL for Smartfactory Dashboard
  });

  // ========== DSP EDGE BOX - equal spacing with other boxes ==========
  const dspBoxGap = 40;  // Equal spacing between all DSP boxes
  containers.push({
    id: 'edge',
    label: '',  // "EDGE" - label at top center
    x: LAYOUT.CONTENT_START_X + 140 + dspBoxGap,
    y: LAYOUT.DSP_LAYER_Y + 40,
    width: 420,
    height: LAYOUT.DSP_BOX_HEIGHT,
    type: 'dsp-edge',
    state: 'hidden',
    logoIconKey: 'logo-dsp' as IconKey,
    logoPosition: 'top-left',
    borderColor: '#009B77',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    labelPosition: 'top-center',  // Changed to top-center
    functionIcons: [
      { iconKey: 'edge-data-storage' as IconKey, size: 40 },
      { iconKey: 'edge-digital-twin' as IconKey, size: 40 },
      { iconKey: 'edge-network' as IconKey, size: 40 },
      { iconKey: 'edge-workflow' as IconKey, size: 40 },
    ],
    url: '/edge',  // Default URL for DSP Edge
  });

  // ========== DSP MANAGEMENT COCKPIT BOX - two icons ==========
  containers.push({
    id: 'management',
    label: '',  // "Management Cockpit" - label at top center
    x: LAYOUT.CONTENT_START_X + 140 + dspBoxGap + 420 + dspBoxGap,
    y: LAYOUT.DSP_LAYER_Y + 40,
    width: 280,
    height: LAYOUT.DSP_BOX_HEIGHT,
    type: 'dsp-cloud',
    state: 'hidden',
    logoIconKey: 'logo-distributed' as IconKey,  // orbis/distributed.svg
    logoPosition: 'top-left',
    secondaryLogoIconKey: 'shopfloor-it' as IconKey,  // shopfloor/information-technology.svg
    secondaryLogoPosition: 'top-right',
    borderColor: '#0078D4',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    labelPosition: 'top-center',  // Changed to top-center
    url: '/management-cockpit',  // Default URL for Management Cockpit
  });

  // ========== BUSINESS PROCESSES (equal-sized boxes, labels at top centered, with icons) ==========
  const businessAvailableWidth = VIEWBOX_WIDTH - LAYOUT.CONTENT_START_X - 30;
  const businessBoxCount = 4;
  const businessGap = 20;
  const businessBoxWidth = (businessAvailableWidth - (businessBoxCount - 1) * businessGap) / businessBoxCount;
  const businessBoxY = LAYOUT.BUSINESS_Y + 50;
  const businessStartX = LAYOUT.CONTENT_START_X;

  containers.push({
    id: 'bp-sap-shopfloor',
    label: '',  // "Shopfloor" - label at top center
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
    labelPosition: 'top-center',
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
    borderColor: 'rgba(31, 84, 178, 0.25)',
    backgroundColor: '#ffffff',
    labelPosition: 'top-center',
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
    borderColor: 'rgba(31, 84, 178, 0.25)',
    backgroundColor: '#ffffff',
    labelPosition: 'top-center',
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
    borderColor: 'rgba(31, 84, 178, 0.25)',
    backgroundColor: '#ffffff',
    labelPosition: 'top-center',
  });

  // ========== SHOPFLOOR LAYER CONTENT ==========

  // Shopfloor Systeme container (left) - label at bottom, horizontally centered
  const shopfloorGroupHeight = 170;
  const shopfloorGroupY = LAYOUT.SHOPFLOOR_Y + 30;

  containers.push({
    id: 'shopfloor-systems-group',
    label: '',  // "Systeme" - label at bottom center
    x: LAYOUT.CONTENT_START_X,
    y: shopfloorGroupY,
    width: 280,
    height: shopfloorGroupHeight,
    type: 'shopfloor',
    state: 'hidden',
    borderColor: 'rgba(31, 84, 178, 0.2)',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',  // Changed to bottom-center
  });

  // Shopfloor System icons with labels below - arrows should go to these icons
  const systemIconY = shopfloorGroupY + 20;
  const systemIconWidth = 90;
  const systemIconHeight = 100;

  containers.push({
    id: 'shopfloor-system-bp',
    label: 'FTS',  // Label below icon
    x: LAYOUT.CONTENT_START_X + 30,
    y: systemIconY,
    width: systemIconWidth,
    height: systemIconHeight,
    type: 'device',
    state: 'hidden',
    logoIconKey: 'shopfloor-fts' as IconKey,
    borderColor: 'rgba(31, 84, 178, 0.1)',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom',
  });

  containers.push({
    id: 'shopfloor-system-fts',
    label: 'MES',  // Label below icon
    x: LAYOUT.CONTENT_START_X + 30 + systemIconWidth + 30,
    y: systemIconY,
    width: systemIconWidth,
    height: systemIconHeight,
    type: 'device',
    state: 'hidden',
    logoIconKey: 'shopfloor-mes' as IconKey,
    borderColor: 'rgba(31, 84, 178, 0.1)',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom',
  });

  // Geräte container (right) - label at bottom, horizontally centered
  containers.push({
    id: 'shopfloor-devices-group',
    label: '',  // "Geräte" - label at bottom center
    x: LAYOUT.CONTENT_START_X + 310,
    y: shopfloorGroupY,
    width: 580,
    height: shopfloorGroupHeight,
    type: 'shopfloor',
    state: 'normal',
    borderColor: 'rgba(31, 84, 178, 0.2)',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',  // Changed to bottom-center
  });

  // Device icons with labels below (DRILL, HBW, MILL, AIQS, DPS, CHRG) using shopfloor/*.svg
  const deviceStartX = LAYOUT.CONTENT_START_X + 330;
  const deviceWidth = 80;
  const deviceGap = 10;
  const deviceY = shopfloorGroupY + 15;
  const deviceHeight = 110;

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
      borderColor: 'rgba(31, 84, 178, 0.1)',
      backgroundColor: '#ffffff',
      labelPosition: 'bottom',
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

    // Step 4: Edge function icons (icons are always shown in edge container)
    {
      id: 'step-4',
      label: '',
      visibleContainerIds: [
        'layer-dsp',
        'layer-shopfloor',
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
        'conn-edge-system-bp',
        'conn-edge-system-fts',
        'conn-edge-device-1',
        'conn-edge-device-2',
        'conn-edge-device-3',
        'conn-edge-device-4',
        'conn-edge-device-5',
        'conn-edge-device-6',
      ],
      highlightedConnectionIds: [
        'conn-edge-system-bp',
        'conn-edge-system-fts',
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
        'conn-edge-system-bp',
        'conn-edge-system-fts',
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
        'conn-edge-system-bp',
        'conn-edge-system-fts',
        'conn-edge-device-1',
        'conn-edge-device-2',
        'conn-edge-device-3',
        'conn-edge-device-4',
        'conn-edge-device-5',
        'conn-edge-device-6',
      ],
      highlightedConnectionIds: ['conn-sap-edge'],
    },

    // Step 8: All remaining BP components - NO HIGHLIGHTING at end of animation
    {
      id: 'step-8',
      label: '',
      visibleContainerIds: [
        'layer-business',
        'layer-dsp',
        'layer-shopfloor',
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
      highlightedContainerIds: [],  // No highlighting at end
      visibleConnectionIds: [
        'conn-ux-edge',
        'conn-edge-management',
        'conn-sap-edge',
        'conn-cloud-edge',
        'conn-analytics-edge',
        'conn-datalake-edge',
        'conn-edge-system-bp',
        'conn-edge-system-fts',
        'conn-edge-device-1',
        'conn-edge-device-2',
        'conn-edge-device-3',
        'conn-edge-device-4',
        'conn-edge-device-5',
        'conn-edge-device-6',
      ],
      highlightedConnectionIds: [],  // No highlighting at end
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
