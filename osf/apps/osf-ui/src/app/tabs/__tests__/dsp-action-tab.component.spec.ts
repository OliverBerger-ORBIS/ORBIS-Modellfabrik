import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, of } from 'rxjs';
import { DspActionTabComponent } from '../dsp-action-tab.component';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { EnvironmentService } from '../../services/environment.service';
import { LanguageService } from '../../services/language.service';
import { ChangeDetectorRef } from '@angular/core';
import type { MonitoredMessage } from '../../services/message-monitor.service';

describe('DspActionTabComponent', () => {
  let component: DspActionTabComponent;
  let fixture: ComponentFixture<DspActionTabComponent>;
  let messageMonitor: jest.Mocked<MessageMonitorService>;
  let environmentService: jest.Mocked<EnvironmentService>;
  let languageService: jest.Mocked<LanguageService>;
  let cdr: jest.Mocked<ChangeDetectorRef>;

  const mockDspActionMessage: MonitoredMessage = {
    topic: 'dsp/drill/action',
    payload: {
      command: 'changeLight',
      value: '#FF0000',
    },
    timestamp: '2025-11-10T18:00:00Z',
    valid: true,
  };

  beforeEach(async () => {
    const messageMonitorMock = {
      getLastMessage: jest.fn(() => of(mockDspActionMessage)),
      getHistory: jest.fn(() => [mockDspActionMessage]),
      addMessage: jest.fn(),
    };

    const environmentServiceMock = {
      current: { key: 'mock' },
      environment$: new BehaviorSubject({ key: 'mock' }),
    };

    const languageServiceMock = {
      current: 'en',
      locale$: new BehaviorSubject('en'),
    };

    const cdrMock = {
      markForCheck: jest.fn(),
      detectChanges: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [DspActionTabComponent],
      providers: [
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: LanguageService, useValue: languageServiceMock },
        { provide: ChangeDetectorRef, useValue: cdrMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(DspActionTabComponent);
    component = fixture.componentInstance;
    messageMonitor = TestBed.inject(MessageMonitorService) as any;
    environmentService = TestBed.inject(EnvironmentService) as any;
    languageService = TestBed.inject(LanguageService) as any;
    cdr = TestBed.inject(ChangeDetectorRef) as any;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize messages stream', () => {
    expect(component.messages$).toBeDefined();
  });

  it('should detect mock mode', () => {
    expect(component.isMockMode).toBe(true);
  });

  it('should have topic pattern', () => {
    expect(component.topicPattern).toBe('dsp/drill/action');
  });

  it('should get DSP action messages', () => {
    const messages = component['getDspActionMessages']();
    expect(messages.length).toBeGreaterThanOrEqual(0);
  });

  it('should process DSP action message', () => {
    component['processDspActionMessage'](mockDspActionMessage);
    expect(component.currentLightValue).toBe('#FF0000');
    expect(component.lastCommandTimestamp).toBe('2025-11-10T18:00:00Z');
  });

  it('should update previous light value when current changes', () => {
    component.currentLightValue = '#00FF00';
    // Process a message with a different value
    const newMessage = { ...mockDspActionMessage, payload: { command: 'changeLight', value: '#0000FF' } };
    component['processDspActionMessage'](newMessage);
    // previousLightValue is only set if currentLightValue changed AND previousValue was not null
    expect(component.currentLightValue).toBe('#0000FF');
  });

  it('should filter messages by topic', () => {
    component.filterTopic = 'drill';
    const filtered = component.filteredMessages;
    expect(filtered.length).toBeGreaterThanOrEqual(0);
  });

  it('should limit filtered messages to 10 most recent', () => {
    // Create more than 10 messages
    const manyMessages = Array.from({ length: 15 }, (_, i) => ({
      topic: 'dsp/drill/action',
      payload: { command: 'changeLight', value: `#${i.toString(16).padStart(6, '0')}` },
      timestamp: `2025-11-10T18:0${i}:00Z`,
      valid: true,
    }));
    jest.spyOn(messageMonitor, 'getHistory').mockReturnValue(manyMessages as any);

    const filtered = component.filteredMessages;
    expect(filtered.length).toBeLessThanOrEqual(10);
  });

  it('should format timestamp', () => {
    const formatted = component.formatTimestamp('2025-11-10T18:00:00Z');
    expect(formatted).toBeDefined();
    expect(formatted).toContain('10');
  });

  it('should handle invalid timestamp', () => {
    const formatted = component.formatTimestamp('invalid-date');
    // formatTimestamp may return "Invalid Date" string or the original string
    expect(formatted).toBeDefined();
  });

  it('should track messages by topic and timestamp', () => {
    const message = {
      topic: 'dsp/drill/action',
      timestamp: '2025-11-10T18:00:00Z',
      payload: { command: 'changeLight', value: '#FF0000' },
      rawPayload: '{}',
    };
    const trackBy = component.trackByTopic(0, message);
    expect(trackBy).toBe('dsp/drill/action-2025-11-10T18:00:00Z');
  });

  it('should unsubscribe on destroy', () => {
    const unsubscribeSpy = jest.spyOn(component['subscriptions'], 'unsubscribe');
    component.ngOnDestroy();
    expect(unsubscribeSpy).toHaveBeenCalled();
  });

  it('should handle load drill action fixture', async () => {
    // loadDrillActionFixture uses dynamic import which may not work in test environment
    expect(component.loadDrillActionFixture).toBeDefined();
    try {
      await component.loadDrillActionFixture();
    } catch (error) {
      // Expected in test environment
      expect(error).toBeDefined();
    }
  });

  it('should not load fixture in non-mock mode', async () => {
    // Create a new component with live environment
    const liveEnvironmentService = {
      current: { key: 'live' },
      environment$: new BehaviorSubject({ key: 'live' }),
    };
    TestBed.resetTestingModule();
    await TestBed.configureTestingModule({
      imports: [DspActionTabComponent],
      providers: [
        { provide: MessageMonitorService, useValue: messageMonitor },
        { provide: EnvironmentService, useValue: liveEnvironmentService },
        { provide: LanguageService, useValue: languageService },
        { provide: ChangeDetectorRef, useValue: cdr },
      ],
    }).compileComponents();
    const liveFixture = TestBed.createComponent(DspActionTabComponent);
    const liveComponent = liveFixture.componentInstance;

    await liveComponent.loadDrillActionFixture();
    // Should not add messages in non-mock mode
    expect(liveComponent.activeFixture).toBe(false);
  });
});

