import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject } from 'rxjs';
import { getAssetPath } from '../assets/detail-asset-map';

export interface ExternalLinksSettings {
  readonly grafanaDashboardUrl: string;
  readonly smartfactoryDashboardUrl: string;
  readonly dspControlUrl: string;
  readonly managementCockpitUrl: string;
  /** Legacy: ERP/SAP URL (used outside DSP animation). Prefer `bpErpApplicationUrl` for BP box mapping. */
  readonly erpSystemUrl: string;
  /** Legacy: ORBIS MES URL. Prefer `bpMesApplicationUrl` for BP box mapping. */
  readonly mesSystemUrl: string;
  /** Legacy: SAP EWM URL. Prefer `bpEwmApplicationUrl` for BP box mapping. */
  readonly ewmSystemUrl: string;

  /** DSP Architecture: BP-ERP Application URL (container id: bp-erp). */
  readonly bpErpApplicationUrl: string;
  /** DSP Architecture: BP-Planning Application URL (container id: bp-planning). */
  readonly bpPlanningApplicationUrl: string;
  /** DSP Architecture: BP-MES Application URL (container id: bp-mes). */
  readonly bpMesApplicationUrl: string;
  /** DSP Architecture: BP-EWM Application URL (container id: bp-ewm). */
  readonly bpEwmApplicationUrl: string;
  /** DSP Architecture: BP-Analytics Application URL (container id: bp-analytics). */
  readonly bpAnalyticsApplicationUrl: string;
  /** DSP Architecture: BP-Data Lake URL (container id: bp-data-lake). */
  readonly bpDataLakeApplicationUrl: string;
}

const DEFAULT_SETTINGS: ExternalLinksSettings = {
  grafanaDashboardUrl: 'http://192.168.0.201:3000/dashboards',
  smartfactoryDashboardUrl: '/dsp-action',
  dspControlUrl: 'https://www.orbis-group.com/de-de/sap-orbis-loesungen/distributed-shopfloor-processing.html',
  managementCockpitUrl: 'https://dspmcorbisprd.powerappsportals.com',
  erpSystemUrl: 'process', // Default: internal Process-Tab, can be changed to external ERP/SAP URL
  mesSystemUrl: '',
  ewmSystemUrl: '',
  bpErpApplicationUrl: 'process',
  bpPlanningApplicationUrl: '',
  bpMesApplicationUrl: '',
  bpEwmApplicationUrl: '',
  bpAnalyticsApplicationUrl: 'http://192.168.0.201:3000/dashboards',
  bpDataLakeApplicationUrl: '',
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

  resolveBpApplicationUrl(bpContainerId: string): string | undefined {
    const links = this.current;
    const clean = (value: string | undefined): string | undefined => {
      const trimmed = value?.trim();
      return trimmed ? trimmed : undefined;
    };
    switch (bpContainerId) {
      case 'bp-erp':
        return clean(links.bpErpApplicationUrl) ?? clean(links.erpSystemUrl) ?? 'process';
      case 'bp-planning':
        return clean(links.bpPlanningApplicationUrl);
      case 'bp-mes':
        return clean(links.bpMesApplicationUrl) ?? clean(links.mesSystemUrl);
      case 'bp-ewm':
        return clean(links.bpEwmApplicationUrl) ?? clean(links.ewmSystemUrl);
      case 'bp-analytics':
        return clean(links.bpAnalyticsApplicationUrl) ?? clean(links.grafanaDashboardUrl);
      case 'bp-data-lake':
        return clean(links.bpDataLakeApplicationUrl);
      default:
        return undefined;
    }
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

