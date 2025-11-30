import { AsyncPipe, NgFor, NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnDestroy, OnInit, ChangeDetectorRef } from '@angular/core';
import type {
  ModuleOverviewState,
  ModuleAvailabilityStatus,
  ModuleOverviewStatus,
  TransportOverviewStatus,
  FtsState,
} from '@omf3/entities';
import { SHOPFLOOR_ASSET_MAP, type OrderFixtureName } from '@omf3/testing-fixtures';
import { getDashboardController } from '../mock-dashboard';
import type { Observable } from 'rxjs';
import { distinctUntilChanged, map, shareReplay } from 'rxjs/operators';
import { Subscription } from 'rxjs';
import { EnvironmentService } from '../services/environment.service';
import { ModuleNameService } from '../services/module-name.service';
import { ConnectionService } from '../services/connection.service';
import { ModuleOverviewStateService } from '../services/module-overview-state.service';
import { ShopfloorPreviewComponent } from '../components/shopfloor-preview/shopfloor-preview.component';
import { MessageMonitorService } from '../services/message-monitor.service';
import { ModuleDetailsSidebarComponent } from '../components/module-details-sidebar/module-details-sidebar.component';
import { HttpClient } from '@angular/common/http';
import type { ShopfloorLayoutConfig, ShopfloorCellConfig } from '../components/shopfloor-preview/shopfloor-layout.types';

interface ModuleCommand {
  label: string;
  secondary?: boolean;
  handler: () => Promise<void> | void;
}

type ModuleRow = {
  id: string;
  kind: 'module' | 'transport';
  name: string;
  iconPath: string | null;
  registryActive: boolean;
  connected: boolean;
  availabilityLabel: string;
  availabilityClass: string;
  availabilityIcon: string;
  registryIcon: string;
  connectedIcon: string;
  messageCount: number;
  lastUpdate: string;
  actions: ModuleCommand[];
  charging?: boolean;
  lastModuleSerialNumber?: string;
  lastNodeId?: string;
};

type ModuleRegistryEntry = {
  id: string;
  type: keyof typeof MODULE_NAME_MAP;
  kind: 'module' | 'transport';
};

const MODULE_REGISTRY: ModuleRegistryEntry[] = [
  { id: 'SVR3QA0022', type: 'HBW', kind: 'module' },
  { id: 'SVR4H76449', type: 'DRILL', kind: 'module' },
  { id: 'SVR3QA2098', type: 'MILL', kind: 'module' },
  { id: 'SVR4H76530', type: 'AIQS', kind: 'module' },
  { id: 'SVR4H73275', type: 'DPS', kind: 'module' },
  { id: 'CHRG0', type: 'CHRG', kind: 'module' },
  { id: '5iO4', type: 'FTS', kind: 'transport' },
];

const MODULE_REGISTRY_ORDER = MODULE_REGISTRY.map((entry) => entry.id);
const MODULE_REGISTRY_LOOKUP = new Map<string, ModuleRegistryEntry>(
  MODULE_REGISTRY.map((entry) => [entry.id, entry])
);

const MODULE_NAME_MAP: Record<string, string> = {
  HBW: 'HBW',
  DRILL: 'DRILL',
  MILL: 'MILL',
  AIQS: 'AIQS',
  DPS: 'DPS',
  CHRG: 'CHRG',
  FTS: 'FTS',
};

const DEFAULT_SHOPFLOOR_ICON = SHOPFLOOR_ASSET_MAP['QUESTION'] ?? '/shopfloor/question.svg';

const STATUS_ICONS = {
  registry: {
    active: '✅',
    inactive: '❌',
  },
  connection: {
    connected: '📶',
    disconnected: '🚫',
  },
  availability: {
    ready: '🟢',
    busy: '🟠',
    blocked: '🔴',
    unknown: '⚫',
  },
};

