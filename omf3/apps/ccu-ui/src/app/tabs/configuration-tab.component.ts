import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import type { CcuConfigSnapshot, ModuleOverviewState } from '@omf3/entities';
import { SHOPFLOOR_ASSET_MAP } from '@omf3/testing-fixtures';
import { BehaviorSubject, type Observable, combineLatest } from 'rxjs';
import { map, shareReplay, tap, filter, startWith } from 'rxjs/operators';
import { merge } from 'rxjs';
import { getDashboardController } from '../mock-dashboard';
import { MessageMonitorService } from '../services/message-monitor.service';
import { ShopfloorPreviewComponent } from '../components/shopfloor-preview/shopfloor-preview.component';
import type { ShopfloorLayoutConfig, ShopfloorCellConfig } from '../components/shopfloor-preview/shopfloor-layout.types';

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

interface DetailItem {
  label: string;
  value: string;
}

interface SelectedDetailView {
  title: string;
  subtitle?: string;
  items: DetailItem[];
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
  parameterCards: ParameterCardView[];
  highlightModules: string[];
  highlightFixed: string[];
  badgeText: string;
  infoText: string;
}

@Component({
  standalone: true,
  selector: 'app-configuration-tab',
  imports: [CommonModule, ShopfloorPreviewComponent],
  templateUrl: './configuration-tab.component.html',
  styleUrl: './configuration-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ConfigurationTabComponent {
  private readonly dashboard = getDashboardController();
  private readonly selectedCellSubject = new BehaviorSubject<string | null>(null);

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
  };

  private readonly layoutInfo$: Observable<LayoutViewModel>;

  // Subscribe directly to dashboard streams - they already have shareReplay with startWith
  // Use refCount: false to keep streams alive even when no subscribers
  private readonly moduleOverview$: Observable<ModuleOverviewState> = this.dashboard.streams.moduleOverview$.pipe(
    shareReplay({ bufferSize: 1, refCount: false })
  );

  // Subscribe directly to dashboard streams - they already have shareReplay with startWith
  // Use refCount: false to keep streams alive even when no subscribers
  private readonly configSnapshot$: Observable<CcuConfigSnapshot>;

  readonly selectedCell$ = this.selectedCellSubject.asObservable();

  readonly viewModel$: Observable<ConfigurationViewModel>;

  constructor(
    private readonly http: HttpClient,
    private readonly messageMonitor: MessageMonitorService
  ) {
    // config$ doesn't have startWith in gateway layer, so merge MessageMonitor last value with dashboard stream
    const lastConfig = this.messageMonitor.getLastMessage<CcuConfigSnapshot>('ccu/state/config').pipe(
      map((msg) => {
        // If message exists and is valid, use it; otherwise return null
        if (msg !== null && msg.valid) {
          return msg.payload;
        }
        return null;
      }),
      // Only emit non-null values, but keep null for filter below
      startWith(null as CcuConfigSnapshot | null)
    );
    this.configSnapshot$ = merge(lastConfig, this.dashboard.streams.config$).pipe(
      filter((config): config is CcuConfigSnapshot => config !== null),
      shareReplay({ bufferSize: 1, refCount: false })
    );
    this.layoutInfo$ = this.http.get<ShopfloorLayoutConfig>('shopfloor/shopfloor_layout.json').pipe(
      map((layout) => this.buildLayout(layout)),
      tap((layout) => {
        if (!this.selectedCellSubject.value && layout.cells.length > 0) {
          this.selectedCellSubject.next(layout.cells[0]?.id ?? null);
        }
      }),
      shareReplay({ bufferSize: 1, refCount: true })
    );
    this.viewModel$ = combineLatest([
      this.layoutInfo$,
      this.moduleOverview$,
      this.selectedCell$,
      this.configSnapshot$,
    ]).pipe(
      map(([layout, overview, selectedCellId, config]) => {
        const cells = layout.cells.map((cell) => ({
          ...cell,
          isSelected: cell.id === selectedCellId,
        }));

        const selectedCell =
          cells.find((cell) => cell.id === selectedCellId) ?? (cells.length ? cells[0] : null);

        const selection = this.buildSelectedDetails(selectedCell, overview);
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
            ? $localize`:@@configurationInfoModule:Module ${selectedCell.label}`
            : $localize`:@@configurationInfoArea:Area ${selectedCell.label}`
          : $localize`:@@configurationInfoDefault:Shopfloor layout overview`;

        return {
          layout: {
            columns: layout.columns,
            rows: layout.rows,
            cells,
          },
          selection,
          parameterCards,
          highlightModules,
          highlightFixed,
          badgeText,
          infoText,
        };
      })
    );
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

      return {
        title: cell.label,
        subtitle: moduleDetails?.subType ?? cell.type ?? '',
        items: [
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
        ],
      };
    }

    const info = this.fixedPositionDetails[cell.id];
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
      BLUE: 'workpieces/blue_product.svg',
      WHITE: 'workpieces/white_product.svg',
      RED: 'workpieces/red_product.svg',
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
        icon: 'headings/maschine.svg',
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
        title: $localize`:@@configurationFtsSettings:FTS Settings`,
        icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['FTS']),
        description: $localize`:@@configurationFtsSettingsDescription:Driverless transport system thresholds`,
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
}

