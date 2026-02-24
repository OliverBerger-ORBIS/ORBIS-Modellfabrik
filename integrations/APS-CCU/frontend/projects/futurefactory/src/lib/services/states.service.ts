import { Injectable, OnDestroy } from '@angular/core';
import {
  Observable,
  OperatorFunction,
  ReplaySubject,
  combineLatest,
  noop,
} from 'rxjs';
import { map, scan, shareReplay, startWith, takeUntil } from 'rxjs/operators';
import {
  ANY_SERIAL,
  CcuTopic,
  FtsTopic,
  ModuleTopic,
  getCcuCalibrationTopic,
  getFtsTopic,
  getModuleTopic,
} from '../../common/protocol';
import {
  ModuleCalibrationState,
  PairedModule,
  PairingState,
} from '../../common/protocol/ccu';
import { FtsState } from '../../common/protocol/fts';
import { ModuleState } from '../../common/protocol/module';
import { Connection } from '../../common/protocol/vda';
import { TypedMqttService } from '../futurefactory.service';
import { getPayload } from '../utils/rx.utils';

export type StateLogType = 'FTS' | 'MODULE' | 'CONNECTION';
export const StateLogType = {
  FTS: 'FTS' as StateLogType,
  MODULE: 'MODULE' as StateLogType,
  CONNECTION: 'CONNECTION' as StateLogType,
};

export interface StateLogBase {
  type: StateLogType;
  received: Date;
}

export interface StateLogFts extends StateLogBase {
  type: 'FTS';
  state: FtsState;
}

export interface StateLogModule extends StateLogBase {
  type: 'MODULE';
  state: ModuleState;
}
export interface StateLogConnection extends StateLogBase {
  type: 'CONNECTION';
  state: Connection;
}

export type StateLog = StateLogFts | StateLogModule | StateLogConnection;

@Injectable({
  providedIn: 'root',
})
export class StatesService implements OnDestroy {
  private readonly destroy = new ReplaySubject<boolean>(1);

  private readonly STATE_TOPICS = {
    fts: getFtsTopic(ANY_SERIAL, FtsTopic.STATE),
    module: getModuleTopic(ANY_SERIAL, ModuleTopic.STATE),
    fts_connection: getFtsTopic(ANY_SERIAL, FtsTopic.CONNECTION),
    module_connection: getModuleTopic(ANY_SERIAL, ModuleTopic.CONNECTION),
  };

  private readonly ftsState$: Observable<StateLogFts>;
  private readonly moduleState$: Observable<StateLogModule>;
  private readonly ftsConnection$: Observable<StateLogConnection>;
  private readonly moduleConnection$: Observable<StateLogConnection>;

  public readonly pairingState$: Observable<PairingState>;
  public readonly pairedModules$: Observable<PairedModule[]>;
  public readonly pairedTransports$: Observable<PairedModule[]>;
  public readonly allModules$: Observable<PairedModule[]>;
  public readonly ftsStateLog$: Observable<StateLogFts[]>;
  public readonly moduleStateLog$: Observable<StateLogModule[]>;
  public readonly ftsConnectionLog$: Observable<StateLogConnection[]>;
  public readonly moduleConnectionLog$: Observable<StateLogConnection[]>;
  public readonly moduleStates$: Observable<Map<string, ModuleState>>;
  public readonly ftsStates$: Observable<Map<string, FtsState>>;
  public readonly stateLog$: Observable<StateLog[]>;
  public readonly calibrationState$: Observable<ModuleCalibrationState>;

