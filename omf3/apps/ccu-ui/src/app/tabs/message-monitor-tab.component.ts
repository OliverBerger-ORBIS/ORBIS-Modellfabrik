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

  // Observable state
  readonly topics$ = combineLatest([
    this.refreshTrigger,
    interval(1000).pipe(startWith(0))
  ]).pipe(
    map(() => this.getTopicsInfo())
  );

  // UI state
  selectedTopic: string | null = null;
  selectedMessage: MonitoredMessage | null = null;
  messageHistory: MonitoredMessage[] = [];
  
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

  getTopicsInfo(): TopicInfo[] {
    const allTopics = this.messageMonitor.getTopics();
    
    return allTopics
      .map(topic => {
        const history = this.messageMonitor.getHistory(topic);
        const lastMessage = history.length > 0 ? history[history.length - 1] : null;
        
        return {
          topic,
          messageCount: history.length,
          lastTimestamp: lastMessage?.timestamp || '',
          valid: lastMessage?.valid ?? true,
        };
      })
      .filter(info => this.filterTopic(info))
      .sort((a, b) => {
        // Sort by last timestamp (most recent first)
        if (!a.lastTimestamp) return 1;
        if (!b.lastTimestamp) return -1;
        return b.lastTimestamp.localeCompare(a.lastTimestamp);
      });
  }

  filterTopic(info: TopicInfo): boolean {
    // Text filter
    if (this.filterText && !info.topic.toLowerCase().includes(this.filterText.toLowerCase())) {
      return false;
    }

    // Module/Serial filter
    if (this.filterModule) {
      const filterLower = this.filterModule.toLowerCase();
      if (!info.topic.toLowerCase().includes(filterLower)) {
        return false;
      }
    }

    // Connection/State filter
    if (this.filterConnectionState) {
      if (!info.topic.includes('/connection') && !info.topic.includes('/state')) {
        return false;
      }
    }

    return true;
  }

  selectTopic(topic: string): void {
    this.selectedTopic = topic;
    this.messageHistory = this.messageMonitor.getHistory(topic);
    
    // Select the last message by default
    if (this.messageHistory.length > 0) {
      this.selectedMessage = this.messageHistory[this.messageHistory.length - 1];
    } else {
      this.selectedMessage = null;
    }
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
      this.selectedTopic = null;
      this.selectedMessage = null;
      this.messageHistory = [];
      this.refreshTrigger.next(Date.now());
    }
  }

  clearTopicData(): void {
    if (this.selectedTopic) {
      if (confirm($localize`:@@messageMonitorClearTopicConfirm:Clear all data for topic ${this.selectedTopic}?`)) {
        this.messageMonitor.clearTopic(this.selectedTopic);
        this.selectedTopic = null;
        this.selectedMessage = null;
        this.messageHistory = [];
        this.refreshTrigger.next(Date.now());
      }
    }
  }

  getRetentionLimit(): number {
    return this.selectedTopic ? this.messageMonitor.getRetention(this.selectedTopic) : 0;
  }

  trackByTopic(_index: number, item: TopicInfo): string {
    return item.topic;
  }

  trackByMessage(index: number, _message: MonitoredMessage): number {
    return index;
  }
}
