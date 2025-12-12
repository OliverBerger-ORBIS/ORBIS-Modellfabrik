import type { ContainerConfig, ConnectionConfig, StepConfig, DiagramConfig } from './types';
import {
  createDefaultContainers,
  createDefaultConnections,
  VIEWBOX_WIDTH,
  VIEWBOX_HEIGHT,
} from './layout.shared.config';

export { VIEWBOX_WIDTH, VIEWBOX_HEIGHT, LAYOUT } from './layout.shared.config';

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

    // Step 4: Interoperability
    {
      id: 'step-4',
      label: $localize`:@@dspArchStepInterop:Interoperability`,
      description: $localize`:@@dspArchStepInteropDesc:DSP enables manufacturer-independent, event-driven communication between machines, shopfloor systems and IT platforms.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: [],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-interoperability'],
    },

    // Step 5: Shopfloor Connectivity
    {
      id: 'step-5',
      label: $localize`:@@dspArchStepConnectivity:Shopfloor Connectivity`,
      description: $localize`:@@dspArchStepConnectivityDesc:DSP connects machines, sensors, logistics systems and shopfloor assets through direct, bidirectional communication without modifying existing control logic.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: baseShopfloorConnections,
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-network'],
    },

    // Step 6: Event-Driven Processing
    {
      id: 'step-6',
      label: $localize`:@@dspArchStepEvent:Event-Driven Processing`,
      description: $localize`:@@dspArchStepEventDesc:DSP processes shopfloor events in real time and transforms technical signals into meaningful process-relevant information.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: [],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-event-driven'],
    },

    // Step 7: Decentralized Process Choreography
    {
      id: 'step-7',
      label: $localize`:@@dspArchStepChoreo:Decentralized Process Choreography`,
      description: $localize`:@@dspArchStepChoreoDesc:DSP enables decentralized, resilient process execution where autonomous process objects coordinate actions without central monolithic control.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: [],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-choreography'],
    },

    // Step 8: Digital Twin
    {
      id: 'step-8',
      label: $localize`:@@dspArchStepDigitalTwin:Digital Twin`,
      description: $localize`:@@dspArchStepDigitalTwinDesc:DSP creates a real-time digital representation of machines, processes and workpieces by consolidating data from multiple systems.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: [],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-digital-twin'],
    },

    // Step 9: Platform Independence / Best-of-Breed
    {
      id: 'step-9',
      label: $localize`:@@dspArchStepBestBreed:Platform Independence & Best-of-Breed Integration`,
      description: $localize`:@@dspArchStepBestBreedDesc:DSP integrates heterogeneous ERP, MES, cloud and analytics systems while remaining independent of vendors, platforms and hyperscalers.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: [],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-best-of-breed'],
    },

    // Step 10: Business & Analytics Integration
    {
      id: 'step-10',
      label: $localize`:@@dspArchStepAnalytics:Business & Analytics Integration`,
      description: $localize`:@@dspArchStepAnalyticsDesc:DSP synchronizes shopfloor events and digital twins with business systems, data lakes and analytics platforms to enable end-to-end visibility.`,
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        'bp-mes',
        'bp-erp',
        'bp-cloud',
        'bp-analytics',
        'bp-data-lake',
        'dsp-edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['bp-analytics', 'bp-cloud'],
      visibleConnectionIds: [
        'conn-bp-mes-dsp-edge',
        'conn-bp-erp-dsp-edge',
        'conn-bp-cloud-dsp-edge',
        'conn-bp-analytics-dsp-edge',
        'conn-bp-data-lake-dsp-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: ['conn-bp-analytics-dsp-edge', 'conn-bp-cloud-dsp-edge'],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-analytics'],
    },

    // Step 11: AI Enablement
    {
      id: 'step-11',
      label: $localize`:@@dspArchStepAI:AI & Analytics Enablement`,
      description: $localize`:@@dspArchStepAIDesc:DSP provides structured, real-time data as the foundation for analytics, machine learning and predictive optimization use cases.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: baseShopfloorConnections,
      highlightedConnectionIds: [],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-ai-enablement'],
    },

    // Step 12: Autonomous & Adaptive Enterprise
    {
      id: 'step-12',
      label: $localize`:@@dspArchStepAuto:Autonomous & Adaptive Enterprise (Target State)`,
      description: $localize`:@@dspArchStepAutoDesc:DSP enables the transition toward autonomous, adaptive manufacturing where processes continuously optimize themselves based on real-time data.`,
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        'bp-mes',
        'bp-erp',
        'bp-cloud',
        'bp-analytics',
        'bp-data-lake',
        'dsp-ux',
        'dsp-edge',
        'dsp-mc',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['layer-bp', 'layer-dsp', 'dsp-edge', 'dsp-mc', 'bp-analytics'],
      visibleConnectionIds: [
        'conn-dsp-ux-dsp-edge',
        'conn-dsp-edge-dsp-mc',
        'conn-bp-mes-dsp-edge',
        'conn-bp-erp-dsp-edge',
        'conn-bp-cloud-dsp-edge',
        'conn-bp-analytics-dsp-edge',
        'conn-bp-data-lake-dsp-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [
        'conn-dsp-edge-dsp-mc',
        'conn-bp-analytics-dsp-edge',
        'conn-bp-cloud-dsp-edge',
      ],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-autonomous-enterprise'],
    },

    // Step 13: Management Cockpit
    {
      id: 'step-13',
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

    // Step 14: SmartFactory Dashboard
    {
      id: 'step-14',
      label: $localize`:@@dspArchStep11:SmartFactory Dashboard`,
      description: $localize`:@@dspArchStep11Desc:Visualization of the digital twin, real-time processes, and track & trace in the shopfloor.`,
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        'bp-mes',
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
        'conn-bp-mes-dsp-edge',
        'conn-bp-erp-dsp-edge',
        'conn-bp-cloud-dsp-edge',
        'conn-bp-analytics-dsp-edge',
        'conn-bp-data-lake-dsp-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: ['conn-dsp-ux-dsp-edge'],
      showFunctionIcons: true,
    },

    // Step 15: Autonomous & Adaptive Enterprise (Zielbild)
    {
      id: 'step-15',
      label: $localize`:@@dspArchStep12:Autonomous & Adaptive Enterprise`,
      description: $localize`:@@dspArchStep12Desc:Data from shopfloor, Edge, ERP, analytics, and data lakes enable autonomous workflows, predictive decisions, and continuous process optimization.`,
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        'bp-mes',
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
        'bp-mes',
        'bp-erp',
        'bp-cloud',
        'bp-analytics',
        'bp-data-lake',
      ],
      visibleConnectionIds: [
        'conn-dsp-ux-dsp-edge',
        'conn-dsp-edge-dsp-mc',
        'conn-bp-mes-dsp-edge',
        'conn-bp-erp-dsp-edge',
        'conn-bp-cloud-dsp-edge',
        'conn-bp-analytics-dsp-edge',
        'conn-bp-data-lake-dsp-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [
        'conn-dsp-ux-dsp-edge',
        'conn-dsp-edge-dsp-mc',
        'conn-bp-mes-dsp-edge',
        'conn-bp-erp-dsp-edge',
        'conn-bp-cloud-dsp-edge',
        'conn-bp-analytics-dsp-edge',
        'conn-bp-data-lake-dsp-edge',
      ],
      showFunctionIcons: true,
    },
  ];
}

export function createFunctionalView(): DiagramConfig {
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
