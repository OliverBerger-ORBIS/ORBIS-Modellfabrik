import { TestBed } from '@angular/core/testing';
import { MessageMonitorService, MonitoredMessage } from '../message-monitor.service';
import { firstValueFrom } from 'rxjs';

describe('MessageMonitorService', () => {
  let service: MessageMonitorService;

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    
    TestBed.configureTestingModule({
      providers: [MessageMonitorService],
    });
    service = TestBed.inject(MessageMonitorService);
  });

  afterEach(() => {
    // Clean up
    service.clearAll();
    localStorage.clear();
  });

  describe('getLastMessage', () => {
    it('should return null for unknown topic', async () => {
      const lastMessage$ = service.getLastMessage('unknown/topic');
      const value = await firstValueFrom(lastMessage$);
      expect(value).toBeNull();
    });

    it('should return last message immediately for new subscribers', async () => {
      const topic = 'test/topic';
      const payload = { data: 'test' };
      
      service.addMessage(topic, payload);
      
      const lastMessage$ = service.getLastMessage(topic);
      const value = await firstValueFrom(lastMessage$);
      
      expect(value).not.toBeNull();
      expect(value?.topic).toBe(topic);
      expect(value?.payload).toEqual(payload);
    });

    it('should update when new message arrives', (done) => {
      const topic = 'test/topic';
      const payload1 = { data: 'first' };
      const payload2 = { data: 'second' };
      
      const lastMessage$ = service.getLastMessage(topic);
      const values: (MonitoredMessage | null)[] = [];
      
      lastMessage$.subscribe((value) => {
        values.push(value);
        
        if (values.length === 3) {
          expect(values[0]).toBeNull(); // Initial value
          expect(values[1]?.payload).toEqual(payload1);
          expect(values[2]?.payload).toEqual(payload2);
          done();
        }
      });
      
      service.addMessage(topic, payload1);
      service.addMessage(topic, payload2);
    });
  });

  describe('getHistory', () => {
    it('should return empty array for unknown topic', () => {
      const history = service.getHistory('unknown/topic');
      expect(history).toEqual([]);
    });

    it('should store message history', () => {
      const topic = 'test/topic';
      
      service.addMessage(topic, { id: 1 });
      service.addMessage(topic, { id: 2 });
      service.addMessage(topic, { id: 3 });
      
      const history = service.getHistory(topic);
      expect(history.length).toBe(3);
      expect(history[0].payload).toEqual({ id: 1 });
      expect(history[1].payload).toEqual({ id: 2 });
      expect(history[2].payload).toEqual({ id: 3 });
    });

    it('should respect default retention limit', () => {
      const topic = 'test/topic';
      const defaultRetention = 50;
      
      // Add more messages than default retention
      for (let i = 0; i < defaultRetention + 10; i++) {
        service.addMessage(topic, { id: i });
      }
      
      const history = service.getHistory(topic);
      expect(history.length).toBe(defaultRetention);
      
      // Should keep the most recent messages
      expect(history[0].payload).toEqual({ id: 10 });
      expect(history[history.length - 1].payload).toEqual({ id: defaultRetention + 9 });
    });
  });

  describe('setRetention', () => {
    it('should set custom retention for topic', () => {
      const topic = 'test/topic';
      service.setRetention(topic, 10);
      
      expect(service.getRetention(topic)).toBe(10);
    });

    it('should trim existing buffer when retention is reduced', () => {
      const topic = 'test/topic';
      
      // Add 20 messages
      for (let i = 0; i < 20; i++) {
        service.addMessage(topic, { id: i });
      }
      
      expect(service.getHistory(topic).length).toBe(20);
      
      // Reduce retention to 10
      service.setRetention(topic, 10);
      
      const history = service.getHistory(topic);
      expect(history.length).toBe(10);
      
      // Should keep the most recent 10
      expect(history[0].payload).toEqual({ id: 10 });
      expect(history[9].payload).toEqual({ id: 19 });
    });

    it('should use special retention for camera topic', () => {
      const topic = '/j1/txt/1/i/cam';
      expect(service.getRetention(topic)).toBe(10);
    });

    it('should use special retention for sensor topics', () => {
      expect(service.getRetention('/j1/txt/1/i/bme680')).toBe(100);
      expect(service.getRetention('/j1/txt/1/i/ldr')).toBe(100);
    });
  });

  describe('validation', () => {
    it('should accept messages without schema (fallback)', () => {
      const topic = 'unknown/topic';
      service.addMessage(topic, { data: 'test' });
      
      const history = service.getHistory(topic);
      expect(history.length).toBe(1);
      expect(history[0].valid).toBe(true);
    });
  });

  describe('persistence', () => {
    it('should persist messages to localStorage', () => {
      const topic = 'test/topic';
      service.addMessage(topic, { data: 'test' });
      
      // Check if data is in localStorage
      const key = 'omf3.message-monitor.test/topic';
      const stored = localStorage.getItem(key);
      
      expect(stored).not.toBeNull();
      
      const parsed = JSON.parse(stored!);
      expect(parsed.length).toBe(1);
      expect(parsed[0].payload).toEqual({ data: 'test' });
    });

    it('should load persisted data on init', () => {
      const topic = 'test/topic';
      const payload = { data: 'persisted' };
      
      // Create first service instance and add message
      service.addMessage(topic, payload);
      
      // Create new service instance (simulates app restart)
      const newService = new MessageMonitorService();
      
      const history = newService.getHistory(topic);
      expect(history.length).toBeGreaterThan(0);
      expect(history[history.length - 1].payload).toEqual(payload);
      
      newService.clearAll();
    });

    it('should not persist camera data', () => {
      const topic = '/j1/txt/1/i/cam';
      service.addMessage(topic, { data: 'base64image' });
      
      const key = 'omf3.message-monitor./j1/txt/1/i/cam';
      const stored = localStorage.getItem(key);
      
      expect(stored).toBeNull();
    });

    it('should initialize BehaviorSubject with last persisted message (no intermediate null)', async () => {
      const topic = 'test/restore';
      const payload = { data: 'persisted-value', id: 123 };
      
      // Setup: persist data via first service instance
      service.addMessage(topic, payload);
      
      // Simulate app restart: create new service instance
      const newService = new MessageMonitorService();
      
      // Get observable IMMEDIATELY after construction (before any messages arrive)
      const lastMessage$ = newService.getLastMessage(topic);
      
      // First emission should be the persisted value, NOT null
      const firstValue = await firstValueFrom(lastMessage$);
      expect(firstValue).not.toBeNull();
      expect(firstValue?.payload).toEqual(payload);
      expect(firstValue?.topic).toBe(topic);
      
      newService.clearAll();
    });

    it('should trim messages exceeding retention when loading persisted data', () => {
      const topic = 'test/retention-trim';
      
      // Add 60 messages (exceeds default retention of 50)
      for (let i = 0; i < 60; i++) {
        service.addMessage(topic, { id: i });
      }
      
      // Verify all 60 are in current service (trimmed to 50 due to circular buffer)
      expect(service.getHistory(topic).length).toBe(50);
      
      // Create new service instance (simulates app restart)
      const newService = new MessageMonitorService();
      
      // Should only load the last 50 messages
      const history = newService.getHistory(topic);
      expect(history.length).toBe(50);
      expect(history[0].payload).toEqual({ id: 10 });
      expect(history[49].payload).toEqual({ id: 59 });
      
      newService.clearAll();
    });
  });

  describe('clearTopic', () => {
    it('should clear all data for topic', () => {
      const topic = 'test/topic';
      service.addMessage(topic, { data: 'test' });
      
      expect(service.getHistory(topic).length).toBe(1);
      
      service.clearTopic(topic);
      
      expect(service.getHistory(topic).length).toBe(0);
      
      // Should also clear from localStorage
      const key = 'omf3.message-monitor.test/topic';
      expect(localStorage.getItem(key)).toBeNull();
    });
  });

  describe('getTopics', () => {
    it('should return list of monitored topics', () => {
      service.addMessage('topic/a', { data: 'a' });
      service.addMessage('topic/b', { data: 'b' });
      service.addMessage('topic/c', { data: 'c' });
      
      const topics = service.getTopics();
      expect(topics.length).toBe(3);
      expect(topics).toContain('topic/a');
      expect(topics).toContain('topic/b');
      expect(topics).toContain('topic/c');
    });
  });
});
