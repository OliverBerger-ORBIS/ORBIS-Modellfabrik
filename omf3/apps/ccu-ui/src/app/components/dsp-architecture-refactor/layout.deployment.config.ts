import type { ContainerConfig, ConnectionConfig, StepConfig, DiagramConfig } from './types';
import {
  createDefaultContainers,
  createDefaultConnections,
  VIEWBOX_WIDTH,
  VIEWBOX_HEIGHT,
} from './layout.shared.config';

export function createDeploymentView(): DiagramConfig {
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
        'bp-mes',
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
        'conn-bp-mes-dsp-edge',
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
    viewBox: {
      width: VIEWBOX_WIDTH,
      height: VIEWBOX_HEIGHT,
    },
  };
}
