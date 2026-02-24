import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { LanguageService } from '../../../services/language.service';
import { getAssetPath } from '../../../assets/detail-asset-map';

/**
 * Service for loading I18n translations for UC-03 AI Lifecycle
 */
@Injectable({ providedIn: 'root' })
export class Uc03I18nService {
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
        if (key.startsWith('@@uc03')) {
          const k = key.replace(/^@@/, '');
          texts[k] = messages[key];
        }
      });

      this.translationsCache.set(locale, texts);
      return texts;
    } catch (error) {
      console.error('Failed to load UC-03 translations:', error);
      return this.getEnglishTranslations();
    }
  }

  private getEnglishTranslations(): Record<string, string> {
    return {
      'uc03.title': 'AI Lifecycle',
      'uc03.subtitle': 'Train centrally, deploy to multiple stations via DSP Edge + Management Cockpit',
      'uc03.outcome': 'Outcome: AI Lifecycle',
      'uc03.lane.process': 'Process Data & Model Lifecycle',
      'uc03.lane.dsp': 'DSP Context Model & Mediation',
      'uc03.lane.shopfloor': 'Shopfloor Systems & Devices',

      'uc03.proc.capture': 'Data Capture',
      'uc03.proc.capture.bullets': 'Shopfloor Events & Signals\nRaw sensor data\nQuality events',

      'uc03.proc.context': 'Context',
      'uc03.proc.context.bullets': 'Order / Workpiece / Station\nBusiness context\nTime enrichment',

      'uc03.proc.train': 'Train (Cloud)',
      'uc03.proc.train.bullets': 'Training pipeline\nModel evaluation\nPackaging',

      'uc03.proc.validate': 'Validate',
      'uc03.proc.validate.bullets': 'Test sets\nPerformance metrics\nRelease approval',

      'uc03.proc.monitor': 'Monitor & Feedback',
      'uc03.proc.monitor.bullets': 'Quality/latency/drift\nTelemetry & labels\nRetrain trigger',

      'uc03.dsp.edge1': 'DSP Edge 1',
      'uc03.dsp.edge2': 'DSP Edge 2',
      'uc03.dsp.edge.bullets': 'Model runtime\nStation interfaces',

      'uc03.dsp.cockpit': 'DSP Management Cockpit',
      'uc03.dsp.cockpit.bullets': 'Model registry & rollout\nApprovals & rollback',

      'uc03.sf.shopfloor1': 'Shopfloor 1',
      'uc03.sf.shopfloor2': 'Shopfloor 2',
      'uc03.sf.systemsLabel': 'Systems',
      'uc03.sf.devicesLabel': 'Devices',

      'uc03.feedback': 'Feedback',
      'uc03.conn.dspProcess': 'DSP ↔ Process',
      'uc03.footer': 'OSF is a demonstrator showcasing integration principles; productive implementations depend on the customer\'s target landscape.',
    };
  }
}
