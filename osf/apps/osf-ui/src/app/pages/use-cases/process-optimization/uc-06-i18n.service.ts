import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { LanguageService } from '../../../services/language.service';
import { getAssetPath } from '../../../assets/detail-asset-map';

/**
 * Service for loading I18n translations for UC-06 Process Optimization
 */
@Injectable({ providedIn: 'root' })
export class Uc06I18nService {
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
        if (key.startsWith('@@uc06')) {
          const k = key.replace(/^@@/, '');
          texts[k] = messages[key];
        }
      });

      this.translationsCache.set(locale, texts);
      return texts;
    } catch (error) {
      console.error('Failed to load UC-06 translations:', error);
      return this.getEnglishTranslations();
    }
  }

  private getEnglishTranslations(): Record<string, string> {
    return {
      'uc06.title': 'Process Optimization',
      'uc06.subtitle': 'Observe → Analyze → Recommend → Simulate → Execute → Feedback (KPI-to-Action Loop)',
      'uc06.outcome': 'Outcome: Process Optimization',
      'uc06.lane.process': 'Optimization Loop',
      'uc06.lane.shopfloor': 'Shopfloor Sources & Targets',

      'uc06.proc.observe': 'Observe',
      'uc06.proc.observe.bullets': 'KPIs, cycle times\nMachine utilization',

      'uc06.proc.analyze': 'Analyze',
      'uc06.proc.analyze.bullets': 'Bottleneck analysis\nRoot-cause indicators',

      'uc06.proc.recommend': 'Recommend',
      'uc06.proc.recommend.bullets': 'AI recommendations\nParameters, sequence, takt',

      'uc06.proc.simulate': 'Simulate',
      'uc06.proc.simulate.bullets': 'What-if scenarios\nBefore physical changes',

      'uc06.proc.execute': 'Execute',
      'uc06.proc.execute.bullets': 'DSP executors\nMES workflows',

      'uc06.proc.feedback': 'Feedback',
      'uc06.proc.feedback.bullets': 'Improved KPIs\nBack to Observe',

      'uc06.mixed.dsp': 'DSP',
      'uc06.mixed.dsp.bullets': 'Analytics & bottleneck analysis\nContext enrichment',

      'uc06.mixed.recommend': 'Recommendation\n& Simulation',
      'uc06.mixed.recommend.sub': 'AI + What-if',

      'uc06.mixed.target': 'Target',
      'uc06.mixed.target.bullets': 'MES / ERP / Planning\nBest-of-Breed',
      'uc06.mixed.target.mes': 'MES',
      'uc06.mixed.target.erp': 'ERP',
      'uc06.mixed.target.planning': 'Planning',

      'uc06.sf.sourcesTitle': 'Shopfloor (Sources)',
      'uc06.sf.targetsTitle': 'Shopfloor (Targets)',
      'uc06.sf.systemsLabel': 'Systems',
      'uc06.sf.devicesLabel': 'Devices',

      'uc06.conn.kpis': 'KPIs & context',
      'uc06.conn.recommendation': 'Recommendation',
      'uc06.conn.action': 'Execute',
      'uc06.feedback': 'Feedback',
      'uc06.footer': 'OSF is a demonstrator and not a productive system.',
    };
  }
}
