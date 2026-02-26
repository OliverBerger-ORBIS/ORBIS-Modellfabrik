import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { AppComponent } from './app.component';
import { EnvironmentService } from './services/environment.service';
import { LanguageService } from './services/language.service';
import { RoleService } from './services/role.service';
import { ConnectionService } from './services/connection.service';
import { MessageMonitorService } from './services/message-monitor.service';
import { WorkpieceHistoryService } from './services/workpiece-history.service';
import * as mockDashboard from './mock-dashboard';

// Mock getDashboardController to avoid createGateway issues in tests
jest.spyOn(mockDashboard, 'getDashboardController').mockReturnValue({
  streams: {
    orders$: { pipe: jest.fn(() => ({ subscribe: jest.fn() })) } as any,
    completedOrders$: { pipe: jest.fn(() => ({ subscribe: jest.fn() })) } as any,
    orderCounts$: { pipe: jest.fn(() => ({ subscribe: jest.fn() })) } as any,
    stockByPart$: { pipe: jest.fn(() => ({ subscribe: jest.fn() })) } as any,
    moduleStates$: { pipe: jest.fn(() => ({ subscribe: jest.fn() })) } as any,
    ftsStates$: { pipe: jest.fn(() => ({ subscribe: jest.fn() })) } as any,
    moduleOverview$: { pipe: jest.fn(() => ({ subscribe: jest.fn() })) } as any,
    inventoryOverview$: { pipe: jest.fn(() => ({ subscribe: jest.fn() })) } as any,
    flows$: { pipe: jest.fn(() => ({ subscribe: jest.fn() })) } as any,
    config$: { pipe: jest.fn(() => ({ subscribe: jest.fn() })) } as any,
    sensorOverview$: { pipe: jest.fn(() => ({ subscribe: jest.fn() })) } as any,
    cameraFrames$: { pipe: jest.fn(() => ({ subscribe: jest.fn() })) } as any,
  },
  streams$: { pipe: jest.fn(() => ({ subscribe: jest.fn() })) } as any,
  commands: {
    calibrateModule: jest.fn(),
    setFtsCharge: jest.fn(),
    dockFts: jest.fn(),
    sendCustomerOrder: jest.fn(),
    requestRawMaterial: jest.fn(),
    requestCorrelationInfo: jest.fn(),
    moveCamera: jest.fn(),
    resetFactory: jest.fn(),
  },
  loadFixture: jest.fn(),
  getCurrentFixture: jest.fn(() => 'startup'),
} as any);

describe('AppComponent', () => {
  // Mock window.location to avoid JSDOM navigation errors
  const originalLocation = window.location;
  let mockLocation: Location;

  beforeEach(async () => {
    // Mock window.location with a valid locale in pathname to avoid redirect
    mockLocation = {
      ...originalLocation,
      pathname: '/en/dsp',
      href: '/en/dsp',
    } as Location;
    
    // Replace window.location
    Object.defineProperty(window, 'location', {
      writable: true,
      value: mockLocation,
    });

    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [
        provideRouter([]),
        EnvironmentService,
        LanguageService,
        RoleService,
        ConnectionService,
        MessageMonitorService,
        { provide: WorkpieceHistoryService, useValue: { initialize: jest.fn() } },
      ],
    }).compileComponents();
  });

  afterEach(() => {
    // Restore original location
    Object.defineProperty(window, 'location', {
      writable: true,
      value: originalLocation,
    });
  });

  it('should render dashboard header', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    // Header title is now "SmartFactory" (i18n)
    expect(compiled.querySelector('h1')?.textContent).toContain('SmartFactory');
    // Navigation items are now dynamic and i18n, so we just check that nav exists
    const navLinks = Array.from(compiled.querySelectorAll('nav a'));
    expect(navLinks.length).toBeGreaterThan(0);
  });
});
