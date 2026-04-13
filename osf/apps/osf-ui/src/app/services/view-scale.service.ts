import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

const STORAGE_KEY = 'OSF.viewScale';
const DEFAULT_SCALE = 1;
const MIN_SCALE = 0.4;
const MAX_SCALE = 1.8;

@Injectable({ providedIn: 'root' })
export class ViewScaleService {
  private readonly subject = new BehaviorSubject<number>(this.loadInitial());
  readonly scale$ = this.subject.asObservable();

  get current(): number {
    return this.subject.value;
  }

  setScale(value: number): void {
    const next = clamp(value, MIN_SCALE, MAX_SCALE);
    if (Math.abs(next - this.subject.value) < 0.0001) {
      return;
    }
    this.subject.next(next);
    try {
      sessionStorage?.setItem(STORAGE_KEY, String(next));
    } catch {
      // ignore (private mode / blocked storage)
    }
  }

  private loadInitial(): number {
    try {
      const raw = sessionStorage?.getItem(STORAGE_KEY);
      if (!raw) {
        return DEFAULT_SCALE;
      }
      const num = Number(raw);
      if (!Number.isFinite(num)) {
        return DEFAULT_SCALE;
      }
      return clamp(num, MIN_SCALE, MAX_SCALE);
    } catch {
      return DEFAULT_SCALE;
    }
  }
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}
