import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import type { FtsState, OrderActive, InventoryOverviewState, InventorySlotState, StockSnapshot } from '@omf3/entities';
import { getDashboardController, type DashboardStreamSet } from '../mock-dashboard';
import { OrdersViewComponent } from '../orders-view.component';
import { FtsViewComponent } from '../fts-view.component';
import type { OrderFixtureName } from '@omf3/testing-fixtures';
import type { Observable } from 'rxjs';
import { map, shareReplay, filter, startWith } from 'rxjs/operators';
import { merge } from 'rxjs';
import { EnvironmentService } from '../services/environment.service';
import { MessageMonitorService } from '../services/message-monitor.service';

const INVENTORY_LOCATIONS = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3'];
const WORKPIECE_TYPES = ['BLUE', 'WHITE', 'RED'] as const;
const PRODUCT_ICON_MAP: Record<(typeof WORKPIECE_TYPES)[number], string> = {
  BLUE: 'workpieces/blue_product.svg',
  WHITE: 'workpieces/white_product.svg',
  RED: 'workpieces/red_product.svg',
};
const RAW_ICON_MAP: Record<(typeof WORKPIECE_TYPES)[number], string> = {
  BLUE: 'workpieces/blue_instock_unprocessed.svg',
  WHITE: 'workpieces/white_instock_unprocessed.svg',
  RED: 'workpieces/red_instock_unprocessed.svg',
};
const RESERVED_ICON_MAP: Record<(typeof WORKPIECE_TYPES)[number], string> = {
  BLUE: 'workpieces/blue_instock_reserved.svg',
  WHITE: 'workpieces/white_instock_reserved.svg',
  RED: 'workpieces/red_instock_reserved.svg',
};
const THREE_D_ICON_MAP: Record<(typeof WORKPIECE_TYPES)[number], string> = {
  BLUE: 'workpieces/blue_3dim.svg',
  WHITE: 'workpieces/white_3dim.svg',
  RED: 'workpieces/red_3dim.svg',
};
const EMPTY_SLOT_ICON = 'workpieces/slot_empty.svg';
const MAX_CAPACITY = 3;