  constructor(private mqttService: TypedMqttService) {
    this.pairingState$ = this.mqttService
      .subscribe<PairingState>(CcuTopic.PAIRING_STATE)
      .pipe(getPayload(), shareReplay(1));
    this.pairedModules$ = this.pairingState$.pipe(
      map((payload) => payload.modules),
      shareReplay(1)
    );
    this.pairedTransports$ = this.pairingState$.pipe(
      map((payload) => payload.transports),
      shareReplay(1)
    );
    this.allModules$ = this.pairingState$.pipe(
      map((payload) => [...payload.modules, ...payload.transports]),
      shareReplay(1)
    );
    this.ftsState$ = this.subscribeTo<FtsState, StateLogFts>(
      this.STATE_TOPICS.fts,
      'FTS'
    );
    this.moduleState$ = this.subscribeTo<ModuleState, StateLogModule>(
      this.STATE_TOPICS.module,
      'MODULE'
    );
    this.ftsConnection$ = this.subscribeTo<Connection, StateLogConnection>(
      this.STATE_TOPICS.fts_connection,
      'CONNECTION'
    );
    this.moduleConnection$ = this.subscribeTo<Connection, StateLogConnection>(
      this.STATE_TOPICS.module_connection,
      'CONNECTION'
    );

    this.ftsStateLog$ = this.ftsState$.pipe(this.collectLogs(), shareReplay(1));

    this.moduleStateLog$ = this.moduleState$.pipe(
      this.collectLogs(),
      shareReplay(1)
    );

    this.ftsConnectionLog$ = this.ftsConnection$.pipe(
      this.collectLogs(),
      shareReplay(1)
    );

    this.moduleConnectionLog$ = this.moduleConnection$.pipe(
      this.collectLogs(),
      shareReplay(1)
    );

    this.moduleStates$ = this.moduleState$.pipe(
      scan((states, moduleState) => {
        const newStates = new Map(states);
        if (moduleState.type === 'MODULE') {
          newStates.set(moduleState.state.serialNumber, moduleState.state);
        }
        return newStates;
      }, new Map<string, ModuleState>()),
      shareReplay(1)
    );

    this.ftsStates$ = this.ftsState$.pipe(
      scan((states, ftsState) => {
        const newStates = new Map(states);
        if (ftsState.type === 'FTS') {
          newStates.set(ftsState.state.serialNumber, ftsState.state);
        }
        return newStates;
      }, new Map<string, FtsState>()),
      shareReplay(1)
    );

    this.stateLog$ = combineLatest([
      this.ftsState$,
      this.moduleState$,
      this.ftsConnection$,
      this.moduleConnection$,
    ]).pipe(
      scan((acc, val) => {
        const filled = val.filter((v) => v.type !== undefined);
        return [...new Set([...acc, ...filled])];
      }, [] as StateLog[]),
      shareReplay(1)
    );

    this.calibrationState$ = this.mqttService
      .subscribe<ModuleCalibrationState>(getCcuCalibrationTopic(ANY_SERIAL))
      .pipe(map((message) => message.payload));

    this.calibrationState$ = this.mqttService
      .subscribe<ModuleCalibrationState>(getCcuCalibrationTopic(ANY_SERIAL))
      .pipe(getPayload());

    // immediately start accumulating data
    this.ftsStateLog$.pipe(takeUntil(this.destroy)).subscribe(noop);
    this.moduleStateLog$.pipe(takeUntil(this.destroy)).subscribe(noop);
    this.ftsConnectionLog$.pipe(takeUntil(this.destroy)).subscribe(noop);
    this.moduleConnectionLog$.pipe(takeUntil(this.destroy)).subscribe(noop);
    this.stateLog$.pipe(takeUntil(this.destroy)).subscribe(noop);
    this.moduleStates$.pipe(takeUntil(this.destroy)).subscribe(noop);
  }

  ngOnDestroy(): void {
    this.destroy.next(true);
    this.destroy.complete();
  }

  private subscribeTo<T, R>(topic: string, type: StateLogType): Observable<R> {
    return this.mqttService.subscribe<T>(topic).pipe(
      map((msg) => {
        return {
          type,
          received: new Date(),
          state: msg.payload,
        } as unknown as R;
      }),
      startWith({} as R),
      shareReplay(1)
    );
  }

  private collectLogs<T>(): OperatorFunction<T, T[]> {
    return scan<T, T[]>((acc, log) => {
      if (!(log as any).type) {
        return acc;
      }
      return [...new Set([...acc, log])];
    }, [] as T[]);
  }
}
