import { Component, Input } from '@angular/core';
import { Observable } from 'rxjs';
import { map, shareReplay, take } from 'rxjs/operators';
import {
  FtsPairedModule,
  PairedModule,
  PairingState,
} from '../../../common/protocol/ccu';
import { VdaError } from '../../../common/protocol/vda';
import {
  StateLog,
  StateLogType,
  StatesService,
} from '../../services/states.service';

@Component({
  selector: 'ff-state-log-details',
  templateUrl: './state-log-details.component.html',
  styleUrls: ['./state-log-details.component.scss'],
})
export class StateLogDetailsComponent {
  private readonly pairingState$: Observable<PairingState>;
  readonly displayColumns = ['errorType', 'errorLevel'];
  readonly errorColumns = [
    'timestamp',
    ...this.displayColumns,
    'errorReferences',
  ];
  readonly StateLogType = StateLogType;
  readonly moduleInfo$: Observable<PairedModule | undefined>;
  readonly ftsInfo$: Observable<FtsPairedModule | undefined>;

  @Input() stateLog: StateLog | null = null;

  constructor(private stateService: StatesService) {
    this.pairingState$ = this.stateService.pairingState$;

    this.moduleInfo$ = this.setupModuleInfo(this.pairingState$);
    this.ftsInfo$ = this.setupFtsInfo(this.pairingState$);
  }

  /**
   * Check if errors are present and if they are not empty. The empty check is run against the errorLevel property.
   * @param errors The errors to check.
   * @returns True if errors are present and not empty.
   */
  public hasErrors(errors: Array<VdaError>): boolean {
    const errs = errors ?? [];
    return errs.length > 0 && errs.some((e) => !!e.errorLevel);
  }

  /**
   * Filter out empty errors. Empty errors are those that have no errorLevel.
   * @param errors
   * @returns filtered errors
   */
  public filterEmptyErrors(errors: Array<VdaError>): Array<VdaError> {
    const errs = errors ?? [];
    return errs.filter((e) => !!e.errorLevel);
  }

  private setupModuleInfo(
    pairingState$: Observable<PairingState>
  ): Observable<PairedModule | undefined> {
    return pairingState$.pipe(
      map(
        (pairingState) =>
          [
            ...pairingState.modules,
            ...pairingState.transports,
          ] as PairedModule[]
      ),
      map((modules) => {
        const serialNumber = this.stateLog?.state?.serialNumber;
        return modules.find((m) => m.serialNumber === serialNumber);
      }),
      take(1),
      shareReplay(1)
    );
  }

  private setupFtsInfo(
    pairingState$: Observable<PairingState>
  ): Observable<FtsPairedModule | undefined> {
    return pairingState$.pipe(
      map((pairingState) => pairingState.transports as FtsPairedModule[]),
      map((modules) => {
        const serialNumber = this.stateLog?.state?.serialNumber;
        return modules.find((m) => m.serialNumber === serialNumber);
      }),
      take(1),
      shareReplay(1)
    );
  }
}
