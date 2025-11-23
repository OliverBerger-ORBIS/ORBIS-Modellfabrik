import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface ExternalLinksSettings {
  readonly orbisWebsiteUrl: string;
  readonly dspControlUrl: string;
  readonly managementCockpitUrl: string;
  readonly grafanaDashboardUrl: string;
}

const STORAGE_KEY = 'omf3.externalLinks';

const DEFAULT_SETTINGS: ExternalLinksSettings = {
  orbisWebsiteUrl: 'https://www.orbis.de',
  dspControlUrl: 'https://www.orbis.de/en-de/solutions/orbis-dsp.html',
  managementCockpitUrl: 'https://www.orbis.de/en-de/solutions/orbis-dsp.html',
  grafanaDashboardUrl: 'https://grafana.example.com',
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

