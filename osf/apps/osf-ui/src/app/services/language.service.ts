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
    
    // Get current route without locale
    const urlSegments = this.router.url.split('/').filter(Boolean);
    const currentLocale = urlSegments[0] as LocaleKey;
    let routePath = 'overview';
    
    // If current URL has a locale, extract the route after it
    if (this.supportedLocales.includes(currentLocale)) {
      routePath = urlSegments.slice(1).join('/') || 'overview';
    } else {
      // No locale in URL, use current path
      routePath = urlSegments.join('/') || 'overview';
    }
    
    // Navigate to new locale with same route
    this.router.navigate([locale, routePath]).then(() => {
      // Reload to apply translations
      window.location.reload();
    });
  }
}
