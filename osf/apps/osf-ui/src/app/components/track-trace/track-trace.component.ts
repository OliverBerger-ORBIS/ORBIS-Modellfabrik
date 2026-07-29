import { Component, ChangeDetectionStrategy, OnInit, OnDestroy, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Observable, map, Subscription, combineLatest, BehaviorSubject } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import { WorkpieceHistoryService, WorkpieceHistory, TrackTraceEvent, OrderContext, StationTaskGroup } from '../../services/workpiece-history.service';
import { ModuleNameService } from '../../services/module-name.service';
import { EnvironmentService } from '../../services/environment.service';
import {
  TrackTraceEnvironmentService,
  type TrackTraceEnvironmentRow,
  type TrackTraceEnvironmentSnapshot,
} from '../../services/track-trace-environment.service';
import { ICONS } from '../../shared/icons/icon.registry';

/** Manufacturing event types that should be grouped by station */
const MANUFACTURING_EVENT_TYPES = [
  'PICK',
  'PROCESS',
  'DROP',
  'DRILL',
  'MILL',
  'CHECK_QUALITY',
] as const;

/** Workpiece / NFC color family for cascade selection */
export type TrackTraceWorkpieceColor = 'WHITE' | 'BLUE' | 'RED';

export interface TrackTraceCascadeVm {
  color: TrackTraceWorkpieceColor | null;
  tags: WorkpieceHistory[];
  stats: { WHITE: number; BLUE: number; RED: number; total: number };
}

/**
 * Track & Trace Component
 * Enables workpiece-based tracking through the entire production process
 * Shows Order context (Storage Order vs Production Order) with ERP links
 * Groups manufacturing tasks by station (PICK → PROCESS → DROP)
 */
