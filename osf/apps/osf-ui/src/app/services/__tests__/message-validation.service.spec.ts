import { TestBed } from '@angular/core/testing';
import { MessageValidationService } from '../message-validation.service';

describe('MessageValidationService', () => {
  let service: MessageValidationService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [MessageValidationService],
    });
    service = TestBed.inject(MessageValidationService);
  });

  describe('validate', () => {
    it('should accept messages without schema (fallback behavior)', () => {
      const result = service.validate('unknown/topic', { data: 'test' });
      expect(result.valid).toBe(true);
      expect(result.errors).toBeUndefined();
    });

    it('should handle null payload gracefully', () => {
      const result = service.validate('test/topic', null);
      expect(result.valid).toBe(true);
    });

    it('should handle undefined payload gracefully', () => {
      const result = service.validate('test/topic', undefined);
      expect(result.valid).toBe(true);
    });

    it('should handle empty string payload', () => {
      const result = service.validate('test/topic', '');
      expect(result.valid).toBe(true);
    });

    it('should handle number payload', () => {
      const result = service.validate('test/topic', 42);
      expect(result.valid).toBe(true);
    });

    it('should handle boolean payload', () => {
      const result = service.validate('test/topic', true);
      expect(result.valid).toBe(true);
    });

    it('should handle array payload', () => {
      const result = service.validate('test/topic', [1, 2, 3]);
      expect(result.valid).toBe(true);
    });

    it('should handle complex nested payload', () => {
      const payload = {
        nested: {
          deep: {
            value: 'test',
          },
        },
      };
      const result = service.validate('test/topic', payload);
      expect(result.valid).toBe(true);
    });
  });

  describe('registerSchema and validate', () => {
    it('should register a valid schema', () => {
      const schema = {
        type: 'object',
        properties: {
          name: { type: 'string' },
          age: { type: 'number' },
        },
        required: ['name'],
      };

      expect(() => {
        service.registerSchema('test/topic', schema);
      }).not.toThrow();

      // Verify schema is registered
      expect(service.hasSchema('test/topic')).toBe(true);
    });

    it('should validate message against registered schema', () => {
      const schema = {
        type: 'object',
        properties: {
          id: { type: 'string' },
          value: { type: 'number' },
        },
        required: ['id'],
      };

      service.registerSchema('test/valid', schema);

      // Valid message
      const validResult = service.validate('test/valid', { id: 'test', value: 42 });
      expect(validResult.valid).toBe(true);
      expect(validResult.errors).toBeUndefined();
    });

    it('should reject invalid message with errors', () => {
      const schema = {
        type: 'object',
        properties: {
          id: { type: 'string' },
          count: { type: 'number' },
        },
        required: ['id', 'count'],
      };

      service.registerSchema('test/invalid', schema);

      // Missing required field
      const result1 = service.validate('test/invalid', { id: 'test' });
      expect(result1.valid).toBe(false);
      expect(result1.errors).toBeDefined();
      expect(result1.errors!.length).toBeGreaterThan(0);

      // Wrong type
      const result2 = service.validate('test/invalid', { id: 123, count: 'not-a-number' });
      expect(result2.valid).toBe(false);
      expect(result2.errors).toBeDefined();
    });

    it('should handle complex nested schemas', () => {
      const schema = {
        type: 'object',
        properties: {
          user: {
            type: 'object',
            properties: {
              name: { type: 'string' },
              age: { type: 'number' },
            },
            required: ['name'],
          },
        },
        required: ['user'],
      };

      service.registerSchema('test/nested', schema);

      // Valid nested
      const validResult = service.validate('test/nested', {
        user: { name: 'John', age: 30 },
      });
      expect(validResult.valid).toBe(true);

      // Invalid nested - wrong type for age
      const invalidResult = service.validate('test/nested', {
        user: { name: 'John', age: 'thirty' }, // age should be number
      });
      expect(invalidResult.valid).toBe(false);
      expect(invalidResult.errors).toBeDefined();
      expect(invalidResult.errors!.length).toBeGreaterThan(0);
    });

    it('should handle invalid schema gracefully', () => {
      const invalidSchema = {
        type: 'invalid-type',
        properties: 'not-an-object',
      };

      // Should not throw (error is caught and logged internally)
      // The service catches errors and logs them, so the method doesn't throw
      expect(() => {
        service.registerSchema('test/topic', invalidSchema);
      }).not.toThrow();
      
      // Schema should not be registered
      expect(service.hasSchema('test/topic')).toBe(false);
    });

    it('should handle null schema gracefully', () => {
      // Should not throw (error is caught and logged internally)
      expect(() => {
        service.registerSchema('test/topic', null as unknown as object);
      }).not.toThrow();
      
      // Schema should not be registered
      expect(service.hasSchema('test/topic')).toBe(false);
    });

    it('should handle empty schema object', () => {
      expect(() => {
        service.registerSchema('test/topic', {});
      }).not.toThrow();
    });

    it('should overwrite existing schema', () => {
      const schema1 = {
        type: 'object',
        properties: { value: { type: 'string' } },
      };
      const schema2 = {
        type: 'object',
        properties: { value: { type: 'number' } },
      };

      service.registerSchema('test/topic', schema1);
      service.registerSchema('test/topic', schema2);

      // Should have the second schema
      expect(service.hasSchema('test/topic')).toBe(true);
    });
  });

  describe('hasSchema', () => {
    it('should return false for unknown topic', () => {
      expect(service.hasSchema('unknown/topic')).toBe(false);
    });

    it('should return true after registering schema', () => {
      const schema = {
        type: 'object',
        properties: { value: { type: 'string' } },
      };

      service.registerSchema('test/topic', schema);
      expect(service.hasSchema('test/topic')).toBe(true);
    });

    it('should handle topics with special characters', () => {
      const topic = '/j1/txt/1/i/cam';
      expect(service.hasSchema(topic)).toBe(false);

      const schema = {
        type: 'object',
        properties: { image: { type: 'string' } },
      };

      service.registerSchema(topic, schema);
      expect(service.hasSchema(topic)).toBe(true);
    });
  });

  describe('Edge Cases', () => {
    it('should handle very long topic names', () => {
      const longTopic = 'a'.repeat(1000);
      const result = service.validate(longTopic, { data: 'test' });
      expect(result.valid).toBe(true);
    });

    it('should handle topic with special characters', () => {
      const topic = '/j1/txt/1/i/bme680';
      const result = service.validate(topic, { temperature: 25 });
      expect(result.valid).toBe(true);
    });

    it('should handle topic with query parameters', () => {
      const topic = 'test/topic?param=value';
      const result = service.validate(topic, { data: 'test' });
      expect(result.valid).toBe(true);
    });

    it('should handle very large payload', () => {
      const largePayload = {
        data: 'x'.repeat(10000),
        array: Array(1000).fill(0),
      };
      const result = service.validate('test/topic', largePayload);
      expect(result.valid).toBe(true);
    });
  });
});

