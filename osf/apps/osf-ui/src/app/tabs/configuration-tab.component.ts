import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import type { CcuConfigSnapshot, ModuleOverviewState } from '@osf/entities';
import { SHOPFLOOR_ASSET_MAP, type OrderFixtureName } from '@osf/testing-fixtures';
import { BehaviorSubject, type Observable, combineLatest, merge, Subscription } from 'rxjs';
import { map, shareReplay, tap, filter, startWith, distinctUntilChanged } from 'rxjs/operators';
import { getDashboardController, type DashboardStreamSet } from '../mock-dashboard';
import { MessageMonitorService, MonitoredMessage } from '../services/message-monitor.service';
import { ModuleNameService } from '../services/module-name.service';
import { ShopfloorMappingService } from '../services/shopfloor-mapping.service';
import { ModuleHardwareService } from '../services/module-hardware.service';
import { EnvironmentService } from '../services/environment.service';
import { ConnectionService } from '../services/connection.service';
import { ShopfloorPreviewComponent } from '../components/shopfloor-preview/shopfloor-preview.component';
import { DspDetailComponent } from '../components/dsp-detail/dsp-detail.component';
import { DspArchitectureComponent } from '../components/dsp-architecture/dsp-architecture.component';
import type { ShopfloorLayoutConfig, ShopfloorCellConfig } from '../components/shopfloor-preview/shopfloor-layout.types';
import { ExternalLinksService, type ExternalLinksSettings } from '../services/external-links.service';
import { ICONS } from '../shared/icons/icon.registry';
import {
  type DetailItem,
  type SelectedDetailView,
  type DetailPanelView,
  type DspDetailView,
  type DspArchitectureLayer,
  type DspActionLink,
} from './configuration-detail.types';
import { DETAIL_ASSET_MAP, getAssetPath } from '../assets/detail-asset-map';
import { getIconPath } from '../assets/icon-registry';

type LayoutCellKind = 'module' | 'fixed';

interface LayoutCell {
  id: string;
  label: string;
  kind: LayoutCellKind;
  row: number;
  column: number;
  rowSpan: number;
  columnSpan: number;
  icon: string;
  tooltip: string;
  serialNumber?: string;
  type?: string;
  background?: string;
  isSelected?: boolean;
  position?: { x: number; y: number };
  size?: { w: number; h: number };
}

interface LayoutViewModel {
  columns: number;
  rows: number;
  cells: LayoutCell[];
}

interface ParameterItemView extends DetailItem {
  icon?: string;
}

interface ParameterCardView {
  title: string;
  icon: string;
  description?: string;
  items: ParameterItemView[];
}

interface ConfigurationViewModel {
  layout: LayoutViewModel;
  selection: SelectedDetailView;
  detailPanel: DetailPanelView;
  parameterCards: ParameterCardView[];
  highlightModules: string[];
  highlightFixed: string[];
  badgeText: string;
  infoText: string;
}

