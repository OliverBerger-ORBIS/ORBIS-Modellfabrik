import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface ExternalLinksSettings {
  readonly grafanaDashboardUrl: string;
  readonly smartfactoryDashboardUrl: string;
  readonly dspControlUrl: string;
  readonly managementCockpitUrl: string;
  readonly erpSystemUrl: string; // Task 12: ERP/SAP System URL for future integration
}

const STORAGE_KEY = 'omf3.externalLinks';

const DEFAULT_SETTINGS: ExternalLinksSettings = {
  grafanaDashboardUrl: 'http://192.168.0.201:3000/dashboards',
  smartfactoryDashboardUrl: '/dsp-action',
  dspControlUrl: 'https://www.orbis-group.com/de-de/sap-orbis-loesungen/distributed-shopfloor-processing.html',
  managementCockpitUrl: 'https://dspmcorbisprd.powerappsportals.com',
  erpSystemUrl: 'process', // Default: internal Process-Tab, can be changed to external ERP/SAP URL
};

@Injectable({ providedIn: 'root' })
export class ExternalLinksService {
  private readonly settingsSubject: BehaviorSubject<ExternalLinksSettings>;

  constructor() {
    this.settingsSubject = new BehaviorSubject<ExternalLinksSettings>(this.loadSettings());
  }

  get settings$() {
    return this.settingsSubject.asObservable();
  }

  get current(): ExternalLinksSettings {
    return this.settingsSubject.value;
  }

  updateSettings(settings: ExternalLinksSettings): void {
    this.settingsSubject.next({ ...settings });
    try {
      localStorage?.setItem(STORAGE_KEY, JSON.stringify(settings));
    } catch (error) {
      console.warn('[external-links] Failed to persist settings', error);
    }
  }

  private loadSettings(): ExternalLinksSettings {
    try {
      const stored = localStorage?.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as Partial<ExternalLinksSettings>;
        return {
          ...DEFAULT_SETTINGS,
          ...parsed,
        };
      }
    } catch (error) {
      console.warn('[external-links] Failed to parse stored settings', error);
    }
    return DEFAULT_SETTINGS;
  }
}

