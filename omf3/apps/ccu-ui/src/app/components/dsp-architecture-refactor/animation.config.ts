/**
 * Animation configuration for DSP Architecture component.
 * 
 * Defines example animation scenes for each view mode.
 * Scenes use box IDs for view-agnostic definitions and support various actions:
 * - highlight: Emphasize specific boxes
 * - fadeothers: Dim non-highlighted boxes
 * - connect: Show specific arrows
 * - disconnect: Hide specific arrows
 * - show: Reveal specific boxes
 * - hide: Conceal specific boxes
 * - focus: Zoom/camera focus on area
 * - text: Display overlay text
 */

import type { AnimationScene, SceneStep } from './types';
import { ORBIS_COLORS } from '../../assets/color-palette';

/**
 * Functional View Animation Scene
 * Demonstrates data flow from business to shopfloor
 */
const FUNCTIONAL_SCENE: AnimationScene = {
  id: 'functional-data-flow',
  name: 'Data Flow - Functional View',
  description: 'Shows how data flows from business systems through DSP to shopfloor devices',
  viewMode: 'functional',
  steps: [
    {
      id: 'step-1',
      label: 'Business Layer',
      description: 'Business systems initiate processes',
      actions: [
        {
          type: 'highlight',
          targets: ['bp-1', 'bp-2', 'bp-3'],
          color: ORBIS_COLORS.orbisBlue.light,
        },
        {
          type: 'fadeothers',
        },
        {
          type: 'text',
          text: 'Business systems (ERP, SCM, Analytics) initiate manufacturing processes',
        },
      ],
    },
    {
      id: 'step-2',
      label: 'Business to DSP',
      description: 'Data flows to DSP layer',
      actions: [
        {
          type: 'highlight',
          targets: ['bp-1', 'bp-2', 'dsp-edge', 'dsp-management-cockpit'],
          color: ORBIS_COLORS.orbisBlue.medium,
        },
        {
          type: 'connect',
          targets: ['arrow-bp1-to-dsp-edge', 'arrow-bp2-to-dsp-edge', 'arrow-bp3-to-dsp-cockpit'],
        },
        {
          type: 'text',
          text: 'Orders and configuration flow from business to DSP Edge',
        },
      ],
    },
    {
      id: 'step-3',
      label: 'DSP Processing',
      description: 'DSP processes and routes data',
      actions: [
        {
          type: 'highlight',
          targets: ['dsp-smartfactory-dashboard', 'dsp-edge', 'dsp-management-cockpit'],
          color: ORBIS_COLORS.solutionPetrol.medium,
        },
        {
          type: 'text',
          text: 'DSP Edge processes data and provides real-time monitoring via Dashboard',
        },
      ],
    },
    {
      id: 'step-4',
      label: 'DSP to Systems',
      description: 'Commands sent to shopfloor systems',
      actions: [
        {
          type: 'highlight',
          targets: ['dsp-edge', 'sf-system-1', 'sf-system-2', 'sf-system-3', 'sf-system-4'],
          color: ORBIS_COLORS.shopfloorHighlight.medium,
        },
        {
          type: 'connect',
          targets: ['arrow-dsp-edge-to-systems'],
        },
        {
          type: 'text',
          text: 'DSP sends orchestrated commands to shopfloor systems',
        },
      ],
    },
    {
      id: 'step-5',
      label: 'Systems to Devices',
      description: 'Systems control devices',
      actions: [
        {
          type: 'highlight',
          targets: ['sf-system-1', 'sf-system-2', 'sf-device-mill', 'sf-device-hbw'],
          color: ORBIS_COLORS.shopfloorHighlight.strong,
        },
        {
          type: 'connect',
          targets: ['arrow-system1-to-mill', 'arrow-system2-to-hbw'],
        },
        {
          type: 'text',
          text: 'Shopfloor systems control individual devices and machines',
        },
      ],
    },
    {
      id: 'step-6',
      label: 'Complete Flow',
      description: 'End-to-end data flow',
      actions: [
        {
          type: 'highlight',
          targets: ['bp-1', 'dsp-edge', 'sf-system-1', 'sf-device-mill'],
          color: ORBIS_COLORS.highlightGreen.medium,
        },
        {
          type: 'text',
          text: 'Complete end-to-end flow from ERP to shopfloor device',
        },
      ],
    },
    {
      id: 'step-7',
      label: 'Reset',
      description: 'Return to initial state',
      actions: [
        {
          type: 'highlight',
          targets: [],
          reset: true,
        },
        {
          type: 'disconnect',
          targets: ['arrow-bp1-to-dsp-edge', 'arrow-bp2-to-dsp-edge', 'arrow-bp3-to-dsp-cockpit', 'arrow-dsp-edge-to-systems', 'arrow-system1-to-mill', 'arrow-system2-to-hbw'],
        },
        {
          type: 'text',
          text: '',
        },
      ],
    },
  ],
};

