import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { LanguageService } from '../../../services/language.service';

/**
 * Service for loading I18n translations for UC-06
 */
@Injectable({ providedIn: 'root' })
export class Uc06I18nService {
  private translationsCache: Map<string, Record<string, string>> = new Map();
  
  constructor(
    private readonly http: HttpClient,
    private readonly languageService: LanguageService
  ) {}
  
  /**
   * Load all I18n texts for UC-06
   */
  async loadTexts(): Promise<Record<string, string>> {
    const locale = this.languageService.current;
    
    // Check cache
    if (this.translationsCache.has(locale)) {
      return this.translationsCache.get(locale)!;
    }
    
    try {
      // Load messages.json for current locale (fallback to DE for EN)
      const loadLocale = locale === 'en' ? 'de' : locale;
      const messagesPath = `locale/messages.${loadLocale}.json`;
      const messages = await firstValueFrom(this.http.get<Record<string, string>>(messagesPath));
      
      // Extract UC-06 keys (keys starting with @@uc06)
      const uc06Texts: Record<string, string> = {};
      Object.keys(messages).forEach((key) => {
        if (key.startsWith('@@uc06')) {
          // Remove @@ prefix for internal use
          const internalKey = key.replace(/^@@/, '');
          uc06Texts[internalKey] = messages[key];
        }
      });
      
      // For EN locale, replace with English translations
      if (locale === 'en') {
        const enTexts = this.getEnglishTranslations();
        Object.assign(uc06Texts, enTexts);
      }
      
      // Cache translations
      this.translationsCache.set(locale, uc06Texts);
      
      return uc06Texts;
    } catch (error) {
      console.error('Failed to load UC-06 translations:', error);
      // Return English as fallback
      return locale === 'en' ? this.getEnglishTranslations() : {};
    }
  }
  
  /**
   * English translations for UC-06 (fallback when EN file doesn't exist)
   */
  private getEnglishTranslations(): Record<string, string> {
    return {
      'uc06.title': 'Interoperability: Event-to-Process Map',
      'uc06.subtitle': 'Turn shopfloor events into a process-ready view through normalization and context.',
      'uc06.sources.header': 'Sources: events & signals',
      'uc06.lane.business_context.title': 'Business context (ERP/MES)',
      'uc06.chip.production_order': 'Production order',
      'uc06.chip.production_order.line1': 'Production',
      'uc06.chip.production_order.line2': 'order',
      'uc06.chip.storage_order': 'Storage Order',
      'uc06.chip.storage_order.line1': 'Storage',
      'uc06.chip.storage_order.line2': 'Order',
      'uc06.chip.material': 'Material',
      'uc06.chip.customer': 'Customer',
      'uc06.chip.routing': 'Routing',
      'uc06.chip.operation': 'Operation',
      'uc06.lane.machine_station.title': 'Machine / station / device',
      'uc06.chip.operation_label': 'Operation:',
      'uc06.chip.start': 'Start',
      'uc06.chip.stop': 'Stop',
      'uc06.chip.state_label': 'State:',
      'uc06.chip.running': 'Running',
      'uc06.chip.idle': 'Idle',
      'uc06.chip.fail': 'Fail',
      'uc06.lane.agv_system.title': 'AGV / system',
      'uc06.chip.pick': 'PICK',
      'uc06.chip.transfer': 'TRANSFER',
      'uc06.chip.drop': 'DROP',
      'uc06.chip.route': 'Route',
      'uc06.lane.quality_aiqs.title': 'Quality (AIQS)',
      'uc06.chip.check_quality': 'CHECK_QUALITY:',
      'uc06.chip.pass': 'Pass',
      'uc06.lane.environment_sensors.title': 'Environment / sensors',
      'uc06.chip.temperature': 'Temperature',
      'uc06.chip.energy': 'Energy',
      'uc06.chip.vibration': 'Vibration',
      'uc06.chip.pressure': 'Pressure',
      'uc06.dsp.header': 'DSP: Normalize + context + correlate',
      'uc06.step.normalize.title': 'Normalize (semantics & format)',
      'uc06.step.normalize.description': 'Canonicalize events across protocols and data models',
      'uc06.step.enrich.title': 'Enrich context (order, workpiece, station, time)',
      'uc06.step.enrich.description': 'Link events to process context',
      'uc06.step.correlate.title': 'Correlate (event chain → process step)',
      'uc06.step.correlate.description': 'Map event chains into interpretable steps',
      'uc06.bar.process_ready': 'Events + context = process readiness',
      'uc06.bar.reusable': 'Reusable instead of point-to-point',
      'uc06.bar.foundation': 'Foundation for traceability, KPIs & closed loops',
      'uc06.bar.foundation.line1': 'Foundation for traceability, KPIs',
      'uc06.bar.foundation.line2': '& closed loops',
      'uc06.targets.header': 'Process view & target systems',
      'uc06.process_view.title': 'Event-to-Process Map',
      'uc06.timeline.warehouse': 'Warehouse',
      'uc06.timeline.agv': 'AGV',
      'uc06.timeline.station': 'Station',
      'uc06.timeline.transfer': 'Transfer',
      'uc06.timeline.quality': 'Quality',
      'uc06.timeline.complete': 'Complete',
      'uc06.target.erp': 'ERP',
      'uc06.target.mes': 'MES',
      'uc06.target.analytics_ai': 'Analytics / AI',
      'uc06.targets.note': 'Best-of-breed: SAP may be an example, but it is not a prerequisite.',
      'uc06.outcome.traceability': 'Traceability / genealogy',
      'uc06.outcome.kpi': 'KPI calculation (lead time, downtime, OEE building blocks)',
      'uc06.outcome.kpi.line1': 'KPI calculation',
      'uc06.outcome.kpi.line2': '(lead time, downtime, OEE building blocks)',
      'uc06.outcome.closed_loop': 'Closed-loop orchestration',
      'uc06.footer': 'Combines events from machines, AGVs, quality, and business context into one shared process view.',
    };
  }
}
