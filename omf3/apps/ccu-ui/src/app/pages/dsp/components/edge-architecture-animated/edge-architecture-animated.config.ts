/**
 * Configuration for the animated DSP Edge Architecture diagram.
 * Defines containers, connections, and 4-step animation sequence.
 */

import type { ContainerConfig } from '../../../../components/dsp-architecture/dsp-architecture.types';

export interface EdgeContainerConfig {
  id: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  state?: 'normal' | 'highlight' | 'dimmed' | 'hidden';
  icon?: string;  // Path to SVG icon
}

export interface EdgeConnectionConfig {
  id: string;
  from: string;
  to: string;
  bidirectional?: boolean;
  state?: 'normal' | 'highlight' | 'dimmed' | 'hidden';
}

export interface EdgeStepConfig {
  id: string;
  label: string;
  description: string;
  visibleContainerIds: string[];
  highlightedContainerIds: string[];
  visibleConnectionIds: string[];
  highlightedConnectionIds: string[];
  showBusinessZone?: boolean;
  showShopfloorZone?: boolean;
  showExternalConnections?: boolean;
  showFullArchitecture?: boolean;  // Show full DSP Reference Architecture from Step 3+
}

// SVG viewBox dimensions - matches full DSP Reference Architecture with extended DSP layer
export const EDGE_VIEWBOX_WIDTH = 1200;
export const EDGE_VIEWBOX_HEIGHT = 900;  // Increased for extended DSP layer (Business 80-340, DSP 340-640, Shopfloor 640-900)

// Layout constants for Steps 1-2 (detail view)
// Canvas matches full architecture size, components spread maximally within EDGE box
export const EDGE_LAYOUT = {
  // Main EDGE container - positioned to match DSP layer in full architecture
  EDGE_X: 350,    // Centered horizontally in DSP layer
  EDGE_Y: 360,    // In DSP layer (340 + 20px margin)
  EDGE_WIDTH: 500, // Matches DSP-Function-Box width from reference architecture
  EDGE_HEIGHT: 260, // Increased to accommodate 3 rows without overlap (60px boxes + margins)
  
  // Component boxes inside EDGE - sized to fit properly without overflow
  BOX_WIDTH: 85,  // Reduced from 105 to fit within 500px width with proper margins
  BOX_HEIGHT: 55, // Reduced from 65 to fit within 260px height with 3 rows
  
  // Spacing - 3 rows, smaller border margins (10-15px), larger inter-row gaps (35-45px) for arrow visibility
  // Row 1: DISC (left), Event Bus (right) - horizontally distributed to avoid covering EDGE label
  ROW_1_Y: 375,   // EDGE_Y + 15px margin
  
  // Row 2: App Server (left), Router (center), Agent (right) - vertically centered for horizontal arrows
  // Positioned to align with SmartFactory Dashboard and Management Cockpit for horizontal-only arrows
  ROW_2_Y: 460,   // EDGE_Y + 100px - moved up slightly, centered for horizontal arrows to Dashboard/Cockpit
  
  // Row 3: Log Server (left), DISI (center), Edge Database (right) - close to bottom border
  ROW_3_Y: 545,   // EDGE_Y + 185px - adjusted to maintain proper spacing
  
  // Horizontal positions - evenly distributed with adequate space for bidirectional arrows
  // Row 1 uses wider distribution to avoid covering EDGE label (left) with DISC
  COL_LEFT_X: 390,      // EDGE_X + 40px margin (more space from left edge to avoid EDGE label)
  COL_CENTER_X: 557,    // EDGE_X + (EDGE_WIDTH / 2) - (BOX_WIDTH / 2) - centered
  COL_RIGHT_X: 725,     // EDGE_X + EDGE_WIDTH - BOX_WIDTH - 40px margin (symmetric with left)
  
  // External zone positions (fallback for when shared config is not available)
  BUSINESS_ZONE_Y: 120,
  BUSINESS_ZONE_HEIGHT: 60,
  SHOPFLOOR_ZONE_Y: 660,  // Updated for extended DSP layer
  SHOPFLOOR_ZONE_HEIGHT: 60,
};

// Scaled layout for Steps 3-4 (integrated in full architecture)
// No scaling needed - components already sized for DSP-Function-Box
export const EDGE_LAYOUT_SCALED = {
  // No scaling - components already fit properly
  SCALE: 1.0,
  
  // No offset needed - components already positioned correctly
  OFFSET_X: 0,
  OFFSET_Y: 0,
  
  // Same dimensions as detail view
  BOX_WIDTH: 85,
  BOX_HEIGHT: 55,
  ICON_SIZE: 30,   // Smaller icons for compact view, but still visible
};

