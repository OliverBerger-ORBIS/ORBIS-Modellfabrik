import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import type { CcuConfigSnapshot, ModuleOverviewState } from '@omf3/entities';
import { SHOPFLOOR_ASSET_MAP, type OrderFixtureName } from '@omf3/testing-fixtures';
import { BehaviorSubject, type Observable, combineLatest, merge, Subscription } from 'rxjs';
import { map, shareReplay, tap, filter, startWith, distinctUntilChanged } from 'rxjs/operators';
import { getDashboardController, type DashboardStreamSet } from '../mock-dashboard';
import { MessageMonitorService, MonitoredMessage } from '../services/message-monitor.service';
import { ModuleNameService } from '../services/module-name.service';
import { ShopfloorMappingService } from '../services/shopfloor-mapping.service';
import { EnvironmentService } from '../services/environment.service';
import { ConnectionService } from '../services/connection.service';
import { ShopfloorPreviewComponent } from '../components/shopfloor-preview/shopfloor-preview.component';
import { OrbisDetailComponent } from '../components/orbis-detail/orbis-detail.component';
import { DspDetailComponent } from '../components/dsp-detail/dsp-detail.component';
import { DspArchitectureComponent } from '../components/dsp-architecture/dsp-architecture.component';
import type { ShopfloorLayoutConfig, ShopfloorCellConfig } from '../components/shopfloor-preview/shopfloor-layout.types';
import { ExternalLinksService, type ExternalLinksSettings } from '../services/external-links.service';
import { ICONS } from '../shared/icons/icon.registry';
import {
  type DetailItem,
  type SelectedDetailView,
  type DetailPanelView,
  type OrbisDetailView,
  type DspDetailView,
  type OrbisPhaseDefinition,
  type OrbisUseCaseDefinition,
  type OrbisPhaseView,
  type OrbisUseCaseView,
  type DspArchitectureLayer,
  type DspActionLink,
} from './configuration-detail.types';
import { DETAIL_ASSET_MAP, getAssetPath } from '../assets/detail-asset-map';

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
  imports: [CommonModule, ShopfloorPreviewComponent, OrbisDetailComponent, DspDetailComponent, DspArchitectureComponent],
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
  readonly positionLabel = $localize`:@@configurationPositionLabel:Position`;

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

  private readonly orbisPhases: OrbisPhaseDefinition[] = [
    {
      id: 'phase1',
      title: $localize`:@@orbisPhase1Title:Phase 1 • Data Foundation & Connectivity`,
      summary: $localize`:@@orbisPhase1Summary:Connect machines, sensors, ERP, MES, and quality systems.`,
      activities: [
        $localize`:@@orbisPhase1Activity1:Connect machines, sensors, ERP, MES, and quality systems.`,
        $localize`:@@orbisPhase1Activity2:Standardize data via OPC UA, MQTT, and ISA-95.`,
        $localize`:@@orbisPhase1Activity3:Build data lake architecture (Azure Data Lake, SAP Edge, IoT Hub).`,
        $localize`:@@orbisPhase1Activity4:Ensure secure, scalable data ingestion pipelines.`,
      ],
      outcome: $localize`:@@orbisPhase1Outcome:End-to-end visibility and data availability.`,
    },
    {
      id: 'phase2',
      title: $localize`:@@orbisPhase2Title:Phase 2 • Data Integration & Modeling`,
      summary: $localize`:@@orbisPhase2Summary:Combine OT + IT data into a single semantic layer.`,
      activities: [
        $localize`:@@orbisPhase2Activity1:Combine OT + IT data into a single semantic layer.`,
        $localize`:@@orbisPhase2Activity2:Establish master data management and governance.`,
        $localize`:@@orbisPhase2Activity3:Model production, inventory, and quality data relationships.`,
        $localize`:@@orbisPhase2Activity4:Deploy SAP Datasphere, Azure Synapse, or Databricks for harmonization.`,
      ],
      outcome: $localize`:@@orbisPhase2Outcome:Trusted, consistent single source of truth.`,
    },
    {
      id: 'phase3',
      title: $localize`:@@orbisPhase3Title:Phase 3 • Advanced Analytics & Intelligence`,
      summary: $localize`:@@orbisPhase3Summary:Connect analytics outputs to workflows and RPA bots.`,
      activities: [
        $localize`:@@orbisPhase3Activity1:Connect analytics outputs to workflows and RPA bots.`,
        $localize`:@@orbisPhase3Activity2:Automate repetitive tasks across SAP and Azure ecosystems.`,
        $localize`:@@orbisPhase3Activity3:Use event-driven triggers for maintenance, quality, or logistics actions.`,
        $localize`:@@orbisPhase3Activity4:Deploy Power Automate, SAP Build Process Automation, Logic Apps.`,
      ],
      outcome: $localize`:@@orbisPhase3Outcome:Closed-loop automation, faster reaction time, reduced manual effort.`,
    },
    {
      id: 'phase4',
      title: $localize`:@@orbisPhase4Title:Phase 4 • Automation & Orchestration`,
      summary: $localize`:@@orbisPhase4Summary:Connect analytics outputs to workflows and RPA bots.`,
      activities: [
        $localize`:@@orbisPhase4Activity1:Connect analytics outputs to workflows and RPA bots.`,
        $localize`:@@orbisPhase4Activity2:Automate repetitive tasks across SAP and Azure ecosystems.`,
        $localize`:@@orbisPhase4Activity3:Use event-driven triggers for maintenance, quality, or logistics actions.`,
        $localize`:@@orbisPhase4Activity4:Deploy Power Automate, SAP Build Process Automation, Logic Apps.`,
      ],
      outcome: $localize`:@@orbisPhase4Outcome:Closed-loop automation, faster reaction time, reduced manual effort.`,
    },
    {
      id: 'phase5',
      title: $localize`:@@orbisPhase5Title:Phase 5 • Autonomous & Adaptive Enterprise`,
      summary: $localize`:@@orbisPhase5Summary:Deploy agentic AI to reason, plan, and act autonomously.`,
      activities: [
        $localize`:@@orbisPhase5Activity1:Deploy agentic AI to reason, plan, and act autonomously.`,
        $localize`:@@orbisPhase5Activity2:Integrate digital twins, LLMs, and reinforcement learning.`,
        $localize`:@@orbisPhase5Activity3:Continuously self-optimize production, energy, and supply chain flows.`,
        $localize`:@@orbisPhase5Activity4:Enable AI copilots for operators, planners, and engineers.`,
      ],
      outcome: $localize`:@@orbisPhase5Outcome:Self-learning, adaptive, intelligent manufacturing enterprise.`,
    },
  ];

  private readonly orbisUseCases: OrbisUseCaseDefinition[] = [
    {
      id: 'data-aggregation',
      title: $localize`:@@orbisUseCaseAggregationTitle:Data Aggregation`,
      description: $localize`:@@orbisUseCaseAggregationDescription:Harmonize business, shopfloor, and sensor data for a single contextual production view.`,
      highlights: [
        $localize`:@@orbisUseCaseAggregationHighlight1:ERP order streams enriched with MES execution events and machine states.`,
        $localize`:@@orbisUseCaseAggregationHighlight2:Machine telemetry correlated with single-part identifiers (NFC) and process parameters.`,
        $localize`:@@orbisUseCaseAggregationHighlight3:Environmental data (temperature, humidity, air quality) linked to production sequences and genealogy.`,
        $localize`:@@orbisUseCaseAggregationHighlight4:Process optimization via analysis of cycle times, takt variability, energy consumption, and machine utilization.`,
      ],
      icon: 'assets/svg/orbis/consolidate.svg',
    },
    {
      id: 'track-trace',
      title: $localize`:@@orbisUseCaseTrackTraceTitle:Track & Trace`,
      description: $localize`:@@orbisUseCaseTrackTraceDescription:Complete object genealogy with real-time traceability and quality correlation.`,
      highlights: [
        $localize`:@@orbisUseCaseTrackTraceHighlight1:Object-level location tracking across conveyors, modules, and high-bay storage (HBW).`,
        $localize`:@@orbisUseCaseTrackTraceHighlight2:Correlation of process parameters (DRILL, MILL, AIQS) with ERP/MES customer orders.`,
        $localize`:@@orbisUseCaseTrackTraceHighlight3:Sensor and telemetry data linked to quality outcomes, rework decisions, and root-cause analysis.`,
      ],
      icon: 'assets/svg/orbis/integration.svg',
    },
    {
      id: 'predictive-maintenance',
      title: $localize`:@@orbisUseCasePredictiveTitle:Predictive Maintenance`,
      description: $localize`:@@orbisUseCasePredictiveDescription:AI-driven detection of anomalies, wear patterns, and optimal service windows.`,
      highlights: [
        $localize`:@@orbisUseCasePredictiveHighlight1:Pattern recognition on spindle load, vibration, cycle duration, and energy usage.`,
        $localize`:@@orbisUseCasePredictiveHighlight2:Anomaly scoring with automated escalation to maintenance bots or SAP notifications.`,
        $localize`:@@orbisUseCasePredictiveHighlight3:Predictive forecasts feeding SAP maintenance plans, spare-part logistics, and operator guidance.`,
      ],
      icon: 'assets/svg/orbis/ai-algorithm.svg',
    },
    {
      id: 'process-optimization',
      title: $localize`:@@orbisUseCaseOptimizationTitle:Process Optimization`,
      description: $localize`:@@orbisUseCaseOptimizationDescription:Continuous optimization of manufacturing processes using real-time and historical data.`,
      highlights: [
        $localize`:@@orbisUseCaseOptimizationHighlight1:Bottleneck and cycle-time analysis across DRILL, MILL, AIQS, FTS, and HBW.`,
        $localize`:@@orbisUseCaseOptimizationHighlight2:Optimization of machine utilization, takt stability, and conveyor flow.`,
        $localize`:@@orbisUseCaseOptimizationHighlight3:Energy and resource optimization using spindle load, vibration, and consumption data.`,
        $localize`:@@orbisUseCaseOptimizationHighlight4:AI recommendations for parameters such as feed rate or spindle speed.`,
        $localize`:@@orbisUseCaseOptimizationHighlight5:Simulation of what-if scenarios before applying changes to the physical line.`,
        $localize`:@@orbisUseCaseOptimizationHighlight6:Closed-loop improvements via DSP executors and MES/DSP workflows.`,
      ],
      icon: 'assets/svg/orbis/database-management.svg',
    },
  ];

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
        { iconKey: 'edge-workflow', size: 48 },
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
  private readonly orbisPhaseSubject = new BehaviorSubject<string | null>(null);
  private readonly orbisUseCaseExpandedSubject = new BehaviorSubject<Set<string>>(new Set());

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
  drillActionActive = false;

  constructor(
    private readonly http: HttpClient,
    private readonly messageMonitor: MessageMonitorService,
    private readonly moduleNameService: ModuleNameService,
    private readonly environmentService: EnvironmentService,
    private readonly connectionService: ConnectionService,
    private readonly externalLinksService: ExternalLinksService,
    private readonly router: Router,
    private readonly route: ActivatedRoute,
    private readonly mappingService: ShopfloorMappingService
  ) {
    this.externalLinks$ = this.externalLinksService.settings$;
    this.layoutInfo$ = this.http.get<ShopfloorLayoutConfig>('shopfloor/shopfloor_layout.json').pipe(
      tap((layout) => this.mappingService.initializeLayout(layout)),
      map((layout) => this.buildLayout(layout)),
      tap((layout) => {
        if (!this.selectedCellSubject.value && layout.cells.length > 0) {
          // Default to DSP cell if available, otherwise first cell
          const dspCell = layout.cells.find(
            (cell) => cell.kind === 'fixed' && (cell.label === 'DSP' || cell.type === 'DSP')
          );
          this.selectedCellSubject.next(dspCell?.id ?? layout.cells[0]?.id ?? null);
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
          label: this.serialLabel,
          value: moduleDetails?.id ?? cell.serialNumber ?? this.unknownLabel,
        },
        {
          label: this.availabilityLabel,
          value: moduleDetails?.availability ?? this.unknownLabel,
        },
        {
          label: this.connectedLabel,
          value: moduleDetails ? (moduleDetails.connected ? this.yesLabel : this.noLabel) : this.unknownLabel,
        },
        {
          label: this.configuredLabel,
          value: moduleDetails ? (moduleDetails.configured ? this.yesLabel : this.noLabel) : this.unknownLabel,
        },
        {
          label: this.lastUpdateLabel,
          value: moduleDetails?.lastUpdate ?? this.unknownLabel,
        },
        {
          label: this.positionLabel,
          value: this.formatPosition(cell),
        },
      ];

      // Add DSP-Edge information for DRILL module
      if (moduleType === 'DRILL') {
        const dspActionMsg = this.messageMonitor.getLastMessage('dsp/drill/action');
        // Note: This is a synchronous call, but we need async data
        // We'll handle this in the template with async pipe
        items.push({
          label: $localize`:@@configurationDspEdgeControlled:Controlled by DSP Edge`,
          value: $localize`:@@configurationDspEdgeStatus:Loading status...`,
        });
      }

      return {
        title: moduleDisplay.fullName,
        subtitle: `${moduleDisplay.id}${moduleDetails?.subType ? ` • ${moduleDetails.subType}` : ''}`,
        items,
        moduleType: moduleType,
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
        items: [...info.items, { label: this.positionLabel, value: this.formatPosition(cell) }],
      };
    }

    return {
      title: cell.label,
      items: [{ label: this.positionLabel, value: this.formatPosition(cell) }],
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

  private formatPosition(cell: LayoutCell): string {
    return `R${cell.row + 1} • C${cell.column + 1}`;
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

  selectOrbisPhase(phaseId: string): void {
    if (!this.orbisPhases.some((phase) => phase.id === phaseId)) {
      return;
    }
    const current = this.orbisPhaseSubject.value;
    this.orbisPhaseSubject.next(current === phaseId ? null : phaseId);
  }

  toggleOrbisUseCase(useCaseId: string): void {
    if (!this.orbisUseCases.some((useCase) => useCase.id === useCaseId)) {
      return;
    }
    const next = new Set(this.orbisUseCaseExpandedSubject.value);
    if (next.has(useCaseId)) {
      next.delete(useCaseId);
    } else {
      next.add(useCaseId);
    }
    this.orbisUseCaseExpandedSubject.next(next);
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
      
      // Automatically load Drill Action fixture
      await this.loadDrillActionFixture();
    } catch (error) {
      console.warn('Failed to load configuration fixture', fixture, error);
    }
  }

  async loadDrillActionFixture(): Promise<void> {
    if (!this.isMockMode) {
      return; // Don't load fixtures in live/replay mode
    }
    this.drillActionActive = true;
    try {
      const { createDspActionFixtureStream } = await import('@omf3/testing-fixtures');
      const stream$ = createDspActionFixtureStream({
        intervalMs: 1000,
        loop: true,
      });
      // Subscribe to the stream and add messages directly to MessageMonitor
      const subscription = stream$.subscribe((message) => {
        try {
          const payload = typeof message.payload === 'string' 
            ? JSON.parse(message.payload) 
            : message.payload;
          this.messageMonitor.addMessage(message.topic, payload, message.timestamp);
        } catch (error) {
          console.error('[configuration] Failed to parse message payload:', error);
        }
      });
      // Store subscription to clean up later if needed
      // Note: This subscription will persist until component destruction
      // In a real implementation, you might want to manage this differently
    } catch (error) {
      console.error('[configuration] Failed to load drill action fixture:', error);
    }
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
      this.orbisPhaseSubject.asObservable(),
      this.orbisUseCaseExpandedSubject.asObservable(),
    ]).pipe(
      map(([layout, overview, selectedCellId, config, links, activePhaseId, expandedUseCases]) => {
        const cells = layout.cells.map((cell) => ({
          ...cell,
          isSelected: cell.id === selectedCellId,
        }));

        const selectedCell =
          cells.find((cell) => cell.id === selectedCellId) ?? (cells.length ? cells[0] : null);

        const selection = this.buildSelectedDetails(selectedCell, overview);
        const detailPanel = this.buildDetailPanel(
          selectedCell,
          overview,
          links,
          activePhaseId,
          expandedUseCases
        );
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
    links: ExternalLinksSettings,
    activePhaseId: string | null,
    expandedUseCases: Set<string>
  ): DetailPanelView {
    if (!selectedCell) {
      return { kind: 'default', selection: this.buildSelectedDetails(null, overview) };
    }

    if (selectedCell.kind === 'fixed') {
      const normalized = this.normalizeCellKey(selectedCell);
      if (normalized === 'ORBIS') {
        return {
          kind: 'orbis',
          view: this.buildOrbisDetailView(links, activePhaseId, expandedUseCases),
        };
      }
      if (normalized === 'DSP') {
        return {
          kind: 'dsp',
          view: this.buildDspDetailView(links),
        };
      }
    }

    return {
      kind: 'default',
      selection: this.buildSelectedDetails(selectedCell, overview),
    };
  }

  private buildOrbisDetailView(
    links: ExternalLinksSettings,
    activePhaseId: string | null,
    expandedUseCases: Set<string>
  ): OrbisDetailView {
    const activePhase = activePhaseId
      ? this.orbisPhases.find((phase) => phase.id === activePhaseId) ?? null
      : null;
    const phases: OrbisPhaseView[] = this.orbisPhases.map((phase) => ({
      ...phase,
      active: phase.id === activePhaseId,
    }));
    const useCases: OrbisUseCaseView[] = this.orbisUseCases.map((useCase) => ({
      ...useCase,
      expanded: expandedUseCases.has(useCase.id),
    }));

    return {
      phases,
      activePhase,
      useCases,
      websiteUrl: links.orbisWebsiteUrl,
    };
  }

  private buildDspDetailView(links: ExternalLinksSettings): DspDetailView {
    const actions: DspActionLink[] = [
      {
        id: 'edge',
        label: $localize`:@@dspActionEdge:Open EDGE control`,
        description: $localize`:@@dspActionEdgeDescription:Launch the configured EDGE endpoint in a new tab.`,
        url: links.dspControlUrl,
      },
      {
        id: 'management',
        label: $localize`:@@dspActionManagement:Open management cockpit`,
        description: $localize`:@@dspActionManagementDescription:Navigate to the cloud cockpit for KPI and workflow management.`,
        url: links.managementCockpitUrl,
      },
      {
        id: 'grafana',
        label: $localize`:@@dspActionGrafana:Open Grafana dashboard`,
        description: $localize`:@@dspActionGrafanaDescription:Switch to the analytics dashboard (Grafana) in a new window.`,
        url: links.grafanaDashboardUrl,
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
      edgeUrl: links.dspControlUrl,
      managementUrl: links.managementCockpitUrl,
      analyticsUrl: links.grafanaDashboardUrl,
      smartfactoryDashboardUrl: links.smartfactoryDashboardUrl,
    };
  }

  private normalizeCellKey(cell: Pick<LayoutCell, 'id' | 'label' | 'type'>): string {
    return (cell.type ?? cell.label ?? cell.id ?? '').toUpperCase();
  }

}

