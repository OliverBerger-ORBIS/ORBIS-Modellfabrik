import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { LanguageService } from '../../../services/language.service';
import { getAssetPath } from '../../../assets/detail-asset-map';

/**
 * Service for loading I18n translations for UC-04 Closed Loop Quality
 */
@Injectable({ providedIn: 'root' })
export class Uc04I18nService {
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

      const texts: Record<string, string> = { ...this.getEnglishTranslations() };
      Object.keys(messages).forEach((key) => {
        if (key.startsWith('@@uc04')) {
          const k = key.replace(/^@@/, '');
          texts[k] = messages[key];
        }
      });

      this.translationsCache.set(locale, texts);
      return texts;
    } catch (error) {
      console.error('Failed to load UC-04 translations:', error);
      return this.getEnglishTranslations();
    }
  }

  private getEnglishTranslations(): Record<string, string> {
    return {
      'uc04.title': 'Closed Loop Quality',
      'uc04.subtitle': 'Quality Inspection Event → Decide → Act → Feedback to MES/ERP/Analytics',
      'uc04.outcome': 'Outcome: Closed Loop Quality (FPY)',
      'uc04.lane.process': 'Process Data & Quality Flow',
      'uc04.lane.mixed': 'DSP Edge | Quality Event | Target',
      'uc04.lane.shopfloor': 'Shopfloor Sources & Devices',

      'uc04.proc.detect': 'Detect',
      'uc04.proc.detect.bullets': 'Nonconformance / inspection results\nAIQS / quality stations',

      'uc04.proc.decide': 'Decide',
      'uc04.proc.decide.bullets': 'Rules & policies\nContext-based decisions',

      'uc04.proc.act': 'Act',
      'uc04.proc.act.bullets': 'Block / Rework / Rebuild\nConditional release',

      'uc04.proc.feedback': 'Feedback',
      'uc04.proc.feedback.bullets': 'MES / ERP / Analytics\nAuditable traceability',

      'uc04.mixed.dspEdge': 'DSP Edge',
      'uc04.mixed.dspEdge.bullets': 'Event normalization\nContext enrichment',

      'uc04.mixed.qualityEvent': 'Quality Event',
      'uc04.mixed.qualityEvent.sub': 'Inspection result with context',

      'uc04.mixed.target': 'Target',
      'uc04.mixed.target.bullets': 'MES / ERP / Analytics\nBest-of-Breed',
      'uc04.mixed.target.mes': 'MES',
      'uc04.mixed.target.erp': 'ERP',
      'uc04.mixed.target.analytics': 'Analytics',

      'uc04.sf.productionOrder': 'Production Order',
      'uc04.sf.aiqs': 'AIQS Station',
      'uc04.sf.systemsDevicesTitle': 'Systems & Devices',
      'uc04.sf.systemsLabel': 'Systems',
      'uc04.sf.devicesLabel': 'Devices',

      'uc04.conn.qualityEvents': 'Quality events',
      'uc04.conn.qualityEvent': 'Quality event',
      'uc04.conn.action': 'Action',
      'uc04.feedback': 'Feedback',
      'uc04.footer': 'OSF is a demonstrator showcasing integration principles; productive implementations depend on the customer\'s target landscape.',
    };
  }
}
