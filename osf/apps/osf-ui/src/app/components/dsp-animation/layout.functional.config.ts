import type { ContainerConfig, ConnectionConfig, StepConfig, DiagramConfig } from './types';
import { DiagramConfigBuilder } from './layout.builder';
import type { CustomerDspConfig } from './configs/types';
import {
  getShopfloorContainerIds,
  getShopfloorDeviceIds,
  getShopfloorConnectionIds,
  getDspContainerIds,
  getBusinessContainerIds,
  getBpProcessContainerIds,
} from './layout.shared.config';

export { VIEWBOX_WIDTH, VIEWBOX_HEIGHT, LAYOUT } from './layout.shared.config';

/**
 * Helper function to generate connection IDs using new naming convention: conn_<from-id>_<to-id>
 */
function conn(fromId: string, toId: string): string {
  return `conn_${fromId}_${toId}`;
}

/**
 * Helper function to generate business process connection IDs
 */
function getBpConnections(customerConfig?: CustomerDspConfig): string[] {
  if (customerConfig) {
    return customerConfig.bpProcesses.map(bp => conn(bp.id, 'dsp-edge'));
  }
  return [
    conn('bp-erp', 'dsp-edge'),
    conn('bp-mes', 'dsp-edge'),
    conn('bp-cloud', 'dsp-edge'),
    conn('bp-analytics', 'dsp-edge'),
    conn('bp-data-lake', 'dsp-edge'),
  ];
}

function moveInteroperabilitySummaryToStep12(steps: StepConfig[]): StepConfig[] {
  const orderedIds = ['step-4', 'step-5', 'step-6', 'step-7', 'step-8', 'step-9', 'step-10', 'step-11', 'step-12'];
  const originals = orderedIds
    .map((id) => steps.find((step) => step.id === id))
    .filter((step): step is StepConfig => Boolean(step))
    .map((step) => ({ ...step }));

  if (originals.length !== orderedIds.length) {
    return steps;
  }

  const rotated = originals.slice(1).concat(originals[0]);
  const stepById = new Map(steps.map((step) => [step.id, step]));

  for (let i = 0; i < orderedIds.length; i += 1) {
    const targetId = orderedIds[i];
    const target = stepById.get(targetId);
    const source = rotated[i];
    if (!target || !source) {
      continue;
    }
    target.label = source.label;
    target.description = source.description;
    target.visibleContainerIds = source.visibleContainerIds;
    target.highlightedContainerIds = source.highlightedContainerIds;
    target.visibleConnectionIds = source.visibleConnectionIds;
    target.highlightedConnectionIds = source.highlightedConnectionIds;
    target.showFunctionIcons = source.showFunctionIcons;
    target.highlightedFunctionIcons = source.highlightedFunctionIcons;
  }

  return steps;
}