@Component({
  standalone: true,
  selector: 'app-overview-tab',
  imports: [CommonModule, OrdersViewComponent, FtsViewComponent],
  templateUrl: './overview-tab.component.html',
  styleUrl: './overview-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OverviewTabComponent implements OnInit {
  private dashboard = getDashboardController();

  constructor(
    private readonly environmentService: EnvironmentService,
    private readonly messageMonitor: MessageMonitorService
  ) {
    // Pattern 2: inventoryOverview$ comes from gateway.stockSnapshots$ which has NO startWith
    // Therefore we need MessageMonitorService to get the last value immediately
    const lastInventory = this.messageMonitor.getLastMessage<StockSnapshot>('ccu/state/stock').pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => this.buildInventoryOverviewFromSnapshot(msg!.payload)),
      startWith({ slots: {}, availableCounts: {}, reservedCounts: {}, lastUpdated: new Date().toISOString() } as InventoryOverviewState)
    );
    // Merge MessageMonitor last value with dashboard stream
    // MessageMonitor stream comes first to ensure it takes priority when messages are available
    this.inventoryOverview$ = merge(lastInventory, this.dashboard.streams.inventoryOverview$).pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
    this.availableCounts$ = this.inventoryOverview$.pipe(map((state) => state.availableCounts));
    this.reservedCounts$ = this.inventoryOverview$.pipe(map((state) => state.reservedCounts));
    this.inventorySlots$ = this.inventoryOverview$.pipe(
      map((state) => INVENTORY_LOCATIONS.map((location) => state.slots[location] ?? { location, workpiece: null }))
    );

    // Other streams that have startWith in business layer should work fine
    this.orders$ = this.dashboard.streams.orders$.pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
    this.orderCounts$ = this.dashboard.streams.orderCounts$.pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
    this.ftsStates$ = this.dashboard.streams.ftsStates$.pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  readonly fixtureOptions: OrderFixtureName[] = ['startup', 'white', 'white_step3', 'blue', 'red', 'mixed', 'storage'];
  activeFixture: OrderFixtureName = this.dashboard.getCurrentFixture();

  readonly fixtureLabels: Record<OrderFixtureName, string> = {
    startup: $localize`:@@fixtureLabelStartup:Startup`,
    white: $localize`:@@fixtureLabelWhite:White`,
    white_step3: $localize`:@@fixtureLabelWhiteStep3:White • Step 3`,
    blue: $localize`:@@fixtureLabelBlue:Blue`,
    red: $localize`:@@fixtureLabelRed:Red`,
    mixed: $localize`:@@fixtureLabelMixed:Mixed`,
    storage: $localize`:@@fixtureLabelStorage:Storage`,
  };

  orders$: Observable<OrderActive[]>;
  orderCounts$: Observable<Record<'running' | 'queued' | 'completed', number>>;
  ftsStates$: Observable<Record<string, FtsState>>;
  inventoryOverview$: Observable<InventoryOverviewState>;
  availableCounts$: Observable<Record<string, number>>;
  reservedCounts$: Observable<Record<string, number>>;
  inventorySlots$: Observable<InventorySlotState[]>;

  productIcons = PRODUCT_ICON_MAP;
  rawIcons = RAW_ICON_MAP;
  reservedIcons = RESERVED_ICON_MAP;
  threeDIcons = THREE_D_ICON_MAP;
  emptySlotIcon = EMPTY_SLOT_ICON;
  workpieceTypes = WORKPIECE_TYPES;
  maxCapacity = MAX_CAPACITY;

  readonly yesLabel = $localize`:@@commonYes:Yes`;
  readonly noLabel = $localize`:@@commonNo:No`;
  readonly orderButtonLabel = $localize`:@@overviewOrderButton:Order`;
  readonly orderRawMaterialLabel = $localize`:@@overviewOrderRawMaterial:Order Raw Material`;
  readonly erpRequiredLabel = $localize`:@@overviewErpRequired:ERP integration required`;
  readonly emptySlotLabel = $localize`:@@overviewInventoryEmpty:Empty`;

  readonly customerOrdersIcon = 'headings/lieferung-bestellen.svg';
  readonly inventoryIcon = 'headings/warehouse.svg';
  readonly purchaseOrdersIcon = 'headings/box.svg';

  ngOnInit(): void {
    // Only load fixture in mock mode; in live/replay mode, streams are already initialized in constructor
    if (this.isMockMode) {
      void this.loadFixture(this.activeFixture);
    }
  }

  async loadFixture(fixture: OrderFixtureName) {
    if (!this.isMockMode) {
      return; // Don't load fixtures in live/replay mode
    }
    this.activeFixture = fixture;
    try {
      const streams: DashboardStreamSet = await this.dashboard.loadFixture(fixture);
      this.orders$ = streams.orders$;
      this.orderCounts$ = streams.orderCounts$;
      this.ftsStates$ = streams.ftsStates$;
      this.inventoryOverview$ = streams.inventoryOverview$;
      this.availableCounts$ = this.inventoryOverview$.pipe(map((state) => state.availableCounts));
      this.reservedCounts$ = this.inventoryOverview$.pipe(map((state) => state.reservedCounts));
      this.inventorySlots$ = this.inventoryOverview$.pipe(
        map((state) => INVENTORY_LOCATIONS.map((location) => state.slots[location] ?? { location, workpiece: null }))
      );
    } catch (error) {
      console.warn('Failed to load fixture', fixture, error);
    }
  }

  async orderWorkpiece(type: (typeof WORKPIECE_TYPES)[number]) {
    try {
      await this.dashboard.commands.sendCustomerOrder(type);
    } catch (error) {
      console.warn('Failed to send customer order', type, error);
    }
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
      return `${slot.location}: ${this.emptySlotLabel}`;
    }

    const type = this.normalizeType(workpiece.type);
    const label = type ? this.getWorkpieceLabel(type) : workpiece.type;
    const id = workpiece.id && workpiece.id !== '' ? workpiece.id : '—';
    const state = workpiece.state ?? 'RAW';
    return `${slot.location}: ${label} · ${state} · ID ${id}`;
  }

  getWorkpieceLabel(type: (typeof WORKPIECE_TYPES)[number]): string {
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

  getNeed(counts: Record<string, number>, type: (typeof WORKPIECE_TYPES)[number]): number {
    return Math.max(0, this.maxCapacity - (counts[type] ?? 0));
  }

  isAvailable(availableCounts: Record<string, number>, type: (typeof WORKPIECE_TYPES)[number]): boolean {
    return (availableCounts[type] ?? 0) > 0;
  }

  asArray(length: number): number[] {
    return Array.from({ length }, (_, index) => index);
  }

  private normalizeType(input?: string): (typeof WORKPIECE_TYPES)[number] | null {
    if (!input) {
      return null;
    }
    const normalized = input.toUpperCase();
    return WORKPIECE_TYPES.find((type) => type === normalized) ?? null;
  }

  private buildInventoryOverviewFromSnapshot(snapshot: StockSnapshot | null | undefined): InventoryOverviewState {
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

    if (snapshot && Array.isArray(snapshot.stockItems)) {
      snapshot.stockItems.forEach((item) => {
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
      lastUpdated: snapshot?.ts ?? new Date().toISOString(),
    };
  }
}