@Component({
  selector: 'app-track-trace',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './track-trace.component.html',
  styleUrls: ['./track-trace.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TrackTraceComponent implements OnInit, OnDestroy {
  private readonly workpieceHistoryService = inject(WorkpieceHistoryService);
  private readonly moduleNameService = inject(ModuleNameService);
  private readonly environmentService = inject(EnvironmentService);
  private readonly trackTraceEnvironment = inject(TrackTraceEnvironmentService);
  private readonly cdr = inject(ChangeDetectorRef);
  private subscription?: Subscription;

  searchTerm = '';
  selectedWorkpieceId: string | null = null;
  private readonly selectedWorkpieceId$ = new BehaviorSubject<string | null>(null);

  /** Selected workpiece color for NFC cascade (step 1) */
  readonly selectedColor$ = new BehaviorSubject<TrackTraceWorkpieceColor | null>(null);

  /** Filter substring for NFC tag list (step 2) */
  private readonly filterTerm$ = new BehaviorSubject<string>('');

  /** All tracked workpieces */
  workpieces$!: Observable<WorkpieceHistory[]>;

  /** Cascade: counts per color + filtered NFC tags sorted by earliest event time */
  cascadeVm$!: Observable<TrackTraceCascadeVm>;

  /** Currently selected workpiece history */
  selectedHistory$!: Observable<WorkpieceHistory | undefined>;

  /** MQTT environment / sensor column (30 s refresh; immediate on alarm edges) */
  environmentSnapshot$!: Observable<TrackTraceEnvironmentSnapshot | null>;

  ngOnInit(): void {
    const environmentKey = this.environmentService.current.key;
    
    // Initialize tracking for current environment
    this.workpieceHistoryService.initialize(environmentKey);

    // Get all workpieces
    this.workpieces$ = this.workpieceHistoryService.getHistory$(environmentKey).pipe(
      map((historyMap) => Array.from(historyMap.values()))
    );

    this.cascadeVm$ = combineLatest([
      this.workpieces$,
      this.selectedColor$.asObservable(),
      this.filterTerm$.asObservable(),
    ]).pipe(
      map(([wps, color, term]) => ({
        color,
        tags: color ? this.buildNfcTagList(wps, color, term) : [],
        stats: this.buildColorStats(wps),
      })),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Get selected workpiece history - reactive to selectedWorkpieceId changes
    this.selectedHistory$ = combineLatest([
      this.workpieceHistoryService.getHistory$(environmentKey),
      this.selectedWorkpieceId$.asObservable()
    ]).pipe(
      map(([historyMap, selectedId]) => (selectedId ? historyMap.get(selectedId) : undefined)),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    this.environmentSnapshot$ = combineLatest([
      this.selectedWorkpieceId$.asObservable(),
      this.trackTraceEnvironment.snapshot$,
    ]).pipe(
      map(([id, snap]) => (id ? snap : null)),
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
  }

  selectWorkpiece(workpieceId: string): void {
    this.selectedWorkpieceId = workpieceId;
    this.selectedWorkpieceId$.next(workpieceId);
  }

  /** Step 1: choose White / Blue / Red — clears selected NFC tag */
  selectColor(color: TrackTraceWorkpieceColor): void {
    this.selectedColor$.next(color);
    this.selectedWorkpieceId = null;
    this.selectedWorkpieceId$.next(null);
  }

  /** Clears chosen color (step 1) and NFC selection */
  clearColorSelection(): void {
    this.selectedColor$.next(null);
    this.selectedWorkpieceId = null;
    this.selectedWorkpieceId$.next(null);
  }

  /** Search / filter input for NFC tag IDs within the selected color */
  onSearchFilterChange(value: string): void {
    this.searchTerm = value;
    this.filterTerm$.next(value);
  }

  /** Clears filter text only */
  clearSearchFilter(): void {
    this.searchTerm = '';
    this.filterTerm$.next('');
  }

  /** Template: distinguish empty NFC list vs filter miss */
  hasActiveSearchFilter(): boolean {
    return this.searchTerm.trim().length > 0;
  }

  /** Close button on event history — NFC list stays visible */
  clearHistorySelection(): void {
    this.selectedWorkpieceId = null;
    this.selectedWorkpieceId$.next(null);
  }

  /** Earliest shopfloor event timestamp label for NFC row (chronological ordering context) */
  firstSeenTimestamp(wp: WorkpieceHistory): string | null {
    const iso = this.earliestEventIso(wp);
    return iso ? this.formatTimestamp(iso) : null;
  }

  private normalizeWorkpieceColor(type: string | undefined): string {
    return (type || '').toUpperCase();
  }

  private buildColorStats(wps: WorkpieceHistory[]): { WHITE: number; BLUE: number; RED: number; total: number } {
    let w = 0;
    let b = 0;
    let r = 0;
    for (const wp of wps) {
      switch (this.normalizeWorkpieceColor(wp.workpieceType)) {
        case 'WHITE':
          w++;
          break;
        case 'BLUE':
          b++;
          break;
        case 'RED':
          r++;
          break;
        default:
          break;
      }
    }
    return { WHITE: w, BLUE: b, RED: r, total: wps.length };
  }

  private buildNfcTagList(wps: WorkpieceHistory[], color: TrackTraceWorkpieceColor, termRaw: string): WorkpieceHistory[] {
    const term = termRaw.trim().toLowerCase();
    let list = wps.filter((wp) => this.normalizeWorkpieceColor(wp.workpieceType) === color);
    if (term) {
      list = list.filter((wp) => wp.workpieceId.toLowerCase().includes(term));
    }
    return [...list].sort((a, b) => {
      const ta = this.earliestEventTimestampMs(a);
      const tb = this.earliestEventTimestampMs(b);
      if (ta !== tb) return ta - tb;
      return a.workpieceId.localeCompare(b.workpieceId);
    });
  }

  private earliestEventTimestampMs(wp: WorkpieceHistory): number {
    if (!wp.events?.length) return Number.POSITIVE_INFINITY;
    let min = Number.POSITIVE_INFINITY;
    for (const e of wp.events) {
      const t = Date.parse(e.timestamp);
      if (!Number.isNaN(t) && t < min) min = t;
    }
    return min;
  }

  private earliestEventIso(wp: WorkpieceHistory): string | undefined {
    if (!wp.events?.length) return undefined;
    let minMs = Number.POSITIVE_INFINITY;
    let best = wp.events[0].timestamp;
    for (const e of wp.events) {
      const t = Date.parse(e.timestamp);
      if (!Number.isNaN(t) && t < minMs) {
        minMs = t;
        best = e.timestamp;
      }
    }
    return best;
  }

  getTypeClass(type: string | undefined): string {
    if (!type) return '';
    return type.toLowerCase();
  }

  getEventIcon(eventType: string, event?: TrackTraceEvent): string {
    // Return SVG path instead of emoji
    switch (eventType.toUpperCase()) {
      case 'DOCK':
        return ICONS.shopfloor.shared.dockEvent;
      case 'PICK':
        return ICONS.shopfloor.shared.pickEvent;
      case 'DROP':
        return ICONS.shopfloor.shared.dropEvent;
      case 'TURN':
        // Check for TURN LEFT or TURN RIGHT direction
        if (event?.details && 'direction' in event.details) {
          const dir = String(event.details['direction']).toUpperCase();
          if (dir === 'LEFT') return ICONS.shopfloor.shared.turnLeftEvent;
          if (dir === 'RIGHT') return ICONS.shopfloor.shared.turnRightEvent;
        }
        return ICONS.shopfloor.shared.turnEvent; // Fallback to generic turn icon
      case 'PASS':
        return ICONS.shopfloor.shared.passEvent;
      case 'TRANSPORT':
        return ICONS.shopfloor.shared.agvVehicle;
      case 'PROCESS':
      case 'DRILL':
      case 'MILL':
      case 'CHECK_QUALITY':
      case 'INPUT_RGB':
      case 'RGB_NFC':
        return ICONS.shopfloor.shared.processEvent;
      default:
        return ICONS.shopfloor.shared.locationMarker;
    }
  }
  
  getEventLabel(eventType: string, event?: TrackTraceEvent): string {
    const type = eventType.toUpperCase();
    if (type === 'TURN' && event?.details && 'direction' in event.details) {
      const dir = String(event.details['direction']).toUpperCase();
      if (dir === 'LEFT') return $localize`:@@ftsActionTurnLeft:TURN LEFT`;
      if (dir === 'RIGHT') return $localize`:@@ftsActionTurnRight:TURN RIGHT`;
    }
    if (type === 'INPUT_RGB') {
      return $localize`:@@trackTraceEventColor:Color`;
    }
    if (type === 'RGB_NFC') {
      return $localize`:@@trackTraceEventNfc:NFC`;
    }
    // Keep action name clean; rack slot is shown via getEventPositionLabel
    return eventType;
  }

  /** HBW rack slot / FTS bucket position label. */
  getEventPositionLabel(event: TrackTraceEvent): string | null {
    const eventType = (event.eventType || '').toUpperCase();

    if (event.eventSource === 'FTS') {
      const intersectionNum = event.details?.['intersectionNumber'];
      const loadPos = event.details?.['loadPosition'];
      const workpieceType = (event.workpieceType || '').toUpperCase();

      const parts: string[] = [];
      if (typeof intersectionNum === 'string' && intersectionNum.trim()) {
        parts.push(
          $localize`:@@trackTraceIntersection:Intersection ${intersectionNum}:number:`
        );
      }

      // Bucket slot + color for non-DOCK FTS events
      if (typeof loadPos === 'string' && loadPos.trim() && eventType !== 'DOCK') {
        const slotLabel = $localize`:@@trackTracePosition:Position: ${loadPos}:position:`;
        const colorSuffix = workpieceType ? ` (${workpieceType})` : '';
        parts.push(`${slotLabel}${colorSuffix}`);
      }
      return parts.length > 0 ? parts.join(' · ') : null;
    }

    // Station events
    const pos = event.details?.['loadPosition'];
    if (typeof pos !== 'string' || !pos.trim()) {
      return null;
    }
    const station = (event.stationId || event.moduleName || '').toUpperCase();
    if (station === 'HBW') {
      return $localize`:@@trackTracePositionInHbw:Position in HBW: ${pos}:position:`;
    }
    return $localize`:@@trackTracePositionGeneric:Position: ${pos}:position:`;
  }

  /** Icon for bucket slot in FTS transport events (colored workpiece or empty slot). */
  getBucketPositionIcon(event: TrackTraceEvent): string | null {
    if (event.eventSource !== 'FTS') return null;
    const eventType = (event.eventType || '').toUpperCase();
    if (eventType === 'DOCK') return null;
    const loadPos = event.details?.['loadPosition'];
    if (typeof loadPos !== 'string' || !loadPos.trim()) return null;
    // Show colored workpiece icon or empty slot
    return this.getWorkpieceIcon(event.workpieceType || '');
  }

  /** Result badge for CHECK_QUALITY events (e.g. "OK", "FAILED"). */
  getQualityResultBadge(event: TrackTraceEvent): string | null {
    const eventType = (event.eventType || '').toUpperCase();
    if (eventType !== 'CHECK_QUALITY') {
      return null;
    }
    const result = event.details?.['result'];
    if (typeof result === 'string' && result.trim()) {
      return result.toUpperCase();
    }
    return null;
  }

  getQualityResultClass(event: TrackTraceEvent): string {
    const badge = this.getQualityResultBadge(event);
    if (!badge) return '';
    if (badge === 'OK' || badge === 'PASS' || badge === 'PASSED') {
      return 'quality-result--ok';
    }
    if (
      badge === 'FAILED' ||
      badge === 'FAIL' ||
      badge === 'NOK' ||
      badge === 'ERROR'
    ) {
      return 'quality-result--failed';
    }
    return 'quality-result--unknown';
  }

  getEventPrimaryActor(event: TrackTraceEvent): string {
    const eventType = (event.eventType || '').toUpperCase();
    const isStationAction =
      eventType === 'PICK' ||
      eventType === 'PROCESS' ||
      eventType === 'DROP' ||
      eventType === 'DRILL' ||
      eventType === 'MILL' ||
      eventType === 'CHECK_QUALITY' ||
      eventType === 'INPUT_RGB' ||
      eventType === 'RGB_NFC';
    if (isStationAction && event.stationId) {
      return event.stationId.toUpperCase();
    }
    return event.moduleName || 'FTS';
  }

  getAgvAccentClass(label: string | null | undefined): string {
    const normalized = (label || '').toUpperCase();
    if (normalized.includes('AGV-1')) {
      return 'agv-accent--1';
    }
    if (normalized.includes('AGV-2')) {
      return 'agv-accent--2';
    }
    return '';
  }

  getEventTransportContext(event: TrackTraceEvent): string | null {
    const eventType = (event.eventType || '').toUpperCase();
    const isBracketAction =
      eventType === 'PICK' ||
      eventType === 'PROCESS' ||
      eventType === 'DROP' ||
      eventType === 'DRILL' ||
      eventType === 'MILL' ||
      eventType === 'CHECK_QUALITY' ||
      eventType === 'INPUT_RGB' ||
      eventType === 'RGB_NFC';
    if (!isBracketAction) {
      return null;
    }
    const moduleName = (event.moduleName || '').toUpperCase();
    const stationId = (event.stationId || '').toUpperCase();
    if (!moduleName || moduleName === stationId) {
      return null;
    }
    if (moduleName.includes('AGV') || moduleName.includes('FTS')) {
      return moduleName;
    }
    return null;
  }

  /** Publisher badge label (B1): FTS MQTT vs module device MQTT. */
  getEventSourceLabel(source: 'FTS' | 'MODULE' | undefined): string | null {
    if (source === 'MODULE') {
      return $localize`:@@trackTraceEventSourceModule:Module`;
    }
    if (source === 'FTS') {
      return $localize`:@@trackTraceEventSourceFts:FTS`;
    }
    return null;
  }

  getOrderTypeIcon(orderType: string | undefined): string {
    if (!orderType) return 'assets/svg/ui/heading-customer-orders.svg';
    switch (orderType.toUpperCase()) {
      case 'STORAGE':
        return 'assets/svg/ui/heading-storage.svg';
      case 'PRODUCTION':
        return 'assets/svg/ui/heading-production.svg';
      default:
        return 'assets/svg/ui/heading-customer-orders.svg';
    }
  }

  getOrderTypeLabel(orderType: string | undefined): string {
    if (!orderType) return $localize`:@@trackTraceOrder:Order`;
    switch (orderType.toUpperCase()) {
      case 'STORAGE':
        return $localize`:@@trackTraceStorageOrder:Storage Order (Raw Material)`;
      case 'PRODUCTION':
        return $localize`:@@trackTraceProductionOrder:Production Order`;
      default:
        return orderType;
    }
  }

  formatPlannedStationChain(chain: string[] | undefined): string {
    if (!chain || chain.length === 0) {
      return '';
    }
    return chain.join(' -> ');
  }

  isOrderScopedEvent(event: TrackTraceEvent): boolean {
    const orderType = (event.orderType || '').toUpperCase();
    return orderType === 'STORAGE' || orderType === 'PRODUCTION';
  }

  getEventEnvironmentSnapshot(event: TrackTraceEvent): TrackTraceEnvironmentSnapshot | null {
    const raw = event.details?.['environmentSnapshot'];
    if (!raw || typeof raw !== 'object') {
      return null;
    }
    const candidate = raw as Partial<TrackTraceEnvironmentSnapshot>;
    if (!Array.isArray(candidate.rows)) {
      return null;
    }
    const rows = candidate.rows.filter(
      (row): row is TrackTraceEnvironmentRow =>
        !!row &&
        typeof row.id === 'string' &&
        typeof row.label === 'string' &&
        typeof row.value === 'string' &&
        (row.variant === 'normal' || row.variant === 'warn' || row.variant === 'alarm')
    );
    return {
      rows,
      hasAlarm: Boolean(candidate.hasAlarm),
      updatedAt: typeof candidate.updatedAt === 'string' ? candidate.updatedAt : event.timestamp,
    };
  }

  isEnvironmentAlarm(snapshot: TrackTraceEnvironmentSnapshot): boolean {
    return snapshot.hasAlarm || snapshot.rows.some((row) => row.variant === 'alarm');
  }

  isEnvironmentWarn(snapshot: TrackTraceEnvironmentSnapshot): boolean {
    if (this.isEnvironmentAlarm(snapshot)) {
      return false;
    }
    return snapshot.rows.some((row) => row.variant === 'warn');
  }

  getOrderFlowAccents(
    events: TrackTraceEvent[] | undefined,
    order: OrderContext | null | undefined
  ): Array<{ station: string; index: number; total: number; active: boolean }> {
    const plannedChain = (order?.plannedStationChain ?? []).map((step) => step.toUpperCase());
    if (!events || !order || plannedChain.length === 0) {
      return [];
    }

    const orderType = (order.orderType || '').toUpperCase();
    const orderEvents = events.filter((event) => event.orderId === order.orderId);

    return plannedChain.map((station, idx) => {
      const active = orderEvents.some((event) =>
        this.isFlowAnchorEvent(orderType, station, (event.eventType || '').toUpperCase()) &&
        (event.stationId || '').toUpperCase() === station
      );
      return {
        station,
        index: idx + 1,
        total: plannedChain.length,
        active,
      };
    });
  }

  getBusinessFlowAccent(
    event: TrackTraceEvent,
    order: OrderContext | null | undefined
  ): { station: string; index: number; total: number } | null {
    const plannedChain = (order?.plannedStationChain ?? []).map((step) => step.toUpperCase());
    if (plannedChain.length === 0) {
      return null;
    }

    const station = (event.stationId || '').toUpperCase();
    if (!station) {
      return null;
    }

    const stationIndex = plannedChain.indexOf(station);
    if (stationIndex < 0) {
      return null;
    }

    return {
      station,
      index: stationIndex + 1,
      total: plannedChain.length,
    };
  }

  /** Station column: module MQTT (+ intake). Transport column: FTS DOCK/PASS/TURN. */
  classifyShopfloorColumn(event: TrackTraceEvent): 'station' | 'transport' {
    const type = (event.eventType || '').toUpperCase();
    if (event.eventSource === 'MODULE') {
      return 'station';
    }
    if (event.eventSource === 'FTS') {
      return 'transport';
    }
    if (
      type === 'INPUT_RGB' ||
      type === 'RGB_NFC' ||
      type === 'PICK' ||
      type === 'DROP' ||
      type === 'PROCESS' ||
      type === 'DRILL' ||
      type === 'MILL' ||
      type === 'CHECK_QUALITY'
    ) {
      return 'station';
    }
    return 'transport';
  }

  /**
   * Chronological shopfloor rows: station visits get one header + business chip;
   * events go into Station or Transport column (B3 layout).
   */
  buildShopfloorTimeline(
    events: TrackTraceEvent[],
    order: OrderContext | null
  ): Array<
    | { kind: 'station-header'; stationId: string; stationName: string }
    | {
        kind: 'event';
        event: TrackTraceEvent;
        column: 'station' | 'transport';
        showBusinessChip: boolean;
      }
  > {
    const sorted = [...events].sort((a, b) => {
      const timeDiff = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
      if (timeDiff !== 0) {
        return timeDiff;
      }
      return (a.actionId || '').localeCompare(b.actionId || '');
    });

    const items: Array<
      | { kind: 'station-header'; stationId: string; stationName: string }
      | {
          kind: 'event';
          event: TrackTraceEvent;
          column: 'station' | 'transport';
          showBusinessChip: boolean;
        }
    > = [];

    let lastStationVisitId: string | null = null;

    for (const event of sorted) {
      if (!this.isOrderScopedEvent(event)) {
        continue;
      }
      const column = this.classifyShopfloorColumn(event);

      if (column === 'station') {
        const sid = (event.stationId || event.moduleName || '').toUpperCase();
        const isNewVisit = !!sid && sid !== lastStationVisitId;
        if (isNewVisit) {
          items.push({
            kind: 'station-header',
            stationId: sid,
            stationName: event.stationName || sid,
          });
          lastStationVisitId = sid;
        }
        items.push({
          kind: 'event',
          event,
          column: 'station',
          showBusinessChip: isNewVisit && this.getBusinessFlowAccent(event, order) !== null,
        });
      } else {
        lastStationVisitId = null;
        items.push({
          kind: 'event',
          event,
          column: 'transport',
          showBusinessChip: false,
        });
      }
    }

    return items;
  }

  trackByTimelineItem(
    index: number,
    item:
      | { kind: 'station-header'; stationId: string }
      | { kind: 'event'; event: TrackTraceEvent }
  ): string {
    if (item.kind === 'station-header') {
      return `hdr-${item.stationId}-${index}`;
    }
    return `evt-${item.event.timestamp}-${item.event.eventType}-${item.event.actionId || index}`;
  }

  private isFlowAnchorEvent(orderType: string, station: string, eventType: string): boolean {
    if (orderType === 'PRODUCTION') {
      if (['DRILL', 'MILL', 'AIQS'].includes(station)) {
        return (
          eventType === 'PROCESS' ||
          eventType === 'DRILL' ||
          eventType === 'MILL' ||
          eventType === 'CHECK_QUALITY'
        );
      }
      if (station === 'HBW') {
        return eventType === 'DROP';
      }
      if (station === 'DPS') {
        return eventType === 'PICK';
      }
      return false;
    }

    if (orderType === 'STORAGE') {
      // One DPS visit chip is driven by timeline (first station event); anchors for strip helper:
      if (station === 'DPS') {
        return eventType === 'DROP' || eventType === 'INPUT_RGB' || eventType === 'RGB_NFC';
      }
      if (station === 'HBW') {
        return eventType === 'PICK';
      }
      return false;
    }

    return false;
  }

  getStationIcon(stationId: string | undefined): string {
    if (!stationId) return ICONS.shopfloor.systems.factory;
    switch (stationId.toUpperCase()) {
      case 'HBW':
        return ICONS.shopfloor.stations.hbw;
      case 'DRILL':
        return ICONS.shopfloor.stations.drill;
      case 'MILL':
        return ICONS.shopfloor.stations.mill;
      case 'AIQS':
        return ICONS.shopfloor.stations.aiqs;
      case 'DPS':
        return ICONS.shopfloor.stations.dps;
      default:
        return ICONS.shopfloor.systems.factory;
    }
  }

  formatTimestamp(timestamp: string): string {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  }

  formatDuration(seconds: number | undefined): string {
    if (!seconds) return '';
    return `${seconds}s`;
  }

  getLocationLabel(location: string): string {
    const locationInfo = this.moduleNameService.getLocationDisplayText(location);
    if (locationInfo.serialNumber) {
      return `${locationInfo.moduleType} (${locationInfo.fullName}) (${locationInfo.serialNumber})`;
    }
    return `${locationInfo.moduleType} (${locationInfo.fullName})`;
  }

  getLocationInfo(location: string): { moduleType: string; fullName: string; serialNumber: string | null } {
    return this.moduleNameService.getLocationDisplayText(location);
  }

  getWorkpieceIcon(workpieceType: string): string {
    const type = workpieceType.toUpperCase();
    if (type === 'BLUE') return ICONS.shopfloor.workpieces.blue.dim3;
    if (type === 'WHITE') return ICONS.shopfloor.workpieces.white.dim3;
    if (type === 'RED') return ICONS.shopfloor.workpieces.red.dim3;
    return ICONS.shopfloor.workpieces.slotEmpty;
  }

  /** Group events by order context */
  groupEventsByOrder(history: WorkpieceHistory): { order: OrderContext | null; events: TrackTraceEvent[]; stationGroups: StationTaskGroup[] }[] {
    if (!history.orders || history.orders.length === 0) {
      return [{ order: null, events: history.events, stationGroups: [] }];
    }

    const groups: { order: OrderContext | null; events: TrackTraceEvent[]; stationGroups: StationTaskGroup[] }[] = [];

    // Group events by order type
    let currentOrderType: string | undefined = undefined;
    let currentGroup: TrackTraceEvent[] = [];

    for (const event of history.events) {
      if (event.orderType !== currentOrderType) {
        if (currentGroup.length > 0) {
          const order = history.orders?.find((o) => o.orderType === currentOrderType) || null;
          const stationGroups = this.groupEventsByStation(currentGroup, currentOrderType);
          
          // All events are shown (both station and non-station events)
          // The grouping by Sub-Order-ID will handle the separation
          groups.push({ order, events: currentGroup, stationGroups });
        }
        currentOrderType = event.orderType;
        currentGroup = [event];
      } else {
        currentGroup.push(event);
      }
    }

    // Add last group
    if (currentGroup.length > 0) {
      const order = history.orders?.find((o) => o.orderType === currentOrderType) || null;
      const stationGroups = this.groupEventsByStation(currentGroup, currentOrderType);
      
      // All events are shown (both station and non-station events)
      // The grouping by Sub-Order-ID will handle the separation
      groups.push({ order, events: currentGroup, stationGroups });
    }

    return groups;
  }

  /** Group production events by station (PICK → PROCESS → DROP)
   * Includes all modules: MILL, DRILL, AIQS, HBW, DPS
   */
  private groupEventsByStation(events: TrackTraceEvent[], orderType: string | undefined): StationTaskGroup[] {
    if (orderType !== 'PRODUCTION') {
      return [];
    }

    // First, group events by subOrderId
    const eventsBySubOrder = new Map<string, TrackTraceEvent[]>();
    
    for (const event of events) {
      // Consider all module events (PICK, PROCESS, DROP) with stationId
      // Includes: MILL, DRILL, AIQS, HBW, DPS
      if (
        event.stationId &&
        MANUFACTURING_EVENT_TYPES.includes(event.eventType.toUpperCase() as (typeof MANUFACTURING_EVENT_TYPES)[number])
      ) {
        const subOrderId = event.subOrderId || 'unknown';
        if (!eventsBySubOrder.has(subOrderId)) {
          eventsBySubOrder.set(subOrderId, []);
        }
        eventsBySubOrder.get(subOrderId)!.push(event);
      }
    }

    // Then, group by station (events with same subOrderId belong to same station)
    const stationGroups: StationTaskGroup[] = [];
    const stationMap = new Map<string, StationTaskGroup>();

    for (const [subOrderId, subOrderEvents] of eventsBySubOrder.entries()) {
      if (subOrderEvents.length === 0) continue;

      // All events with same subOrderId belong to the same station
      const firstEvent = subOrderEvents[0];
      const stationId = firstEvent.stationId || 'UNKNOWN';
      const stationName = firstEvent.stationName || stationId;

      // Get or create station group
      if (!stationMap.has(stationId)) {
        const stationGroup: StationTaskGroup = {
          stationId,
          stationName,
          events: [],
          startTime: undefined,
          endTime: undefined,
          duration: undefined,
        };
        stationMap.set(stationId, stationGroup);
        stationGroups.push(stationGroup);
      }

      // Add all events from this subOrder to the station group
      const stationGroup = stationMap.get(stationId)!;
      stationGroup.events.push(...subOrderEvents);
    }

    // Sort events within each station group by timestamp
    // Calculate duration for each station group
    for (const stationGroup of stationGroups) {
      stationGroup.events.sort((a, b) => {
        return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
      });

      if (stationGroup.events.length > 0) {
        stationGroup.startTime = stationGroup.events[0]?.timestamp;
        stationGroup.endTime = stationGroup.events[stationGroup.events.length - 1]?.timestamp;
        if (stationGroup.startTime && stationGroup.endTime) {
          stationGroup.duration = this.calculateDuration(stationGroup.startTime, stationGroup.endTime);
        }
      }
    }

    // Sort station groups by start time
    stationGroups.sort((a, b) => {
      if (!a.startTime || !b.startTime) return 0;
      return new Date(a.startTime).getTime() - new Date(b.startTime).getTime();
    });

    return stationGroups;
  }

  /**
   * Calculate duration in seconds between two timestamps
   */
  private calculateDuration(startTime: string, endTime: string): number {
    try {
      const start = new Date(startTime).getTime();
      const end = new Date(endTime).getTime();
      return Math.round((end - start) / 1000);
    } catch {
      return 0;
    }
  }

  formatStationDuration(seconds: number | undefined): string {
    if (!seconds) return '';
    if (seconds < 60) {
      return `${seconds}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  }

  trackByWorkpieceId(_index: number, workpiece: WorkpieceHistory): string {
    return workpiece.workpieceId;
  }

  trackByEvent(index: number, event: TrackTraceEvent): string {
    // Use combination of timestamp and index for unique tracking
    return `${event.timestamp}-${index}`;
  }

  trackByOrder(index: number, group: { order: OrderContext | null; events: TrackTraceEvent[] }): string {
    return group.order?.orderId || `group-${index}`;
  }

  trackByStation(index: number, station: StationTaskGroup): string {
    return `${station.stationId}-${index}`;
  }

  trackBySubOrderGroup(index: number, group: { subOrderId: string; moduleId?: string; moduleName?: string; events: TrackTraceEvent[] }): string {
    return group.subOrderId || `group-${index}`;
  }

  trackByEnvRow(_index: number, row: { id: string }): string {
    return row.id;
  }

  /**
   * Group events by Sub-Order-ID and Module
   * Events with same Sub-Order-ID are grouped under their module
   * Other events are listed separately
   * IMPORTANT: ALL events must be included, no filtering!
   */
  groupEventsBySubOrder(
    events: TrackTraceEvent[],
    stationGroups: StationTaskGroup[]
  ): Array<{ subOrderId: string; moduleId?: string; moduleName?: string; events: TrackTraceEvent[] }> {
    // Build map of Sub-Order-ID to Module from station groups
    const subOrderToModule = new Map<string, { moduleId: string; moduleName: string }>();
    stationGroups.forEach((station) => {
      station.events.forEach((event) => {
        if (event.subOrderId) {
          subOrderToModule.set(event.subOrderId, {
            moduleId: station.stationId,
            moduleName: station.stationName,
          });
        }
      });
    });

    // Group ALL events by Sub-Order-ID (including events without subOrderId)
    const eventsBySubOrder = new Map<string, TrackTraceEvent[]>();
    const eventsWithoutSubOrder: TrackTraceEvent[] = [];
    
    events.forEach((event) => {
      if (event.subOrderId) {
        const subOrderId = event.subOrderId;
        if (!eventsBySubOrder.has(subOrderId)) {
          eventsBySubOrder.set(subOrderId, []);
        }
        eventsBySubOrder.get(subOrderId)!.push(event);
      } else {
        // Events without subOrderId go to a special group
        eventsWithoutSubOrder.push(event);
      }
    });

    // Build result groups
    const groups: Array<{ subOrderId: string; moduleId?: string; moduleName?: string; events: TrackTraceEvent[] }> = [];

    // First, add module-grouped events (sorted by timestamp, then subOrderId, then actionId)
    const moduleGroups: Array<{ subOrderId: string; moduleId: string; moduleName: string; events: TrackTraceEvent[] }> = [];
    eventsBySubOrder.forEach((eventList, subOrderId) => {
      const moduleInfo = subOrderToModule.get(subOrderId);
      if (moduleInfo) {
        // Sort events: timestamp first, then subOrderId, then actionId
        eventList.sort((a, b) => {
          const timeDiff = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
          if (timeDiff !== 0) return timeDiff;
          
          const subOrderDiff = (a.subOrderId || '').localeCompare(b.subOrderId || '');
          if (subOrderDiff !== 0) return subOrderDiff;
          
          return (a.actionId || '').localeCompare(b.actionId || '');
        });
        moduleGroups.push({
          subOrderId,
          moduleId: moduleInfo.moduleId,
          moduleName: moduleInfo.moduleName,
          events: eventList,
        });
      }
    });

    // Collect all groups (module groups + other events) and sort by earliest event time (C1).
    // Sub-Order suffix order is only a tie-breaker — chronology has higher priority for the demo.
    const allGroups: Array<{ subOrderId: string; moduleId?: string; moduleName?: string; events: TrackTraceEvent[] }> = [];
    
    // Add module groups
    moduleGroups.forEach(group => {
      allGroups.push(group);
    });
    
    // Add other events with Sub-Order-ID but no module assignment
    eventsBySubOrder.forEach((eventList, subOrderId) => {
      if (!subOrderToModule.has(subOrderId)) {
        // Sort events: timestamp first, then subOrderId, then actionId
        eventList.sort((a, b) => {
          const timeDiff = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
          if (timeDiff !== 0) return timeDiff;
          
          const subOrderDiff = (a.subOrderId || '').localeCompare(b.subOrderId || '');
          if (subOrderDiff !== 0) return subOrderDiff;
          
          return (a.actionId || '').localeCompare(b.actionId || '');
        });
        allGroups.push({
          subOrderId,
          events: eventList,
        });
      }
    });

    // Events without Sub-Order-ID (e.g. buffered Color before NFC) — merge chronologically, not at end
    if (eventsWithoutSubOrder.length > 0) {
      eventsWithoutSubOrder.sort((a, b) => {
        const timeDiff = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
        if (timeDiff !== 0) return timeDiff;
        return (a.actionId || '').localeCompare(b.actionId || '');
      });
      allGroups.push({
        subOrderId: 'no-sub-order',
        events: eventsWithoutSubOrder,
      });
    }

    allGroups.sort((a, b) => {
      const timeA = this.getGroupEarliestTimestampMs(a.events);
      const timeB = this.getGroupEarliestTimestampMs(b.events);
      if (timeA !== timeB) {
        return timeA - timeB;
      }
      const numA = this.extractSubOrderNumber(a.subOrderId);
      const numB = this.extractSubOrderNumber(b.subOrderId);
      if (numA !== null && numB !== null) {
        return numA - numB;
      }
      return (a.subOrderId || '').localeCompare(b.subOrderId || '');
    });

    groups.push(...allGroups);

    return groups;
  }

  /**
   * Earliest timestamp in a sub-order group (ms). Used for chronological group order (C1).
   */
  private getGroupEarliestTimestampMs(events: TrackTraceEvent[]): number {
    let min = Number.POSITIVE_INFINITY;
    for (const event of events) {
      const t = new Date(event.timestamp).getTime();
      if (!Number.isNaN(t) && t < min) {
        min = t;
      }
    }
    return min === Number.POSITIVE_INFINITY ? 0 : min;
  }

  /**
   * Extract numeric part from Sub-Order-ID
   * Format: "orderId-1" -> 1, "orderId-10" -> 10
   * Returns null if extraction fails
   */
  private extractSubOrderNumber(subOrderId: string | undefined): number | null {
    if (!subOrderId) return null;
    
    // Extract number after last '-'
    const parts = subOrderId.split('-');
    if (parts.length < 2) return null;
    
    const lastPart = parts[parts.length - 1];
    const num = parseInt(lastPart, 10);
    
    return isNaN(num) ? null : num;
  }

}

