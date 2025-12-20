import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import type { DspDetailView, FunctionIconConfig, IconKey } from '../../tabs/configuration-detail.types';
import { DETAIL_ASSET_MAP } from '../../assets/detail-asset-map';
import { getIconPath } from '../../assets/icon-registry';

type DetailAccordionPanel = 'edge' | 'management';

@Component({
  standalone: true,
  selector: 'app-dsp-detail',
  imports: [CommonModule],
  templateUrl: './dsp-detail.component.html',
  styleUrl: './dsp-detail.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspDetailComponent {
  @Input({ required: true }) view!: DspDetailView;
  @Output() actionTriggered = new EventEmitter<{ id: string; url: string }>();

  private readonly layerIconMap: Record<string, string> = {
    ux: DETAIL_ASSET_MAP.DSP_LAYER_SHOPFLOOR,
    edge: DETAIL_ASSET_MAP.DSP_LAYER_EDGE,
    management: DETAIL_ASSET_MAP.DSP_LAYER_CLOUD,
  };

  readonly edgeIcons = [
    this.assetPath(DETAIL_ASSET_MAP.DSP_EDGE_DATABASE),
    this.assetPath(DETAIL_ASSET_MAP.DSP_EDGE_DIGITAL_TWIN),
    this.assetPath(DETAIL_ASSET_MAP.DSP_EDGE_WORKFLOW),
    this.assetPath(DETAIL_ASSET_MAP.DSP_EDGE_NETWORK),
  ];
  protected expandedPanel: DetailAccordionPanel | null = null;

  triggerAction(actionId: string, url: string): void {
    this.actionTriggered.emit({ id: actionId, url });
  }

  private assetPath(candidate: string): string {
    return candidate.startsWith('/') ? candidate.slice(1) : candidate;
  }

  handleKeyActivation(event: Event, actionId: string, url: string): void {
    event.preventDefault();
    this.triggerAction(actionId, url);
  }

  protected architectureTrackBy(_: number, layer: DspDetailView['architecture'][number]): string {
    return layer.id;
  }

  protected featureTrackBy(index: number): number {
    return index;
  }

  protected actionTrackBy(_: number, action: DspDetailView['actions'][number]): string {
    return action.id;
  }

  protected resourceTrackBy(_: number, resource: DspDetailView['resources'][number]): string {
    return resource.url;
  }

  protected getLayerIcon(layerId: string): string {
    return this.layerIconMap[layerId] ?? DETAIL_ASSET_MAP.DSP_FALLBACK;
  }

  protected businessTrackBy(_: number, process: DspDetailView['businessProcesses'][number]): string {
    return process.id;
  }

  protected platformTrackBy(_: number, platform: DspDetailView['shopfloorPlatforms'][number]): string {
    return platform.label;
  }

  protected shopfloorTrackBy(_: number, device: DspDetailView['shopfloorSystems'][number]): string {
    return device.label;
  }

  protected onProcessClick(processId: string): void {
    const url = this.getActionUrl(processId);
    if (url) {
      this.triggerAction(processId, url);
    }
  }

  protected onProcessKey(event: Event, processId: string): void {
    const url = this.getActionUrl(processId);
    if (url) {
      this.handleKeyActivation(event, processId, url);
    }
  }

  protected getLayerActionId(layerId: string): string | null {
    return this.view.architecture.find((layer) => layer.id === layerId)?.actionId ?? null;
  }

  protected onLayerClick(layerId: string): void {
    const actionId = this.getLayerActionId(layerId);
    if (!actionId) {
      return;
    }
    const url = this.getActionUrl(actionId);
    if (url) {
      this.triggerAction(actionId, url);
    }
  }

  protected onLayerKey(event: Event, layerId: string): void {
    const actionId = this.getLayerActionId(layerId);
    if (!actionId) {
      return;
    }
    const url = this.getActionUrl(actionId);
    if (url) {
      this.handleKeyActivation(event, actionId, url);
    }
  }

  protected getLayerById(layerId: string): DspDetailView['architecture'][number] | undefined {
    return this.view.architecture.find((layer) => layer.id === layerId);
  }

  protected getActionUrl(actionId?: string | null): string | null {
    if (!actionId) {
      return null;
    }
    return this.view.actions.find((action) => action.id === actionId)?.url ?? null;
  }

  protected togglePanel(panel: DetailAccordionPanel): void {
    this.expandedPanel = this.expandedPanel === panel ? null : panel;
  }

  protected isExpanded(panel: DetailAccordionPanel): boolean {
    return this.expandedPanel === panel;
  }

  /**
   * Resolves an IconKey to its asset path using the central icon registry.
   */
  protected resolveIconKey(key: IconKey | undefined | null): string {
    return getIconPath(key);
  }

  /**
   * TrackBy function for function icons in a layer.
   */
  protected functionIconTrackBy(index: number, icon: FunctionIconConfig): string {
    return `${icon.iconKey}-${index}`;
  }
}

