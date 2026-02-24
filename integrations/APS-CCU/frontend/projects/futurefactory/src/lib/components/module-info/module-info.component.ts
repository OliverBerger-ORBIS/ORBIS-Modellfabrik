import { Component, Input } from '@angular/core';
import { Observable, combineLatest } from 'rxjs';
import { filter, map, shareReplay, startWith, take } from 'rxjs/operators';
import {
  FtsPairedModule,
  PairedModule,
  PairingState,
} from '../../../common/protocol/ccu';
import { StateLog, StatesService } from '../../services/states.service';

export type ModuleInfo = {
  serialNumber: string;
  type: string;
  subType?: string;
};

@Component({
  selector: 'ff-module-info',
  templateUrl: './module-info.component.html',
  styleUrls: ['./module-info.component.scss'],
})
export class ModuleInfoComponent {
  private readonly pairingState$: Observable<PairingState>;
  private readonly pairedModule$: Observable<PairedModule | undefined>;
  private readonly pairedFts$: Observable<FtsPairedModule | undefined>;

  readonly moduleInfo$: Observable<ModuleInfo | undefined>;

  @Input() stateLog: StateLog | null = null;

  constructor(private stateService: StatesService) {
    this.pairingState$ = this.stateService.pairingState$;
    this.pairedModule$ = this.setupPairedModule(this.pairingState$);
    this.pairedFts$ = this.setupPairedFts(this.pairingState$);
    this.moduleInfo$ = this.setupModuleInfo(
      this.pairedModule$,
      this.pairedFts$
    );
  }

  private setupPairedModule(
    pairingState$: Observable<PairingState>
  ): Observable<PairedModule | undefined> {
    return pairingState$.pipe(
      map((pairingState) => pairingState.modules as PairedModule[]),
      map((modules) => {
        const serialNumber = this.stateLog?.state?.serialNumber;
        return modules.find((m) => m.serialNumber === serialNumber);
      }),
      take(1),
      shareReplay(1)
    );
  }

  private setupPairedFts(
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

  private setupModuleInfo(
    pairedModule$: Observable<PairedModule | undefined>,
    pairedFts$: Observable<FtsPairedModule | undefined>
  ): Observable<ModuleInfo | undefined> {
    return combineLatest([pairedModule$, pairedFts$]).pipe(
      map(([pairedModule, pairedFts]) => pairedModule ?? pairedFts),
      filter((pairedModule) => !!pairedModule),
      map((pairedModule) => ({
        serialNumber: pairedModule!.serialNumber,
        type: pairedModule!.type,
        subType: pairedModule!.subType,
      })),
      startWith(undefined),
      shareReplay(1)
    );
  }
}
