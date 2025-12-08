/**
 * Layout configurations for DSP Architecture views.
 * 
 * Uses the exact layout from the existing DSP architecture component
 * with continuous layer backgrounds and grid-based box positioning.
 */

import type { Layer, Box, Arrow, ArchitectureConfig } from './types';
import { ORBIS_COLORS } from '../../assets/color-palette';

/**
 * SVG viewBox dimensions - matching existing DSP architecture
 */
export const VIEWBOX_WIDTH = 1200;
export const VIEWBOX_HEIGHT = 860;

/**
 * Layout constants - matching existing DSP architecture
 */
export const LAYOUT = {
  // Layer dimensions
  LAYER_HEIGHT: 260,
  LAYER_START_Y: 80,
  
  // Label area
  LABEL_X: 10,
  LABEL_WIDTH: 90,
  
  // Business Process layer (top - white)
  BUSINESS_Y: 80,
  
  // DSP layer (middle - blue) - TALLER for component view
  DSP_LAYER_Y: 340,
  DSP_LAYER_HEIGHT: 360, // Increased to fit Edge component view
  
  // Shopfloor layer (bottom - gray)
  SHOPFLOOR_Y: 700,
  
  // Box dimensions
  BUSINESS_BOX_WIDTH: 200,
  BUSINESS_BOX_HEIGHT: 140,
  DSP_BOX_HEIGHT: 165,
  
  // Content area
  CONTENT_START_X: 100,
  MARGIN_RIGHT: 30,
  CONTENT_WIDTH: 1090,
  BOX_GAP: 25,
};

/**
 * Layer color definitions matching existing architecture
 */
const LAYER_COLORS = {
  business: '#ffffff',
  dsp: 'rgba(207, 230, 255, 0.5)', // Blue tint
  shopfloor: 'rgba(241, 243, 247, 0.8)', // Gray tint
};

/**
 * Functional View Configuration
 * Shows high-level functional capabilities across layers
 */
const FUNCTIONAL_LAYERS: Layer[] = [
  {
    id: 'business-layer',
    type: 'business',
    label: 'Business Processes',
    backgroundColor: LAYER_COLORS.business,
    heightRatio: 1,
    boxes: [
      {
        id: 'bp-1',
        label: 'ERP',
        widthRatio: 1/3,
        layer: 'business',
        position: 0,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'bp-2',
        label: 'SCM',
        widthRatio: 1/3,
        layer: 'business',
        position: 1,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'bp-3',
        label: 'Analytics',
        widthRatio: 1/3,
        layer: 'business',
        position: 2,
        clickable: true,
        hoverEffect: true,
      },
    ],
  },
  {
    id: 'dsp-layer',
    type: 'dsp',
    label: 'Distributed Shopfloor Processing (DSP)',
    backgroundColor: LAYER_COLORS.dsp,
    heightRatio: 1.5,
    boxes: [
      {
        id: 'dsp-smartfactory-dashboard',
        label: 'SmartFactory\nDashboard',
        widthRatio: 1/3,
        layer: 'dsp',
        position: 0,
        clickable: true,
        hoverEffect: true,
        borderColor: ORBIS_COLORS.orbisBlue.strong,
      },
      {
        id: 'dsp-edge',
        label: 'Edge',
        widthRatio: 1,
        layer: 'dsp',
        position: 1,
        clickable: true,
        hoverEffect: true,
        borderColor: ORBIS_COLORS.orbisBlue.medium,
      },
      {
        id: 'dsp-management-cockpit',
        label: 'Management\nCockpit',
        widthRatio: 2/3,
        layer: 'dsp',
        position: 2,
        clickable: true,
        hoverEffect: true,
        borderColor: ORBIS_COLORS.orbisBlue.strong,
      },
    ],
  },
  {
    id: 'shopfloor-systems-layer',
    type: 'shopfloor-systems',
    label: 'Shopfloor - Systems',
    backgroundColor: LAYER_COLORS.shopfloor,
    heightRatio: 0.8,
    boxes: [
      {
        id: 'sf-system-1',
        label: 'MES',
        widthRatio: 1/4,
        layer: 'shopfloor-systems',
        position: 0,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-system-2',
        label: 'Warehouse\nSystem',
        widthRatio: 1/4,
        layer: 'shopfloor-systems',
        position: 1,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-system-3',
        label: 'AGV\nSystem',
        widthRatio: 1/4,
        layer: 'shopfloor-systems',
        position: 2,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-system-4',
        label: 'SCADA',
        widthRatio: 1/4,
        layer: 'shopfloor-systems',
        position: 3,
        clickable: true,
        hoverEffect: true,
      },
    ],
  },
  {
    id: 'shopfloor-devices-layer',
    type: 'shopfloor-devices',
    label: 'Shopfloor - Devices',
    backgroundColor: LAYER_COLORS.shopfloor,
    heightRatio: 0.7,
    boxes: [
      {
        id: 'sf-device-mill',
        label: 'Mill',
        widthRatio: 1/6,
        layer: 'shopfloor-devices',
        position: 0,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-device-drill',
        label: 'Drill',
        widthRatio: 1/6,
        layer: 'shopfloor-devices',
        position: 1,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-device-aiqs',
        label: 'AIQS',
        widthRatio: 1/6,
        layer: 'shopfloor-devices',
        position: 2,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-device-hbw',
        label: 'HBW',
        widthRatio: 1/6,
        layer: 'shopfloor-devices',
        position: 3,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-device-dps',
        label: 'DPS',
        widthRatio: 1/6,
        layer: 'shopfloor-devices',
        position: 4,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-device-chrg',
        label: 'Charger',
        widthRatio: 1/6,
        layer: 'shopfloor-devices',
        position: 5,
        clickable: true,
        hoverEffect: true,
      },
    ],
  },
];