/**
 * Component View Animation Scene
 * Shows internal DSP component interactions
 */
const COMPONENT_SCENE: AnimationScene = {
  id: 'component-internal-flow',
  name: 'Component Flow - Component View',
  description: 'Demonstrates internal DSP component interactions and data processing',
  viewMode: 'component',
  steps: [
    {
      id: 'step-1',
      label: 'Business Input',
      description: 'Business systems send data',
      actions: [
        {
          type: 'highlight',
          targets: ['bp-1', 'bp-2'],
          color: ORBIS_COLORS.orbisBlue.light,
        },
        {
          type: 'fadeothers',
        },
        {
          type: 'text',
          text: 'Business systems initiate requests',
        },
      ],
    },
    {
      id: 'step-2',
      label: 'Connectivity Layer',
      description: 'Data enters via connectivity',
      actions: [
        {
          type: 'highlight',
          targets: ['bp-1', 'edge-connectivity'],
          color: ORBIS_COLORS.orbisBlue.medium,
        },
        {
          type: 'connect',
          targets: ['arrow-bp1-to-connectivity'],
        },
        {
          type: 'text',
          text: 'Connectivity component receives and normalizes data',
        },
      ],
    },
    {
      id: 'step-3',
      label: 'Digital Twin Processing',
      description: 'Digital twin maintains state',
      actions: [
        {
          type: 'highlight',
          targets: ['edge-connectivity', 'edge-digital-twin'],
          color: ORBIS_COLORS.solutionPetrol.medium,
        },
        {
          type: 'text',
          text: 'Digital Twin component maintains shopfloor state model',
        },
      ],
    },
    {
      id: 'step-4',
      label: 'Analytics Processing',
      description: 'Analytics processes data',
      actions: [
        {
          type: 'highlight',
          targets: ['edge-digital-twin', 'edge-analytics'],
          color: ORBIS_COLORS.highlightGreen.medium,
        },
        {
          type: 'text',
          text: 'Analytics component performs real-time calculations',
        },
      ],
    },
    {
      id: 'step-5',
      label: 'Workflow Orchestration',
      description: 'Workflow orchestrates actions',
      actions: [
        {
          type: 'highlight',
          targets: ['edge-analytics', 'edge-workflow'],
          color: ORBIS_COLORS.microsoftOrange.medium,
        },
        {
          type: 'text',
          text: 'Workflow component orchestrates shopfloor operations',
        },
      ],
    },
    {
      id: 'step-6',
      label: 'To Shopfloor',
      description: 'Commands sent to shopfloor',
      actions: [
        {
          type: 'highlight',
          targets: ['edge-connectivity', 'sf-system-1'],
          color: ORBIS_COLORS.shopfloorHighlight.medium,
        },
        {
          type: 'connect',
          targets: ['arrow-connectivity-to-system1'],
        },
        {
          type: 'text',
          text: 'Commands sent to shopfloor systems via connectivity',
        },
      ],
    },
    {
      id: 'step-7',
      label: 'Reset',
      description: 'Return to initial state',
      actions: [
        {
          type: 'highlight',
          targets: [],
          reset: true,
        },
        {
          type: 'disconnect',
          targets: ['arrow-bp1-to-connectivity', 'arrow-connectivity-to-system1'],
        },
        {
          type: 'text',
          text: '',
        },
      ],
    },
  ],
};

