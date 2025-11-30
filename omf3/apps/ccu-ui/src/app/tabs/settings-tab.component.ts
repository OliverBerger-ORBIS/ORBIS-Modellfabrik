import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { EnvironmentDefinition, EnvironmentService, EnvironmentKey } from '../services/environment.service';
import { ConnectionService, ConnectionSettings } from '../services/connection.service';
import { ExternalLinksService, ExternalLinksSettings } from '../services/external-links.service';

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
            <span i18n="@@settingsOrbisLinkLabel">ORBIS website URL</span>
            <input type="url" formControlName="orbisWebsiteUrl" placeholder="https://www.orbis.de" />
          </label>

          <label>
            <span i18n="@@settingsDspLinkLabel">DSP landing URL</span>
            <input type="url" formControlName="dspControlUrl" placeholder="https://dsp.example.com" />
          </label>

          <label>
            <span i18n="@@settingsManagementLinkLabel">Management Cockpit URL</span>
            <input type="url" formControlName="managementCockpitUrl" placeholder="https://management.example.com" />
          </label>

          <label>
            <span i18n="@@settingsGrafanaLinkLabel">Grafana dashboard URL</span>
            <input type="url" formControlName="grafanaDashboardUrl" placeholder="https://grafana.example.com" />
          </label>

          <label>
            <span i18n="@@settingsSmartFactoryLinkLabel">SmartFactory Dashboard URL</span>
            <input type="text" formControlName="smartfactoryDashboardUrl" placeholder="/dsp-action" />
          </label>

          <footer>
            <button type="submit" class="primary" [disabled]="linksForm.pristine || linksForm.invalid" i18n="@@settingsSaveButton">
              Save changes
            </button>
          </footer>
        </form>
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

  constructor(
    private readonly environmentService: EnvironmentService,
    private readonly connectionService: ConnectionService,
    private readonly externalLinksService: ExternalLinksService,
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
      orbisWebsiteUrl: [linkSettings.orbisWebsiteUrl, [Validators.required]],
      dspControlUrl: [linkSettings.dspControlUrl, [Validators.required]],
      managementCockpitUrl: [linkSettings.managementCockpitUrl, [Validators.required]],
      grafanaDashboardUrl: [linkSettings.grafanaDashboardUrl, [Validators.required]],
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
