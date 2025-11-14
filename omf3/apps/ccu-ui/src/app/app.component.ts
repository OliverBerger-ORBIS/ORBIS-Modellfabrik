import { ChangeDetectionStrategy, Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AsyncPipe, NgClass, NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { EnvironmentKey, EnvironmentService } from './services/environment.service';
import { RoleService, UserRole } from './services/role.service';
import { LanguageService, LocaleKey } from './services/language.service';
import { ConnectionService, ConnectionState } from './services/connection.service';
import { getDashboardController } from './mock-dashboard';
import { Subscription } from 'rxjs';

interface NavigationItem {
  id: string;
  label: string;
  route: string;
  roles: UserRole[];
  icon?: string;
}

const NAVIGATION_ITEMS: NavigationItem[] = [
  {
    id: 'overview',
    label: $localize`:@@navOverview:Overview`,
    route: '/overview',
    roles: ['operator', 'admin'],
  },
  {
    id: 'order',
    label: $localize`:@@navOrder:Order`,
    route: '/order',
    roles: ['operator', 'admin'],
  },
  {
    id: 'process',
    label: $localize`:@@navProcess:Process`,
    route: '/process',
    roles: ['operator', 'admin'],
  },
  {
    id: 'sensor',
    label: $localize`:@@navSensor:Sensor Data`,
    route: '/sensor',
    roles: ['operator', 'admin'],
  },
  {
    id: 'module',
    label: $localize`:@@navModule:Module`,
    route: '/module',
    roles: ['operator', 'admin'],
  },
  {
    id: 'configuration',
    label: $localize`:@@navConfiguration:Configuration`,
    route: '/configuration',
    roles: ['admin'],
  },
  {
    id: 'settings',
    label: $localize`:@@navSettings:Settings`,
    route: '/settings',
    roles: ['admin'],
  },
];

@Component({
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    NgFor,
    NgIf,
    NgClass,
    AsyncPipe,
    FormsModule,
  ],
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AppComponent implements OnDestroy {
  readonly environments;
  readonly environment$;
  readonly role$;
  readonly locales;
  readonly navigation = NAVIGATION_ITEMS;
  sidebarCollapsed = false;
  selectedEnvironment: EnvironmentKey;
  selectedRole: UserRole;
  selectedLocale: LocaleKey;
  readonly connectionState$;

  readonly headerTitle = $localize`:@@headerTitle:SmartFactory`;
  readonly headerSubtitle =
    $localize`:@@headerSubtitle:ORBIS Modelfactory managed by Distributed Shopfloor Processing with IT/OT Integration, Interoperability and AI`;
  readonly resetLabel = $localize`:@@headerResetButton:Reset factory`;
  readonly orbitLogoPath = 'shopfloor/ORBIS_logo_RGB.svg';

  readonly mqttStatusLabel = $localize`:@@sidebarMqttStatusLabel:MQTT connection`;
  readonly mqttStatusSimulated = $localize`:@@sidebarMqttStatusMock:Simulated (mock)`;
  readonly mqttStatusPending = $localize`:@@sidebarMqttStatusPending:Not connected`;
  readonly connectionStatusLabels: Record<ConnectionState, string> = {
    disconnected: $localize`:@@headerConnectionStatusDisconnected:Disconnected`,
    connecting: $localize`:@@headerConnectionStatusConnecting:Connecting…`,
    connected: $localize`:@@headerConnectionStatusConnected:Connected`,
    error: $localize`:@@headerConnectionStatusError:Connection error`,
  };

  readonly roleOptions: { key: UserRole; label: string }[] = [
    { key: 'operator', label: $localize`:@@roleOperator:Operator` },
    { key: 'admin', label: $localize`:@@roleAdministrator:Administrator` },
  ];

  readonly languageLabels: Record<LocaleKey, string> = {
    en: 'EN',
    de: 'DE',
    fr: 'FR',
  };

  private readonly subscriptions = new Subscription();

  constructor(
    private readonly environmentService: EnvironmentService,
    private readonly roleService: RoleService,
    private readonly connectionService: ConnectionService,
    public readonly languageService: LanguageService
  ) {
    this.environments = this.environmentService.environments;
    this.environment$ = this.environmentService.environment$;
    this.role$ = this.roleService.role$;
    this.locales = this.languageService.supportedLocales;
    this.connectionState$ = this.connectionService.state$;
    this.selectedEnvironment = this.environmentService.current.key;
    this.selectedRole = this.roleService.current;
    this.selectedLocale = this.languageService.current;
    this.subscriptions.add(
      this.environmentService.environment$.subscribe((environment) => {
        this.selectedEnvironment = environment.key;
      })
    );
    this.subscriptions.add(
      this.roleService.role$.subscribe((role) => {
        this.selectedRole = role;
      })
    );
  }

  setEnvironment(value: EnvironmentKey): void {
    this.environmentService.setEnvironment(value);
  }

  setRole(value: UserRole): void {
    this.roleService.setRole(value);
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  trackNav(_index: number, item: NavigationItem): string {
    return item.id;
  }

  onEnvironmentChange(event: Event): void {
    const value = (event as unknown as EnvironmentKey) ?? this.selectedEnvironment;
    this.environmentService.setEnvironment(value);
  }

  toggleSidebar(): void {
    this.sidebarCollapsed = !this.sidebarCollapsed;
  }

  onRoleChange(event: Event): void {
    const value = (event as unknown as UserRole) ?? this.selectedRole;
    this.roleService.setRole(value);
  }

  changeLanguage(locale: LocaleKey): void {
    this.selectedLocale = locale;
    this.languageService.setLocale(locale);
  }

  resetFactory(): void {
    const environment = this.environmentService.current.key;
    if (environment === 'mock') {
      const controller = getDashboardController();
      void controller.loadFixture('startup');
      return;
    }
    console.info('[reset]', environment, 'reset not implemented yet');
  }

  isNavVisible(item: NavigationItem, role: UserRole | null): boolean {
    if (!role) {
      return false;
    }
    return item.roles.includes(role);
  }

  get connectionStatus(): string {
    return this.connectionStatusLabels[this.connectionService.currentState];
  }

  get currentError(): string | null {
    return this.connectionService.currentError;
  }
}
