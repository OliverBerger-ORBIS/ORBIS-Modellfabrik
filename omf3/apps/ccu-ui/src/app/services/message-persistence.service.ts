import { Injectable } from '@angular/core';
import type { MonitoredMessage } from './message-monitor.service';

const STORAGE_KEY_PREFIX = 'omf3.message-monitor';
const STORAGE_SIZE_LIMIT = 5 * 1024 * 1024; // 5MB

// Topics that should NOT be persisted
const NO_PERSIST_TOPICS = ['/j1/txt/1/i/cam'];

/**
 * Service responsible for persisting and loading messages from localStorage
 * Separated from MessageMonitorService for better testability and single responsibility
 */
@Injectable({ providedIn: 'root' })
export class MessagePersistenceService {
  /**
   * Persist messages for a topic to localStorage
   * Returns true if successful, false if skipped or failed
   */
  persist(topic: string, messages: MonitoredMessage[]): boolean {
    // Don't persist camera data or other excluded topics
    if (NO_PERSIST_TOPICS.includes(topic)) {
      return false;
    }

    try {
      const key = `${STORAGE_KEY_PREFIX}.${topic}`;
      const data = JSON.stringify(messages);
      
      // Check storage size limit
      if (this.getStorageSize() + data.length > STORAGE_SIZE_LIMIT) {
        console.warn('[MessagePersistence] Storage size limit reached, skipping persistence for', topic);
        return false;
      }

      localStorage.setItem(key, data);
      return true;
    } catch (error) {
      console.error('[MessagePersistence] Failed to persist messages:', error);
      return false;
    }
  }

  /**
   * Load persisted messages for a topic
   * Returns empty array if no persisted data exists
   */
  load(topic: string): MonitoredMessage[] {
    try {
      const key = `${STORAGE_KEY_PREFIX}.${topic}`;
      const data = localStorage.getItem(key);
      
      if (!data) {
        return [];
      }

      const messages = JSON.parse(data) as MonitoredMessage[];
      
      // Defensive: ensure it's an array
      if (!Array.isArray(messages)) {
        console.warn(`[MessagePersistence] Persisted data for ${topic} is not an array, removing.`);
        this.remove(topic);
        return [];
      }

      return messages;
    } catch (error) {
      console.warn(`[MessagePersistence] Failed to load persisted data for ${topic}, removing corrupt entry.`, error);
      this.remove(topic);
      return [];
    }
  }

  /**
   * Load all persisted topics
   * Returns a map of topic -> messages
   */
  loadAll(): Map<string, MonitoredMessage[]> {
    const result = new Map<string, MonitoredMessage[]>();
    
    try {
      const prefix = STORAGE_KEY_PREFIX + '.';
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(prefix)) {
          const topic = key.substring(prefix.length);
          const messages = this.load(topic);
          if (messages.length > 0) {
            result.set(topic, messages);
          }
        }
      }
    } catch (error) {
      console.error('[MessagePersistence] Failed to load all persisted data:', error);
    }

    return result;
  }

  /**
   * Remove persisted data for a topic
   */
  remove(topic: string): void {
    try {
      const key = `${STORAGE_KEY_PREFIX}.${topic}`;
      localStorage.removeItem(key);
    } catch (error) {
      console.error('[MessagePersistence] Failed to remove persisted topic:', error);
    }
  }

  /**
   * Clear all persisted data
   */
  clearAll(): void {
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
      console.error('[MessagePersistence] Failed to clear persisted data:', error);
    }
  }

  /**
   * Get total storage size used by persisted messages
   */
  getStorageSize(): number {
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

  /**
   * Check if a topic should be persisted
   */
  shouldPersist(topic: string): boolean {
    return !NO_PERSIST_TOPICS.includes(topic);
  }
}