@Component({
  standalone: true,
  selector: 'app-module-tab',
  imports: [NgIf, NgFor, AsyncPipe, ShopfloorPreviewComponent, ModuleDetailsSidebarComponent],
  templateUrl: './module-tab.component.html',
  styleUrls: ['./module-tab.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ModuleTabComponent implements OnInit, OnDestroy {
  private dashboard = getDashboardController();
  private readonly subscriptions = new Subscription();
  private fixtureSubscriptions = new Subscription();
  private moduleOverviewSub?: Subscription;
  private currentEnvironmentKey: string;

  // Shopfloor preview state
  shopfloorPreviewExpanded = false;
  private readonly shopfloorPreviewStorageKey = 'module-tab-shopfloor-preview-expanded';

  constructor(
    private readonly environmentService: EnvironmentService,
    private readonly moduleNameService: ModuleNameService,
    private readonly connectionService: ConnectionService,
    private readonly moduleOverviewState: ModuleOverviewStateService,
    private readonly messageMonitor: MessageMonitorService,
    private readonly cdr: ChangeDetectorRef,
    private readonly http: HttpClient
  ) {
    this.currentEnvironmentKey = this.environmentService.current.key;
    this.loadShopfloorPreviewState();
    this.bindCacheOutputs();
    this.initializeStreams();
  }

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  readonly fixtureOptions: (OrderFixtureName | 'shopfloor-status')[] = ['startup', 'white', 'white_step3', 'blue', 'red', 'mixed', 'storage', 'shopfloor-status'];
  readonly fixtureLabels: Record<OrderFixtureName | 'shopfloor-status', string> = {
    startup: $localize`:@@fixtureLabelStartup:Startup`,
    white: $localize`:@@fixtureLabelWhite:White`,
    white_step3: $localize`:@@fixtureLabelWhiteStep3:White • Step 3`,
    blue: $localize`:@@fixtureLabelBlue:Blue`,
    red: $localize`:@@fixtureLabelRed:Red`,
    mixed: $localize`:@@fixtureLabelMixed:Mixed`,
    storage: $localize`:@@fixtureLabelStorage:Storage`,
    'shopfloor-status': $localize`:@@fixtureLabelShopfloorStatus:Shopfloor Status`,
  };

  activeFixture: OrderFixtureName | 'shopfloor-status' = 'startup';
  moduleOverview$!: Observable<ModuleOverviewState>;
  rows$!: Observable<ModuleRow[]>;
  moduleStatusMap$!: Observable<Map<string, { connected: boolean; availability: ModuleAvailabilityStatus }>>;
  
  // Expose moduleStatusMap as a property for template access
  currentModuleStatusMap: Map<string, { connected: boolean; availability: ModuleAvailabilityStatus }> | null = null;
  
  // FTS position for shopfloor preview
  ftsPosition: { x: number; y: number } | null = null;

  // Module details sidebar state
  sidebarOpen = false;
  selectedModuleSerialId: string | null = null;
  selectedModuleName: string | null = null;

  // Shopfloor layout config for serial number lookup
  private layoutConfig: ShopfloorLayoutConfig | null = null;

  readonly headingIcon = 'headings/mehrere.svg';

  // I18n labels for shopfloor preview
  readonly shopfloorPreviewExpandLabel = $localize`:@@moduleTabShopfloorPreviewExpand:Expand shopfloor preview`;
  readonly shopfloorPreviewCollapseLabel = $localize`:@@moduleTabShopfloorPreviewCollapse:Collapse shopfloor preview`;

  ngOnInit(): void {
    // Load shopfloor layout config for serial number lookup
    this.http.get<ShopfloorLayoutConfig>('shopfloor/shopfloor_layout.json').subscribe({
      next: (config) => {
        this.layoutConfig = config;
      },
      error: (error) => {
        console.warn('Failed to load shopfloor layout config:', error);
      }
    });

    this.subscriptions.add(
      this.connectionService.state$
        .pipe(distinctUntilChanged())
        .subscribe((state) => {
          if (state === 'connected') {
            this.initializeStreams();
          }
        })
    );

    this.subscriptions.add(
      this.environmentService.environment$
        .pipe(distinctUntilChanged((prev, next) => prev.key === next.key))
        .subscribe((environment) => {
          this.currentEnvironmentKey = environment.key;
          this.moduleOverviewState.clear(this.currentEnvironmentKey);
          this.bindCacheOutputs();
          this.initializeStreams();
          if (environment.key === 'mock' && this.activeFixture !== 'shopfloor-status') {
            // Don't auto-load shopfloor-status fixture - user must click it explicitly
            void this.loadFixture(this.activeFixture);
          }
        })
    );

    // Only load fixture in mock mode; in live/replay mode, streams are already connected
    // Don't auto-load shopfloor-status fixture - user must click it explicitly
    if (this.isMockMode && this.activeFixture !== 'shopfloor-status') {
      void this.loadFixture(this.activeFixture);
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
    this.fixtureSubscriptions.unsubscribe();
    this.moduleOverviewSub?.unsubscribe();
  }

  trackById(_: number, row: ModuleRow): string {
    return row.id;
  }

  async onCommand(action: ModuleCommand): Promise<void> {
    try {
      await action.handler?.();
    } catch (error) {
      console.error('Failed to execute command', action.label, error);
    }
  }

  async loadFixture(fixture: OrderFixtureName | 'shopfloor-status'): Promise<void> {
    if (!this.isMockMode) {
      return; // Don't load fixtures in live/replay mode
    }
    this.activeFixture = fixture;
    try {
      // Special handling for shopfloor-status fixture
      if (fixture === 'shopfloor-status') {
        // Load only shopfloor status fixtures (ccu/pairing/state + fts position)
        // DON'T load any other fixtures - this is a standalone fixture
        // First clear state
        this.moduleOverviewState.clear(this.currentEnvironmentKey);
        
        // Load the fixtures (this will inject messages into the stream)
        await this.loadModuleStatusFixture();
        
        // Wait a bit for messages to be processed
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Force change detection
        this.cdr.markForCheck();
      } else {
        // Map OrderFixtureName to tab-specific preset
        const presetMap: Record<OrderFixtureName, string> = {
          startup: 'module-status-test',
          white: 'module-status-test',
          white_step3: 'module-status-test',
          blue: 'module-status-test',
          red: 'module-status-test',
          mixed: 'module-status-test',
          storage: 'module-status-test',
        };
        
        const preset = presetMap[fixture] || 'module-status-test';
        await this.dashboard.loadTabFixture(preset);
        
        // If white_step3, also load the order fixture
        if (fixture === 'white_step3') {
          await this.dashboard.loadTabFixture('order-white-step3');
        }
        
        // Re-bind module overview stream after loading fixture (like other tabs do)
        const streams = this.dashboard.streams;
        this.moduleOverview$ = streams.moduleOverview$.pipe(
          shareReplay({ bufferSize: 1, refCount: false })
        );
        this.bindModuleOverviewStream(this.moduleOverview$);
        this.bindCacheOutputs();
        
        // Also load module status fixtures (for testing availability and FTS position)
        await this.loadModuleStatusFixture();
      }
    } catch (error) {
      console.warn('Failed to load module fixture', fixture, error);
    }
  }

  async loadModuleStatusFixture(): Promise<void> {
    if (!this.isMockMode) {
      return;
    }
    try {
      // Unsubscribe from previous fixture subscriptions to avoid duplicates
      // This is important when reloading the fixture
      this.fixtureSubscriptions.unsubscribe();
      this.fixtureSubscriptions = new Subscription();
      
      // Load shopfloor status fixture (ccu/pairing/state) for ModuleOverviewState
      const { createModuleShopfloorStatusFixtureStream } = await import('@omf3/testing-fixtures');
      const shopfloorStream$ = createModuleShopfloorStatusFixtureStream({ intervalMs: 0 });
      
      // Also load module status fixture (module/v1/ff/...) for FTS position
      const { createModuleStatusFixtureStream } = await import('@omf3/testing-fixtures');
      const moduleStream$ = createModuleStatusFixtureStream({ intervalMs: 0 });
      
      // Subscribe to both streams and inject messages into the dashboard's message stream
      const shopfloorSub = shopfloorStream$.subscribe((message) => {
        if (this.dashboard.injectMessage) {
          this.dashboard.injectMessage(message);
        }
        try {
          const payload = typeof message.payload === 'string' 
            ? JSON.parse(message.payload) 
            : message.payload;
          this.messageMonitor.addMessage(message.topic, payload, message.timestamp);
        } catch (error) {
          console.error('[module-tab] Failed to parse shopfloor status payload:', error);
        }
      });
      
      const moduleSub = moduleStream$.subscribe((message) => {
        if (this.dashboard.injectMessage) {
          this.dashboard.injectMessage(message);
        }
        try {
          const payload = typeof message.payload === 'string' 
            ? JSON.parse(message.payload) 
            : message.payload;
          this.messageMonitor.addMessage(message.topic, payload, message.timestamp);
        } catch (error) {
          console.error('[module-tab] Failed to parse module status payload:', error);
        }
      });
      
      // Store subscriptions for cleanup
      this.fixtureSubscriptions.add(shopfloorSub);
      this.fixtureSubscriptions.add(moduleSub);
    } catch (error) {
      console.error('[module-tab] Failed to load module status fixture:', error);
      // Don't throw - let loadFixture handle the error state
    }
  }

  private initializeStreams(): void {
    const controller = getDashboardController();
    this.dashboard = controller;
    this.activeFixture = controller.getCurrentFixture();

    this.moduleOverview$ = this.dashboard.streams.moduleOverview$.pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
    const dashboardModuleStream$ = this.moduleOverview$;
    this.bindModuleOverviewStream(dashboardModuleStream$);
    this.bindCacheOutputs();
    
    // Subscribe to FTS states to get FTS position
    this.subscriptions.add(
      this.dashboard.streams.ftsStates$.pipe(
        map((ftsStates) => {
          // Get first FTS position (assuming single FTS for now)
          const ftsEntries = Object.values(ftsStates);
          if (ftsEntries.length > 0 && ftsEntries[0].position) {
            return ftsEntries[0].position;
          }
          return null;
        })
      ).subscribe((position) => {
        this.ftsPosition = position;
        this.cdr.markForCheck();
      })
    );
  }

  private bindModuleOverviewStream(source: Observable<ModuleOverviewState>): void {
    this.moduleOverviewSub?.unsubscribe();
    this.moduleOverviewSub = source.subscribe((state) => {
      this.moduleOverviewState.setState(this.currentEnvironmentKey, state);
    });
  }

  private bindCacheOutputs(): void {
    const state$ = this.moduleOverviewState
      .getState$(this.currentEnvironmentKey)
      .pipe(
        map((state) => state ?? this.createEmptyModuleOverviewState()),
        shareReplay({ bufferSize: 1, refCount: true })
      );
    this.rows$ = this.createRowsStream(state$);
    this.moduleStatusMap$ = this.createModuleStatusMapStream(state$).pipe(
      shareReplay({ bufferSize: 1, refCount: true })
    );
    
    // Subscribe to update currentModuleStatusMap for template access
    this.subscriptions.add(
      this.moduleStatusMap$.subscribe((map) => {
        this.currentModuleStatusMap = map;
        this.cdr.markForCheck();
      })
    );
  }

  private createEmptyModuleOverviewState(): ModuleOverviewState {
    return {
      modules: {},
      transports: {},
    };
  }

  private buildRows(state: ModuleOverviewState): ModuleRow[] {
    const rows = new Map<string, ModuleRow>();

    MODULE_REGISTRY.forEach((entry) => {
      rows.set(entry.id, this.createRegistryPlaceholderRow(entry));
    });

    Object.values(state.modules).forEach((module) => {
      rows.set(module.id, this.createModuleRow(module));
    });

    Object.values(state.transports).forEach((transport) => {
      rows.set(transport.id, this.createTransportRow(transport));
    });

    return Array.from(rows.values());
  }

  private createRowsStream(source: Observable<ModuleOverviewState>): Observable<ModuleRow[]> {
    return source.pipe(
      map((overview) => this.buildRows(overview)),
      map((rows) => this.sortRows(rows))
    );
  }

  private sortRows(rows: ModuleRow[]): ModuleRow[] {
    const orderLookup = new Map<string, number>();
    MODULE_REGISTRY_ORDER.forEach((id, index) => orderLookup.set(id, index));

    return [...rows].sort((a, b) => {
      const orderA = orderLookup.has(a.id) ? orderLookup.get(a.id)! : Number.MAX_SAFE_INTEGER;
      const orderB = orderLookup.has(b.id) ? orderLookup.get(b.id)! : Number.MAX_SAFE_INTEGER;
      if (orderA !== orderB) {
        return orderA - orderB;
      }
      return a.id.localeCompare(b.id);
    });
  }

  private createModuleRow(module: ModuleOverviewStatus): ModuleRow {
    const moduleType = module.subType ?? 'UNKNOWN';
    const name = this.moduleNameService.getModuleDisplayText(moduleType, 'id-full');
    const iconPath = this.resolveIconPath(moduleType);
    const availabilityLabel = this.getAvailabilityLabel(module.availability);
    const registryEntry = MODULE_REGISTRY_LOOKUP.get(module.id);
    const isRegistryModule = registryEntry?.kind === 'module';

    const actions: ModuleCommand[] = [];
    if (module.hasCalibration) {
      actions.push({
        label: $localize`:@@moduleCommandCalibrate:Calibrate`,
        handler: () => this.dashboard.commands.calibrateModule(module.id),
      });
    }

    // Calculate message count for this specific module (by serial-Id)
    const messageCount = this.getModuleMessageCount(module.id);

    return {
      id: module.id,
      kind: 'module',
      name,
      iconPath,
      registryActive: Boolean(isRegistryModule),
      connected: module.connected,
      availabilityLabel,
      availabilityClass: this.getAvailabilityClass(module.availability),
      availabilityIcon: this.getAvailabilityIcon(module.availability),
      registryIcon: isRegistryModule ? STATUS_ICONS.registry.active : STATUS_ICONS.registry.inactive,
      connectedIcon: module.connected ? STATUS_ICONS.connection.connected : STATUS_ICONS.connection.disconnected,
      messageCount,
      lastUpdate: module.lastUpdate ?? 'N/A',
      actions,
    };
  }

  private createTransportRow(transport: TransportOverviewStatus): ModuleRow {
    const availabilityLabel = this.getAvailabilityLabel(transport.availability);
    const actions: ModuleCommand[] = [];
    const registryEntry = MODULE_REGISTRY_LOOKUP.get(transport.id);
    const isRegistryTransport = registryEntry?.kind === 'transport';

    const needsInitialDock =
      !transport.lastModuleSerialNumber || transport.lastModuleSerialNumber === 'UNKNOWN';

    if (needsInitialDock) {
      actions.push({
        label: $localize`:@@moduleCommandDock:Dock`,
        handler: () => this.dashboard.commands.dockFts(transport.id, transport.lastNodeId),
      });
    }

    actions.push({
      label: transport.charging 
        ? $localize`:@@moduleCommandStopCharging:Stop Charging`
        : $localize`:@@moduleCommandCharge:Charge`,
      secondary: transport.charging ?? false,
      handler: () =>
        this.dashboard.commands.setFtsCharge(transport.id, !(transport.charging ?? false)),
    });

    // Calculate message count for this specific transport (by serial-Id)
    const messageCount = this.getModuleMessageCount(transport.id);

    return {
      id: transport.id,
      kind: 'transport',
      name: this.moduleNameService.getModuleDisplayText('FTS', 'id-full'),
      iconPath: this.resolveIconPath('FTS'),
      registryActive: Boolean(isRegistryTransport),
      connected: transport.connected,
      availabilityLabel,
      availabilityClass: this.getAvailabilityClass(transport.availability),
      availabilityIcon: this.getAvailabilityIcon(transport.availability),
      registryIcon: isRegistryTransport ? STATUS_ICONS.registry.active : STATUS_ICONS.registry.inactive,
      connectedIcon: transport.connected
        ? STATUS_ICONS.connection.connected
        : STATUS_ICONS.connection.disconnected,
      messageCount,
      lastUpdate: transport.lastUpdate ?? 'N/A',
      actions,
      charging: transport.charging ?? false,
      lastModuleSerialNumber: transport.lastModuleSerialNumber,
      lastNodeId: transport.lastNodeId,
    };
  }

  private resolveIconPath(key: string): string {
    const asset =
      SHOPFLOOR_ASSET_MAP[key as keyof typeof SHOPFLOOR_ASSET_MAP] ?? DEFAULT_SHOPFLOOR_ICON;
    return asset.startsWith('/') ? asset.slice(1) : asset;
  }

  private createRegistryPlaceholderRow(entry: ModuleRegistryEntry): ModuleRow {
    const availability: ModuleAvailabilityStatus = 'Unknown';
    const name = this.moduleNameService.getModuleDisplayText(entry.type, 'id-full');
    return {
      id: entry.id,
      kind: entry.kind,
      name,
      iconPath: this.resolveIconPath(entry.type),
      registryActive: true,
      connected: false,
      availabilityLabel: this.getAvailabilityLabel(availability),
      availabilityClass: this.getAvailabilityClass(availability),
      availabilityIcon: this.getAvailabilityIcon(availability),
      registryIcon: STATUS_ICONS.registry.active,
      connectedIcon: STATUS_ICONS.connection.disconnected,
      messageCount: 0,
      lastUpdate: 'N/A',
      actions: [],
    };
  }

  private getAvailabilityLabel(status: ModuleAvailabilityStatus): string {
    switch (status) {
      case 'READY':
        return $localize`:@@moduleAvailabilityAvailable:Available`;
      case 'BUSY':
        return $localize`:@@moduleAvailabilityBusy:Busy`;
      case 'BLOCKED':
        return $localize`:@@moduleAvailabilityBlocked:Blocked`;
      case 'Unknown':
      default:
        return status && status !== '' ? status : $localize`:@@moduleAvailabilityUnknown:Unknown`;
    }
  }

  private getAvailabilityIcon(status: ModuleAvailabilityStatus): string {
    const normalized = (status ?? 'unknown').toString().toLowerCase();
    if (normalized === 'ready') {
      return STATUS_ICONS.availability.ready;
    }
    if (normalized === 'busy') {
      return STATUS_ICONS.availability.busy;
    }
    if (normalized === 'blocked') {
      return STATUS_ICONS.availability.blocked;
    }
    return STATUS_ICONS.availability.unknown;
  }

  private getAvailabilityClass(status: ModuleAvailabilityStatus): string {
    const normalized = (status ?? 'unknown').toString().toLowerCase();
    if (normalized === 'ready') {
      return 'availability availability--ready';
    }
    if (normalized === 'busy') {
      return 'availability availability--busy';
    }
    if (normalized === 'blocked') {
      return 'availability availability--blocked';
    }
    return 'availability availability--unknown';
  }

  private createModuleStatusMapStream(source: Observable<ModuleOverviewState>): Observable<Map<string, { connected: boolean; availability: ModuleAvailabilityStatus }>> {
    return source.pipe(
      map((overview) => {
        const statusMap = new Map<string, { connected: boolean; availability: ModuleAvailabilityStatus }>();
        
        // Add module statuses - map by multiple keys for flexible lookup
        Object.values(overview.modules).forEach((module) => {
          const status = {
            connected: module.connected,
            availability: module.availability,
          };
          
          // Map by serial-Id (primary key)
          statusMap.set(module.id, status);
          
          // Also map by module type/subType for cell.name matching
          if (module.subType) {
            statusMap.set(module.subType, status);
            statusMap.set(module.subType.toUpperCase(), status);
            statusMap.set(module.subType.toLowerCase(), status);
          }
        });
        
        // Add transport (FTS) statuses
        Object.values(overview.transports).forEach((transport) => {
          const status = {
            connected: transport.connected,
            availability: transport.availability,
          };
          
          // Map by serial-Id (primary key)
          statusMap.set(transport.id, status);
          
          // Also map by "FTS" for cell.name matching
          statusMap.set('FTS', status);
          statusMap.set('fts', status);
        });
        
        return statusMap;
      })
    );
  }

  toggleShopfloorPreview(): void {
    this.shopfloorPreviewExpanded = !this.shopfloorPreviewExpanded;
    this.saveShopfloorPreviewState();
    this.cdr.markForCheck();
  }

  private loadShopfloorPreviewState(): void {
    try {
      const saved = localStorage.getItem(this.shopfloorPreviewStorageKey);
      if (saved !== null) {
        this.shopfloorPreviewExpanded = saved === 'true';
      }
    } catch (error) {
      // Ignore localStorage errors
    }
  }

  private saveShopfloorPreviewState(): void {
    try {
      localStorage.setItem(this.shopfloorPreviewStorageKey, String(this.shopfloorPreviewExpanded));
    } catch (error) {
      // Ignore localStorage errors
    }
  }

  onModuleCellSelected(event: { id: string; kind: 'module' | 'fixed' }): void {
    if (event.kind !== 'module') {
      return;
    }

    // Get layout config to find serial number
    if (this.layoutConfig) {
      const cell = this.layoutConfig.cells.find((c: ShopfloorCellConfig) => c.id === event.id);

      if (cell && cell.serial_number) {
        this.selectedModuleSerialId = cell.serial_number;
        this.selectedModuleName = this.moduleNameService.getModuleDisplayText(cell.name ?? cell.id, 'id-full');
        this.sidebarOpen = true;
        this.cdr.markForCheck();
        return;
      }
    }

    // Fallback: Try to find by module overview state (use id as serial)
    this.subscriptions.add(
      this.moduleOverview$.pipe(
        map((state) => {
          const module = Object.values(state.modules).find((m) => m.id === event.id);
          if (module) {
            this.selectedModuleSerialId = module.id; // Use id as serial number
            this.selectedModuleName = this.moduleNameService.getModuleDisplayText(module.subType ?? 'UNKNOWN', 'id-full');
            this.sidebarOpen = true;
            this.cdr.markForCheck();
          }
        })
      ).subscribe()
    );
  }

  closeSidebar(): void {
    this.sidebarOpen = false;
    this.selectedModuleSerialId = null;
    this.selectedModuleName = null;
    this.cdr.markForCheck();
  }

  /**
   * Get message count for a specific module/transport by serial-Id.
   * Counts all messages from topics that belong to this module.
   */
  private getModuleMessageCount(serialId: string): number {
    try {
      const allTopics = this.messageMonitor.getTopics();
      let count = 0;

      // Patterns for module topics:
      // - module/v1/ff/<serial>/...
      // - module/v1/ff/NodeRed/<serial>/...
      // - module/<serial>/...
      // - fts/v1/ff/<serial>/... (for FTS)
      // - fts/<serial>/... (for FTS)

      allTopics.forEach((topic) => {
        // Module topics
        if (topic.startsWith('module/')) {
          const parts = topic.split('/');
          // Check for NodeRed pattern: module/v1/ff/NodeRed/<serial>/...
          if (parts.length >= 5 && parts[3] === 'NodeRed' && parts[4] === serialId) {
            const history = this.messageMonitor.getHistory(topic);
            count += history.length;
          }
          // Check for direct pattern: module/v1/ff/<serial>/...
          else if (parts.length >= 4 && parts[1] === 'v1' && parts[2] === 'ff' && parts[3] === serialId) {
            const history = this.messageMonitor.getHistory(topic);
            count += history.length;
          }
          // Check for generic pattern: module/<serial>/...
          else if (parts.length >= 2 && parts[1] === serialId) {
            const history = this.messageMonitor.getHistory(topic);
            count += history.length;
          }
        }
        // FTS topics
        else if (topic.startsWith('fts/')) {
          const parts = topic.split('/');
          // Check for pattern: fts/v1/ff/<serial>/...
          if (parts.length >= 4 && parts[1] === 'v1' && parts[2] === 'ff' && parts[3] === serialId) {
            const history = this.messageMonitor.getHistory(topic);
            count += history.length;
          }
          // Check for generic pattern: fts/<serial>/...
          else if (parts.length >= 2 && parts[1] === serialId) {
            const history = this.messageMonitor.getHistory(topic);
            count += history.length;
          }
        }
      });

      return count;
    } catch (error) {
      console.warn(`[ModuleTab] Failed to get message count for ${serialId}:`, error);
      return 0;
    }
  }
}

