import { Injectable } from '@angular/core';

export type LocaleKey = 'en' | 'de' | 'fr';

const STORAGE_KEY = 'omf3.locale';

@Injectable({ providedIn: 'root' })
export class LanguageService {
  readonly supportedLocales: LocaleKey[] = ['en', 'de', 'fr'];

  get current(): LocaleKey {
    return (localStorage?.getItem(STORAGE_KEY) as LocaleKey | null) ?? 'en';
  }

  setLocale(locale: LocaleKey): void {
    if (locale === this.current) {
      return;
    }
    localStorage?.setItem(STORAGE_KEY, locale);
    // Force a complete page reload to ensure main.ts re-executes and loads the correct locale
    location.reload();
  }
}