const FUNCTIONAL_ARROWS: Arrow[] = [
  // Business to DSP connections
  {
    id: 'arrow-bp1-to-dsp-edge',
    from: 'bp-1',
    to: 'dsp-edge',
    type: 'l-shaped',
    color: ORBIS_COLORS.orbisBlue.medium,
    strokeWidth: 2,
    visible: true,
  },
  {
    id: 'arrow-bp2-to-dsp-edge',
    from: 'bp-2',
    to: 'dsp-edge',
    type: 'l-shaped',
    color: ORBIS_COLORS.orbisBlue.medium,
    strokeWidth: 2,
    visible: true,
  },
  {
    id: 'arrow-bp3-to-dsp-cockpit',
    from: 'bp-3',
    to: 'dsp-management-cockpit',
    type: 'l-shaped',
    color: ORBIS_COLORS.orbisBlue.medium,
    strokeWidth: 2,
    visible: true,
  },
  // DSP to Shopfloor Systems
  {
    id: 'arrow-dsp-edge-to-systems',
    from: 'dsp-edge',
    to: 'sf-system-1',
    type: 'l-shaped',
    color: ORBIS_COLORS.solutionPetrol.medium,
    strokeWidth: 2,
    visible: true,
  },
  // Systems to Devices
  {
    id: 'arrow-system1-to-mill',
    from: 'sf-system-1',
    to: 'sf-device-mill',
    type: 'straight',
    color: ORBIS_COLORS.shopfloorHighlight.medium,
    strokeWidth: 2,
    visible: true,
  },
  {
    id: 'arrow-system2-to-hbw',
    from: 'sf-system-2',
    to: 'sf-device-hbw',
    type: 'straight',
    color: ORBIS_COLORS.shopfloorHighlight.medium,
    strokeWidth: 2,
    visible: true,
  },
];

/**
 * Component View Configuration
 * Shows detailed component architecture with internal DSP components
 */
