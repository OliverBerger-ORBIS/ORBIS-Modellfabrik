import {
  CdkDrag,
  CdkDragDrop,
  CdkDropList,
  moveItemInArray,
  transferArrayItem,
} from '@angular/cdk/drag-drop';
import { Component, OnDestroy } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TranslateService } from '@ngx-translate/core';
import {
  Observable,
  ReplaySubject,
  firstValueFrom,
  map,
  takeUntil,
} from 'rxjs';
import { CcuTopic } from '../../../common/protocol';
import {
  PairedModule,
  ProductionFlows,
  Workpiece,
} from '../../../common/protocol/ccu';
import { ModuleType, SUPPORT_MODULES } from '../../../common/protocol/module';
import { TypedMqttService } from '../../futurefactory.service';
import { FactoryLayoutService } from '../../services/factory-layout.service';
import { OrderStatesService } from '../../services/order-states.service';
import { ProductionFlowsService } from '../../services/production-flow.service';

// This record contains the allowed modules for each workpiece type
// It has to reside outside of the component, otherwise the drag and drop functionality
// will not work correctly
const allowedModules = {
  [Workpiece.BLUE]: [
    ModuleType.AIQS,
    ModuleType.MILL,
    ModuleType.DRILL,
    ModuleType.OVEN,
  ],
  [Workpiece.RED]: [ModuleType.AIQS, ModuleType.MILL, ModuleType.OVEN],
  [Workpiece.WHITE]: [ModuleType.AIQS, ModuleType.DRILL, ModuleType.OVEN],
};

/**
 * This record contains the allowed modules for each workpiece type
 * after the extended flows option is enabled
 */
const allModules = [
  ModuleType.AIQS,
  ModuleType.MILL,
  ModuleType.DRILL,
  ModuleType.OVEN,
];

/**
 * Allows viewing and editing the steps for the production of a workpiece type
 */
@Component({
  selector: 'ff-flow-editor',
  templateUrl: './flow-editor.component.html',
  styleUrls: ['./flow-editor.component.scss'],
})
export class FutureFactoryFlowEditorComponent implements OnDestroy {
  private readonly destroyed$ = new ReplaySubject<void>(1);
  private productionFlows: ProductionFlows = {};
  readonly availableTypes$: Observable<Array<ModuleType>>;
  readonly selectableTypes$: Observable<Array<ModuleType>>;
  readonly Workpiece = Workpiece;
  readonly availableModulesId = 'available-modules';
  readonly hasRunningOrders$: Observable<boolean>;

  modified = false;
  extendedFlows = false;
  enterPredicate__bound = this.enterPredicate.bind(this);
  blueSteps: ModuleType[] = [];
  redSteps: ModuleType[] = [];
  whiteSteps: ModuleType[] = [];

  constructor(
    public productionFlowsService: ProductionFlowsService,
    public layout: FactoryLayoutService,
    private orderStates: OrderStatesService,
    private mqtt: TypedMqttService,
    private translate: TranslateService,
    private notification: MatSnackBar
  ) {
    productionFlowsService.productionFlows$
      .pipe(takeUntil(this.destroyed$))
      .subscribe((flows) => {
        this.productionFlows = flows;
        this.resetFlows();
      });

    const isPairedProductionModule = (module: PairedModule) =>
      module.pairedSince &&
      module.subType &&
      !SUPPORT_MODULES.has(module.subType);

    this.availableTypes$ = layout.pairedModules$.pipe(
      map((modules) =>
        modules
          .filter(isPairedProductionModule)
          .map((module) => module.subType!)
      )
    );
    this.selectableTypes$ = this.availableTypes$.pipe(
      map((modTypes) => [...new Set(modTypes ?? [])])
    );

    this.hasRunningOrders$ = this.orderStates.hasRunningOrders$;
  }

  /**
   * Reset the flows to the current factory configuration
   * @private
   */
  public resetFlows(): void {
    this.modified = false;
    const flows = JSON.parse(JSON.stringify(this.productionFlows));
    if (!this.modified) {
      this.blueSteps = flows.BLUE?.steps || [];
      this.redSteps = flows.RED?.steps || [];
      this.whiteSteps = flows.WHITE?.steps || [];
    }
  }

  ngOnDestroy(): void {
    this.destroyed$.next();
    this.destroyed$.complete();
  }

