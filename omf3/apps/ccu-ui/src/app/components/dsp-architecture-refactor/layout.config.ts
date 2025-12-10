/**
 * Layout configuration for refactored DSP Architecture component.
 * Based on existing dsp-architecture.config.ts with taller DSP layer for component view.
 */
import type { ContainerConfig, ConnectionConfig, StepConfig } from './types';
import type { IconKey } from '../../assets/icon-registry';

/** SVG viewBox dimensions - increased height for taller DSP layer */
export const VIEWBOX_WIDTH = 1200;
export const VIEWBOX_HEIGHT = 1060; // Increased to accommodate taller DSP layer

/** Layout constants */
export const LAYOUT = {
  // Title area
  TITLE_Y: 30,
  SUBTITLE_Y: 55,

  // Layer dimensions
  LAYER_HEIGHT: 260,
  LAYER_START_Y: 80,

  // Labels inside layers (left edge)
  LABEL_X: 10,
  LABEL_WIDTH: 90,

  // Business Process layer (top - white)
  BUSINESS_Y: 80,

  // DSP layer (middle - blue) - MUCH TALLER for component view
  DSP_LAYER_Y: 340,
  DSP_LAYER_HEIGHT: 460, // Increased from 260 to 460 for Edge component icons

  // Shopfloor layer (bottom - gray)
  SHOPFLOOR_Y: 800, // Adjusted: 80 + 260 + 460

  // Box dimensions
  BUSINESS_BOX_WIDTH: 200,
  BUSINESS_BOX_HEIGHT: 140,
  DSP_BOX_HEIGHT: 300, // Much taller for component icons

  // Margins and spacing
  CONTENT_START_X: 100,
  MARGIN_RIGHT: 30,
  CONTENT_WIDTH: 1090,
  BOX_GAP: 25,
};

/**
 * Create default containers matching existing DSP architecture
 */
