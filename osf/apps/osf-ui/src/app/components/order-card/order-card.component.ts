import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, Input, OnChanges, OnDestroy, OnInit, SimpleChanges } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Subscription } from 'rxjs';
import { Observable, of } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { utcIsoTimestampMs, type OrderActive, type ProductionStep } from '@osf/entities';
import { SHOPFLOOR_ASSET_MAP } from '@osf/testing-fixtures';
import { ShopfloorPreviewComponent, type FtsPositionItem } from '../shopfloor-preview/shopfloor-preview.component';
import { ModuleNameService } from '../../services/module-name.service';
import { ShopfloorMappingService } from '../../services/shopfloor-mapping.service';
import { CorrelationInfoService, type CorrelationInfo } from '../../services/correlation-info.service';
import { FtsOrderAssignmentService } from '../../services/fts-order-assignment.service';
import { LanguageService } from '../../services/language.service';
import { resolveLegacyShopfloorPath } from '../../shared/icons/legacy-shopfloor-map';
import { ICONS } from '../../shared/icons/icon.registry';

type StepState = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';

const STEP_STATE_MAP: Record<StepState, { class: string; label: () => string; icon: string }> = {
  queued: { class: 'queued', label: () => $localize`:@@orderCardStepQueued:Queued`, icon: '⏳' },
  running: { class: 'running', label: () => $localize`:@@orderCardStepInProgress:In progress`, icon: '🟠' },
  completed: { class: 'completed', label: () => $localize`:@@orderCardStepFinished:Finished`, icon: '✅' },
  failed: { class: 'failed', label: () => $localize`:@@orderCardStepFailed:Failed`, icon: '❌' },
  cancelled: {
    class: 'cancelled',
    label: () => $localize`:@@orderCardStepCancelled:Cancelled`,
    icon: '⊘',
  },
};

const ORDER_TYPE_ICONS: Record<'PRODUCTION' | 'STORAGE', string> = {
  PRODUCTION: ICONS.ui.orderProduction,
  STORAGE: ICONS.ui.orderStorage,
};

const PRODUCT_ICON_MAP: Record<'BLUE' | 'WHITE' | 'RED', string> = {
  BLUE: ICONS.shopfloor.workpieces.blue.product,
  WHITE: ICONS.shopfloor.workpieces.white.product,
  RED: ICONS.shopfloor.workpieces.red.product,
};

const THREE_D_ICON_MAP: Record<'BLUE' | 'WHITE' | 'RED', string> = {
  BLUE: ICONS.shopfloor.workpieces.blue.dim3,
  WHITE: ICONS.shopfloor.workpieces.white.dim3,
  RED: ICONS.shopfloor.workpieces.red.dim3,
};

const DEFAULT_SHOPFLOOR_ICON = resolveLegacyShopfloorPath('assets/svg/shopfloor/shared/question.svg');

/** Callback to request ERP correlation info for an order. Passes full order so requestId can be sent when available. */
export type RequestCorrelationFn = (order: OrderActive) => Promise<void>;

