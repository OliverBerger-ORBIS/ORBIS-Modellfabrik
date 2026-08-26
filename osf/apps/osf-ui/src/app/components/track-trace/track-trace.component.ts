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
import { AgvRouteService } from '../../services/agv-route.service';
import { ShopfloorLayoutService } from '../../services/shopfloor-layout.service';
import { ShopfloorMappingService } from '../../services/shopfloor-mapping.service';
import type { ShopfloorLayoutConfig } from '../shopfloor-preview/shopfloor-layout.types';
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

/** Compact shopfloor map for FTS timeline events (roads + AGV marker). */
export interface AgvEventShopfloorMiniMap {
  viewBox: string;
  roads: Array<{ x1: number; y1: number; x2: number; y2: number }>;
  marker: { x: number; y: number; color: string; r: number };
}

/** Timeline rows for Station | Transport columns. */
export type TrackTraceTimelineItem =
  | {
      kind: 'station-header';
      stationId: string;
      stationName: string;
      serialNumber: string | null;
    }
  | {
      kind: 'transport-group';
      id: string;
      fromStation: string | null;
      toStation: string | null;
      events: TrackTraceEvent[];
      istStations: string[];
      agvLabel: string;
    }
  | {
      kind: 'event';
      event: TrackTraceEvent;
      column: 'station' | 'transport';
      showBusinessChip: boolean;
      /** Unplanned / Ist station chip (dashed) in business-flow column. */
      istStationChip: string | null;
    };

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
  private readonly agvRouteService = inject(AgvRouteService);
  private readonly shopfloorLayout = inject(ShopfloorLayoutService);
  private readonly shopfloorMapping = inject(ShopfloorMappingService);
  private readonly cdr = inject(ChangeDetectorRef);
  private subscription?: Subscription;
  private layoutSubscription?: Subscription;
  private layoutConfig: ShopfloorLayoutConfig | null = null;
  /** Expanded environment panels (key = event identity). Default: collapsed. */
  private readonly expandedEnvironmentKeys = new Set<string>();
  /** Expanded transport groups between planned stations. Default: collapsed. */
  private readonly expandedTransportGroupIds = new Set<string>();

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
        tags: this.buildNfcTagList(wps, color, term),
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

    this.layoutSubscription = this.shopfloorLayout.config$.subscribe((config) => {
      this.layoutConfig = config;
      if (config) {
        this.agvRouteService.initializeLayout(config);
      }
      this.cdr.markForCheck();
    });
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
    this.layoutSubscription?.unsubscribe();
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

  /** Search / filter input for NFC tag IDs (within selected color, or all when no color) */
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

  private buildNfcTagList(
    wps: WorkpieceHistory[],
    color: TrackTraceWorkpieceColor | null,
    termRaw: string
  ): WorkpieceHistory[] {
    const term = termRaw.trim().toLowerCase();
    let list = color
      ? wps.filter((wp) => this.normalizeWorkpieceColor(wp.workpieceType) === color)
      : [...wps];
    if (term) {
      list = list.filter((wp) => wp.workpieceId.toLowerCase().includes(term));
    }
    // Newest first (top-left → right → next row)
    return [...list].sort((a, b) => {
      const ta = this.earliestEventTimestampMs(a);
      const tb = this.earliestEventTimestampMs(b);
      if (ta !== tb) return tb - ta;
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

  /**
   * AGV load buckets: always Pos 1–3 (MQTT may omit empty slots → EMPTY).
   */
  getTransportLoadRows(event: TrackTraceEvent): Array<{
    icon: string;
    label: string;
    position: string;
    empty: boolean;
  }> {
    if (event.eventSource !== 'FTS') {
      return [];
    }
    const byPos = new Map<string, { loadId?: string; loadType?: string; loadPosition?: string }>();
    for (const load of this.getAgvLoadsFromEvent(event)) {
      const pos = String(load.loadPosition || '').trim();
      if (pos) {
        byPos.set(pos, load);
      }
    }
    // Legacy single loadPosition when agvLoads missing
    if (byPos.size === 0) {
      const loadPos = event.details?.['loadPosition'];
      const eventType = (event.eventType || '').toUpperCase();
      if (typeof loadPos === 'string' && loadPos.trim() && eventType !== 'DOCK') {
        byPos.set(loadPos.trim(), {
          loadPosition: loadPos.trim(),
          loadType: event.workpieceType,
          loadId: event.workpieceId,
        });
      }
    }

    if (byPos.size === 0) {
      return [];
    }

    return ['1', '2', '3'].map((position) => {
      const load = byPos.get(position);
      const color = (load?.loadType || '').toUpperCase();
      if (color === 'BLUE' || color === 'WHITE' || color === 'RED') {
        return {
          position,
          empty: false,
          icon: this.getWorkpieceIcon(color),
          label: $localize`:@@trackTraceAgvBucketFilled:Pos ${position}:position: (${color}:color:)`,
        };
      }
      return {
        position,
        empty: true,
        icon: ICONS.shopfloor.workpieces.slotEmpty,
        label: $localize`:@@trackTraceAgvBucketEmpty:Pos ${position}:position: (EMPTY)`,
      };
    });
  }

  /**
   * Compact shopfloor preview for FTS events: orthogonal road network + AGV marker in AGV color.
   * Module endpoints use layout node positions (HBW/DPS = main subcell), not raw road centers.
   */
  getAgvEventShopfloorMiniMap(event: TrackTraceEvent): AgvEventShopfloorMiniMap | null {
    if (event.eventSource !== 'FTS' || !event.location || !this.layoutConfig) {
      return null;
    }
    const pos =
      this.agvRouteService.getAgvMarkerCenter(event.location) ??
      this.agvRouteService.getNodePosition(event.location);
    if (!pos) {
      return null;
    }
    const canvas = this.layoutConfig.metadata?.canvas;
    if (!canvas?.width || !canvas?.height) {
      return null;
    }
    const serial = event.moduleId || '';
    const color = this.shopfloorMapping.getAgvColor(serial);
    const resolveEndpoint = (ref: string, fallback: { x: number; y: number }): { x: number; y: number } =>
      this.agvRouteService.getNodePosition(ref) ?? fallback;

    const roads: Array<{ x1: number; y1: number; x2: number; y2: number }> = [];
    for (const road of this.layoutConfig.parsed_roads ?? []) {
      const from = resolveEndpoint(road.from.ref, road.from.center);
      const to = resolveEndpoint(road.to.ref, road.to.center);
      // Orthogonalize non-axis-aligned segments (compound road centers vs main-cell nodes)
      if (from.x === to.x || from.y === to.y) {
        roads.push({ x1: from.x, y1: from.y, x2: to.x, y2: to.y });
      } else {
        // Prefer bend on shared intersection axis (horizontal then vertical)
        roads.push({ x1: from.x, y1: from.y, x2: to.x, y2: from.y });
        roads.push({ x1: to.x, y1: from.y, x2: to.x, y2: to.y });
      }
    }
    return {
      viewBox: `0 0 ${canvas.width} ${canvas.height}`,
      roads,
      marker: { x: pos.x, y: pos.y, color, r: 56 },
    };
  }

  /** Intersection meta for FTS (shown above load rows). */
  getTransportMetaLabel(event: TrackTraceEvent): string | null {
    if (event.eventSource !== 'FTS') {
      return null;
    }
    const intersectionNum = event.details?.['intersectionNumber'];
    if (typeof intersectionNum === 'string' && intersectionNum.trim()) {
      return $localize`:@@trackTraceIntersection:Intersection ${intersectionNum}:number:`;
    }
    return null;
  }

  /** Station rack position label (non-FTS); skipped for HBW when mini-grid is shown. */
  getEventPositionLabel(event: TrackTraceEvent): string | null {
    if (event.eventSource === 'FTS') {
      return null;
    }
    if (this.getHbwMiniGrid(event)) {
      return null;
    }
    const pos = event.details?.['loadPosition'];
    if (typeof pos !== 'string' || !pos.trim()) {
      return null;
    }
    return $localize`:@@trackTracePositionGeneric:Position: ${pos}:position:`;
  }

  /**
   * Mini HBW 3×3 (A1–C3) for MODULE HBW PICK/DROP — MQTT shelf snapshot + active slot.
   */
  getHbwMiniGrid(event: TrackTraceEvent): {
    cells: Array<{
      loadPosition: string;
      loadType: string | null;
      icon: string;
      active: boolean;
      empty: boolean;
    }>;
    activePosition: string | null;
  } | null {
    if (event.eventSource !== 'MODULE') {
      return null;
    }
    const station = (event.stationId || event.moduleName || '').toUpperCase();
    if (station !== 'HBW') {
      return null;
    }
    const eventType = (event.eventType || '').toUpperCase();
    if (eventType !== 'PICK' && eventType !== 'DROP') {
      return null;
    }

    const activeRaw = event.details?.['loadPosition'];
    const activePosition =
      typeof activeRaw === 'string' && activeRaw.trim() ? activeRaw.trim().toUpperCase() : null;

    const order = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3'];
    const byPos = new Map<string, { loadType: string | null; loadId: string | null }>();
    const rawShelf = event.details?.['hbwShelf'];
    if (Array.isArray(rawShelf)) {
      for (const cell of rawShelf) {
        if (!cell || typeof cell !== 'object') {
          continue;
        }
        const row = cell as { loadPosition?: unknown; loadType?: unknown; loadId?: unknown };
        const pos = typeof row.loadPosition === 'string' ? row.loadPosition.trim().toUpperCase() : '';
        if (!pos) {
          continue;
        }
        const loadType =
          typeof row.loadType === 'string' && row.loadType.trim()
            ? row.loadType.trim().toUpperCase()
            : null;
        const loadId =
          typeof row.loadId === 'string' && row.loadId.trim() ? row.loadId.trim() : null;
        byPos.set(pos, { loadType, loadId });
      }
    }

    // Ensure active slot is visible even if shelf snapshot omitted it
    if (activePosition && !byPos.has(activePosition) && event.workpieceType) {
      byPos.set(activePosition, {
        loadType: String(event.workpieceType).toUpperCase(),
        loadId: event.workpieceId || null,
      });
    }

    const cells = order.map((loadPosition) => {
      const cell = byPos.get(loadPosition);
      const loadType = cell?.loadType ?? null;
      const empty = !(loadType === 'BLUE' || loadType === 'WHITE' || loadType === 'RED');
      // On DROP, active slot is the vacated one — show color highlight even if shelf emptied
      const active = activePosition === loadPosition;
      const showType =
        !empty
          ? loadType
          : active && event.workpieceType
            ? String(event.workpieceType).toUpperCase()
            : null;
      return {
        loadPosition,
        loadType: showType,
        empty: !showType,
        active,
        icon: showType
          ? this.getWorkpieceIcon(showType)
          : ICONS.shopfloor.workpieces.slotEmpty,
      };
    });

    return { cells, activePosition };
  }

  /** Filled AGV bucket slots persisted on FTS transport events. */
  getAgvLoadsFromEvent(
    event: TrackTraceEvent
  ): Array<{ loadId?: string; loadType?: string; loadPosition?: string }> {
    const raw = event.details?.['agvLoads'];
    if (!Array.isArray(raw)) {
      return [];
    }
    return raw
      .filter(
        (item): item is { loadId?: string; loadType?: string; loadPosition?: string } =>
          !!item && typeof item === 'object'
      )
      .filter((item) => !!item.loadType || !!item.loadId)
      .sort((a, b) => String(a.loadPosition ?? '').localeCompare(String(b.loadPosition ?? '')));
  }

  /** Icon for single-slot FTS events (legacy helpers / tests). */
  getBucketPositionIcon(event: TrackTraceEvent): string | null {
    const rows = this.getTransportLoadRows(event).filter((r) => !r.empty);
    return rows.length === 1 ? rows[0].icon : null;
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

  /** AIQS camera frame attached to CHECK_QUALITY (PASSED and FAILED). */
  getQualityImageUrl(event: TrackTraceEvent): string | null {
    if ((event.eventType || '').toUpperCase() !== 'CHECK_QUALITY') {
      return null;
    }
    const raw = event.details?.['qualityImage'];
    return typeof raw === 'string' && raw.startsWith('data:image/') ? raw : null;
  }

  getQualityClassificationLabel(event: TrackTraceEvent): string | null {
    if ((event.eventType || '').toUpperCase() !== 'CHECK_QUALITY') {
      return null;
    }
    const classification = event.details?.['qualityClassification'];
    const desc = event.details?.['qualityClassificationDesc'];
    const parts: string[] = [];
    if (typeof classification === 'string' && classification.trim()) {
      parts.push(classification.trim());
    }
    if (typeof desc === 'string' && desc.trim()) {
      parts.push(desc.trim());
    }
    return parts.length > 0 ? parts.join(' — ') : null;
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

  /**
   * SOLL checklist: planned stations with visited flag from module (or flow-anchor) events.
   */
  getPlannedStationChecklist(
    events: TrackTraceEvent[] | undefined,
    order: OrderContext | null | undefined
  ): Array<{ station: string; visited: boolean }> {
    return this.getOrderFlowAccents(events, order).map((accent) => ({
      station: accent.station,
      visited: accent.active,
    }));
  }

  /** Co-passenger / foreign-station FTS DOCK (not in planned machining workflow). */
  getIstVisitBadge(event: TrackTraceEvent): string | null {
    if (event.eventSource !== 'FTS') {
      return null;
    }
    if ((event.eventType || '').toUpperCase() !== 'DOCK') {
      return null;
    }
    if (event.details?.['visitKind'] !== 'IST_ONLY') {
      return null;
    }
    return $localize`:@@trackTraceIstStopBadge:Ist stop`;
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

  /**
   * Snapshot for UI when event is an env anchor; otherwise null.
   */
  getDisplayedEnvironmentSnapshot(event: TrackTraceEvent): TrackTraceEnvironmentSnapshot | null {
    if (!this.shouldDisplayEnvironmentSnapshot(event)) {
      return null;
    }
    return this.getEventEnvironmentSnapshot(event);
  }

  /**
   * Show env only on timeline anchor events (DOCK / PICK / DROP / CHECK_QUALITY).
   * Hides snapshots on PASS/TURN/PROCESS even if present in older session data.
   */
  shouldDisplayEnvironmentSnapshot(event: TrackTraceEvent): boolean {
    const type = (event.eventType || '').toUpperCase();
    if (!['DOCK', 'PICK', 'DROP', 'CHECK_QUALITY'].includes(type)) {
      return false;
    }
    return this.getEventEnvironmentSnapshot(event) !== null;
  }

  private environmentExpandKey(event: TrackTraceEvent): string {
    return [
      event.timestamp,
      event.eventType,
      event.actionId || '',
      event.location || '',
      event.stationId || '',
    ].join('|');
  }

  isEnvironmentExpanded(event: TrackTraceEvent): boolean {
    return this.expandedEnvironmentKeys.has(this.environmentExpandKey(event));
  }

  toggleEnvironmentExpanded(event: TrackTraceEvent): void {
    const key = this.environmentExpandKey(event);
    if (this.expandedEnvironmentKeys.has(key)) {
      this.expandedEnvironmentKeys.delete(key);
    } else {
      this.expandedEnvironmentKeys.add(key);
    }
    this.cdr.markForCheck();
  }

  getEnvironmentStatusLabel(snapshot: TrackTraceEnvironmentSnapshot): string {
    if (this.isEnvironmentAlarm(snapshot)) {
      return $localize`:@@trackTraceEnvStatusAlarm:ALARM`;
    }
    if (this.isEnvironmentWarn(snapshot)) {
      return $localize`:@@trackTraceEnvStatusWarn:WARN`;
    }
    return $localize`:@@trackTraceEnvStatusOk:OK`;
  }

  isEnvironmentAlarm(snapshot: TrackTraceEnvironmentSnapshot): boolean {
    // Prefer row severity so a stale hasAlarm latch cannot force ALARM on green rows.
    return snapshot.rows.some((row) => row.variant === 'alarm');
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
      const active = this.isPlannedStationVisited(events, orderEvents, orderType, station);
      return {
        station,
        index: idx + 1,
        total: plannedChain.length,
        active,
      };
    });
  }

  /**
   * Planned-station checklist: MQTT-treu.
   * 1) Classic flow anchors on this orderId (MODULE HBW DROP / DRILL / … / DPS PICK).
   * 2) PRODUCTION mfg only: any FTS DOCK at that station on this workpiece (incl. Mitfahrt).
   *    Physical stop is a real event; does not invent MODULE process / quality.
   */
  private isPlannedStationVisited(
    allEvents: TrackTraceEvent[],
    orderEvents: TrackTraceEvent[],
    orderType: string,
    station: string
  ): boolean {
    const byAnchor = orderEvents.some(
      (event) =>
        this.isFlowAnchorEvent(orderType, station, (event.eventType || '').toUpperCase()) &&
        (event.stationId || '').toUpperCase() === station
    );
    if (byAnchor) {
      return true;
    }

    if (orderType === 'PRODUCTION' && ['DRILL', 'MILL', 'AIQS'].includes(station)) {
      return allEvents.some(
        (event) =>
          event.eventSource === 'FTS' &&
          (event.eventType || '').toUpperCase() === 'DOCK' &&
          (event.stationId || '').toUpperCase() === station
      );
    }

    return false;
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
   * Chronological shopfloor rows: station visits + collapsible transport groups
   * between planned stations. Expanded transport groups flatten to event rows.
   */
  buildShopfloorTimeline(
    events: TrackTraceEvent[],
    order: OrderContext | null
  ): TrackTraceTimelineItem[] {
    const sorted = [...events].sort((a, b) => {
      const timeDiff = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
      if (timeDiff !== 0) {
        return timeDiff;
      }
      return (a.actionId || '').localeCompare(b.actionId || '');
    });

    const planned = new Set((order?.plannedStationChain ?? []).map((s) => s.toUpperCase()));
    const items: TrackTraceTimelineItem[] = [];
    let lastStationVisitId: string | null = null;
    let lastPlannedStation: string | null = null;
    let transportBuffer: TrackTraceEvent[] = [];
    let transportGroupSeq = 0;

    const flushTransport = (toStation: string | null): void => {
      if (transportBuffer.length === 0) {
        return;
      }
      transportGroupSeq += 1;
      const groupId = `tg-${transportGroupSeq}-${transportBuffer[0]?.timestamp ?? transportGroupSeq}`;
      const group: TrackTraceTimelineItem = {
        kind: 'transport-group',
        id: groupId,
        fromStation: lastPlannedStation,
        toStation,
        events: [...transportBuffer],
        istStations: this.extractIstStationsFromTransport(transportBuffer, planned),
        agvLabel: this.resolveAgvLabelFromEvents(transportBuffer),
      };
      items.push(group);
      if (this.isTransportGroupExpanded(groupId)) {
        for (const ev of group.events) {
          items.push({
            kind: 'event',
            event: ev,
            column: 'transport',
            showBusinessChip: false,
            istStationChip: this.resolveIstStationChip(ev, planned),
          });
        }
      }
      transportBuffer = [];
    };

    for (const event of sorted) {
      if (!this.isOrderScopedEvent(event)) {
        continue;
      }
      const column = this.classifyShopfloorColumn(event);

      if (column === 'station') {
        const sid = (event.stationId || event.moduleName || '').toUpperCase();
        const isNewVisit = !!sid && sid !== lastStationVisitId;
        if (isNewVisit) {
          flushTransport(sid || null);
          items.push({
            kind: 'station-header',
            stationId: sid,
            stationName: event.stationName || sid,
            serialNumber: this.resolveStationSerial(event),
          });
          lastStationVisitId = sid;
          if (sid && (planned.size === 0 || planned.has(sid))) {
            lastPlannedStation = sid;
          }
        }
        items.push({
          kind: 'event',
          event,
          column: 'station',
          showBusinessChip: isNewVisit && this.getBusinessFlowAccent(event, order) !== null,
          istStationChip: null,
        });
      } else {
        lastStationVisitId = null;
        transportBuffer.push(event);
      }
    }
    flushTransport(null);

    return items;
  }

  isTransportGroupExpanded(groupId: string): boolean {
    return this.expandedTransportGroupIds.has(groupId);
  }

  toggleTransportGroup(groupId: string): void {
    if (this.expandedTransportGroupIds.has(groupId)) {
      this.expandedTransportGroupIds.delete(groupId);
    } else {
      this.expandedTransportGroupIds.add(groupId);
    }
    this.cdr.markForCheck();
  }

  getTransportGroupSummaryLabel(item: Extract<TrackTraceTimelineItem, { kind: 'transport-group' }>): string {
    const n = item.events.length;
    const route =
      item.fromStation && item.toStation
        ? `${item.fromStation}→${item.toStation}`
        : item.fromStation
          ? `${item.fromStation}→…`
          : item.toStation
            ? `…→${item.toStation}`
            : '';
    const agv = item.agvLabel || 'AGV';
    if (route) {
      return $localize`:@@trackTraceTransportGroupSummary:${agv}:agv: · ${n}:count: · ${route}:route:`;
    }
    return $localize`:@@trackTraceTransportGroupSummaryNoRoute:${agv}:agv: · ${n}:count: events`;
  }

  /** Prefer alarm/warn snapshot among grouped transport events for collapsed env cell. */
  getTransportGroupEnvironmentSummary(
    item: Extract<TrackTraceTimelineItem, { kind: 'transport-group' }>
  ): TrackTraceEnvironmentSnapshot | null {
    let best: TrackTraceEnvironmentSnapshot | null = null;
    let bestRank = -1;
    for (const event of item.events) {
      const snap = this.getDisplayedEnvironmentSnapshot(event);
      if (!snap) {
        continue;
      }
      const rank = this.isEnvironmentAlarm(snap) ? 2 : this.isEnvironmentWarn(snap) ? 1 : 0;
      if (rank > bestRank) {
        best = snap;
        bestRank = rank;
      }
    }
    return best;
  }

  private extractIstStationsFromTransport(
    events: TrackTraceEvent[],
    planned: Set<string>
  ): string[] {
    const found: string[] = [];
    for (const event of events) {
      const station = this.resolveIstStationChip(event, planned);
      if (station && !found.includes(station)) {
        found.push(station);
      }
    }
    return found;
  }

  /** Unplanned / Ist DOCK station for dashed business-flow chip; else null. */
  resolveIstStationChip(event: TrackTraceEvent, planned?: Set<string>): string | null {
    if ((event.eventType || '').toUpperCase() !== 'DOCK') {
      return null;
    }
    const station = (event.stationId || '').toUpperCase();
    if (!station) {
      return null;
    }
    if (event.details?.['visitKind'] === 'IST_ONLY' || event.details?.['coPassenger'] === true) {
      return station;
    }
    const plannedSet =
      planned ??
      new Set<string>();
    if (plannedSet.size > 0 && !plannedSet.has(station)) {
      return station;
    }
    return null;
  }

  private resolveAgvLabelFromEvents(events: TrackTraceEvent[]): string {
    for (const event of events) {
      const actor = this.getEventPrimaryActor(event);
      if (actor && /AGV/i.test(actor)) {
        return actor;
      }
    }
    return 'AGV';
  }

  trackByTimelineItem(index: number, item: TrackTraceTimelineItem): string {
    if (item.kind === 'station-header') {
      return `hdr-${item.stationId}-${index}`;
    }
    if (item.kind === 'transport-group') {
      return item.id;
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
      case 'CHRG':
        return ICONS.shopfloor.stations.chrg;
      default:
        return ICONS.shopfloor.systems.factory;
    }
  }

  /** Location row icon: station SVG when known, else generic marker. */
  getLocationRowIcon(event: TrackTraceEvent): string {
    const station = (event.stationId || '').toUpperCase();
    const known = new Set(['HBW', 'DRILL', 'MILL', 'AIQS', 'DPS', 'CHRG']);
    if (known.has(station)) {
      return this.getStationIcon(station);
    }
    const loc = (event.location || '').toUpperCase();
    if (loc === 'CHRG0' || loc === 'CHRG') {
      return ICONS.shopfloor.stations.chrg;
    }
    return 'assets/svg/shopfloor/shared/location-marker.svg';
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

  /** Compact location for NFC tiles — module name only, no serial (saves space). */
  getTileLocationLabel(location: string): string {
    if (!location?.trim()) {
      return '';
    }
    const info = this.moduleNameService.getLocationDisplayText(location);
    if (info.moduleType && info.fullName) {
      return `${info.moduleType} (${info.fullName})`;
    }
    return info.moduleType || info.fullName || location;
  }

  getLocationInfo(location: string): { moduleType: string; fullName: string; serialNumber: string | null } {
    return this.moduleNameService.getLocationDisplayText(location);
  }

  /** Compact FTS position line for the Position section (no serial — shown on station headers only). */
  getFtsPositionLine(event: TrackTraceEvent): string | null {
    if (event.eventSource !== 'FTS' || !event.location) {
      return null;
    }
    const info = this.getLocationInfo(event.location);
    if (info.moduleType && info.fullName) {
      return `${info.moduleType} (${info.fullName})`;
    }
    return info.moduleType || info.fullName || event.location;
  }

  /** Module serial for station group header (from event location / moduleId). */
  resolveStationSerial(event: TrackTraceEvent): string | null {
    const candidates = [event.location, event.moduleId].filter(
      (v): v is string => typeof v === 'string' && !!v.trim()
    );
    for (const candidate of candidates) {
      const info = this.getLocationInfo(candidate);
      if (info.serialNumber) {
        return info.serialNumber;
      }
      // Bare module serial in location field
      if (/^[A-Z0-9]{6,}$/i.test(candidate.trim()) && !/^(intersection:)?\d+$/i.test(candidate)) {
        return candidate.trim();
      }
    }
    return null;
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

