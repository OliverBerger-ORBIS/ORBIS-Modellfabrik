import { Injectable, inject } from '@angular/core';
import { Location } from '@angular/common';
import { Router } from '@angular/router';
import { LanguageService } from './language.service';

@Injectable({ providedIn: 'root' })
export class NavigationBackService {
  private readonly location = inject(Location);
  private readonly router = inject(Router);
  private readonly language = inject(LanguageService);

  /**
   * Tries to go back using browser history.
   * Falls back to a locale-aware route when there is no safe in-app referrer
   * (common for deep links / new tabs).
   *
   * @param fallbackPath Path without locale prefix (e.g. 'dsp', 'dsp/use-case').
   */
  backOrNavigate(fallbackPath: string): void {
    const canUseHistoryBack = this.hasSameOriginReferrer() && this.hasHistory();
    if (canUseHistoryBack) {
      this.location.back();
      return;
    }

    const locale = this.language.current;
    const normalized = fallbackPath.replace(/^\/+/, '');
    void this.router.navigateByUrl(`/${locale}/${normalized}`);
  }

  private hasHistory(): boolean {
    try {
      return typeof window !== 'undefined' && window.history.length > 1;
    } catch {
      return false;
    }
  }

  private hasSameOriginReferrer(): boolean {
    try {
      if (typeof document === 'undefined' || typeof window === 'undefined') {
        return false;
      }
      const referrer = document.referrer;
      if (!referrer) {
        return false;
      }
      return referrer.startsWith(window.location.origin);
    } catch {
      return false;
    }
  }
}

