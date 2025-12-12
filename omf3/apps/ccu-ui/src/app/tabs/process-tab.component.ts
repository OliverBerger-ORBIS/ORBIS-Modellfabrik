import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import type { ProductionFlowMap } from '@omf3/entities';
import { SHOPFLOOR_ASSET_MAP, type OrderFixtureName } from '@omf3/testing-fixtures';
import { getDashboardController, type DashboardStreamSet } from '../mock-dashboard';
import { MessageMonitorService } from '../services/message-monitor.service';
import { ModuleNameService } from '../services/module-name.service';
import { EnvironmentService } from '../services/environment.service';
import { ConnectionService } from '../services/connection.service';
import type { Observable } from 'rxjs';
import { map, shareReplay, filter, startWith, distinctUntilChanged } from 'rxjs/operators';
import { merge, Subscription } from 'rxjs';
import { ICONS } from '../shared/icons/icon.registry';
import { resolveLegacyShopfloorPath } from '../shared/icons/legacy-shopfloor-map';

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

@Component({
  standalone: true,
  selector: 'app-process-tab',
  imports: [CommonModule],
  templateUrl: './process-tab.component.html',
  styleUrl: './process-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProcessTabComponent implements OnInit, OnDestroy {
  private dashboard = getDashboardController();
  private readonly subscriptions = new Subscription();
  private readonly defaultShopfloorIcon = resolveLegacyShopfloorPath('assets/svg/shopfloor/shared/question.svg');

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

  flows$!: Observable<ProductionFlowMap>;
  
  products$!: Observable<ProcessProductView[]>;

  constructor(
    private readonly messageMonitor: MessageMonitorService,
    private readonly moduleNameService: ModuleNameService,
    private readonly environmentService: EnvironmentService,
    private readonly connectionService: ConnectionService
  ) {
    this.initializeStreams();
  }

  readonly processIcon = ICONS.ui.processFlow;
  readonly startIcon = this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['HBW'] ?? 'assets/svg/shopfloor/stations/hbw-station.svg');
  readonly endIcons = [
    this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS_SQUARE1'] ?? 'assets/svg/shopfloor/systems/warehouse-system.svg'),
    this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS'] ?? 'assets/svg/shopfloor/stations/dps-station.svg'),
    this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS_SQUARE2'] ?? 'assets/svg/shopfloor/shared/order-tracking.svg'),
  ];
  readonly stepCountI18nMap: { [k: string]: string } = {
    '=0': $localize`:@@processNoSteps:No processing steps`,
    '=1': $localize`:@@processOneStep:1 Processing Step`,
    other: $localize`:@@processManySteps:# Processing Steps`,
  };
  readonly deleteIcon = '🗑️';

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

  private getModuleMeta(key: string): { label: string; icon: string } {
    return {
      label: this.moduleNameService.getModuleFullName(key),
      icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP[key as keyof typeof SHOPFLOOR_ASSET_MAP]),
    };
  }

  private resolveAssetPath(path?: string): string {
    const candidate = path && path.length > 0 ? path : this.defaultShopfloorIcon;
    return resolveLegacyShopfloorPath(candidate);
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
    const moduleMeta = this.getModuleMeta(key);

    return {
      id: `${key}-${index}`,
      label: moduleMeta.label,
      icon: moduleMeta.icon,
      isPlaceholder: false,
    };
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
      // Always use process-startup preset (only startup fixtures needed for Process tab)
      // The fixture parameter is kept for UI consistency, but we always load startup
      await this.dashboard.loadTabFixture('process-startup');
      const streams = this.dashboard.streams;
      this.bindStreams(streams);
    } catch (error) {
      console.warn('Failed to load process fixture', fixture, error);
    }
  }

  private initializeStreams(): void {
    const controller = getDashboardController();
    this.dashboard = controller;
    this.activeFixture = controller.getCurrentFixture();
    this.bindStreams();
  }

  private bindStreams(streams?: DashboardStreamSet): void {
    const lastFlows = this.messageMonitor.getLastMessage<ProductionFlowMap>('ccu/state/flows').pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => msg!.payload),
      startWith({} as ProductionFlowMap)
    );
    // Pattern enforcement: merge(lastFlows, this.dashboard.streams.flows$)
    this.flows$ = merge(lastFlows, streams?.flows$ ?? this.dashboard.streams.flows$).pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
    this.products$ = this.flows$.pipe(map((flows) => this.buildProductViews(flows)));
  }
}