/**
 * Create edge component containers
 * @param sharedConfig Optional shared architecture configuration from service
 */
export function createEdgeContainers(sharedConfig?: {
  layers: ContainerConfig[];
  business: any;
  shopfloor: any;
  cloud: any;
}): EdgeContainerConfig[] {
  const containers: EdgeContainerConfig[] = [];
  
  // Main EDGE container box
  containers.push({
    id: 'edge-container',
    label: 'EDGE',
    x: EDGE_LAYOUT.EDGE_X,
    y: EDGE_LAYOUT.EDGE_Y,
    width: EDGE_LAYOUT.EDGE_WIDTH,
    height: EDGE_LAYOUT.EDGE_HEIGHT,
    state: 'hidden',
  });
  
  // Row 1: DISC (left) and Event Bus (right) - maximally spread apart
  containers.push({
    id: 'disc',
    label: 'DISC',
    x: EDGE_LAYOUT.COL_LEFT_X,
    y: EDGE_LAYOUT.ROW_1_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-disc.svg',
  });
  
  containers.push({
    id: 'event-bus',
    label: 'Event Bus',
    x: EDGE_LAYOUT.COL_RIGHT_X,
    y: EDGE_LAYOUT.ROW_1_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-event-bus.svg',
  });
  
  // Row 2: App Server (left), Router (center), Agent (right)
  // App Server and Agent at same vertical position for horizontal arrows
  containers.push({
    id: 'app-server',
    label: 'App Server',
    x: EDGE_LAYOUT.COL_LEFT_X,
    y: EDGE_LAYOUT.ROW_2_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-app-server.svg',
  });
  
  containers.push({
    id: 'router',
    label: 'Router',
    x: EDGE_LAYOUT.COL_CENTER_X,
    y: EDGE_LAYOUT.ROW_2_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-router.svg',
  });
  
  containers.push({
    id: 'agent',
    label: 'Agent',
    x: EDGE_LAYOUT.COL_RIGHT_X,
    y: EDGE_LAYOUT.ROW_2_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-agent.svg',
  });
  
  // Row 3: Log Server (left), DISI (center), Edge Database (right) - same column positions
  containers.push({
    id: 'log-server',
    label: 'Log Server',
    x: EDGE_LAYOUT.COL_LEFT_X,
    y: EDGE_LAYOUT.ROW_3_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-log-server.svg',
  });
  
  containers.push({
    id: 'disi',
    label: 'DISI',
    x: EDGE_LAYOUT.COL_CENTER_X,
    y: EDGE_LAYOUT.ROW_3_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-disi.svg',
  });
  
  containers.push({
    id: 'db',
    label: 'Edge Database',
    x: EDGE_LAYOUT.COL_RIGHT_X,
    y: EDGE_LAYOUT.ROW_3_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-database.svg',
  });
  
  // External zones (for Step 3 & 4)
  // Use shared configuration if provided, otherwise use simplified zones
  if (sharedConfig) {
    // Add layer backgrounds from shared config (for full architecture view)
    sharedConfig.layers.forEach((layer: ContainerConfig) => {
      containers.push({
        id: layer.id,
        label: layer.label || '',
        x: layer.x,
        y: layer.y,
        width: layer.width,
        height: layer.height,
        state: 'hidden',
      });
    });
    
    // Add Business layer containers from shared config
    const businessContainers = [
      sharedConfig.business.erp,
      sharedConfig.business.cloud,
      sharedConfig.business.analytics,
      sharedConfig.business.dataLake,
    ];
    
    businessContainers.forEach((container: ContainerConfig) => {
      containers.push({
        id: container.id,
        label: container.label || '',
        x: container.x,
        y: container.y,
        width: container.width,
        height: container.height,
        state: 'hidden',
        icon: container.logoIconKey ? `assets/svg/icons/${container.logoIconKey}.svg` : undefined,
      });
    });
    
    // Add Shopfloor layer containers from shared config
    const shopfloorContainers = [
      sharedConfig.shopfloor.systems,
      sharedConfig.shopfloor.devices,
    ];
    
    shopfloorContainers.forEach((container: ContainerConfig) => {
      containers.push({
        id: container.id,
        label: container.label || '',
        x: container.x,
        y: container.y,
        width: container.width,
        height: container.height,
        state: 'hidden',
        icon: container.logoIconKey ? `assets/svg/icons/${container.logoIconKey}.svg` : undefined,
      });
    });
    
    // Add Cloud layer containers (Management Cockpit)
    const cloudContainers = [sharedConfig.cloud.managementCockpit];
    
    cloudContainers.forEach((container: ContainerConfig) => {
      containers.push({
        id: container.id,
        label: container.label || '',
        x: container.x,
        y: container.y,
        width: container.width,
        height: container.height,
        state: 'hidden',
        icon: container.logoIconKey ? `assets/svg/icons/${container.logoIconKey}.svg` : undefined,
      });
    });
    
    // Add SmartFactory Dashboard if available
    if (sharedConfig.business.dashboard) {
      containers.push({
        id: sharedConfig.business.dashboard.id,
        label: sharedConfig.business.dashboard.label || '',
        x: sharedConfig.business.dashboard.x,
        y: sharedConfig.business.dashboard.y,
        width: sharedConfig.business.dashboard.width,
        height: sharedConfig.business.dashboard.height,
        state: 'hidden',
        icon: sharedConfig.business.dashboard.logoIconKey ? `assets/svg/icons/${sharedConfig.business.dashboard.logoIconKey}.svg` : undefined,
      });
    }
  } else {
    // Fallback: simplified zones for Steps 1-3
    containers.push({
      id: 'business-zone',
      label: 'Business',
      x: 200,
      y: EDGE_LAYOUT.BUSINESS_ZONE_Y,
      width: 800,
      height: EDGE_LAYOUT.BUSINESS_ZONE_HEIGHT,
      state: 'hidden',
    });
    
    containers.push({
      id: 'shopfloor-zone',
      label: 'Shopfloor',
      x: 200,
      y: EDGE_LAYOUT.SHOPFLOOR_ZONE_Y,
      width: 800,
      height: EDGE_LAYOUT.SHOPFLOOR_ZONE_HEIGHT,
      state: 'hidden',
    });
  }
  
  return containers;
}

