import type { ContainerConfig, ConnectionConfig, StepConfig, DiagramConfig } from './types';
import { DiagramConfigBuilder } from './layout.builder';
import { getEdgeComponentIds } from './layout.shared.config';

export function createComponentView(): DiagramConfig {
  // Add bidirectional connections between edge components
  // All components connect to Router as the central hub
  const edgeComponentConnections: ConnectionConfig[] = [
    // Internal router connections
    { id: 'conn-ec-disc-router', fromId: 'edge-comp-disc', toId: 'edge-comp-router', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-eventbus-router', fromId: 'edge-comp-event-bus', toId: 'edge-comp-router', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-appserver-router', fromId: 'edge-comp-app-server', toId: 'edge-comp-router', fromSide: 'right', toSide: 'left', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-agent-router', fromId: 'edge-comp-agent', toId: 'edge-comp-router', fromSide: 'left', toSide: 'right', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-logserver-router', fromId: 'edge-comp-log-server', toId: 'edge-comp-router', fromSide: 'top', toSide: 'bottom', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-disi-router', fromId: 'edge-comp-disi', toId: 'edge-comp-router', fromSide: 'top', toSide: 'bottom', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-database-router', fromId: 'edge-comp-database', toId: 'edge-comp-router', fromSide: 'top', toSide: 'bottom', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },

    // DISI to Shopfloor Systems
    { id: 'conn-ec-disi-sf-system-bp', fromId: 'edge-comp-disi', toId: 'sf-system-bp', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-disi-sf-system-fts', fromId: 'edge-comp-disi', toId: 'sf-system-fts', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-disi-sf-system-warehouse', fromId: 'edge-comp-disi', toId: 'sf-system-warehouse', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-disi-sf-system-factory', fromId: 'edge-comp-disi', toId: 'sf-system-factory', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },

    // DISI to Shopfloor Devices
    { id: 'conn-ec-disi-sf-device-mill', fromId: 'edge-comp-disi', toId: 'sf-device-mill', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-disi-sf-device-drill', fromId: 'edge-comp-disi', toId: 'sf-device-drill', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-disi-sf-device-aiqs', fromId: 'edge-comp-disi', toId: 'sf-device-aiqs', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-disi-sf-device-hbw', fromId: 'edge-comp-disi', toId: 'sf-device-hbw', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-disi-sf-device-dps', fromId: 'edge-comp-disi', toId: 'sf-device-dps', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-disi-sf-device-chrg', fromId: 'edge-comp-disi', toId: 'sf-device-chrg', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-disi-sf-device-conveyor', fromId: 'edge-comp-disi', toId: 'sf-device-conveyor', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-disi-sf-device-stone-oven', fromId: 'edge-comp-disi', toId: 'sf-device-stone-oven', fromSide: 'bottom', toSide: 'top', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },

    // Business / UX integrations
    { id: 'conn-ec-disc-bp-erp', fromId: 'edge-comp-disc', toId: 'bp-erp', fromSide: 'top', toSide: 'bottom', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ux-ec-appserver', fromId: 'dsp-ux', toId: 'edge-comp-app-server', fromSide: 'right', toSide: 'left', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
    { id: 'conn-ec-agent-management', fromId: 'edge-comp-agent', toId: 'dsp-mc', fromSide: 'right', toSide: 'left', state: 'hidden', hasArrow: true, bidirectional: true, arrowSize: 6 },
  ];
  
  const baseShopfloorContainers = [
    'sf-systems-group',
    'sf-system-bp',
    'sf-system-fts',
    'sf-system-warehouse',
    'sf-system-factory',
    'sf-devices-group',
    'sf-device-mill',
    'sf-device-drill',
    'sf-device-aiqs',
    'sf-device-hbw',
    'sf-device-dps',
    'sf-device-chrg',
    'sf-device-conveyor',
    'sf-device-stone-oven',
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
    'conn-ec-disi-sf-system-warehouse',
    'conn-ec-disi-sf-system-factory',
    'conn-ec-disi-sf-device-mill',
    'conn-ec-disi-sf-device-drill',
    'conn-ec-disi-sf-device-aiqs',
    'conn-ec-disi-sf-device-hbw',
    'conn-ec-disi-sf-device-dps',
    'conn-ec-disi-sf-device-chrg',
    'conn-ec-disi-sf-device-conveyor',
    'conn-ec-disi-sf-device-stone-oven',
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
        ...getEdgeComponentIds(),
      ],
      highlightedContainerIds: getEdgeComponentIds(),
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
        ...getEdgeComponentIds(),
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
        'bp-mes',
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
        'bp-mes',
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
        'bp-mes',
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
        'bp-mes',
        'bp-erp',
        'layer-dsp',
        'dsp-ux',
        'dsp-edge',
        'dsp-mc',
        ...getEdgeComponentIds(),
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
  
  return new DiagramConfigBuilder()
    .withComponentView(steps, edgeComponentConnections)
    .build();
}
