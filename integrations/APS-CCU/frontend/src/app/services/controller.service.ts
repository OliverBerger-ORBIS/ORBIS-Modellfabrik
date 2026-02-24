import { Injectable } from '@angular/core';
import { ControllerResponse } from '@fischertechnik/ft-api';
import { IControllerService } from '@ft/futurefactory';
import { BehaviorSubject, Observable, ReplaySubject } from 'rxjs';

/**
 * Assigned module as enum integer. 0 = unset, 1 = smart home, 2 = training factory, 3 = agile production simulation.
 */
enum FtModule {
  Unset = 0,
  SmartHome = 1,
  TrainingFactory = 2,
  // The Agile Production Simulation module.
  APS = 3,
}

/**
 * Raspberry PI based implementation of the IControllerService.
 * The implementation is based on the mock implementation of the ft-api.
 */
@Injectable({
  providedIn: 'root',
})
export class LocalControllerService implements IControllerService {
  private readonly controllers$ = new BehaviorSubject<ControllerResponse[]>([
    {
      targetModule: FtModule.APS,
      name: 'APS',
      hardwareModel: 'TXT',
      alarm: true,
      pushMessage: true,
      shared: true,
      mqttUser: {
        mqttUserId: 1,
        password: 'password',
        crdate: 1560873431,
        controllerId: '1',
      },
      softwareVersion: '1.1.9',
      softwareName: 'txt',
      controllerId: 1,
      crdate: 1560873431,
    },
  ]);

  onChange(): Observable<ControllerResponse[]> {
    return this.controllers$.asObservable();
  }

  loadControllers(): void {
    // Do nothing.
  }
}
