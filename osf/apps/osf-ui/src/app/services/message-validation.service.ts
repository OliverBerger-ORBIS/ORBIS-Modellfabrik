import { Injectable } from '@angular/core';
import Ajv from 'ajv';
import type { ValidateFunction } from 'ajv';

export interface ValidationResult {
  valid: boolean;
  errors?: string[];
}

/**
 * Service responsible for validating MQTT messages against JSON schemas
 * Separated from MessageMonitorService for better testability and single responsibility
 */
@Injectable({ providedIn: 'root' })
export class MessageValidationService {
  private readonly schemas = new Map<string, ValidateFunction>();
  private readonly ajv: Ajv;

  constructor() {
    this.ajv = new Ajv({ allErrors: true });
    this.loadSchemas();
  }

  /**
   * Validate a message payload against its schema
   * Returns valid: true if no schema is found (fallback behavior)
   */
  validate(topic: string, payload: unknown): ValidationResult {
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

  /**
   * Register a schema for a topic
   */
  registerSchema(topic: string, schema: object): void {
    const schemaKey = this.topicToSchemaKey(topic);
    try {
      const validator = this.ajv.compile(schema);
      this.schemas.set(schemaKey, validator);
    } catch (error) {
      console.error(`[MessageValidation] Failed to register schema for ${topic}:`, error);
    }
  }

  /**
   * Check if a schema exists for a topic
   */
  hasSchema(topic: string): boolean {
    const schemaKey = this.topicToSchemaKey(topic);
    return this.schemas.has(schemaKey);
  }

  private topicToSchemaKey(topic: string): string {
    // Convert MQTT topic to schema key
    // Examples:
    // /j1/txt/1/i/cam -> j1_txt_1_i_cam
    // ccu/order/active -> ccu_order_active
    return topic.replace(/^\//, '').replace(/\//g, '_');
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
    // - Registering schemas with this.registerSchema(topic, schema)
    
    console.log('[MessageValidation] Schema validation in fallback mode - all messages accepted');
  }
}

