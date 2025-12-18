import { AsyncPipe, NgFor, NgIf, NgClass, JsonPipe } from '@angular/common';
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
import { ConnectionService, type ConnectionState } from '../services/connection.service';
import { ModuleOverviewStateService } from '../services/module-overview-state.service';
import { ShopfloorPreviewComponent } from '../components/shopfloor-preview/shopfloor-preview.component';
import { MessageMonitorService, type MonitoredMessage } from '../services/message-monitor.service';
import { ModuleDetailsSidebarComponent } from '../components/module-details-sidebar/module-details-sidebar.component';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import type { ShopfloorLayoutConfig, ShopfloorCellConfig } from '../components/shopfloor-preview/shopfloor-layout.types';
import { ShopfloorMappingService, type ModuleInfo } from '../services/shopfloor-mapping.service';

interface ModuleCommand {
  label: string;
  secondary?: boolean;
  handler: () => Promise<void> | void;
}

interface SequenceCommand {
  timestamp?: string;
  serialNumber: string;
  orderId: string;
  orderUpdateId: number;
  action: {
    id: string;
    command: string;
    metadata: Record<string, unknown>;
  };
}

interface ModuleSequenceCommands {
  commands: SequenceCommand[];
  topic: string;
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

const MODULE_NAME_MAP: Record<string, string> = {
  HBW: 'HBW',
  DRILL: 'DRILL',
  MILL: 'MILL',
  AIQS: 'AIQS',
  DPS: 'DPS',
  CHRG: 'CHRG',
  FTS: 'FTS',
};

const DEFAULT_SHOPFLOOR_ICON = SHOPFLOOR_ASSET_MAP['QUESTION'] ?? 'assets/svg/shopfloor/shared/question.svg';

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
  imports: [NgIf, NgFor, NgClass, AsyncPipe, JsonPipe, ShopfloorPreviewComponent, ModuleDetailsSidebarComponent],
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
  private moduleRegistry: ModuleRegistryEntry[] = [];
  private moduleRegistryOrder: string[] = [];
  private moduleRegistryLookup = new Map<string, ModuleRegistryEntry>();

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
    private readonly http: HttpClient,
    private readonly mappingService: ShopfloorMappingService,
    private readonly route: ActivatedRoute,
    private readonly router: Router
  ) {
    this.currentEnvironmentKey = this.environmentService.current.key;
    this.loadShopfloorPreviewState();
    this.bindCacheOutputs();
    this.initializeStreams();
  }

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  readonly fixtureOptions: (OrderFixtureName | 'shopfloor-status' | 'drill-action' | 'module-action-history')[] = [
    'startup',
    'white',
    'white_step3',
    'blue',
    'red',
    'mixed',
    'storage',
    'shopfloor-status',
    'drill-action',
    'module-action-history',
  ];
  readonly fixtureLabels: Partial<Record<OrderFixtureName | 'shopfloor-status' | 'drill-action' | 'module-action-history', string>> = {
    startup: $localize`:@@fixtureLabelStartup:Startup`,
    white: $localize`:@@fixtureLabelWhite:White`,
    white_step3: $localize`:@@fixtureLabelWhiteStep3:White • Step 3`,
    blue: $localize`:@@fixtureLabelBlue:Blue`,
    red: $localize`:@@fixtureLabelRed:Red`,
    mixed: $localize`:@@fixtureLabelMixed:Mixed`,
    storage: $localize`:@@fixtureLabelStorage:Storage`,
    'track-trace': $localize`:@@fixtureLabelTrackTrace:Track & Trace`,
    'shopfloor-status': $localize`:@@fixtureLabelShopfloorStatus:Shopfloor Status`,
    'drill-action': $localize`:@@dspActionFixtureLabel:Drill Action`,
    'module-action-history': $localize`:@@moduleActionHistoryFixtureLabel:Module Test Data`,
  };

  activeFixture: OrderFixtureName | 'shopfloor-status' | 'drill-action' | 'module-action-history' = 'startup';
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
  selectedModuleIcon: string | null = null;
  selectedModuleMeta: {
    availability?: ModuleAvailabilityStatus | string;
    availabilityLabel?: string;
    availabilityIcon?: string;
    availabilityClass?: string;
    connected?: boolean;
    connectionIcon?: string;
    connectionLabel?: string;
    configured?: boolean;
    lastUpdate?: string;
    position?: string;
    ipAddress?: string;
    moduleType?: string;
    drillAction?: {
      currentLight: string | null;
      previousLight: string | null;
      messages: MonitoredMessage[];
    };
    hbwData?: {
      currentAction?: { command: string; state: string };
      storageSlot?: string;
      storageLevel?: string;
      workpieceId?: string;
    };
    drillData?: {
      currentAction?: { command: string; state: string };
      drillDepth?: number;
      drillSpeed?: number;
      workpieceId?: string;
    };
    millData?: {
      currentAction?: { command: string; state: string };
      millDepth?: number;
      millSpeed?: number;
      workpieceId?: string;
    };
  } | null = null;

  // Shopfloor layout config for serial number lookup
  private layoutConfig: ShopfloorLayoutConfig | null = null;

  // Sequence commands for selected module
  sequenceCommands: ModuleSequenceCommands | null = null;
  // Track sent commands for developer mode
  sentSequenceCommands: Array<{ command: SequenceCommand; topic: string; timestamp: string }> = [];

  readonly headingIcon = 'assets/svg/ui/heading-modules.svg';

  // I18n labels for shopfloor preview
  readonly shopfloorPreviewExpandLabel = $localize`:@@moduleTabShopfloorPreviewExpand:Expand shopfloor preview`;
  readonly shopfloorPreviewCollapseLabel = $localize`:@@moduleTabShopfloorPreviewCollapse:Collapse shopfloor preview`;
  readonly modulesStatusBadgeText = $localize`:@@moduleTabModulesStatusBadge:Modules Status`;

  private initializeRegistry(): void {
    // Build registry from mapping service; fallback: add common FTS serial if not present
    const modules = this.mappingService.getAllModules();
    this.moduleRegistry = modules.map((m: ModuleInfo) => ({
      id: m.serialId,
      type: (m.moduleType as keyof typeof MODULE_NAME_MAP) ?? 'UNKNOWN',
      kind: 'module',
    }));

    // Ensure FTS placeholder exists (common serial for AGV)
    if (!this.moduleRegistry.find((e) => e.id === '5iO4')) {
      this.moduleRegistry.push({ id: '5iO4', type: 'FTS', kind: 'transport' });
    }

    this.moduleRegistryOrder = this.moduleRegistry.map((entry) => entry.id);
    this.moduleRegistryLookup = new Map<string, ModuleRegistryEntry>(
      this.moduleRegistry.map((entry) => [entry.id, entry])
    );
  }

  ngOnInit(): void {
    // Load shopfloor layout config for serial number lookup and registry initialization
    this.http.get<ShopfloorLayoutConfig>('shopfloor/shopfloor_layout.json').subscribe({
      next: (config) => {
        this.layoutConfig = config;
        this.mappingService.initializeLayout(config);
        this.initializeRegistry();
        
        // Check for module query parameter from architecture click
        this.route.queryParams.subscribe(params => {
          const moduleType = params['module'];
          if (moduleType) {
            // Find module of this type and select it
            this.selectModuleByType(moduleType);
            // Remove query parameter from URL
            this.router.navigate([], {
              relativeTo: this.route,
              queryParams: {},
              replaceUrl: true
            });
          }
        });
      },
      error: (error) => {
        console.warn('Failed to load shopfloor layout config:', error);
      }
    });

    this.subscriptions.add(
      this.connectionService.state$
        .pipe(distinctUntilChanged())
        .subscribe((state: ConnectionState) => {
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

  async loadFixture(fixture: OrderFixtureName | 'shopfloor-status' | 'drill-action' | 'module-action-history'): Promise<void> {
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
      } else if (fixture === 'drill-action') {
        // Clear previous and load status + drill action fixture
        this.moduleOverviewState.clear(this.currentEnvironmentKey);
        await this.loadModuleStatusFixture();
        await this.loadDrillActionFixture();
        await new Promise((resolve) => setTimeout(resolve, 300));
        this.cdr.markForCheck();
      } else if (fixture === 'module-action-history') {
        // Load module action history fixture with HBW, DRILL, MILL data
        this.moduleOverviewState.clear(this.currentEnvironmentKey);
        await this.loadModuleStatusFixture();
        await this.loadModuleActionHistoryFixture();
        await new Promise((resolve) => setTimeout(resolve, 300));
        this.cdr.markForCheck();
      } else {
        // Map OrderFixtureName to tab-specific preset
        const presetMap: Partial<Record<OrderFixtureName, string>> = {
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

  private async loadDrillActionFixture(): Promise<void> {
    try {
      const { createDspActionFixtureStream } = await import('@omf3/testing-fixtures');
      const stream$ = createDspActionFixtureStream({
        intervalMs: 1000,
        loop: true,
      });
      const sub = stream$.subscribe((message) => {
        try {
          const payload = typeof message.payload === 'string' ? JSON.parse(message.payload) : message.payload;
          this.messageMonitor.addMessage(message.topic, payload, message.timestamp);
        } catch (error) {
          console.error('[module-tab] Failed to parse drill action payload:', error);
        }
      });
      this.fixtureSubscriptions.add(sub);
    } catch (error) {
      console.error('[module-tab] Failed to load drill action fixture:', error);
    }
  }

  private async loadModuleActionHistoryFixture(): Promise<void> {
    try {
      const { createModuleActionHistoryFixtureStream } = await import('@omf3/testing-fixtures');
      const stream$ = createModuleActionHistoryFixtureStream({
        intervalMs: 0,
      });
      const sub = stream$.subscribe((message) => {
        try {
          const payload = typeof message.payload === 'string' ? JSON.parse(message.payload) : message.payload;
          this.messageMonitor.addMessage(message.topic, payload, message.timestamp);
        } catch (error) {
          console.error('[module-tab] Failed to parse module action history payload:', error);
        }
      });
      this.fixtureSubscriptions.add(sub);
    } catch (error) {
      console.error('[module-tab] Failed to load module action history fixture:', error);
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
    this.moduleOverviewSub = source.subscribe((state: ModuleOverviewState) => {
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

    this.moduleRegistry.forEach((entry) => {
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
    this.moduleRegistryOrder.forEach((id, index) => orderLookup.set(id, index));

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
    const registryEntry = this.moduleRegistryLookup.get(module.id);
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
    const registryEntry = this.moduleRegistryLookup.get(transport.id);
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

  onModuleCellDoubleClicked(event: { id: string; kind: 'module' | 'fixed' }): void {
    if (event.kind !== 'module') {
      return;
    }
    // Reuse selection lookup and open sidebar
    this.onModuleCellSelected(event);
    this.openSidebarForSelected();
  }

  private updateSelectedMeta(cell: ShopfloorCellConfig | null): void {
    const snapshot = this.moduleOverviewState.getSnapshot(this.currentEnvironmentKey);
    const moduleId = this.selectedModuleSerialId ?? cell?.id ?? null;
    const moduleDetails =
      moduleId ? snapshot?.modules?.[moduleId] ?? snapshot?.modules?.[cell?.id ?? ''] : null;

    const availabilityStatus = (moduleDetails?.availability ?? 'Unknown') as ModuleAvailabilityStatus;
    const availabilityLabel = this.getAvailabilityLabel(availabilityStatus);
    const availabilityIcon = this.getAvailabilityIcon(availabilityStatus);
    const availabilityClass = this.getAvailabilityClass(availabilityStatus);

    const connectionLabel =
      moduleDetails?.connected === true
        ? $localize`:@@moduleTabConnected:Connected`
        : moduleDetails?.connected === false
        ? $localize`:@@moduleTabDisconnected:Disconnected`
        : $localize`:@@moduleTabUnknown:Unknown`;
    const connectionIcon =
      moduleDetails?.connected === true
        ? STATUS_ICONS.connection.connected
        : moduleDetails?.connected === false
        ? STATUS_ICONS.connection.disconnected
        : STATUS_ICONS.availability.unknown;

    const moduleType = moduleDetails?.subType ?? cell?.name ?? 'UNKNOWN';
    
    // Load sequence commands for this module type
    this.loadSequenceCommands(moduleType);

    // Get module-specific data based on module type
    const moduleTypeUpper = moduleType.toUpperCase();
    const hbwData = moduleTypeUpper === 'HBW' && moduleId ? this.getHbwData(moduleId) : undefined;
    const drillData = moduleTypeUpper === 'DRILL' && moduleId ? this.getDrillData(moduleId) : undefined;
    const millData = moduleTypeUpper === 'MILL' && moduleId ? this.getMillData(moduleId) : undefined;

    this.selectedModuleMeta = {
      availability: availabilityStatus,
      availabilityLabel,
      availabilityIcon,
      availabilityClass,
      connected: moduleDetails?.connected,
      connectionIcon,
      connectionLabel,
      configured: moduleDetails?.configured,
      lastUpdate: moduleDetails?.lastUpdate,
      position: cell ? this.formatPosition(cell) : undefined,
      ipAddress: (moduleDetails as any)?.ipAddress ?? undefined,
      moduleType,
      drillAction: moduleType === 'DRILL' ? this.getDrillActionData() : undefined,
      hbwData: hbwData ?? undefined,
      drillData: drillData ?? undefined,
      millData: millData ?? undefined,
    };

    const iconKey = cell?.icon ?? cell?.name ?? moduleDetails?.subType ?? moduleDetails?.id ?? 'QUESTION';
    this.selectedModuleIcon = this.resolveIconPath(iconKey);
  }

  openSidebarForSelected(): void {
    if (!this.selectedModuleSerialId) {
      return;
    }
    this.sidebarOpen = true;
    this.cdr.markForCheck();
  }

  get selectedStatus(): { connected: boolean; availability: ModuleAvailabilityStatus } | null {
    if (!this.selectedModuleSerialId || !this.currentModuleStatusMap) {
      return null;
    }
    return this.currentModuleStatusMap.get(this.selectedModuleSerialId) ?? null;
  }

  get selectedAvailabilityLabel(): string {
    const availability = this.selectedStatus?.availability;
    if (!availability) return 'Unknown';
    const normalized = availability.toString().toLowerCase();
    if (normalized === 'ready') return 'Ready';
    if (normalized === 'busy') return 'Busy';
    if (normalized === 'blocked') return 'Blocked';
    return 'Unknown';
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

  /**
   * Select module by type (e.g., 'MILL', 'DRILL', etc.)
   * Used when navigating from architecture diagram
   */
  private selectModuleByType(moduleType: string): void {
    if (!this.layoutConfig) {
      return;
    }

    // Find cell with matching module type
    const cell = this.layoutConfig.cells.find((c: ShopfloorCellConfig) => {
      const cellName = c.name?.toUpperCase();
      return cellName === moduleType.toUpperCase();
    });

    if (cell) {
      // Simulate cell selection
      this.onModuleCellSelected({ id: cell.id, kind: 'module' });
    } else {
      // Fallback: try to find by serial number pattern or module registry
      const snapshot = this.moduleOverviewState.getSnapshot(this.currentEnvironmentKey);
      const moduleStates = snapshot?.modules ?? {};
      
      // Find first module with matching type
      const moduleEntry = Object.values(moduleStates).find(
        (m) => m.subType?.toUpperCase() === moduleType.toUpperCase()
      );

      if (moduleEntry) {
        this.selectedModuleSerialId = moduleEntry.id;
        const display = this.moduleNameService.getModuleDisplayName(moduleEntry.subType ?? moduleType);
        this.selectedModuleName = display.fullName;
        this.updateSelectedMeta(null);
        this.loadSequenceCommands(moduleEntry.subType ?? moduleType);
        this.cdr.markForCheck();
      }
    }
  }

  onModuleCellSelected(event: { id: string; kind: 'module' | 'fixed' }): void {
    if (event.kind !== 'module') {
      return;
    }

    const cell = this.layoutConfig?.cells.find((c: ShopfloorCellConfig) => c.id === event.id) ?? null;
    const snapshot = this.moduleOverviewState.getSnapshot(this.currentEnvironmentKey);
    const moduleStates = snapshot?.modules ?? {};
    const moduleDetails =
      Object.values(moduleStates).find((m) => m.id === (cell?.serial_number ?? event.id)) ??
      moduleStates[event.id];

    const moduleType = moduleDetails?.subType ?? cell?.name ?? 'UNKNOWN';
    const display = this.moduleNameService.getModuleDisplayName(moduleType);

    this.selectedModuleSerialId = moduleDetails?.id ?? cell?.serial_number ?? event.id;
    this.selectedModuleName = display.fullName;

    this.updateSelectedMeta(cell);
    this.loadSequenceCommands(moduleType);
    this.cdr.markForCheck();
  }

  closeSidebar(): void {
    this.sidebarOpen = false;
    // Preserve selection - don't clear selectedModuleSerialId, selectedModuleName, etc.
    // This allows the user to reopen the sidebar without losing their selection
    this.cdr.markForCheck();
  }

  /**
   * Load sequence commands for the selected module type
   */
  private async loadSequenceCommands(moduleType: string): Promise<void> {
    const sequenceFileMap: Record<string, string> = {
      'DRILL': 'DRILL-Sequence.json',
      'MILL': 'MILL-Sequence.json',
      'AIQS': 'AIQS-Sequence.json',
    };

    const sequenceFile = sequenceFileMap[moduleType.toUpperCase()];
    if (!sequenceFile) {
      this.sequenceCommands = null;
      this.sentSequenceCommands = [];
      return;
    }

    try {
      const response = await this.http.get(`data/omf-data/${sequenceFile}`, { responseType: 'text' }).toPromise();
      if (!response) {
        this.sequenceCommands = null;
        this.sentSequenceCommands = [];
        return;
      }

      // Parse the sequence file (format: Topic line, then JSON payloads separated by blank lines)
      const lines = response.split('\n');
      let topic = '';
      const commands: SequenceCommand[] = [];
      let currentJson = '';
      let inPayload = false;

      for (const line of lines) {
        const trimmed = line.trim();
        
        // Skip comments and empty lines at start
        if (trimmed === '' || trimmed.startsWith('#')) {
          if (inPayload && currentJson.trim() !== '') {
            // End of JSON payload
            try {
              const payload = JSON.parse(currentJson.trim());
              commands.push(payload);
              currentJson = '';
              inPayload = false;
            } catch (error) {
              console.warn(`[module-tab] Failed to parse sequence command:`, error);
              currentJson = '';
              inPayload = false;
            }
          }
          continue;
        }
        
        if (trimmed.startsWith('Topic:')) {
          topic = trimmed.replace('Topic:', '').trim();
          continue;
        }
        
        if (trimmed.startsWith('Payload:')) {
          // Start of payload section
          continue;
        }
        
        if (trimmed.startsWith('{')) {
          // Start of JSON object
          inPayload = true;
          currentJson = trimmed;
          continue;
        }
        
        if (inPayload) {
          currentJson += '\n' + line;
        }
      }

      // Parse last JSON if exists
      if (currentJson.trim() !== '') {
        try {
          const payload = JSON.parse(currentJson.trim());
          commands.push(payload);
        } catch (error) {
          console.warn(`[module-tab] Failed to parse last sequence command:`, error);
        }
      }

      if (commands.length > 0 && topic) {
        this.sequenceCommands = { commands, topic };
        this.sentSequenceCommands = []; // Reset sent commands when loading new sequence
        console.log(`[module-tab] Loaded ${commands.length} sequence commands for ${moduleType}`, { topic, commands });
      } else {
        console.warn(`[module-tab] No commands or topic found for ${moduleType}`, { commands: commands.length, topic });
        this.sequenceCommands = null;
        this.sentSequenceCommands = [];
      }
    } catch (error) {
      console.warn(`[module-tab] Failed to load sequence commands for ${moduleType}:`, error);
      this.sequenceCommands = null;
      this.sentSequenceCommands = [];
    }
    this.cdr.markForCheck();
  }

  /**
   * Send a specific command from the sequence by index
   */
  async sendSequenceCommand(commandIndex: number): Promise<void> {
    if (!this.sequenceCommands || commandIndex < 0 || commandIndex >= this.sequenceCommands.commands.length) {
      console.warn(`[module-tab] Invalid command index: ${commandIndex}`);
      return;
    }

    const command = this.sequenceCommands.commands[commandIndex];
    
    // Add current timestamp to command payload (overwrite placeholder if exists)
    const commandWithTimestamp = {
      ...command,
      timestamp: new Date().toISOString(),
    };
    
    try {
      await this.connectionService.publish(this.sequenceCommands.topic, commandWithTimestamp, { qos: 1 });
      console.log(`[module-tab] Sent sequence command ${commandIndex + 1}/${this.sequenceCommands.commands.length}: ${command.action.command}`);
      
      // Track sent command for developer mode (use command with timestamp)
      this.sentSequenceCommands.push({
        command: commandWithTimestamp,
        topic: this.sequenceCommands.topic,
        timestamp: new Date().toISOString(),
      });
      
      // Keep only last 10 sent commands
      if (this.sentSequenceCommands.length > 10) {
        this.sentSequenceCommands.shift();
      }
      
      this.cdr.markForCheck();
    } catch (error) {
      console.error(`[module-tab] Failed to send sequence command:`, error);
    }
  }

  /**
   * Check if a command has been sent
   */
  isCommandSent(commandIndex: number): boolean {
    if (!this.sequenceCommands || commandIndex < 0 || commandIndex >= this.sequenceCommands.commands.length) {
      return false;
    }
    const command = this.sequenceCommands.commands[commandIndex];
    return this.sentSequenceCommands.some(
      (sent: { command: SequenceCommand; topic: string; timestamp: string }) => 
        sent.command.orderUpdateId === command.orderUpdateId && sent.command.action.id === command.action.id
    );
  }

  /**
   * Format JSON payload for display (like in sidebar)
   */
  formatJsonPayload(payload: unknown): string {
    if (typeof payload === 'string') {
      try {
        const parsed = JSON.parse(payload);
        return JSON.stringify(parsed, null, 2);
      } catch {
        return payload;
      }
    }
    return JSON.stringify(payload, null, 2);
  }

  /**
   * Reset sent commands to allow retesting
   */
  resetSequenceCommands(): void {
    this.sentSequenceCommands = [];
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

  private formatPosition(cell: ShopfloorCellConfig): string {
    const { position, size } = cell;
    return `x:${position.x}, y:${position.y} (w:${size.w}, h:${size.h})`;
  }

  private getDrillActionData(): {
    currentLight: string | null;
    previousLight: string | null;
    messages: MonitoredMessage[];
  } {
    try {
      const history = this.messageMonitor.getHistory('dsp/drill/action');
      const lastTwo = history.slice(-2).reverse();

      // Determine current/previous changeLight values
      let currentLight: string | null = null;
      let previousLight: string | null = null;
      for (let i = history.length - 1; i >= 0; i -= 1) {
        const msg = history[i];
        const payload = this.parseDspActionPayload(msg);
        if (payload?.command === 'changeLight' && payload.value) {
          if (!currentLight) {
            currentLight = payload.value;
          } else if (!previousLight) {
            previousLight = payload.value;
            break;
          }
        }
      }

      return {
        currentLight,
        previousLight,
        messages: lastTwo,
      };
    } catch (error) {
      console.warn('[ModuleTab] Failed to read dsp/drill/action history', error);
      return { currentLight: null, previousLight: null, messages: [] };
    }
  }

  private parseDspActionPayload(msg: MonitoredMessage): { command?: string; value?: string } | null {
    try {
      if (typeof msg.payload === 'object' && msg.payload !== null) {
        return msg.payload as { command?: string; value?: string };
      }
      return JSON.parse(String(msg.payload)) as { command?: string; value?: string };
    } catch {
      return null;
    }
  }

  /**
   * Get HBW-specific data from MQTT state messages
   */
  private getHbwData(serialId: string): {
    currentAction?: { command: string; state: string };
    storageSlot?: string;
    storageLevel?: string;
    workpieceId?: string;
  } | null {
    try {
      const stateTopic = `module/v1/ff/${serialId}/state`;
      const history = this.messageMonitor.getHistory(stateTopic);
      
      if (history.length === 0) {
        return null;
      }

      // Get the latest state message
      const lastMsg = history[history.length - 1];
      const payload = this.parseModuleStatePayload(lastMsg);

      if (!payload) {
        return null;
      }

      return {
        currentAction: payload.actionState ? {
          command: payload.actionState.command || 'Unknown',
          state: payload.actionState.state || 'Unknown'
        } : undefined,
        storageSlot: payload.actionState?.metadata?.slot,
        storageLevel: payload.actionState?.metadata?.level,
        workpieceId: payload.actionState?.metadata?.workpieceId || payload.actionState?.metadata?.workpiece?.workpieceId,
      };
    } catch (error) {
      console.warn('[ModuleTab] Failed to get HBW data', error);
      return null;
    }
  }

  /**
   * Get DRILL-specific data from MQTT state messages
   */
  private getDrillData(serialId: string): {
    currentAction?: { command: string; state: string };
    drillDepth?: number;
    drillSpeed?: number;
    workpieceId?: string;
  } | null {
    try {
      const stateTopic = `module/v1/ff/${serialId}/state`;
      const history = this.messageMonitor.getHistory(stateTopic);
      
      if (history.length === 0) {
        return null;
      }

      // Get the latest state message
      const lastMsg = history[history.length - 1];
      const payload = this.parseModuleStatePayload(lastMsg);

      if (!payload) {
        return null;
      }

      return {
        currentAction: payload.actionState ? {
          command: payload.actionState.command || 'Unknown',
          state: payload.actionState.state || 'Unknown'
        } : undefined,
        drillDepth: payload.actionState?.metadata?.drillDepth,
        drillSpeed: payload.actionState?.metadata?.drillSpeed,
        workpieceId: payload.actionState?.metadata?.workpieceId || payload.actionState?.metadata?.workpiece?.workpieceId,
      };
    } catch (error) {
      console.warn('[ModuleTab] Failed to get DRILL data', error);
      return null;
    }
  }

  /**
   * Get MILL-specific data from MQTT state messages
   */
  private getMillData(serialId: string): {
    currentAction?: { command: string; state: string };
    millDepth?: number;
    millSpeed?: number;
    workpieceId?: string;
  } | null {
    try {
      const stateTopic = `module/v1/ff/${serialId}/state`;
      const history = this.messageMonitor.getHistory(stateTopic);
      
      if (history.length === 0) {
        return null;
      }

      // Get the latest state message
      const lastMsg = history[history.length - 1];
      const payload = this.parseModuleStatePayload(lastMsg);

      if (!payload) {
        return null;
      }

      return {
        currentAction: payload.actionState ? {
          command: payload.actionState.command || 'Unknown',
          state: payload.actionState.state || 'Unknown'
        } : undefined,
        millDepth: payload.actionState?.metadata?.millDepth,
        millSpeed: payload.actionState?.metadata?.millSpeed,
        workpieceId: payload.actionState?.metadata?.workpieceId || payload.actionState?.metadata?.workpiece?.workpieceId,
      };
    } catch (error) {
      console.warn('[ModuleTab] Failed to get MILL data', error);
      return null;
    }
  }

  /**
   * Parse module state payload from MQTT message
   */
  private parseModuleStatePayload(msg: MonitoredMessage): any {
    try {
      if (typeof msg.payload === 'object' && msg.payload !== null) {
        return msg.payload;
      }
      return JSON.parse(String(msg.payload));
    } catch {
      return null;
    }
  }
}
