import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { getBaseHref } from '../assets/detail-asset-map';
import { EnvironmentDefinition, EnvironmentService, EnvironmentKey } from '../services/environment.service';
import { ConnectionService, ConnectionSettings } from '../services/connection.service';
import { ExternalLinksService, ExternalLinksSettings } from '../services/external-links.service';
import { LanguageService, LocaleKey } from '../services/language.service';
import { ShopfloorRotationService, type ShopfloorRotation } from '../services/shopfloor-rotation.service';

@Component({
  standalone: true,
  selector: 'app-settings-tab',
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <section class="settings-tab">
      <header>
        <div>
          <h2 i18n="@@settingsHeadline">System Settings</h2>
          <p i18n="@@settingsDescription">
            Manage environment specific connection parameters for replay and live gateways.
          </p>
        </div>
      </header>

      <div class="environment-cards">
        <article
          *ngFor="let environment of environments"
          class="environment-card"
          [class.environment-card--readonly]="environment.readOnly"
        >
          <header>
            <h3>{{ environment.label }}</h3>
            <p>{{ environment.description }}</p>
          </header>

          <form [formGroup]="forms.get(environment.key)!" (ngSubmit)="save(environment)">
            <div class="form-grid">
              <label>
                <span i18n="@@settingsHostLabel">MQTT Host</span>
                <input
                  type="text"
                  formControlName="mqttHost"
                  [readonly]="environment.readOnly"
                />
              </label>
              <label>
                <span i18n="@@settingsPortLabel">Port</span>
                <input
                  type="number"
                  formControlName="mqttPort"
                  min="0"
                  [readonly]="environment.readOnly"
                />
              </label>
              <label>
                <span i18n="@@settingsUsernameLabel">Username</span>
                <input
                  type="text"
                  formControlName="mqttUsername"
                  [readonly]="environment.readOnly"
                />
              </label>
              <label>
                <span i18n="@@settingsPasswordLabel">Password</span>
                <input
                  type="password"
                  formControlName="mqttPassword"
                  [readonly]="environment.readOnly"
                />
              </label>
            </div>

            <footer *ngIf="!environment.readOnly">
              <button
                type="submit"
                class="primary"
                [disabled]="forms.get(environment.key)!.pristine || forms.get(environment.key)!.invalid"
                i18n="@@settingsSaveButton"
              >
                Save changes
              </button>
            </footer>
            <footer *ngIf="environment.readOnly" class="note" i18n="@@settingsMockHint">
              Configuration is managed automatically for mock fixtures.
            </footer>
          </form>
        </article>
      </div>

      <section class="connection-settings">
        <header>
          <h3 i18n="@@settingsConnectionHeadline">Connection behaviour</h3>
          <p i18n="@@settingsConnectionDescription">Configure auto-connect and retry behaviour for gateway connections.</p>
        </header>

        <form [formGroup]="connectionForm" (ngSubmit)="saveConnectionSettings()" class="connection-form">
          <label class="switch">
            <input type="checkbox" formControlName="autoConnect" />
            <span>
              <strong i18n="@@settingsAutoConnectLabel">Auto-connect</strong>
              <small i18n="@@settingsAutoConnectHint"> connect automatically when switching environments</small>
            </span>
          </label>

          <label class="switch">
            <input type="checkbox" formControlName="retryEnabled" />
            <span>
              <strong i18n="@@settingsRetryLabel">Retry on failure</strong>
              <small i18n="@@settingsRetryHint">Attempt reconnection automatically if the gateway disconnects</small>
            </span>
          </label>

          <label class="retry-interval">
            <span i18n="@@settingsRetryIntervalLabel">Retry interval (ms)</span>
            <input type="number" min="1000" step="500" formControlName="retryIntervalMs" />
          </label>

          <footer>
            <button type="submit" class="primary" [disabled]="connectionForm.pristine || connectionForm.invalid" i18n="@@settingsSaveButton">
              Save changes
            </button>
          </footer>
        </form>
      </section>

      <section class="shopfloor-settings">
        <header>
          <h3 i18n="@@settingsShopfloorHeadline">Shopfloor layout</h3>
          <p i18n="@@settingsShopfloorDescription">
            Rotation is applied to all shopfloor previews (including presentation mode). Labels stay readable.
          </p>
        </header>

        <form [formGroup]="shopfloorForm" class="shopfloor-form">
          <label>
            <span i18n="@@settingsShopfloorRotationLabel">Rotation</span>
            <select formControlName="rotation">
              <option value="none" i18n="@@settingsShopfloorRotationNone">No rotation</option>
              <option value="cw90" i18n="@@settingsShopfloorRotationCw90">90° clockwise</option>
              <option value="ccw90" i18n="@@settingsShopfloorRotationCcw90">90° counter-clockwise</option>
            </select>
          </label>
        </form>
      </section>

      <section class="link-settings">
        <header>
          <h3 i18n="@@settingsLinksHeadline">External links</h3>
          <p i18n="@@settingsLinksDescription">
            Configure the URLs used by the DSP architecture boxes and detail views.
          </p>
        </header>

        <form [formGroup]="linksForm" (ngSubmit)="saveExternalLinks()" class="links-form">
          <label>
            <span i18n="@@settingsSmartFactoryLinkLabel">DSP SmartFactory Dashboard URL</span>
            <input type="text" formControlName="smartfactoryDashboardUrl" placeholder="/dsp-action" />
          </label>

          <label>
            <span i18n="@@settingsDspLinkLabel">DSP Edge URL</span>
            <input type="url" formControlName="dspControlUrl" placeholder="https://dsp.example.com" />
          </label>

          <label>
            <span i18n="@@settingsManagementLinkLabel">DSP Management Cockpit URL</span>
            <input type="url" formControlName="managementCockpitUrl" placeholder="https://management.example.com" />
          </label>

          <label>
            <span i18n="@@settingsBpErpSystemLinkLabel">BP-ERP Application URL</span>
            <input type="text" formControlName="bpErpApplicationUrl" placeholder="process" />
            <small i18n="@@settingsBpErpSystemLinkHint">Internal route (e.g., 'process') or external ERP/SAP URL.</small>
          </label>

          <label>
            <span i18n="@@settingsBpPlanningLinkLabel">BP-Planning Application URL</span>
            <input type="url" formControlName="bpPlanningApplicationUrl" placeholder="https://" />
            <small i18n="@@settingsBpPlanningLinkHint">Opens in a new tab when the BP-Planning box is clicked. Leave empty to disable.</small>
          </label>

          <label>
            <span i18n="@@settingsBpMesSystemLinkLabel">BP-MES Application URL (ORBIS MES)</span>
            <input type="url" formControlName="bpMesApplicationUrl" placeholder="https://" />
            <small i18n="@@settingsBpMesSystemLinkHint">Opens in a new tab when the BP-MES box is clicked. Leave empty to disable.</small>
          </label>

          <label>
            <span i18n="@@settingsBpEwmSystemLinkLabel">BP-EWM Application URL (SAP EWM)</span>
            <input type="url" formControlName="bpEwmApplicationUrl" placeholder="https://" />
            <small i18n="@@settingsBpEwmSystemLinkHint">Opens in a new tab when the BP-EWM box is clicked. Leave empty to disable.</small>
          </label>

          <label>
            <span i18n="@@settingsBpAnalyticsLinkLabel">BP-Analytics Application URL</span>
            <input type="url" formControlName="bpAnalyticsApplicationUrl" placeholder="https://grafana.example.com" />
          </label>

          <label>
            <span i18n="@@settingsBpDataLakeLinkLabel">BP-Data Lake URL</span>
            <input type="url" formControlName="bpDataLakeApplicationUrl" placeholder="https://" />
            <small i18n="@@settingsBpDataLakeLinkHint">Optional: open a Data Lake page from the BP-Data-Lake box.</small>
          </label>

          <footer>
            <button type="submit" class="primary" [disabled]="linksForm.pristine || linksForm.invalid" i18n="@@settingsSaveButton">
              Save changes
            </button>
            <button
              type="button"
              class="secondary"
              (click)="exportExternalLinksJson()"
              [disabled]="linksForm.invalid"
              i18n="@@settingsExportLinksButton"
            >
              Export JSON
            </button>
          </footer>
          <p class="hint" i18n="@@settingsLinksRepoHint">
            Repo-managed config: export and paste into <code>osf/apps/osf-ui/public/assets/config/external-links.json</code>,
            then commit & deploy to apply on the RPi.
          </p>
        </form>
      </section>

      <section class="direct-pages">
        <header>
          <h3 i18n="@@settingsDirectPagesTitle">Direct-access pages (not in navigation)</h3>
          <p i18n="@@settingsDirectPagesDescription">
            These routes can be opened directly (e.g. for presentations/video mode) without adding extra tabs to the navigation.
          </p>
        </header>

        <ul class="direct-page-list">
          <li *ngFor="let page of directPages">
            <div class="direct-page__header">
              <strong>{{ page.label }}</strong>
              <span class="badge" [class.badge--planned]="!page.available">
                {{ page.available ? ('Available' | uppercase) : ('Planned' | uppercase) }}
              </span>
            </div>
            <div class="direct-page__url">
              <a [href]="resolveUrl(page.path)" target="_blank" rel="noreferrer noopener">{{ resolveUrl(page.path) }}</a>
            </div>
            <p class="direct-page__desc">{{ page.description }}</p>
            <!-- Language links for each page -->
            <div class="direct-page__languages" *ngIf="page.available">
              <span class="language-label" i18n="@@settingsLanguageLinks">Languages:</span>
              <div class="language-buttons">
                <button
                  *ngFor="let locale of supportedLocales"
                  type="button"
                  class="language-btn"
                  [class.language-btn--active]="locale === currentLocale"
                  (click)="navigateToLanguageForPage(locale, page.path)"
                  [attr.aria-label]="getLanguageLabel(locale)"
                >
                  {{ locale.toUpperCase() }}
                </button>
              </div>
            </div>
          </li>
        </ul>
      </section>
    </section>
  `,
  styleUrl: './settings-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SettingsTabComponent implements OnInit {
  environments: EnvironmentDefinition[] = [];
  readonly forms = new Map<EnvironmentDefinition['key'], FormGroup>();
  connectionForm!: FormGroup;
  shopfloorForm!: FormGroup;
  linksForm!: FormGroup;
  readonly directPages = [
    {
      label: 'Presentation (FTS Route & Shopfloor Layout)',
      path: '/#/en/presentation',
      description: 'Direct access for video/presentation mode; not part of the tab navigation.',
      available: true,
    },
    {
      label: 'DSP Animation',
      path: '/#/en/dsp-animation',
      description: 'DSP animation component with multiple view modes, reachable via direct URL only.',
      available: true,
    },
    {
      label: 'DSP Action',
      path: '/#/en/dsp-action',
      description: 'Direct access page for DSP Action (not in tab navigation).',
      available: true,
    },
    {
      label: 'DSP Use Cases',
      path: '/#/en/dsp/use-case',
      description: 'Select and view use case demonstrations (Track & Trace, Interoperability, and more).',
      available: true,
    },
    {
      label: 'UC-01 Track & Trace (Concept)',
      path: '/#/en/dsp/use-case/track-trace?tab=concept',
      description: 'UC-01 genealogy diagram (Concept tab). Same page as Live Demo with different tab.',
      available: true,
    },
    {
      label: 'UC-01 Track & Trace (Live Demo)',
      path: '/#/en/dsp/use-case/track-trace?tab=live',
      description: 'UC-01 live Track & Trace dashboard (Live Demo tab).',
      available: true,
    },
    {
      label: 'DSP Customer Architecture',
      path: '/#/en/dsp/customer',
      description: 'Select and view customer-specific DSP architecture demonstrations (OSF, FMF, LogiMAT, ECME).',
      available: true,
    },
  ];

  resolveUrl(path: string): string {
    const baseHref = getBaseHref();
    // Remove leading slash from path to avoid double slash if baseHref ends with /
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    const cleanBase = baseHref.endsWith('/') ? baseHref : `${baseHref}/`;
    return `${cleanBase}${cleanPath}`;
  }

  /**
   * Get language-specific URL for a given path
   */
  getLanguageUrl(path: string, locale: LocaleKey): string {
    // Replace locale in path
    return path.replace(/\/#\/[a-z]{2}\//, `/#/${locale}/`);
  }

  /**
   * Navigate to language-specific version of a page path
   */
  navigateToLanguageForPage(locale: LocaleKey, pagePath: string): void {
    // Extract path without locale and hash
    // pagePath format: /#/en/dsp-animation or /#/en/dsp/use-case/track-trace?tab=concept
    let cleanPath = pagePath.replace(/^\/#\//, ''); // Remove /#/
    
    // Remove locale prefix if present (en/, de/, fr/)
    const localeMatch = cleanPath.match(/^(en|de|fr)\/(.+)$/);
    if (localeMatch) {
      cleanPath = localeMatch[2]; // Get path after locale
    }
    
    // Navigate to locale-specific path so the correct build loads (/en/, /de/, /fr/).
    const hash = `#/${locale}/${cleanPath}`;
    const pathname = window.location.pathname.replace(/\/(en|de|fr)\/?/, `/${locale}/`);
    const pathWithLocale = pathname.match(/\/(en|de|fr)\/?/) ? pathname : `${pathname.replace(/\/$/, '')}/${locale}/`;
    const newUrl = `${window.location.origin}${pathWithLocale}${hash}`;
    window.location.assign(newUrl);
  }

  /**
   * Get current locale
   */
  get currentLocale(): LocaleKey {
    return this.languageService.current;
  }

  /**
   * Get all supported locales
   */
  get supportedLocales(): LocaleKey[] {
    return this.languageService.supportedLocales;
  }

  /**
   * Get language label
   */
  getLanguageLabel(locale: LocaleKey): string {
    const labels: Record<LocaleKey, string> = {
      en: 'English',
      de: 'Deutsch',
      fr: 'Français',
    };
    return labels[locale];
  }

  constructor(
    private readonly environmentService: EnvironmentService,
    private readonly connectionService: ConnectionService,
    private readonly externalLinksService: ExternalLinksService,
    private readonly languageService: LanguageService,
    private readonly router: Router,
    private readonly fb: FormBuilder,
    private readonly shopfloorRotation: ShopfloorRotationService
  ) {}

  ngOnInit(): void {
    this.environments = this.environmentService.environments;
    this.environments.forEach((environment) => {
      const connection = environment.connection;
      const form = this.fb.group({
        mqttHost: [{ value: connection.mqttHost, disabled: environment.readOnly }, [Validators.required]],
        mqttPort: [{ value: connection.mqttPort, disabled: environment.readOnly }, [Validators.required, Validators.min(0)]],
        mqttUsername: [{ value: connection.mqttUsername ?? '', disabled: environment.readOnly }],
        mqttPassword: [{ value: connection.mqttPassword ?? '', disabled: environment.readOnly }],
      });
      this.forms.set(environment.key, form);
    });

    const settings = this.connectionService.currentSettings;
    this.connectionForm = this.fb.group({
      autoConnect: [settings.autoConnect],
      retryEnabled: [settings.retryEnabled],
      retryIntervalMs: [settings.retryIntervalMs, [Validators.required, Validators.min(1000)]],
    });

    this.shopfloorForm = this.fb.group({
      rotation: [this.shopfloorRotation.current],
    });
    this.shopfloorForm.get('rotation')?.valueChanges.subscribe((value) => {
      this.shopfloorRotation.setRotation(value as ShopfloorRotation);
    });

    const linkSettings = this.externalLinksService.current;
    this.linksForm = this.fb.group({
      // DSP Architecture BP boxes
      bpErpApplicationUrl: [linkSettings.bpErpApplicationUrl ?? linkSettings.erpSystemUrl],
      bpPlanningApplicationUrl: [linkSettings.bpPlanningApplicationUrl],
      bpMesApplicationUrl: [linkSettings.bpMesApplicationUrl ?? linkSettings.mesSystemUrl],
      bpEwmApplicationUrl: [linkSettings.bpEwmApplicationUrl ?? linkSettings.ewmSystemUrl],
      bpAnalyticsApplicationUrl: [linkSettings.bpAnalyticsApplicationUrl ?? linkSettings.grafanaDashboardUrl, [Validators.required]],
      bpDataLakeApplicationUrl: [linkSettings.bpDataLakeApplicationUrl],

      smartfactoryDashboardUrl: [linkSettings.smartfactoryDashboardUrl],
      dspControlUrl: [linkSettings.dspControlUrl, [Validators.required]],
      managementCockpitUrl: [linkSettings.managementCockpitUrl, [Validators.required]],
      // Legacy fields kept for backward-compat consumers and repo config
      grafanaDashboardUrl: [linkSettings.grafanaDashboardUrl],
      erpSystemUrl: [linkSettings.erpSystemUrl],
      mesSystemUrl: [linkSettings.mesSystemUrl],
      ewmSystemUrl: [linkSettings.ewmSystemUrl],
    });
  }

  save(environment: EnvironmentDefinition): void {
    if (environment.readOnly) {
      return;
    }
    const form = this.forms.get(environment.key);
    if (!form || form.invalid) {
      return;
    }
    this.environmentService.updateConnection(environment.key, {
      mqttHost: form.get('mqttHost')!.value,
      mqttPort: Number(form.get('mqttPort')!.value) || 0,
      mqttUsername: form.get('mqttUsername')!.value || undefined,
      mqttPassword: form.get('mqttPassword')!.value || undefined,
    });
    form.markAsPristine();
  }

  saveConnectionSettings(): void {
    if (!this.connectionForm || this.connectionForm.invalid) {
      return;
    }
    const value = this.connectionForm.value as ConnectionSettings;
    this.connectionService.updateSettings(value);
    this.connectionForm.markAsPristine();
  }

  saveExternalLinks(): void {
    if (!this.linksForm || this.linksForm.invalid) {
      return;
    }
    const raw = this.linksForm.value as ExternalLinksSettings;
    // Keep legacy fields in sync so other parts of the UI keep working.
    const value: ExternalLinksSettings = {
      ...raw,
      grafanaDashboardUrl: raw.bpAnalyticsApplicationUrl || raw.grafanaDashboardUrl,
      erpSystemUrl: raw.bpErpApplicationUrl || raw.erpSystemUrl,
      mesSystemUrl: raw.bpMesApplicationUrl || raw.mesSystemUrl,
      ewmSystemUrl: raw.bpEwmApplicationUrl || raw.ewmSystemUrl,
    };
    this.externalLinksService.updateSettings(value);
    this.linksForm.markAsPristine();
  }

  exportExternalLinksJson(): void {
    if (!this.linksForm || this.linksForm.invalid) {
      return;
    }
    const value = this.linksForm.value as ExternalLinksSettings;
    const content = `${JSON.stringify(value, null, 2)}\n`;
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    try {
      const a = document.createElement('a');
      a.href = url;
      a.download = 'external-links.json';
      a.click();
    } finally {
      URL.revokeObjectURL(url);
    }
  }
}
