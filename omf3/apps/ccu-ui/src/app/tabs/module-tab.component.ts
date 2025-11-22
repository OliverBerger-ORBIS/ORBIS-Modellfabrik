import { AsyncPipe, NgFor, NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import type {
  ModuleOverviewState,
  ModuleAvailabilityStatus,
  ModuleOverviewStatus,
  TransportOverviewStatus,
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
  imports: [NgIf, NgFor, AsyncPipe],
  templateUrl: './module-tab.component.html',
  styleUrls: ['./module-tab.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ModuleTabComponent implements OnInit, OnDestroy {
  private dashboard = getDashboardController();
  private readonly subscriptions = new Subscription();
  private moduleOverviewSub?: Subscription;
  private currentEnvironmentKey: string;

  constructor(
    private readonly environmentService: EnvironmentService,
    private readonly moduleNameService: ModuleNameService,
    private readonly connectionService: ConnectionService,
    private readonly moduleOverviewState: ModuleOverviewStateService
  ) {
    this.currentEnvironmentKey = this.environmentService.current.key;
    this.bindCacheOutputs();
    this.initializeStreams();
  }

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  readonly fixtureOptions: OrderFixtureName[] = ['startup', 'white', 'white_step3', 'blue', 'red', 'mixed', 'storage'];
  readonly fixtureLabels: Record<OrderFixtureName, string> = {
    startup: $localize`:@@fixtureLabelStartup:Startup`,
    white: $localize`:@@fixtureLabelWhite:White`,
    white_step3: $localize`:@@fixtureLabelWhiteStep3:White • Step 3`,
    blue: $localize`:@@fixtureLabelBlue:Blue`,
    red: $localize`:@@fixtureLabelRed:Red`,
    mixed: $localize`:@@fixtureLabelMixed:Mixed`,
    storage: $localize`:@@fixtureLabelStorage:Storage`,
  };

  activeFixture: OrderFixtureName = this.dashboard.getCurrentFixture();
  loading = false;

  moduleOverview$!: Observable<ModuleOverviewState>;
  rows$!: Observable<ModuleRow[]>;

  readonly headingIcon = 'headings/mehrere.svg';

  ngOnInit(): void {
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
          if (environment.key === 'mock') {
            void this.loadFixture(this.activeFixture);
          }
        })
    );

    // Only load fixture in mock mode; in live/replay mode, streams are already connected
    if (this.isMockMode) {
      void this.loadFixture(this.activeFixture);
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
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

  async loadFixture(fixture: OrderFixtureName): Promise<void> {
    if (!this.isMockMode) {
      return; // Don't load fixtures in live/replay mode
    }
    if (this.loading) {
      return;
    }
    this.activeFixture = fixture;
    this.loading = true;
    try {
      const streams = await this.dashboard.loadFixture(fixture);
      this.moduleOverviewState.clear(this.currentEnvironmentKey);
      this.moduleOverview$ = streams.moduleOverview$.pipe(
        shareReplay({ bufferSize: 1, refCount: false })
      );
      const fixtureModuleStream$ = this.moduleOverview$;
      this.bindModuleOverviewStream(fixtureModuleStream$);
    } catch (error) {
      console.warn('Failed to load module fixture', fixture, error);
    } finally {
      this.loading = false;
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
      messageCount: module.messageCount ?? 0,
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
      messageCount: transport.messageCount ?? 0,
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
}

