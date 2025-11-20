import { Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import Ajv from 'ajv';
import type { ValidateFunction } from 'ajv';

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
const STORAGE_KEY_PREFIX = 'omf3.message-monitor';
const STORAGE_SIZE_LIMIT = 5 * 1024 * 1024; // 5MB

// Topics that should NOT be persisted
const NO_PERSIST_TOPICS = ['/j1/txt/1/i/cam'];

// Default retention configuration for specific topics
const RETENTION_CONFIG: Record<string, number> = {
  '/j1/txt/1/i/cam': 10,      // Camera frames: low retention
  '/j1/txt/1/i/bme680': 100,  // BME680 sensor: high retention
  '/j1/txt/1/i/ldr': 100,     // LDR sensor: high retention
};

@Injectable({ providedIn: 'root' })
export class MessageMonitorService implements OnDestroy {
  private readonly subjects = new Map<string, BehaviorSubject<MonitoredMessage | null>>();
  private readonly buffers = new Map<string, CircularBuffer<MonitoredMessage>>();
  private readonly retentionConfig = new Map<string, number>(Object.entries(RETENTION_CONFIG));
  private readonly schemas = new Map<string, ValidateFunction>();
  private readonly ajv: Ajv;
  private broadcastChannel?: BroadcastChannel;

  constructor() {
    this.ajv = new Ajv({ allErrors: true });
    this.loadSchemas();
    this.loadPersistedData();
    this.setupBroadcastChannel();
  }

  /**
   * Get the last message for a topic as an Observable
   * Returns null if no message has been received yet
   */
  getLastMessage<T = unknown>(topic: string): Observable<MonitoredMessage<T> | null> {
    // Always check buffer for current value FIRST, even if subject already exists
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
    const validation = this.validateMessage(topic, payload);
    
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
    this.persistMessage(topic, message);

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
    return this.retentionConfig.get(topic) || DEFAULT_RETENTION;
  }

  /**
   * Clear all messages for a topic
   */
  clearTopic(topic: string): void {
    this.subjects.delete(topic);
    this.buffers.delete(topic);
    this.removePersistedTopic(topic);
  }

  /**
   * Clear all monitored data
   */
  clearAll(): void {
    this.subjects.clear();
    this.buffers.clear();
    this.clearAllPersisted();
  }

  /**
   * Get all monitored topics
   */
  getTopics(): string[] {
    return Array.from(this.subjects.keys());
  }

  private validateMessage(topic: string, payload: unknown): { valid: boolean; errors?: string[] } {
    const schemaKey = this.topicToSchemaKey(topic);
    const validator = this.schemas.get(schemaKey);

    if (!validator) {
      // No schema found - accept message (fallback behavior)
      return { valid: true };
    }

    const valid = validator(payload);
    if (valid) {
      return { valid: true };
    }

    const errors = validator.errors?.map(err => {
      return `${err.instancePath} ${err.message}`;
    }) || [];

    return { valid: false, errors };
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

  private loadSchemas(): void {
    // Load JSON schemas from registry
    // TODO: Implement schema loading from omf2/registry/schemas/
    // 
    // Implementation options:
    // 1. Bundle schemas as assets in project.json and fetch via HttpClient
    // 2. Import schemas as JSON modules at build time
    // 3. Fetch schemas from a backend API endpoint
    // 
    // For now, the service operates in fallback mode (accepts all messages).
    // Schema validation can be added by:
    // - Adding schemas to project.json assets configuration
    // - Using HttpClient to load schemas on service init
    // - Registering schemas with this.ajv.addSchema(schema)
    
    console.log('[MessageMonitor] Schema validation in fallback mode - all messages accepted');
  }

  private topicToSchemaKey(topic: string): string {
    // Convert MQTT topic to schema key
    // Examples:
    // /j1/txt/1/i/cam -> j1_txt_1_i_cam
    // ccu/order/active -> ccu_order_active
    return topic.replace(/^\//, '').replace(/\//g, '_');
  }

  private persistMessage(topic: string, message: MonitoredMessage): void {
    // Don't persist camera data or other excluded topics
    if (NO_PERSIST_TOPICS.includes(topic)) {
      return;
    }

    try {
      const key = `${STORAGE_KEY_PREFIX}.${topic}`;
      const buffer = this.buffers.get(topic);
      
      if (!buffer) {
        return;
      }

      const data = JSON.stringify(buffer.items);
      
      // Check storage size limit
      if (this.getStorageSize() + data.length > STORAGE_SIZE_LIMIT) {
        console.warn('[MessageMonitor] Storage size limit reached, skipping persistence for', topic);
        return;
      }

      localStorage.setItem(key, data);
    } catch (error) {
      console.error('[MessageMonitor] Failed to persist message:', error);
    }
  }

  private loadPersistedData(): void {
    try {
      const prefix = STORAGE_KEY_PREFIX + '.';
      let loadedTopics = 0;
      let trimmedTopics = 0;
      let corruptedTopics = 0;
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(prefix)) {
          const topic = key.substring(prefix.length);
          const data = localStorage.getItem(key);
          
          if (!data) {
            continue;
          }

          try {
            const messages = JSON.parse(data) as MonitoredMessage[];
            
            // Defensive: ensure it's an array
            if (!Array.isArray(messages)) {
              console.warn(`[MessageMonitor] Persisted data for ${topic} is not an array, skipping.`);
              localStorage.removeItem(key);
              corruptedTopics++;
              continue;
            }

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
          } catch (err) {
            console.warn(`[MessageMonitor] Failed parsing persisted data for ${topic}, removing corrupt entry.`, err);
            // If parse fails, remove the corrupt persisted key to prevent repeated failures
            localStorage.removeItem(key);
            corruptedTopics++;
          }
        }
      }

      console.log(`[MessageMonitor] Loaded persisted data for ${loadedTopics} topics${trimmedTopics > 0 ? ` (trimmed ${trimmedTopics} topics)` : ''}${corruptedTopics > 0 ? ` (removed ${corruptedTopics} corrupted entries)` : ''}`);
    } catch (error) {
      console.error('[MessageMonitor] Failed to load persisted data:', error);
    }
  }

  private removePersistedTopic(topic: string): void {
    try {
      const key = `${STORAGE_KEY_PREFIX}.${topic}`;
      localStorage.removeItem(key);
    } catch (error) {
      console.error('[MessageMonitor] Failed to remove persisted topic:', error);
    }
  }

  private clearAllPersisted(): void {
    try {
      const prefix = STORAGE_KEY_PREFIX + '.';
      const keysToRemove: string[] = [];
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(prefix)) {
          keysToRemove.push(key);
        }
      }

      keysToRemove.forEach(key => localStorage.removeItem(key));
    } catch (error) {
      console.error('[MessageMonitor] Failed to clear persisted data:', error);
    }
  }

  private getStorageSize(): number {
    let total = 0;
    const prefix = STORAGE_KEY_PREFIX + '.';
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(prefix)) {
        const value = localStorage.getItem(key);
        if (value) {
          total += value.length;
        }
      }
    }

    return total;
  }

  private setupBroadcastChannel(): void {
    try {
      // BroadcastChannel for multi-tab sync
      this.broadcastChannel = new BroadcastChannel('omf3-message-monitor');
      
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