export function createDefaultSteps(customerConfig?: CustomerDspConfig): StepConfig[] {
  const baseShopfloorContainers = getShopfloorContainerIds(customerConfig);
  const baseShopfloorConnections = getShopfloorConnectionIds(customerConfig);
  const bpConnections = getBpConnections(customerConfig);
  const bpProcessIds = getBpProcessContainerIds(customerConfig);
  const bpFocusIds = ['bp-erp', 'bp-mes', 'bp-ewm', 'bp-crm'];
  const bpFocusConnections = bpFocusIds.map((id) => conn(id, 'dsp-edge'));
  const bpStep7VisibleIds = ['bp-erp', 'bp-mes', 'bp-ewm'].filter((id) => bpProcessIds.includes(id));
  const bpStep7VisibleConnections = bpStep7VisibleIds.map((id) => conn(id, 'dsp-edge')).filter((id) => bpConnections.includes(id));
  const bpWithoutAnalyticsAndDataLake = bpProcessIds.filter((id) => id !== 'bp-analytics' && id !== 'bp-data-lake');
  const bpWithoutAnalyticsAndDataLakeConnections = bpWithoutAnalyticsAndDataLake
    .map((id) => conn(id, 'dsp-edge'))
    .filter((id) => bpConnections.includes(id));
  const bpWithoutDataLake = bpProcessIds.filter((id) => id !== 'bp-data-lake');
  const bpWithoutDataLakeConnections = bpWithoutDataLake
    .map((id) => conn(id, 'dsp-edge'))
    .filter((id) => bpConnections.includes(id));
  const step14Highlights = ['dsp-mc', 'sf-devices-group'];
  if (bpProcessIds.includes('bp-erp')) {
    step14Highlights.push('bp-erp');
  }
  const step15Highlights = ['dsp-mc'];
  if (bpProcessIds.includes('bp-mes')) {
    step15Highlights.push('bp-mes');
  }
  if (baseShopfloorContainers.includes('sf-system-fts')) {
    step15Highlights.push('sf-system-fts');
  }

  const steps: StepConfig[] = [
    // Step 1: Shopfloor Devices
    {
      id: 'step-1',
      label: $localize`:@@dspArchStep1:Shopfloor Devices`,
      description: $localize`:@@dspArchStep1Desc:DSP connects heterogeneous devices in the shopfloor without interfering with machine logic.`,
      visibleContainerIds: [
        'layer-sf',
        'sf-devices-group',
        ...getShopfloorDeviceIds(customerConfig),
      ],
      highlightedContainerIds: [
        'sf-devices-group',
        ...getShopfloorDeviceIds(customerConfig),
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
      highlightedContainerIds: customerConfig 
        ? ['sf-systems-group', ...customerConfig.sfSystems.map(s => s.id)]
        : ['sf-systems-group', 'sf-system-any', 'sf-system-fts'],
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
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        ...getBpProcessContainerIds(customerConfig),
        'dsp-edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: [
        'dsp-edge',
        ...(customerConfig ? ['bp-mes', 'bp-ewm', 'bp-crm'] : ['bp-mes']),
        ...(customerConfig ? ['sf-system-fts', 'sf-device-aiqs', 'sf-device-hbw'] : ['sf-system-fts', 'sf-device-aiqs', 'sf-device-hbw']),
      ],
      visibleConnectionIds: [
        ...bpConnections,
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [
        conn('bp-mes', 'dsp-edge'),
        conn('bp-ewm', 'dsp-edge'),
        conn('bp-crm', 'dsp-edge'),
        conn('dsp-edge', 'sf-system-fts'),
        conn('dsp-edge', 'sf-device-aiqs'),
        conn('dsp-edge', 'sf-device-hbw'),
      ].filter((id) => [...bpConnections, ...baseShopfloorConnections].includes(id)),
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-interoperability'], // Nur func-SVG highlight
    },

    // Step 5: Shopfloor Connectivity
    {
      id: 'step-5',
      label: $localize`:@@dspArchStepConnectivity:Shopfloor-Konnektivität`,
      description: $localize`:@@dspArchStepConnectivityDesc:DSP verbindet Maschinen, Sensoren, Logistiksysteme und Shopfloor-Assets über direkte, bidirektionale Kommunikation – ohne Eingriffe in bestehende Steuerungslogik.`,
      visibleContainerIds: ['layer-dsp', 'dsp-edge', ...baseShopfloorContainers],
      highlightedContainerIds: ['dsp-edge'],
      visibleConnectionIds: customerConfig
        ? customerConfig.sfDevices.map(d => `conn_dsp-edge_${d.id}`)
        : [
            'conn_dsp-edge_sf-device-mill',
            'conn_dsp-edge_sf-device-drill',
            'conn_dsp-edge_sf-device-aiqs',
            'conn_dsp-edge_sf-device-hbw',
            'conn_dsp-edge_sf-device-dps',
            'conn_dsp-edge_sf-device-chrg',
          ], // Nur Device-Connections, keine System-Connections
      highlightedConnectionIds: customerConfig
        ? customerConfig.sfDevices.map(d => `conn_dsp-edge_${d.id}`)
        : [
            'conn_dsp-edge_sf-device-mill',
            'conn_dsp-edge_sf-device-drill',
            'conn_dsp-edge_sf-device-aiqs',
            'conn_dsp-edge_sf-device-hbw',
            'conn_dsp-edge_sf-device-dps',
            'conn_dsp-edge_sf-device-chrg',
          ], // Nur Device-Connections highlighted
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
      visibleConnectionIds: customerConfig
        ? [
            // Device-Connections zuerst (werden zuerst gerendert, liegen unten)
            ...customerConfig.sfDevices.map(d => `conn_dsp-edge_${d.id}`),
            // System-Connections danach (werden später gerendert, liegen oben)
            ...customerConfig.sfSystems.map(s => `conn_dsp-edge_${s.id}`),
          ]
        : [
            // Device-Connections zuerst (werden zuerst gerendert, liegen unten)
            'conn_dsp-edge_sf-device-mill',
            'conn_dsp-edge_sf-device-drill',
            'conn_dsp-edge_sf-device-aiqs',
            'conn_dsp-edge_sf-device-hbw',
            'conn_dsp-edge_sf-device-dps',
            'conn_dsp-edge_sf-device-chrg',
            // System-Connections danach (werden später gerendert, liegen oben)
            'conn_dsp-edge_sf-system-any',
            'conn_dsp-edge_sf-system-fts',
          ],
      highlightedConnectionIds: customerConfig
        ? customerConfig.sfSystems.map(s => `conn_dsp-edge_${s.id}`)
        : [
            'conn_dsp-edge_sf-system-any',
            'conn_dsp-edge_sf-system-fts',
          ], // Nur System-Connections highlighted (werden zuletzt gerendert)
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-event-driven'],
    },

    // Step 7: Decentralized Process Choreography
    {
      id: 'step-7',
      label: $localize`:@@dspArchStepChoreo:Dezentrale Prozesschoreografie`,
      description: $localize`:@@dspArchStepChoreoDesc:DSP ermöglicht dezentrale, resiliente Prozessausführung, bei der autonome Prozessobjekte ohne zentrale monolithische Steuerung zusammenarbeiten.`,
      visibleContainerIds: [
        'layer-bp',
        'bp-erp',
        'layer-dsp',
        'dsp-edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['dsp-edge', 'bp-erp'], // bp-erp mit Highlight
      visibleConnectionIds: [
        ...(customerConfig 
          ? customerConfig.bpProcesses.filter(bp => bp.id === 'bp-erp').map(bp => `conn_${bp.id}_dsp-edge`)
          : ['conn_bp-erp_dsp-edge']
        ),
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: customerConfig
        ? customerConfig.bpProcesses.filter(bp => bp.id === 'bp-erp').map(bp => `conn_${bp.id}_dsp-edge`)
        : ['conn_bp-erp_dsp-edge'], // conn_bp-erp_dsp-edge mit Highlight
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-choreography'],
    },

    // Step 8: Digital Twin
    {
      id: 'step-8',
      label: $localize`:@@dspArchStepDigitalTwin:Digitaler Zwilling`,
      description: $localize`:@@dspArchStepDigitalTwinDesc:DSP erzeugt ein digitales Echtzeit-Abbild von Maschinen, Prozessen und Werkstücken durch die Zusammenführung von Daten aus verschiedenen Systemen.`,
      visibleContainerIds: [
        'layer-bp',
        ...bpStep7VisibleIds,
        'layer-dsp',
        'dsp-edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: [
        'dsp-edge',
        'bp-mes',
        'bp-ewm',
      ],
      visibleConnectionIds: [
        ...bpStep7VisibleConnections,
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [
        conn('bp-mes', 'dsp-edge'),
        conn('bp-ewm', 'dsp-edge'),
      ].filter((id) => bpConnections.includes(id)),
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-digital-twin'],
    },

    // Step 9: Platform Independence / Best-of-Breed
    {
      id: 'step-9',
      label: $localize`:@@dspArchStepBestBreed:Plattformunabhängigkeit & Best-of-Breed-Integration`,
      description: $localize`:@@dspArchStepBestBreedDesc:DSP integriert heterogene ERP-, MES-, EWM-, CRM-, Analytics- und Data-Lake-Systeme und bleibt dabei unabhängig von Herstellern und Plattformen.`,
      visibleContainerIds: [
        'layer-bp',
        ...bpWithoutAnalyticsAndDataLake,
        'layer-dsp',
        'dsp-edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['dsp-edge', ...bpFocusIds.filter((id) => bpWithoutAnalyticsAndDataLake.includes(id))],
      visibleConnectionIds: [
        ...bpWithoutAnalyticsAndDataLakeConnections,
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: bpFocusConnections.filter((id) => bpWithoutAnalyticsAndDataLakeConnections.includes(id)),
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
        ...bpWithoutDataLake,
        'dsp-edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: bpWithoutDataLake.includes('bp-analytics') ? ['bp-analytics'] : [],
      visibleConnectionIds: [
        ...bpWithoutDataLakeConnections,
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [conn('bp-analytics', 'dsp-edge')].filter((id) => bpWithoutDataLakeConnections.includes(id)),
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-analytics'],
    },

    // Step 11: AI Enablement
    {
      id: 'step-11',
      label: $localize`:@@dspArchStepAI:AI- & Analytics-Enablement`,
      description: $localize`:@@dspArchStepAIDesc:DSP stellt strukturierte Echtzeitdaten als Grundlage für Analytics, Machine Learning und prädiktive Optimierung bereit.`,
      visibleContainerIds: [
        ...getBusinessContainerIds(customerConfig),
        'layer-dsp',
        'dsp-edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['dsp-edge', 'bp-data-lake'],
      visibleConnectionIds: [
        ...bpConnections,
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [conn('bp-data-lake', 'dsp-edge')], // Highlight conn_bp-data-lake_dsp-edge
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
        ...getBpProcessContainerIds(customerConfig),
        'dsp-edge',
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: [
        'layer-bp',
        'layer-dsp',
        'dsp-edge',
        'bp-mes',
        'bp-erp',
        ...(customerConfig
          ? customerConfig.bpProcesses.map((bp) => bp.id).filter((id) => id !== 'bp-erp' && id !== 'bp-mes')
          : ['bp-cloud', 'bp-analytics', 'bp-data-lake']),
        ...(customerConfig ? customerConfig.sfSystems.map((s) => s.id) : ['sf-system-any', 'sf-system-fts']),
        ...getShopfloorDeviceIds(customerConfig),
      ],
      visibleConnectionIds: [
        ...bpConnections,
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: customerConfig
        ? [
            ...bpConnections,
            ...customerConfig.sfSystems.map(s => conn('dsp-edge', s.id)),
            ...customerConfig.sfDevices.map(d => conn('dsp-edge', d.id)),
          ]
        : [
            conn('bp-mes', 'dsp-edge'),
            conn('bp-erp', 'dsp-edge'),
            conn('bp-cloud', 'dsp-edge'),
            conn('bp-analytics', 'dsp-edge'),
            conn('bp-data-lake', 'dsp-edge'),
            conn('dsp-edge', 'sf-system-any'),
            conn('dsp-edge', 'sf-system-fts'),
            conn('dsp-edge', 'sf-device-mill'),
            conn('dsp-edge', 'sf-device-drill'),
            conn('dsp-edge', 'sf-device-aiqs'),
            conn('dsp-edge', 'sf-device-hbw'),
            conn('dsp-edge', 'sf-device-dps'),
            conn('dsp-edge', 'sf-device-chrg'),
          ], // Highlight aller conn_dsp-edge_<xyz>
      showFunctionIcons: true,
      highlightedFunctionIcons: ['edge-autonomous-enterprise'],
    },

    // Step 13: Management Cockpit (full context, all objects visible, MC highlighted) - moved from Step 14
    // Keine Darstellung von dsp-ux
    {
      id: 'step-13',
      label: $localize`:@@dspArchStep9:Management Cockpit`,
      description: $localize`:@@dspArchStep9Desc:Cloud-based design and deployment workspace for asset modeling, organization management, and controlled Edge rollouts.`,
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        ...getBpProcessContainerIds(customerConfig),
        'dsp-edge',
        'dsp-mc',
        ...baseShopfloorContainers,
        // Explicitly exclude dsp-ux to ensure it's hidden
      ],
      highlightedContainerIds: ['dsp-mc'],
      visibleConnectionIds: [
        conn('dsp-edge', 'dsp-mc'),
        // Explicitly exclude conn('dsp-ux', 'dsp-edge') to ensure dsp-ux is hidden
        ...bpConnections,
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [conn('dsp-edge', 'dsp-mc')],
      showFunctionIcons: false,
    },

    // Step 14: Organization & Asset Modeling (MC) - moved from Step 15
    // Keine Darstellung von dsp-ux
    {
      id: 'step-14',
      label: $localize`:@@dspMcStepOrg:Organization & Asset Modeling`,
      description: $localize`:@@dspMcStepOrgDesc:Central digital model of shopfloor structures, assets, and connected back-end systems across sites.`,
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        ...getBpProcessContainerIds(customerConfig),
        'dsp-edge',
        'dsp-mc',
        ...baseShopfloorContainers,
        // Explicitly exclude dsp-ux to ensure it's hidden
      ],
      highlightedContainerIds: step14Highlights,
      visibleConnectionIds: [
        conn('dsp-edge', 'dsp-mc'),
        // Explicitly exclude conn('dsp-ux', 'dsp-edge') to ensure dsp-ux is hidden
        ...bpConnections,
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [conn('dsp-edge', 'dsp-mc')],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['mc-hierarchical-structure'],
    },

    // Step 15: Process & Data Flow Configuration (MC) - moved from Step 16
    // Keine Darstellung von dsp-ux
    {
      id: 'step-15',
      label: $localize`:@@dspMcStepFlow:Process & Data Flow Configuration`,
      description: $localize`:@@dspMcStepFlowDesc:Process and integration models are configured centrally and deployed to Edge nodes.`,
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        ...getBpProcessContainerIds(customerConfig),
        'dsp-edge',
        'dsp-mc',
        ...baseShopfloorContainers,
        // Explicitly exclude dsp-ux to ensure it's hidden
      ],
      highlightedContainerIds: step15Highlights,
      visibleConnectionIds: [
        conn('dsp-edge', 'dsp-mc'),
        // Explicitly exclude conn('dsp-ux', 'dsp-edge') to ensure dsp-ux is hidden
        ...bpConnections,
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [
        conn('dsp-edge', 'dsp-mc'),
        conn('bp-mes', 'dsp-edge'),
        conn('dsp-edge', 'sf-system-fts'),
      ].filter((id) => [conn('dsp-edge', 'dsp-mc'), ...bpConnections, ...baseShopfloorConnections].includes(id)),
      showFunctionIcons: true,
      highlightedFunctionIcons: ['mc-orchestration'],
    },

    // Step 16: Central Governance & Orchestration (MC) - moved from Step 17
    // Keine Darstellung von dsp-ux
    {
      id: 'step-16',
      label: $localize`:@@dspMcStepGov:Central Governance & Orchestration`,
      description: $localize`:@@dspMcStepGovDesc:Governance covers roles, versions, and release policies; Edge runtime remains autonomous and does not require 24/7 cockpit availability.`,
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        ...getBpProcessContainerIds(customerConfig),
        'dsp-edge',
        'dsp-mc',
        ...baseShopfloorContainers,
        // Explicitly exclude dsp-ux to ensure it's hidden
      ],
      highlightedContainerIds: ['dsp-mc'],
      visibleConnectionIds: [
        conn('dsp-edge', 'dsp-mc'),
        // Explicitly exclude conn('dsp-ux', 'dsp-edge') to ensure dsp-ux is hidden
        ...bpConnections,
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['mc-governance'],
    },

    // Step 17: MC Edge Segment - Central Edge Node (first edge box) - moved from Step 18
    // logo-edge-b wird gehighlighted, Connection zu zentralem logo-mc wird gehighlighted
    // Die zuvor gezeigten functional icons von dsp-mc sollen noch angezeigt werden
    // DSP-UX wird NICHT dargestellt
    {
      id: 'step-17',
      label: $localize`:@@dspMcStepEdge:Managed Edge Landscape`,
      description: $localize`:@@dspMcStepEdgeDesc:Management Cockpit manages Edge landscapes through central models and deployments; direct shopfloor component access is handled via Edge.`,
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        ...getBpProcessContainerIds(customerConfig),
        'dsp-edge',
        'dsp-mc',
        ...baseShopfloorContainers,
        // Explicitly exclude dsp-ux to ensure it's hidden
      ],
      highlightedContainerIds: ['dsp-mc', 'dsp-edge'],
      visibleConnectionIds: [
        conn('dsp-edge', 'dsp-mc'),
        // Explicitly exclude conn('dsp-ux', 'dsp-edge') to ensure dsp-ux is hidden
        ...bpConnections,
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [conn('dsp-edge', 'dsp-mc')],
      showFunctionIcons: true,
      highlightedFunctionIcons: ['logo-edge-b'], // logo-edge-b gehighlighted, Connection zu zentralem logo-mc gehighlighted
    },

    // Step 18: MC Edge Segment - Complete (all 3 edge boxes with connections) - moved from Step 19
    // Highlight von logo-edge-a, logo-edge-b, logo-edge-c
    // Gestrichelte Verbindung zwischen logo-edge-abc untereinander
    // Highlight zu zentralem logo-mc
    // Es wird kein dsp-ux dargestellt
    {
      id: 'step-18',
      label: $localize`:@@dspMcStepEdgeComplete:Multi-Edge Management`,
      description: $localize`:@@dspMcStepEdgeCompleteDesc:Management Cockpit manages multiple Edge nodes (similar or heterogeneous) with centralized deployment governance.`,
      visibleContainerIds: [
        'layer-bp',
        'layer-dsp',
        ...getBpProcessContainerIds(customerConfig),
        'dsp-edge',
        'dsp-mc',
        ...baseShopfloorContainers,
        // Explicitly exclude dsp-ux to ensure it's hidden
      ],
      highlightedContainerIds: ['dsp-mc', 'dsp-edge'],
      visibleConnectionIds: [
        conn('dsp-edge', 'dsp-mc'),
        // Connections between edge icons are handled by function icons rendering (dashed lines)
        ...bpConnections,
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [conn('dsp-edge', 'dsp-mc')], // Connection to central dsp-mc-Icon highlighted
      showFunctionIcons: true,
      highlightedFunctionIcons: ['logo-edge-a', 'logo-edge-b', 'logo-edge-c'], // All three edge icons highlighted
    },

    // Step 19: SmartFactory Dashboard - moved from Step 13
    // Highlight von dsp-ux + connection zu dsp-edge
    // In dsp-mc werden nur MC Function Icons dargestellt (keine logo-edge-a,b,c), keine Connection von logo-edge zu logo-mc
    // In dsp-edge werden alle functional icons dargestellt, aber kein highlighting
    {
      id: 'step-19',
      label: $localize`:@@dspArchStep11:SmartFactory Dashboard`,
      description: $localize`:@@dspArchStep11Desc:Operational runtime visibility of digital twin, real-time processes, and track & trace in the shopfloor via Edge-connected systems.`,
      visibleContainerIds: [
        ...getBusinessContainerIds(customerConfig),
        'layer-dsp',
        'dsp-ux',
        'dsp-edge',
        'dsp-mc', // Only MC Function Icons shown (no logo-edge-a,b,c), no highlighting
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: ['dsp-ux'], // Only highlight dsp-ux, not dsp-edge or dsp-mc
      visibleConnectionIds: [
        conn('dsp-ux', 'dsp-edge'),
        conn('dsp-edge', 'dsp-mc'),
        ...bpConnections,
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [conn('dsp-ux', 'dsp-edge')], // Highlight connection from dsp-ux to dsp-edge
      showFunctionIcons: true,
      // No highlightedFunctionIcons - all functional icons shown but not highlighted
    },

    // Step 20: Full overview (Zielbild) - Everything visible, nothing highlighted
    {
      id: 'step-20',
      label: $localize`:@@dspArchStep20:Bridge between IT and OT: ORBIS DSP as an enabler`,
      description: $localize`:@@dspArchStep20Desc:ORBIS DSP connects shopfloor and business IT as an end-to-end enabler for interoperable processes.`,
      visibleContainerIds: [
        'layer-dsp',
        'layer-sf',
        ...getBusinessContainerIds(customerConfig),
        ...getDspContainerIds(),
        ...baseShopfloorContainers,
      ],
      highlightedContainerIds: [], // No highlighting in final step
      visibleConnectionIds: [
        conn('dsp-ux', 'dsp-edge'),
        conn('dsp-edge', 'dsp-mc'),
        ...bpConnections,
        ...baseShopfloorConnections,
      ],
      highlightedConnectionIds: [], // No highlighting in final step
      showFunctionIcons: true, // All Edge + MC function icons visible
      highlightedFunctionIcons: [], // None highlighted
    },
  ];

  return moveInteroperabilitySummaryToStep12(steps);
}

export function createSlimSteps(customerConfig?: CustomerDspConfig): StepConfig[] {
  // Keep the full (long) story flow incl. BP boxes, MC and OSF dashboard,
  // but compress the DSP function focus into two summary steps near the end:
  // 1) all remaining functions at once, 2) interoperability as final summary.
  const steps = createDefaultSteps(customerConfig).map((s) => ({ ...s }));

  const remainingFunctions: Array<
    | 'edge-network'
    | 'edge-event-driven'
    | 'edge-choreography'
    | 'edge-digital-twin'
    | 'edge-best-of-breed'
    | 'edge-analytics'
    | 'edge-ai-enablement'
    | 'edge-autonomous-enterprise'
  > = [
    'edge-network',
    'edge-event-driven',
    'edge-choreography',
    'edge-digital-twin',
    'edge-best-of-breed',
    'edge-analytics',
    'edge-ai-enablement',
    'edge-autonomous-enterprise',
  ];

  for (const step of steps) {
    if (!('highlightedFunctionIcons' in step)) {
      continue;
    }
    // Clear all per-function highlight steps by default; we re-enable for step-4/5 below.
    step.highlightedFunctionIcons = [];
  }

  const stepInterop = steps.find((s) => s.id === 'step-12');
  if (stepInterop) {
    stepInterop.showFunctionIcons = true;
    stepInterop.highlightedFunctionIcons = ['edge-interoperability'];
  }

  const stepAllFunctions = steps.find((s) => s.id === 'step-11');
  if (stepAllFunctions) {
    stepAllFunctions.label = $localize`:@@dspArchStepFunctions:DSP Functions`;
    stepAllFunctions.description = $localize`:@@dspArchStepFunctionsDesc:All DSP functions are available on the Edge; interoperability is highlighted first, then the remaining functions appear together.`;
    stepAllFunctions.showFunctionIcons = true;
    stepAllFunctions.highlightedFunctionIcons = remainingFunctions;
  }

  return steps;
}

function shouldUseSlimSteps(customerConfig?: CustomerDspConfig): boolean {
  const key = customerConfig?.customerKey ?? '';
  // OCC is the long-term default story. Keep slim steps only for the Hannover booth variant.
  return key.includes('hannover');
}

export function createFunctionalView(customerConfig?: import('./configs/types').CustomerDspConfig): DiagramConfig {
  const steps = shouldUseSlimSteps(customerConfig) ? createSlimSteps(customerConfig) : createDefaultSteps(customerConfig);
  return new DiagramConfigBuilder(customerConfig).withFunctionalSteps(steps).build();
}
