import { TestBed } from '@angular/core/testing';
import { MessagePersistenceService } from '../message-persistence.service';
import type { MonitoredMessage } from '../message-monitor.service';

describe('MessagePersistenceService', () => {
  let service: MessagePersistenceService;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [MessagePersistenceService],
    });
    service = TestBed.inject(MessagePersistenceService);
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('persist', () => {
    it('should persist messages to localStorage', () => {
      const topic = 'test/topic';
      const messages: MonitoredMessage[] = [
        {
          topic,
          payload: { data: 'test' },
          timestamp: '2024-01-01T00:00:00Z',
          valid: true,
        },
      ];

      const result = service.persist(topic, messages);
      expect(result).toBe(true);

      const loaded = service.load(topic);
      expect(loaded.length).toBe(1);
      expect(loaded[0].payload).toEqual({ data: 'test' });
    });

    it('should not persist camera data', () => {
      const topic = '/j1/txt/1/i/cam';
      const messages: MonitoredMessage[] = [
        {
          topic,
          payload: { image: 'base64' },
          timestamp: '2024-01-01T00:00:00Z',
          valid: true,
        },
      ];

      const result = service.persist(topic, messages);
      expect(result).toBe(false);

      const loaded = service.load(topic);
      expect(loaded.length).toBe(0);
    });

    it('should handle empty messages array', () => {
      const topic = 'test/topic';
      const result = service.persist(topic, []);
      expect(result).toBe(true);

      const loaded = service.load(topic);
      expect(loaded.length).toBe(0);
    });

    it('should handle large messages array', () => {
      const topic = 'test/topic';
      const messages: MonitoredMessage[] = Array(100).fill(null).map((_, i) => ({
        topic,
        payload: { id: i },
        timestamp: `2024-01-01T00:00:${i.toString().padStart(2, '0')}Z`,
        valid: true,
      }));

      const result = service.persist(topic, messages);
      expect(result).toBe(true);

      const loaded = service.load(topic);
      expect(loaded.length).toBe(100);
    });

    it('should handle localStorage quota exceeded gracefully', () => {
      // Fill localStorage to near capacity
      const largeData = 'x'.repeat(4 * 1024 * 1024); // 4MB
      try {
        for (let i = 0; i < 10; i++) {
          localStorage.setItem(`test-${i}`, largeData);
        }
      } catch {
        // localStorage might not support that much, continue anyway
      }

      const topic = 'test/topic';
      const messages: MonitoredMessage[] = [
        {
          topic,
          payload: { data: 'test' },
          timestamp: '2024-01-01T00:00:00Z',
          valid: true,
        },
      ];

      // Should handle quota exceeded gracefully
      const result = service.persist(topic, messages);
      // Result might be false if quota exceeded, or true if there's still space
      expect(typeof result).toBe('boolean');
    });

    it('should handle localStorage errors gracefully', () => {
      const topic = 'test/topic';
      const messages: MonitoredMessage[] = [
        {
          topic,
          payload: { data: 'test' },
          timestamp: '2024-01-01T00:00:00Z',
          valid: true,
        },
      ];

      // Spy on localStorage.setItem and make it throw
      const setItemSpy = jest.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
        throw new Error('Storage quota exceeded');
      });

      const result = service.persist(topic, messages);
      // Should return false when localStorage.setItem throws
      expect(result).toBe(false);
      expect(setItemSpy).toHaveBeenCalled();

      // Restore original
      setItemSpy.mockRestore();
    });
  });

  describe('load', () => {
    it('should return empty array for unknown topic', () => {
      const loaded = service.load('unknown/topic');
      expect(loaded).toEqual([]);
    });

    it('should load persisted messages', () => {
      const topic = 'test/topic';
      const messages: MonitoredMessage[] = [
        {
          topic,
          payload: { data: 'test1' },
          timestamp: '2024-01-01T00:00:00Z',
          valid: true,
        },
        {
          topic,
          payload: { data: 'test2' },
          timestamp: '2024-01-01T00:00:01Z',
          valid: true,
        },
      ];

      service.persist(topic, messages);
      const loaded = service.load(topic);

      expect(loaded.length).toBe(2);
      expect(loaded[0].payload).toEqual({ data: 'test1' });
      expect(loaded[1].payload).toEqual({ data: 'test2' });
    });

    it('should handle corrupted data gracefully', () => {
      const topic = 'test/corrupted';
      const key = 'omf3.message-monitor.test/corrupted';
      localStorage.setItem(key, '{"not": "an array"}');

      const loaded = service.load(topic);
      expect(loaded).toEqual([]);

      // Corrupted entry should be removed
      expect(localStorage.getItem(key)).toBeNull();
    });

    it('should handle invalid JSON gracefully', () => {
      const topic = 'test/invalid-json';
      const key = 'omf3.message-monitor.test/invalid-json';
      localStorage.setItem(key, 'not valid json{{{');

      const loaded = service.load(topic);
      expect(loaded).toEqual([]);

      // Invalid entry should be removed
      expect(localStorage.getItem(key)).toBeNull();
    });

    it('should handle null in localStorage', () => {
      const topic = 'test/null';
      const key = 'omf3.message-monitor.test/null';
      localStorage.setItem(key, 'null');

      const loaded = service.load(topic);
      expect(loaded).toEqual([]);
    });

    it('should handle empty string in localStorage', () => {
      const topic = 'test/empty';
      const key = 'omf3.message-monitor.test/empty';
      localStorage.setItem(key, '');

      const loaded = service.load(topic);
      expect(loaded).toEqual([]);
    });
  });

  describe('loadAll', () => {
    it('should return empty map when no persisted data', () => {
      const all = service.loadAll();
      expect(all.size).toBe(0);
    });

    it('should load all persisted topics', () => {
      const topic1 = 'test/topic1';
      const topic2 = 'test/topic2';

      service.persist(topic1, [
        {
          topic: topic1,
          payload: { data: 'test1' },
          timestamp: '2024-01-01T00:00:00Z',
          valid: true,
        },
      ]);

      service.persist(topic2, [
        {
          topic: topic2,
          payload: { data: 'test2' },
          timestamp: '2024-01-01T00:00:01Z',
          valid: true,
        },
      ]);

      const all = service.loadAll();
      expect(all.size).toBe(2);
      expect(all.has(topic1)).toBe(true);
      expect(all.has(topic2)).toBe(true);
    });

    it('should skip corrupted entries', () => {
      const topic1 = 'test/valid';
      const topic2 = 'test/corrupted';

      service.persist(topic1, [
        {
          topic: topic1,
          payload: { data: 'test' },
          timestamp: '2024-01-01T00:00:00Z',
          valid: true,
        },
      ]);

      // Inject corrupted data
      const key = 'omf3.message-monitor.test/corrupted';
      localStorage.setItem(key, '{"not": "an array"}');

      const all = service.loadAll();
      expect(all.size).toBe(1);
      expect(all.has(topic1)).toBe(true);
      expect(all.has(topic2)).toBe(false);
    });
  });

  describe('remove', () => {
    it('should remove persisted topic', () => {
      const topic = 'test/topic';
      service.persist(topic, [
        {
          topic,
          payload: { data: 'test' },
          timestamp: '2024-01-01T00:00:00Z',
          valid: true,
        },
      ]);

      service.remove(topic);

      const loaded = service.load(topic);
      expect(loaded.length).toBe(0);
    });

    it('should handle removing non-existent topic', () => {
      expect(() => {
        service.remove('unknown/topic');
      }).not.toThrow();
    });
  });

  describe('clearAll', () => {
    it('should clear all persisted data', () => {
      service.persist('test/topic1', [
        {
          topic: 'test/topic1',
          payload: { data: 'test1' },
          timestamp: '2024-01-01T00:00:00Z',
          valid: true,
        },
      ]);

      service.persist('test/topic2', [
        {
          topic: 'test/topic2',
          payload: { data: 'test2' },
          timestamp: '2024-01-01T00:00:01Z',
          valid: true,
        },
      ]);

      service.clearAll();

      const all = service.loadAll();
      expect(all.size).toBe(0);
    });

    it('should handle clearAll when no data exists', () => {
      expect(() => {
        service.clearAll();
      }).not.toThrow();
    });
  });

  describe('getStorageSize', () => {
    it('should return 0 when no persisted data', () => {
      const size = service.getStorageSize();
      expect(size).toBe(0);
    });

    it('should calculate total storage size', () => {
      const topic1 = 'test/topic1';
      const topic2 = 'test/topic2';

      service.persist(topic1, [
        {
          topic: topic1,
          payload: { data: 'test1' },
          timestamp: '2024-01-01T00:00:00Z',
          valid: true,
        },
      ]);

      service.persist(topic2, [
        {
          topic: topic2,
          payload: { data: 'test2' },
          timestamp: '2024-01-01T00:00:01Z',
          valid: true,
        },
      ]);

      const size = service.getStorageSize();
      expect(size).toBeGreaterThan(0);
    });
  });

  describe('shouldPersist', () => {
    it('should return true for regular topics', () => {
      expect(service.shouldPersist('test/topic')).toBe(true);
      expect(service.shouldPersist('/j1/txt/1/i/bme680')).toBe(true);
    });

    it('should return false for camera topic', () => {
      expect(service.shouldPersist('/j1/txt/1/i/cam')).toBe(false);
    });
  });
});