/**
 * Deployment View Animation Scene
 * Shows infrastructure and deployment flow
 */
const DEPLOYMENT_SCENE: AnimationScene = {
  id: 'deployment-infrastructure',
  name: 'Infrastructure Flow - Deployment View',
  description: 'Demonstrates infrastructure layers and deployment architecture',
  viewMode: 'deployment',
  steps: [
    {
      id: 'step-1',
      label: 'Cloud Layer',
      description: 'Cloud and on-premise systems',
      actions: [
        {
          type: 'highlight',
          targets: ['bp-1', 'bp-2', 'bp-3'],
          color: ORBIS_COLORS.orbisBlue.light,
        },
        {
          type: 'fadeothers',
        },
        {
          type: 'text',
          text: 'Cloud and on-premise business systems',
        },
      ],
    },
    {
      id: 'step-2',
      label: 'Edge Runtime',
      description: 'Edge containerized platform',
      actions: [
        {
          type: 'highlight',
          targets: ['dsp-edge', 'dsp-smartfactory-dashboard', 'dsp-management-cockpit'],
          color: ORBIS_COLORS.solutionPetrol.medium,
        },
        {
          type: 'text',
          text: 'DSP Edge runs on Docker/Kubernetes containers',
        },
      ],
    },
    {
      id: 'step-3',
      label: 'Network Connection',
      description: 'Secure network connections',
      actions: [
        {
          type: 'highlight',
          targets: ['bp-1', 'dsp-edge'],
          color: ORBIS_COLORS.orbisBlue.medium,
        },
        {
          type: 'connect',
          targets: ['arrow-bp1-to-edge'],
        },
        {
          type: 'text',
          text: 'Secure bi-directional connection between cloud and edge',
        },
      ],
    },
    {
      id: 'step-4',
      label: 'Shopfloor IT',
      description: 'Shopfloor IT infrastructure',
      actions: [
        {
          type: 'highlight',
          targets: ['sf-system-1', 'sf-system-2'],
          color: ORBIS_COLORS.shopfloorHighlight.medium,
        },
        {
          type: 'text',
          text: 'Shopfloor IT layer with MES and PLC network',
        },
      ],
    },
    {
      id: 'step-5',
      label: 'Edge to Shopfloor',
      description: 'Edge connects to shopfloor',
      actions: [
        {
          type: 'highlight',
          targets: ['dsp-edge', 'sf-system-1'],
          color: ORBIS_COLORS.solutionPetrol.strong,
        },
        {
          type: 'connect',
          targets: ['arrow-edge-to-mes'],
        },
        {
          type: 'text',
          text: 'DSP Edge communicates with shopfloor IT systems',
        },
      ],
    },
    {
      id: 'step-6',
      label: 'Hardware Layer',
      description: 'Physical devices',
      actions: [
        {
          type: 'highlight',
          targets: ['sf-device-mill', 'sf-device-drill', 'sf-device-hbw', 'sf-device-dps'],
          color: ORBIS_COLORS.shopfloorHighlight.strong,
        },
        {
          type: 'text',
          text: 'Physical shopfloor devices and PLCs',
        },
      ],
    },
    {
      id: 'step-7',
      label: 'Reset',
      description: 'Return to initial state',
      actions: [
        {
          type: 'highlight',
          targets: [],
          reset: true,
        },
        {
          type: 'disconnect',
          targets: ['arrow-bp1-to-edge', 'arrow-edge-to-mes'],
        },
        {
          type: 'text',
          text: '',
        },
      ],
    },
  ],
};

/**
 * Get animation scene for a specific view mode
 */
export function getAnimationScene(viewMode: 'functional' | 'component' | 'deployment'): AnimationScene | undefined {
  switch (viewMode) {
    case 'functional':
      return FUNCTIONAL_SCENE;
    case 'component':
      return COMPONENT_SCENE;
    case 'deployment':
      return DEPLOYMENT_SCENE;
    default:
      return undefined;
  }
}

/**
 * Get all available animation scenes
 */
export function getAllAnimationScenes(): AnimationScene[] {
  return [FUNCTIONAL_SCENE, COMPONENT_SCENE, DEPLOYMENT_SCENE];
}
