import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { LanguageService } from '../../../services/language.service';

/**
 * Service for loading I18n translations for UC-00 (Interoperability)
 */
@Injectable({ providedIn: 'root' })
export class Uc00I18nService {
  private translationsCache: Map<string, Record<string, string>> = new Map();
  
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
      const messagesPath = `locale/messages.${loadLocale}.json`;
      const messagesResponse = await firstValueFrom(this.http.get<{ locale: string; translations: Record<string, string> }>(messagesPath));
      const messages = messagesResponse.translations || messagesResponse as unknown as Record<string, string>;
      const uc00Texts: Record<string, string> = {};
      Object.keys(messages).forEach((key) => {
        if (key.startsWith('@@uc00')) {
          uc00Texts[key.replace(/^@@/, '')] = messages[key];
        }
      });
      if (locale === 'en') {
        Object.assign(uc00Texts, this.getEnglishTranslations());
      }
      this.translationsCache.set(locale, uc00Texts);
      return uc00Texts;
    } catch (error) {
      console.error('Failed to load UC-00 translations:', error);
      return locale === 'en' ? this.getEnglishTranslations() : {};
    }
  }
  
  private getEnglishTranslations(): Record<string, string> {
    return {
      'uc00.title': 'Interoperability: Event-to-Process Map',
      'uc00.subtitle': 'Turn shopfloor events into a process-ready view through normalization and context.',
      'uc00.sources.header': 'Sources: events & signals',
      'uc00.lane.business_context.title': 'Business context (ERP/MES)',
      'uc00.chip.production_order': 'Production order',
      'uc00.chip.production_order.line1': 'Production',
      'uc00.chip.production_order.line2': 'order',
      'uc00.chip.storage_order': 'Storage Order',
      'uc00.chip.storage_order.line1': 'Storage',
      'uc00.chip.storage_order.line2': 'Order',
      'uc00.chip.material': 'Material',
      'uc00.chip.customer': 'Customer',
      'uc00.chip.routing': 'Routing',
      'uc00.chip.operation': 'Operation',
      'uc00.lane.machine_station.title': 'Machine / station / device',
      'uc00.chip.operation_label': 'Operation:',
      'uc00.chip.start': 'Start',
      'uc00.chip.stop': 'Stop',
      'uc00.chip.state_label': 'State:',
      'uc00.chip.running': 'Running',
      'uc00.chip.idle': 'Idle',
      'uc00.chip.fail': 'Fail',
      'uc00.lane.agv_system.title': 'AGV / system',
      'uc00.chip.pick': 'PICK',
      'uc00.chip.transfer': 'TRANSFER',
      'uc00.chip.drop': 'DROP',
      'uc00.chip.route': 'Route',
      'uc00.lane.quality_aiqs.title': 'Quality (AIQS)',
      'uc00.chip.check_quality': 'CHECK_QUALITY:',
      'uc00.chip.pass': 'Pass',
      'uc00.lane.environment_sensors.title': 'Environment / sensors',
      'uc00.chip.temperature': 'Temperature',
      'uc00.chip.energy': 'Energy',
      'uc00.chip.vibration': 'Vibration',
      'uc00.chip.pressure': 'Pressure',
      'uc00.dsp.header': 'DSP: Normalize + context + correlate',
      'uc00.step.normalize.title': 'Normalize (semantics & format)',
      'uc00.step.normalize.description': 'Canonicalize events across protocols and data models',
      'uc00.step.enrich.title': 'Enrich context (order, workpiece, station, time)',
      'uc00.step.enrich.description': 'Link events to process context',
      'uc00.step.correlate.title': 'Correlate (event chain → process step)',
      'uc00.step.correlate.description': 'Map event chains into interpretable steps',
      'uc00.bar.process_ready': 'Events + context = process readiness',
      'uc00.bar.reusable': 'Reusable instead of point-to-point',
      'uc00.bar.foundation': 'Foundation for traceability, KPIs & closed loops',
      'uc00.bar.foundation.line1': 'Foundation for traceability, KPIs',
      'uc00.bar.foundation.line2': '& closed loops',
      'uc00.targets.header': 'Process view & target systems',
      'uc00.section.process_view': 'Process View',
      'uc00.section.target_systems': 'Target systems',
      'uc00.section.use_cases': 'Use-Cases',
      'uc00.process_view.title': 'Event-to-Process Map',
      'uc00.timeline.warehouse': 'Warehouse',
      'uc00.timeline.agv': 'AGV',
      'uc00.timeline.station': 'Station',
      'uc00.timeline.transfer': 'Transfer',
      'uc00.timeline.quality': 'Quality',
      'uc00.timeline.complete': 'Complete',
      'uc00.target.erp': 'ERP',
      'uc00.target.mes': 'MES',
      'uc00.target.analytics_ai': 'Analytics / AI',
      'uc00.targets.note': 'Best-of-breed: SAP may be an example, but it is not a prerequisite.',
      'uc00.outcome': 'Outcome: Process Efficiency & Latency Reduction',
      'uc00.outcome.uc01': 'Track & Trace',
      'uc00.outcome.uc02': 'Data Aggregation',
      'uc00.outcome.uc03': 'AI Lifecycle',
      'uc00.outcome.uc04.line1': 'Closed Loop',
      'uc00.outcome.uc04.line2': 'Quality',
      'uc00.outcome.uc05.line1': 'Predictive',
      'uc00.outcome.uc05.line2': 'Maintenance',
      'uc00.outcome.uc06.line1': 'Process',
      'uc00.outcome.uc06.line2': 'Optimization',
      'uc00.footer': 'Combines events from machines, AGVs, quality, and business context into one shared process view.',
    };
  }
}
