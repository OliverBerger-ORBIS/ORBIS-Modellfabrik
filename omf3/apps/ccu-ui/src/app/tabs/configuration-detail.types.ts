export type DetailPanelKind = 'default' | 'orbis' | 'dsp';

export interface DetailItem {
  label: string;
  value: string;
}

export interface SelectedDetailView {
  title: string;
  subtitle?: string;
  items: DetailItem[];
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
  actionId?: string;
}

export interface DspShopfloorItem {
  label: string;
  icon: string;
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
}

export type DetailPanelView =
  | { kind: 'default'; selection: SelectedDetailView }
  | { kind: 'orbis'; view: OrbisDetailView }
  | { kind: 'dsp'; view: DspDetailView };

