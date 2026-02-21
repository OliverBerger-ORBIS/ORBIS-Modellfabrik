import { Component, Input, Output, EventEmitter, TemplateRef, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import type { UseCaseStep } from '../base-use-case.component';

/**
 * Shared header controls for Use-Case diagram components.
 * Provides: title slot, optional view toggle, navigation, step dots, zoom.
 */
@Component({
  selector: 'app-use-case-controls',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './use-case-controls.component.html',
  styleUrls: ['./use-case-controls.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UseCaseControlsComponent {
  @Input() steps: UseCaseStep[] = [];
  @Input() currentStepIndex = 0;
  @Input() zoom = 1;
  @Input() minZoom = 0.4;
  @Input() maxZoom = 1.8;
  @Input() showDescription = false;
  @Input() loopToStart = true;
  @Input() isAutoPlaying = false;
  @Input() viewToggleTemplate: TemplateRef<unknown> | null = null;

  /** Use-Case code (e.g. UC-00) – displayed separately from title when both are set */
  @Input() useCaseCode: string | null = null;
  /** Use-Case title (e.g. Interoperability) – displayed without code prefix when useCaseCode is set */
  @Input() useCaseTitle: string | null = null;

  @Input() btnPrev = $localize`:@@dspArchPrev:Previous`;
  @Input() btnNext = $localize`:@@dspArchNext:Next`;
  @Input() btnAutoPlay = $localize`:@@dspArchAutoPlay:Auto Play`;
  @Input() btnStopPlay = $localize`:@@dspArchStopPlay:Stop`;
  @Input() zoomOutLabel = $localize`:@@shopfloorPreviewZoomOut:Zoom out`;
  @Input() zoomInLabel = $localize`:@@shopfloorPreviewZoomIn:Zoom in`;
  @Input() resetZoomLabel = $localize`:@@shopfloorPreviewResetZoom:Reset zoom`;

  @Input() getStepTitle: (step: UseCaseStep) => string = () => '';

  @Output() prevStep = new EventEmitter<void>();
  @Output() nextStep = new EventEmitter<void>();
  @Output() goToStep = new EventEmitter<number>();
  @Output() toggleAutoPlay = new EventEmitter<void>();
  @Output() toggleLoop = new EventEmitter<void>();
  @Output() toggleDescription = new EventEmitter<void>();
  @Output() zoomIn = new EventEmitter<void>();
  @Output() zoomOut = new EventEmitter<void>();
  @Output() resetZoom = new EventEmitter<void>();
}
