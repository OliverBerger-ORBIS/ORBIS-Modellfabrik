import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { LanguageService } from '../../../services/language.service';

/**
 * Service for loading I18n translations for UC-01 Track & Trace Genealogy
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
      const messagesResponse = await firstValueFrom(this.http.get<{ locale: string; translations: Record<string, string> }>(messagesPath));
      
      // Extract translations object (messages.json has nested structure)
      const messages = messagesResponse.translations || messagesResponse as unknown as Record<string, string>;
      
      // Extract UC-01 keys (keys starting with @@uc01)
      const uc01Texts: Record<string, string> = {};
      Object.keys(messages).forEach((key) => {
        if (key.startsWith('@@uc01')) {
          // Remove @@ prefix for internal use
          const internalKey = key.replace(/^@@/, '');
          uc01Texts[internalKey] = messages[key];
        }
      });
      
      // For EN locale, replace with English translations
      if (locale === 'en') {
        const enTexts = this.getEnglishTranslations();
        Object.assign(uc01Texts, enTexts);
      }
      
      // Cache translations
      this.translationsCache.set(locale, uc01Texts);
      
      // Debug: Log loaded translations
      console.log(`[UC-01 I18n] Loaded ${Object.keys(uc01Texts).length} translations for locale: ${locale}`);
      if (Object.keys(uc01Texts).length === 0) {
        console.warn('[UC-01 I18n] No translations found! Keys in messages.json:', Object.keys(messages).filter(k => k.startsWith('@@uc01')).slice(0, 10));
      }
      
      return uc01Texts;
    } catch (error) {
      console.error('Failed to load UC-01 translations:', error);
      // Return English as fallback
      const fallback = locale === 'en' ? this.getEnglishTranslations() : {};
      console.log(`[UC-01 I18n] Using fallback translations: ${Object.keys(fallback).length} keys`);
      return fallback;
    }
  }
  
  /**
   * English translations for UC-01 (fallback when EN file doesn't exist)
   */
  private getEnglishTranslations(): Record<string, string> {
    return {
      'uc01.title': 'Track & Trace Genealogy',
      'uc01.subtitle': 'Correlate events along a unique workpiece ID',
      'uc01.column.business_events': 'Business Events',
      'uc01.lane.supplier_order': 'Supplier Order',
      'uc01.chip.purchase_order': 'Purchase Order',
      'uc01.chip.purchase_order.line1': 'Purchase',
      'uc01.chip.purchase_order.line2': 'Order',
      'uc01.chip.supplier_info': 'Supplier Info',
      'uc01.chip.material_batch': 'Material / Batch',
      'uc01.chip.erp_id': 'ERP-ID',
      'uc01.lane.storage_order': 'Storage Order',
      'uc01.chip.storage_order_id': 'Storage Order ID',
      'uc01.chip.warehouse': 'Warehouse',
      'uc01.lane.customer_order': 'Customer Order',
      'uc01.chip.customer_order_id': 'Customer Order ID',
      'uc01.chip.production_order': 'Production Order',
      'uc01.chip.production_order.line1': 'Production',
      'uc01.chip.production_order.line2': 'Order',
      'uc01.chip.customer_id': 'Customer ID',
      'uc01.column.production_plan': 'Production Plan',
      'uc01.plan.warehouse': 'Warehouse',
      'uc01.plan.drill': 'DRILL',
      'uc01.plan.quality': 'Quality',
      'uc01.plan.dps': 'DPS',
      'uc01.column.actual_path': 'Actual Path',
      'uc01.actual.warehouse': 'Warehouse',
      'uc01.actual.fts': 'FTS',
      'uc01.actual.drill': 'DRILL',
      'uc01.actual.quality': 'Quality',
      'uc01.actual.dps': 'DPS',
      'uc01.column.correlated_timeline': 'Correlated Timeline',
      'uc01.nfc_tag.label': 'NFC / Workpiece ID',
      'uc01.timeline.start_transfer': 'START TRANSFER',
      'uc01.timeline.timestamp_1': '10:01',
      'uc01.timeline.warehouse_move': 'WAREHOUSE MOVE',
      'uc01.timeline.timestamp_2': '10:10',
      'uc01.timeline.station_process': 'STATION PROCESS',
      'uc01.timeline.timestamp_3': '10:03',
      'uc01.timeline.quality_check': 'QUALITY CHECK',
      'uc01.timeline.timestamp_4': '10:15',
      'uc01.timeline.end_transport': 'END TRANSPORT',
      'uc01.timeline.timestamp_5': '10:20',
      'uc01.order_context.production_order': 'Production Order',
      'uc01.order_context.customer_order': 'Customer Order',
      'uc01.order_context.material_batch': 'Material / Batch',
      'uc01.order_context.erp_id': 'ERP-ID',
    };
  }
}
