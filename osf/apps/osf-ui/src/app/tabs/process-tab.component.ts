import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import type { OrderActive, ProductionFlowMap, InventoryOverviewState, StockSnapshot } from '@osf/entities';
import { getDashboardController, type DashboardStreamSet } from '../mock-dashboard';
import { MessageMonitorService } from '../services/message-monitor.service';
import { EnvironmentService } from '../services/environment.service';
import { ConnectionService } from '../services/connection.service';
import { InventoryStateService } from '../services/inventory-state.service';
import type { OrderFixtureName } from '@osf/testing-fixtures';
import { SHOPFLOOR_ASSET_MAP } from '@osf/testing-fixtures';
import type { Observable } from 'rxjs';
import { map, shareReplay, filter, startWith, distinctUntilChanged, switchMap } from 'rxjs/operators';
import { merge, Subscription, combineLatest } from 'rxjs';
import { ICONS } from '../shared/icons/icon.registry';
import { ErpInfoBoxComponent, type PurchaseOrderData, type CustomerOrderData, type ErpOrderType } from '../components/erp-info-box/erp-info-box.component';
import { ErpOrderDataService } from '../services/erp-order-data.service';

const INVENTORY_LOCATIONS = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3'];
const WORKPIECE_TYPES = ['BLUE', 'WHITE', 'RED'] as const;
const PRODUCT_ICON_MAP: Record<(typeof WORKPIECE_TYPES)[number], string> = {
  BLUE: ICONS.shopfloor.workpieces.blue.product,
  WHITE: ICONS.shopfloor.workpieces.white.product,
  RED: ICONS.shopfloor.workpieces.red.product,
};
const THREE_D_ICON_MAP: Record<(typeof WORKPIECE_TYPES)[number], string> = {
  BLUE: ICONS.shopfloor.workpieces.blue.dim3,
  WHITE: ICONS.shopfloor.workpieces.white.dim3,
  RED: ICONS.shopfloor.workpieces.red.dim3,
};
const EMPTY_SLOT_ICON = ICONS.shopfloor.workpieces.slotEmpty;
const MAX_CAPACITY = 3;

interface ProcessStepView {
  id: string;
  label: string;
  icon: string;
  isPlaceholder?: boolean;
}

interface ProcessProductView {
  type: string;
  label: string;
  dotClass: string;
  steps: ProcessStepView[];
  stepCount: number;
  productIcon: string;
  product3dIcon: string;
  backgroundClass: string;
}

/**
 * Process Tab Component
 * 
 * Displays business processes (Customer Orders, Purchase Orders) and shopfloor processes
 * (Production Flow, Storage Flow) in a two-column layout.
 * 
 * Left column: Business processes (ERP bridge)
 * - Purchase Orders: Material orders (exact copy from Overview Tab)
 * - Customer Orders: Orders from customers (exact copy from Overview Tab)
 * 
 * Right column: Shopfloor processes (ERP-controlled)
 * - Production Flow: HBW -> Manufacturing Steps (MILL, DRILL, AIQS) -> DPS
 * - Storage Flow: DPS -> HBW
 */
