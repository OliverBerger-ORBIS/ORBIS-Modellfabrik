// Import @angular/localize/init explicitly to control initialization order
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
  const translations = json.translations ?? json.default?.translations ?? json;
  
  // Convert @@key format to key format for loadTranslations API
  const formattedTranslations: Record<string, string> = {};
  for (const [key, value] of Object.entries(translations)) {
    // Remove @@ prefix if present
    const normalizedKey = key.startsWith('@@') ? key.slice(2) : key;
    formattedTranslations[normalizedKey] = value as string;
  }
  
  return formattedTranslations;
}

function getLocaleFromUrl(): LocaleKey {
  const pathSegments = window.location.pathname.split('/').filter(Boolean);
  const localeFromUrl = pathSegments[0] as LocaleKey;
  const supportedLocales: LocaleKey[] = ['en', 'de', 'fr'];
  if (supportedLocales.includes(localeFromUrl)) {
    return localeFromUrl;
  }
  return 'en';
}

async function prepareLocale(): Promise<void> {
  // Priority: URL > localStorage > default 'en'
  const urlLocale = getLocaleFromUrl();
  
  // URL has highest priority
  const targetLocale = urlLocale;
  
  // Store in localStorage for next visit
  localStorage?.setItem(LOCALE_STORAGE_KEY, targetLocale);
  
  // Set locale ID for Angular FIRST
  setLocaleId(targetLocale);
  
  // Load translations for non-English locales
  if (targetLocale !== 'en') {
    try {
      const translations = await loadLocaleFile(targetLocale);
      loadTranslations(translations);
    } catch (error) {
      console.warn('[locale] Failed to load translations for', targetLocale, error);
    }
  }
}

prepareLocale()
  .then(() => {
    return bootstrapApplication(AppComponent, appConfig);
  })
  .catch((err) => console.error(err));
