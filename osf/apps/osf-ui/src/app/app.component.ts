import { ChangeDetectionStrategy, Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AsyncPipe, NgClass, NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { EnvironmentKey, EnvironmentService } from './services/environment.service';
import { RoleService, UserRole } from './services/role.service';
import { LanguageService, LocaleKey } from './services/language.service';
import { ConnectionService, ConnectionState } from './services/connection.service';
import { getDashboardController, type DashboardMessageMonitor } from './mock-dashboard';
import { MessageMonitorService } from './services/message-monitor.service';
import { FooterComponent } from './components/footer/footer.component';
import { Subscription } from 'rxjs';

interface NavigationItem {
  id: string;
  label: string;
  route: string;
  roles: UserRole[];
  icon?: string;
}

const NAVIGATION_ITEMS: Omit<NavigationItem, 'label'>[] = [
  {
    id: 'dsp',
    route: '/dsp',
    roles: ['operator', 'admin'],
  },
  {
    id: 'shopfloor',
    route: '/module',
    roles: ['operator', 'admin'],
  },
  {
    id: 'process',
    route: '/process',
    roles: ['operator', 'admin'],
  },
  {
    id: 'order',
    route: '/order',
    roles: ['operator', 'admin'],
  },
  {
    id: 'sensor',
    route: '/sensor',
    roles: ['operator', 'admin'],
  },
  {
    id: 'configuration',
    route: '/configuration',
    roles: ['admin'],
  },
  {
    id: 'message-monitor',
    route: '/message-monitor',
    roles: ['admin'],
    icon: 'assets/svg/ui/heading-message-monitor.svg',
  },
  {
    id: 'agv',
    route: '/agv',
    roles: ['operator', 'admin'],
  },
  {
    id: 'settings',
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
    FooterComponent,
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
  get navigation(): NavigationItem[] {
    const labelMap: Record<string, string> = {
      'dsp': $localize`:@@navDsp:DSP`,
      'shopfloor': $localize`:@@navShopfloor:Shopfloor`,
      'overview': $localize`:@@navOverview:Overview`,
      'order': $localize`:@@navOrder:Orders`,
      'process': $localize`:@@navProcess:Processes`,
      'sensor': $localize`:@@navSensor:Environment Data`,
      'module': $localize`:@@navModule:Modules`,
      'configuration': $localize`:@@navConfiguration:Configuration`,
      'message-monitor': $localize`:@@navMessageMonitor:Message Monitor`,
      'fts': $localize`:@@navFts:AGV`,
      'track-trace': $localize`:@@navTrackTrace:Track & Trace`,
      'settings': $localize`:@@navSettings:Settings`,
    };
    
    return NAVIGATION_ITEMS
      .filter((item) => this.isNavVisible({ ...item, label: labelMap[item.id] || item.id } as NavigationItem, this.selectedRole))
      .map((item) => ({
        ...item,
        label: labelMap[item.id] || item.id,
      })) as NavigationItem[];
  }
  sidebarCollapsed = false;
  selectedEnvironment: EnvironmentKey;
  selectedRole: UserRole;
  selectedLocale: LocaleKey;
  readonly connectionState$;

  readonly headerTitle = $localize`:@@headerTitle:SmartFactory`;
  readonly headerSubtitle =
    $localize`:@@headerSubtitle:Fischertechnik Model Factory (APS) orchestrated by ORBIS DSP — IT/OT integration, ERP connectivity and AI-enabled shopfloor intelligence.`;
  readonly resetLabel = $localize`:@@headerResetButton:Reset factory`;
  readonly connectButtonLabel = $localize`:@@headerConnectButtonLabel:Connect`;
  readonly orbitLogoPath = 'assets/svg/brand/orbis-logo.svg';

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
  private readonly dashboardMessageMonitor: DashboardMessageMonitor;

  constructor(
    private readonly environmentService: EnvironmentService,
    private readonly roleService: RoleService,
    private readonly connectionService: ConnectionService,
    public readonly languageService: LanguageService,
    private readonly messageMonitor: MessageMonitorService
  ) {
    this.environments = this.environmentService.environments;
    this.environment$ = this.environmentService.environment$;
    this.role$ = this.roleService.role$;
    this.locales = this.languageService.supportedLocales;
    this.connectionState$ = this.connectionService.state$;
    this.selectedEnvironment = this.environmentService.current.key;
    this.selectedRole = this.roleService.current;
    this.selectedLocale = this.languageService.current;
    
    // Note: With hash routing, locale detection and redirects are handled by:
    // 1. ensureHashRoute() in main.ts (ensures hash exists before bootstrap)
    // 2. Router redirectTo configuration in app.routes.ts
    // No need for pathname-based redirect logic here
    
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

    this.dashboardMessageMonitor = {
      addMessage: (topic: string, payload: unknown, timestamp?: string) =>
        this.messageMonitor.addMessage(topic, payload, timestamp),
      getTopics: () => this.messageMonitor.getTopics(),
      getHistory: <T>(topic: string) => this.messageMonitor.getHistory<T>(topic),
    };

    // Initialize dashboard controller for mock mode with MessageMonitor
    if (this.environmentService.current.key === 'mock') {
      getDashboardController(undefined, this.dashboardMessageMonitor);
    }
    
    // Update dashboard controller when MQTT client becomes available
    this.subscriptions.add(
      this.connectionService.state$.subscribe((state) => {
        if (state === 'connected') {
          const mqttClient = this.connectionService.mqttClient;
          if (mqttClient) {
            // Recreate dashboard controller with MQTT client for live/replay mode
            const controller = getDashboardController(mqttClient, this.dashboardMessageMonitor);
            // Also update existing controller if it has updateMqttClient method
            if (controller.updateMqttClient) {
              controller.updateMqttClient(mqttClient);
            }
            console.log('[app] Dashboard controller updated with MQTT client');
          }
        }
      })
    );
    
    // Update dashboard controller when environment changes to mock
    this.subscriptions.add(
      this.environmentService.environment$.subscribe((environment) => {
        if (environment.key === 'mock') {
          getDashboardController(undefined, this.dashboardMessageMonitor);
        }
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

  getRouteWithLocale(route: string): string[] {
    const currentLocale = this.languageService.current;
    // Remove leading slash from route if present
    const cleanRoute = route.startsWith('/') ? route.slice(1) : route;
    // Return as array for routerLink
    return [currentLocale, cleanRoute];
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

  async resetFactory(): Promise<void> {
    const environment = this.environmentService.current.key;
    if (environment === 'mock') {
      const controller = getDashboardController(undefined, this.dashboardMessageMonitor);
      void controller.loadFixture('startup');
      return;
    }
    
    // For live/replay environments, use business layer command
    try {
      const dashboard = getDashboardController();
      await dashboard.commands.resetFactory();
    } catch (error) {
      console.warn('Failed to reset factory', error);
    }
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

  manualConnect(): void {
    const environment = this.environmentService.getDefinition(this.environmentService.current.key);
    if (environment) {
      this.connectionService.connect(environment);
    }
  }

  manualDisconnect(): void {
    this.connectionService.disconnect();
  }
}
