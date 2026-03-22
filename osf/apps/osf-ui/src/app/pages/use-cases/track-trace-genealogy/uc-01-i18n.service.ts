import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { LanguageService } from '../../../services/language.service';

/**
 * Service for loading I18n translations for UC-01 Track & Trace Genealogy (Partiture layout)
 */
@Injectable({ providedIn: 'root' })
export class Uc01I18nService {
  private translationsCache: Map<string, Record<string, string>> = new Map();

  constructor(
    private readonly http: HttpClient,
    private readonly languageService: LanguageService
  ) {}

  /**
   * Load all I18n texts for UC-01
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
      const messagesResponse = await firstValueFrom(
        this.http.get<{ locale: string; translations: Record<string, string> }>(messagesPath)
      );

      // Extract translations object (messages.json has nested structure)
      const messages = messagesResponse.translations || messagesResponse as unknown as Record<string, string>;

      // Extract UC-01 keys (keys starting with @@uc01)
      const uc01Texts: Record<string, string> = {};
      Object.keys(messages).forEach((key) => {
        if (key.startsWith('uc01.') || key.startsWith('@@uc01')) {
          const internalKey = key.replace(/^@@/, '');
          uc01Texts[internalKey] = messages[key];
        }
      });

      const enTexts = this.getEnglishTranslations();
      // EN: prefer explicit English map over DE file
      if (locale === 'en') {
        Object.assign(uc01Texts, enTexts);
      } else {
        // DE/FR/etc.: fill gaps (e.g. new uc01.join.* keys) so IDs and labels never disappear
        for (const k of Object.keys(enTexts)) {
          const v = uc01Texts[k];
          if (v === undefined || v === '') {
            uc01Texts[k] = enTexts[k];
          }
        }
      }

      // Cache translations
      this.translationsCache.set(locale, uc01Texts);

      return uc01Texts;
    } catch (error) {
      console.error('Failed to load UC-01 translations:', error);
      // Return English as fallback
      const fallback = locale === 'en' ? this.getEnglishTranslations() : {};
      return fallback;
    }
  }

  /**
   * English translations for UC-01 Partiture layout
   */
  private getEnglishTranslations(): Record<string, string> {
    return {
      // Title & Subtitle
      'uc01.title': 'Track & Trace — SinglePart (NFC)',
      'uc01.subtitle': 'Business Context + Trace + Enrichment',
      'uc01.outcome': 'Outcome: Traceability Coverage (100%)',
      // Lanes
      'uc01.lane.business': 'Business Context',
      'uc01.lane.trace': 'Trace & Genealogy',
      'uc01.lane.shopfloor': 'Shopfloor & Enrichment',
      // Time arrow
      'uc01.time_arrow': 'Time →',
      // NFC Thread (two lines in SVG)
      'uc01.thread.line1': 'NFC [UID-1234]',
      'uc01.thread.line2': 'Single-part thread',
      // Join correlation IDs (on dashed lines, Business → Trace)
      'uc01.join.id.po': '[PO-ID]',
      'uc01.join.id.so': '[SO-ID]',
      'uc01.join.id.co': '[CO-ID]',
      'uc01.join.id.prod': '[PROD-ID]',
      // Station Nodes
      'uc01.node.dps': 'DPS',
      'uc01.node.mill_par': '(MILL)',
      'uc01.node.hbw': 'HBW',
      'uc01.node.aiqs_par': '(AIQS)',
      'uc01.node.drill': 'DRILL',
      'uc01.node.dps_par': '(DPS)',
      'uc01.node.aiqs': 'AIQS',
      'uc01.node.dps_out': 'DPS',
      // Business Boxes (spelled out; IDs on join lines)
      'uc01.biz.po': 'Purchase order',
      'uc01.biz.so': 'Sales order',
      'uc01.biz.co': 'Customer order',
      'uc01.biz.prod': 'Production order',
      // Enrichment Boxes
      'uc01.enrich.agv': 'AGV / shuttle',
      'uc01.enrich.oee': 'OEE\nOverall equipment effectiveness',
      'uc01.enrich.cfg': 'Machine configuration',
      'uc01.enrich.cam': 'Camera / vision',
      'uc01.enrich.temp': 'Temperature',
      // Phases
      'uc01.phase.procurement': 'Phase 1: Procurement',
      'uc01.phase.production': 'Phase 2: Production Fulfillment',
      // Legend
      'uc01.legend.title': 'Legend',
      'uc01.legend.cyan': 'Physical part (NFC)',
      'uc01.legend.red': 'Parallel stop ①',
      'uc01.legend.dashed': 'Correlation / join',
      'uc01.legend.parallel': 'Parallel job FTS',
      // Footer
      'uc01.footer': 'OSF is a demonstrator showcasing integration principles; productive implementations depend on the customer\'s target landscape.',
    };
  }
}
