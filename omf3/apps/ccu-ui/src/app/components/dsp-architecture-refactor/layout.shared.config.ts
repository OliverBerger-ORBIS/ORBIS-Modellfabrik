/**
 * Layout configuration for refactored DSP Architecture component.
 * Based on existing dsp-architecture.config.ts with taller DSP layer for component view.
 */
import type { ContainerConfig, ConnectionConfig } from './types';
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
  const uxBoxHeight = LAYOUT.DSP_BOX_HEIGHT / 2 + 60; // reduce to 50% then add 60px height
  const uxCenterY = LAYOUT.DSP_LAYER_Y + 70 + LAYOUT.DSP_BOX_HEIGHT / 2; // keep center identical
  const edgeBoxWidth = 480;
  const managementBoxWidth = dspAvailableWidth - uxBoxWidth - edgeBoxWidth - (dspBoxGap * 2);



  // ========== DSP BOXES ==========

  // SmartFactory Dashboard (UX) - No ORBIS logo, only dashboard icon
  containers.push({
    id: 'dsp-ux',
    label: '',
    x: LAYOUT.CONTENT_START_X,
    y: uxCenterY - uxBoxHeight / 2,
    width: uxBoxWidth,
    height: uxBoxHeight,
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
    centerIconKey: 'logo-edge' as IconKey,
    borderColor: '#009681',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    labelPosition: 'top-center',
    fontSize: 16,
    functionIcons: [
      { iconKey: 'edge-interoperability' as IconKey, size: 48 },
      { iconKey: 'edge-network' as IconKey, size: 48 }, // connectivity
      { iconKey: 'edge-event-driven' as IconKey, size: 48 },
      { iconKey: 'edge-choreography' as IconKey, size: 48 },
      { iconKey: 'edge-digital-twin' as IconKey, size: 48 },
      { iconKey: 'edge-best-of-breed' as IconKey, size: 48 },
      { iconKey: 'edge-analytics' as IconKey, size: 48 },
      { iconKey: 'edge-ai-enablement' as IconKey, size: 48 },
      { iconKey: 'edge-autonomous-enterprise' as IconKey, size: 48 },
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
    centerIconKey: 'logo-mc' as IconKey,
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
  const businessBoxCount = 5;
  const baseBusinessGap = 30;
  const widthForCurrentCount =
    (businessAvailableWidth - (businessBoxCount - 1) * baseBusinessGap) / businessBoxCount;
  const widthForFourBoxes = (businessAvailableWidth - 3 * baseBusinessGap) / 4;
  const businessBoxWidth = Math.min(widthForCurrentCount, widthForFourBoxes);
  const businessGap =
    businessBoxCount > 1
      ? (businessAvailableWidth - businessBoxCount * businessBoxWidth) / (businessBoxCount - 1)
      : 0;
  const businessBoxY = LAYOUT.BUSINESS_Y + 65;
  const businessStartX = LAYOUT.CONTENT_START_X;

  // ERP first
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

  // MES second (with ORBIS top-left)
  containers.push({
    id: 'bp-mes',
    label: '',
    x: businessStartX + (businessBoxWidth + businessGap),
    y: businessBoxY,
    width: businessBoxWidth,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    logoIconKey: 'mes-application' as IconKey,
    secondaryLogoIconKey: 'logo-orbis' as IconKey,
    secondaryLogoPosition: 'top-left',
    borderColor: 'rgba(22, 65, 148, 0.25)',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 16,
  });

  containers.push({
    id: 'bp-cloud',
    label: '',
    x: businessStartX + (businessBoxWidth + businessGap) * 2,
    y: businessBoxY,
    width: businessBoxWidth,
    height: LAYOUT.BUSINESS_BOX_HEIGHT,
    type: 'business',
    state: 'hidden',
    logoIconKey: 'bp-cloud-apps' as IconKey,
    secondaryLogos: ['aws-logo' as IconKey, 'google-cloud-logo' as IconKey],
    borderColor: 'rgba(22, 65, 148, 0.25)',
    backgroundColor: '#ffffff',
    labelPosition: 'bottom-center',
    fontSize: 16,
  });

  containers.push({
    id: 'bp-analytics',
    label: '',
    x: businessStartX + (businessBoxWidth + businessGap) * 3,
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
    x: businessStartX + (businessBoxWidth + businessGap) * 4,
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
  const shopfloorGap = 40;
  const shopfloorGroupHeight = 165; // icon + label + group label
  const shopfloorGroupY = LAYOUT.SHOPFLOOR_Y + (LAYOUT.LAYER_HEIGHT - shopfloorGroupHeight) / 2;

  // Default: 2 systems, 6 devices
  const systemEntries: { id: string; icon: IconKey; url?: string }[] = [
    { id: 'sf-system-bp', icon: 'shopfloor-systems' as IconKey, url: 'fts' },
    { id: 'sf-system-fts', icon: 'shopfloor-fts' as IconKey, url: 'process' },
  ];

  const deviceEntries: { id: string; icon: IconKey; url?: string }[] = [
    { id: 'sf-device-mill', icon: 'device-mill' as IconKey, url: 'module' },
    { id: 'sf-device-drill', icon: 'device-drill' as IconKey, url: 'module' },
    { id: 'sf-device-aiqs', icon: 'device-aiqs' as IconKey, url: 'module' },
    { id: 'sf-device-hbw', icon: 'device-hbw' as IconKey, url: 'module' },
    { id: 'sf-device-dps', icon: 'device-dps' as IconKey, url: 'module' },
    { id: 'sf-device-chrg', icon: 'device-chrg' as IconKey, url: 'module' },
  ];

  const systemsCount = systemEntries.length;
  const devicesCount = deviceEntries.length;
  const minGap = 10;
  const itemMargin = 20;
  const maxSystemBoxWidth = 120; // cap at current visual width
  const maxDeviceBoxWidth = 120; // cap at current visual width

  const baseSystemsWidth = systemsCount * maxSystemBoxWidth + Math.max(0, systemsCount - 1) * minGap;
  const baseDevicesWidth = devicesCount * maxDeviceBoxWidth + Math.max(0, devicesCount - 1) * minGap;
  const baseTotal = baseSystemsWidth + baseDevicesWidth;

  const systemsGroupWidth = baseTotal > 0 ? (shopfloorAvailableWidth - shopfloorGap) * (baseSystemsWidth / baseTotal) : 0;
  const devicesGroupWidth = shopfloorAvailableWidth - shopfloorGap - systemsGroupWidth;

  const distribute = (available: number, count: number, maxWidth: number) => {
    if (count <= 0) {
      return { width: 0, gap: 0 };
    }
    const width = Math.min(maxWidth, (available - minGap * Math.max(0, count - 1)) / count);
    const gap = count > 1 ? (available - width * count) / (count - 1) : 0;
    return { width, gap };
  };

  // Systems group
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
    labelPosition: 'bottom',
    fontSize: 14,
    isGroup: true,
  });

  const { width: systemBoxWidth, gap: systemGap } = distribute(
    Math.max(0, systemsGroupWidth - itemMargin * 2),
    systemsCount,
    maxSystemBoxWidth
  );
  const systemStartX = LAYOUT.CONTENT_START_X + itemMargin;
  const systemY = shopfloorGroupY + 10;
  const systemBoxHeight = 120;

  systemEntries.forEach((entry, i) => {
    containers.push({
      id: entry.id,
      label: '',
      x: systemStartX + i * (systemBoxWidth + systemGap),
      y: systemY,
      width: systemBoxWidth,
      height: systemBoxHeight,
      type: 'device',
      state: 'normal',
      logoIconKey: entry.icon,
      borderColor: 'rgba(0, 0, 0, 0.12)',
      backgroundColor: 'url(#shopfloor-gradient)',
      labelPosition: 'bottom-center',
      fontSize: 13,
      url: entry.url,
    });
  });

  // Devices group
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
    labelPosition: 'bottom',
    fontSize: 14,
    isGroup: true,
  });

  const { width: deviceBoxWidth, gap: deviceGap } = distribute(
    Math.max(0, devicesGroupWidth - itemMargin * 2),
    devicesCount,
    maxDeviceBoxWidth
  );
  const devicesStartX = LAYOUT.CONTENT_START_X + systemsGroupWidth + shopfloorGap + itemMargin;
  const deviceY = shopfloorGroupY + 10;
  const deviceBoxHeight = 120;

  deviceEntries.forEach((entry, i) => {
    containers.push({
      id: entry.id,
      label: '',
      x: devicesStartX + i * (deviceBoxWidth + deviceGap),
      y: deviceY,
      width: deviceBoxWidth,
      height: deviceBoxHeight,
      type: 'device',
      state: 'normal',
      logoIconKey: entry.icon,
      borderColor: 'rgba(0, 0, 0, 0.12)',
      backgroundColor: 'url(#shopfloor-gradient)',
      labelPosition: 'bottom-center',
      fontSize: 12,
      url: entry.url,
    });
  });

  return containers;
}

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
      id: 'conn-bp-mes-dsp-edge',
      fromId: 'bp-mes',
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
