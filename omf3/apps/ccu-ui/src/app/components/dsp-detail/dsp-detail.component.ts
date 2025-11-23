import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import type { DspDetailView } from '../../tabs/configuration-detail.types';
import { DETAIL_ASSET_MAP } from '../../assets/detail-asset-map';

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
    cloud: DETAIL_ASSET_MAP.DSP_LAYER_CLOUD,
    edge: DETAIL_ASSET_MAP.DSP_LAYER_EDGE,
    shopfloor: DETAIL_ASSET_MAP.DSP_LAYER_SHOPFLOOR,
  };

  triggerAction(actionId: string, url: string): void {
    this.actionTriggered.emit({ id: actionId, url });
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

  protected businessTrackBy(index: number): number {
    return index;
  }

  protected shopfloorTrackBy(_: number, device: DspDetailView['shopfloorSystems'][number]): string {
    return device.label;
  }
}

