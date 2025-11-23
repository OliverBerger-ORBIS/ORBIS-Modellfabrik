import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import type { OrbisDetailView } from '../../tabs/configuration-detail.types';
import { DETAIL_ASSET_MAP } from '../../assets/detail-asset-map';

@Component({
  standalone: true,
  selector: 'app-orbis-detail',
  imports: [CommonModule],
  templateUrl: './orbis-detail.component.html',
  styleUrl: './orbis-detail.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrbisDetailComponent {
  @Input({ required: true }) view!: OrbisDetailView;
  @Output() phaseSelected = new EventEmitter<string>();
  @Output() useCaseToggled = new EventEmitter<string>();

  private readonly phaseIconMap: Record<string, string> = {
    phase1: DETAIL_ASSET_MAP.ORBIS_PHASE_1,
    phase2: DETAIL_ASSET_MAP.ORBIS_PHASE_2,
    phase3: DETAIL_ASSET_MAP.ORBIS_PHASE_3,
    phase4: DETAIL_ASSET_MAP.ORBIS_PHASE_4,
    phase5: DETAIL_ASSET_MAP.ORBIS_PHASE_5,
  };

  selectPhase(phaseId: string): void {
    this.phaseSelected.emit(phaseId);
  }

  toggleUseCase(useCaseId: string): void {
    this.useCaseToggled.emit(useCaseId);
  }

  protected phaseTrackBy(_: number, phase: OrbisDetailView['phases'][number]): string {
    return phase.id;
  }

  protected useCaseTrackBy(_: number, useCase: OrbisDetailView['useCases'][number]): string {
    return useCase.id;
  }

  protected getPhaseIcon(phaseId: string): string {
    return this.phaseIconMap[phaseId] ?? DETAIL_ASSET_MAP.ORBIS_FALLBACK;
  }

  protected getPhaseName(title: string): string {
    const separatorIndex = title.indexOf('•');
    if (separatorIndex === -1) {
      return title;
    }
    return title.slice(separatorIndex + 1).trim();
  }
}