/**
 * Create connections between edge components
 */
export function createEdgeConnections(): EdgeConnectionConfig[] {
  return [
    // Internal connections (Step 2)
    { id: 'disc-router', from: 'disc', to: 'router', bidirectional: true, state: 'hidden' },
    { id: 'router-agent', from: 'router', to: 'agent', bidirectional: true, state: 'hidden' },
    { id: 'app-server-router', from: 'app-server', to: 'router', bidirectional: true, state: 'hidden' },
    { id: 'log-server-router', from: 'log-server', to: 'router', bidirectional: true, state: 'hidden' },
    { id: 'disi-router', from: 'disi', to: 'router', bidirectional: true, state: 'hidden' },
    { id: 'router-db', from: 'router', to: 'db', bidirectional: true, state: 'hidden' },
    { id: 'router-event-bus', from: 'router', to: 'event-bus', bidirectional: true, state: 'hidden' },
    
    // External connections (Steps 3-4) - using shared container IDs
    // Agent connects only to Management Cockpit
    { id: 'agent-cockpit', from: 'agent', to: 'cloud-management-cockpit', state: 'hidden' },
    // App Server only to SmartFactory Dashboard
    { id: 'app-server-dashboard', from: 'app-server', to: 'business-dashboard', state: 'hidden' },
    // DISI to Shopfloor Systems
    { id: 'disi-shopfloor-systems', from: 'disi', to: 'shopfloor-systems', state: 'hidden' },
    // DISI to Shopfloor Devices
    { id: 'disi-shopfloor-devices', from: 'disi', to: 'shopfloor-devices', state: 'hidden' },
    // DISC to ERP Application (Business Process Layer)
    { id: 'disc-erp', from: 'disc', to: 'business-erp', state: 'hidden' },
    // Event Bus to Data Lake
    { id: 'event-bus-datalake', from: 'event-bus', to: 'business-data-lake', state: 'hidden' },
    // Edge Database to Data Lake - REMOVED per user request
    // { id: 'db-datalake', from: 'db', to: 'business-data-lake', state: 'hidden' },
  ];
}

/**
 * Create 4-step animation sequence
 */
