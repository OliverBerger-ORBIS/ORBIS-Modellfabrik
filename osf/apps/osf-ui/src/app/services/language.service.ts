import { Injectable, inject } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

export type LocaleKey = 'en' | 'de' | 'fr';

const STORAGE_KEY = 'OSF.locale';

@Injectable({ providedIn: 'root' })
export class LanguageService {
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  readonly supportedLocales: LocaleKey[] = ['en', 'de', 'fr'];

  get current(): LocaleKey {
    // Try to get from URL first
    const urlSegments = this.router.url.split('/').filter(Boolean);
    const localeFromUrl = urlSegments[0] as LocaleKey;
    if (this.supportedLocales.includes(localeFromUrl)) {
      return localeFromUrl;
    }
    // Fallback to localStorage
    return (localStorage?.getItem(STORAGE_KEY) as LocaleKey | null) ?? 'en';
  }

  setLocale(locale: LocaleKey): void {
    if (locale === this.current) {
      return;
    }
    localStorage?.setItem(STORAGE_KEY, locale);
    const newUrl = this.buildLocaleSwitchUrl(locale);
    window.location.assign(newUrl);
  }

  /**
   * Build URL for locale switch. Public for testing.
   * Navigates to locale-specific path so the correct build loads (/en/, /de/, /fr/).
   */
  buildLocaleSwitchUrl(locale: LocaleKey): string {
    const urlSegments = this.router.url.split('/').filter(Boolean);
    const currentLocale = urlSegments[0] as LocaleKey;
    let routePath = 'dsp';
    if (this.supportedLocales.includes(currentLocale)) {
      routePath = urlSegments.slice(1).join('/') || 'dsp';
    } else {
      routePath = urlSegments.join('/') || 'dsp';
    }
    const hash = `#/${locale}/${routePath}`;
    const pathname = typeof window !== 'undefined' ? window.location.pathname : '/en/';
    const replaced = pathname.replace(/\/(en|de|fr)\/?/, `/${locale}/`);
    const pathWithLocale = replaced.match(/\/(en|de|fr)\/?/) ? replaced : `${pathname.replace(/\/$/, '')}/${locale}/`;
    const origin = typeof window !== 'undefined' ? window.location.origin : 'http://localhost';
    return `${origin}${pathWithLocale}${hash}`;
  }
}
