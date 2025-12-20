import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import type { InventoryOverviewState } from '@osf/entities';

@Injectable({ providedIn: 'root' })
export class InventoryStateService {
  private readonly stores = new Map<string, BehaviorSubject<InventoryOverviewState | null>>();

  getState$(environmentKey: string): Observable<InventoryOverviewState | null> {
    return this.getStore(environmentKey).asObservable();
  }

  getSnapshot(environmentKey: string): InventoryOverviewState | null {
    return this.getStore(environmentKey).value;
  }

  setState(environmentKey: string, state: InventoryOverviewState): void {
    this.getStore(environmentKey).next(state);
  }

  clear(environmentKey: string): void {
    this.getStore(environmentKey).next(null);
  }

  private getStore(environmentKey: string): BehaviorSubject<InventoryOverviewState | null> {
    if (!this.stores.has(environmentKey)) {
      this.stores.set(environmentKey, new BehaviorSubject<InventoryOverviewState | null>(null));
    }
    return this.stores.get(environmentKey)!;
  }
}

