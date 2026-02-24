import { Component, Input, OnDestroy } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute } from '@angular/router';
import {
  BehaviorSubject,
  Observable,
  Subject,
  combineLatestWith,
  filter,
  map,
  shareReplay,
  startWith,
  takeUntil,
} from 'rxjs';
import { CcuTopic } from '../../../common/protocol';
import {
  ModuleCalibration,
  ModuleCalibrationCommand,
  ModuleCalibrationState,
  PairedModule,
} from '../../../common/protocol/ccu';
import { ModuleCalibrationStatusKeys } from '../../../common/protocol/module';
import { ReferenceValue } from '../../../common/protocol/vda';
import { TypedMqttService } from '../../futurefactory.service';
import { FactoryLayoutService } from '../../services/factory-layout.service';
import { StatesService } from '../../services/states.service';
import { getRouteToModuleRoot } from '../../utils/routes.utils';

@Component({
  selector: 'ff-module-details',
  templateUrl: './module-calibration.component.html',
  styleUrls: ['./module-calibration.component.scss'],
})
export class FutureFactoryModuleCalibrationComponent implements OnDestroy {
  readonly ModuleCalibrationCommand = ModuleCalibrationCommand;

  readonly moduleId$ = new BehaviorSubject<string | undefined>(undefined);
  private destroyed$ = new Subject<void>();
  readonly routeToRoot$: Observable<string>;

  public image_data: Array<ReferenceValue> = [];
  public calibration_data: Array<ReferenceValue> = [];
  public available_positions: string[] = [];
  public current_position: string = '';
  public status_values: Array<ReferenceValue> = [];

  @Input() set moduleId(id: string | undefined) {
    this.moduleId$.next(id);
  }

  get moduleId(): string | undefined {
    return this.moduleId$.value;
  }

  private moduleCalibration$: Observable<ModuleCalibrationState | undefined>;
  readonly moduleData$: Observable<PairedModule | undefined>;

  constructor(
    readonly factoryLayoutService: FactoryLayoutService,
    readonly statesService: StatesService,
    private mqttClient: TypedMqttService,
    private route: ActivatedRoute,
    readonly dialog: MatDialog
  ) {
    route.params.pipe(takeUntil(this.destroyed$)).subscribe((params) => {
      if (params['moduleId']) {
        this.moduleId = params['moduleId'];
      }
    });

    this.routeToRoot$ = getRouteToModuleRoot(route);

    this.moduleData$ = this.createModuleDataObservable();
    this.moduleCalibration$ = this.createModuleCalibrationObservable();

    this.moduleCalibration$.subscribe((calibration_data) => {
      if (calibration_data) {
        this.calibration_data = [];
        this.status_values = [];
        this.image_data = [];
        this.available_positions = [];
        this.current_position = '';
        if (calibration_data.references) {
          for (const ref of calibration_data.references) {
            this.calibration_data.push(ref);
          }
        }
        if (calibration_data.status_references) {
          for (const ref of calibration_data.status_references) {
            if (
              typeof ref.referenceValue === 'string' &&
              ref.referenceValue.startsWith('data:')
            ) {
              this.image_data.push(ref);
            } else if (
              ref.referenceKey ===
                ModuleCalibrationStatusKeys.POSITIONS_AVAILABLE &&
              typeof ref.referenceValue === 'string'
            ) {
              this.available_positions = ref.referenceValue.split(',');
            } else if (
              ref.referenceKey ===
                ModuleCalibrationStatusKeys.POSITIONS_CURRENT &&
              typeof ref.referenceValue === 'string'
            ) {
              this.current_position = ref.referenceValue;
            } else {
              this.status_values.push(ref);
            }
          }
        }
        const referenceSorter = (refA: ReferenceValue, refB: ReferenceValue) =>
          refA.referenceKey.localeCompare(refB.referenceKey);
        this.calibration_data.sort(referenceSorter);
        this.status_values.sort(referenceSorter);
        this.image_data.sort(referenceSorter);
      }
    });
  }

  updateRef(refInput: HTMLInputElement, ref: ReferenceValue, newValue: number) {
    this.calibration_data = this.calibration_data.map((_ref) => {
      if (_ref.referenceKey === ref.referenceKey) {
        _ref.referenceValue = newValue;
      }
      return _ref;
    });
    refInput.focus();
  }

  /**
   * Get the module calibration data for the given module
   * @private
   */
  private createModuleCalibrationObservable() {
    return this.statesService.calibrationState$.pipe(
      combineLatestWith(this.moduleId$),
      map(([calib, moduleId]) =>
        calib.serialNumber === moduleId ? calib : null
      ),
      filter((calib): calib is ModuleCalibrationState => !!calib),
      startWith(undefined),
      shareReplay(1),
      takeUntil(this.destroyed$)
    );
  }

  /**
   * Get the paired module data for the given module
   * @private
   */
  private createModuleDataObservable() {
    return this.factoryLayoutService.pairedModules$.pipe(
      combineLatestWith(this.moduleId$),
      map(([modules, moduleId]) =>
        moduleId
          ? modules.find((module) => module.serialNumber === moduleId)
          : undefined
      ),
      shareReplay(1),
      takeUntil(this.destroyed$)
    );
  }

  ngOnDestroy() {
    this.destroyed$.complete();
    this.moduleId$.complete();
  }

  calibrationCommandWithValues(command: ModuleCalibrationCommand) {
    if (this.moduleId) {
      this.sendCalibrationCommand(
        command,
        undefined,
        undefined,
        this.calibration_data.map((ref) => {
          ref.referenceValue = +ref.referenceValue;
          return ref;
        })
      );
    }
  }

  public sendCalibrationCommand(
    command: ModuleCalibrationCommand,
    position?: string,
    factory?: boolean,
    references?: Array<ReferenceValue>
  ) {
    if (this.moduleId) {
      this.mqttClient.publish<ModuleCalibration>(
        CcuTopic.SET_MODULE_CALIBRATION,
        {
          timestamp: new Date(),
          serialNumber: this.moduleId,
          command: command,
          position,
          factory,
          references,
        }
      );
    }
  }
}
