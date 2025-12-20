import { ChangeDetectionStrategy, ChangeDetectorRef, Component, inject, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable, Subscription, merge } from 'rxjs';
import { distinctUntilChanged, filter, map, shareReplay, startWith } from 'rxjs/operators';
import type { InventoryOverviewState, InventorySlotState, StockSnapshot } from '@osf/entities';
import { InventoryStateService } from '../../services/inventory-state.service';
import { EnvironmentService } from '../../services/environment.service';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { getDashboardController } from '../../mock-dashboard';
import { ICONS } from '../../shared/icons/icon.registry';

const INVENTORY_LOCATIONS = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3'];
const WORKPIECE_TYPES = ['BLUE', 'WHITE', 'RED'] as const;

const PRODUCT_ICON_MAP: Record<(typeof WORKPIECE_TYPES)[number], string> = {
  BLUE: ICONS.shopfloor.workpieces.blue.product,
  WHITE: ICONS.shopfloor.workpieces.white.product,
  RED: ICONS.shopfloor.workpieces.red.product,
};

const RAW_ICON_MAP: Record<(typeof WORKPIECE_TYPES)[number], string> = {
  BLUE: ICONS.shopfloor.workpieces.blue.instockUnprocessed,
  WHITE: ICONS.shopfloor.workpieces.white.instockUnprocessed,
  RED: ICONS.shopfloor.workpieces.red.instockUnprocessed,
};

const RESERVED_ICON_MAP: Record<(typeof WORKPIECE_TYPES)[number], string> = {
  BLUE: ICONS.shopfloor.workpieces.blue.instockReserved,
  WHITE: ICONS.shopfloor.workpieces.white.instockReserved,
  RED: ICONS.shopfloor.workpieces.red.instockReserved,
};

const EMPTY_SLOT_ICON = ICONS.shopfloor.workpieces.slotEmpty;

/**
 * HBW Stock Grid Component
 * 
 * Displays a compact 3x3 grid showing stock inventory for HBW (High Bay Warehouse).
 * Reusable component that can be used on any page.
 * 
 * Features:
 * - 96x96px icons
 * - State-based styling (Empty/Reserved/Processed)
 * - Responsive grid layout
 * - Tooltip support with WorkpieceID
 * - Replay mode support (loads from MessageMonitor)
 */
