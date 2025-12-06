/**
 * Configuration for the animated DSP Edge Architecture diagram.
 * Defines containers, connections, and 4-step animation sequence.
 */

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
}

// SVG viewBox dimensions
export const EDGE_VIEWBOX_WIDTH = 1200;
export const EDGE_VIEWBOX_HEIGHT = 600;

// Layout constants
export const EDGE_LAYOUT = {
  // Main EDGE container
  EDGE_X: 100,
  EDGE_Y: 120,
  EDGE_WIDTH: 1000,
  EDGE_HEIGHT: 380,
  
  // Component boxes inside EDGE
  BOX_WIDTH: 150,
  BOX_HEIGHT: 60,
  
  // Spacing
  ROW_1_Y: 160,  // DISC
  ROW_2_Y: 260,  // App Server, Router, Agent
  ROW_3_Y: 360,  // Log Server, DISI, Edge DB, Event Bus
  
  // External zones
  BUSINESS_ZONE_Y: 40,
  BUSINESS_ZONE_HEIGHT: 50,
  SHOPFLOOR_ZONE_Y: 530,
  SHOPFLOOR_ZONE_HEIGHT: 50,
};

/**
 * Create edge component containers
 */
export function createEdgeContainers(): EdgeContainerConfig[] {
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
  
  // Row 1: DISC (centered)
  containers.push({
    id: 'disc',
    label: 'DISC',
    x: EDGE_LAYOUT.EDGE_X + 425,
    y: EDGE_LAYOUT.ROW_1_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-disc.svg',
  });
  
  // Row 2: App Server, Router, Agent
  containers.push({
    id: 'app-server',
    label: 'App Server',
    x: EDGE_LAYOUT.EDGE_X + 150,
    y: EDGE_LAYOUT.ROW_2_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-app-server.svg',
  });
  
  containers.push({
    id: 'router',
    label: 'Router',
    x: EDGE_LAYOUT.EDGE_X + 425,
    y: EDGE_LAYOUT.ROW_2_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-router.svg',
  });
  
  containers.push({
    id: 'agent',
    label: 'Agent',
    x: EDGE_LAYOUT.EDGE_X + 700,
    y: EDGE_LAYOUT.ROW_2_Y,
    width: EDGE_LAYOUT.BOX_WIDTH,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-agent.svg',
  });
  
  // Row 3: Log Server, DISI, Edge DB, Event Bus
  containers.push({
    id: 'log-server',
    label: 'Log Server',
    x: EDGE_LAYOUT.EDGE_X + 70,
    y: EDGE_LAYOUT.ROW_3_Y,
    width: 140,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-log-server.svg',
  });
  
  containers.push({
    id: 'disi',
    label: 'DISI',
    x: EDGE_LAYOUT.EDGE_X + 290,
    y: EDGE_LAYOUT.ROW_3_Y,
    width: 140,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-disi.svg',
  });
  
  containers.push({
    id: 'db',
    label: 'Edge Database',
    x: EDGE_LAYOUT.EDGE_X + 510,
    y: EDGE_LAYOUT.ROW_3_Y,
    width: 140,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-database.svg',
  });
  
  containers.push({
    id: 'event-bus',
    label: 'Event Bus',
    x: EDGE_LAYOUT.EDGE_X + 730,
    y: EDGE_LAYOUT.ROW_3_Y,
    width: 140,
    height: EDGE_LAYOUT.BOX_HEIGHT,
    state: 'hidden',
    icon: 'assets/svg/dsp/edge-components/edge-event-bus.svg',
  });
  
  // External zones (for Step 3 & 4)
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
    
    // External connections (Step 3)
    { id: 'disc-business', from: 'disc', to: 'business-zone', state: 'hidden' },
    { id: 'app-server-business', from: 'app-server', to: 'business-zone', state: 'hidden' },
    { id: 'disi-shopfloor', from: 'disi', to: 'shopfloor-zone', state: 'hidden' },
    { id: 'agent-shopfloor', from: 'agent', to: 'shopfloor-zone', state: 'hidden' },
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
    
    // Step 3: Vertical Context
    {
      id: 'step-3',
      label: $localize`:@@edgeAnimStep3:Business ↔ Edge ↔ Shopfloor`,
      description: $localize`:@@edgeAnimStep3Desc:Edge acts as the real-time bridge between shopfloor devices and business systems.`,
      visibleContainerIds: ['edge-container', ...allComponentIds, 'business-zone', 'shopfloor-zone'],
      highlightedContainerIds: ['disc', 'app-server', 'disi', 'agent'],
      visibleConnectionIds: [...allInternalConnectionIds, 'disc-business', 'app-server-business', 'disi-shopfloor', 'agent-shopfloor'],
      highlightedConnectionIds: ['disc-business', 'app-server-business', 'disi-shopfloor', 'agent-shopfloor'],
      showBusinessZone: true,
      showShopfloorZone: true,
      showExternalConnections: true,
    },
    
    // Step 4: Integration into Full Architecture
    {
      id: 'step-4',
      label: $localize`:@@edgeAnimStep4:Integration into Full Architecture`,
      description: $localize`:@@edgeAnimStep4Desc:Edge components connect SmartFactory dashboards, management cockpit, shopfloor assets and analytics platforms.`,
      visibleContainerIds: ['edge-container', ...allComponentIds, 'business-zone', 'shopfloor-zone'],
      highlightedContainerIds: ['app-server', 'agent', 'disi', 'db', 'event-bus'],
      visibleConnectionIds: [...allInternalConnectionIds, 'disc-business', 'app-server-business', 'disi-shopfloor', 'agent-shopfloor'],
      highlightedConnectionIds: ['app-server-business', 'agent-shopfloor', 'router-db', 'router-event-bus'],
      showBusinessZone: true,
      showShopfloorZone: true,
      showExternalConnections: true,
    },
  ];
}