const COMPONENT_LAYERS: Layer[] = [
  {
    id: 'business-layer',
    type: 'business',
    label: 'Business Processes',
    backgroundColor: LAYER_COLORS.business,
    heightRatio: 1,
    boxes: [
      {
        id: 'bp-1',
        label: 'ERP System',
        widthRatio: 1/2,
        layer: 'business',
        position: 0,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'bp-2',
        label: 'Cloud Applications',
        widthRatio: 1/2,
        layer: 'business',
        position: 1,
        clickable: true,
        hoverEffect: true,
      },
    ],
  },
  {
    id: 'dsp-layer',
    type: 'dsp',
    label: 'DSP Components',
    backgroundColor: LAYER_COLORS.dsp,
    heightRatio: 2,
    boxes: [
      {
        id: 'dsp-smartfactory-dashboard',
        label: 'SmartFactory\nDashboard',
        widthRatio: 1/3,
        layer: 'dsp',
        position: 0,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'edge-connectivity',
        label: 'Connectivity',
        widthRatio: 1/4,
        layer: 'dsp',
        position: 1,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'edge-digital-twin',
        label: 'Digital Twin',
        widthRatio: 1/4,
        layer: 'dsp',
        position: 2,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'edge-analytics',
        label: 'Analytics',
        widthRatio: 1/4,
        layer: 'dsp',
        position: 3,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'edge-workflow',
        label: 'Workflow',
        widthRatio: 1/4,
        layer: 'dsp',
        position: 4,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'dsp-management-cockpit',
        label: 'Management\nCockpit',
        widthRatio: 2/3,
        layer: 'dsp',
        position: 5,
        clickable: true,
        hoverEffect: true,
      },
    ],
  },
  {
    id: 'shopfloor-systems-layer',
    type: 'shopfloor-systems',
    label: 'Shopfloor - Systems',
    backgroundColor: LAYER_COLORS.shopfloor,
    heightRatio: 0.8,
    boxes: [
      {
        id: 'sf-system-1',
        label: 'Factory\nSystem',
        widthRatio: 1/3,
        layer: 'shopfloor-systems',
        position: 0,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-system-2',
        label: 'Warehouse\nSystem',
        widthRatio: 1/3,
        layer: 'shopfloor-systems',
        position: 1,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-system-3',
        label: 'AGV\nSystem',
        widthRatio: 1/3,
        layer: 'shopfloor-systems',
        position: 2,
        clickable: true,
        hoverEffect: true,
      },
    ],
  },
  {
    id: 'shopfloor-devices-layer',
    type: 'shopfloor-devices',
    label: 'Shopfloor - Devices',
    backgroundColor: LAYER_COLORS.shopfloor,
    heightRatio: 0.7,
    boxes: [
      {
        id: 'sf-device-mill',
        label: 'Mill',
        widthRatio: 1/5,
        layer: 'shopfloor-devices',
        position: 0,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-device-drill',
        label: 'Drill',
        widthRatio: 1/5,
        layer: 'shopfloor-devices',
        position: 1,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-device-aiqs',
        label: 'AIQS',
        widthRatio: 1/5,
        layer: 'shopfloor-devices',
        position: 2,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-device-hbw',
        label: 'HBW',
        widthRatio: 1/5,
        layer: 'shopfloor-devices',
        position: 3,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-device-dps',
        label: 'DPS',
        widthRatio: 1/5,
        layer: 'shopfloor-devices',
        position: 4,
        clickable: true,
        hoverEffect: true,
      },
    ],
  },
];

const COMPONENT_ARROWS: Arrow[] = [
  {
    id: 'arrow-bp1-to-connectivity',
    from: 'bp-1',
    to: 'edge-connectivity',
    type: 'l-shaped',
    color: ORBIS_COLORS.orbisBlue.medium,
    strokeWidth: 2,
    visible: true,
  },
  {
    id: 'arrow-connectivity-to-system1',
    from: 'edge-connectivity',
    to: 'sf-system-1',
    type: 'l-shaped',
    color: ORBIS_COLORS.solutionPetrol.medium,
    strokeWidth: 2,
    visible: true,
  },
];

/**
 * Deployment View Configuration
 * Shows infrastructure and deployment architecture
 */
