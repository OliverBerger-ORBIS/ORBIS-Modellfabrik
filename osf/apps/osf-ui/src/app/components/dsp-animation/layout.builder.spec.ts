import { DiagramConfigBuilder } from './layout.builder';
import type { StepConfig, ConnectionConfig, ContainerConfig } from './types';

describe('DiagramConfigBuilder', () => {
  describe('Constructor', () => {
    it('should initialize with default containers and connections', () => {
      const builder = new DiagramConfigBuilder();
      const config = builder.build();

      expect(config.containers).toBeDefined();
      expect(config.connections).toBeDefined();
      expect(config.containers.length).toBeGreaterThan(0);
      expect(config.connections.length).toBeGreaterThan(0);
    });

    it('should initialize with empty steps', () => {
      const builder = new DiagramConfigBuilder();
      const config = builder.build();

      expect(config.steps).toEqual([]);
    });

    it('should have correct viewBox dimensions', () => {
      const builder = new DiagramConfigBuilder();
      const config = builder.build();

      expect(config.viewBox).toBeDefined();
      expect(config.viewBox.width).toBe(1200);
      expect(config.viewBox.height).toBeGreaterThan(0);
    });
  });

  describe('withFunctionalSteps', () => {
    it('should add functional steps to the builder', () => {
      const steps: StepConfig[] = [
        {
          id: 'step-1',
          label: 'Test Step',
          visibleContainerIds: ['layer-sf'],
          highlightedContainerIds: [],
          visibleConnectionIds: [],
          highlightedConnectionIds: [],
        },
      ];

      const builder = new DiagramConfigBuilder();
      const config = builder.withFunctionalSteps(steps).build();

      expect(config.steps).toEqual(steps);
      expect(config.steps.length).toBe(1);
    });

    it('should support method chaining', () => {
      const steps: StepConfig[] = [];
      const builder = new DiagramConfigBuilder();
      const result = builder.withFunctionalSteps(steps);

      expect(result).toBe(builder);
    });
  });

  describe('withComponentView', () => {
    it('should add component view steps and connections', () => {
      const steps: StepConfig[] = [
        {
          id: 'comp-step-1',
          label: 'Component Test',
          visibleContainerIds: [],
          highlightedContainerIds: [],
          visibleConnectionIds: [],
          highlightedConnectionIds: [],
        },
      ];
      const additionalConnections: ConnectionConfig[] = [
        {
          id: 'test-conn',
          fromId: 'edge-comp-router',
          toId: 'edge-comp-disc',
          state: 'hidden',
        },
      ];

      const builder = new DiagramConfigBuilder();
      const config = builder.withComponentView(steps, additionalConnections).build();

      expect(config.steps).toEqual(steps);
      expect(config.connections.length).toBeGreaterThan(0);
      // Check that additional connection was added
      const hasTestConn = config.connections.some((c) => c.id === 'test-conn');
      expect(hasTestConn).toBe(true);
    });

    it('should support method chaining', () => {
      const builder = new DiagramConfigBuilder();
      const result = builder.withComponentView([], []);

      expect(result).toBe(builder);
    });
  });

  describe('withDeploymentView', () => {
    it('should add deployment view steps and pipeline containers', () => {
      const steps: StepConfig[] = [
        {
          id: 'deploy-step-1',
          label: 'Deployment Test',
          visibleContainerIds: [],
          highlightedContainerIds: [],
          visibleConnectionIds: [],
          highlightedConnectionIds: [],
        },
      ];
      const pipelineContainers: ContainerConfig[] = [
        {
          id: 'pipeline-1',
          label: 'Integration',
          x: 100,
          y: 100,
          width: 180,
          height: 60,
          type: 'pipeline',
          state: 'hidden',
        },
      ];

      const builder = new DiagramConfigBuilder();
      const config = builder.withDeploymentView(steps, pipelineContainers).build();

      expect(config.steps).toEqual(steps);
      expect(config.containers.length).toBeGreaterThan(0);
      // Check that pipeline container was added
      const hasPipeline = config.containers.some((c) => c.id === 'pipeline-1');
      expect(hasPipeline).toBe(true);
    });

    it('should support method chaining', () => {
      const builder = new DiagramConfigBuilder();
      const result = builder.withDeploymentView([], []);

      expect(result).toBe(builder);
    });
  });

  describe('addContainers', () => {
    it('should add additional containers', () => {
      const newContainers: ContainerConfig[] = [
        {
          id: 'custom-container',
          label: 'Custom',
          x: 0,
          y: 0,
          width: 100,
          height: 100,
          type: 'box',
          state: 'normal',
        },
      ];

      const builder = new DiagramConfigBuilder();
      const config = builder.addContainers(newContainers).build();

      const hasCustom = config.containers.some((c) => c.id === 'custom-container');
      expect(hasCustom).toBe(true);
    });
  });

  describe('addConnections', () => {
    it('should add additional connections', () => {
      const newConnections: ConnectionConfig[] = [
        {
          id: 'custom-conn',
          fromId: 'a',
          toId: 'b',
          state: 'normal',
        },
      ];

      const builder = new DiagramConfigBuilder();
      const config = builder.addConnections(newConnections).build();

      const hasCustom = config.connections.some((c) => c.id === 'custom-conn');
      expect(hasCustom).toBe(true);
    });
  });

  describe('build', () => {
    it('should return a complete DiagramConfig', () => {
      const builder = new DiagramConfigBuilder();
      const config = builder.build();

      expect(config).toBeDefined();
      expect(config.containers).toBeDefined();
      expect(config.connections).toBeDefined();
      expect(config.steps).toBeDefined();
      expect(config.viewBox).toBeDefined();
    });

    it('should create independent configs on multiple builds', () => {
      const builder1 = new DiagramConfigBuilder();
      const config1 = builder1.build();

      const builder2 = new DiagramConfigBuilder();
      const config2 = builder2.build();

      // Both should have default containers but be independent instances
      expect(config1.containers.length).toBe(config2.containers.length);
      expect(config1.containers).not.toBe(config2.containers);
    });
  });
});
