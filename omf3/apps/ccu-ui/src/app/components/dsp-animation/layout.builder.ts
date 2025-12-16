/**
 * Builder Pattern for DSP Architecture Diagram Configuration.
 * Provides a fluent API to construct diagram configs with common defaults.
 */
import type { ContainerConfig, ConnectionConfig, StepConfig, DiagramConfig } from './types';
import type { CustomerDspConfig } from './configs/types';
import {
  createDefaultContainers,
  createCustomerContainers,
  createDefaultConnections,
  VIEWBOX_WIDTH,
  VIEWBOX_HEIGHT,
} from './layout.shared.config';

/**
 * DiagramConfigBuilder provides a fluent API for constructing DiagramConfig objects.
 * It starts with default containers and connections, then allows customization
 * through method chaining.
 * 
 * @example
 * ```typescript
 * const config = new DiagramConfigBuilder()
 *   .withFunctionalSteps(steps)
 *   .build();
 * ```
 */
export class DiagramConfigBuilder {
  private containers: ContainerConfig[];
  private connections: ConnectionConfig[];
  private steps: StepConfig[];

  constructor(customerConfig?: CustomerDspConfig) {
    // Initialize with customer-specific or default containers
    if (customerConfig) {
      this.containers = createCustomerContainers(customerConfig);
    } else {
      this.containers = createDefaultContainers();
    }
    this.connections = createDefaultConnections();
    this.steps = [];
  }

  /**
   * Adds functional view animation steps.
   * @param steps Array of step configurations
   * @returns This builder instance for chaining
   */
  withFunctionalSteps(steps: StepConfig[]): this {
    this.steps = steps;
    return this;
  }

  /**
   * Configures the builder for component view.
   * Adds component-specific steps and connections.
   * @param steps Array of step configurations for component view
   * @param additionalConnections Additional connections specific to component view
   * @returns This builder instance for chaining
   */
  withComponentView(steps: StepConfig[], additionalConnections: ConnectionConfig[]): this {
    this.steps = steps;
    this.connections.push(...additionalConnections);
    return this;
  }

  /**
   * Configures the builder for deployment view.
   * Adds deployment-specific steps and containers (pipeline steps).
   * @param steps Array of step configurations for deployment view
   * @param pipelineContainers Additional containers for deployment pipeline visualization
   * @returns This builder instance for chaining
   */
  withDeploymentView(steps: StepConfig[], pipelineContainers: ContainerConfig[]): this {
    this.steps = steps;
    this.containers.push(...pipelineContainers);
    return this;
  }

  /**
   * Adds additional containers to the diagram.
   * @param containers Array of container configurations to add
   * @returns This builder instance for chaining
   */
  addContainers(containers: ContainerConfig[]): this {
    this.containers.push(...containers);
    return this;
  }

  /**
   * Adds additional connections to the diagram.
   * @param connections Array of connection configurations to add
   * @returns This builder instance for chaining
   */
  addConnections(connections: ConnectionConfig[]): this {
    this.connections.push(...connections);
    return this;
  }

  /**
   * Builds and returns the final DiagramConfig.
   * @returns Complete diagram configuration ready for rendering
   */
  build(): DiagramConfig {
    return {
      containers: this.containers,
      connections: this.connections,
      steps: this.steps,
      viewBox: {
        width: VIEWBOX_WIDTH,
        height: VIEWBOX_HEIGHT,
      },
    };
  }
}
