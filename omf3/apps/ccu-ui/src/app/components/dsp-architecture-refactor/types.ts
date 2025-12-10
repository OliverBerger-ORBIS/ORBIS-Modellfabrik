/**
 * Type definitions for the DSP Architecture SVG component.
 * These types define the data structures for containers, connections, and animation steps.
 */
import type { IconKey } from '../../assets/icon-registry';

/** Position for logo icons within a container */
export type LogoPosition = 'top-left' | 'top-right';

/** Position for label text within a container */
export type LabelPosition = 'top-center' | 'bottom-center' | 'left' | 'left-inside' | 'right-inside' | 'bottom';

/** Visual state of a container */
export type ContainerState = 'normal' | 'highlight' | 'dimmed' | 'hidden';

/** Visual state of a connection */
export type ConnectionState = 'normal' | 'highlight' | 'dimmed' | 'hidden';

/** Anchor side for connection endpoints */
export type AnchorSide = 'top' | 'bottom' | 'left' | 'right';

/** Container type classification */
export type ContainerType = 'layer' | 'box' | 'device' | 'ux' | 'business' | 'shopfloor' | 'shopfloor-group' | 'dsp-edge' | 'dsp-cloud' | 'label' | 'environment-label';

/**
 * Configuration for function icons displayed inside containers.
 */
export interface FunctionIconConfig {
  iconKey: IconKey;
  size: number;
}

/**
 * Configuration for a visual container/box in the architecture diagram.
 */
export interface ContainerConfig {
  id: string;
  label?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  type: ContainerType;

  /** Optional logo icon key (from icon-registry) */
  logoIconKey?: IconKey;
  /** Position of the logo within the container */
  logoPosition?: LogoPosition;
  /** Optional center icon key (e.g., for UX dashboard center icon) */
  centerIconKey?: IconKey;
  /** Optional secondary logo (e.g., Azure logo) from icon-registry */
  secondaryLogoIconKey?: IconKey;
  /** Position of the secondary logo */
  secondaryLogoPosition?: LogoPosition;

  /** Function icons displayed centered in the container */
  functionIcons?: FunctionIconConfig[];

  /** Visual state for animation */
  state?: ContainerState;

  /** Border color override */
  borderColor?: string;
  /** Background color override */
  backgroundColor?: string;
  /** Text color override */
  textColor?: string;

  /** Font size for label */
  fontSize?: number;
  /** Whether this is a group/layer container */
  isGroup?: boolean;
  /** Position of the label within the container */
  labelPosition?: LabelPosition;
  /** Clickable URL for navigation when container is clicked */
  url?: string;
  /** Environment label to display above the container (e.g., "On Premise", "Cloud") */
  environmentLabel?: string;
}

/**
 * Configuration for a connection/arrow between containers.
 */
export interface ConnectionConfig {
  id: string;
  fromId: string;
  toId: string;
  fromSide?: AnchorSide;
  toSide?: AnchorSide;
  state?: ConnectionState;
  /** Whether to show arrow head */
  hasArrow?: boolean;
  /** Whether connection is bidirectional */
  bidirectional?: boolean;
}

/**
 * Configuration for an animation step (slide).
 */
export interface StepConfig {
  id: string;
  label: string;
  /** Container IDs that should be visible in this step */
  visibleContainerIds: string[];
  /** Container IDs that should be highlighted in this step */
  highlightedContainerIds: string[];
  /** Connection IDs that should be visible in this step */
  visibleConnectionIds: string[];
  /** Connection IDs that should be highlighted in this step */
  highlightedConnectionIds: string[];
  /** Whether to show function icons in containers (default true) */
  showFunctionIcons?: boolean;
  /** Specific function icon keys to highlight in this step */
  highlightedFunctionIcons?: string[];
  /** Description text to display for this step */
  description?: string;
}

/**
 * Point coordinates in SVG coordinate system.
 */
export interface Point {
  x: number;
  y: number;
}

/**
 * Complete diagram configuration.
 */
export interface DiagramConfig {
  containers: ContainerConfig[];
  connections: ConnectionConfig[];
  steps: StepConfig[];
  viewBox: {
    width: number;
    height: number;
  };
}