const DEPLOYMENT_LAYERS: Layer[] = [
  {
    id: 'business-layer',
    type: 'business',
    label: 'Cloud / On-Premise',
    backgroundColor: LAYER_COLORS.business,
    heightRatio: 1,
    boxes: [
      {
        id: 'bp-1',
        label: 'SAP S/4HANA',
        widthRatio: 1/3,
        layer: 'business',
        position: 0,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'bp-2',
        label: 'Azure Cloud',
        widthRatio: 1/3,
        layer: 'business',
        position: 1,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'bp-3',
        label: 'Data Lake',
        widthRatio: 1/3,
        layer: 'business',
        position: 2,
        clickable: true,
        hoverEffect: true,
      },
    ],
  },
  {
    id: 'dsp-layer',
    type: 'dsp',
    label: 'DSP Platform (Edge)',
    backgroundColor: LAYER_COLORS.dsp,
    heightRatio: 1.5,
    boxes: [
      {
        id: 'dsp-smartfactory-dashboard',
        label: 'Dashboard\nContainer',
        widthRatio: 1/3,
        layer: 'dsp',
        position: 0,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'dsp-edge',
        label: 'Edge Runtime\n(Docker/K8s)',
        widthRatio: 1,
        layer: 'dsp',
        position: 1,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'dsp-management-cockpit',
        label: 'Cockpit\nContainer',
        widthRatio: 2/3,
        layer: 'dsp',
        position: 2,
        clickable: true,
        hoverEffect: true,
      },
    ],
  },
  {
    id: 'shopfloor-systems-layer',
    type: 'shopfloor-systems',
    label: 'Shopfloor IT',
    backgroundColor: LAYER_COLORS.shopfloor,
    heightRatio: 0.8,
    boxes: [
      {
        id: 'sf-system-1',
        label: 'MES Server',
        widthRatio: 1/2,
        layer: 'shopfloor-systems',
        position: 0,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-system-2',
        label: 'PLC Network',
        widthRatio: 1/2,
        layer: 'shopfloor-systems',
        position: 1,
        clickable: true,
        hoverEffect: true,
      },
    ],
  },
  {
    id: 'shopfloor-devices-layer',
    type: 'shopfloor-devices',
    label: 'Devices / Hardware',
    backgroundColor: LAYER_COLORS.shopfloor,
    heightRatio: 0.7,
    boxes: [
      {
        id: 'sf-device-mill',
        label: 'Mill PLC',
        widthRatio: 1/4,
        layer: 'shopfloor-devices',
        position: 0,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-device-drill',
        label: 'Drill PLC',
        widthRatio: 1/4,
        layer: 'shopfloor-devices',
        position: 1,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-device-hbw',
        label: 'HBW PLC',
        widthRatio: 1/4,
        layer: 'shopfloor-devices',
        position: 2,
        clickable: true,
        hoverEffect: true,
      },
      {
        id: 'sf-device-dps',
        label: 'DPS PLC',
        widthRatio: 1/4,
        layer: 'shopfloor-devices',
        position: 3,
        clickable: true,
        hoverEffect: true,
      },
    ],
  },
];

const DEPLOYMENT_ARROWS: Arrow[] = [
  {
    id: 'arrow-bp1-to-edge',
    from: 'bp-1',
    to: 'dsp-edge',
    type: 'l-shaped',
    color: ORBIS_COLORS.orbisBlue.medium,
    strokeWidth: 2,
    visible: true,
    bidirectional: true,
  },
  {
    id: 'arrow-edge-to-mes',
    from: 'dsp-edge',
    to: 'sf-system-1',
    type: 'l-shaped',
    color: ORBIS_COLORS.solutionPetrol.medium,
    strokeWidth: 2,
    visible: true,
    bidirectional: true,
  },
];

/**
 * Get architecture configuration for a specific view mode
 */
export function getArchitectureConfig(viewMode: 'functional' | 'component' | 'deployment'): ArchitectureConfig {
  switch (viewMode) {
    case 'functional':
      return {
        viewMode: 'functional',
        layers: FUNCTIONAL_LAYERS,
        arrows: FUNCTIONAL_ARROWS,
      };
    case 'component':
      return {
        viewMode: 'component',
        layers: COMPONENT_LAYERS,
        arrows: COMPONENT_ARROWS,
      };
    case 'deployment':
      return {
        viewMode: 'deployment',
        layers: DEPLOYMENT_LAYERS,
        arrows: DEPLOYMENT_ARROWS,
      };
    default:
      return {
        viewMode: 'functional',
        layers: FUNCTIONAL_LAYERS,
        arrows: FUNCTIONAL_ARROWS,
      };
  }
}

/**
 * Apply customer-specific layer overrides to the configuration
 */
export function applyLayerOverrides(
  config: ArchitectureConfig,
  overrides?: Partial<ArchitectureConfig>
): ArchitectureConfig {
  if (!overrides) {
    return config;
  }

  return {
    ...config,
    layers: overrides.layers || config.layers,
    arrows: overrides.arrows || config.arrows,
    scenes: overrides.scenes || config.scenes,
  };
}
