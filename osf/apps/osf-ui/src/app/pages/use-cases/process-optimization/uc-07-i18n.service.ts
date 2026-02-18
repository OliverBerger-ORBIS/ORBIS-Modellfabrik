import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { LanguageService } from '../../../services/language.service';
import { getAssetPath } from '../../../assets/detail-asset-map';

/**
 * Service for loading I18n translations for UC-07 Process Optimization
 */
@Injectable({ providedIn: 'root' })
export class Uc07I18nService {
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
        if (key.startsWith('@@uc07')) {
          const k = key.replace(/^@@/, '');
          texts[k] = messages[key];
        }
      });

      this.translationsCache.set(locale, texts);
      return texts;
    } catch (error) {
      console.error('Failed to load UC-07 translations:', error);
      return this.getEnglishTranslations();
    }
  }

  private getEnglishTranslations(): Record<string, string> {
    return {
      'uc07.title': 'UC-07 — Process Optimization',
      'uc07.subtitle': 'Observe → Analyze → Recommend → Simulate → Execute → Feedback (KPI-to-Action Loop)',

      'uc07.lane.process': 'Optimization Loop',
      'uc07.lane.shopfloor': 'Shopfloor Sources & Targets',

      'uc07.proc.observe': 'Observe',
      'uc07.proc.observe.bullets': 'KPIs, cycle times\nMachine utilization',

      'uc07.proc.analyze': 'Analyze',
      'uc07.proc.analyze.bullets': 'Bottleneck analysis\nRoot-cause indicators',

      'uc07.proc.recommend': 'Recommend',
      'uc07.proc.recommend.bullets': 'AI recommendations\nParameters, sequence, takt',

      'uc07.proc.simulate': 'Simulate',
      'uc07.proc.simulate.bullets': 'What-if scenarios\nBefore physical changes',

      'uc07.proc.execute': 'Execute',
      'uc07.proc.execute.bullets': 'DSP executors\nMES workflows',

      'uc07.proc.feedback': 'Feedback',
      'uc07.proc.feedback.bullets': 'Improved KPIs\nBack to Observe',

      'uc07.mixed.dsp': 'DSP',
      'uc07.mixed.dsp.bullets': 'Analytics & bottleneck analysis\nContext enrichment',

      'uc07.mixed.recommend': 'Recommendation\n& Simulation',
      'uc07.mixed.recommend.sub': 'AI + What-if',

      'uc07.mixed.target': 'Target',
      'uc07.mixed.target.bullets': 'MES / ERP / Planning\nBest-of-Breed',
      'uc07.mixed.target.mes': 'MES',
      'uc07.mixed.target.erp': 'ERP',
      'uc07.mixed.target.planning': 'Planning',

      'uc07.sf.sourcesTitle': 'Shopfloor (Sources)',
      'uc07.sf.targetsTitle': 'Shopfloor (Targets)',
      'uc07.sf.systemsLabel': 'Systems',
      'uc07.sf.devicesLabel': 'Devices',

      'uc07.conn.kpis': 'KPIs & context',
      'uc07.conn.recommendation': 'Recommendation',
      'uc07.conn.action': 'Execute',
      'uc07.feedback': 'Feedback',
    };
  }
}
