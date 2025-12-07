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

// SVG viewBox dimensions
export const EDGE_VIEWBOX_WIDTH = 1200;
export const EDGE_VIEWBOX_HEIGHT = 600;

// Layout constants for Steps 1-2 (detail view)
export const EDGE_LAYOUT = {
  // Main EDGE container
  EDGE_X: 100,
  EDGE_Y: 120,
  EDGE_WIDTH: 1000,
  EDGE_HEIGHT: 380,
  
  // Component boxes inside EDGE - taller boxes for icon above label
  BOX_WIDTH: 150,
  BOX_HEIGHT: 80,  // Increased height for icon on top, label below
  
  // Spacing - 3 rows with equal vertical distribution, closer to edges
  ROW_1_Y: 140,  // DISC, Event Bus (closer to top)
  ROW_2_Y: 270,  // App Server, Router, Agent (center)
  ROW_3_Y: 400,  // Log Server, DISI, Edge Database (closer to bottom)
  
  // External zones
  BUSINESS_ZONE_Y: 40,
  BUSINESS_ZONE_HEIGHT: 50,
  SHOPFLOOR_ZONE_Y: 530,
  SHOPFLOOR_ZONE_HEIGHT: 50,
};

// Scaled layout for Steps 3-4 (integrated in full architecture)
// Components scaled to ~40% to fit in DSP Edge box (approximately 500x200px)
export const EDGE_LAYOUT_SCALED = {
  // Scaling factor to fit within full architecture EDGE box
  SCALE: 0.4,
  
  // Offset to center scaled components within the EDGE box in full architecture
  OFFSET_X: 375,   // Center horizontally in the DSP layer
  OFFSET_Y: 330,   // Position in DSP layer
  
  // Scaled dimensions
  BOX_WIDTH: 60,   // 40% of 150
  BOX_HEIGHT: 32,  // 40% of 80
  ICON_SIZE: 15,   // Scaled down from 38px
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
  
  // Row 1: DISC and Event Bus (evenly distributed)
  containers.push({
    id: 'disc',
    label: 'DISC',
    x: EDGE_LAYOUT.EDGE_X + 200,  // Left position in row 1
    y: EDGE_LAYOUT.ROW_1_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-disc.svg',
  });
  
  containers.push({
    id: 'event-bus',
    label: 'Event Bus',
    x: EDGE_LAYOUT.EDGE_X + 650,  // Right position in row 1
    y: EDGE_LAYOUT.ROW_1_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-event-bus.svg',
  });
  
  // Row 2: App Server, Router, Agent (evenly distributed)
  containers.push({
    id: 'app-server',
    label: 'App Server',
    x: EDGE_LAYOUT.EDGE_X + 100,  // Left position in row 2
    y: EDGE_LAYOUT.ROW_2_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-app-server.svg',
  });
  
  containers.push({
    id: 'router',
    label: 'Router',
    x: EDGE_LAYOUT.EDGE_X + 425,  // Center position in row 2
    y: EDGE_LAYOUT.ROW_2_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-router.svg',
  });
  
  containers.push({
    id: 'agent',
    label: 'Agent',
    x: EDGE_LAYOUT.EDGE_X + 750,  // Right position in row 2
    y: EDGE_LAYOUT.ROW_2_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-agent.svg',
  });
  
  // Row 3: Log Server, DISI, Edge Database (evenly distributed, same as Row 2)
  containers.push({
    id: 'log-server',
    label: 'Log Server',
    x: EDGE_LAYOUT.EDGE_X + 100,  // Left position in row 3 (same as App Server)
    y: EDGE_LAYOUT.ROW_3_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-log-server.svg',
  });
  
  containers.push({
    id: 'disi',
    label: 'DISI',
    x: EDGE_LAYOUT.EDGE_X + 425,  // Center position in row 3 (same as Router)
    y: EDGE_LAYOUT.ROW_3_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-disi.svg',
  });
  
  containers.push({
    id: 'db',
    label: 'Edge Database',
    x: EDGE_LAYOUT.EDGE_X + 750,  // Right position in row 3 (same as Agent)
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
    // DISI to Shopfloor Systems/Devices
    { id: 'disi-shopfloor', from: 'disi', to: 'shopfloor-systems', state: 'hidden' },
    // DISC to ERP Application (Business Process Layer)
    { id: 'disc-erp', from: 'disc', to: 'business-erp', state: 'hidden' },
    // Event Bus to Data Lake
    { id: 'event-bus-datalake', from: 'event-bus', to: 'business-data-lake', state: 'hidden' },
    // Edge Database to Data Lake
    { id: 'db-datalake', from: 'db', to: 'business-data-lake', state: 'hidden' },
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
    
    // Step 3: Vertical Context (now with FULL architecture)
    {
      id: 'step-3',
      label: $localize`:@@edgeAnimStep3:Business ↔ Edge ↔ Shopfloor`,
      description: $localize`:@@edgeAnimStep3Desc:Edge acts as the real-time bridge between shopfloor devices and business systems.`,
      visibleContainerIds: [
        'edge-container', 
        ...allComponentIds, 
        ...sharedBusinessIds,
        ...sharedShopfloorIds,
        ...sharedCloudIds
      ],
      highlightedContainerIds: ['app-server', 'disi', 'agent', 'disc'],
      visibleConnectionIds: [
        ...allInternalConnectionIds, 
        'app-server-dashboard', 
        'disi-shopfloor',
        'agent-cockpit',
        'disc-erp'
      ],
      highlightedConnectionIds: ['app-server-dashboard', 'disi-shopfloor', 'agent-cockpit', 'disc-erp'],
      showFullArchitecture: true,
    },
    
    // Step 4: Integration into Full Architecture (now with all shared containers and all connections)
    {
      id: 'step-4',
      label: $localize`:@@edgeAnimStep4:Integration into Full Architecture`,
      description: $localize`:@@edgeAnimStep4Desc:Edge components connect SmartFactory dashboards, management cockpit, shopfloor assets and analytics platforms.`,
      visibleContainerIds: [
        'edge-container', 
        ...allComponentIds, 
        ...sharedBusinessIds,
        ...sharedShopfloorIds,
        ...sharedCloudIds
      ],
      highlightedContainerIds: ['app-server', 'agent', 'disi', 'disc', 'db', 'event-bus'],
      visibleConnectionIds: [
        ...allInternalConnectionIds, 
        'app-server-dashboard', 
        'agent-cockpit',
        'disi-shopfloor',
        'disc-erp',
        'db-datalake',
        'event-bus-datalake'
      ],
      highlightedConnectionIds: [
        'app-server-dashboard', 
        'agent-cockpit',
        'disi-shopfloor',
        'disc-erp',
        'db-datalake',
        'event-bus-datalake'
      ],
      showFullArchitecture: true,
    },
  ];
}
