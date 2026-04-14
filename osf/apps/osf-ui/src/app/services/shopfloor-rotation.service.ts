import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
 
export type ShopfloorRotation = 'none' | 'cw90' | 'ccw90';
 
const STORAGE_KEY = 'OSF.shopfloorRotation';
 
@Injectable({ providedIn: 'root' })
export class ShopfloorRotationService {
  private readonly subject = new BehaviorSubject<ShopfloorRotation>(this.loadInitial());
  readonly rotation$ = this.subject.asObservable();
 
  get current(): ShopfloorRotation {
    return this.subject.value;
  }
 
  setRotation(next: ShopfloorRotation): void {
    if (next === this.subject.value) {
      return;
    }
    this.subject.next(next);
    try {
      localStorage?.setItem(STORAGE_KEY, next);
    } catch {
      // ignore (private mode / blocked storage)
    }
  }
 
  private loadInitial(): ShopfloorRotation {
    try {
      const raw = localStorage?.getItem(STORAGE_KEY);
      if (raw === 'cw90' || raw === 'ccw90' || raw === 'none') {
        return raw;
      }
      return 'none';
    } catch {
      return 'none';
    }
  }
}
