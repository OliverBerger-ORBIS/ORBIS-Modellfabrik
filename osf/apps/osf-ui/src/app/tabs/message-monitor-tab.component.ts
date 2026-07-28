import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnDestroy, OnInit, AfterViewChecked, ElementRef, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MessageMonitorService, MonitoredMessage } from '../services/message-monitor.service';
import { EnvironmentService } from '../services/environment.service';
import { ModuleNameService } from '../services/module-name.service';
import { ShopfloorLayoutService } from '../services/shopfloor-layout.service';
import { ShopfloorMappingService } from '../services/shopfloor-mapping.service';
import { resolveLegacyShopfloorPath } from '../shared/icons/legacy-shopfloor-map';
import { ICONS } from '../shared/icons/icon.registry';
import { BehaviorSubject, combineLatest, interval, Subscription } from 'rxjs';
import { filter, map, startWith } from 'rxjs/operators';
import hljs from 'highlight.js';

interface ModuleInfo {
  serial: string;
  name: string;
  icon: string;
}

type TopicTypeFilter = 'all' | 'ccu' | 'dsp' | 'module-fts' | 'osf';
type StatusFilter = 'all' | 'connection' | 'state' | 'factsheet';

const CCU_ICON = 'assets/svg/ui/heading-ccu.svg';
const TXT_ICON = 'assets/svg/shopfloor/stations/mixer.svg';
const DSP_ICON = ICONS.brand.dsp;
const FTS_ICON = resolveLegacyShopfloorPath('assets/svg/shopfloor/shared/agv-vehicle.svg');
const DEFAULT_MODULE_ICON = resolveLegacyShopfloorPath('assets/svg/shopfloor/stations/dps-station.svg');

