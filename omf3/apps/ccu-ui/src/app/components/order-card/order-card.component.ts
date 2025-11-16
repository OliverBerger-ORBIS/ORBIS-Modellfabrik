import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import type { OrderActive, ProductionStep } from '@omf3/entities';
import { SHOPFLOOR_ASSET_MAP } from '@omf3/testing-fixtures';
import { ShopfloorPreviewComponent } from '../shopfloor-preview/shopfloor-preview.component';
import { ModuleNameService } from '../../services/module-name.service';

type StepState = 'queued' | 'running' | 'completed' | 'failed';

const STEP_STATE_MAP: Record<StepState, { class: string; label: string; icon: string }> = {
  queued: { class: 'queued', label: 'Queued', icon: '⏳' },
  running: { class: 'running', label: 'In progress', icon: '🟠' },
  completed: { class: 'completed', label: 'Finished', icon: '✅' },
  failed: { class: 'failed', label: 'Failed', icon: '❌' },
};

const ORDER_TYPE_ICONS: Record<'PRODUCTION' | 'STORAGE', string> = {
  PRODUCTION: 'headings/maschine.svg',
  STORAGE: 'headings/ladung.svg',
};

@Component({
  standalone: true,
  selector: 'app-order-card',
  imports: [CommonModule, ShopfloorPreviewComponent],
  templateUrl: './order-card.component.html',
  styleUrl: './order-card.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrderCardComponent implements OnChanges {
  @Input({ required: true }) order: OrderActive | null | undefined;
  @Input({ transform: (v: unknown) => Boolean(v) }) isCompleted = false;

  steps: ProductionStep[] = [];
  collapsed = false;

  constructor(private readonly moduleNameService: ModuleNameService) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['order']) {
      this.steps = (this.order?.productionSteps ?? []) as ProductionStep[];
      if (changes['order'].firstChange) {
        this.collapsed = Boolean(this.isCompleted);
      }
    }
  }

  get activeStep(): ProductionStep | undefined {
    return this.steps.find((step) =>
      ['IN_PROGRESS', 'RUNNING'].includes(step.state?.toUpperCase() ?? '')
    );
  }

  get nextPendingStep(): ProductionStep | undefined {
    return this.steps.find((step) =>
      ['ENQUEUED', 'PENDING'].includes(step.state?.toUpperCase() ?? '')
    );
  }

  get completedSteps(): ProductionStep[] {
    return this.steps.filter((step) =>
      ['FINISHED', 'COMPLETED'].includes(step.state?.toUpperCase() ?? '')
    );
  }

  get headerStateClass(): string {
    const state = (this.order?.state ?? this.order?.status ?? '').toUpperCase();
    if (['IN_PROGRESS', 'RUNNING'].includes(state)) {
      return 'state--running';
    }
    if (['COMPLETED', 'FINISHED'].includes(state)) {
      return 'state--completed';
    }
    if (state === 'FAILED') {
      return 'state--failed';
    }
    return 'state--queued';
  }

  get headerStatus(): { class: string; label: string } {
    const state = (this.order?.state ?? this.order?.status ?? '').toUpperCase();

    if (['IN_PROGRESS', 'RUNNING'].includes(state)) {
      return { class: 'state--running', label: 'In progress' };
    }
    if (['COMPLETED', 'FINISHED'].includes(state)) {
      return { class: 'state--completed', label: 'Finished' };
    }
    if (state === 'FAILED') {
      return { class: 'state--failed', label: 'Failed' };
    }
    return { class: 'state--queued', label: 'Queued' };
  }

  get orderTypeIcon(): string {
    const key = (this.order?.orderType ?? '').toUpperCase() === 'STORAGE' ? 'STORAGE' : 'PRODUCTION';
    return ORDER_TYPE_ICONS[key];
  }

  get orderStartedAt(): string | null {
    return this.formatTimestamp(this.order?.startedAt);
  }

  get orderDuration(): string | null {
    const startedAt = this.order?.startedAt;
    if (!startedAt) {
      return null;
    }

    const finishedAt = this.getOrderEndTimestamp();
    if (finishedAt) {
      return this.formatDuration(startedAt, finishedAt);
    }

    if (!this.isOrderFinished()) {
      return this.formatDuration(startedAt, new Date().toISOString());
    }

    return null;
  }

  get workpieceId(): string | null {
    return this.readOrderString('workpieceId') ?? this.order?.productId ?? null;
  }

  get activeStepStartedAt(): string | null {
    return this.formatTimestamp(this.activeStep?.startedAt);
  }

  stepBackgroundClass(step: ProductionStep): string {
    const state = this.resolveStepState(step);
    return `step--${STEP_STATE_MAP[state].class}`;
  }

  stepStatusClass(step: ProductionStep): string {
    const state = this.resolveStepState(step);
    return `step__status-icon--${STEP_STATE_MAP[state].class}`;
  }

  stepStatusIcon(step: ProductionStep): string {
    const state = this.resolveStepState(step);
    return STEP_STATE_MAP[state].icon;
  }

  stepStateLabel(step: ProductionStep): string {
    const state = this.resolveStepState(step);
    return STEP_STATE_MAP[state].label;
  }

  private resolveStepState(step: ProductionStep): StepState {
    const normalized = (step.state ?? '').toUpperCase();
    if (normalized === 'FAILED') {
      return 'failed';
    }
    if (['IN_PROGRESS', 'RUNNING'].includes(normalized)) {
      return 'running';
    }
    if (['FINISHED', 'COMPLETED'].includes(normalized)) {
      return 'completed';
    }
    return 'queued';
  }

  private formatTimestamp(value?: string | null): string | null {
    if (!value) {
      return null;
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return null;
    }

    return new Intl.DateTimeFormat('de-DE', {
      dateStyle: 'short',
      timeStyle: 'medium',
    }).format(date);
  }

  private formatDuration(start?: string | null, end?: string | null): string | null {
    if (!start) {
      return null;
    }

    const startDate = new Date(start);
    const endDate = end ? new Date(end) : new Date();

    if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
      return null;
    }

    let delta = Math.max(0, endDate.getTime() - startDate.getTime());

    const hours = Math.floor(delta / (1000 * 60 * 60));
    delta -= hours * 1000 * 60 * 60;
    const minutes = Math.floor(delta / (1000 * 60));
    delta -= minutes * 1000 * 60;
    const seconds = Math.floor(delta / 1000);

    const parts = [] as string[];
    if (hours > 0) {
      parts.push(`${hours}h`);
    }
    if (minutes > 0 || hours > 0) {
      parts.push(`${minutes}m`);
    }
    parts.push(`${seconds}s`);

    return parts.join(' ');
  }

  private readOrderString(key: string): string | null {
    if (!this.order) {
      return null;
    }
    const record = this.order as unknown as Record<string, unknown>;
    const value = record[key];
    return typeof value === 'string' && value ? value : null;
  }

  trackStep(_: number, step: ProductionStep): string {
    return step.id;
  }

  get previewStep(): ProductionStep | undefined {
    return (
      this.activeStep ??
      this.nextPendingStep ??
      (this.completedSteps.length ? this.completedSteps[this.completedSteps.length - 1] : undefined)
    );
  }

  commandLabel(step: ProductionStep): string {
    if (step.type === 'NAVIGATION') {
      return `${step.source ?? ''} → ${step.target ?? ''}`.trim();
    }
    return step.command ?? step.type ?? '';
  }

  moduleIcon(step: ProductionStep): string | null {
    const key =
      step.type === 'NAVIGATION'
        ? 'FTS'
        : step.moduleType ?? step.type ?? '';
    return this.assetPath(key);
  }

  moduleName(step: ProductionStep): string {
    if (step.type === 'NAVIGATION') {
      return this.moduleNameService.getModuleDisplayText('FTS', 'id-full');
    }
    const moduleType = step.moduleType ?? step.type ?? '';
    return this.moduleNameService.getModuleDisplayText(moduleType, 'id-full');
  }

  moduleFullName(step: ProductionStep): string {
    if (step.type === 'NAVIGATION') {
      return this.moduleNameService.getModuleFullName('FTS');
    }
    const moduleType = step.moduleType ?? step.type ?? '';
    return this.moduleNameService.getModuleFullName(moduleType);
  }

  private assetPath(key?: string | null): string | null {
    if (!key) {
      return null;
    }
    const asset = SHOPFLOOR_ASSET_MAP[key];
    if (!asset) {
      return null;
    }
    return asset.startsWith('/') ? asset.slice(1) : asset;
  }

  toggleCollapse(): void {
    this.collapsed = !this.collapsed;
  }

  private getOrderEndTimestamp(): string | null {
    if (!this.order) {
      return null;
    }

    const primaryKeys = ['stoppedAt', 'updatedAt', 'finishedAt', 'timestamp', 'receivedAt'] as const;

    for (const key of primaryKeys) {
      const candidate = this.readStringProp(this.order, key);
      if (this.isValidTimestamp(candidate)) {
        return candidate!;
      }
    }

    const stepCandidates = this.order.productionSteps ?? [];
    let latest: string | null = null;
    for (const step of stepCandidates) {
      for (const key of ['finishedAt', 'stoppedAt', 'startedAt'] as const) {
        const candidate = this.readStringProp(step, key);
        if (!this.isValidTimestamp(candidate)) {
          continue;
        }

        if (!latest || new Date(candidate!).getTime() > new Date(latest).getTime()) {
          latest = candidate!;
        }
        break;
      }
    }

    return latest;
  }

  private readStringProp(source: unknown, key: string): string | null {
    if (!source || typeof source !== 'object') {
      return null;
    }
    const value = (source as Record<string, unknown>)[key];
    return typeof value === 'string' ? value : null;
  }

  private isValidTimestamp(value?: string | null): value is string {
    if (!value) {
      return false;
    }
    const time = new Date(value).getTime();
    return Number.isFinite(time);
  }

  private isOrderFinished(): boolean {
    const state = (this.order?.state ?? this.order?.status ?? '').toUpperCase();
    return ['COMPLETED', 'FINISHED', 'ERROR', 'FAILED'].includes(state);
  }
}

