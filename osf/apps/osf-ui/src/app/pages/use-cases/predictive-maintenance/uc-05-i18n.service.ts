import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { LanguageService } from '../../../services/language.service';
import { getAssetPath } from '../../../assets/detail-asset-map';

/**
 * Service for loading I18n translations for UC-05 Predictive Maintenance
 */
@Injectable({ providedIn: 'root' })
export class Uc05I18nService {
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
        if (key.startsWith('@@uc05')) {
          const k = key.replace(/^@@/, '');
          texts[k] = messages[key];
        }
      });

      this.translationsCache.set(locale, texts);
      return texts;
    } catch (error) {
      console.error('Failed to load UC-05 translations:', error);
      return this.getEnglishTranslations();
    }
  }

  private getEnglishTranslations(): Record<string, string> {
    return {
      'uc05.title': 'Predictive Maintenance',
      'uc05.subtitle': 'Condition monitoring: Detect vibrations → Evaluate → Alarm → Act → Feedback',

      'uc05.lane.process': 'Process Data & Alarm Flow',
      'uc05.lane.mixed': 'DSP Edge | Alarm | Target',
      'uc05.lane.shopfloor': 'Shopfloor Trigger & Sensors',

      'uc05.proc.detect': 'Detect',
      'uc05.proc.detect.bullets': 'Vibration / sensor signals\nAnomaly detection',

      'uc05.proc.evaluate': 'Evaluate',
      'uc05.proc.evaluate.bullets': 'Thresholds & rules\nDSP Edge analytics',

      'uc05.proc.alarm': 'Alarm',
      'uc05.proc.alarm.bullets': 'Event emission\nEscalation',

      'uc05.proc.action': 'Act',
      'uc05.proc.action.bullets': 'Stop / Safe-State\nOptional automation',

      'uc05.proc.feedback': 'Feedback',
      'uc05.proc.feedback.bullets': 'MES / ERP / Analytics\nMaintenance scheduling',

      'uc05.mixed.dspEdge': 'DSP Edge',
      'uc05.mixed.dspEdge.bullets': 'Rule & threshold evaluation\nReal-time analytics',

      'uc05.mixed.alarm': 'ALARM',
      'uc05.mixed.alarm.sub': 'Event emission',

      'uc05.mixed.target': 'Target',
      'uc05.mixed.target.bullets': 'MES / ERP / Analytics\nBest-of-Breed',
      'uc05.mixed.target.mes': 'MES',
      'uc05.mixed.target.erp': 'ERP',
      'uc05.mixed.target.analytics': 'Analytics',

      'uc05.sf.title': 'Trigger & Sensors',
      'uc05.sf.systemsDevicesTitle': 'Systems & Devices',
      'uc05.sf.trigger': 'Trigger',
      'uc05.sf.detector': 'Detector',
      'uc05.sf.vibrationSensor': 'Vibration Sensor',
      'uc05.sf.sensorLabel': 'Sensors',
      'uc05.sf.systemsLabel': 'Systems',
      'uc05.sf.devicesLabel': 'Devices',

      'uc05.conn.signals': 'Signals',
      'uc05.conn.alarmEvent': 'Alarm Event',
      'uc05.conn.productionPause': 'Production pause',
      'uc05.feedback': 'Feedback',
    };
  }
}
