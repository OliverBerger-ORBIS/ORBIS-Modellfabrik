import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { EnvironmentDefinition, EnvironmentService, EnvironmentKey } from '../services/environment.service';
import { ConnectionService, ConnectionSettings } from '../services/connection.service';
import { ExternalLinksService, ExternalLinksSettings } from '../services/external-links.service';
import { LanguageService, LocaleKey } from '../services/language.service';

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

      <section class="link-settings">
        <header>
          <h3 i18n="@@settingsLinksHeadline">External links</h3>
          <p i18n="@@settingsLinksDescription">
            Configure the URLs used for ORBIS and DSP detail views in the configuration tab.
          </p>
        </header>

        <form [formGroup]="linksForm" (ngSubmit)="saveExternalLinks()" class="links-form">
          <label>
            <span i18n="@@settingsGrafanaLinkLabel">BP Analytical Application URL</span>
            <input type="url" formControlName="grafanaDashboardUrl" placeholder="https://grafana.example.com" />
          </label>

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

          <footer>
            <button type="submit" class="primary" [disabled]="linksForm.pristine || linksForm.invalid" i18n="@@settingsSaveButton">
              Save changes
            </button>
          </footer>
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
              <a [href]="page.path" target="_blank" rel="noreferrer noopener">{{ page.path }}</a>
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
      label: 'Track & Trace (Use Case)',
      path: '/#/en/dsp/use-case/track-trace',
      description: 'Track & Trace use case page, accessible via direct URL (not in tab navigation). Fixtures available in mock mode.',
      available: true,
    },
    {
      label: 'DSP Customer Architecture',
      path: '/#/en/dsp/customer',
      description: 'Select and view customer-specific DSP architecture demonstrations (FMF, ECME).',
      available: true,
    },
    {
      label: 'Overview',
      path: '/#/en/overview',
      description: 'Overview tab with orders, FTS status, and inventory information. Moved from main navigation.',
      available: true,
    },
  ];

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
    // pagePath format: /#/en/dsp-animation or /#/en/dsp/use-case/track-trace
    let cleanPath = pagePath.replace(/^\/#\//, ''); // Remove /#/
    
    // Remove locale prefix if present (en/, de/, fr/)
    const localeMatch = cleanPath.match(/^(en|de|fr)\/(.+)$/);
    if (localeMatch) {
      cleanPath = localeMatch[2]; // Get path after locale
    }
    
    // Navigate using Angular Router (works with hash routing)
    // Router expects array format: ['locale', 'route', 'parts']
    const routeParts = cleanPath.split('/').filter(Boolean);
    this.router.navigate([locale, ...routeParts]).then(() => {
      // Reload to apply translations
      window.location.reload();
    }).catch((error) => {
      console.error('Navigation error:', error);
      // Fallback to window.location if router fails
      const newPath = `/#/${locale}/${cleanPath}`;
      window.location.href = newPath;
    });
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
    private readonly fb: FormBuilder
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

    const linkSettings = this.externalLinksService.current;
    this.linksForm = this.fb.group({
      grafanaDashboardUrl: [linkSettings.grafanaDashboardUrl, [Validators.required]],
      smartfactoryDashboardUrl: [linkSettings.smartfactoryDashboardUrl],
      dspControlUrl: [linkSettings.dspControlUrl, [Validators.required]],
      managementCockpitUrl: [linkSettings.managementCockpitUrl, [Validators.required]],
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
    const value = this.linksForm.value as ExternalLinksSettings;
    this.externalLinksService.updateSettings(value);
    this.linksForm.markAsPristine();
  }
}
