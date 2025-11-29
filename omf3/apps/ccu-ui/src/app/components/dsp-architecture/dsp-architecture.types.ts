/**
 * Type definitions for the DSP Architecture SVG component.
 * These types define the data structures for containers, connections, and animation steps.
 */

/** Position for logo icons within a container */
export type LogoPosition = 'top-left' | 'top-right';

/** Visual state of a container */
export type ContainerState = 'normal' | 'highlight' | 'dimmed' | 'hidden';

/** Visual state of a connection */
export type ConnectionState = 'normal' | 'highlight' | 'dimmed' | 'hidden';

/** Anchor side for connection endpoints */
export type AnchorSide = 'top' | 'bottom' | 'left' | 'right';

/** Container type classification */
export type ContainerType = 'layer' | 'box' | 'device' | 'ux' | 'business' | 'shopfloor' | 'dsp-edge' | 'dsp-cloud' | 'label';

/**
 * Configuration for function icons displayed inside containers.
 */
export interface FunctionIconConfig {
  iconKey: string;
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

  /** Optional logo icon key (from DETAIL_ASSET_MAP) */
  logoIconKey?: string;
  /** Position of the logo within the container */
  logoPosition?: LogoPosition;
  /** Optional secondary logo (e.g., Azure logo) */
  secondaryLogoIconKey?: string;
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
