import type { IconKey, FunctionIconConfig } from '../assets/icon-registry';

export type { IconKey, FunctionIconConfig };

export type DetailPanelKind = 'default' | 'orbis' | 'dsp';

export interface DetailItem {
  label: string;
  value: string;
  /** Optional icon key for visual representation (e.g., 'opc-ua-station', 'txt-controller') */
  icon?: string;
}

export interface SelectedDetailView {
  title: string;
  subtitle?: string;
  items: DetailItem[];
  /** Module type for conditional rendering (e.g., DRILL for DSP-Edge section) */
  moduleType?: string;
  /** Optional icon path for the selected cell/module */
  icon?: string;
  /** Optional icon name/key for the selected cell/module */
  iconName?: string;
  /** OPC-UA station items (separate section) */
  opcUaItems?: DetailItem[];
  /** TXT Controller items (separate section) */
  txtControllerItems?: DetailItem[];
  /** Whether module has OPC-UA station (for icon display) */
  hasOpcUaStation?: boolean;
  /** Whether module has TXT controller (for icon display) */
  hasTxtController?: boolean;
}

export interface OrbisPhaseDefinition {
  id: string;
  title: string;
  summary: string;
  activities: string[];
  outcome: string;
}

export interface OrbisUseCaseDefinition {
  id: string;
  title: string;
  description: string;
  highlights: string[];
  icon: string;
}

export interface OrbisPhaseView extends OrbisPhaseDefinition {
  active: boolean;
}

export interface OrbisUseCaseView extends OrbisUseCaseDefinition {
  expanded: boolean;
}

export interface OrbisDetailView {
  phases: OrbisPhaseView[];
  activePhase?: OrbisPhaseDefinition | null;
  useCases: OrbisUseCaseView[];
  websiteUrl: string;
}

export interface DspArchitectureLayer {
  id: string;
  title: string;
  description: string;
  capabilities: string[];
  actionId?: string;
  /** Logo icon key displayed in the corner of the container */
  logoIconKey?: IconKey;
  /** Secondary logo icon key (e.g., Azure logo) */
  secondaryLogoIconKey?: IconKey;
  /** Function icons displayed centered in the container */
  functionIcons?: FunctionIconConfig[];
  /** Position hint for layout: 'left' | 'center' | 'right' */
  position?: 'left' | 'center' | 'right';
}

export interface DspActionLink {
  id: string;
  label: string;
  description: string;
  url: string;
}

export interface DspBusinessProcess {
  id: string;
  label: string;
  icon?: string;
  /** Icon key for logo resolution via ICON_MAP */
  iconKey?: IconKey;
  actionId?: string;
}

export interface DspShopfloorItem {
  label: string;
  icon: string;
  /** Icon key for icon resolution via ICON_MAP */
  iconKey?: IconKey;
}

export interface DspDetailView {
  architecture: DspArchitectureLayer[];
  features: string[];
  actions: DspActionLink[];
  resources: { label: string; url: string }[];
  businessProcesses: DspBusinessProcess[];
  shopfloorPlatforms: DspShopfloorItem[];
  shopfloorSystems: DspShopfloorItem[];
  edgeUrl: string;
  managementUrl: string;
  analyticsUrl: string;
  smartfactoryDashboardUrl: string;
}

export type DetailPanelView =
  | { kind: 'default'; selection: SelectedDetailView }
  | { kind: 'orbis'; view: OrbisDetailView }
  | { kind: 'dsp'; view: DspDetailView };

