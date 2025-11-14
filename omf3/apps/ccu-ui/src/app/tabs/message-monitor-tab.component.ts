import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MessageMonitorService, MonitoredMessage } from '../services/message-monitor.service';
import { EnvironmentService } from '../services/environment.service';
import { BehaviorSubject, combineLatest, interval, Subscription } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

interface TopicInfo {
  topic: string;
  messageCount: number;
  lastTimestamp: string;
  valid: boolean;
}

@Component({
  standalone: true,
  selector: 'app-message-monitor-tab',
  imports: [CommonModule, FormsModule],
  templateUrl: './message-monitor-tab.component.html',
  styleUrl: './message-monitor-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MessageMonitorTabComponent implements OnInit, OnDestroy {
  private readonly subscriptions = new Subscription();
  private readonly refreshTrigger = new BehaviorSubject<number>(0);

  // Observable state - get all messages from all topics, sorted newest first
  readonly messages$ = combineLatest([
    this.refreshTrigger,
    interval(1000).pipe(startWith(0))
  ]).pipe(
    map(() => this.getAllMessages())
  );

  // UI state
  selectedMessage: MonitoredMessage | null = null;
  
  // Filter state
  filterText = '';
  filterModule = '';
  filterConnectionState = false;
  
  readonly monitorHeadingIcon = 'headings/smart.svg';

  constructor(
    private readonly messageMonitor: MessageMonitorService,
    private readonly environmentService: EnvironmentService
  ) {}

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  get environmentLabel(): string {
    return this.environmentService.current.label;
  }

  ngOnInit(): void {
    // Trigger initial refresh
    this.refreshTrigger.next(Date.now());
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  getAllMessages(): MonitoredMessage[] {
    const allTopics = this.messageMonitor.getTopics();
    const allMessages: MonitoredMessage[] = [];
    
    // Collect all messages from all topics
    allTopics.forEach(topic => {
      const history = this.messageMonitor.getHistory(topic);
      allMessages.push(...history);
    });
    
    // Filter messages
    const filtered = allMessages.filter(msg => this.filterMessage(msg));
    
    // Sort by timestamp, newest first (as per new requirement "Die Neuste zuoberst")
    return filtered.sort((a, b) => {
      if (!a.timestamp) return 1;
      if (!b.timestamp) return -1;
      return b.timestamp.localeCompare(a.timestamp);
    });
  }

  filterMessage(message: MonitoredMessage): boolean {
    // Text filter
    if (this.filterText && !message.topic.toLowerCase().includes(this.filterText.toLowerCase())) {
      return false;
    }

    // Module/Serial filter
    if (this.filterModule) {
      const filterLower = this.filterModule.toLowerCase();
      if (!message.topic.toLowerCase().includes(filterLower)) {
        return false;
      }
    }

    // Connection/State filter
    if (this.filterConnectionState) {
      if (!message.topic.includes('/connection') && !message.topic.includes('/state')) {
        return false;
      }
    }

    return true;
  }

  selectMessage(message: MonitoredMessage): void {
    this.selectedMessage = message;
  }

  formatTimestamp(ts: string): string {
    if (!ts) {
      return '—';
    }
    try {
      const date = new Date(ts);
      if (Number.isNaN(date.getTime())) {
        return ts;
      }
      return date.toLocaleString();
    } catch {
      return ts;
    }
  }

  formatJsonPayload(payload: unknown): string {
    try {
      return JSON.stringify(payload, null, 2);
    } catch {
      return String(payload);
    }
  }

  clearFilters(): void {
    this.filterText = '';
    this.filterModule = '';
    this.filterConnectionState = false;
    this.refreshTrigger.next(Date.now());
  }

  clearAllData(): void {
    if (confirm($localize`:@@messageMonitorClearConfirm:Are you sure you want to clear all monitored data?`)) {
      this.messageMonitor.clearAll();
      this.selectedMessage = null;
      this.refreshTrigger.next(Date.now());
    }
  }

  closeDetailPanel(): void {
    this.selectedMessage = null;
  }

  formatPayloadPreview(payload: unknown): string {
    try {
      const str = JSON.stringify(payload);
      // Show first 100 characters
      return str.length > 100 ? str.substring(0, 100) + '...' : str;
    } catch {
      return String(payload);
    }
  }

  trackByMessage(_index: number, message: MonitoredMessage): string {
    return `${message.topic}-${message.timestamp}`;
  }
}
