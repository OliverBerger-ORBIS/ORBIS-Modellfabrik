import { Injectable } from '@angular/core';
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
export class MessageMonitorService {
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
    if (!this.subjects.has(topic)) {
      this.subjects.set(topic, new BehaviorSubject<MonitoredMessage | null>(null));
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

    // Update BehaviorSubject for immediate access
    if (!this.subjects.has(topic)) {
      this.subjects.set(topic, new BehaviorSubject<MonitoredMessage | null>(null));
    }
    this.subjects.get(topic)!.next(message);

    // Add to circular buffer with retention limit
    this.addToBuffer(topic, message);

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
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(prefix)) {
          const topic = key.substring(prefix.length);
          const data = localStorage.getItem(key);
          
          if (data) {
            const messages = JSON.parse(data) as MonitoredMessage[];
            
            // Restore buffer
            const retention = this.getRetention(topic);
            this.buffers.set(topic, {
              items: messages.slice(-retention), // Only keep up to retention limit
              maxSize: retention,
            });

            // Restore last message
            if (messages.length > 0) {
              const lastMessage = messages[messages.length - 1];
              if (!this.subjects.has(topic)) {
                this.subjects.set(topic, new BehaviorSubject<MonitoredMessage | null>(null));
              }
              this.subjects.get(topic)!.next(lastMessage);
            }
          }
        }
      }

      console.log('[MessageMonitor] Loaded persisted data for', this.buffers.size, 'topics');
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
