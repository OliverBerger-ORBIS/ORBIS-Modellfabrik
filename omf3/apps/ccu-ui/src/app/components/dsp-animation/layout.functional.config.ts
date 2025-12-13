import type { ContainerConfig, ConnectionConfig, StepConfig, DiagramConfig } from './types';
import { DiagramConfigBuilder } from './layout.builder';
import {
  getShopfloorContainerIds,
  getShopfloorDeviceIds,
  getShopfloorConnectionIds,
  getDspContainerIds,
  getBusinessContainerIds,
} from './layout.shared.config';

export { VIEWBOX_WIDTH, VIEWBOX_HEIGHT, LAYOUT } from './layout.shared.config';

export function createDefaultSteps(): StepConfig[] {
  const baseShopfloorContainers = getShopfloorContainerIds();
  const baseShopfloorConnections = getShopfloorConnectionIds();

  return [
    // Step 1: Shopfloor Devices
    {
      id: 'step-1',
      label: $localize`:@@dspArchStep1:Shopfloor Devices`,
      description: $localize`:@@dspArchStep1Desc:DSP connects heterogeneous devices in the shopfloor without interfering with machine logic.`,
      visibleContainerIds: [
        'layer-sf',
        'sf-devices-group',
        ...getShopfloorDeviceIds(),
      ],
      highlightedContainerIds: [
        'sf-devices-group',
        ...getShopfloorDeviceIds(),
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
      label: $localize`:@@dspArchStepInterop:Interoperabilität`,
      description: $localize`:@@dspArchStepInteropDesc:DSP ermöglicht herstellerunabhängige, ereignisgesteuerte Kommunikation zwischen Maschinen, Shopfloor-Systemen und IT-Plattformen.`,
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
      label: $localize`:@@dspArchStepConnectivity:Shopfloor-Konnektivität`,
      description: $localize`:@@dspArchStepConnectivityDesc:DSP verbindet Maschinen, Sensoren, Logistiksysteme und Shopfloor-Assets über direkte, bidirektionale Kommunikation – ohne Eingriffe in bestehende Steuerungslogik.`,
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
      label: $localize`:@@dspArchStepEvent:Ereignisgesteuerte Verarbeitung`,
      description: $localize`:@@dspArchStepEventDesc:DSP verarbeitet Shopfloor-Ereignisse in Echtzeit und übersetzt technische Signale in prozessrelevante Informationen.`,
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
      label: $localize`:@@dspArchStepChoreo:Dezentrale Prozesschoreografie`,
      description: $localize`:@@dspArchStepChoreoDesc:DSP ermöglicht dezentrale, resiliente Prozessausführung, bei der autonome Prozessobjekte ohne zentrale monolithische Steuerung zusammenarbeiten.`,
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
      label: $localize`:@@dspArchStepDigitalTwin:Digitaler Zwilling`,
      description: $localize`:@@dspArchStepDigitalTwinDesc:DSP erzeugt ein digitales Echtzeit-Abbild von Maschinen, Prozessen und Werkstücken durch die Zusammenführung von Daten aus verschiedenen Systemen.`,
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
      label: $localize`:@@dspArchStepBestBreed:Plattformunabhängigkeit & Best-of-Breed-Integration`,
      description: $localize`:@@dspArchStepBestBreedDesc:DSP integriert heterogene ERP-, MES-, Cloud- und Analytics-Systeme und bleibt dabei unabhängig von Herstellern, Plattformen und Hyperscalern.`,
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
      label: $localize`:@@dspArchStepAnalytics:Business- & Analytics-Integration`,
      description: $localize`:@@dspArchStepAnalyticsDesc:DSP synchronisiert Shopfloor-Ereignisse und digitale Zwillinge mit Business-Systemen, Data Lakes und Analytics-Plattformen für durchgängige Transparenz.`,
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
      label: $localize`:@@dspArchStepAI:AI- & Analytics-Enablement`,
      description: $localize`:@@dspArchStepAIDesc:DSP stellt strukturierte Echtzeitdaten als Grundlage für Analytics, Machine Learning und prädiktive Optimierung bereit.`,
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
      label: $localize`:@@dspArchStepAuto:Autonomes & Adaptives Unternehmen (Zielbild)`,
      description: $localize`:@@dspArchStepAutoDesc:DSP ermöglicht den Übergang zu einer autonomen, adaptiven Fertigung, in der sich Prozesse kontinuierlich auf Basis von Echtzeitdaten selbst optimieren.`,
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

    // Step 14: SmartFactory Dashboard (full context, all objects visible, MC highlighted)
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
      highlightedContainerIds: ['dsp-mc'],
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
      highlightedConnectionIds: ['conn-dsp-edge-dsp-mc'],
      showFunctionIcons: true,
    },

    // Step 15: Organization & Asset Modeling (MC)
    {
      id: 'step-15',
      label: $localize`:@@dspMcStepOrg:Organization & Asset Modeling`,
      description: $localize`:@@dspMcStepOrgDesc:The Management Cockpit centrally models shopfloor structures, assets and connected systems across all sites.`,
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
      highlightedContainerIds: ['dsp-mc'],
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
      highlightedConnectionIds: ['conn-dsp-edge-dsp-mc'],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['mc-hierarchical-structure'],
    },

    // Step 16: Process & Data Flow Configuration (MC)
    {
      id: 'step-16',
      label: $localize`:@@dspMcStepFlow:Process & Data Flow Configuration`,
      description: $localize`:@@dspMcStepFlowDesc:The Management Cockpit defines process models and controls how events and data are routed between shopfloor, business and cloud systems.`,
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
      highlightedContainerIds: ['dsp-mc'],
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
      highlightedConnectionIds: ['conn-dsp-edge-dsp-mc'],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['mc-orchestration'],
    },

    // Step 17: Central Governance & Orchestration (MC)
    {
      id: 'step-17',
      label: $localize`:@@dspMcStepGov:Central Governance & Orchestration`,
      description: $localize`:@@dspMcStepGovDesc:The Management Cockpit centrally governs, configures and orchestrates all DSP Edge nodes across locations and environments.`,
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
      highlightedContainerIds: ['dsp-mc'],
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
      highlightedConnectionIds: ['conn-dsp-edge-dsp-mc'],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['mc-governance'],
    },

    // Step 18: MC Edge Segment (3x edge box)
    {
      id: 'step-18',
      label: $localize`:@@dspMcStepEdge:Edge Node Visualization`,
      description: $localize`:@@dspMcStepEdgeDesc:Management Cockpit displaying three DSP Edge nodes within a 120° segment.`,
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
      highlightedContainerIds: ['dsp-mc', 'dsp-edge'],
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
      highlightedConnectionIds: ['conn-dsp-edge-dsp-mc'],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['logo-edge-a', 'logo-edge-b', 'logo-edge-c'],
    },

    // Step 19: Autonomous & Adaptive Enterprise (Zielbild)
    {
      id: 'step-19',
      label: $localize`:@@dspArchStep12:Autonomous & Adaptive Enterprise`,
      description: $localize`:@@dspArchStep12Desc:Data from shopfloor, Edge, ERP, analytics, and data lakes enable autonomous workflows, predictive decisions, and continuous process optimization.`,
      visibleContainerIds: [
        ...getBusinessContainerIds(),
        ...getDspContainerIds(),
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: [
        ...getBusinessContainerIds(),
        ...getDspContainerIds(),
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
  return new DiagramConfigBuilder()
    .withFunctionalSteps(createDefaultSteps())
    .build();
}
