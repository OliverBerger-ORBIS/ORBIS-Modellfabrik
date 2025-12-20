import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, of } from 'rxjs';
import { PresentationPageComponent } from '../presentation-page.component';
import { EnvironmentService } from '../../../services/environment.service';
import { MessageMonitorService } from '../../../services/message-monitor.service';
import { ConnectionService } from '../../../services/connection.service';
import { ModuleNameService } from '../../../services/module-name.service';
import { AgvRouteService } from '../../../services/agv-route.service';
import { AgvAnimationService } from '../../../services/agv-animation.service';
import { LanguageService } from '../../../services/language.service';
import { ChangeDetectorRef } from '@angular/core';
import * as mockDashboard from '../../../mock-dashboard';

// Mock getDashboardController
jest.spyOn(mockDashboard, 'getDashboardController').mockReturnValue({
  streams: { orders$: of({}) },
  loadTabFixture: jest.fn().mockResolvedValue(undefined),
  getCurrentFixture: jest.fn(() => 'startup'),
} as any);

describe('PresentationPageComponent', () => {
  let component: PresentationPageComponent;
  let fixture: ComponentFixture<PresentationPageComponent>;

  beforeEach(async () => {
    const environmentSubject = new BehaviorSubject({ key: 'mock' as const, label: 'Mock', description: 'Mock', connection: { mqttHost: 'localhost', mqttPort: 1883 } });
    const environmentServiceMock = {
      get current() {
        return environmentSubject.value;
      },
      environment$: environmentSubject.asObservable(),
    };

    const messageMonitorMock = {
      getLastMessage: jest.fn(() => of({ valid: false, payload: null })),
      getHistory: jest.fn(() => []),
      addMessage: jest.fn(),
    };

    const connectionServiceMock = {
      state$: new BehaviorSubject<'connected'>('connected'),
    };

    const moduleNameServiceMock = {
      getModuleDisplayText: jest.fn((id: string) => id),
    };

    const ftsRouteServiceMock = {
      initializeLayout: jest.fn(),
      getNodePosition: jest.fn(() => ({ x: 100, y: 100 })),
      findRoute: jest.fn(() => []),
      resolveNodeRef: jest.fn((nodeId: string) => nodeId),
    };

    const ftsAnimationServiceMock = {
      animationState$: new BehaviorSubject({
        isAnimating: false,
        animatedPosition: null,
        currentRoute: [],
      }),
      getState: jest.fn(() => ({
        isAnimating: false,
        animatedPosition: null,
        currentRoute: [],
      })),
      stopAnimation: jest.fn(),
      startAnimation: jest.fn(),
    };

    const languageServiceMock = {
      current: 'en' as const,
      locale$: new BehaviorSubject('en'),
    };

    const cdrMock = {
      markForCheck: jest.fn(),
      detectChanges: jest.fn(),
    };

    const httpMock = {
      get: jest.fn(() => of({ cells: [], roads: [] })),
    };

    await TestBed.configureTestingModule({
      imports: [PresentationPageComponent],
      providers: [
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: ConnectionService, useValue: connectionServiceMock },
        { provide: ModuleNameService, useValue: moduleNameServiceMock },
        { provide: AgvRouteService, useValue: ftsRouteServiceMock },
        { provide: AgvAnimationService, useValue: ftsAnimationServiceMock },
        { provide: LanguageService, useValue: languageServiceMock },
        { provide: ChangeDetectorRef, useValue: cdrMock },
        { provide: HttpClient, useValue: httpMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(PresentationPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render AgvTabComponent with presentationMode', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const agvTab = compiled.querySelector('app-agv-tab');
    expect(agvTab).toBeTruthy();
  });
});

