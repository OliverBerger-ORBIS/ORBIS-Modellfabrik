import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import type { OrbisDetailView } from '../../tabs/configuration-detail.types';

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

  // Map phase IDs to relative asset paths (from ASSET_PATHS in detail-asset-map.ts)
  // Use relative paths without leading slash - Angular will combine with baseHref automatically
  private readonly phaseIconMap: Record<string, string> = {
    phase1: 'details/orbis/data-lake.svg',
    phase2: 'details/orbis/semantic.svg',
    phase3: 'details/orbis/dashboard.svg',
    phase4: 'details/orbis/workflow_1.svg',
    phase5: 'details/orbis/ai.svg',
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
    // Return relative path without leading slash - Angular will combine with baseHref automatically
    // This matches the pattern used in DSP-Architecture component
    const relativePath = this.phaseIconMap[phaseId];
    if (relativePath) {
      return relativePath;
    }
    return 'details/orbis/stack.svg';
  }

  protected getPhaseName(title: string): string {
    const separatorIndex = title.indexOf('•');
    if (separatorIndex === -1) {
      return title;
    }
    return title.slice(separatorIndex + 1).trim();
  }

  protected getUseCaseIcon(iconPath: string): string {
    // Return relative path without leading slash - Angular will combine with baseHref automatically
    // This matches the pattern used in DSP-Architecture component
    // If iconPath already has baseHref (starts with '/ORBIS-Modellfabrik/'), extract relative path
    if (iconPath.startsWith('/ORBIS-Modellfabrik/')) {
      return iconPath.slice('/ORBIS-Modellfabrik/'.length);
    }
    // If it's an absolute path (starts with '/'), remove leading slash
    if (iconPath.startsWith('/')) {
      return iconPath.slice(1);
    }
    // If it's already a relative path, use as-is
    return iconPath;
  }
}