@Component({
  standalone: true,
  selector: 'app-configuration-tab',
  imports: [CommonModule, ShopfloorPreviewComponent, DspDetailComponent, DspArchitectureComponent],
  templateUrl: './configuration-tab.component.html',
  styleUrl: './configuration-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ConfigurationTabComponent implements OnInit, OnDestroy {
  private dashboard = getDashboardController();
  private readonly selectedCellSubject = new BehaviorSubject<string | null>(null);
  private readonly subscriptions = new Subscription();

  readonly yesLabel = $localize`:@@commonYes:Yes`;
  readonly noLabel = $localize`:@@commonNo:No`;
  readonly unknownLabel = $localize`:@@configurationUnknown:Unknown`;
  readonly serialLabel = $localize`:@@configurationSerialLabel:Serial Number`;
  readonly availabilityLabel = $localize`:@@configurationAvailabilityLabel:Availability`;
  readonly connectedLabel = $localize`:@@configurationConnectedLabel:Connected`;
  readonly configuredLabel = $localize`:@@configurationConfiguredLabel:Configured`;
  readonly lastUpdateLabel = $localize`:@@configurationLastUpdateLabel:Last Update`;
  readonly gridPositionLabel = $localize`:@@configurationGridPositionLabel:Grid Position`;
  readonly cellPositionLabel = $localize`:@@configurationCellPositionLabel:Cell Position`;
  readonly cellDimensionLabel = $localize`:@@configurationCellDimensionLabel:Cell Dimension`;

  private readonly fixedPositionDetails: Record<
    string,
    { title: string; subtitle?: string; items: DetailItem[] }
  > = {
    COMPANY: {
      title: $localize`:@@configurationCompanyTitle:Company Showcase`,
      subtitle: $localize`:@@configurationCompanySubtitle:ORBIS Digital Transformation Partner`,
      items: [
        {
          label: $localize`:@@configurationRoleLabel:Role`,
          value: $localize`:@@configurationCompanyRole:Host area with visitor welcome and brand presentation`,
        },
      ],
    },
    ORBIS: {
      title: $localize`:@@configurationOrbisTitle:ORBIS Transformation Hub`,
      subtitle: $localize`:@@configurationOrbisSubtitle:Advisory, innovation paths, and customer stories`,
      items: [
        {
          label: $localize`:@@configurationRoleLabel:Role`,
          value: $localize`:@@configurationOrbisRole:Showcase for methodology, best practices, and consulting services`,
        },
      ],
    },
    SOFTWARE: {
      title: $localize`:@@configurationSoftwareTitle:Software & Control`,
      subtitle: $localize`:@@configurationSoftwareSubtitle:Distributed Shopfloor Processing (DSP)`,
      items: [
        {
          label: $localize`:@@configurationRoleLabel:Role`,
          value: $localize`:@@configurationSoftwareRole:Control center for MQTT routing and rule evaluation`,
        },
      ],
    },
    DSP: {
      title: $localize`:@@configurationDspTitle:Distributed Shopfloor Processing`,
      subtitle: $localize`:@@configurationDspSubtitle:Edge-to-cloud orchestration and interoperability`,
      items: [
        {
          label: $localize`:@@configurationRoleLabel:Role`,
          value: $localize`:@@configurationDspRole:Edge control platform with rule execution and analytics`,
        },
      ],
    },
  };

  private readonly dspArchitecture: DspArchitectureLayer[] = [
    {
      id: 'ux',
      title: $localize`:@@dspLayerUxTitle:SmartFactory Dashboard`,
      description: $localize`:@@dspLayerUxDescription:Visual access for operators and planners.`,
      capabilities: [],
      logoIconKey: 'logo-orbis',
      position: 'left',
    },
    {
      id: 'edge',
      title: $localize`:@@dspLayerEdgeTitle:EDGE`,
      description: $localize`:@@dspLayerEdgeDescription:Low-latency processing close to the machines.`,
      capabilities: [
        $localize`:@@dspEdgeBullet1:Low-latency processing close to the machines.`,
        $localize`:@@dspEdgeBullet2:Object-oriented choreography with decentralized control.`,
        $localize`:@@dspEdgeBullet3:Protocol conversion (OPC UA, MQTT, REST).`,
        $localize`:@@dspEdgeBullet4:Streaming analytics and buffering during connectivity issues.`,
      ],
      actionId: 'edge',
      logoIconKey: 'logo-dsp',
      functionIcons: [
        { iconKey: 'edge-data-storage', size: 48 },
        { iconKey: 'edge-digital-twin', size: 48 },
        { iconKey: 'edge-connectivity', size: 48 },
        { iconKey: 'edge-choreography', size: 48 },
        { iconKey: 'edge-analytics', size: 48 },
      ],
      position: 'center',
    },
    {
      id: 'management',
      title: $localize`:@@dspLayerManagementTitle:Management Cockpit`,
      description: $localize`:@@dspLayerManagementDescription:Cloud-based control and KPI monitoring.`,
      capabilities: [
        $localize`:@@dspManagementBullet1:Cloud-based control and KPI monitoring.`,
        $localize`:@@dspManagementBullet2:Governance, rules, and automation.`,
        $localize`:@@dspManagementBullet3:Digital twins enriched with enterprise data.`,
        $localize`:@@dspManagementBullet4:Analytics workloads for KPIs.`,
      ],
      actionId: 'management',
      logoIconKey: 'logo-dsp',
      secondaryLogoIconKey: 'logo-azure',
      position: 'right',
    },
  ];

  private readonly dspFeatures: string[] = [
    $localize`:@@dspGeneralBullet1:Interoperability for IT/OT landscapes with bi-directional topics.`,
    $localize`:@@dspGeneralBullet2:Decentralized control through object-oriented process choreography.`,
    $localize`:@@dspGeneralBullet3:Digital twins mirroring assets with contextual KPIs.`,
    $localize`:@@dspGeneralBullet4:Hybrid edge–cloud processing for latency-sensitive flows.`,
    $localize`:@@dspGeneralBullet5:Built-in Industry 4.0 capabilities (IIoT, AI, analytics).`,
  ];

  private readonly layoutInfo$: Observable<LayoutViewModel>;

  private moduleOverview$!: Observable<ModuleOverviewState>;
  private configSnapshot$!: Observable<CcuConfigSnapshot>;
  private externalLinks$!: Observable<ExternalLinksSettings>;
  readonly selectedCell$ = this.selectedCellSubject.asObservable();

  viewModel$!: Observable<ConfigurationViewModel>;

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

  constructor(
    private readonly http: HttpClient,
    private readonly messageMonitor: MessageMonitorService,
    private readonly moduleNameService: ModuleNameService,
    private readonly environmentService: EnvironmentService,
    private readonly connectionService: ConnectionService,
    private readonly externalLinksService: ExternalLinksService,
    private readonly router: Router,
    private readonly route: ActivatedRoute,
    private readonly mappingService: ShopfloorMappingService,
    private readonly moduleHardwareService: ModuleHardwareService
  ) {
    this.externalLinks$ = this.externalLinksService.settings$;
    this.layoutInfo$ = this.http.get<ShopfloorLayoutConfig>('shopfloor/shopfloor_layout.json').pipe(
      tap((layout) => this.mappingService.initializeLayout(layout)),
      map((layout) => this.buildLayout(layout)),
      tap((layout) => {
        if (!this.selectedCellSubject.value && layout.cells.length > 0) {
          const firstModule = layout.cells.find((cell) => cell.kind === 'module');
          this.selectedCellSubject.next(firstModule?.id ?? layout.cells[0]?.id ?? null);
        }
      }),
      shareReplay({ bufferSize: 1, refCount: true })
    );
    this.initializeStreams();
  }

  selectCell(cellId: string): void {
    this.selectedCellSubject.next(cellId);
  }

  onCellSelected(event: { id: string; kind: LayoutCellKind }): void {
    this.selectCell(event.id);
  }

  onCellDoubleClick(event: { id: string; kind: LayoutCellKind }): void {
    console.info('[configuration-tab] double click placeholder', event);
  }

  get factoryIcon(): string {
    return this.resolveAssetPath(
      SHOPFLOOR_ASSET_MAP['FACTORY_CONFIGURATION'] ?? SHOPFLOOR_ASSET_MAP['SHOPFLOOR_LAYOUT']
    );
  }

  get parametersIcon(): string {
    return this.resolveAssetPath(
      SHOPFLOOR_ASSET_MAP['PARAMETER_CONFIGURATION'] ?? SHOPFLOOR_ASSET_MAP['CONFIGURATION']
    );
  }

  /**
   * Get icon path from icon key (for DetailItem icons)
   * @param iconKey Icon key (e.g., 'opc-ua-station', 'txt-controller')
   * @returns Icon path or empty string if not found
   */
  getIconPath(iconKey?: string): string {
    if (!iconKey) {
      return '';
    }
    return getIconPath(iconKey as any);
  }

  private buildLayout(layout: ShopfloorLayoutConfig): LayoutViewModel {
    const baseWidth = 200;
    const baseHeight = 200;
    const columns = Math.max(1, Math.round(layout.metadata.canvas.width / baseWidth));
    const rows = Math.max(1, Math.round(layout.metadata.canvas.height / baseHeight));

    const moduleCells = layout.cells
      .filter((cell) => cell.role === 'module')
      .map((cell) =>
        this.createLayoutCell(cell, baseWidth, baseHeight, {
          id: cell.id,
          label: cell.show_name === false ? cell.id : cell.name ?? cell.id,
          kind: 'module',
          icon: this.resolveAssetPath(
            SHOPFLOOR_ASSET_MAP[cell.icon ?? cell.name ?? cell.id] ?? SHOPFLOOR_ASSET_MAP[cell.name ?? cell.id] ?? ''
          ),
          serialNumber: cell.serial_number,
          type: cell.name ?? cell.id,
          tooltip: cell.serial_number
            ? `${cell.name ?? cell.id} • ${cell.serial_number}`
            : `${cell.name ?? cell.id} • ${$localize`:@@configurationNoSerial:No serial`}`,
        })
      );

    const fixedCells = layout.cells
      .filter((cell) => cell.role === 'company' || cell.role === 'software')
      .map((cell) =>
        this.createLayoutCell(cell, baseWidth, baseHeight, {
          id: cell.id,
          label: cell.name ?? cell.id,
          kind: 'fixed',
          icon: this.resolveAssetPath(
            SHOPFLOOR_ASSET_MAP[cell.icon ?? cell.name ?? cell.id] ?? SHOPFLOOR_ASSET_MAP[cell.name ?? cell.id] ?? ''
          ),
          tooltip: cell.name ?? cell.id,
          background: cell.background_color,
          type: cell.name ?? cell.id,
        })
      );

    return {
      columns,
      rows,
      cells: [...moduleCells, ...fixedCells],
    };
  }

  private createLayoutCell(
    cell: ShopfloorCellConfig,
    baseWidth: number,
    baseHeight: number,
    meta: Omit<LayoutCell, 'row' | 'column' | 'rowSpan' | 'columnSpan'>
  ): LayoutCell {
    const column = Math.max(0, Math.floor(cell.position.x / baseWidth));
    const row = Math.max(0, Math.floor(cell.position.y / baseHeight));
    const columnSpan = Math.max(1, Math.round(cell.size.w / baseWidth));
    const rowSpan = Math.max(1, Math.round(cell.size.h / baseHeight));
    const iconKey = cell.icon ?? cell.name ?? cell.id;

    return {
      ...meta,
      row,
      column,
      rowSpan,
      columnSpan,
      icon: meta.icon || this.resolveAssetPath(SHOPFLOOR_ASSET_MAP[iconKey] ?? iconKey),
      position: cell.position,
      size: cell.size,
    };
  }

  private buildSelectedDetails(
    cell: (LayoutCell & { isSelected?: boolean }) | null,
    overview: ModuleOverviewState
  ): SelectedDetailView {
    if (!cell) {
      return {
        title: $localize`:@@configurationNoSelection:Select a module or position`,
        items: [],
      };
    }

    if (cell.kind === 'module') {
      const moduleDetails =
        overview.modules[cell.serialNumber ?? cell.id] ??
        overview.modules[cell.id] ??
        (cell.serialNumber ? overview.modules[cell.serialNumber] : undefined);

      const moduleType = moduleDetails?.subType ?? cell.type ?? 'UNKNOWN';
      const moduleDisplay = this.moduleNameService.getModuleDisplayName(moduleType);

      const items: DetailItem[] = [
        {
          label: $localize`:@@configurationNameLabel:Name`,
          value: moduleDisplay.fullName,
        },
        {
          label: this.serialLabel,
          value: moduleDetails?.id ?? cell.serialNumber ?? this.unknownLabel,
        },
        {
          label: $localize`:@@configurationIconLabel:Icon`,
          value: cell.type ?? this.unknownLabel,
        },
        {
          label: this.gridPositionLabel,
          value: this.formatGridPosition(cell),
        },
        {
          label: this.cellPositionLabel,
          value: this.formatCellPosition(cell),
        },
        {
          label: this.cellDimensionLabel,
          value: this.formatCellDimension(cell),
        },
      ];

      // Prepare OPC-UA and TXT Controller sections separately
      const opcUaItems: DetailItem[] = [];
      const txtControllerItems: DetailItem[] = [];
      let hasOpcUaStation = false;
      let hasTxtController = false;
      
      if (cell.serialNumber) {
        const hardwareConfig = this.moduleHardwareService.getModuleHardwareConfig(cell.serialNumber);
        
        if (hardwareConfig) {
          // OPC-UA Station Information (only if available)
          if (hardwareConfig.opc_ua_station) {
            hasOpcUaStation = true;
            opcUaItems.push({
              label: $localize`:@@configurationOpcUaEndpoint:OPC-UA Endpoint`,
              value: hardwareConfig.opc_ua_station.endpoint,
            });
            opcUaItems.push({
              label: $localize`:@@configurationOpcUaIpAddress:OPC-UA IP Address`,
              value: hardwareConfig.opc_ua_station.ip_address,
            });
            if (hardwareConfig.opc_ua_station.description) {
              opcUaItems.push({
                label: $localize`:@@configurationOpcUaDescription:OPC-UA Description`,
                value: hardwareConfig.opc_ua_station.description,
              });
            }
          }

          // TXT Controller Information (only if available)
          const txtControllers = hardwareConfig.txt_controllers ?? [];
          if (txtControllers.length > 0) {
            hasTxtController = true;
            txtControllers.forEach((txt, index) => {
              const suffix = txtControllers.length > 1 ? ` ${index + 1}` : '';
              txtControllerItems.push({
                label: `${$localize`:@@configurationTxtControllerName:TXT Controller Name`}${suffix}`,
                value: `${txt.name} (${txt.id})`,
              });
              txtControllerItems.push({
                label: `${$localize`:@@configurationTxtControllerIp:TXT Controller IP`}${suffix}`,
                value: `${txt.ip_address} ${$localize`:@@configurationTxtControllerIpNote:(DHCP)`}`,
              });
              if (txt.description) {
                txtControllerItems.push({
                  label: `${$localize`:@@configurationTxtControllerDescription:TXT Controller Description`}${suffix}`,
                  value: txt.description,
                });
              }
            });
          }
        }
      }

      return {
        title: moduleDisplay.fullName,
        subtitle: `${moduleDisplay.id}${moduleDetails?.subType ? ` • ${moduleDetails.subType}` : ''}`,
        items,
        moduleType: moduleType,
        icon: cell.icon,
        iconName: cell.type,
        opcUaItems: hasOpcUaStation ? opcUaItems : undefined,
        txtControllerItems: hasTxtController ? txtControllerItems : undefined,
        hasOpcUaStation,
        hasTxtController,
      };
    }

    const normalizedKey = (cell.type ?? cell.label ?? '').toUpperCase();
    const info =
      this.fixedPositionDetails[cell.id] ??
      this.fixedPositionDetails[cell.label] ??
      this.fixedPositionDetails[normalizedKey];
    if (info) {
      return {
        title: info.title,
        subtitle: info.subtitle,
        items: [
          ...info.items,
          { label: this.gridPositionLabel, value: this.formatGridPosition(cell) },
          { label: this.cellPositionLabel, value: this.formatCellPosition(cell) },
          { label: this.cellDimensionLabel, value: this.formatCellDimension(cell) },
          { label: $localize`:@@configurationIconLabel:Icon`, value: cell.type ?? this.unknownLabel },
        ],
        icon: cell.icon,
        iconName: cell.type,
      };
    }

    return {
      title: cell.label,
      items: [
        { label: this.gridPositionLabel, value: this.formatGridPosition(cell) },
        { label: this.cellPositionLabel, value: this.formatCellPosition(cell) },
        { label: this.cellDimensionLabel, value: this.formatCellDimension(cell) },
        { label: $localize`:@@configurationIconLabel:Icon`, value: cell.type ?? this.unknownLabel },
      ],
      icon: cell.icon,
      iconName: cell.type,
    };
  }

  private buildParameterCards(config: CcuConfigSnapshot): ParameterCardView[] {
    const durations = config.productionDurations ?? {};
    const workpieceIcons: Record<string, string> = {
      BLUE: ICONS.shopfloor.workpieces.blue.product,
      WHITE: ICONS.shopfloor.workpieces.white.product,
      RED: ICONS.shopfloor.workpieces.red.product,
    };

    const durationItems: ParameterItemView[] = ['BLUE', 'WHITE', 'RED'].map((type) => ({
      label:
        type === 'BLUE'
          ? $localize`:@@configurationBlueDuration:Blue Workpiece`
          : type === 'WHITE'
          ? $localize`:@@configurationWhiteDuration:White Workpiece`
          : $localize`:@@configurationRedDuration:Red Workpiece`,
      value: durations?.[type] != null ? `${durations[type]} ${$localize`:@@configurationSecondsLabel:s`}` : this.unknownLabel,
      icon: workpieceIcons[type],
    }));

    const productionSettingsItems: ParameterItemView[] = [
      {
        label: $localize`:@@configurationMaxParallelOrders:Max Parallel Orders`,
        value:
          config.productionSettings?.maxParallelOrders != null
            ? String(config.productionSettings.maxParallelOrders)
            : this.unknownLabel,
      },
    ];

    const ftsItems: ParameterItemView[] = [
      {
        label: $localize`:@@configurationChargeThreshold:Charge Threshold (%)`,
        value:
          config.ftsSettings?.chargeThresholdPercent != null
            ? `${config.ftsSettings.chargeThresholdPercent}%`
            : this.unknownLabel,
      },
    ];

    return [
      {
        title: $localize`:@@configurationProductionDurations:Production Durations`,
        icon: 'assets/svg/ui/heading-production.svg',
        description: $localize`:@@configurationProductionDurationsDescription:Configured target durations for each workpiece colour`,
        items: durationItems,
      },
      {
        title: $localize`:@@configurationProductionSettings:Production Settings`,
        icon: this.resolveAssetPath(
          SHOPFLOOR_ASSET_MAP['PRODUCTION_SETTINGS'] ?? SHOPFLOOR_ASSET_MAP['CONFIGURATION']
        ),
        description: $localize`:@@configurationProductionSettingsDescription:Global production parameters for the CCU`,
        items: productionSettingsItems,
      },
      {
        title: $localize`:@@configurationFtsSettings:AGV Settings`,
        icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['FTS']),
        description: $localize`:@@configurationFtsSettingsDescription:AGV system thresholds`,
        items: ftsItems,
      },
    ];
  }

  private resolveAssetPath(path?: string): string {
    const fallback = SHOPFLOOR_ASSET_MAP['QUESTION'] ?? '';
    const candidate = path && path.length > 0 ? path : fallback;
    const normalized = candidate.startsWith('/') ? candidate.slice(1) : candidate;
    if (normalized) {
      return normalized;
    }
    return fallback.startsWith('/') ? fallback.slice(1) : fallback;
  }

  private formatGridPosition(cell: LayoutCell): string {
    return `R${cell.row + 1} • C${cell.column + 1}`;
  }

  private formatCellPosition(cell: LayoutCell): string {
    if (!cell.position) {
      return this.unknownLabel;
    }
    return `x: ${cell.position.x}, y: ${cell.position.y}`;
  }

  private formatCellDimension(cell: LayoutCell): string {
    if (!cell.size) {
      return this.unknownLabel;
    }
    return `w: ${cell.size.w}, h: ${cell.size.h}`;
  }

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  openExternalLink(url: string): void {
    if (!url) {
      return;
    }
    // If URL starts with '/', treat it as internal route and navigate
    if (url.startsWith('/')) {
      // Get current locale from route
      const locale = this.route.snapshot.paramMap.get('locale') || 'en';
      // Build full path with locale prefix
      const fullPath = `/${locale}${url}`;
      this.router.navigateByUrl(fullPath);
    } else {
      // External URL - open in new tab
      window.open(url, '_blank', 'noreferrer noopener');
    }
  }

  getDspActionMessage(): Observable<MonitoredMessage | null> {
    return this.messageMonitor.getLastMessage('dsp/drill/action');
  }

  getChangeLightValue(msg: MonitoredMessage | null): string | null {
    if (!msg || !msg.payload) {
      return null;
    }
    try {
      const payload = typeof msg.payload === 'object' && msg.payload !== null
        ? msg.payload as { command?: string; value?: string }
        : JSON.parse(String(msg.payload));
      
      if (payload.command === 'changeLight' && payload.value) {
        return payload.value;
      }
    } catch (error) {
      console.error('[configuration] Failed to parse DSP action message:', error);
    }
    return null;
  }

  formatTimestamp(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('de-DE', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch {
      return timestamp;
    }
  }

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
          this.initializeStreams();
          if (environment.key === 'mock') {
            void this.loadFixture(this.activeFixture);
          }
        })
    );

    if (this.isMockMode) {
      void this.loadFixture(this.activeFixture);
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  async loadFixture(fixture: OrderFixtureName): Promise<void> {
    if (!this.isMockMode) {
      return; // Don't load fixtures in live/replay mode
    }
    this.activeFixture = fixture;
    try {
      // Use config-default preset (focused on configuration data)
      await this.dashboard.loadTabFixture('config-default');
      const streams = this.dashboard.streams;
      this.bindStreams(streams);
    } catch (error) {
      console.warn('Failed to load configuration fixture', fixture, error);
    }
  }

  /**
   * Legacy no-op for tests: Drill Action fixture handling moved out; keep method to satisfy specs.
   */
  async loadDrillActionFixture(): Promise<void> {
    return;
  }

  private initializeStreams(): void {
    const controller = getDashboardController();
    this.dashboard = controller;
    this.activeFixture = controller.getCurrentFixture();
    this.bindStreams();
  }

  private bindStreams(streams?: DashboardStreamSet): void {
    this.moduleOverview$ = (streams?.moduleOverview$ ?? this.dashboard.streams.moduleOverview$).pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Pattern enforcement: getLastMessage with filter, map, startWith in pipe chain
    // Then merge with dashboard.streams.config$
    const lastConfig = this.messageMonitor.getLastMessage<CcuConfigSnapshot>('ccu/state/config').pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => msg!.payload),
      startWith({} as CcuConfigSnapshot)
    );

    // Pattern enforcement: merge(lastConfig, this.dashboard.streams.config$)
    this.configSnapshot$ = merge(lastConfig, streams?.config$ ?? this.dashboard.streams.config$).pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );

    this.viewModel$ = combineLatest([
      this.layoutInfo$,
      this.moduleOverview$,
      this.selectedCell$,
      this.configSnapshot$,
      this.externalLinks$,
    ]).pipe(
      map(([layout, overview, selectedCellId, config, links]) => {
        const cells = layout.cells.map((cell) => ({
          ...cell,
          isSelected: cell.id === selectedCellId,
        }));

        const selectedCell =
          cells.find((cell) => cell.id === selectedCellId) ?? (cells.length ? cells[0] : null);

        const selection = this.buildSelectedDetails(selectedCell, overview);
        const detailPanel = this.buildDetailPanel(selectedCell, overview, links);
        const parameterCards = this.buildParameterCards(config);

        const highlightModules: string[] = [];
        const highlightFixed: string[] = [];

        if (selectedCell) {
          if (selectedCell.kind === 'module') {
            highlightModules.push(selectedCell.id);
            if (selectedCell.type) {
              highlightModules.push(selectedCell.type);
            }
            if (selectedCell.serialNumber) {
              highlightModules.push(`serial:${selectedCell.serialNumber}`);
            }
          } else if (selectedCell.kind === 'fixed') {
            highlightFixed.push(selectedCell.id);
            if (selectedCell.type) {
              highlightFixed.push(selectedCell.type);
            }
          }
        }

        const badgeText = $localize`:@@configurationBadgeShopfloor:SHOPFLOOR LAYOUT`;
        const infoText = selectedCell
          ? selectedCell.kind === 'module'
            ? (() => {
                const moduleDisplay = this.moduleNameService.getModuleDisplayName(selectedCell.type ?? selectedCell.label);
                return `Module ${moduleDisplay.fullName}`;
              })()
            : $localize`:@@configurationInfoArea:Area ${selectedCell.label}`
          : $localize`:@@configurationInfoDefault:Shopfloor layout overview`;

        return {
          layout: {
            columns: layout.columns,
            rows: layout.rows,
            cells,
          },
          selection,
          detailPanel,
          parameterCards,
          highlightModules,
          highlightFixed,
          badgeText,
          infoText,
        };
      }),
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  private buildDetailPanel(
    selectedCell: (LayoutCell & { isSelected?: boolean }) | null,
    overview: ModuleOverviewState,
    _links: ExternalLinksSettings
  ): DetailPanelView {
    if (!selectedCell) {
      return { kind: 'default', selection: this.buildSelectedDetails(null, overview) };
    }

    return {
      kind: 'default',
      selection: this.buildSelectedDetails(selectedCell, overview),
    };
  }

  private buildDspDetailView(links: ExternalLinksSettings): DspDetailView {
    const actions: DspActionLink[] = [
      {
        id: 'analytics',
        label: $localize`:@@dspActionAnalytics:Open BP Analytical Application`,
        description: $localize`:@@dspActionAnalyticsDescription:Switch to the analytics dashboard (BP Analytical Application) in a new window.`,
        url: links.grafanaDashboardUrl,
      },
      {
        id: 'smartfactory',
        label: $localize`:@@dspActionSmartfactory:Open DSP SmartFactory Dashboard`,
        description: $localize`:@@dspActionSmartfactoryDescription:Navigate to the SmartFactory Dashboard in a new tab.`,
        url: links.smartfactoryDashboardUrl,
      },
      {
        id: 'edge',
        label: $localize`:@@dspActionEdge:Open DSP Edge`,
        description: $localize`:@@dspActionEdgeDescription:Launch the configured DSP Edge endpoint in a new tab.`,
        url: links.dspControlUrl,
      },
      {
        id: 'management',
        label: $localize`:@@dspActionManagement:Open DSP Management Cockpit`,
        description: $localize`:@@dspActionManagementDescription:Navigate to the DSP Management Cockpit for KPI and workflow management.`,
        url: links.managementCockpitUrl,
      },
    ];

    const resources = [
      {
        label: $localize`:@@dspResourceOrbisWebsite:ORBIS website`,
        url: 'https://www.orbis.de',
      },
      {
        label: $localize`:@@dspResourceAward:Factory Innovation Award 2024`,
        url: 'https://factory-innovation-award.de',
      },
    ];

    const businessProcesses = [
      {
        id: 'shopfloor',
        label: $localize`:@@dspBusinessShopfloor:Shopfloor`,
        icon: this.resolveAssetPath(DETAIL_ASSET_MAP.DSP_BUSINESS_SAP),
      },
      {
        id: 'cloud-apps',
        label: $localize`:@@dspBusinessCloudApps:Cloud Applications`,
        icon: this.resolveAssetPath(DETAIL_ASSET_MAP.DSP_BUSINESS_CLOUD),
      },
      {
        id: 'analytics',
        label: $localize`:@@dspBusinessAnalytics:Analytics Applications`,
        icon: this.resolveAssetPath(DETAIL_ASSET_MAP.DSP_BUSINESS_ANALYTICS),
        actionId: 'grafana',
      },
      {
        id: 'data-lake',
        label: $localize`:@@dspBusinessDataLake:Data Lake`,
        icon: this.resolveAssetPath(DETAIL_ASSET_MAP.DSP_BUSINESS_DATA_LAKE),
      },
    ];

    const shopfloorPlatforms = [
      {
        label: $localize`:@@dspPlatformUnknown:Additional Integration`,
        icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['QUESTION']),
      },
      {
        label: $localize`:@@dspPlatformFts:FTS`,
        icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['FTS']),
      },
    ];

    const shopfloorSystems = [
      {
        label: $localize`:@@dspDeviceDps:DPS`,
        icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS']),
      },
      {
        label: $localize`:@@dspDeviceHbw:HBW`,
        icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['HBW']),
      },
      {
        label: $localize`:@@dspDeviceMill:Mill Station`,
        icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['MILL']),
      },
      {
        label: $localize`:@@dspDeviceDrill:Drill Station`,
        icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DRILL']),
      },
      {
        label: $localize`:@@dspDeviceAiqs:AIQS`,
        icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['AIQS']),
      },
    ];

    return {
      architecture: this.dspArchitecture,
      features: this.dspFeatures,
      actions,
      resources,
      businessProcesses,
      shopfloorPlatforms,
      shopfloorSystems,
      analyticsUrl: links.grafanaDashboardUrl,
      smartfactoryDashboardUrl: links.smartfactoryDashboardUrl,
      edgeUrl: links.dspControlUrl,
      managementUrl: links.managementCockpitUrl,
    };
  }

  private normalizeCellKey(cell: Pick<LayoutCell, 'id' | 'label' | 'type'>): string {
    return (cell.type ?? cell.label ?? cell.id ?? '').toUpperCase();
  }

}

