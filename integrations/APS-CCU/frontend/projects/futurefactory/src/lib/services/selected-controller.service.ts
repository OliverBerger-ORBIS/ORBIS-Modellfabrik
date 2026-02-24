import { Inject, Injectable, OnDestroy } from '@angular/core';
import { ControllerResponse } from '@fischertechnik/ft-api';
import { BehaviorSubject, Observable, ReplaySubject, from, of, scheduled } from 'rxjs';
import {
  filter,
  map,
  shareReplay,
  switchMap,
  takeUntil,
  withLatestFrom,
} from 'rxjs/operators';
import {
  ControllerClientService,
  IControllerService,
} from '../futurefactory.external.service';

/**
 * This service provides the currently selected controller
 * and a list of available controllers.
 *
 * The after loading the available controllers, the first controller
 * is selected from the list of available controllers.
 */
@Injectable()
export class SelectedControllerService implements OnDestroy {
  private readonly destroy$ = new ReplaySubject<boolean>(1);
  readonly selectedController$ = new BehaviorSubject<
    ControllerResponse | undefined
  >(undefined);
  readonly availableControllers$: Observable<ControllerResponse[]>;
  readonly availableFutureFactoryControllers$: Observable<ControllerResponse[]>;

  constructor(
    @Inject(ControllerClientService)
    private controllerService: IControllerService
  ) {
    this.availableControllers$ = of(this.controllerService.loadControllers()).pipe(
      switchMap(() => this.controllerService.onChange()),
      shareReplay(1)
    );
    this.availableFutureFactoryControllers$ =
      this.setupAvailableFutureFactoryControllers(this.availableControllers$);

    this.setupSelectedController(this.availableFutureFactoryControllers$);
  }

  ngOnDestroy(): void {
    this.destroy$.next(true);
    this.destroy$.complete();
  }

  /**
   * This method loads the available controllers from the backend.
   */
  loadControllers(): void {
    this.controllerService.loadControllers();
  }

  private setupAvailableFutureFactoryControllers(
    availableControllers$: Observable<ControllerResponse[]>
  ): Observable<ControllerResponse[]> {
    return availableControllers$.pipe(
      filter((ac) => ac?.length > 0),
      map((ac) => ac.filter((c) => c?.targetModule === 3)),
      shareReplay(1)
    );
  }

  /**
   * This method takes the list of available controllers
   * and selects the first controller from the list, if no controller
   * is selected, otherwise the selected controller is checked against
   * the list of available controllers and selected if it is available.
   *
   * @param availableControllers$ Observable of available controllers
   */
  private setupSelectedController(
    availableControllers$: Observable<ControllerResponse[]>
  ): void {
    availableControllers$
      .pipe(
        filter((ac) => ac?.length > 0),
        map((ac) => ac.filter((c) => !!c)),
        withLatestFrom(this.selectedController$),
        map(
          ([available, selected]) =>
            // select first controller if selected is undefined
            available.find((c) => c.controllerId === selected?.controllerId) ??
            available[0]
        ),
        takeUntil(this.destroy$)
      )
      .subscribe((controller) => this.selectedController$.next(controller));
  }
}