/** CCU placeholders / demo serials — not shown in Live module filter. */
function isPlaceholderOrDemoSerial(serial: string): boolean {
  const upper = serial.toUpperCase();
  return upper.endsWith('-MISSING') || upper.endsWith('-DEMO');
}

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
    interval(1000).pipe(startWith(0)),
  ]).pipe(map(() => this.getAllMessages()));

  // UI state
  selectedMessage: MonitoredMessage | null = null;

  // Filter state
  filterText = '';
  filterTopicType: TopicTypeFilter = 'all';
  filterModule = '';
  filterStatus: StatusFilter = 'all';

  /** Module/AGV filter options — layout registry (Live); + topic extras in Mock/Replay */
  availableModules: ModuleInfo[] = [];

  readonly monitorHeadingIcon = 'assets/svg/ui/heading-message-monitor.svg';

  private readonly STORAGE_KEY = 'OSF.message-monitor.filters';

  constructor(
    private readonly messageMonitor: MessageMonitorService,
    private readonly environmentService: EnvironmentService,
    private readonly moduleNameService: ModuleNameService,
    private readonly mappingService: ShopfloorMappingService,
    private readonly layoutService: ShopfloorLayoutService
  ) {}

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  get isLiveEnvironment(): boolean {
    return this.environmentService.current.key === 'live';
  }

  get environmentLabel(): string {
    return this.environmentService.current.label;
  }

  ngOnInit(): void {
    this.loadFilterSettings();

    this.updateAvailableModules();
    this.subscriptions.add(
      this.layoutService.config$
        .pipe(filter((config): config is NonNullable<typeof config> => config !== null))
        .subscribe(() => {
          this.updateAvailableModules();
          this.refreshTrigger.next(Date.now());
        })
    );

    this.refreshTrigger.next(Date.now());
  }

  ngOnDestroy(): void {
    this.saveFilterSettings();
    this.subscriptions.unsubscribe();
  }

  getAllMessages(): MonitoredMessage[] {
    const allTopics = this.messageMonitor.getTopics();
    const allMessages: MonitoredMessage[] = [];

    allTopics.forEach((topic) => {
      const history = this.messageMonitor.getHistory(topic);
      allMessages.push(...history);
    });

    this.updateAvailableModules();

    const filtered = allMessages.filter((msg) => this.filterMessage(msg));

    return filtered.sort((a, b) => {
      if (!a.timestamp) return 1;
      if (!b.timestamp) return -1;
      return b.timestamp.localeCompare(a.timestamp);
    });
  }

  filterMessage(message: MonitoredMessage): boolean {
    if (this.filterTopicType === 'ccu') {
      if (!message.topic.startsWith('ccu/')) {
        return false;
      }
    } else if (this.filterTopicType === 'dsp') {
      if (!message.topic.startsWith('dsp/')) {
        return false;
      }
    } else if (this.filterTopicType === 'module-fts') {
      const isModuleTopic = message.topic.startsWith('module/');
      const isFtsTopic = message.topic.startsWith('fts/');
      if (!isModuleTopic && !isFtsTopic) {
        return false;
      }
    } else if (this.filterTopicType === 'osf') {
      if (!message.topic.startsWith('osf/')) {
        return false;
      }
    }

    if (this.filterTopicType === 'module-fts' && this.filterModule) {
      // Legacy: "AGV" filter shows all fts/* topics (localStorage)
      if (this.filterModule === 'AGV') {
        if (!message.topic.startsWith('fts/')) {
          return false;
        }
      } else if (!message.topic.includes(this.filterModule)) {
        return false;
      }
    }

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
    if (this.filterTopicType !== 'module-fts') {
      this.filterModule = '';
    }
    this.refreshTrigger.next(Date.now());
  }

  onFilterChange(): void {
    this.refreshTrigger.next(Date.now());
  }

  /**
   * Build Module/AGV dropdown from shopfloor layout registry.
   * Live: layout serials only (no HBW-DEMO / *-MISSING).
   * Mock/Replay: layout + non-placeholder topic serials not already listed.
   */
  updateAvailableModules(): void {
    const seen = new Set<string>();
    const moduleList: ModuleInfo[] = [];

    if (this.mappingService.isInitialized()) {
      const bySerial = new Map(
        this.mappingService.getAllModules().map((m) => [m.serialNumber, m])
      );
      for (const serial of this.mappingService.getShopfloorTableRowSerialOrder()) {
        const module = bySerial.get(serial);
        if (!module || seen.has(serial) || isPlaceholderOrDemoSerial(serial)) {
          continue;
        }
        moduleList.push(this.toFilterModuleInfo(module.serialNumber, module.moduleType));
        seen.add(serial);
        seen.add(serial.toLowerCase());
      }
      for (const module of bySerial.values()) {
        if (seen.has(module.serialNumber) || isPlaceholderOrDemoSerial(module.serialNumber)) {
          continue;
        }
        moduleList.push(this.toFilterModuleInfo(module.serialNumber, module.moduleType));
        seen.add(module.serialNumber);
        seen.add(module.serialNumber.toLowerCase());
      }
    }

    if (!this.isLiveEnvironment) {
      for (const serial of this.extractSerialsFromTopics()) {
        if (isPlaceholderOrDemoSerial(serial)) {
          continue;
        }
        const mapped = this.mappingService.getModuleBySerial(serial);
        const canonical = mapped?.serialNumber ?? serial;
        if (
          seen.has(canonical) ||
          seen.has(canonical.toLowerCase()) ||
          seen.has(serial.toLowerCase())
        ) {
          continue;
        }
        const moduleType =
          mapped?.moduleType ?? this.mappingService.getModuleTypeFromSerial(serial) ?? serial;
        moduleList.push(this.toFilterModuleInfo(canonical, moduleType));
        seen.add(canonical);
        seen.add(canonical.toLowerCase());
      }
    }

    if (!this.mappingService.isInitialized()) {
      for (const serial of this.extractSerialsFromTopics()) {
        if (isPlaceholderOrDemoSerial(serial) || seen.has(serial.toLowerCase())) {
          continue;
        }
        moduleList.push(this.toFilterModuleInfo(serial, serial));
        seen.add(serial);
        seen.add(serial.toLowerCase());
      }
    }

    moduleList.sort((a, b) => a.name.localeCompare(b.name));
    this.availableModules = moduleList;

    if (
      this.filterModule &&
      this.filterModule !== 'AGV' &&
      !moduleList.some((m) => m.serial === this.filterModule)
    ) {
      this.filterModule = '';
    }
  }

  private toFilterModuleInfo(serial: string, moduleType: string): ModuleInfo {
    const isFts =
      moduleType === 'FTS' || this.mappingService.getModuleTypeFromSerial(serial) === 'FTS';
    let name: string;
    if (isFts) {
      const agvLabel = this.mappingService.getAgvLabel(serial);
      const ftsFull = this.moduleNameService.getModuleFullName('FTS');
      name = agvLabel
        ? `${agvLabel} (${ftsFull})`
        : this.moduleNameService.getModuleDisplayText('FTS', 'id-full');
    } else {
      name = this.moduleNameService.getModuleDisplayText(moduleType, 'id-full');
    }
    // Layout stores icon keys (e.g. "FTS"); img src needs asset paths
    const mappedIcon = this.mappingService.getModuleIcon(serial);
    const icon =
      mappedIcon && mappedIcon.includes('/')
        ? mappedIcon
        : isFts
          ? FTS_ICON
          : DEFAULT_MODULE_ICON;
    return { serial, name, icon };
  }

  private extractSerialsFromTopics(): string[] {
    const allTopics = this.messageMonitor.getTopics();
    const moduleSerials = new Set<string>();
    const topicSuffixes = new Set([
      'status',
      'connection',
      'factsheet',
      'state',
      'order',
      'instantAction',
    ]);

    allTopics.forEach((topic) => {
      if (topic.startsWith('module/')) {
        const parts = topic.split('/');
        if (parts.length >= 5 && parts[3] === 'NodeRed') {
          const potentialSerial = parts[4];
          if (!topicSuffixes.has(potentialSerial)) {
            moduleSerials.add(potentialSerial);
          }
        } else if (parts.length >= 4 && parts[1] === 'v1' && parts[2] === 'ff') {
          const potentialSerial = parts[3];
          if (!topicSuffixes.has(potentialSerial)) {
            moduleSerials.add(potentialSerial);
          }
        } else if (parts.length >= 2) {
          const potentialSerial = parts[1];
          if (!topicSuffixes.has(potentialSerial)) {
            moduleSerials.add(potentialSerial);
          }
        }
      } else if (topic.startsWith('fts/')) {
        const parts = topic.split('/');
        if (parts.length >= 4 && parts[1] === 'v1' && parts[2] === 'ff') {
          const potentialSerial = parts[3];
          if (!topicSuffixes.has(potentialSerial)) {
            moduleSerials.add(potentialSerial);
          }
        } else if (parts.length >= 2) {
          const potentialSerial = parts[1];
          if (!topicSuffixes.has(potentialSerial)) {
            moduleSerials.add(potentialSerial);
          }
        }
      }
    });

    return Array.from(moduleSerials);
  }

  getTopicName(topic: string): { name: string; icon: string } {
    if (topic.startsWith('ccu/')) {
      return { name: 'CCU', icon: CCU_ICON };
    }

    if (topic.startsWith('dsp/')) {
      return { name: 'DSP', icon: DSP_ICON };
    }

    if (topic.startsWith('/j1/txt/')) {
      return { name: 'TXT', icon: TXT_ICON };
    }

    if (topic.startsWith('module/v1/ff/')) {
      const parts = topic.split('/');
      let serial: string | undefined;

      if (parts.length >= 5 && parts[3] === 'NodeRed') {
        serial = parts[4];
      } else if (parts.length >= 4) {
        serial = parts[3];
      }

      if (serial) {
        const moduleType = this.mappingService.getModuleTypeFromSerial(serial) ?? serial;
        const displayName = this.moduleNameService.getModuleDisplayText(moduleType, 'id-only');
        const mappedIcon = this.mappingService.getModuleIcon(serial);
        const icon =
          mappedIcon && mappedIcon.includes('/') ? mappedIcon : DEFAULT_MODULE_ICON;
        return { name: displayName, icon };
      }
    }

    // FTS topics — prefer AGV-1 / AGV-2 when layout known
    if (topic.startsWith('fts/v1/ff/')) {
      const parts = topic.split('/');
      if (parts.length >= 4) {
        const serial = parts[3];
        const agvLabel = this.mappingService.getAgvLabel(serial);
        const displayName =
          agvLabel ?? this.moduleNameService.getModuleDisplayText('FTS', 'id-only');
        const mappedIcon = this.mappingService.getModuleIcon(serial);
        const icon = mappedIcon && mappedIcon.includes('/') ? mappedIcon : FTS_ICON;
        return { name: displayName, icon };
      }
    }

    const firstElement = topic.split('/')[0] || topic;
    return { name: firstElement, icon: DEFAULT_MODULE_ICON };
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
    if (
      confirm(
        $localize`:@@messageMonitorClearConfirm:Are you sure you want to clear all monitored data?`
      )
    ) {
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
    if (this.shouldHighlight && this.jsonCodeBlock) {
      hljs.highlightElement(this.jsonCodeBlock.nativeElement);
      this.shouldHighlight = false;
    }
  }

  formatPayloadPreview(payload: unknown): string {
    try {
      const str = JSON.stringify(payload);
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
