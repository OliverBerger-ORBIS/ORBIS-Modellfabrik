/**
 * Type definitions for the refactored DSP Architecture component.
 * 
 * This file defines the core types used for rendering the three-layer ORBIS DSP architecture
 * (Functional / Component / Deployment views) with animations, arrows, and interactions.
 */

/**
 * View mode determines which architecture perspective is displayed
 */
export type ViewMode = 'functional' | 'component' | 'deployment';

/**
 * Layer types in the DSP architecture
 */
export type LayerType = 'business' | 'dsp' | 'shopfloor-systems' | 'shopfloor-devices';

/**
 * Layer configuration defining visual and layout properties
 */
export interface Layer {
  id: string;
  type: LayerType;
  label: string;
  backgroundColor: string;
  heightRatio: number; // Relative height compared to other layers
  boxes: Box[];
}

/**
 * Box represents a component/module in the architecture
 */
export interface Box {
  id: string;
  label: string;
  iconPath?: string;
  widthRatio: number; // Relative width (1 = full width, 0.5 = half width, etc.)
  layer: LayerType;
  position?: number; // Position in the layer (0-based index)
  // Visual properties
  borderColor?: string;
  backgroundColor?: string;
  textColor?: string;
  // Interaction
  clickable?: boolean;
  hoverEffect?: boolean;
  tooltip?: string;
}

/**
 * Arrow/Connection configuration between boxes
 */
export interface Arrow {
  id: string;
  from: string; // Source box ID
  to: string; // Target box ID
  type: 'straight' | 'l-shaped' | 'curved';
  color: string;
  strokeWidth?: number;
  animated?: boolean; // Enable pulse animation
  visible?: boolean;
  label?: string;
  // Arrow styling
  dashed?: boolean;
  bidirectional?: boolean;
}

/**
 * Point in 2D space for arrow calculations
 */
export interface Point {
  x: number;
  y: number;
}

/**
 * Box bounds for arrow anchor calculations
 */
export interface BoxBounds {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  centerX: number;
  centerY: number;
}

/**
 * Action types for animation scenes
 */
export type SceneActionType =
  | 'highlight'      // Highlight specific boxes
  | 'fadeothers'     // Fade out non-highlighted boxes
  | 'connect'        // Show specific arrows
  | 'disconnect'     // Hide specific arrows
  | 'show'           // Show specific boxes
  | 'hide'           // Hide specific boxes
  | 'focus'          // Zoom/focus on specific area
  | 'text';          // Display overlay text

/**
 * Scene action for animation steps
 */
export interface SceneAction {
  type: SceneActionType;
  targets?: string[]; // Box or arrow IDs affected by this action
  text?: string; // Text content for 'text' action
  duration?: number; // Animation duration in ms
  color?: string; // Color override for highlights
  reset?: boolean; // Reset to initial state
}

/**
 * Scene step defines a single animation step
 */
export interface SceneStep {
  id: string;
  label: string;
  description?: string;
  actions: SceneAction[];
  duration?: number; // Step duration in ms (auto-advance if set)
}

/**
 * Animation scene is a collection of steps
 */
export interface AnimationScene {
  id: string;
  name: string;
  description?: string;
  viewMode: ViewMode;
  steps: SceneStep[];
  loop?: boolean; // Loop back to first step after last
}

/**
 * Configuration for customer-specific layer overrides
 */
export interface LayerOverrideConfig {
  business?: Partial<Layer>;
  shopfloorSystems?: Partial<Layer>;
  shopfloorDevices?: Partial<Layer>;
}

/**
 * Complete architecture configuration
 */
export interface ArchitectureConfig {
  viewMode: ViewMode;
  layers: Layer[];
  arrows: Arrow[];
  scenes?: AnimationScene[];
  customOverrides?: LayerOverrideConfig;
}

/**
 * Component state for tracking UI interactions
 */
export interface ComponentState {
  currentView: ViewMode;
  currentSceneIndex: number;
  currentStepIndex: number;
  isPlaying: boolean;
  zoom: number;
  highlightedBoxes: Set<string>;
  visibleArrows: Set<string>;
  hiddenBoxes: Set<string>;
  overlayText: string | null;
}

/**
 * Event emitted when a box is clicked
 */
export interface BoxClickEvent {
  boxId: string;
  layer: LayerType;
  label: string;
}

/**
 * Event emitted when animation step changes
 */
export interface StepChangeEvent {
  sceneId: string;
  stepId: string;
  stepIndex: number;
  totalSteps: number;
}
