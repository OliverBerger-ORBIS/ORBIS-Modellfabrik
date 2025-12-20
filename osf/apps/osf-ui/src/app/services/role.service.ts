import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type UserRole = 'operator' | 'admin';

const STORAGE_KEY = 'OSF.user.role';

@Injectable({ providedIn: 'root' })
export class RoleService {
  private readonly roleSubject: BehaviorSubject<UserRole>;

  constructor() {
    this.roleSubject = new BehaviorSubject<UserRole>(this.loadInitialRole());
  }

  get role$() {
    return this.roleSubject.asObservable();
  }

  get current(): UserRole {
    return this.roleSubject.value;
  }

  setRole(role: UserRole): void {
    if (role === this.current) {
      return;
    }
    localStorage?.setItem(STORAGE_KEY, role);
    this.roleSubject.next(role);
  }

  private loadInitialRole(): UserRole {
    const stored = localStorage?.getItem(STORAGE_KEY) as UserRole | null;
    if (stored === 'admin' || stored === 'operator') {
      return stored;
    }
    return 'admin';
  }
}
