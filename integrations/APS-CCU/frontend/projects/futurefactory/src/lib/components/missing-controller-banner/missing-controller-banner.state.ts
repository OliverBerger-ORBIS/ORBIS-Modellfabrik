import { Injectable } from '@angular/core';
import { ControllerResponse } from '@fischertechnik/ft-api';
import { Observable } from 'rxjs';
import { map, shareReplay, withLatestFrom } from 'rxjs/operators';
import { SelectedControllerService } from '../../services/selected-controller.service';

@Injectable()
export class MissingControllerBannerState {
  private readonly factoryControllers$: Observable<ControllerResponse[]>;
  public readonly hasController$: Observable<boolean>;

  constructor(private controllerService: SelectedControllerService) {
    this.factoryControllers$ =
      this.controllerService.availableFutureFactoryControllers$;
    this.hasController$ = this.setupHasController(
      this.factoryControllers$,
      this.controllerService.selectedController$
    );
  }

  private setupHasController(
    factoryControllers$: Observable<ControllerResponse[]>,
    selectedController$: Observable<ControllerResponse | undefined>
  ): Observable<boolean> {
    return factoryControllers$.pipe(
      withLatestFrom(selectedController$),
      map(
        ([controllers, selectedController]) =>
          !!selectedController || controllers.length > 0
      ),
      shareReplay(1)
    );
  }
}
