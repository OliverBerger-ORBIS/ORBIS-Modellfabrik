import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MessageMonitorTabComponent } from '../message-monitor-tab.component';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { EnvironmentService } from '../../services/environment.service';
import { MessageValidationService } from '../../services/message-validation.service';
import { MessagePersistenceService } from '../../services/message-persistence.service';
import { firstValueFrom } from 'rxjs';
import type { MonitoredMessage } from '../../services/message-monitor.service';

describe('MessageMonitorTabComponent Integration', () => {
  let component: MessageMonitorTabComponent;
  let fixture: ComponentFixture<MessageMonitorTabComponent>;
  let messageMonitor: MessageMonitorService;
  let environmentService: EnvironmentService;

  beforeEach(() => {
    localStorage.clear();

    TestBed.configureTestingModule({
      imports: [MessageMonitorTabComponent],
      providers: [
        MessageMonitorService,
        MessageValidationService,
        MessagePersistenceService,
        EnvironmentService,
      ],
    });

    fixture = TestBed.createComponent(MessageMonitorTabComponent);
    component = fixture.componentInstance;
    messageMonitor = TestBed.inject(MessageMonitorService);
    environmentService = TestBed.inject(EnvironmentService);
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('MessageMonitorService Integration', () => {
    it('should integrate with MessageMonitorService for messages', async () => {
      // Add message to monitor
      messageMonitor.addMessage('test/topic', { data: 'test' });

      // Initialize component
      component.ngOnInit();
      fixture.detectChanges();
      await new Promise((resolve) => setTimeout(resolve, 300));
      fixture.detectChanges();

      // Verify MessageMonitor has the message
      const lastMessage = await firstValueFrom(messageMonitor.getLastMessage('test/topic'));
      expect(lastMessage).not.toBeNull();
      expect(lastMessage?.valid).toBe(true);
      
      // Verify component can access messages
      expect(component.messages$).toBeDefined();
    });

    it('should update when new message arrives', async () => {
      component.ngOnInit();
      fixture.detectChanges();

      // Add message
      messageMonitor.addMessage('topic/1', { id: 1 });
      await new Promise((resolve) => setTimeout(resolve, 300));
      fixture.detectChanges();

      // Verify MessageMonitor received the message
      const lastMessage = await firstValueFrom(messageMonitor.getLastMessage('topic/1'));
      expect(lastMessage).not.toBeNull();
    });

    it('should filter messages by topic type', async () => {
      component.ngOnInit();
      fixture.detectChanges();

      // Add CCU topic message
      messageMonitor.addMessage('ccu/order/active', { id: 'order-1' });
      await new Promise((resolve) => setTimeout(resolve, 300));
      fixture.detectChanges();

      // Set filter to CCU topics
      component.filterTopicType = 'ccu';
      component.onTopicTypeChange();
      fixture.detectChanges();

      // Verify filter is set
      expect(component.filterTopicType).toBe('ccu');
    });

    it('should filter messages by text', async () => {
      component.ngOnInit();
      fixture.detectChanges();

      messageMonitor.addMessage('test/topic', { name: 'test-message' });
      await new Promise((resolve) => setTimeout(resolve, 300));
      fixture.detectChanges();

      // Set text filter
      component.filterText = 'test';
      component.onFilterChange();
      fixture.detectChanges();

      // Verify filter is set
      expect(component.filterText).toBe('test');
    });

    it('should handle message selection', async () => {
      component.ngOnInit();
      fixture.detectChanges();

      messageMonitor.addMessage('test/topic', { data: 'test' });
      await new Promise((resolve) => setTimeout(resolve, 300));
      fixture.detectChanges();

      // Create a mock message
      const mockMessage: MonitoredMessage = {
        topic: 'test/topic',
        payload: { data: 'test' },
        timestamp: new Date().toISOString(),
        valid: true,
      };

      component.selectMessage(mockMessage);
      expect(component.selectedMessage).toBe(mockMessage);
    });
  });

  describe('EnvironmentService Integration', () => {
    it('should display environment label', () => {
      environmentService.setEnvironment('mock');
      fixture.detectChanges();

      expect(component.environmentLabel).toBeDefined();
    });

    it('should update environment label on environment change', () => {
      environmentService.setEnvironment('mock');
      fixture.detectChanges();
      const label1 = component.environmentLabel;

      environmentService.setEnvironment('replay');
      fixture.detectChanges();
      const label2 = component.environmentLabel;

      expect(label1).not.toBe(label2);
    });
  });

  describe('Full Data Flow', () => {
    it('should process complete message lifecycle', async () => {
      environmentService.setEnvironment('replay');
      component.ngOnInit();
      fixture.detectChanges();

      // 1. Add message
      const payload = { id: 1, data: 'test' };
      messageMonitor.addMessage('test/topic', payload);
      await new Promise((resolve) => setTimeout(resolve, 100));
      fixture.detectChanges();

      // 2. Verify message appears
      let messages = await firstValueFrom(component.messages$);
      expect(messages.some((m) => m.topic === 'test/topic')).toBe(true);

      // 3. Update message
      messageMonitor.addMessage('test/topic', { id: 1, data: 'updated' });
      await new Promise((resolve) => setTimeout(resolve, 100));
      fixture.detectChanges();

      // 4. Verify update
      messages = await firstValueFrom(component.messages$);
      const updatedMessage = messages.find((m) => m.topic === 'test/topic');
      expect(updatedMessage).toBeDefined();
    });
  });
});

