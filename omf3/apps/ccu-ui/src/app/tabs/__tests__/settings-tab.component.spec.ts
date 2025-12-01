import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { BehaviorSubject } from 'rxjs';
import { SettingsTabComponent } from '../settings-tab.component';
import { EnvironmentService, EnvironmentDefinition } from '../../services/environment.service';
import { ConnectionService, ConnectionSettings } from '../../services/connection.service';
import { ExternalLinksService, ExternalLinksSettings } from '../../services/external-links.service';

describe('SettingsTabComponent', () => {
  let component: SettingsTabComponent;
  let fixture: ComponentFixture<SettingsTabComponent>;
  let environmentService: jest.Mocked<EnvironmentService>;
  let connectionService: jest.Mocked<ConnectionService>;
  let externalLinksService: jest.Mocked<ExternalLinksService>;

  const mockEnvironments: EnvironmentDefinition[] = [
    {
      key: 'mock',
      label: 'Mock',
      description: 'Mock environment',
      readOnly: true,
      connection: {
        mqttHost: 'localhost',
        mqttPort: 1883,
        mqttPath: '',
      },
    },
    {
      key: 'replay',
      label: 'Replay',
      description: 'Replay environment',
      readOnly: false,
      connection: {
        mqttHost: 'localhost',
        mqttPort: 9001,
        mqttPath: '',
        mqttUsername: 'user',
        mqttPassword: 'pass',
      },
    },
  ];

  const mockConnectionSettings: ConnectionSettings = {
    autoConnect: true,
    retryEnabled: true,
    retryIntervalMs: 5000,
  };

  const mockExternalLinks: ExternalLinksSettings = {
    orbisWebsiteUrl: 'https://www.orbis.de',
    dspControlUrl: 'https://dsp.example.com',
    managementCockpitUrl: 'https://management.example.com',
    grafanaDashboardUrl: 'https://grafana.example.com',
    smartfactoryDashboardUrl: '/dsp-action',
  };

  beforeEach(async () => {
    const environmentServiceMock = {
      environments: mockEnvironments,
      current: { key: 'mock' },
      environment$: new BehaviorSubject({ key: 'mock' }),
      updateConnection: jest.fn(),
    };

    const connectionServiceMock = {
      currentSettings: mockConnectionSettings,
      updateSettings: jest.fn(),
    };

    const externalLinksServiceMock = {
      current: mockExternalLinks,
      settings$: new BehaviorSubject(mockExternalLinks),
      updateSettings: jest.fn(),
    };

    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    });

    await TestBed.configureTestingModule({
      imports: [SettingsTabComponent, ReactiveFormsModule],
      providers: [
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: ConnectionService, useValue: connectionServiceMock },
        { provide: ExternalLinksService, useValue: externalLinksServiceMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(SettingsTabComponent);
    component = fixture.componentInstance;
    environmentService = TestBed.inject(EnvironmentService) as any;
    connectionService = TestBed.inject(ConnectionService) as any;
    externalLinksService = TestBed.inject(ExternalLinksService) as any;
    
    // Trigger ngOnInit
    component.ngOnInit();
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize environments', () => {
    expect(component.environments.length).toBe(2);
  });

  it('should create forms for each environment', () => {
    expect(component.forms.size).toBe(2);
    expect(component.forms.has('mock')).toBe(true);
    expect(component.forms.has('replay')).toBe(true);
  });

  it('should initialize connection form', () => {
    expect(component.connectionForm).toBeDefined();
    expect(component.connectionForm.get('autoConnect')?.value).toBe(true);
    expect(component.connectionForm.get('retryEnabled')?.value).toBe(true);
    expect(component.connectionForm.get('retryIntervalMs')?.value).toBe(5000);
  });

  it('should initialize links form', () => {
    expect(component.linksForm).toBeDefined();
    expect(component.linksForm.get('orbisWebsiteUrl')?.value).toBe('https://www.orbis.de');
    expect(component.linksForm.get('dspControlUrl')?.value).toBe('https://dsp.example.com');
    expect(component.linksForm.get('managementCockpitUrl')?.value).toBe('https://management.example.com');
    expect(component.linksForm.get('grafanaDashboardUrl')?.value).toBe('https://grafana.example.com');
    expect(component.linksForm.get('smartfactoryDashboardUrl')?.value).toBe('/dsp-action');
  });

  it('should save environment connection settings', () => {
    const replayForm = component.forms.get('replay');
    if (replayForm) {
      replayForm.patchValue({
        mqttHost: 'newhost',
        mqttPort: 9002,
      });
      component.save(mockEnvironments[1]);
      expect(environmentService.updateConnection).toHaveBeenCalledWith('replay', {
        mqttHost: 'newhost',
        mqttPort: 9002,
        mqttUsername: 'user',
        mqttPassword: 'pass',
      });
    }
  });

  it('should not save read-only environment', () => {
    component.save(mockEnvironments[0]);
    expect(environmentService.updateConnection).not.toHaveBeenCalled();
  });

  it('should not save invalid form', () => {
    const replayForm = component.forms.get('replay');
    if (replayForm) {
      replayForm.patchValue({
        mqttHost: '', // Invalid: required field
      });
      component.save(mockEnvironments[1]);
      expect(environmentService.updateConnection).not.toHaveBeenCalled();
    }
  });

  it('should save connection settings', () => {
    component.connectionForm.patchValue({
      autoConnect: false,
      retryIntervalMs: 10000,
    });
    component.saveConnectionSettings();
    expect(connectionService.updateSettings).toHaveBeenCalled();
    expect(component.connectionForm.pristine).toBe(true);
  });

  it('should not save invalid connection form', () => {
    component.connectionForm.patchValue({
      retryIntervalMs: 500, // Invalid: min is 1000
    });
    component.saveConnectionSettings();
    expect(connectionService.updateSettings).not.toHaveBeenCalled();
  });

  it('should save external links', () => {
    component.linksForm.patchValue({
      orbisWebsiteUrl: 'https://new.orbis.de',
    });
    component.saveExternalLinks();
    expect(externalLinksService.updateSettings).toHaveBeenCalled();
    expect(component.linksForm.pristine).toBe(true);
  });

  it('should not save invalid links form', () => {
    component.linksForm.patchValue({
      orbisWebsiteUrl: '', // Invalid: required field
    });
    component.saveExternalLinks();
    expect(externalLinksService.updateSettings).not.toHaveBeenCalled();
  });

  it('should mark form as pristine after save', () => {
    const replayForm = component.forms.get('replay');
    if (replayForm) {
      replayForm.patchValue({ mqttHost: 'newhost' });
      replayForm.markAsDirty(); // Explicitly mark as dirty
      expect(replayForm.pristine).toBe(false);
      component.save(mockEnvironments[1]);
      expect(replayForm.pristine).toBe(true);
    }
  });
});

