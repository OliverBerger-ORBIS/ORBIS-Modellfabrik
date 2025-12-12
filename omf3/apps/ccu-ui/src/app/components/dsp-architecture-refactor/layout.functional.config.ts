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
        'bp-mes',
        'bp-erp',
        'bp-cloud',
        'bp-analytics',
        'bp-data-lake',
        'dsp-edge',
        'dsp-mc',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['layer-bp', 'bp-mes', 'bp-erp', 'bp-cloud', 'bp-analytics', 'bp-data-lake'],
      visibleConnectionIds: [
        'conn-dsp-edge-dsp-mc',
        'conn-bp-mes-dsp-edge',
        'conn-bp-erp-dsp-edge',
        'conn-bp-cloud-dsp-edge',
        'conn-bp-analytics-dsp-edge',
        'conn-bp-data-lake-dsp-edge',
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [
        'conn-bp-mes-dsp-edge',
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

    // Step 13: Autonomous & Adaptive Enterprise
    {
      id: 'step-13',
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

    // Step 14: Complete Overview
    {
      id: 'step-14',
      label: $localize`:@@dspArchStep13:Complete DSP Architecture`,
      description: '',
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
      highlightedContainerIds: [],
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
      highlightedConnectionIds: [],
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
