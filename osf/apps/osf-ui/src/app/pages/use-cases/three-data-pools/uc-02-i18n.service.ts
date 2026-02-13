import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { LanguageService } from '../../../services/language.service';
import { getAssetPath } from '../../../assets/detail-asset-map';

/**
 * Service for loading I18n translations for UC-02 Three Data Pools
 */
@Injectable({ providedIn: 'root' })
export class Uc02I18nService {
  private translationsCache = new Map<string, Record<string, string>>();

  constructor(
    private readonly http: HttpClient,
    private readonly languageService: LanguageService
  ) {}

  async loadTexts(): Promise<Record<string, string>> {
    const locale = this.languageService.current;

    if (this.translationsCache.has(locale)) {
      return this.translationsCache.get(locale)!;
    }

    try {
      const loadLocale = locale === 'en' ? 'de' : locale;
      const messagesPath = getAssetPath(`locale/messages.${loadLocale}.json`);
      const messagesResponse = await firstValueFrom(
        this.http.get<{ locale: string; translations: Record<string, string> }>(messagesPath)
      );
      const messages = messagesResponse.translations || (messagesResponse as unknown as Record<string, string>);

      const texts: Record<string, string> = {};
      Object.keys(messages).forEach((key) => {
        if (key.startsWith('@@uc02')) {
          texts[key.replace(/^@@/, '')] = messages[key];
        }
      });

      if (locale === 'en') {
        Object.assign(texts, this.getEnglishTranslations());
      }

      this.translationsCache.set(locale, texts);
      return texts;
    } catch (error) {
      console.error('Failed to load UC-02 translations:', error);
      // Always return at least English fallback so IDs are never shown
      return this.getEnglishTranslations();
    }
  }

  private getEnglishTranslations(): Record<string, string> {
    return {
      'uc02.title': 'Data Aggregation: Three Data Pools for Reliable KPIs',
      'uc02.subtitle': 'Business + Shopfloor + Environment: only the combination makes KPIs explainable and actionable.',
      'uc02.dsp.header': 'DSP Context Model & Mediation',
      'uc02.src.business': 'Business Data',
      'uc02.src.business.sub': 'ERP, Order, Material',
      'uc02.src.shopfloor': 'Shopfloor Data',
      'uc02.src.shopfloor.sub': 'Events, FTS, Quality',
      'uc02.src.env': 'Environment Data',
      'uc02.src.env.sub': 'Energy, Temp, Vibration',
      'uc02.step.normalize': '1. Normalize',
      'uc02.step.normalize.sub': 'Units, Formats',
      'uc02.step.enrich': '2. Enrich',
      'uc02.step.enrich.sub': 'Add Content',
      'uc02.step.correlate': '3. Correlate',
      'uc02.step.correlate.sub': 'Link Data',
      'uc02.note.context': 'Order ↔ Workpiece-ID ↔ Station',
      'uc02.tgt.analytics': 'Analytics & AI App',
      'uc02.tgt.bi': 'BI / Data Lake',
      'uc02.tgt.closed_loop': 'Closed Loop / ERP',
      'uc02.feedback': 'Feedback',
      'uc02.footer': 'OSF is a demonstrator showcasing integration principles; productive implementations depend on the customer\'s target landscape.',
      'uc02.lane.analytics': 'Analytics & Value Layer',
      'uc02.lane.dsp': 'DSP Context Model & Mediation',
      'uc02.lane.data': 'Data Layer',
    };
  }
}
