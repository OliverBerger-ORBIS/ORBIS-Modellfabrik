import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnDestroy, OnInit, AfterViewChecked, ElementRef, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MessageMonitorService, MonitoredMessage } from '../services/message-monitor.service';
import { EnvironmentService } from '../services/environment.service';
import { ModuleNameService } from '../services/module-name.service';
import { ShopfloorMappingService } from '../services/shopfloor-mapping.service';
import { resolveLegacyShopfloorPath } from '../shared/icons/legacy-shopfloor-map';
import { ICONS } from '../shared/icons/icon.registry';
import { BehaviorSubject, combineLatest, interval, Subscription } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';

interface TopicInfo {
  topic: string;
  messageCount: number;
  lastTimestamp: string;
  valid: boolean;
}

interface ModuleInfo {
  serial: string;
  name: string;
  icon: string;
}

type TopicTypeFilter = 'all' | 'ccu' | 'module-fts';
type StatusFilter = 'all' | 'connection' | 'state' | 'factsheet';

const CCU_ICON = 'assets/svg/ui/heading-ccu.svg';
const TXT_ICON = 'assets/svg/shopfloor/stations/mixer.svg';
const DSP_ICON = ICONS.brand.dsp;

@Component({
  standalone: true,
  selector: 'app-message-monitor-tab',
  imports: [CommonModule, FormsModule],
  templateUrl: './message-monitor-tab.component.html',
  styleUrl: './message-monitor-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MessageMonitorTabComponent implements OnInit, OnDestroy, AfterViewChecked {
  private readonly subscriptions = new Subscription();
  private readonly refreshTrigger = new BehaviorSubject<number>(0);
  
  @ViewChild('jsonCodeBlock', { static: false }) jsonCodeBlock?: ElementRef<HTMLElement>;
  private shouldHighlight = false;

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
  filterTopicType: TopicTypeFilter = 'all';
  filterModule = '';
  filterStatus: StatusFilter = 'all';
  
  // Available modules/FTS for dropdown (extracted from topics)
  availableModules: ModuleInfo[] = [];
  
  readonly monitorHeadingIcon = 'assets/svg/ui/heading-message-monitor.svg';
  
  private readonly STORAGE_KEY = 'omf3.message-monitor.filters';

  constructor(
    private readonly messageMonitor: MessageMonitorService,
    private readonly environmentService: EnvironmentService,
    private readonly moduleNameService: ModuleNameService,
    private readonly mappingService: ShopfloorMappingService
  ) {}

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  get environmentLabel(): string {
    return this.environmentService.current.label;
  }

  ngOnInit(): void {
    // Load persisted filter settings
    this.loadFilterSettings();
    
    // Extract available modules/FTS from topics
    this.updateAvailableModules();
    
    // Trigger initial refresh
    this.refreshTrigger.next(Date.now());
  }

  ngOnDestroy(): void {
    // Save filter settings when leaving tab
    this.saveFilterSettings();
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
    
    // Update available modules/FTS when topics change
    this.updateAvailableModules();
    
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
    // Topic type filter (All Topics, ccu-topics, Module/FTS topics)
    if (this.filterTopicType === 'ccu') {
      if (!message.topic.startsWith('ccu/')) {
        return false;
      }
    } else if (this.filterTopicType === 'module-fts') {
      // Filter for module/* and fts/* topics (with or without /v1/)
      const isModuleTopic = message.topic.startsWith('module/');
      const isFtsTopic = message.topic.startsWith('fts/');
      if (!isModuleTopic && !isFtsTopic) {
        return false;
      }
    }
    // 'all' shows everything, no filter needed

    // Module/FTS filter (only when Topic Type is Module/FTS)
    if (this.filterTopicType === 'module-fts' && this.filterModule) {
      // Special case: "AGV" filter shows all fts/* topics
      if (this.filterModule === 'AGV') {
        if (!message.topic.startsWith('fts/')) {
          return false;
        }
      } else {
        // Filter by module serial (for module topics)
      if (!message.topic.includes(this.filterModule)) {
        return false;
        }
      }
    }

    // Status filter (only when Topic Type is Module/FTS)
    if (this.filterTopicType === 'module-fts' && this.filterStatus !== 'all') {
      if (this.filterStatus === 'connection' && !message.topic.includes('/connection')) {
        return false;
      }
      if (this.filterStatus === 'state' && !message.topic.includes('/state')) {
        return false;
      }
      if (this.filterStatus === 'factsheet' && !message.topic.includes('/factsheet')) {
        return false;
      }
    }

    // Text filter (always applies)
    if (this.filterText && !message.topic.toLowerCase().includes(this.filterText.toLowerCase())) {
      return false;
    }

    return true;
  }

  selectMessage(message: MonitoredMessage): void {
    this.selectedMessage = message;
    this.shouldHighlight = true;
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
    this.filterTopicType = 'all';
    this.filterModule = '';
    this.filterStatus = 'all';
    this.refreshTrigger.next(Date.now());
  }

  onTopicTypeChange(): void {
    // Reset module filter when switching topic type
    if (this.filterTopicType !== 'module-fts') {
      this.filterModule = '';
    }
    this.refreshTrigger.next(Date.now());
  }

  onFilterChange(): void {
    this.refreshTrigger.next(Date.now());
  }

  updateAvailableModules(): void {
    const allTopics = this.messageMonitor.getTopics();
    const moduleSerials = new Set<string>();
    let hasFtsTopics = false;

    // Known topic suffixes that should NOT be treated as module serials
    const topicSuffixes = new Set(['status', 'connection', 'factsheet', 'state', 'order', 'instantAction']);

    // Extract module/FTS serials from topics
    allTopics.forEach(topic => {
      // Module topics: module/* (with or without /v1/)
      if (topic.startsWith('module/')) {
        const parts = topic.split('/');
        // Check for NodeRed pattern: module/v1/ff/NodeRed/<serial>/...
        if (parts.length >= 5 && parts[3] === 'NodeRed') {
          const potentialSerial = parts[4];
          // Only add if it's not a known topic suffix
          if (!topicSuffixes.has(potentialSerial)) {
            moduleSerials.add(potentialSerial);
          }
        } else if (parts.length >= 4 && parts[1] === 'v1' && parts[2] === 'ff') {
          // Direct pattern: module/v1/ff/<serial>/...
          const potentialSerial = parts[3];
          // Only add if it's not a known topic suffix
          if (!topicSuffixes.has(potentialSerial)) {
            moduleSerials.add(potentialSerial);
          }
        } else if (parts.length >= 2) {
          // Generic pattern: module/<serial>/...
          const potentialSerial = parts[1];
          // Only add if it's not a known topic suffix
          if (!topicSuffixes.has(potentialSerial)) {
            moduleSerials.add(potentialSerial);
          }
        }
      }
      // FTS topics: fts/* (with or without /v1/)
      else if (topic.startsWith('fts/')) {
        hasFtsTopics = true;
        const parts = topic.split('/');
        if (parts.length >= 4 && parts[1] === 'v1' && parts[2] === 'ff') {
          // Pattern: fts/v1/ff/<serial>/...
          const potentialSerial = parts[3];
          // Only add if it's not a known topic suffix
          if (!topicSuffixes.has(potentialSerial)) {
            moduleSerials.add(potentialSerial);
          }
        } else if (parts.length >= 2) {
          // Generic pattern: fts/<serial>/...
          const potentialSerial = parts[1];
          // Only add if it's not a known topic suffix
          if (!topicSuffixes.has(potentialSerial)) {
            moduleSerials.add(potentialSerial);
          }
        }
      }
    });

    // Build module info list
    const moduleList = Array.from(moduleSerials)
      .map((serial) => {
        const moduleType = this.mappingService.getModuleTypeFromSerial(serial) ?? serial;
        const displayName = this.moduleNameService.getModuleDisplayText(moduleType, 'id-full');
        const icon = this.mappingService.getModuleIcon(serial) ?? resolveLegacyShopfloorPath('assets/svg/shopfloor/stations/dps-station.svg');
        return { serial, name: displayName, icon };
      })
      .sort((a, b) => a.name.localeCompare(b.name));

    // Add "AGV" option if FTS topics exist
    if (hasFtsTopics) {
      // Check if AGV is already in the list (by serial '5iO4')
      const hasAgv = moduleList.some(m => m.serial === '5iO4' || m.name.toUpperCase().includes('AGV'));
      if (!hasAgv) {
        // Add AGV option at the beginning
        moduleList.unshift({
          serial: 'AGV',
          name: this.moduleNameService.getModuleDisplayText('FTS', 'id-full'),
          icon: resolveLegacyShopfloorPath('assets/svg/shopfloor/shared/agv-vehicle.svg')
        });
      }
    }

    this.availableModules = moduleList;
  }

  getTopicName(topic: string): { name: string; icon: string } {
    // CCU topics
    if (topic.startsWith('ccu/')) {
      return { name: 'CCU', icon: CCU_ICON };
    }

    // DSP topics (use DSP icon)
    if (topic.startsWith('dsp/')) {
      return { name: 'DSP', icon: DSP_ICON };
    }

    // TXT topics
    if (topic.startsWith('/j1/txt/')) {
      return { name: 'TXT', icon: TXT_ICON };
    }

    // Module topics: extract serial and get module info
    if (topic.startsWith('module/v1/ff/')) {
      const parts = topic.split('/');
      let serial: string | undefined;
      
      // Check for NodeRed pattern: module/v1/ff/NodeRed/<serial>/...
      if (parts.length >= 5 && parts[3] === 'NodeRed') {
        serial = parts[4];
      } else if (parts.length >= 4) {
        // Direct pattern: module/v1/ff/<serial>/...
        serial = parts[3];
      }

      if (serial) {
        const moduleType = this.mappingService.getModuleTypeFromSerial(serial) ?? serial;
        const displayName = this.moduleNameService.getModuleDisplayText(moduleType, 'id-only');
        const icon = this.mappingService.getModuleIcon(serial) ?? resolveLegacyShopfloorPath('assets/svg/shopfloor/stations/dps-station.svg');
        return { name: displayName, icon };
      }
    }

    // FTS topics: fts/v1/ff/<serial>/...
    if (topic.startsWith('fts/v1/ff/')) {
      const parts = topic.split('/');
      if (parts.length >= 4) {
        const serial = parts[3];
        const moduleType = this.mappingService.getModuleTypeFromSerial(serial) ?? 'FTS';
        const displayName = this.moduleNameService.getModuleDisplayText(moduleType, 'id-only');
        const icon = this.mappingService.getModuleIcon(serial) ?? resolveLegacyShopfloorPath('assets/svg/shopfloor/shared/agv-vehicle.svg');
        return { name: displayName, icon };
      }
    }

    // Default: use first element of topic path
    const firstElement = topic.split('/')[0] || topic;
    return { name: firstElement, icon: resolveLegacyShopfloorPath('assets/svg/shopfloor/stations/dps-station.svg') };
  }

  private loadFilterSettings(): void {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const settings = JSON.parse(stored);
        this.filterTopicType = settings.filterTopicType || 'all';
        this.filterModule = settings.filterModule || '';
        this.filterStatus = settings.filterStatus || 'all';
        this.filterText = settings.filterText || '';
      }
    } catch (error) {
      console.warn('[MessageMonitor] Failed to load filter settings:', error);
    }
  }

  private saveFilterSettings(): void {
    try {
      const settings = {
        filterTopicType: this.filterTopicType,
        filterModule: this.filterModule,
        filterStatus: this.filterStatus,
        filterText: this.filterText,
      };
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(settings));
    } catch (error) {
      console.warn('[MessageMonitor] Failed to save filter settings:', error);
    }
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
    this.shouldHighlight = false;
  }

  ngAfterViewChecked(): void {
    // Highlight JSON when code block is rendered
    if (this.shouldHighlight && this.jsonCodeBlock) {
      hljs.highlightElement(this.jsonCodeBlock.nativeElement);
      this.shouldHighlight = false;
    }
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

  getCloseLabel(): string {
    return $localize`:@@messageMonitorClose:Close`;
  }

  getValidMessageTooltip(): string {
    return $localize`:@@messageMonitorValidPayload:Valid`;
  }

  getInvalidMessageTooltip(): string {
    return $localize`:@@messageMonitorInvalidPayload:Invalid`;
  }
}
