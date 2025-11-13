import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import type { CcuConfigSnapshot, ModuleOverviewState } from '@omf3/entities';
import { SHOPFLOOR_ASSET_MAP } from '@omf3/testing-fixtures';
import { BehaviorSubject, type Observable, combineLatest } from 'rxjs';
import { map, shareReplay, switchMap, tap, startWith } from 'rxjs/operators';
import { getDashboardController } from '../mock-dashboard';
import { ShopfloorPreviewComponent } from '../components/shopfloor-preview/shopfloor-preview.component';

type GridTuple = [number, number];

interface ShopfloorModuleLayout {
  id: string;
  type: string;
  serialNumber?: string;
  position: GridTuple;
  cell_size?: GridTuple;
  show_label?: boolean;
}

interface ShopfloorFixedPositionLayout {
  id: string;
  type: string;
  position: GridTuple;
  cell_size?: GridTuple;
  background_color?: string;
}

interface ShopfloorLayout {
  grid: {
    rows: number;
    columns: number;
    cell_size?: string;
  };
  modules: ShopfloorModuleLayout[];
  fixed_positions: ShopfloorFixedPositionLayout[];
}

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

  private readonly moduleOverview$: Observable<ModuleOverviewState> = this.dashboard.streams$.pipe(
    map((streams) => streams.moduleOverview$),
    switchMap((stream$) => stream$),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  private readonly configSnapshot$: Observable<CcuConfigSnapshot> = this.dashboard.streams$.pipe(
    map((streams) => streams.config$),
    switchMap((stream$) => stream$.pipe(startWith({} as CcuConfigSnapshot))),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  readonly selectedCell$ = this.selectedCellSubject.asObservable();

  readonly viewModel$: Observable<ConfigurationViewModel>;

  constructor(private readonly http: HttpClient) {
    this.layoutInfo$ = this.http.get<ShopfloorLayout>('shopfloor/shopfloor_layout.json').pipe(
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
              highlightModules.push(selectedCell.serialNumber);
            }
          } else if (selectedCell.kind === 'fixed') {
            highlightFixed.push(selectedCell.id);
            if (selectedCell.type) {
              highlightFixed.push(selectedCell.type);
            }
          }
        }

        const badgeText = $localize`:@@configurationBadgeProduction:Production`;
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

  get factoryIcon(): string {
    return this.resolveAssetPath(
      SHOPFLOOR_ASSET_MAP['SHOPFLOOR_LAYOUT'] ?? SHOPFLOOR_ASSET_MAP['FACTORY_CONFIGURATION']
    );
  }

  get parametersIcon(): string {
    return this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['CONFIGURATION']);
  }

  private buildLayout(layout: ShopfloorLayout): LayoutViewModel {
    const [baseWidth, baseHeight] = this.parseCellSize(layout.grid.cell_size);
    const columns = layout.grid.columns ?? 1;
    const rows = layout.grid.rows ?? 1;

    const moduleCells = layout.modules.map((mod) =>
      this.createLayoutCell(mod.position, mod.cell_size, baseWidth, baseHeight, {
        id: mod.id,
        label: mod.show_label ? mod.id : mod.type,
        kind: 'module',
        icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP[mod.type] ?? SHOPFLOOR_ASSET_MAP[mod.id]),
        serialNumber: mod.serialNumber,
        type: mod.type,
        tooltip: mod.serialNumber
          ? `${mod.id} • ${mod.serialNumber}`
          : `${mod.id} • ${$localize`:@@configurationNoSerial:No serial`}`,
      })
    );

    const fixedCells = layout.fixed_positions.map((pos) =>
      this.createLayoutCell(pos.position, pos.cell_size, baseWidth, baseHeight, {
        id: pos.id,
        label: pos.type,
        kind: 'fixed',
        icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP[pos.type] ?? ''),
        tooltip: pos.type,
        background: pos.background_color,
      })
    );

    return {
      columns,
      rows,
      cells: [...moduleCells, ...fixedCells],
    };
  }

  private createLayoutCell(
    position: GridTuple,
    cellSize: GridTuple | undefined,
    baseWidth: number,
    baseHeight: number,
    meta: Omit<LayoutCell, 'row' | 'column' | 'rowSpan' | 'columnSpan'>
  ): LayoutCell {
    const column = position?.[1] ?? 0;
    const row = position?.[0] ?? 0;
    const targetWidth = cellSize?.[0] ?? baseWidth;
    const targetHeight = cellSize?.[1] ?? baseHeight;

    const columnSpan = Math.max(1, Math.round(targetWidth / baseWidth));
    const rowSpan = Math.max(1, Math.round(targetHeight / baseHeight));

    return {
      ...meta,
      row,
      column,
      rowSpan,
      columnSpan,
      icon: meta.icon || this.resolveAssetPath(SHOPFLOOR_ASSET_MAP[meta.id] ?? ''),
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
        icon: 'headings/dezentral.svg',
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

  private parseCellSize(cellSize?: string): [number, number] {
    if (!cellSize) {
      return [200, 200];
    }

    const [width, height] = cellSize.split('x').map((value) => Number.parseInt(value, 10));
    return [Number.isFinite(width) ? width : 200, Number.isFinite(height) ? height : 200];
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

