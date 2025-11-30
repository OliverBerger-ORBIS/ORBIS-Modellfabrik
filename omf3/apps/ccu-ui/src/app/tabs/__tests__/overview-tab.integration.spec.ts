import { ComponentFixture, TestBed } from '@angular/core/testing';
import { OverviewTabComponent } from '../overview-tab.component';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { EnvironmentService } from '../../services/environment.service';
import { ConnectionService } from '../../services/connection.service';
import { MessageValidationService } from '../../services/message-validation.service';
import { MessagePersistenceService } from '../../services/message-persistence.service';
import { firstValueFrom } from 'rxjs';
import type { ModuleState } from '@omf3/entities';

describe('OverviewTabComponent Integration', () => {
  let component: OverviewTabComponent;
  let fixture: ComponentFixture<OverviewTabComponent>;
  let messageMonitor: MessageMonitorService;
  let environmentService: EnvironmentService;

  beforeEach(() => {
    localStorage.clear();

    TestBed.configureTestingModule({
      imports: [OverviewTabComponent],
      providers: [
        MessageMonitorService,
        MessageValidationService,
        MessagePersistenceService,
        EnvironmentService,
        ConnectionService,
      ],
    });

    fixture = TestBed.createComponent(OverviewTabComponent);
    component = fixture.componentInstance;
    messageMonitor = TestBed.inject(MessageMonitorService);
    environmentService = TestBed.inject(EnvironmentService);
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('MessageMonitorService Integration', () => {
    it('should integrate with MessageMonitorService for module states', async () => {
      // Add module state message
      const moduleState: ModuleState = {
        moduleId: 'test-module',
        state: 'idle',
        lastSeen: new Date().toISOString(),
      };

      messageMonitor.addMessage('ccu/module/state', moduleState);

      // Initialize component
      component.ngOnInit();
      fixture.detectChanges();
      await new Promise((resolve) => setTimeout(resolve, 300));
      fixture.detectChanges();

      // Verify MessageMonitor has the message
      const lastMessage = await firstValueFrom(messageMonitor.getLastMessage('ccu/module/state'));
      expect(lastMessage).not.toBeNull();
      expect(lastMessage?.valid).toBe(true);
      
      // Verify component streams are initialized
      expect(component.ftsStates$).toBeDefined();
      expect(component.orders$).toBeDefined();
    });

    it('should update when new module state arrives', async () => {
      component.ngOnInit();
      fixture.detectChanges();

      // Add module state
      const state: ModuleState = {
        moduleId: 'module-1',
        state: 'idle',
        lastSeen: new Date().toISOString(),
      };

      messageMonitor.addMessage('ccu/module/state', state);
      await new Promise((resolve) => setTimeout(resolve, 300));
      fixture.detectChanges();

      // Verify MessageMonitor received the message
      const lastMessage = await firstValueFrom(messageMonitor.getLastMessage('ccu/module/state'));
      expect(lastMessage).not.toBeNull();
    });
  });

  describe('EnvironmentService Integration', () => {
    it('should detect mock mode correctly', () => {
      environmentService.setEnvironment('mock');
      fixture.detectChanges();

      expect(component.isMockMode).toBe(true);
    });

    it('should react to environment changes', () => {
      environmentService.setEnvironment('mock');
      fixture.detectChanges();
      expect(component.isMockMode).toBe(true);

      environmentService.setEnvironment('replay');
      fixture.detectChanges();
      expect(component.isMockMode).toBe(false);
    });
  });
});

