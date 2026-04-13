import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject } from 'rxjs';
import { getAssetPath } from '../assets/detail-asset-map';

export interface ExternalLinksSettings {
  readonly grafanaDashboardUrl: string;
  readonly smartfactoryDashboardUrl: string;
  readonly dspControlUrl: string;
  readonly managementCockpitUrl: string;
  readonly erpSystemUrl: string; // Task 12: ERP/SAP System URL for future integration
  /** External ORBIS MES (or other MES) URL; DSP animation bp-mes opens this when set */
  readonly mesSystemUrl: string;
  /** External SAP EWM (or other EWM) URL; DSP animation bp-ewm opens this when set */
  readonly ewmSystemUrl: string;
}

const DEFAULT_SETTINGS: ExternalLinksSettings = {
  grafanaDashboardUrl: 'http://192.168.0.201:3000/dashboards',
  smartfactoryDashboardUrl: '/dsp-action',
  dspControlUrl: 'https://www.orbis-group.com/de-de/sap-orbis-loesungen/distributed-shopfloor-processing.html',
  managementCockpitUrl: 'https://dspmcorbisprd.powerappsportals.com',
  erpSystemUrl: 'process', // Default: internal Process-Tab, can be changed to external ERP/SAP URL
  mesSystemUrl: '',
  ewmSystemUrl: '',
};

@Injectable({ providedIn: 'root' })
export class ExternalLinksService {
  private readonly settingsSubject: BehaviorSubject<ExternalLinksSettings>;
  private readonly http = inject(HttpClient);

  constructor() {
    this.settingsSubject = new BehaviorSubject<ExternalLinksSettings>(DEFAULT_SETTINGS);
    this.loadFromRepoConfig();
  }

  get settings$() {
    return this.settingsSubject.asObservable();
  }

  get current(): ExternalLinksSettings {
    return this.settingsSubject.value;
  }

  updateSettings(settings: ExternalLinksSettings): void {
    this.settingsSubject.next({ ...settings });
  }

  private loadFromRepoConfig(): void {
    const url = getAssetPath('assets/config/external-links.json');
    this.http.get<Partial<ExternalLinksSettings>>(url).subscribe({
      next: (config) => {
        this.settingsSubject.next({
          ...DEFAULT_SETTINGS,
          ...config,
        });
      },
      error: (error) => {
        console.warn('[external-links] Failed to load repo config', error);
      },
    });
  }
}

