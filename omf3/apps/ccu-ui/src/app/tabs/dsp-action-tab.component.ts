import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MessageMonitorService, MonitoredMessage } from '../services/message-monitor.service';
import { EnvironmentService } from '../services/environment.service';
import { LanguageService } from '../services/language.service';
import { BehaviorSubject, combineLatest, interval, Subscription } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

interface DspActionMessage {
  topic: string;
  timestamp: string;
  payload: {
    command: string;
    value: string;
  };
  rawPayload: string;
}

@Component({
  standalone: true,
  selector: 'app-dsp-action-tab',
  imports: [CommonModule, FormsModule],
  templateUrl: './dsp-action-tab.component.html',
  styleUrl: './dsp-action-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspActionTabComponent implements OnInit, OnDestroy {
  private readonly subscriptions = new Subscription();
  private readonly refreshTrigger = new BehaviorSubject<number>(0);
  
  readonly messages$ = combineLatest([
    this.refreshTrigger,
    interval(1000).pipe(startWith(0))
  ]).pipe(
    map(() => this.getDspActionMessages())
  );

  // Filter state
  filterTopic = '';
  showDeveloperMode = false;

  // changeLight visualization
  currentLightValue: string | null = null;
  previousLightValue: string | null = null;
  lastCommandTimestamp: string | null = null;

  readonly topicPattern = 'dsp/drill/action';

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  constructor(
    private readonly messageMonitor: MessageMonitorService,
    private readonly environmentService: EnvironmentService,
    private readonly languageService: LanguageService,
    private readonly cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    // Subscribe to dsp/drill/action topic
    const messageSub = this.messageMonitor.getLastMessage(this.topicPattern).subscribe((msg) => {
      if (msg) {
        // Store previous value BEFORE processing new message
        const previousValue = this.currentLightValue;
        this.processDspActionMessage(msg);
        // Only update previous value if current value actually changed
        if (this.currentLightValue !== previousValue && previousValue !== null) {
          this.previousLightValue = previousValue;
        }
        this.refreshTrigger.next(Date.now());
        this.cdr.markForCheck();
      }
    });
    this.subscriptions.add(messageSub);

    // Subscribe to messages$ to trigger change detection
    const allMessagesSub = this.messages$.subscribe(() => {
      this.cdr.markForCheck();
    });
    this.subscriptions.add(allMessagesSub);

    // Note: Angular's $localize works at compile-time and runtime translations
    // are loaded in main.ts before bootstrap. When locale changes, the page
    // reloads (see language.service.ts), so translations should be available.
    // No special handling needed here - the i18n attributes in the template
    // will use the loaded translations automatically.
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  private getDspActionMessages(): DspActionMessage[] {
    // Get message history from MessageMonitorService
    const history = this.messageMonitor.getHistory(this.topicPattern);
    return history.map((msg) => {
      try {
        const payload = typeof msg.payload === 'object' && msg.payload !== null
          ? msg.payload as { command?: string; value?: string }
          : JSON.parse(String(msg.payload));
        
        return {
          topic: msg.topic,
          timestamp: msg.timestamp,
          payload: {
            command: payload.command || 'unknown',
            value: payload.value || '',
          },
          rawPayload: JSON.stringify(msg.payload, null, 2),
        };
      } catch (error) {
        return {
          topic: msg.topic,
          timestamp: msg.timestamp,
          payload: {
            command: 'parse-error',
            value: '',
          },
          rawPayload: JSON.stringify(msg.payload, null, 2),
        };
      }
    });
  }

  private processDspActionMessage(msg: MonitoredMessage): void {
    try {
      const payload = typeof msg.payload === 'object' && msg.payload !== null
        ? msg.payload as { command?: string; value?: string }
        : JSON.parse(String(msg.payload));

      if (payload.command === 'changeLight' && payload.value) {
        // Only update if value actually changed
        if (this.currentLightValue !== payload.value) {
          this.currentLightValue = payload.value;
          this.lastCommandTimestamp = msg.timestamp;
        }
      }
    } catch (error) {
      console.error('[dsp-action] Failed to process message:', error);
    }
  }

  get filteredMessages(): DspActionMessage[] {
    const messages = this.getDspActionMessages();
    let filtered = messages;
    if (this.filterTopic) {
      filtered = messages.filter((msg) =>
        msg.topic.toLowerCase().includes(this.filterTopic.toLowerCase())
      );
    }
    // Limit to 10 most recent messages
    return filtered.slice(-10).reverse();
  }

  formatTimestamp(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      const locale = this.languageService.current === 'de' ? 'de-DE' : this.languageService.current === 'fr' ? 'fr-FR' : 'en-US';
      return date.toLocaleString(locale, {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch {
      return timestamp;
    }
  }

  trackByTopic(_: number, message: DspActionMessage): string {
    return `${message.topic}-${message.timestamp}`;
  }

  async loadDrillActionFixture(): Promise<void> {
    if (!this.isMockMode) {
      return;
    }
    try {
      const { createDspActionFixtureStream } = await import('@omf3/testing-fixtures');
      const stream$ = createDspActionFixtureStream({
        intervalMs: 1000,
        loop: true,
      });
      // Subscribe to the stream and add messages directly to MessageMonitor
      const subscription = stream$.subscribe((message) => {
        try {
          const payload = typeof message.payload === 'string' 
            ? JSON.parse(message.payload) 
            : message.payload;
          this.messageMonitor.addMessage(message.topic, payload, message.timestamp);
          this.refreshTrigger.next(Date.now());
        } catch (error) {
          console.error('[dsp-action] Failed to parse message payload:', error);
        }
      });
      // Store subscription to clean up later if needed
      this.subscriptions.add(subscription);
    } catch (error) {
      console.error('[dsp-action] Failed to load drill action fixture:', error);
    }
  }
}