@Component({
  standalone: true,
  selector: 'app-process-tab',
  imports: [CommonModule, ErpInfoBoxComponent],
  templateUrl: './process-tab.component.html',
  styleUrl: './process-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProcessTabComponent implements OnInit, OnDestroy {
  private dashboard = getDashboardController();
  private readonly subscriptions = new Subscription();
  private inventoryStreamSub?: Subscription;
  private currentEnvironmentKey: string;

  readonly fixtureOptions: OrderFixtureName[] = ['startup', 'white', 'white_step3', 'blue', 'red', 'mixed', 'storage'];
  readonly fixtureLabels: Partial<Record<OrderFixtureName, string>> = {
    startup: $localize`:@@fixtureLabelStartup:Startup`,
    white: $localize`:@@fixtureLabelWhite:White`,
    white_step3: $localize`:@@fixtureLabelWhiteStep3:White • Step 3`,
    blue: $localize`:@@fixtureLabelBlue:Blue`,
    red: $localize`:@@fixtureLabelRed:Red`,
    mixed: $localize`:@@fixtureLabelMixed:Mixed`,
    storage: $localize`:@@fixtureLabelStorage:Storage`,
  };
  activeFixture: OrderFixtureName = this.dashboard.getCurrentFixture();

  // Business processes - Inventory data
  inventoryOverview$!: Observable<InventoryOverviewState>;
  availableCounts$!: Observable<Record<string, number>>;

  // Shopfloor processes - Production flows
  flows$!: Observable<ProductionFlowMap>;
  products$!: Observable<ProcessProductView[]>;

  // Icons and labels
  productIcons = PRODUCT_ICON_MAP;
  threeDIcons = THREE_D_ICON_MAP;
  emptySlotIcon = EMPTY_SLOT_ICON;
  workpieceTypes = WORKPIECE_TYPES;
  maxCapacity = MAX_CAPACITY;

  readonly yesLabel = $localize`:@@commonYes:Yes`;
  readonly noLabel = $localize`:@@commonNo:No`;
  readonly orderButtonLabel = $localize`:@@overviewOrderButton:Order`;
  readonly orderRawMaterialLabel = $localize`:@@overviewOrderRawMaterial:Order Raw Material`;
  readonly erpRequiredLabel = $localize`:@@overviewErpRequired:ERP integration required`;

  readonly customerOrdersIcon = 'assets/svg/ui/heading-customer-orders.svg';
  readonly purchaseOrdersIcon = 'assets/svg/ui/heading-purchase-orders.svg';
  readonly processIcon = ICONS.ui.processFlow;

  // Accordion state
  protected readonly expandedSections = new Set<string>(['procurement', 'production']); // Both expanded by default

  // ERP Info Box state - per workpiece type
  erpInfoBoxOpen: Record<string, boolean> = {};
  erpOrderDataByType: Record<string, PurchaseOrderData | CustomerOrderData | null> = {};
  erpOrderWorkpieceType: Record<string, string> = {}; // Store workpieceType for each order

  isSectionExpanded(sectionId: string): boolean {
    return this.expandedSections.has(sectionId);
  }

  toggleSection(sectionId: string): void {
    if (this.expandedSections.has(sectionId)) {
      this.expandedSections.delete(sectionId);
    } else {
      this.expandedSections.add(sectionId);
    }
    this.cdr.markForCheck();
  }

  // Production flow icons
  readonly startIcon = this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['HBW'] ?? '/shopfloor/stock.svg');
  // DPS icons for Production Flow: Warehouse, Robotic Arm, Delivery Truck
  readonly productionEndIcons = [
    this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS_SQUARE1'] ?? '/shopfloor/warehouse.svg'), // Warehouse
    this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS'] ?? '/shopfloor/robot-arm.svg'), // Robotic Arm
    this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS_SQUARE2'] ?? '/shopfloor/order-tracking.svg'), // Delivery Truck
  ];
  // DPS icons for Storage Flow: Truck (order-tracking), Robotic Arm, Warehouse
  readonly storageEndIcons = [
    this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS_SQUARE2'] ?? '/shopfloor/order-tracking.svg'), // Truck
    this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS'] ?? '/shopfloor/robot-arm.svg'), // Robotic Arm
    this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS_SQUARE1'] ?? '/shopfloor/warehouse.svg'), // Warehouse
  ];
  readonly stepCountI18nMap: { [k: string]: string } = {
    '=0': $localize`:@@processNoSteps:No processing steps`,
    '=1': $localize`:@@processOneStep:1 Processing Step`,
    other: $localize`:@@processManySteps:# Processing Steps`,
  };

  private readonly workpieceOrder = ['BLUE', 'WHITE', 'RED'] as const;

  private readonly workpieceMeta = {
    BLUE: {
      label: $localize`:@@processWorkpieceBlue:Blue`,
      dotClass: 'blue',
      productIcon: ICONS.shopfloor.workpieces.blue.product,
      product3dIcon: ICONS.shopfloor.workpieces.blue.dim3,
      backgroundClass: 'bg-blue',
    },
    WHITE: {
      label: $localize`:@@processWorkpieceWhite:White`,
      dotClass: 'white',
      productIcon: ICONS.shopfloor.workpieces.white.product,
      product3dIcon: ICONS.shopfloor.workpieces.white.dim3,
      backgroundClass: 'bg-white',
    },
    RED: {
      label: $localize`:@@processWorkpieceRed:Red`,
      dotClass: 'red',
      productIcon: ICONS.shopfloor.workpieces.red.product,
      product3dIcon: ICONS.shopfloor.workpieces.red.dim3,
      backgroundClass: 'bg-red',
    },
  } as const;

  private readonly moduleMeta: Record<string, { label: string; icon: string }> = {
    HBW: { label: $localize`:@@processModuleHBW:High-bay warehouse`, icon: this.startIcon },
    DRILL: { label: $localize`:@@processModuleDrill:Drill`, icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DRILL']) },
    MILL: { label: $localize`:@@processModuleMill:Mill`, icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['MILL']) },
    AIQS: {
      label: $localize`:@@processModuleAiQs:AI Quality Station`,
      icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['AIQS']),
    },
    DPS: { label: $localize`:@@processModuleDps:Goods outgoing`, icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS']) },
  };

  constructor(
    private readonly environmentService: EnvironmentService,
    private readonly messageMonitor: MessageMonitorService,
    private readonly connectionService: ConnectionService,
    private readonly inventoryState: InventoryStateService,
    private readonly cdr: ChangeDetectorRef,
    private readonly erpOrderDataService: ErpOrderDataService
  ) {
    this.currentEnvironmentKey = this.environmentService.current.key;
    this.bindInventoryOutputs();
    this.initializeFlowsStream();
  }

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  ngOnInit(): void {
    this.subscriptions.add(
      this.connectionService.state$
        .pipe(distinctUntilChanged())
        .subscribe((state) => {
          if (state === 'connected') {
            this.bindInventoryOutputs();
            this.setupInventoryStreamSubscription();
            this.initializeFlowsStream();
          }
        })
    );

    this.subscriptions.add(
      this.environmentService.environment$
        .pipe(distinctUntilChanged((prev, next) => prev.key === next.key))
        .subscribe((environment) => {
          this.currentEnvironmentKey = environment.key;
          this.bindInventoryOutputs();
          this.resetInventoryTracking();
          this.setupInventoryStreamSubscription();
          this.initializeFlowsStream();
          if (environment.key === 'mock') {
            void this.loadFixture(this.activeFixture);
          }
        })
    );

    this.setupInventoryStreamSubscription();

    if (this.isMockMode) {
      void this.loadFixture(this.activeFixture);
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
    this.inventoryStreamSub?.unsubscribe();
  }

  async loadFixture(fixture: OrderFixtureName): Promise<void> {
    if (!this.isMockMode) {
      return;
    }
    this.activeFixture = fixture;
    try {
      this.resetInventoryTracking();
      
      const presetMap: Partial<Record<OrderFixtureName, string>> = {
        startup: 'process-startup',
        white: 'order-white',
        white_step3: 'order-white-step3',
        blue: 'order-blue',
        red: 'order-red',
        mixed: 'order-mixed',
        storage: 'order-storage',
      };
      
      const preset = presetMap[fixture] || 'process-startup';
      await this.dashboard.loadTabFixture(preset);
      this.setupInventoryStreamSubscription();
    } catch (error) {
      console.warn('Failed to load process fixture', fixture, error);
    }
  }

  /**
   * Generate Purchase Order Data (consistent with Track-Trace)
   */
  private generatePurchaseOrderData(): PurchaseOrderData {
    const now = new Date();
    const deliveryDate = new Date(now);
    deliveryDate.setDate(deliveryDate.getDate() + 7); // 7 days from now

    // Generate IDs consistent with Track-Trace format
    const random = Math.random().toString(36).substring(2, 8).toUpperCase();
    const supplierRandom = Math.random().toString(36).substring(2, 6).toUpperCase();

    return {
      purchaseOrderId: `ERP-PO-${random}`,
      supplierId: `SUP-${supplierRandom}`,
      orderDate: now.toISOString(),
      orderAmount: 1,
      plannedDeliveryDate: deliveryDate.toISOString(),
    };
  }

  /**
   * Generate Customer Order Data (consistent with Track-Trace)
   */
  private generateCustomerOrderData(): CustomerOrderData {
    const now = new Date();
    const deliveryDate = new Date(now);
    deliveryDate.setDate(deliveryDate.getDate() + 7); // 7 days from now

    // Generate IDs consistent with Track-Trace format
    const random = Math.random().toString(36).substring(2, 8).toUpperCase();
    const customerRandom = Math.random().toString(36).substring(2, 6).toUpperCase();

    return {
      customerOrderId: `ERP-CO-${random}`,
      customerId: `CUST-${customerRandom}`,
      orderDate: now.toISOString(),
      orderAmount: 1,
      plannedDeliveryDate: deliveryDate.toISOString(),
    };
  }

  /**
   * Order raw material (Purchase Order) - Task 12
   */
  async orderRawMaterial(type: (typeof WORKPIECE_TYPES)[number]): Promise<void> {
    try {
      console.info('[process-tab] Ordering raw material:', type);
      const dashboard = getDashboardController();
      await dashboard.commands.requestRawMaterial(type);
      console.info('[process-tab] Raw material order sent successfully:', type);

      // Generate and store Purchase Order data with workpiece type
      const purchaseData = this.generatePurchaseOrderData();
      this.erpOrderDataService.storePurchaseOrder(type, purchaseData);

      // Show ERP Info Box inline for this workpiece type
      // Store data with a key that includes the order type to separate Purchase and Customer orders
      const purchaseKey = `purchase-${type}`;
      this.erpOrderDataByType[purchaseKey] = purchaseData;
      this.erpOrderWorkpieceType[purchaseKey] = type; // Store workpieceType (BLUE/WHITE/RED)
      this.erpInfoBoxOpen[purchaseKey] = true;
      this.cdr.markForCheck();
    } catch (error) {
      console.error('[process-tab] Failed to order raw material', type, error);
    }
  }

  /**
   * Order workpiece (Customer Order) - Task 12
   */
  async orderWorkpiece(type: (typeof WORKPIECE_TYPES)[number]): Promise<void> {
    try {
      console.info('[process-tab] Sending customer order:', type);
      const dashboard = getDashboardController();
      await dashboard.commands.sendCustomerOrder(type);
      console.info('[process-tab] Customer order sent successfully:', type);

      // Generate and store Customer Order data
      const customerData = this.generateCustomerOrderData();
      this.erpOrderDataService.storeCustomerOrder(customerData);

      // Show ERP Info Box inline for this workpiece type
      // Store data with a key that includes the order type to separate Purchase and Customer orders
      const customerKey = `customer-${type}`;
      this.erpOrderDataByType[customerKey] = customerData;
      this.erpOrderWorkpieceType[customerKey] = type; // Store workpieceType (BLUE/WHITE/RED)
      this.erpInfoBoxOpen[customerKey] = true;
      this.cdr.markForCheck();
    } catch (error) {
      console.error('[process-tab] Failed to send customer order', type, error);
    }
  }

  /**
   * Close ERP Info Box for a specific order key
   */
  closeErpInfoBox(key: string): void {
    this.erpInfoBoxOpen[key] = false;
    this.cdr.markForCheck();
  }

  /**
   * Check if ERP Info Box is open for a workpiece type (legacy method, kept for compatibility)
   */
  isErpInfoBoxOpen(type: string): boolean {
    // Check both purchase and customer keys
    return this.erpInfoBoxOpen[`purchase-${type}`] === true || this.erpInfoBoxOpen[`customer-${type}`] === true;
  }

  /**
   * Get ERP Order Data for a workpiece type (legacy method, kept for compatibility)
   */
  getErpOrderData(type: string): PurchaseOrderData | CustomerOrderData | null {
    return this.erpOrderDataByType[`purchase-${type}`] || this.erpOrderDataByType[`customer-${type}`] || null;
  }

  /**
   * Check if any Purchase Order has ERP data
   */
  hasAnyPurchaseOrderErpData(): boolean {
    return this.workpieceTypes.some(type => {
      const key = `purchase-${type}`;
      return this.erpInfoBoxOpen[key] === true && this.erpOrderDataByType[key] !== null;
    });
  }

  /**
   * Get the first Purchase Order ERP data (for display in full-width box)
   */
  getFirstPurchaseOrderErpData(): PurchaseOrderData | null {
    for (const type of this.workpieceTypes) {
      const key = `purchase-${type}`;
      const data = this.erpOrderDataByType[key];
      if (data && this.erpInfoBoxOpen[key] === true) {
        return data as PurchaseOrderData;
      }
    }
    return null;
  }

  /**
   * Get the workpiece type for the first Purchase Order (for display in ERP box)
   */
  getFirstPurchaseOrderWorkpieceType(): string | undefined {
    for (const type of this.workpieceTypes) {
      const key = `purchase-${type}`;
      if (this.erpInfoBoxOpen[key] === true && this.erpOrderDataByType[key] !== null) {
        return this.erpOrderWorkpieceType[key] || type;
      }
    }
    return undefined;
  }

  /**
   * Close all Purchase Order ERP data
   */
  closeAllPurchaseOrderErpData(): void {
    for (const type of this.workpieceTypes) {
      const key = `purchase-${type}`;
      this.erpInfoBoxOpen[key] = false;
    }
    this.cdr.markForCheck();
  }

  /**
   * Check if any Customer Order has ERP data (only if orderWorkpiece was called)
   */
  hasAnyCustomerOrderErpData(): boolean {
    return this.workpieceTypes.some(type => {
      const key = `customer-${type}`;
      return this.erpInfoBoxOpen[key] === true && this.erpOrderDataByType[key] !== null;
    });
  }

  /**
   * Get the first Customer Order ERP data (for display in full-width box)
   */
  getFirstCustomerOrderErpData(): CustomerOrderData | null {
    for (const type of this.workpieceTypes) {
      const key = `customer-${type}`;
      const data = this.erpOrderDataByType[key];
      if (data && this.erpInfoBoxOpen[key] === true) {
        return data as CustomerOrderData;
      }
    }
    return null;
  }

  /**
   * Get the workpiece type for the first Customer Order (for display in ERP box)
   */
  getFirstCustomerOrderWorkpieceType(): string | undefined {
    for (const type of this.workpieceTypes) {
      const key = `customer-${type}`;
      if (this.erpInfoBoxOpen[key] === true && this.erpOrderDataByType[key] !== null) {
        return this.erpOrderWorkpieceType[key] || type;
      }
    }
    return undefined;
  }

  /**
   * Close all Customer Order ERP data
   */
  closeAllCustomerOrderErpData(): void {
    for (const type of this.workpieceTypes) {
      const key = `customer-${type}`;
      this.erpInfoBoxOpen[key] = false;
    }
    this.cdr.markForCheck();
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

  private resolveAssetPath(path?: string): string {
    if (!path) {
      return '';
    }
    return path.startsWith('/') ? path.slice(1) : path;
  }

  private bindInventoryOutputs(): void {
    const inventory$ = this.inventoryState
      .getState$(this.currentEnvironmentKey)
      .pipe(
        map((state) => state ?? this.createEmptyInventoryState()),
        shareReplay({ bufferSize: 1, refCount: true })
      );

    this.inventoryOverview$ = inventory$;
    this.availableCounts$ = inventory$.pipe(map((state) => state.availableCounts));
  }

  private resetInventoryTracking(): void {
    this.inventoryState.clear(this.currentEnvironmentKey);
    this.messageMonitor.clearTopic('ccu/state/stock');
    this.inventoryStreamSub?.unsubscribe();
    this.inventoryStreamSub = undefined;
  }

  private createEmptyInventoryState(): InventoryOverviewState {
    const slots: Record<string, { location: string; workpiece: null }> = {};
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

  private buildInventoryOverviewFromSnapshot(
    snapshot: StockSnapshot | string | null | undefined
  ): InventoryOverviewState {
    let normalizedSnapshot: StockSnapshot | null | undefined = null;
    if (typeof snapshot === 'string') {
      try {
        normalizedSnapshot = JSON.parse(snapshot) as StockSnapshot;
      } catch (error) {
        console.warn('[process-tab] Failed to parse stock snapshot payload', error);
        normalizedSnapshot = null;
      }
    } else {
      normalizedSnapshot = snapshot;
    }

    const slots: Record<string, { location: string; workpiece: { id: string; type: string; state: string } | null }> = {};
    const availableCounts: Record<string, number> = {};
    const reservedCounts: Record<string, number> = {};

    INVENTORY_LOCATIONS.forEach((location) => {
      slots[location] = { location, workpiece: null };
    });

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

  private setupInventoryStreamSubscription(): void {
    const inventorySource$ = this.createInventorySourceStream();
    this.inventoryStreamSub?.unsubscribe();
    this.inventoryStreamSub = inventorySource$.subscribe((state) => {
      this.inventoryState.setState(this.currentEnvironmentKey, state);
    });
  }

  private createInventorySourceStream(): Observable<InventoryOverviewState> {
    const cachedState = this.inventoryState.getSnapshot(this.currentEnvironmentKey);
    const initialState = cachedState ?? this.createEmptyInventoryState();

    const lastInventory = this.messageMonitor.getLastMessage<StockSnapshot>('ccu/state/stock').pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => this.buildInventoryOverviewFromSnapshot(msg!.payload)),
      startWith(initialState)
    );

    return merge(lastInventory, this.dashboard.streams.inventoryOverview$).pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  private initializeFlowsStream(): void {
    // Pattern 2: MessageMonitorService + merge with dashboard.streams.flows$
    const lastFlows = this.messageMonitor.getLastMessage<ProductionFlowMap>('ccu/state/flows').pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => msg!.payload as ProductionFlowMap),
      startWith({} as ProductionFlowMap)
    );

    this.flows$ = merge(lastFlows, this.dashboard.streams.flows$).pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Initialize products$ after flows$ is set
    this.products$ = this.flows$.pipe(map((flows) => this.buildProductViews(flows)));
  }

  private buildProductViews(flows: ProductionFlowMap): ProcessProductView[] {
    if (!flows) {
      return [];
    }
 
    const products: ProcessProductView[] = [];
    const maxSteps = this.workpieceOrder.reduce((acc, type) => {
      const count = flows[type]?.steps?.length ?? 0;
      return count > acc ? count : acc;
    }, 0);

    this.workpieceOrder.forEach((type) => {
      const definition = flows[type];
      if (!definition) {
        return;
      }

      const meta = this.workpieceMeta[type];
      const steps = (definition.steps ?? []).map((step, index) => this.mapStep(step, index));
      const actualCount = steps.length;

      for (let placeholderIndex = steps.length; placeholderIndex < maxSteps; placeholderIndex += 1) {
        steps.push({
          id: `${type}-placeholder-${placeholderIndex}`,
          label: '',
          icon: '',
          isPlaceholder: true,
        });
      }

      products.push({
        type,
        label: meta.label,
        dotClass: meta.dotClass,
        productIcon: meta.productIcon,
        product3dIcon: meta.product3dIcon,
        stepCount: actualCount,
        steps,
        backgroundClass: meta.backgroundClass,
      });
    });

    return products;
  }

  private mapStep(step: string, index: number): ProcessStepView {
    const key = step.toUpperCase();
    const moduleMeta = this.moduleMeta[key] ?? {
      label: step,
      icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS'] ?? 'shopfloor/robotic.svg'),
    };

    return {
      id: `${key}-${index}`,
      label: moduleMeta.label,
      icon: moduleMeta.icon,
      isPlaceholder: false,
    };
  }
}
