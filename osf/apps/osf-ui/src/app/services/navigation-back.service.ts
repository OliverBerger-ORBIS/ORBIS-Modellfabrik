import { Injectable, inject } from '@angular/core';
import { Location } from '@angular/common';
import { Router } from '@angular/router';
import { LanguageService } from './language.service';
import {
  DSP_RETURN_SECTION_SESSION_KEY,
  isDspAccordionSectionId,
} from '../pages/dsp/dsp-accordion-sections';

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
   * If the user opened the current flow from an embedded DSP accordion (e.g. Use Cases),
   * returns to `/{locale}/dsp?section=…` so the accordion can open the right panel.
   *
   * @param fallbackPath Path without locale prefix (e.g. 'dsp', 'dsp/use-case').
   */
  backOrNavigate(fallbackPath: string): void {
    const pendingSection = this.consumePendingDspReturnSection();
    if (pendingSection) {
      const locale = this.language.current;
      void this.router.navigate([locale, 'dsp'], {
        queryParams: { section: pendingSection },
        replaceUrl: true,
      });
      return;
    }

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

  /**
   * Reads and clears the session flag set when navigating from the DSP page
   * into a use-case detail (embedded tiles).
   */
  private consumePendingDspReturnSection(): string | null {
    try {
      if (typeof sessionStorage === 'undefined') {
        return null;
      }
      const raw = sessionStorage.getItem(DSP_RETURN_SECTION_SESSION_KEY);
      sessionStorage.removeItem(DSP_RETURN_SECTION_SESSION_KEY);
      if (!raw || !isDspAccordionSectionId(raw)) {
        return null;
      }
      return raw;
    } catch {
      return null;
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

