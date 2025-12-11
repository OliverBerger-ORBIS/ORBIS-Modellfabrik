/**
 * Layout configuration for refactored DSP Architecture component.
 * Based on existing dsp-architecture.config.ts with taller DSP layer for component view.
 */
import type { ContainerConfig, ConnectionConfig, StepConfig } from './types';
import type { IconKey } from '../../assets/icon-registry';

/** SVG viewBox dimensions - increased height for taller DSP layer */
export const VIEWBOX_WIDTH = 1200;
export const VIEWBOX_HEIGHT = 1140; // Increased to accommodate taller DSP layer (880 + 260)

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
  DSP_LAYER_HEIGHT: 540, // Increased from 520 to 540 for more space

  // Shopfloor layer (bottom - gray)
  SHOPFLOOR_Y: 880, // Adjusted: 80 + 260 + 540

  // Box dimensions
  BUSINESS_BOX_WIDTH: 200,
  BUSINESS_BOX_HEIGHT: 140,
  DSP_BOX_HEIGHT: 400, // Much taller for component icons (increased from 360 to 400)

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
    id: 'layer-bp',
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
    id: 'layer-sf',
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
    id: 'dsp-ux',
    label: '',
    x: LAYOUT.CONTENT_START_X,
    y: LAYOUT.DSP_LAYER_Y + 70,
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
  const edgeX = LAYOUT.CONTENT_START_X + uxBoxWidth + dspBoxGap;
  const edgeY = LAYOUT.DSP_LAYER_Y + 70;
  containers.push({
    id: 'dsp-edge',
    label: '',
    x: edgeX,
    y: edgeY,
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

  // ========== DSP EDGE COMPONENTS (inside Edge container) ==========
  // Layout: 3 rows with 8 components - all same size, evenly spaced
  // Row 1: DISC, Event Bus (2 components - centered with gaps)
  // Row 2: App Server, Router, Agent (3 components)
  // Row 3: Log Server, DISI, Database (3 components)
  
  const edgeComponentPadding = 10; // padding inside edge box
  const edgeComponentGap = 40; // gap between components
  const edgeInnerWidth = edgeBoxWidth - 2 * edgeComponentPadding;
  const edgeInnerHeight = LAYOUT.DSP_BOX_HEIGHT - 2 * edgeComponentPadding; // full height minus padding

  // 3-column grid
  const componentColumns = 3;
  const componentWidth = (edgeInnerWidth - edgeComponentGap * (componentColumns - 1)) / componentColumns;
  const componentHeight = (edgeInnerHeight - edgeComponentGap * 2) / 3; // 3 rows, 2 vertical gaps

  // Position rows so that the middle row center aligns with edge box center
  const desiredMidCenterY = edgeY + LAYOUT.DSP_BOX_HEIGHT / 2;
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
  
  // Row 1: 2 components (DISC at col1, Event Bus at col3)
  containers.push({
    id: 'edge-comp-disc',
    label: '',
    x: row1Col1X,
    y: row1Y,
    width: componentWidth,
    height: componentHeight,
    type: 'device',
    state: 'hidden',
    logoIconKey: 'edge-component-disc' as IconKey,
    borderColor: '#009681',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 12,
  });

  containers.push({
    id: 'edge-comp-event-bus',
    label: '',
    x: row1Col2X,
    y: row1Y,
    width: componentWidth,
    height: componentHeight,
    type: 'device',
    state: 'hidden',
    logoIconKey: 'edge-component-event-bus' as IconKey,
    borderColor: '#009681',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 12,
  });

  // Row 2: 3 components (App Server, Router, Agent)
  containers.push({
    id: 'edge-comp-app-server',
    label: '',
    x: col1X,
    y: row2Y,
    width: componentWidth,
    height: componentHeight,
    type: 'device',
    state: 'hidden',
    logoIconKey: 'edge-component-app-server' as IconKey,
    borderColor: '#009681',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 12,
  });

  containers.push({
    id: 'edge-comp-router',
    label: '',
    x: col2X,
    y: row2Y,
    width: componentWidth,
    height: componentHeight,
    type: 'device',
    state: 'hidden',
    logoIconKey: 'edge-component-router' as IconKey,
    borderColor: '#009681',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 12,
  });

  containers.push({
    id: 'edge-comp-agent',
    label: '',
    x: col3X,
    y: row2Y,
    width: componentWidth,
    height: componentHeight,
    type: 'device',
    state: 'hidden',
    logoIconKey: 'edge-component-agent' as IconKey,
    borderColor: '#009681',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 12,
  });

  // Row 3: 3 components (Log Server, DISI, Database)
  containers.push({
    id: 'edge-comp-log-server',
    label: '',
    x: col1X,
    y: row3Y,
    width: componentWidth,
    height: componentHeight,
    type: 'device',
    state: 'hidden',
    logoIconKey: 'edge-component-log-server' as IconKey,
    borderColor: '#009681',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 12,
  });

  containers.push({
    id: 'edge-comp-disi',
    label: '',
    x: col2X,
    y: row3Y,
    width: componentWidth,
    height: componentHeight,
    type: 'device',
    state: 'hidden',
    logoIconKey: 'edge-component-disi' as IconKey,
    borderColor: '#009681',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 12,
  });

  containers.push({
    id: 'edge-comp-database',
    label: '',
    x: col3X,
    y: row3Y,
    width: componentWidth,
    height: componentHeight,
    type: 'device',
    state: 'hidden',
    logoIconKey: 'edge-component-database' as IconKey,
    borderColor: '#009681',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 12,
  });

  // Management Cockpit - Environment label as property
  containers.push({
    id: 'dsp-mc',
    label: '',
    x: LAYOUT.CONTENT_START_X + uxBoxWidth + dspBoxGap + edgeBoxWidth + dspBoxGap,
    y: LAYOUT.DSP_LAYER_Y + 70,
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
    id: 'bp-erp',
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
    id: 'bp-cloud',
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
    url: '/analytics',
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
    id: 'sf-systems-group',
    label: '',
    x: LAYOUT.CONTENT_START_X,
    y: shopfloorGroupY,
    width: systemsGroupWidth,
    height: shopfloorGroupHeight,
    type: 'shopfloor-group',
    state: 'hidden',
    backgroundColor: '#ffffff',
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
    id: 'sf-system-bp',
    label: '',
    x: LAYOUT.CONTENT_START_X + 10,
    y: shopfloorGroupY + 10,
    width: systemBoxWidth,
    height: systemBoxHeight,
    type: 'device',  // Changed from 'shopfloor' to 'device' for proper icon display
    state: 'hidden',
    logoIconKey: 'shopfloor-systems' as IconKey,
    borderColor: 'rgba(0, 0, 0, 0.12)',
    backgroundColor: 'url(#shopfloor-gradient)',
    labelPosition: 'bottom-center',
    fontSize: 13,
    url: 'fts',
  });

  containers.push({
    id: 'sf-system-fts',
    label: '',
    x: LAYOUT.CONTENT_START_X + 10 + systemBoxWidth + systemBoxGap,
    y: shopfloorGroupY + 10,
    width: systemBoxWidth,
    height: systemBoxHeight,
    type: 'device',  // Changed from 'shopfloor' to 'device' for proper icon display
    state: 'hidden',
    logoIconKey: 'shopfloor-fts' as IconKey,
    borderColor: 'rgba(0, 0, 0, 0.12)',
    backgroundColor: 'url(#shopfloor-gradient)',
    labelPosition: 'bottom-center',
    fontSize: 13,
    url: 'process',
  });

  // Devices group - label inside container at bottom
  containers.push({
    id: 'sf-devices-group',
    label: '',
    x: LAYOUT.CONTENT_START_X + systemsGroupWidth + shopfloorGap,
    y: shopfloorGroupY,
    width: devicesGroupWidth,
    height: shopfloorGroupHeight,
    type: 'shopfloor-group',
    state: 'normal',
    backgroundColor: '#ffffff',
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

  const deviceIcons: { id: string; icon: IconKey }[] = [
    { id: 'sf-device-mill', icon: 'device-mill' as IconKey },
    { id: 'sf-device-drill', icon: 'device-drill' as IconKey },
    { id: 'sf-device-aiqs', icon: 'device-aiqs' as IconKey },
    { id: 'sf-device-hbw', icon: 'device-hbw' as IconKey },
    { id: 'sf-device-dps', icon: 'device-dps' as IconKey },
    { id: 'sf-device-chrg', icon: 'device-chrg' as IconKey },
  ];

  // Single row of 6 devices
  deviceIcons.forEach((device, i) => {
    containers.push({
      id: device.id,
      label: '',
      x: devicesStartX + i * (deviceBoxWidth + deviceBoxGap),
      y: shopfloorGroupY + 10,
      width: deviceBoxWidth,
      height: deviceBoxHeight,
      type: 'device',
      state: 'normal',
      logoIconKey: device.icon,
      borderColor: 'rgba(0, 0, 0, 0.12)',
      backgroundColor: 'url(#shopfloor-gradient)',
      labelPosition: 'bottom-center',
      fontSize: 12,
      url: 'module',
    });
  });

  return containers;
}

/**
 * Create default connections
 */
export function createDefaultConnections(): ConnectionConfig[] {
  return [
    // UX to Edge
    {
      id: 'conn-dsp-ux-dsp-edge',
      fromId: 'dsp-ux',
      toId: 'dsp-edge',
      fromSide: 'right',
      toSide: 'left',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    // Edge to Management
    {
      id: 'conn-dsp-edge-dsp-mc',
      fromId: 'dsp-edge',
      toId: 'dsp-mc',
      fromSide: 'right',
      toSide: 'left',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    // Edge to Shopfloor Systems
    {
      id: 'conn-dsp-edge-sf-system-bp',
      fromId: 'dsp-edge',
      toId: 'sf-system-bp',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    {
      id: 'conn-dsp-edge-sf-system-fts',
      fromId: 'dsp-edge',
      toId: 'sf-system-fts',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    // Edge to Shopfloor Devices
    { id: 'conn-dsp-edge-sf-device-mill', fromId: 'dsp-edge', toId: 'sf-device-mill', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true },
    { id: 'conn-dsp-edge-sf-device-drill', fromId: 'dsp-edge', toId: 'sf-device-drill', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true },
    { id: 'conn-dsp-edge-sf-device-aiqs', fromId: 'dsp-edge', toId: 'sf-device-aiqs', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true },
    { id: 'conn-dsp-edge-sf-device-hbw', fromId: 'dsp-edge', toId: 'sf-device-hbw', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true },
    { id: 'conn-dsp-edge-sf-device-dps', fromId: 'dsp-edge', toId: 'sf-device-dps', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true },
    { id: 'conn-dsp-edge-sf-device-chrg', fromId: 'dsp-edge', toId: 'sf-device-chrg', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true },
    // Business to Edge
    {
      id: 'conn-bp-erp-dsp-edge',
      fromId: 'bp-erp',
      toId: 'dsp-edge',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    {
      id: 'conn-bp-cloud-dsp-edge',
      fromId: 'bp-cloud',
      toId: 'dsp-edge',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    {
      id: 'conn-bp-analytics-dsp-edge',
      fromId: 'bp-analytics',
      toId: 'dsp-edge',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
    {
      id: 'conn-bp-data-lake-dsp-edge',
      fromId: 'bp-data-lake',
      toId: 'dsp-edge',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
    },
  ];
}

/**
 * Create animation steps (13-step parity with legacy DSP animation)
 */
export function createDefaultSteps(): StepConfig[] {
  const baseShopfloorContainers = [
    'layer-sf',
    'sf-systems-group',
    'sf-system-bp',
    'sf-system-fts',
    'sf-devices-group',
    'sf-device-mill',
    'sf-device-drill',
    'sf-device-aiqs',
    'sf-device-hbw',
    'sf-device-dps',
    'sf-device-chrg',
  ];

  const baseShopfloorConnections = [
    'conn-dsp-edge-sf-system-bp',
    'conn-dsp-edge-sf-system-fts',
    'conn-dsp-edge-sf-device-mill',
    'conn-dsp-edge-sf-device-drill',
    'conn-dsp-edge-sf-device-aiqs',
    'conn-dsp-edge-sf-device-hbw',
    'conn-dsp-edge-sf-device-dps',
    'conn-dsp-edge-sf-device-chrg',
  ];

  return [
    // Step 1: Shopfloor Devices
    {
      id: 'step-1',
      label: $localize`:@@dspArchStep1:Shopfloor Devices`,
      description: $localize`:@@dspArchStep1Desc:DSP connects heterogeneous devices in the shopfloor without interfering with machine logic.`,
      visibleContainerIds: [
        'layer-sf',
        'sf-devices-group',
        'sf-device-mill',
        'sf-device-drill',
        'sf-device-aiqs',
        'sf-device-hbw',
        'sf-device-dps',
        'sf-device-chrg',
      ],
      highlightedContainerIds: [
        'sf-devices-group',
        'sf-device-mill',
        'sf-device-drill',
        'sf-device-aiqs',
        'sf-device-hbw',
        'sf-device-dps',
        'sf-device-chrg',
      ],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
    },

    // Step 2: Shopfloor Systems
    {
      id: 'step-2',
      label: $localize`:@@dspArchStep2:Shopfloor Systems`,
      description: $localize`:@@dspArchStep2Desc:DSP integrates complete systems like AGVs, warehouses, and custom controls.`,
      visibleContainerIds: baseShopfloorContainers,
      highlightedContainerIds: ['sf-systems-group', 'sf-system-bp', 'sf-system-fts'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
    },

    // Step 3: DSP Edge Core
    {
      id: 'step-3',
      label: $localize`:@@dspArchStep3:DSP Edge Core`,
      description: $localize`:@@dspArchStep3Desc:The DSP Edge is the local runtime for connectivity, process logic, digital twin and data processing.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: ['layer-dsp', 'dsp-edge'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
      showFunctionIcons: false,
    },

    // Step 4: Connectivity
    {
      id: 'step-4',
      label: $localize`:@@dspArchStep4:Connectivity`,
      description: $localize`:@@dspArchStep4Desc:Connect any machine via OPC UA, MQTT, REST, and custom protocols.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: baseShopfloorConnections,
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-network'],
    },

    // Step 5: Digital Twin
    {
      id: 'step-5',
      label: $localize`:@@dspArchStep5:Digital Twin`,
      description: $localize`:@@dspArchStep5Desc:Real-time machine and workpiece state modelling at the edge.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: [],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-digital-twin'],
    },

    // Step 6: Process Logic
    {
      id: 'step-6',
      label: $localize`:@@dspArchStep6:Process Logic`,
      description: $localize`:@@dspArchStep6Desc:Model event-driven shopfloor processes with decentralized orchestration.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: [],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-workflow'],
    },

    // Step 7: Edge Analytics
    {
      id: 'step-7',
      label: $localize`:@@dspArchStep7:Edge Analytics`,
      description: $localize`:@@dspArchStep7Desc:Edge analytics for cycle time, vibrations, quality, utilization.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: [],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-analytics'],
    },

    // Step 8: Buffering
    {
      id: 'step-8',
      label: $localize`:@@dspArchStep7a:Buffering`,
      description: $localize`:@@dspArchStep7aDesc:Guaranteed event delivery with local buffering during connection loss.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: [],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-data-storage'],
    },

    // Step 9: Shopfloor ↔ Edge
    {
      id: 'step-9',
      label: $localize`:@@dspArchStep8:Shopfloor ↔ Edge`,
      description: $localize`:@@dspArchStep8Desc:DSP enables bidirectional, real-time communication between machines, systems, and Edge.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: [],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: baseShopfloorConnections,
      showFunctionIcons: true,
    },

    // Step 10: Management Cockpit
    {
      id: 'step-10',
      label: $localize`:@@dspArchStep9:Management Cockpit`,
      description: $localize`:@@dspArchStep9Desc:Model processes, manage organization, and orchestrate all Edge nodes from the cloud.`,
      visibleContainerIds: [
        'layer-dsp',
        'dsp-edge',
        'dsp-mc',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['dsp-mc'],
      visibleConnectionIds: ['conn-dsp-edge-dsp-mc', ...baseShopfloorConnections],
      highlightedConnectionIds: ['conn-dsp-edge-dsp-mc'],
      showFunctionIcons: true,
    },

    // Step 11: Business Integration
    {
      id: 'step-11',
      label: $localize`:@@dspArchStep10:Business Integration`,
      description: $localize`:@@dspArchStep10Desc:DSP connects shopfloor events with ERP processes, cloud analytics, and data lakes.`,
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        'bp-erp',
        'bp-cloud',
        'bp-analytics',
        'bp-data-lake',
        'dsp-edge',
        'dsp-mc',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['layer-bp', 'bp-erp', 'bp-cloud', 'bp-analytics', 'bp-data-lake'],
      visibleConnectionIds: [
        'conn-dsp-edge-dsp-mc',
        'conn-bp-erp-dsp-edge',
        'conn-bp-cloud-dsp-edge',
        'conn-bp-analytics-dsp-edge',
        'conn-bp-data-lake-dsp-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [
        'conn-bp-erp-dsp-edge',
        'conn-bp-cloud-dsp-edge',
        'conn-bp-analytics-dsp-edge',
        'conn-bp-data-lake-dsp-edge',
      ],
      showFunctionIcons: true,
    },

    // Step 12: SmartFactory Dashboard
    {
      id: 'step-12',
      label: $localize`:@@dspArchStep11:SmartFactory Dashboard`,
      description: $localize`:@@dspArchStep11Desc:Visualization of the digital twin, real-time processes, and track & trace in the shopfloor.`,
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        'bp-erp',
        'bp-cloud',
        'bp-analytics',
        'bp-data-lake',
        'dsp-ux',
        'dsp-edge',
        'dsp-mc',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['dsp-ux'],
      visibleConnectionIds: [
        'conn-dsp-ux-dsp-edge',
        'conn-dsp-edge-dsp-mc',
        'conn-bp-erp-dsp-edge',
        'conn-bp-cloud-dsp-edge',
        'conn-bp-analytics-dsp-edge',
        'conn-bp-data-lake-dsp-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: ['conn-dsp-ux-dsp-edge'],
      showFunctionIcons: true,
    },

    // Step 13: Autonomous & Adaptive Enterprise
    {
      id: 'step-13',
      label: $localize`:@@dspArchStep12:Autonomous & Adaptive Enterprise`,
      description: $localize`:@@dspArchStep12Desc:Data from shopfloor, Edge, ERP, analytics, and data lakes enable autonomous workflows, predictive decisions, and continuous process optimization.`,
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        'bp-erp',
        'bp-cloud',
        'bp-analytics',
        'bp-data-lake',
        'dsp-ux',
        'dsp-edge',
        'dsp-mc',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: [
        'layer-bp',
        'layer-dsp',
        'dsp-ux',
        'dsp-edge',
        'dsp-mc',
        'bp-erp',
        'bp-cloud',
        'bp-analytics',
        'bp-data-lake',
      ],
      visibleConnectionIds: [
        'conn-dsp-ux-dsp-edge',
        'conn-dsp-edge-dsp-mc',
        'conn-bp-erp-dsp-edge',
        'conn-bp-cloud-dsp-edge',
        'conn-bp-analytics-dsp-edge',
        'conn-bp-data-lake-dsp-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [
        'conn-dsp-ux-dsp-edge',
        'conn-dsp-edge-dsp-mc',
        'conn-bp-erp-dsp-edge',
        'conn-bp-cloud-dsp-edge',
        'conn-bp-analytics-dsp-edge',
        'conn-bp-data-lake-dsp-edge',
      ],
      showFunctionIcons: true,
    },

    // Step 14: Complete Overview
    {
      id: 'step-14',
      label: $localize`:@@dspArchStep13:Complete DSP Architecture`,
      description: '',
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        'bp-erp',
        'bp-cloud',
        'bp-analytics',
        'bp-data-lake',
        'dsp-ux',
        'dsp-edge',
        'dsp-mc',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: [],
      visibleConnectionIds: [
        'conn-dsp-ux-dsp-edge',
        'conn-dsp-edge-dsp-mc',
        'conn-bp-erp-dsp-edge',
        'conn-bp-cloud-dsp-edge',
        'conn-bp-analytics-dsp-edge',
        'conn-bp-data-lake-dsp-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [],
      showFunctionIcons: true,
    },
  ];
}

/**
 * View mode types for multi-view system
 */
export type ViewMode = 'functional' | 'component' | 'deployment';

/**
 * Create Functional View - Standard three-layer architecture
 */
function createFunctionalView(): { containers: ContainerConfig[]; connections: ConnectionConfig[]; steps: StepConfig[] } {
  return {
    containers: createDefaultContainers(),
    connections: createDefaultConnections(),
    steps: createDefaultSteps(),
  };
}

/**
 * Create Component View - DSP Edge internal component architecture
 * Shows 8 edge components in 3-row grid with step-by-step interaction animation
 */
function createComponentView(): { containers: ContainerConfig[]; connections: ConnectionConfig[]; steps: StepConfig[] } {
  const containers = createDefaultContainers();
  const connections = createDefaultConnections();
  
  // Add bidirectional connections between edge components
  // All components connect to Router as the central hub
  const edgeComponentConnections: ConnectionConfig[] = [
    // DISC <-> Router
    {
      id: 'conn-ec-disc-router',
      fromId: 'edge-comp-disc',
      toId: 'edge-comp-router',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6, // Shorter arrow tips
    },
    // Event Bus <-> Router
    {
      id: 'conn-ec-eventbus-router',
      fromId: 'edge-comp-event-bus',
      toId: 'edge-comp-router',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    // App Server <-> Router
    {
      id: 'conn-ec-appserver-router',
      fromId: 'edge-comp-app-server',
      toId: 'edge-comp-router',
      fromSide: 'right',
      toSide: 'left',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    // Agent <-> Router
    {
      id: 'conn-ec-agent-router',
      fromId: 'edge-comp-agent',
      toId: 'edge-comp-router',
      fromSide: 'left',
      toSide: 'right',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    // Log Server <-> Router
    {
      id: 'conn-ec-logserver-router',
      fromId: 'edge-comp-log-server',
      toId: 'edge-comp-router',
      fromSide: 'top',
      toSide: 'bottom',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    // DISI <-> Router
    {
      id: 'conn-ec-disi-router',
      fromId: 'edge-comp-disi',
      toId: 'edge-comp-router',
      fromSide: 'top',
      toSide: 'bottom',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    // Database <-> Router
    {
      id: 'conn-ec-database-router',
      fromId: 'edge-comp-database',
      toId: 'edge-comp-router',
      fromSide: 'top',
      toSide: 'bottom',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    // External connections from edge components
    // DISI to Shopfloor Systems (using L-shaped arrows)
    {
      id: 'conn-ec-disi-sf-system-bp',
      fromId: 'edge-comp-disi',
      toId: 'sf-system-bp',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    {
      id: 'conn-ec-disi-sf-system-fts',
      fromId: 'edge-comp-disi',
      toId: 'sf-system-fts',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    // DISI to Shopfloor Devices
    {
      id: 'conn-ec-disi-sf-device-mill',
      fromId: 'edge-comp-disi',
      toId: 'sf-device-mill',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    {
      id: 'conn-ec-disi-sf-device-drill',
      fromId: 'edge-comp-disi',
      toId: 'sf-device-drill',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    {
      id: 'conn-ec-disi-sf-device-aiqs',
      fromId: 'edge-comp-disi',
      toId: 'sf-device-aiqs',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    {
      id: 'conn-ec-disi-sf-device-hbw',
      fromId: 'edge-comp-disi',
      toId: 'sf-device-hbw',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    {
      id: 'conn-ec-disi-sf-device-dps',
      fromId: 'edge-comp-disi',
      toId: 'sf-device-dps',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    {
      id: 'conn-ec-disi-sf-device-chrg',
      fromId: 'edge-comp-disi',
      toId: 'sf-device-chrg',
      fromSide: 'bottom',
      toSide: 'top',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    // DISC to Business ERP
    {
      id: 'conn-ec-disc-bp-erp',
      fromId: 'edge-comp-disc',
      toId: 'bp-erp',
      fromSide: 'top',
      toSide: 'bottom',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    // SmartFactory Dashboard to App Server (left-to-right)
    {
      id: 'conn-ux-ec-appserver',
      fromId: 'dsp-ux',
      toId: 'edge-comp-app-server',
      fromSide: 'right',
      toSide: 'left',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
    // Agent to Management Cockpit
    {
      id: 'conn-ec-agent-management',
      fromId: 'edge-comp-agent',
      toId: 'dsp-mc',
      fromSide: 'right',
      toSide: 'left',
      state: 'hidden',
      hasArrow: true,
      bidirectional: true,
      arrowSize: 6,
    },
  ];
  
  connections.push(...edgeComponentConnections);
  
  const baseShopfloorContainers = [
    'sf-systems-group',
    'sf-system-bp',
    'sf-system-fts',
    'sf-devices-group',
    'sf-device-mill',
    'sf-device-drill',
    'sf-device-aiqs',
    'sf-device-hbw',
    'sf-device-dps',
    'sf-device-chrg',
  ];
  
  // Edge component connection IDs for internal routing
  const allEdgeComponentConnections = [
    'conn-ec-disc-router',
    'conn-ec-eventbus-router',
    'conn-ec-appserver-router',
    'conn-ec-agent-router',
    'conn-ec-logserver-router',
    'conn-ec-disi-router',
    'conn-ec-database-router',
  ];
  
  // External connections from edge components to shopfloor
  const disiShopfloorConnections = [
    'conn-ec-disi-sf-system-bp',
    'conn-ec-disi-sf-system-fts',
    'conn-ec-disi-sf-device-mill',
    'conn-ec-disi-sf-device-drill',
    'conn-ec-disi-sf-device-aiqs',
    'conn-ec-disi-sf-device-hbw',
    'conn-ec-disi-sf-device-dps',
    'conn-ec-disi-sf-device-chrg',
  ];
  
  const steps: StepConfig[] = [
    // Step 1: Empty DSP layer with Edge container only
    {
      id: 'component-step-1',
      label: $localize`:@@componentStep1:Edge Container`,
      description: $localize`:@@componentStep1Desc:DSP Edge container ready for component deployment.`,
      visibleContainerIds: [
        'layer-dsp',
        'dsp-edge',
      ],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
      showFunctionIcons: false,
    },
    
    // Step 2: All edge components added
    {
      id: 'component-step-2',
      label: $localize`:@@componentStep2:Edge Components`,
      description: $localize`:@@componentStep2Desc:Eight internal edge components provide distributed processing capabilities.`,
      visibleContainerIds: [
        'layer-dsp',
        'dsp-edge',
        'edge-comp-disc',
        'edge-comp-event-bus',
        'edge-comp-app-server',
        'edge-comp-router',
        'edge-comp-agent',
        'edge-comp-log-server',
        'edge-comp-disi',
        'edge-comp-database',
      ],
      highlightedContainerIds: [
        'edge-comp-disc',
        'edge-comp-event-bus',
        'edge-comp-app-server',
        'edge-comp-router',
        'edge-comp-agent',
        'edge-comp-log-server',
        'edge-comp-disi',
        'edge-comp-database',
      ],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
      showFunctionIcons: false,
    },
    
    // Step 3: Internal connections between components and router
    {
      id: 'component-step-3',
      label: $localize`:@@componentStep3:Internal Routing`,
      description: $localize`:@@componentStep3Desc:Router connects all edge components for internal communication.`,
      visibleContainerIds: [
        'layer-dsp',
        'dsp-edge',
        'edge-comp-disc',
        'edge-comp-event-bus',
        'edge-comp-app-server',
        'edge-comp-router',
        'edge-comp-agent',
        'edge-comp-log-server',
        'edge-comp-disi',
        'edge-comp-database',
      ],
      highlightedContainerIds: ['edge-comp-router'],
      visibleConnectionIds: allEdgeComponentConnections,
      highlightedConnectionIds: allEdgeComponentConnections,
      showFunctionIcons: false,
    },
    
    // Step 4: DISC connection to Business layer ERP
    {
      id: 'component-step-4',
      label: $localize`:@@componentStep4:Business Integration`,
      description: $localize`:@@componentStep4Desc:DISC integrates with business ERP for data synchronization.`,
      visibleContainerIds: [
        'layer-bp',
        'bp-erp',
        'layer-dsp',
        'dsp-edge',
        'edge-comp-disc',
        'edge-comp-event-bus',
        'edge-comp-app-server',
        'edge-comp-router',
        'edge-comp-agent',
        'edge-comp-log-server',
        'edge-comp-disi',
        'edge-comp-database',
      ],
      highlightedContainerIds: ['edge-comp-disc', 'bp-erp'],
      visibleConnectionIds: [
        ...allEdgeComponentConnections,
        'conn-ec-disc-bp-erp',
      ],
      highlightedConnectionIds: ['conn-ec-disc-bp-erp'],
      showFunctionIcons: false,
    },
    
    // Step 5: App Server connection to SmartFactory Dashboard
    {
      id: 'component-step-5',
      label: $localize`:@@componentStep5:Dashboard Integration`,
      description: $localize`:@@componentStep5Desc:App Server connects to SmartFactory Dashboard for UI services.`,
      visibleContainerIds: [
        'layer-bp',
        'bp-erp',
        'layer-dsp',
        'dsp-ux',
        'dsp-edge',
        'edge-comp-disc',
        'edge-comp-event-bus',
        'edge-comp-app-server',
        'edge-comp-router',
        'edge-comp-agent',
        'edge-comp-log-server',
        'edge-comp-disi',
        'edge-comp-database',
      ],
      highlightedContainerIds: ['edge-comp-app-server', 'dsp-ux'],
      visibleConnectionIds: [
        ...allEdgeComponentConnections,
        'conn-ec-disc-bp-erp',
        'conn-ux-ec-appserver',
      ],
      highlightedConnectionIds: ['conn-ux-ec-appserver'],
      showFunctionIcons: false,
    },
    
    // Step 6: Agent connection to Management Cockpit
    {
      id: 'component-step-6',
      label: $localize`:@@componentStep6:Management Integration`,
      description: $localize`:@@componentStep6Desc:Agent connects to Management Cockpit for monitoring and control.`,
      visibleContainerIds: [
        'layer-bp',
        'bp-erp',
        'layer-dsp',
        'dsp-ux',
        'dsp-edge',
        'dsp-mc',
        'edge-comp-disc',
        'edge-comp-event-bus',
        'edge-comp-app-server',
        'edge-comp-router',
        'edge-comp-agent',
        'edge-comp-log-server',
        'edge-comp-disi',
        'edge-comp-database',
      ],
      highlightedContainerIds: ['edge-comp-agent', 'dsp-mc'],
      visibleConnectionIds: [
        ...allEdgeComponentConnections,
        'conn-ec-disc-bp-erp',
        'conn-ux-ec-appserver',
        'conn-ec-agent-management',
      ],
      highlightedConnectionIds: ['conn-ec-agent-management'],
      showFunctionIcons: false,
    },
    
    // Step 7: DISI connections to shopfloor devices and systems
    {
      id: 'component-step-7',
      label: $localize`:@@componentStep7:Shopfloor Integration`,
      description: $localize`:@@componentStep7Desc:DISI connects to all shopfloor devices and systems for data collection.`,
      visibleContainerIds: [
        'layer-bp',
        'bp-erp',
        'layer-dsp',
        'dsp-ux',
        'dsp-edge',
        'dsp-mc',
        'edge-comp-disc',
        'edge-comp-event-bus',
        'edge-comp-app-server',
        'edge-comp-router',
        'edge-comp-agent',
        'edge-comp-log-server',
        'edge-comp-disi',
        'edge-comp-database',
        'layer-sf',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['edge-comp-disi'],
      visibleConnectionIds: [
        ...allEdgeComponentConnections,
        'conn-ec-disc-bp-erp',
        'conn-ux-ec-appserver',
        'conn-ec-agent-management',
        ...disiShopfloorConnections,
      ],
      highlightedConnectionIds: disiShopfloorConnections,
      showFunctionIcons: false,
    },
  ];
  
  return {
    containers,
    connections,
    steps,
  };
}

/**
 * Create Deployment View - DSP Edge deployment pipeline
 * Shows 4-step deployment pipeline with processing flow
 */
function createDeploymentView(): { containers: ContainerConfig[]; connections: ConnectionConfig[]; steps: StepConfig[] } {
  const containers = createDefaultContainers();
  const connections = createDefaultConnections();
  
  // Add 4 deployment pipeline step containers inside Edge box
  // Pipeline containers visualized as boxes with arrow-head styling (no SVG icons)
  const edgeContainer = containers.find(c => c.id === 'dsp-edge');
  if (!edgeContainer) throw new Error('Edge container not found');
  
  const edgeX = edgeContainer.x;
  const edgeY = edgeContainer.y;
  const edgeWidth = edgeContainer.width;
  const edgeHeight = edgeContainer.height;
  
  // Treppenförmige Pipeline-Pfeile
  const pipelineStepWidth = 180;
  const pipelineStepHeight = 60;
  const pipelineOffsetX = 90;   // weniger horizontaler Versatz
  const pipelineOffsetY = -80;  // stärkerer vertikaler Versatz (noch steiler)
  const pipelineStartX = edgeX + 16;
  const pipelineStartY = edgeY + edgeHeight - pipelineStepHeight - 20;

  const pipelineShapes = [
    { id: 'deployment-step-integration', label: $localize`:@@dspDeployIntegration:Integration`, fill: '#e0f7f4' },
    { id: 'deployment-step-transformation', label: $localize`:@@dspDeployTransformation:Transformation`, fill: '#c7f0e8' },
    { id: 'deployment-step-consolidation', label: $localize`:@@dspDeployConsolidation:Konsolidierung`, fill: '#a8e8dc' },
    { id: 'deployment-step-provisioning', label: $localize`:@@dspDeployProvisioning:Bereitstellung`, fill: '#89e1d0' },
  ];

  pipelineShapes.forEach((shape, index) => {
    containers.push({
      id: shape.id,
      label: shape.label,
      x: pipelineStartX + index * pipelineOffsetX,
      y: pipelineStartY + index * pipelineOffsetY,
      width: pipelineStepWidth,
      height: pipelineStepHeight,
      type: 'pipeline',
      state: 'hidden',
      borderColor: '#009681',
      backgroundColor: shape.fill,
      fontSize: 14,
    });
  });
  
  // Keine Verbindungen zwischen den Pipeline-Pfeilen (bewusst ohne arrows)
  
  // Deployment View Animation Steps - 5-step pipeline reveal
  const baseShopfloorContainers = [
    'layer-sf',
    'sf-systems-group',
    'sf-system-bp',
    'sf-system-fts',
    'sf-devices-group',
    'sf-device-mill',
    'sf-device-drill',
    'sf-device-aiqs',
    'sf-device-hbw',
    'sf-device-dps',
    'sf-device-chrg',
  ];

  const baseShopfloorConnections = [
    'conn-dsp-edge-sf-system-bp',
    'conn-dsp-edge-sf-system-fts',
    'conn-dsp-edge-sf-device-mill',
    'conn-dsp-edge-sf-device-drill',
    'conn-dsp-edge-sf-device-aiqs',
    'conn-dsp-edge-sf-device-hbw',
    'conn-dsp-edge-sf-device-dps',
    'conn-dsp-edge-sf-device-chrg',
  ];
  
  const steps: StepConfig[] = [
    // Step 1: Edge Container (empty)
    {
      id: 'deployment-step-1',
      label: $localize`:@@dspDeployTitle:DSP Deployment Pipeline`,
      description: $localize`:@@dspDeploySubtitle:From integration and transformation to consolidation and provisioning.`,
      visibleContainerIds: [
        'layer-dsp',
        'dsp-edge',
      ],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
      showFunctionIcons: false,
    },
    
    // Step 2: Source Pipeline Step
    {
      id: 'deployment-step-2',
      label: $localize`:@@dspDeployStepIntegration:Integration`,
      description: $localize`:@@dspDeployStepIntegrationDesc:Connects data sources and systems into the DSP landscape.`,
      visibleContainerIds: [
        'layer-dsp',
        'dsp-edge',
        'deployment-step-integration',
      ],
      highlightedContainerIds: ['deployment-step-integration'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
      showFunctionIcons: false,
    },
    
    // Step 3: Build Pipeline Step  
    {
      id: 'deployment-step-3',
      label: $localize`:@@dspDeployStepTransformation:Transformation`,
      description: $localize`:@@dspDeployStepTransformationDesc:Normalizes and enriches data for processing and analytics.`,
      visibleContainerIds: [
        'layer-dsp',
        'dsp-edge',
        'deployment-step-integration',
        'deployment-step-transformation',
      ],
      highlightedContainerIds: ['deployment-step-transformation'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
      showFunctionIcons: false,
    },
    
    // Step 4: Deploy Pipeline Step
    {
      id: 'deployment-step-4',
      label: $localize`:@@dspDeployStepConsolidation:Consolidation`,
      description: $localize`:@@dspDeployStepConsolidationDesc:Combines data from multiple sources into consistent models.`,
      visibleContainerIds: [
        'layer-dsp',
        'dsp-edge',
        'deployment-step-integration',
        'deployment-step-transformation',
        'deployment-step-consolidation',
      ],
      highlightedContainerIds: ['deployment-step-consolidation'],
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
      showFunctionIcons: false,
    },
    
    // Step 5: Monitor Pipeline Step + Complete Flow
    {
      id: 'deployment-step-5',
      label: $localize`:@@dspDeployStepProvisioning:Provisioning`,
      description: $localize`:@@dspDeployStepProvisioningDesc:Delivers prepared data and events to ERP, MES, cloud and analytics platforms.`,
      visibleContainerIds: [
        'layer-bp',
        'bp-erp',
        'bp-cloud',
        'bp-analytics',
        'bp-data-lake',
        'layer-dsp',
        'dsp-ux',
        'dsp-edge',
        'dsp-mc',
        'deployment-step-integration',
        'deployment-step-transformation',
        'deployment-step-consolidation',
        'deployment-step-provisioning',
        'layer-sf',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['deployment-step-provisioning'],
      visibleConnectionIds: [
        'conn-dsp-ux-dsp-edge',
        'conn-dsp-edge-dsp-mc',
        'conn-bp-erp-dsp-edge',
        'conn-bp-cloud-dsp-edge',
        'conn-bp-analytics-dsp-edge',
        'conn-bp-data-lake-dsp-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [],
      showFunctionIcons: false,
    },
  ];
  
  return {
    containers,
    connections,
    steps,
  };
}

/**
 * Create complete diagram configuration based on view mode
 */
export function createDiagramConfig(viewMode: ViewMode = 'functional'): { containers: ContainerConfig[]; connections: ConnectionConfig[]; steps: StepConfig[] } {
  switch (viewMode) {
    case 'functional':
      return createFunctionalView();
    case 'component':
      return createComponentView();
    case 'deployment':
      return createDeploymentView();
    default:
      return createFunctionalView();
  }
}
