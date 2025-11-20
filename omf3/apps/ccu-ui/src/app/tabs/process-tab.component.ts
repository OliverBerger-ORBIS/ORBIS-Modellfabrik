import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import type { ProductionFlowMap } from '@omf3/entities';
import { SHOPFLOOR_ASSET_MAP, type OrderFixtureName } from '@omf3/testing-fixtures';
import { getDashboardController } from '../mock-dashboard';
import { MessageMonitorService } from '../services/message-monitor.service';
import { ModuleNameService } from '../services/module-name.service';
import { EnvironmentService } from '../services/environment.service';
import type { Observable } from 'rxjs';
import { map, shareReplay, filter, startWith } from 'rxjs/operators';
import { merge } from 'rxjs';

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
export class ProcessTabComponent implements OnInit {
  private readonly dashboard = getDashboardController();

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

  // Subscribe directly to dashboard streams - they already have shareReplay with startWith
  // Use refCount: false to keep streams alive even when no subscribers
  flows$: Observable<ProductionFlowMap>;
  
  products$: Observable<ProcessProductView[]>;

  constructor(
    private readonly messageMonitor: MessageMonitorService,
    private readonly moduleNameService: ModuleNameService,
    private readonly environmentService: EnvironmentService
  ) {
    // flows$ doesn't have startWith in gateway layer, so merge MessageMonitor last value with dashboard stream
    const lastFlows = this.messageMonitor.getLastMessage<ProductionFlowMap>('ccu/state/flows').pipe(
      // Filter first: only process valid messages
      filter((msg) => msg !== null && msg.valid),
      // Map second: extract payload from valid messages
      map((msg) => msg!.payload),
      // StartWith last: provide empty state as fallback only if no valid message exists
      startWith({} as ProductionFlowMap)
    );
    this.flows$ = merge(lastFlows, this.dashboard.streams.flows$).pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
    
    this.products$ = this.flows$.pipe(map((flows) => this.buildProductViews(flows)));
  }

  readonly processIcon = 'headings/gang.svg';
  readonly startIcon = this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['HBW'] ?? '/shopfloor/stock.svg');
  readonly endIcons = [
    this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS_SQUARE1'] ?? '/shopfloor/warehouse.svg'),
    this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS'] ?? '/shopfloor/robot-arm.svg'),
    this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS_SQUARE2'] ?? '/shopfloor/order-tracking.svg'),
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
      productIcon: 'workpieces/blue_product.svg',
      product3dIcon: 'workpieces/blue_3dim.svg',
      backgroundClass: 'bg-blue',
    },
    WHITE: {
      label: $localize`:@@processWorkpieceWhite:White`,
      dotClass: 'white',
      productIcon: 'workpieces/white_product.svg',
      product3dIcon: 'workpieces/white_3dim.svg',
      backgroundClass: 'bg-white',
    },
    RED: {
      label: $localize`:@@processWorkpieceRed:Red`,
      dotClass: 'red',
      productIcon: 'workpieces/red_product.svg',
      product3dIcon: 'workpieces/red_3dim.svg',
      backgroundClass: 'bg-red',
    },
  } as const;

  private getModuleMeta(key: string): { label: string; icon: string } {
    return {
      label: this.moduleNameService.getModuleFullName(key),
      icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP[key as keyof typeof SHOPFLOOR_ASSET_MAP] ?? ''),
    };
  }

  private resolveAssetPath(path?: string): string {
    if (!path) {
      return '';
    }
    return path.startsWith('/') ? path.slice(1) : path;
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
    // Only load fixture in mock mode; in live/replay mode, streams are already connected
    if (this.isMockMode) {
      void this.loadFixture(this.activeFixture);
    }
  }

  async loadFixture(fixture: OrderFixtureName): Promise<void> {
    if (!this.isMockMode) {
      return; // Don't load fixtures in live/replay mode
    }
    this.activeFixture = fixture;
    try {
      const streams = await this.dashboard.loadFixture(fixture);
      // Rebind flows$ with MessageMonitor merge
      const lastFlows = this.messageMonitor.getLastMessage<ProductionFlowMap>('ccu/state/flows').pipe(
        filter((msg) => msg !== null && msg.valid),
        map((msg) => msg!.payload),
        startWith({} as ProductionFlowMap)
      );
      this.flows$ = merge(lastFlows, streams.flows$).pipe(
        shareReplay({ bufferSize: 1, refCount: false })
      );
      // Rebind products$ from flows$
      this.products$ = this.flows$.pipe(map((flows) => this.buildProductViews(flows)));
    } catch (error) {
      console.warn('Failed to load process fixture', fixture, error);
    }
  }
}