  /**
   * Predicate function that only allows dragging of modules that are allowed for the
   * workpiece type at the drop location
   * The AIQS module is only allowed once per workpiece type.
   * Also: When the is no valid index for the module to be dropped, it is not allowed.
   */
  enterPredicate(
    drag: CdkDrag<ModuleType>,
    drop: CdkDropList<ModuleType[]>
  ): boolean {
    const allowedModulesForColor = this.extendedFlows
      ? allModules
      : allowedModules[drop.id] ?? [];
    const hasAiqs =
      drag.data === ModuleType.AIQS && drop.data.includes(ModuleType.AIQS);
    const isAllowedModule = allowedModulesForColor.includes(drag.data);

    if (!(isAllowedModule && !hasAiqs)) {
      return false;
    }
    return true;
  }

  /**
   * Ensures, that no module can be placed directly after or before itself.
   * Also ensures that AIQS is always at the end of the chain.
   * This method is used as a predicate function for the drag-and-drop functionality.
   */
  sortPredicate(index: number, drag: CdkDrag<ModuleType>, drop: CdkDropList<ModuleType[]>): boolean {
    const steps = [...drop.data];
    moveItemInArray(steps, index, drop.data.indexOf(drag.data));

    const isAiqs = drag.data === ModuleType.AIQS;
    const isModuleSame = steps[index + 1] === drag.data;
    const isPreviousModuleSame = steps[index - 1] === drag.data;
    const isPreviousModuleAiqs = steps[index - 1] === ModuleType.AIQS;

    if (isAiqs) {
      return index === steps.length;
    } else {
      return !isModuleSame && !isPreviousModuleSame && !isPreviousModuleAiqs;
    }
  }

  drop(event: CdkDragDrop<ModuleType[]>) {
    if (
      event.previousIndex === event.currentIndex &&
      event.previousContainer === event.container
    ) {
      return;
    }

    this.modified = true;
    if (event.previousContainer === event.container) {
      moveItemInArray(
        event.container.data,
        event.previousIndex,
        event.currentIndex
      );
    } else if (event.previousContainer.id === this.availableModulesId) {
      event.container.data.splice(event.currentIndex, 0, event.item.data);
    } else {
      transferArrayItem(
        event.previousContainer.data,
        event.container.data,
        event.previousIndex,
        event.currentIndex
      );
    }

    this.ensureChainConsistency(event.container.data);
  }

  /**
   * (Ensure = check & repair; mutates the input array!)
   * Ensures that the AIQS is always at the end of the chain.
   *   - If not, it moves the AIQS module to the end of the chain and notifies the user.
   * Ensures, that no module follows or precedes itself.
   *   - If so, it removes the module from the steps array and notifies the user.
   * @param steps The array of steps to check
   * @returns
   */
  ensureChainConsistency(steps: ModuleType[]): void {
    // ensures that AIQS is always at the end of the chain
    const lastIndex = steps.length - 1;
    const aiqsIndex = steps.indexOf(ModuleType.AIQS);
    if (aiqsIndex !== -1 && aiqsIndex !== lastIndex) {
      // move aiqs to end
      steps.splice(lastIndex, 0, steps.splice(aiqsIndex, 1)[0]);
      this.notification.open(
        this.translate.instant('AIQS muss immer am Ende der Kette stehen'),
        this.translate.instant('OK'),
        { duration: 5000 }
      );
    }

    // ensures that no module follows or precedes itself
    let i = 0;
    while (i < steps.length - 1) {
      if (steps[i] === steps[i + 1]) {
        steps.splice(i, 1);
        this.notification.open(
          this.translate.instant(
            'Ein Produktionsschritt wurde entfernt, da dieser direkt auf sich selbst folgte.'
          ),
          this.translate.instant('OK'),
          { duration: 5000 }
        );
      } else {
        i++;
      }
    }
  }

  deleteStepAtIndex(index: number, steps: ModuleType[]) {
    this.modified = true;
    steps.splice(index, 1);

    this.ensureChainConsistency(steps);
  }

  async saveFlows() {
    const hasRunningOrders = await firstValueFrom(this.hasRunningOrders$);
    if (hasRunningOrders) {
      return;
    }
    const flows: ProductionFlows = {
      BLUE: { steps: [...this.blueSteps] },
      RED: { steps: [...this.redSteps] },
      WHITE: { steps: [...this.whiteSteps] },
    };
    this.modified = false;
    this.mqtt.publish(CcuTopic.SET_FLOWS, flows, { qos: 2 });
  }
}
