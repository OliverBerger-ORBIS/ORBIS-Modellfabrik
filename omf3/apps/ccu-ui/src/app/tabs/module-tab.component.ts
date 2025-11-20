import { AsyncPipe, NgFor, NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import type {
  ModuleOverviewState,
  ModuleAvailabilityStatus,
  ModuleOverviewStatus,
  TransportOverviewStatus,
} from '@omf3/entities';
import { SHOPFLOOR_ASSET_MAP, type OrderFixtureName } from '@omf3/testing-fixtures';
import { getDashboardController } from '../mock-dashboard';
import type { Observable } from 'rxjs';
import { filter, map, shareReplay, startWith } from 'rxjs/operators';
import { merge } from 'rxjs';
import { EnvironmentService } from '../services/environment.service';
import { MessageMonitorService } from '../services/message-monitor.service';
import { ModuleNameService } from '../services/module-name.service';

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
  configured: boolean;
  connected: boolean;
  availabilityLabel: string;
  availabilityClass: string;
  availabilityIcon: string;
  registryIcon: string;
  configuredIcon: string;
  connectedIcon: string;
  messageCount: number;
  lastUpdate: string;
  actions: ModuleCommand[];
  charging?: boolean;
  lastModuleSerialNumber?: string;
  lastNodeId?: string;
};

const MODULE_DISPLAY_ORDER = [
  'SVR3QA0022',
  'SVR4H76449',
  'SVR3QA2098',
  'SVR4H76530',
  'SVR4H73275',
  'CHRG0',
  '5iO4',
];

const MODULE_NAME_MAP: Record<string, string> = {
  HBW: 'HBW',
  DRILL: 'DRILL',
  MILL: 'MILL',
  AIQS: 'AIQS',
  DPS: 'DPS',
  CHRG: 'CHRG',
  FTS: 'FTS',
};

const STATUS_ICONS = {
  registry: {
    active: '✅',
    inactive: '❌',
  },
  configured: {
    yes: '📋',
    no: '❌',
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
export class ModuleTabComponent implements OnInit {
  private readonly dashboard = getDashboardController();

  constructor(
    private readonly environmentService: EnvironmentService,
    private readonly messageMonitor: MessageMonitorService,
    private readonly moduleNameService: ModuleNameService
  ) {
    // Pattern: Merge MessageMonitor last messages with dashboard streams
    // This ensures we get the latest module data even when connecting while factory is already running
    // Get last message for pairing state (single topic)
    // Note: Module factsheets come from multiple topics (module/v1/#), so the dashboard stream
    // handles those, but we use MessageMonitor for pairing state to ensure it's available immediately
    const lastPairing = this.messageMonitor.getLastMessage('ccu/pairing/state').pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => msg!.payload),
      startWith(null)
    );
    
    // The dashboard stream already handles the full module overview state aggregation
    // including pairing state, factsheets, etc. The MessageMonitor ensures that when
    // connecting while factory is already running, the last pairing state is available
    // and will be processed by the dashboard stream when it receives the message.
    // We use the dashboard stream directly as it handles all the aggregation logic.
    this.moduleOverview$ = this.dashboard.streams.moduleOverview$.pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
    this.rows$ = this.createRowsStream(this.moduleOverview$);
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

  moduleOverview$: Observable<ModuleOverviewState>;
  rows$: Observable<ModuleRow[]>;

  readonly headingIcon = 'headings/mehrere.svg';

  ngOnInit(): void {
    // Only load fixture in mock mode; in live/replay mode, streams are already connected
    if (this.isMockMode) {
      void this.loadFixture(this.activeFixture);
    }
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
      this.moduleOverview$ = streams.moduleOverview$;
      this.rows$ = this.createRowsStream(this.moduleOverview$);
    } catch (error) {
      console.warn('Failed to load module fixture', fixture, error);
    } finally {
      this.loading = false;
    }
  }

  private buildRows(state: ModuleOverviewState): ModuleRow[] {
    const rows: ModuleRow[] = [];

    Object.values(state.modules).forEach((module) => {
      rows.push(this.createModuleRow(module));
    });

    Object.values(state.transports).forEach((transport) => {
      rows.push(this.createTransportRow(transport));
    });

    return rows;
  }

  private createRowsStream(source: Observable<ModuleOverviewState>): Observable<ModuleRow[]> {
    return source.pipe(
      map((overview) => this.buildRows(overview)),
      map((rows) => this.sortRows(rows))
    );
  }

  private sortRows(rows: ModuleRow[]): ModuleRow[] {
    const orderLookup = new Map<string, number>();
    MODULE_DISPLAY_ORDER.forEach((id, index) => orderLookup.set(id, index));

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
      registryActive: true,
      configured: module.configured ?? false,
      connected: module.connected,
      availabilityLabel,
      availabilityClass: this.getAvailabilityClass(module.availability),
      availabilityIcon: this.getAvailabilityIcon(module.availability),
      registryIcon: STATUS_ICONS.registry.active,
      configuredIcon: (module.configured ?? false) ? STATUS_ICONS.configured.yes : STATUS_ICONS.configured.no,
      connectedIcon: module.connected ? STATUS_ICONS.connection.connected : STATUS_ICONS.connection.disconnected,
      messageCount: module.messageCount ?? 0,
      lastUpdate: module.lastUpdate ?? 'N/A',
      actions,
    };
  }

  private createTransportRow(transport: TransportOverviewStatus): ModuleRow {
    const availabilityLabel = this.getAvailabilityLabel(transport.availability);
    const actions: ModuleCommand[] = [];

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
      registryActive: true,
      configured: true,
      connected: transport.connected,
      availabilityLabel,
      availabilityClass: this.getAvailabilityClass(transport.availability),
      availabilityIcon: this.getAvailabilityIcon(transport.availability),
      registryIcon: STATUS_ICONS.registry.active,
      configuredIcon: STATUS_ICONS.configured.yes,
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

  private resolveIconPath(key: string): string | null {
    const asset = SHOPFLOOR_ASSET_MAP[key as keyof typeof SHOPFLOOR_ASSET_MAP];
    if (!asset) {
      return null;
    }
    return asset.startsWith('/') ? asset.slice(1) : asset;
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