export function createEdgeSteps(): EdgeStepConfig[] {
  const allComponentIds = ['disc', 'router', 'agent', 'app-server', 'log-server', 'disi', 'db', 'event-bus'];
  const allInternalConnectionIds = [
    'disc-router', 'router-agent', 'app-server-router', 
    'log-server-router', 'disi-router', 'router-db', 'router-event-bus'
  ];
  
  // Shared container IDs from DspArchitectureConfigService
  const sharedBusinessIds = ['business-erp', 'business-cloud', 'business-analytics', 'business-data-lake', 'business-dashboard'];
  const sharedShopfloorIds = ['shopfloor-systems', 'shopfloor-devices'];
  const sharedCloudIds = ['cloud-management-cockpit'];
  
  return [
    // Step 1: Edge Components Overview
    {
      id: 'step-1',
      label: $localize`:@@edgeAnimStep1:Edge Components Overview`,
      description: $localize`:@@edgeAnimStep1Desc:DSP Edge consists of controller, integration, router, agents, logging and local storage components.`,
      visibleContainerIds: ['edge-container', ...allComponentIds],
      highlightedContainerIds: allComponentIds,
      visibleConnectionIds: [],
      highlightedConnectionIds: [],
    },
    
    // Step 2: Internal Event Routing
    {
      id: 'step-2',
      label: $localize`:@@edgeAnimStep2:Internal Event Routing`,
      description: $localize`:@@edgeAnimStep2Desc:Router distributes events between DISC, DISI, agents, services and storage inside the Edge.`,
      visibleContainerIds: ['edge-container', ...allComponentIds],
      highlightedContainerIds: ['router'],
      visibleConnectionIds: allInternalConnectionIds,
      highlightedConnectionIds: allInternalConnectionIds,
    },
    
    // Step 3: DSP Layer Integration - show only DSP containers with Dashboard and Cockpit connections
    {
      id: 'step-3',
      label: $localize`:@@edgeAnimStep3:DSP Layer Integration`,
      description: $localize`:@@edgeAnimStep3Desc:Edge components connect to SmartFactory Dashboard and Management Cockpit in the DSP layer.`,
      visibleContainerIds: [
        'edge-container', 
        ...allComponentIds, 
        'business-dashboard',  // Only Dashboard in DSP layer
        ...sharedCloudIds      // Management Cockpit in Cloud layer (part of DSP)
      ],
      highlightedContainerIds: ['app-server', 'agent'],
      visibleConnectionIds: [
        ...allInternalConnectionIds, 
        'app-server-dashboard',   // App Server → SmartFactory Dashboard (horizontal)
        'agent-cockpit'           // Agent → Management Cockpit (horizontal)
      ],
      highlightedConnectionIds: ['app-server-dashboard', 'agent-cockpit'],
      showFullArchitecture: true,
    },
    
    // Step 4: Full Architecture Integration - add Business and Shopfloor layers with connections
    // Note: No Edge Database → Data Lake connection as requested
    {
      id: 'step-4',
      label: $localize`:@@edgeAnimStep4:Full Architecture Integration`,
      description: $localize`:@@edgeAnimStep4Desc:Edge bridges business systems and shopfloor devices with ERP, Data Lake and shopfloor assets.`,
      visibleContainerIds: [
        'edge-container', 
        ...allComponentIds, 
        ...sharedBusinessIds,  // Add Business layer containers (ERP, Cloud Apps, Analytics, Data Lake)
        ...sharedShopfloorIds, // Add Shopfloor layer containers (Systems, Devices)
        ...sharedCloudIds      // Management Cockpit
      ],
      highlightedContainerIds: ['app-server', 'agent', 'disi', 'disc', 'event-bus'],  // Removed 'db' from highlights
      visibleConnectionIds: [
        ...allInternalConnectionIds, 
        'app-server-dashboard',        // App Server → SmartFactory Dashboard
        'agent-cockpit',               // Agent → Management Cockpit
        'disi-shopfloor-systems',      // DISI → Shopfloor Systems
        'disi-shopfloor-devices',      // DISI → Shopfloor Devices
        'disc-erp',                    // DISC → ERP Application
        'event-bus-datalake'           // Event Bus → Data Lake (NO db-datalake connection)
      ],
      highlightedConnectionIds: [
        'disi-shopfloor-systems',      // Highlight new connections in Step 4
        'disi-shopfloor-devices',
        'disc-erp',
        'event-bus-datalake'
      ],
      showFullArchitecture: true,
    },
  ];
}