export function createDefaultContainers(): ContainerConfig[] {
  const containers: ContainerConfig[] = [];

  // ========== LAYER BACKGROUNDS ==========

  // Business Process layer background (white)
  containers.push({
    id: 'layer-business',
    label: '',
    x: 0,
    y: LAYOUT.BUSINESS_Y,
    width: VIEWBOX_WIDTH,
    height: LAYOUT.LAYER_HEIGHT,
    type: 'layer',
    state: 'hidden',
    backgroundColor: '#ffffff',
    borderColor: 'rgba(22, 65, 148, 0.1)',
    isGroup: true,
    labelPosition: 'left',
  });

  // DSP layer background (blue) - TALLER
  containers.push({
    id: 'layer-dsp',
    label: '',
    x: 0,
    y: LAYOUT.DSP_LAYER_Y,
    width: VIEWBOX_WIDTH,
    height: LAYOUT.DSP_LAYER_HEIGHT,
    type: 'layer',
    state: 'hidden',
    backgroundColor: 'rgba(207, 230, 255, 0.5)',
    borderColor: 'rgba(22, 65, 148, 0.15)',
    isGroup: true,
    labelPosition: 'left',
  });

  // Shopfloor layer background (gray)
  containers.push({
    id: 'layer-shopfloor',
    label: '',
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

  // ========== DSP BOXES - Calculate dimensions first ==========
  const dspAvailableWidth = VIEWBOX_WIDTH - LAYOUT.CONTENT_START_X - LAYOUT.MARGIN_RIGHT;
  const dspBoxGap = 50;
  const uxBoxWidth = 175;
  const edgeBoxWidth = 480;
  const managementBoxWidth = dspAvailableWidth - uxBoxWidth - edgeBoxWidth - (dspBoxGap * 2);



  // ========== DSP BOXES ==========

  // SmartFactory Dashboard (UX) - No ORBIS logo, only dashboard icon
  containers.push({
    id: 'ux',
    label: '',
    x: LAYOUT.CONTENT_START_X,
    y: LAYOUT.DSP_LAYER_Y + 55,
    width: uxBoxWidth,
    height: LAYOUT.DSP_BOX_HEIGHT,
    type: 'ux',
    state: 'hidden',
    centerIconKey: 'ux-dashboard' as IconKey,
    borderColor: '#009681',
    backgroundColor: '#ffffff',
    labelPosition: 'top-center',
    fontSize: 16,
    url: '/dashboard',
  });

  // DSP Edge - Environment label as property
  containers.push({
    id: 'edge',
    label: '',
    x: LAYOUT.CONTENT_START_X + uxBoxWidth + dspBoxGap,
    y: LAYOUT.DSP_LAYER_Y + 55,
    width: edgeBoxWidth,
    height: LAYOUT.DSP_BOX_HEIGHT,
    type: 'dsp-edge',
    state: 'hidden',
    logoIconKey: 'logo-dsp' as IconKey,
    logoPosition: 'top-left',
    borderColor: '#009681',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    labelPosition: 'top-center',
    fontSize: 16,
    functionIcons: [
      { iconKey: 'edge-data-storage' as IconKey, size: 60 },
      { iconKey: 'edge-network' as IconKey, size: 60 },
      { iconKey: 'edge-digital-twin' as IconKey, size: 60 },
      { iconKey: 'edge-workflow' as IconKey, size: 60 },
      { iconKey: 'edge-analytics' as IconKey, size: 60 },
    ],
    url: '/edge',
    environmentLabel: 'On Premise',
  });

  // Management Cockpit - Environment label as property
  containers.push({
    id: 'management',
    label: '',
    x: LAYOUT.CONTENT_START_X + uxBoxWidth + dspBoxGap + edgeBoxWidth + dspBoxGap,
    y: LAYOUT.DSP_LAYER_Y + 55,
    width: managementBoxWidth,
    height: LAYOUT.DSP_BOX_HEIGHT,
    type: 'dsp-cloud',
    state: 'hidden',
    logoIconKey: 'logo-dsp' as IconKey,
    logoPosition: 'top-left',
    secondaryLogoIconKey: 'logo-azure' as IconKey,
    secondaryLogoPosition: 'top-right',
    borderColor: '#009681',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    labelPosition: 'top-center',
    fontSize: 16,
    functionIcons: [
      { iconKey: 'logo-distributed' as IconKey, size: 60 },
      { iconKey: 'shopfloor-it' as IconKey, size: 60 },
    ],
    url: '/management-cockpit',
    environmentLabel: 'Cloud',
  });

  // ========== BUSINESS BOXES ==========
  const businessAvailableWidth = VIEWBOX_WIDTH - LAYOUT.CONTENT_START_X - LAYOUT.MARGIN_RIGHT;
  const businessBoxCount = 4;
  const businessGap = 30;
  const businessBoxWidth = (businessAvailableWidth - (businessBoxCount - 1) * businessGap) / businessBoxCount;
  const businessBoxY = LAYOUT.BUSINESS_Y + 65;
  const businessStartX = LAYOUT.CONTENT_START_X;

  containers.push({
    id: 'erp-application',
    label: '',
    x: businessStartX,
    y: businessBoxY,
    width: businessBoxWidth,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    logoIconKey: 'erp-application' as IconKey,
    secondaryLogoIconKey: 'logo-sap' as IconKey,
    secondaryLogoPosition: 'top-right',
    borderColor: 'rgba(22, 65, 148, 0.25)',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 16,
  });

  containers.push({
    id: 'bp-cloud-apps',
    label: '',
    x: businessStartX + (businessBoxWidth + businessGap),
    y: businessBoxY,
    width: businessBoxWidth,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    logoIconKey: 'bp-cloud-apps' as IconKey,
    borderColor: 'rgba(22, 65, 148, 0.25)',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 16,
  });

  containers.push({
    id: 'bp-analytics',
    label: '',
    x: businessStartX + (businessBoxWidth + businessGap) * 2,
    y: businessBoxY,
    width: businessBoxWidth,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    logoIconKey: 'bp-analytics' as IconKey,
    secondaryLogoIconKey: 'logo-grafana' as IconKey,
    secondaryLogoPosition: 'top-right',
    borderColor: 'rgba(22, 65, 148, 0.25)',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 16,
  });

  containers.push({
    id: 'bp-data-lake',
    label: '',
    x: businessStartX + (businessBoxWidth + businessGap) * 3,
    y: businessBoxY,
    width: businessBoxWidth,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    logoIconKey: 'bp-data-lake' as IconKey,
    borderColor: 'rgba(22, 65, 148, 0.25)',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 16,
  });

  // ========== SHOPFLOOR CONTENT ==========
  const shopfloorAvailableWidth = VIEWBOX_WIDTH - LAYOUT.CONTENT_START_X - LAYOUT.MARGIN_RIGHT;
  const shopfloorGap = 30;
  const shopfloorGroupHeight = 165; // Increased for icon + label + group label below
  // Vertically center in shopfloor layer: equal spacing top and bottom
  const shopfloorGroupY = LAYOUT.SHOPFLOOR_Y + (LAYOUT.LAYER_HEIGHT - shopfloorGroupHeight) / 2;

  const systemsGroupWidth = 260;
  const devicesGroupWidth = shopfloorAvailableWidth - systemsGroupWidth - shopfloorGap;

  // Systems group - label inside container at bottom
  containers.push({
    id: 'shopfloor-systems-group',
    label: '',
    x: LAYOUT.CONTENT_START_X,
    y: shopfloorGroupY,
    width: systemsGroupWidth,
    height: shopfloorGroupHeight,
    type: 'shopfloor-group',
    state: 'hidden',
    backgroundColor: 'transparent',
    borderColor: 'rgba(0, 0, 0, 0.08)',
    labelPosition: 'bottom',  // Changed from 'bottom-center' to 'bottom' for inside positioning
    fontSize: 14,
    isGroup: true,
  });

  // Systems - 2 boxes horizontally in ONE row
  const systemBoxWidth = (systemsGroupWidth - 20 - 15) / 2; // 2 boxes side by side
  const systemBoxHeight = 120; // Taller for square icon + label
  const systemBoxGap = 15;

  containers.push({
    id: 'shopfloor-system-bp',
    label: '',
    x: LAYOUT.CONTENT_START_X + 10,
    y: shopfloorGroupY + 10,
    width: systemBoxWidth,
    height: systemBoxHeight,
    type: 'device',  // Changed from 'shopfloor' to 'device' for proper icon display
    state: 'hidden',
    logoIconKey: 'shopfloor-systems' as IconKey,
    borderColor: 'rgba(0, 0, 0, 0.12)',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 13,
  });

  containers.push({
    id: 'shopfloor-system-fts',
    label: '',
    x: LAYOUT.CONTENT_START_X + 10 + systemBoxWidth + systemBoxGap,
    y: shopfloorGroupY + 10,
    width: systemBoxWidth,
    height: systemBoxHeight,
    type: 'device',  // Changed from 'shopfloor' to 'device' for proper icon display
    state: 'hidden',
    logoIconKey: 'shopfloor-fts' as IconKey,
    borderColor: 'rgba(0, 0, 0, 0.12)',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 13,
  });

  // Devices group - label inside container at bottom
  containers.push({
    id: 'shopfloor-devices-group',
    label: '',
    x: LAYOUT.CONTENT_START_X + systemsGroupWidth + shopfloorGap,
    y: shopfloorGroupY,
    width: devicesGroupWidth,
    height: shopfloorGroupHeight,
    type: 'shopfloor-group',
    state: 'normal',
    backgroundColor: 'transparent',
    borderColor: 'rgba(0, 0, 0, 0.08)',
    labelPosition: 'bottom',  // Changed from 'bottom-center' to 'bottom' for inside positioning
    fontSize: 14,
    isGroup: true,
  });

  // Devices - 6 boxes in ONE row
  const deviceBoxWidth = (devicesGroupWidth - 20 - 5 * 12) / 6; // 6 boxes in 1 row
  const deviceBoxHeight = 120; // Taller for square icon + label
  const deviceBoxGap = 12;
  const devicesStartX = LAYOUT.CONTENT_START_X + systemsGroupWidth + shopfloorGap + 10;

  const deviceIcons: IconKey[] = [
    'device-mill' as IconKey,
    'device-drill' as IconKey,
    'device-aiqs' as IconKey,
    'device-hbw' as IconKey,
    'device-dps' as IconKey,
    'device-chrg' as IconKey,
  ];

  // Single row of 6 devices
  for (let i = 0; i < 6; i++) {
    containers.push({
      id: `shopfloor-device-${i + 1}`,
      label: '',
      x: devicesStartX + i * (deviceBoxWidth + deviceBoxGap),
      y: shopfloorGroupY + 10,
      width: deviceBoxWidth,
      height: deviceBoxHeight,
      type: 'device',
      state: 'normal',
      logoIconKey: deviceIcons[i],
      borderColor: 'rgba(0, 0, 0, 0.12)',
      backgroundColor: '#ffffff',
      labelPosition: 'bottom-center',
      fontSize: 12,
    });
  }

  return containers;
}

/**
 * Create default connections
 */
export function createDefaultConnections(): ConnectionConfig[] {
  return [
    // UX to Edge
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
    // Edge to Management
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
    // Edge to Shopfloor Systems
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
    // Edge to Shopfloor Devices
    ...Array.from({ length: 6 }, (_, i) => ({
      id: `conn-edge-device-${i + 1}`,
      fromId: 'edge',
      toId: `shopfloor-device-${i + 1}`,
      fromSide: 'bottom' as const,
      toSide: 'top' as const,
      state: 'hidden' as const,
      hasArrow: true,
      bidirectional: true,
    })),
    // Business to Edge
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
      bidirectional: true,
    },
    {
      id: 'conn-analytics-edge',
      fromId: 'bp-analytics',
      toId: 'edge',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    {
      id: 'conn-datalake-edge',
      fromId: 'bp-data-lake',
      toId: 'edge',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
  ];
}

/**
 * Create animation steps as requested: 1, 2, 3, 7, 10, and final step 4 (complete overview)
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
    // Step 1: Shopfloor Devices only
    {
      id: 'step-1',
      label: $localize`:@@dspArchStep1:Shopfloor Devices`,
      description: $localize`:@@dspArchStep1Desc:DSP connects heterogeneous devices in the shopfloor without interfering with machine logic.`,
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
      highlightedContainerIds: [
        'shopfloor-devices-group',
        'shopfloor-device-1',
        'shopfloor-device-2',
        'shopfloor-device-3',
        'shopfloor-device-4',
        'shopfloor-device-5',
        'shopfloor-device-6',
      ],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
    },

    // Step 2: Shopfloor Systems + Devices
    {
      id: 'step-2',
      label: $localize`:@@dspArchStep2:Shopfloor Systems`,
      description: $localize`:@@dspArchStep2Desc:DSP integrates complete systems like AGVs, warehouses, and custom controls.`,
      visibleContainerIds: baseShopfloorContainers,
      highlightedContainerIds: [
        'shopfloor-systems-group',
        'shopfloor-system-bp',
        'shopfloor-system-fts',
      ],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
    },

    // Step 3: DSP Edge Core appears
    {
      id: 'step-3',
      label: $localize`:@@dspArchStep3:DSP Edge Core`,
      description: $localize`:@@dspArchStep3Desc:The DSP Edge is the local runtime for connectivity, process logic, digital twin and data processing.`,
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

    // Step 7: Analytics / AI Preparation (from original sequence)
    {
      id: 'step-7',
      label: $localize`:@@dspArchStep7:Analytics & AI`,
      description: $localize`:@@dspArchStep7Desc:Real-time KPIs, OEE calculation, and ML preparation at the edge.`,
      visibleContainerIds: [
        'layer-dsp',
        'dsp-label-onpremise',
        'edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['edge'],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: [],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-analytics'],
    },

    // Step 10: Business Integration (from original sequence)
    {
      id: 'step-10',
      label: $localize`:@@dspArchStep10:Business Integration`,
      description: $localize`:@@dspArchStep10Desc:DSP connects shopfloor events with ERP processes, cloud analytics, and data lakes.`,
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
      highlightedContainerIds: [
        'layer-business',
        'erp-application',
        'bp-cloud-apps',
        'bp-analytics',
        'bp-data-lake',
      ],
      visibleConnectionIds: [
        'conn-edge-management',
        'conn-erp-edge',
        'conn-cloud-edge',
        'conn-analytics-edge',
        'conn-datalake-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [
        'conn-erp-edge',
        'conn-cloud-edge',
        'conn-analytics-edge',
        'conn-datalake-edge',
      ],
      showFunctionIcons: true,
    },

    // Step 4: Complete Overview - everything visible, nothing highlighted
    {
      id: 'step-4',
      label: $localize`:@@dspArchStep4Complete:Complete DSP Architecture`,
      description: $localize`:@@dspArchStep4CompleteDesc:Complete overview of the DSP architecture with all layers, connections, and components.`,
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
      highlightedContainerIds: [], // Nothing highlighted as requested
      visibleConnectionIds: [
        'conn-ux-edge',
        'conn-edge-management',
        'conn-erp-edge',
        'conn-cloud-edge',
        'conn-analytics-edge',
        'conn-datalake-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [], // No connections highlighted
      showFunctionIcons: true,
    },
  ];
}

/**
 * Create complete diagram configuration
 */
export function createDiagramConfig(): { containers: ContainerConfig[]; connections: ConnectionConfig[]; steps: StepConfig[] } {
  return {
    containers: createDefaultContainers(),
    connections: createDefaultConnections(),
    steps: createDefaultSteps(),
  };
}
