import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import type { ProductionFlowMap } from '@omf3/entities';
import { SHOPFLOOR_ASSET_MAP } from '@omf3/testing-fixtures';
import { getDashboardController } from '../mock-dashboard';
import { MessageMonitorService } from '../services/message-monitor.service';
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
export class ProcessTabComponent {
  private readonly dashboard = getDashboardController();

  // Subscribe directly to dashboard streams - they already have shareReplay with startWith
  // Use refCount: false to keep streams alive even when no subscribers
  flows$: Observable<ProductionFlowMap>;
  
  products$: Observable<ProcessProductView[]>;

  constructor(private readonly messageMonitor: MessageMonitorService) {
    // flows$ doesn't have startWith in gateway layer, so merge MessageMonitor last value with dashboard stream
    const lastFlows = this.messageMonitor.getLastMessage<ProductionFlowMap>('ccu/state/flows').pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => msg!.payload),
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

  private readonly moduleMeta: Record<string, { label: string; icon: string }> = {
    HBW: { label: $localize`:@@processModuleHBW:High-bay warehouse`, icon: this.startIcon },
    DRILL: { label: $localize`:@@processModuleDrill:Drill`, icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DRILL']) },
    MILL: { label: $localize`:@@processModuleMill:Mill`, icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['MILL']) },
    AIQS: {
      label: $localize`:@@processModuleAiQs:AI Quality Station`,
      icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['AIQS']),
    },
    DPS: { label: $localize`:@@processModuleDps:Goods outgoing`, icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS']) },
  };

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
    const moduleMeta = this.moduleMeta[key] ?? {
      label: step,
      icon: this.resolveAssetPath(SHOPFLOOR_ASSET_MAP['DPS'] ?? 'shopfloor/robotic.svg'),
    };

    return {
      id: `${key}-${index}`,
      label: moduleMeta.label,
      icon: moduleMeta.icon,
      isPlaceholder: false,
    };
  }
}

