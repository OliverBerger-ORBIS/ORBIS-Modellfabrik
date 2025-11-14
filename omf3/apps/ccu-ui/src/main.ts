import '@angular/localize/init';

import { ɵsetLocaleId as setLocaleId } from '@angular/core';
import { loadTranslations } from '@angular/localize';
import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

type LocaleKey = 'en' | 'de' | 'fr';

const LOCALE_STORAGE_KEY = 'omf3.locale';

async function loadLocaleFile(locale: LocaleKey): Promise<Record<string, string>> {
  const response = await fetch(`locale/messages.${locale}.json`);
  if (!response.ok) {
    throw new Error(`Failed to load translations for ${locale}`);
  }
  const json = await response.json();
  return json.translations ?? json.default?.translations ?? json;
}

async function prepareLocale(): Promise<void> {
  const storedLocale = (localStorage?.getItem(LOCALE_STORAGE_KEY) as LocaleKey | null) ?? 'en';
  console.log('[locale] Stored locale:', storedLocale);
  
  if (storedLocale === 'en') {
    setLocaleId('en');
    console.log('[locale] Using English (default)');
    return;
  }

  try {
    console.log('[locale] Loading translations for:', storedLocale);
    const translations = await loadLocaleFile(storedLocale);
    console.log('[locale] Translations loaded, keys:', Object.keys(translations).length);
    loadTranslations(translations);
    setLocaleId(storedLocale);
    console.log('[locale] Locale set to:', storedLocale);
  } catch (error) {
    console.error('[locale] Failed to load translations for', storedLocale, error);
    setLocaleId('en');
    console.log('[locale] Fallback to English due to error');
  }
}

prepareLocale()
  .finally(() => {
    bootstrapApplication(AppComponent, appConfig).catch((err) => console.error(err));
  })
  .catch((err) => console.error(err));