@Component({
  standalone: true,
  selector: 'app-order-card',
  imports: [CommonModule, ShopfloorPreviewComponent],
  templateUrl: './order-card.component.html',
  styleUrl: './order-card.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrderCardComponent implements OnInit, OnChanges, OnDestroy {
  @Input({ required: true }) order: OrderActive | null | undefined;
  @Input({ transform: (v: unknown) => Boolean(v) }) isCompleted = false;
  @Input({ transform: (v: unknown) => Boolean(v) }) expanded = false;
  @Input() onRequestCorrelation: RequestCorrelationFn | null = null;
  /** When set (e.g. from Orders tab), show all AGVs on the map with AGV-1/AGV-2 colors */
  @Input() ftsPositions: FtsPositionItem[] | null = null;

  steps: ProductionStep[] = [];
  collapsed = false;
  contentGridColsVar: string | null = null;

  private readonly orderIdSubject = new BehaviorSubject<string>('');
  private assignmentsSubscription?: Subscription;

  correlationInfo$: Observable<CorrelationInfo | null> = this.orderIdSubject.pipe(
    switchMap((id) => (id ? this.correlationInfoService.getCorrelationInfo$(id) : of(null)))
  );

  constructor(
    private readonly moduleNameService: ModuleNameService,
    private readonly mappingService: ShopfloorMappingService,
    private readonly correlationInfoService: CorrelationInfoService,
    private readonly ftsAssignmentService: FtsOrderAssignmentService,
    private readonly cdr: ChangeDetectorRef,
    private readonly router: Router,
    private readonly languageService: LanguageService
  ) {}

  ngOnInit(): void {
    this.orderIdSubject.next(this.order?.orderId ?? '');
    this.updateCollapsedState();
    this.assignmentsSubscription = this.ftsAssignmentService
      .getAssignments$()
      .subscribe(() => this.cdr.markForCheck());
  }

  ngOnDestroy(): void {
    this.assignmentsSubscription?.unsubscribe();
  }

  onShopfloorViewportChanged(viewport: { widthPx: number; heightPx: number; scale: number }): void {
    // Order cards are narrower than full-page tabs; use tighter clamps.
    const bufferedLeft = viewport.widthPx + 32;
    const clampedLeft = clamp(bufferedLeft, 320, 820);
    this.contentGridColsVar = `${clampedLeft}px 1fr`;
    this.cdr.markForCheck();
  }

  async requestCorrelation(): Promise<void> {
    if (this.order && this.onRequestCorrelation) {
      await this.onRequestCorrelation(this.order);
    }
  }

  /**
   * Click a module cell on the embedded shopfloor map → Shopfloor tab with that station focused (`?module=` matches layout cell name, e.g. HBW).
   */
  onShopfloorPreviewCellSelected(event: { id: string; kind: 'module' | 'fixed' }): void {
    if (event.kind !== 'module') {
      return;
    }
    const cell = this.mappingService.getCellById(event.id);
    const moduleName = cell?.name?.trim();
    if (!moduleName) {
      return;
    }
    const locale = this.languageService.current;
    void this.router.navigate([locale, 'shopfloor'], { queryParams: { module: moduleName } });
  }

  get requestCorrelationButtonLabel(): string {
    return $localize`:@@orderCardRequestCorrelation:Request ERP info`;
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['order']) {
      this.steps = (this.order?.productionSteps ?? []) as ProductionStep[];
      this.orderIdSubject.next(this.order?.orderId ?? '');
    }
    
    // Always update collapsed state when any relevant input changes
    this.updateCollapsedState();
  }

  private updateCollapsedState(): void {
    // CRITICAL: If expanded is true, always uncollapse
    // Otherwise, collapse if this is a completed order
    if (this.expanded) {
      this.collapsed = false;
    } else if (this.isCompleted) {
      this.collapsed = true;
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
    if (['FAILED', 'ERROR'].includes(state)) {
      return 'state--failed';
    }
    return 'state--queued';
  }

  get headerStatus(): { class: string; label: string } {
    const state = (this.order?.state ?? this.order?.status ?? '').toUpperCase();

    if (['IN_PROGRESS', 'RUNNING'].includes(state)) {
      return { class: 'state--running', label: $localize`:@@orderCardStatusInProgress:In progress` };
    }
    if (['COMPLETED', 'FINISHED'].includes(state)) {
      return { class: 'state--completed', label: $localize`:@@orderCardStatusFinished:Finished` };
    }
    if (['FAILED', 'ERROR'].includes(state)) {
      return { class: 'state--failed', label: $localize`:@@orderCardStatusFailed:Failed` };
    }
    return { class: 'state--queued', label: $localize`:@@orderCardStatusQueued:Queued` };
  }

  get orderTypeIcon(): string {
    const key = (this.order?.orderType ?? '').toUpperCase() === 'STORAGE' ? 'STORAGE' : 'PRODUCTION';
    return ORDER_TYPE_ICONS[key];
  }

  get workpieceIcon(): string | null {
    const orderType = (this.order?.orderType ?? '').toUpperCase();
    const workpieceType = (this.order?.type ?? '').toUpperCase() as 'BLUE' | 'WHITE' | 'RED';
    
    if (orderType === 'STORAGE') {
      return THREE_D_ICON_MAP[workpieceType] ?? null;
    }
    // PRODUCTION
    return PRODUCT_ICON_MAP[workpieceType] ?? null;
  }

  getOrderTypeLabel(): string {
    const orderType = (this.order?.orderType ?? '').toUpperCase();
    if (orderType === 'STORAGE') {
      return $localize`:@@orderCardOrderTypeStorage:Storage`;
    }
    return $localize`:@@orderCardOrderTypeProduction:Production`;
  }

  getWorkpieceTypeLabel(): string {
    const type = (this.order?.type ?? '').toUpperCase();
    switch (type) {
      case 'BLUE':
        return $localize`:@@orderCardWorkpieceTypeBlue:Blue`;
      case 'WHITE':
        return $localize`:@@orderCardWorkpieceTypeWhite:White`;
      case 'RED':
        return $localize`:@@orderCardWorkpieceTypeRed:Red`;
      default:
        return type;
    }
  }

  getStepNumberLabel(stepNumber: number): string {
    const formatted = stepNumber.toString().padStart(2, '0');
    // Use template literal with $localize for interpolation
    const stepLabel = $localize`:@@orderCardStepLabel:STEP`;
    return `${stepLabel} ${formatted}`;
  }

  getToggleDetailsLabel(): string {
    return $localize`:@@orderCardToggleDetails:Toggle order details`;
  }

  get orderStartedAt(): string | null {
    return this.formatTimestamp(this.order?.startedAt);
  }

  get orderDuration(): string | null {
    const orderStartedAt = this.order?.startedAt;
    if (!orderStartedAt) {
      return null;
    }

    // Duration = difference between order start and current active step start
    const activeStepStartedAt = this.activeStep?.startedAt;
    if (activeStepStartedAt) {
      return this.formatDuration(orderStartedAt, activeStepStartedAt);
    }

    // If order is finished, use the end timestamp
    if (this.isOrderFinished()) {
    const finishedAt = this.getOrderEndTimestamp();
    if (finishedAt) {
        return this.formatDuration(orderStartedAt, finishedAt);
    }
    }

    // If no active step yet, show duration from start to now
    return this.formatDuration(orderStartedAt, utcIsoTimestampMs());
  }

  get workpieceId(): string | null {
    return this.readOrderString('workpieceId') ?? this.order?.productId ?? null;
  }

  get activeStepStartedAt(): string | null {
    return this.formatTimestampWithDate(this.activeStep?.startedAt);
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
    return STEP_STATE_MAP[state].label();
  }

  private resolveStepState(step: ProductionStep): StepState {
    const normalized = (step.state ?? '').toUpperCase();
    if (['FAILED', 'ERROR'].includes(normalized)) {
      return 'failed';
    }
    if (normalized === 'CANCELLED') {
      return 'cancelled';
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
      timeStyle: 'medium',
    }).format(date);
  }

  private formatTimestampWithDate(value?: string | null): string | null {
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

  targetModuleIcon(step: ProductionStep): string | null {
    // Nur bei NAVIGATION-Schritten und wenn target vorhanden und nicht "START"
    if (step.type !== 'NAVIGATION' || !step.target) {
      return null;
    }
    
    const target = (step.target ?? '').toUpperCase();
    if (target === 'START' || target === '') {
      return null;
    }
    
    return this.assetPath(target);
  }

  moduleName(step: ProductionStep): string {
    if (step.type === 'NAVIGATION') {
      const ftsSerial =
        step.serialNumber ?? this.ftsAssignmentService.getFtsSerialForStep(this.order?.orderId, step.id);
      const agvLabel = ftsSerial ? this.mappingService.getAgvLabel(ftsSerial) : null;
      const id = agvLabel ?? $localize`:@@moduleNameAGV:AGV`;
      const full = this.moduleNameService.getModuleFullName('FTS');
      return `${id} (${full})`;
    }
    const moduleType = step.moduleType ?? step.type ?? '';
    return this.moduleNameService.getModuleDisplayText(moduleType, 'id-full');
  }

  moduleFullName(step: ProductionStep): string {
    if (step.type === 'NAVIGATION') {
      const ftsSerial =
        step.serialNumber ?? this.ftsAssignmentService.getFtsSerialForStep(this.order?.orderId, step.id);
      const agvLabel = ftsSerial ? this.mappingService.getAgvLabel(ftsSerial) : null;
      return agvLabel ?? $localize`:@@moduleNameAGV:AGV`;
    }
    const moduleType = step.moduleType ?? step.type ?? '';
    return this.moduleNameService.getModuleFullName(moduleType);
  }

  private assetPath(key?: string | null): string | null {
    const candidateKey = key ?? '';
    const normalizedKey = candidateKey.toUpperCase();
    const asset =
      SHOPFLOOR_ASSET_MAP[candidateKey] ??
      SHOPFLOOR_ASSET_MAP[normalizedKey] ??
      DEFAULT_SHOPFLOOR_ICON;
    if (!asset) {
      return null;
    }
    return resolveLegacyShopfloorPath(asset);
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

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