@Component({
  standalone: true,
  selector: 'app-hbw-stock-grid',
  imports: [CommonModule],
  templateUrl: './hbw-stock-grid.component.html',
  styleUrl: './hbw-stock-grid.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HbwStockGridComponent implements OnInit, OnDestroy {
  private readonly inventoryState = inject(InventoryStateService);
  private readonly environmentService = inject(EnvironmentService);
  private readonly messageMonitor = inject(MessageMonitorService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly subscriptions = new Subscription();
  private readonly dashboard = getDashboardController();

  inventorySlots$!: Observable<InventorySlotState[]>;
  private currentEnvironmentKey: string;

  readonly productIcons = PRODUCT_ICON_MAP;
  readonly rawIcons = RAW_ICON_MAP;
  readonly reservedIcons = RESERVED_ICON_MAP;
  readonly emptySlotIcon = EMPTY_SLOT_ICON;

  constructor() {
    this.currentEnvironmentKey = this.environmentService.current.key;
  }

  ngOnInit(): void {
    this.bindInventoryOutputs();

    // Update when environment changes
    this.subscriptions.add(
      this.environmentService.environment$
        .pipe(distinctUntilChanged((prev, next) => prev.key === next.key))
        .subscribe((environment) => {
          this.currentEnvironmentKey = environment.key;
          this.bindInventoryOutputs();
          this.cdr.markForCheck();
        })
    );
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  private bindInventoryOutputs(): void {
    // Create inventory source stream that loads from MessageMonitor (for replay) and dashboard streams
    const inventorySource$ = this.createInventorySourceStream();
    
    // Subscribe to inventory source and update InventoryStateService
    this.subscriptions.add(
      inventorySource$.subscribe((state) => {
        this.inventoryState.setState(this.currentEnvironmentKey, state);
      })
    );

    const inventory$ = this.inventoryState
      .getState$(this.currentEnvironmentKey)
      .pipe(
        map((state) => state ?? this.createEmptyInventoryState()),
        shareReplay({ bufferSize: 1, refCount: true })
      );

    this.inventorySlots$ = inventory$.pipe(
      map((state) =>
        INVENTORY_LOCATIONS.map((location) => state.slots[location] ?? { location, workpiece: null })
      )
    );
  }

  private createInventorySourceStream(): Observable<InventoryOverviewState> {
    const cachedState = this.inventoryState.getSnapshot(this.currentEnvironmentKey);
    const initialState = cachedState ?? this.createEmptyInventoryState();

    // Load from MessageMonitor (for replay mode) - this gets persisted messages
    const lastInventory = this.messageMonitor.getLastMessage<StockSnapshot>('ccu/state/stock').pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => this.buildInventoryOverviewFromSnapshot(msg!.payload)),
      startWith(initialState)
    );

    // Merge with dashboard streams (for live/mock mode)
    return merge(lastInventory, this.dashboard.streams.inventoryOverview$).pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  private buildInventoryOverviewFromSnapshot(
    snapshot: StockSnapshot | string | null | undefined
  ): InventoryOverviewState {
    let normalizedSnapshot: StockSnapshot | null | undefined = null;
    if (typeof snapshot === 'string') {
      try {
        normalizedSnapshot = JSON.parse(snapshot) as StockSnapshot;
      } catch (error) {
        console.warn('[hbw-stock-grid] Failed to parse stock snapshot payload', error);
        normalizedSnapshot = null;
      }
    } else {
      normalizedSnapshot = snapshot;
    }

    const slots: Record<string, InventorySlotState> = {};
    const availableCounts: Record<string, number> = {};
    const reservedCounts: Record<string, number> = {};

    // Initialize all inventory locations
    INVENTORY_LOCATIONS.forEach((location) => {
      slots[location] = { location, workpiece: null };
    });

    // Initialize counts for all workpiece types
    WORKPIECE_TYPES.forEach((type) => {
      availableCounts[type] = 0;
      reservedCounts[type] = 0;
    });

    if (normalizedSnapshot && Array.isArray(normalizedSnapshot.stockItems)) {
      normalizedSnapshot.stockItems.forEach((item) => {
        const location = item.location?.toUpperCase();
        if (!location || !slots[location]) {
          return;
        }

        const workpiece = item.workpiece
          ? {
              id: item.workpiece.id ?? '',
              type: item.workpiece.type ?? '',
              state: item.workpiece.state ?? 'RAW',
            }
          : null;

        slots[location] = {
          location,
          workpiece,
        };

        if (workpiece?.type) {
          const workpieceType = workpiece.type.toUpperCase();
          const state = workpiece.state?.toUpperCase();
          if (state === 'RAW') {
            availableCounts[workpieceType] = (availableCounts[workpieceType] ?? 0) + 1;
          } else if (state === 'RESERVED') {
            reservedCounts[workpieceType] = (reservedCounts[workpieceType] ?? 0) + 1;
          }
        }
      });
    }

    return {
      slots,
      availableCounts,
      reservedCounts,
      lastUpdated: normalizedSnapshot?.ts ?? new Date().toISOString(),
    };
  }

  private createEmptyInventoryState(): InventoryOverviewState {
    const slots: Record<string, InventorySlotState> = {};
    INVENTORY_LOCATIONS.forEach((location) => {
      slots[location] = { location, workpiece: null };
    });

    const availableCounts: Record<string, number> = {};
    const reservedCounts: Record<string, number> = {};
    WORKPIECE_TYPES.forEach((type) => {
      availableCounts[type] = 0;
      reservedCounts[type] = 0;
    });

    return {
      slots,
      availableCounts,
      reservedCounts,
      lastUpdated: '',
    };
  }

  getSlotIcon(slot: InventorySlotState): string {
    const workpiece = slot.workpiece;
    if (!workpiece || !workpiece.type) {
      return this.emptySlotIcon;
    }

    const type = this.normalizeType(workpiece.type);
    if (!type) {
      return this.emptySlotIcon;
    }

    const state = workpiece.state?.toUpperCase();
    if (state === 'RESERVED') {
      return this.reservedIcons[type] ?? this.rawIcons[type];
    }

    if (state === 'RAW') {
      return this.rawIcons[type];
    }

    // PROCESSED or other states - use product icon (same as Overview-Tab)
    return this.productIcons[type] ?? this.rawIcons[type];
  }

  getSlotLabel(slot: InventorySlotState): string {
    const workpiece = slot.workpiece;
    if (!workpiece || !workpiece.type) {
      return `${slot.location} [EMPTY]`;
    }
    const type = this.normalizeType(workpiece.type);
    const label = type ? this.getWorkpieceLabel(type) : workpiece.type;
    const state = workpiece.state ? workpiece.state.toUpperCase() : 'RAW';
    return `${slot.location} [${label} – ${state}]`;
  }

  getSlotTooltip(slot: InventorySlotState): string {
    const workpiece = slot.workpiece;
    if (!workpiece || !workpiece.type) {
      return `${slot.location}: ${$localize`:@@overviewInventoryEmpty:Empty`}`;
    }

    const type = this.normalizeType(workpiece.type);
    const label = type ? this.getWorkpieceLabel(type) : workpiece.type;
    const id = workpiece.id && workpiece.id !== '' ? workpiece.id : '—';
    const state = workpiece.state ?? 'RAW';
    return `${slot.location}: ${label} · ${state} · ID ${id}`;
  }

  getSlotClass(slot: InventorySlotState): string {
    const workpiece = slot.workpiece;
    if (!workpiece || !workpiece.type) {
      return 'hbw-stock-grid__slot--empty';
    }

    const state = workpiece.state?.toUpperCase();
    if (state === 'RESERVED') {
      return 'hbw-stock-grid__slot--reserved';
    }

    if (state === 'PROCESSED' || state === 'FINISHED') {
      return 'hbw-stock-grid__slot--processed';
    }

    return '';
  }

  private normalizeType(input?: string): (typeof WORKPIECE_TYPES)[number] | null {
    if (!input) {
      return null;
    }
    const normalized = input.toUpperCase();
    return WORKPIECE_TYPES.find((type) => type === normalized) ?? null;
  }

  private getWorkpieceLabel(type: (typeof WORKPIECE_TYPES)[number]): string {
    switch (type) {
      case 'BLUE':
        return $localize`:@@overviewBlueProduct:Product Blue`;
      case 'WHITE':
        return $localize`:@@overviewWhiteProduct:Product White`;
      case 'RED':
        return $localize`:@@overviewRedProduct:Product Red`;
      default:
        return type;
    }
  }
}
