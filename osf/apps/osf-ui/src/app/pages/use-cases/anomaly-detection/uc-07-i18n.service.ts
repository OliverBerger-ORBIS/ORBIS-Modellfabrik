import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { LanguageService } from '../../../services/language.service';
import { getAssetPath } from '../../../assets/detail-asset-map';

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
        if (key.startsWith('uc07.') || key.startsWith('@@uc07')) {
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
      'uc07.title': 'Anomaly Detection',
      'uc07.subtitle': 'Vibration alarm flow: Detect → Validate → Alarm → Route to CRM → CRM workflow start',
      'uc07.outcome': 'Outcome: Fast anomaly escalation to CRM',
      'uc07.lane.process': 'Process Data & Alarm Flow',
      'uc07.lane.shopfloor': 'Shopfloor Trigger & Sensors',

      'uc07.proc.detect': 'Detect',
      'uc07.proc.detect.bullets': 'Vibration and tilt signals\nEvent trigger',
      'uc07.proc.validate': 'Validate',
      'uc07.proc.validate.bullets': 'Rule checks at DSP Edge\nContext enrichment',
      'uc07.proc.alarm': 'Alarm',
      'uc07.proc.alarm.bullets': 'Alarm event emission\nSeverity and correlation',
      'uc07.proc.route': 'Route',
      'uc07.proc.route.bullets': 'Forward to Microsoft CRM\nTarget mapping',
      'uc07.proc.feedback': 'CRM Start',
      'uc07.proc.feedback.bullets': 'Workflow is started in CRM\nCustomer-specific handling',

      'uc07.mixed.dspEdge': 'DSP Edge',
      'uc07.mixed.dspEdge.bullets': 'Rule and event processing\nLow-latency routing',
      'uc07.mixed.alarm': 'ALARM',
      'uc07.mixed.alarm.sub': 'Event emission',
      'uc07.mixed.target': 'Target',
      'uc07.mixed.target.bullets': 'Microsoft CRM\nWorkflow starts there',
      'uc07.mixed.target.crm': 'CRM',

      'uc07.sf.trigger': 'Trigger',
      'uc07.sf.vibrationSensor': 'Vibration + Tilt',
      'uc07.sf.systemsDevicesTitle': 'Systems & Devices',
      'uc07.sf.systemsLabel': 'Systems',
      'uc07.sf.devicesLabel': 'Devices',

      'uc07.conn.signals': 'Signals',
      'uc07.conn.alarmEvent': 'Alarm Event',
      'uc07.conn.productionPause': 'Operational response',
      'uc07.feedback': 'CRM process started',
      'uc07.footer': 'After DSP forwards the event, workflow behavior is configured inside CRM (automatic, semi-automatic, or manual).',
    };
  }
}
