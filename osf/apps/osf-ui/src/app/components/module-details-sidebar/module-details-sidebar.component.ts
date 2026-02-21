import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, Input, OnInit, OnChanges, SimpleChanges, Output, EventEmitter, AfterViewChecked, ElementRef, ViewChild, QueryList, ViewChildren } from '@angular/core';
import { MessageMonitorService, MonitoredMessage } from '../../services/message-monitor.service';
import { ShopfloorMappingService } from '../../services/shopfloor-mapping.service';
import { combineLatest, Observable, of } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';

interface ModuleTopicMessage {
  topic: string;
  payload: unknown; // Can be object or string
  timestamp: string;
}

@Component({
  standalone: true,
  selector: 'app-module-details-sidebar',
  imports: [CommonModule],
  templateUrl: './module-details-sidebar.component.html',
  styleUrl: './module-details-sidebar.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ModuleDetailsSidebarComponent implements OnInit, OnChanges, AfterViewChecked {
  @Input() serialId: string | null = null;
  @Input() moduleName: string | null = null;
  @Input() isOpen = false;
  @Output() close = new EventEmitter<void>();

  @ViewChildren('jsonCodeBlock') jsonCodeBlocks?: QueryList<ElementRef<HTMLElement>>;
  private shouldHighlight = false;

  messages$: Observable<ModuleTopicMessage[]> = of([]);
  
  readonly closeLabel = $localize`:@@moduleDetailsClose:Close sidebar`;

  constructor(
    private readonly messageMonitor: MessageMonitorService,
    private readonly cdr: ChangeDetectorRef,
    private readonly mappingService: ShopfloorMappingService
  ) {}

  ngOnInit(): void {
    this.updateMessages();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['serialId'] && this.serialId) {
      this.updateMessages();
    }
    if (changes['isOpen'] && this.isOpen) {
      // Trigger highlighting when sidebar opens
      this.shouldHighlight = true;
    }
  }

  ngAfterViewChecked(): void {
    // Highlight JSON when code blocks are rendered
    if (this.shouldHighlight && this.jsonCodeBlocks) {
      this.jsonCodeBlocks.forEach(codeBlock => {
        if (codeBlock.nativeElement) {
          hljs.highlightElement(codeBlock.nativeElement);
        }
      });
      this.shouldHighlight = false;
    }
  }

  closeSidebar(): void {
    this.close.emit();
  }

  private updateMessages(): void {
    if (!this.serialId) {
      this.messages$ = of([]);
      this.cdr.markForCheck();
      return;
    }

    // Get all topics and filter for this module's serial ID
    const allTopics = this.messageMonitor.getTopics();
    const moduleTopics: string[] = [];
    
    // Patterns to match (Standard-Modul-Topics bevorzugt):
    // - module/v1/ff/<serialId>/connection, state, factsheet
    // - fts/v1/ff/<serialId>/... (for FTS)
    // NodeRed-Topics (module/v1/ff/NodeRed/<serialId>/...) werden für connection NICHT verwendet,
    // um mit Fischertechnik-Standard konform zu sein.
    
    allTopics.forEach((topic) => {
      const knownSerials = this.mappingService.getAllModules().map((m) => m.serialId);
      const matchingSerial = knownSerials.find((s) => topic.includes(s));

      if (this.serialId && matchingSerial === this.serialId) {
        if (topic.startsWith('module/') || topic.startsWith('fts/')) {
          if (topic.includes('/connection') || topic.includes('/state') || topic.includes('/factsheet')) {
            // Connection-Info: nur Standard-Topics, keine NodeRed-Topics
            if (topic.includes('/connection') && topic.includes('NodeRed')) {
              return;
            }
            moduleTopics.push(topic);
          }
        }
      }
    });
    
    // Also check ccu/pairing/state (contains all modules)
    moduleTopics.push('ccu/pairing/state');
    
    const topics = moduleTopics;

    // Get last message for each topic
    const messageStreams = topics.map((topic) =>
      this.messageMonitor.getLastMessage(topic).pipe(
        map((msg) => {
          if (!msg || !msg.valid) {
            return null;
          }
          // For ccu/pairing/state, check if it contains this module
          if (topic === 'ccu/pairing/state') {
            const payload = msg.payload as any;
            if (payload?.modules) {
              const module = payload.modules.find((m: any) => m.serialNumber === this.serialId);
              if (!module) {
                return null;
              }
            }
          }
          return {
            topic,
            payload: msg.payload, // Keep as original (object or string)
            timestamp: msg.timestamp,
          } as ModuleTopicMessage;
        }),
        startWith(null)
      )
    );

    this.messages$ = combineLatest(messageStreams).pipe(
      map((messages) => messages.filter((msg): msg is ModuleTopicMessage => msg !== null)),
      map((messages) => {
        // Sort by timestamp (newest first)
        return messages.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
      })
    );

    this.cdr.markForCheck();
  }

  formatTimestamp(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch {
      return timestamp;
    }
  }

  formatJson(payload: string): string {
    try {
      const parsed = JSON.parse(payload);
      return JSON.stringify(parsed, null, 2);
    } catch {
      return payload;
    }
  }

  formatJsonPayload(payload: unknown): string {
    if (typeof payload === 'string') {
      try {
        const parsed = JSON.parse(payload);
        return JSON.stringify(parsed, null, 2);
      } catch {
        return payload;
      }
    }
    return JSON.stringify(payload, null, 2);
  }
}

