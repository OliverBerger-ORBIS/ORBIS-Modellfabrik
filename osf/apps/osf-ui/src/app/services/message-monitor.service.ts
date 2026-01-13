import { Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { MessageValidationService } from './message-validation.service';
import { MessagePersistenceService } from './message-persistence.service';

export interface MonitoredMessage<T = unknown> {
  topic: string;
  payload: T;
  timestamp: string;
  valid: boolean;
  validationErrors?: string[];
}

interface CircularBuffer<T> {
  items: T[];
  maxSize: number;
}

const DEFAULT_RETENTION = 50;

// Topics that bypass buffer (no history, only current value in Subject)
// These topics maintain architectural consistency by staying in MessageMonitor
// but skip buffer/persistence to optimize memory for high-frequency data
const SKIP_BUFFER_TOPICS = ['/j1/txt/1/i/cam'];

// Default retention configuration for specific topics
const RETENTION_CONFIG: Record<string, number> = {
  '/j1/txt/1/i/cam': 0,       // Camera frames: bypass mode (no buffer)
  '/j1/txt/1/i/bme680': 100,  // BME680 sensor: high retention
  '/j1/txt/1/i/ldr': 100,     // LDR sensor: high retention
  '/j1/txt/1/i/quality_check': 50, // Quality check images: moderate retention
};

@Injectable({ providedIn: 'root' })
export class MessageMonitorService implements OnDestroy {
  private readonly subjects = new Map<string, BehaviorSubject<MonitoredMessage | null>>();
  private readonly buffers = new Map<string, CircularBuffer<MonitoredMessage>>();
  private readonly retentionConfig = new Map<string, number>(Object.entries(RETENTION_CONFIG));
  private broadcastChannel?: BroadcastChannel;

  constructor(
    private readonly validationService: MessageValidationService,
    private readonly persistenceService: MessagePersistenceService
  ) {
    this.loadPersistedData();
    this.setupBroadcastChannel();
  }

  /**
   * Get the last message for a topic as an Observable
   * Returns null if no message has been received yet
   */
  getLastMessage<T = unknown>(topic: string): Observable<MonitoredMessage<T> | null> {
    // For bypass topics (e.g., camera), there's no buffer - just return/create the subject
    if (SKIP_BUFFER_TOPICS.includes(topic)) {
      if (!this.subjects.has(topic)) {
        this.subjects.set(topic, new BehaviorSubject<MonitoredMessage | null>(null));
      }
      return this.subjects.get(topic)!.asObservable() as Observable<MonitoredMessage<T> | null>;
    }

    // Standard topics: Always check buffer for current value FIRST, even if subject already exists
    // This ensures we get the latest message even if subject was created before message arrived
    const buffer = this.buffers.get(topic);
    const lastMessage = buffer && buffer.items.length > 0 
      ? buffer.items[buffer.items.length - 1] 
      : null;
    
    if (!this.subjects.has(topic)) {
      // Initialize BehaviorSubject with last message if available, otherwise null
      this.subjects.set(topic, new BehaviorSubject<MonitoredMessage | null>(lastMessage));
    } else {
      // Subject already exists - ALWAYS sync it with current buffer value
      // This is critical to handle race conditions where:
      // 1. Tab calls getLastMessage() before connection is established -> Subject initialized with null
      // 2. Connection established and messages arrive -> Buffer updated, but Subject might still be null
      // 3. Tab subscribes -> Should get the latest message from buffer, not null
      const currentValue = this.subjects.get(topic)!.value;
      
      // Update if different (by reference or by timestamp to catch new messages)
      if (currentValue !== lastMessage) {
        // If both are non-null, compare timestamps to detect new messages
        if (currentValue && lastMessage) {
          if (currentValue.timestamp !== lastMessage.timestamp) {
            this.subjects.get(topic)!.next(lastMessage);
          }
        } else {
          // One is null or they're different references - always update
          this.subjects.get(topic)!.next(lastMessage);
        }
      }
    }
    
    return this.subjects.get(topic)!.asObservable() as Observable<MonitoredMessage<T> | null>;
  }

  /**
   * Get message history for a topic
   * Returns empty array if no history exists
   */
  getHistory<T = unknown>(topic: string): MonitoredMessage<T>[] {
    const buffer = this.buffers.get(topic);
    return buffer ? [...buffer.items] as MonitoredMessage<T>[] : [];
  }

  /**
   * Add a new message to the monitor
   * This validates, stores, persists, and broadcasts the message
   */
  addMessage(topic: string, payload: unknown, timestamp?: string): void {
    const ts = timestamp || new Date().toISOString();
    
    // Validate message against schema
    const validation = this.validationService.validate(topic, payload);
    
    const message: MonitoredMessage = {
      topic,
      payload,
      timestamp: ts,
      valid: validation.valid,
      validationErrors: validation.errors,
    };

    // Log validation errors
    if (!validation.valid && validation.errors) {
      console.warn(`[MessageMonitor] Validation failed for topic ${topic}:`, validation.errors);
    }

    // Bypass mode for high-frequency topics (e.g., camera frames)
    // Maintains architectural consistency - tabs still use getLastMessage()
    // But skips buffer/persistence to optimize memory
    if (SKIP_BUFFER_TOPICS.includes(topic)) {
      // Only update BehaviorSubject with current value - no buffer, no persistence
      if (!this.subjects.has(topic)) {
        this.subjects.set(topic, new BehaviorSubject<MonitoredMessage | null>(message));
      } else {
        this.subjects.get(topic)!.next(message);
      }
      // No broadcast for bypass topics to avoid cross-tab traffic
      return;
    }

    // Standard path for all other topics:
    // Add to circular buffer FIRST to ensure buffer is always up-to-date
    // This ensures getLastMessage() can always retrieve the latest message
    this.addToBuffer(topic, message);

    // Update BehaviorSubject for immediate access
    // This ensures all subscribers get the new message immediately
    if (!this.subjects.has(topic)) {
      this.subjects.set(topic, new BehaviorSubject<MonitoredMessage | null>(message));
    } else {
      this.subjects.get(topic)!.next(message);
    }

    // Persist to localStorage (if allowed for this topic)
    if (this.persistenceService.shouldPersist(topic)) {
      const buffer = this.buffers.get(topic);
      if (buffer) {
        this.persistenceService.persist(topic, buffer.items);
      }
    }

    // Broadcast to other tabs
    this.broadcastMessage(message);
  }

  /**
   * Set retention limit for a specific topic
   */
  setRetention(topic: string, limit: number): void {
    this.retentionConfig.set(topic, limit);
    
    // Trim existing buffer if needed
    const buffer = this.buffers.get(topic);
    if (buffer && buffer.items.length > limit) {
      buffer.maxSize = limit;
      buffer.items = buffer.items.slice(-limit);
    }
  }

  /**
   * Get retention limit for a topic
   */
  getRetention(topic: string): number {
    return this.retentionConfig.get(topic) ?? DEFAULT_RETENTION;
  }

  /**
   * Clear all messages for a topic
   */
  clearTopic(topic: string): void {
    this.subjects.delete(topic);
    this.buffers.delete(topic);
    this.persistenceService.remove(topic);
  }

  /**
   * Clear all monitored data
   */
  clearAll(): void {
    this.subjects.clear();
    this.buffers.clear();
    this.persistenceService.clearAll();
  }

  /**
   * Get all monitored topics (excludes bypass topics that have no buffer)
   * Bypass topics are not shown in MessageMonitor tab as they have no history
   */
  getTopics(): string[] {
    return Array.from(this.subjects.keys())
      .filter(topic => !SKIP_BUFFER_TOPICS.includes(topic));
  }


  private addToBuffer(topic: string, message: MonitoredMessage): void {
    if (!this.buffers.has(topic)) {
      const retention = this.getRetention(topic);
      this.buffers.set(topic, {
        items: [],
        maxSize: retention,
      });
    }

    const buffer = this.buffers.get(topic)!;
    buffer.items.push(message);

    // Trim buffer to max size (circular buffer behavior)
    if (buffer.items.length > buffer.maxSize) {
      buffer.items = buffer.items.slice(-buffer.maxSize);
    }
  }


  private loadPersistedData(): void {
    try {
      const persistedData = this.persistenceService.loadAll();
      let loadedTopics = 0;
      let trimmedTopics = 0;
      
      for (const [topic, messages] of persistedData.entries()) {
        // Get retention limit for this topic
        const retention = this.getRetention(topic);
        
        // Trim messages that exceed retention before storing
        const trimmedMessages = messages.slice(-retention);
        
        // Track if trimming occurred
        if (messages.length > trimmedMessages.length) {
          trimmedTopics++;
          console.log(`[MessageMonitor] Trimmed ${messages.length - trimmedMessages.length} old messages from topic: ${topic}`);
        }
        
        // Restore buffer with trimmed messages
        this.buffers.set(topic, {
          items: trimmedMessages,
          maxSize: retention,
        });

        // Initialize BehaviorSubject directly with last message (no intermediate null)
        // This ensures subscribers immediately get the last persisted value
        if (trimmedMessages.length > 0) {
          const lastMessage = trimmedMessages[trimmedMessages.length - 1];
          
          // Initialize BehaviorSubject with lastMessage directly to avoid transient nulls
          if (!this.subjects.has(topic)) {
            this.subjects.set(topic, new BehaviorSubject<MonitoredMessage | null>(lastMessage));
          } else {
            // Defensive: if subject already exists (shouldn't happen during init, but
            // could occur if service is reinitialized without proper cleanup), ensure
            // its current value is in sync with the last persisted message
            const subj = this.subjects.get(topic)!;
            const cur = subj.value;
            if (!cur || cur.timestamp !== lastMessage.timestamp) {
              subj.next(lastMessage);
            }
          }
          loadedTopics++;
        }
      }

      console.log(`[MessageMonitor] Loaded persisted data for ${loadedTopics} topics${trimmedTopics > 0 ? ` (trimmed ${trimmedTopics} topics)` : ''}`);
    } catch (error) {
      console.error('[MessageMonitor] Failed to load persisted data:', error);
    }
  }

  private setupBroadcastChannel(): void {
    try {
      // BroadcastChannel for multi-tab sync
      this.broadcastChannel = new BroadcastChannel('OSF-message-monitor');
      
      this.broadcastChannel.onmessage = (event) => {
        const message = event.data as MonitoredMessage;
        
        // Update local state with message from other tab
        if (!this.subjects.has(message.topic)) {
          this.subjects.set(message.topic, new BehaviorSubject<MonitoredMessage | null>(null));
        }
        this.subjects.get(message.topic)!.next(message);
        this.addToBuffer(message.topic, message);
      };
    } catch (error) {
      console.warn('[MessageMonitor] BroadcastChannel not available:', error);
    }
  }

  private broadcastMessage(message: MonitoredMessage): void {
    try {
      this.broadcastChannel?.postMessage(message);
    } catch (error) {
      console.error('[MessageMonitor] Failed to broadcast message:', error);
    }
  }

  ngOnDestroy(): void {
    this.broadcastChannel?.close();
  }
}
