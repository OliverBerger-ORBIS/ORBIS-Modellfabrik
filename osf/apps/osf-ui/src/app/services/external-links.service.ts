import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject } from 'rxjs';
import { getAssetPath } from '../assets/detail-asset-map';

/**
 * External link targets for DSP UI (Settings + `public/assets/config/external-links.json`).
 *
 * Property order matches the **DSP architecture diagram** (top → bottom, left → right):
 * 1. Business process layer: ERP → Planning → MES → EWM → Analytics → Data Lake
 * 2. DSP layer: SmartFactory dashboard → Edge → Management Cockpit
 */
export interface ExternalLinksSettings {
  /** BP box `bp-erp` (leftmost in business row). */
  readonly bpErpApplicationUrl: string;
  /** BP box `bp-planning`. */
  readonly bpPlanningApplicationUrl: string;
  /** BP box `bp-mes`. */
  readonly bpMesApplicationUrl: string;
  /** BP box `bp-ewm`. */
  readonly bpEwmApplicationUrl: string;
  /** BP box `bp-analytics`. */
  readonly bpAnalyticsApplicationUrl: string;
  /** BP box `bp-data-lake`. */
  readonly bpDataLakeApplicationUrl: string;

  /** DSP layer: SmartFactory / UX box (`dsp-ux`). */
  readonly dspSmartfactoryDashboardUrl: string;
  /** DSP layer: Edge box (`dsp-edge`). */
  readonly dspEdgeUrl: string;
  /** DSP layer: Management Cockpit (`dsp-mc`). */
  readonly dspManagementCockpitUrl: string;
}

const DEFAULT_SETTINGS: ExternalLinksSettings = {
  bpErpApplicationUrl: 'process',
  bpPlanningApplicationUrl:
    'https://md1.orbis.de/sap/bc/ui5_ui5/omes/pt/index.html?sap-client=100&sap-ui-language=DE&sap-ui-xx-devmode=true#/OrderManagement/1010/SMARTFACTORY',
  bpMesApplicationUrl:
    'https://md1.orbis.de/orbis/web_mes/webviewer/index.htm#mppservice=orbis/mes&mpptimeout=60000&defaultlang=EN&maskid=ffb6098113c549bda9192b793dbb75ab&viewermenue=true&extensions=[%22controlinfo%22]&LAYOUT=LIGHT&Werk=1010',
  bpEwmApplicationUrl: 'https://www.orbis-group.com/de-de/sap-orbis-loesungen/logistics/apps.html',
  bpAnalyticsApplicationUrl: 'http://192.168.0.201:3000/dashboards',
  bpDataLakeApplicationUrl: '',
  dspSmartfactoryDashboardUrl: '/dsp-action',
  dspEdgeUrl: 'https://www.orbis-group.com/de-de/sap-orbis-loesungen/distributed-shopfloor-processing.html',
  dspManagementCockpitUrl: 'https://dspmcorbisprd.powerappsportals.com',
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
        return clean(links.bpErpApplicationUrl);
      case 'bp-planning':
        return clean(links.bpPlanningApplicationUrl);
      case 'bp-mes':
        return clean(links.bpMesApplicationUrl);
      case 'bp-ewm':
        return clean(links.bpEwmApplicationUrl);
      case 'bp-analytics':
        return clean(links.bpAnalyticsApplicationUrl);
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
