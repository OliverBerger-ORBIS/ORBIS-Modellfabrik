import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import type { ModuleOverviewState } from '@omf3/entities';

@Injectable({ providedIn: 'root' })
export class ModuleOverviewStateService {
  private readonly stores = new Map<string, BehaviorSubject<ModuleOverviewState | null>>();

  getState$(environmentKey: string): Observable<ModuleOverviewState | null> {
    return this.getStore(environmentKey).asObservable();
  }

  getSnapshot(environmentKey: string): ModuleOverviewState | null {
    return this.getStore(environmentKey).value;
  }

  setState(environmentKey: string, state: ModuleOverviewState): void {
    this.getStore(environmentKey).next(state);
  }

  clear(environmentKey: string): void {
    this.getStore(environmentKey).next(null);
  }

  private getStore(environmentKey: string): BehaviorSubject<ModuleOverviewState | null> {
    if (!this.stores.has(environmentKey)) {
      this.stores.set(environmentKey, new BehaviorSubject<ModuleOverviewState | null>(null));
    }
    return this.stores.get(environmentKey)!;
  }
}


