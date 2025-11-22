import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import type { SensorOverviewState } from '@omf3/entities';

@Injectable({ providedIn: 'root' })
export class SensorStateService {
  private readonly stores = new Map<string, BehaviorSubject<SensorOverviewState | null>>();

  getState$(environmentKey: string): Observable<SensorOverviewState | null> {
    return this.getStore(environmentKey).asObservable();
  }

  getSnapshot(environmentKey: string): SensorOverviewState | null {
    return this.getStore(environmentKey).value;
  }

  setState(environmentKey: string, state: SensorOverviewState): void {
    this.getStore(environmentKey).next(state);
  }

  clear(environmentKey: string): void {
    this.getStore(environmentKey).next(null);
  }

  private getStore(environmentKey: string): BehaviorSubject<SensorOverviewState | null> {
    if (!this.stores.has(environmentKey)) {
      this.stores.set(environmentKey, new BehaviorSubject<SensorOverviewState | null>(null));
    }
    return this.stores.get(environmentKey)!;
  }
}


