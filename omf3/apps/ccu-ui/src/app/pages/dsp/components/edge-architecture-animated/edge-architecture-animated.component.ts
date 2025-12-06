import { CommonModule } from '@angular/common';
import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  OnDestroy,
  OnInit,
} from '@angular/core';
import type {
  EdgeContainerConfig,
  EdgeConnectionConfig,
  EdgeStepConfig,
} from './edge-architecture-animated.config';
import {
  createEdgeContainers,
  createEdgeConnections,
  createEdgeSteps,
  EDGE_VIEWBOX_WIDTH,
  EDGE_VIEWBOX_HEIGHT,
} from './edge-architecture-animated.config';

/**
 * DSP Edge Architecture Animated Component
 * 
 * Displays a 4-step animation showing:
 * 1. Edge Components Overview
 * 2. Internal Event Routing
 * 3. Vertical Context (Business ↔ Edge ↔ Shopfloor)
 * 4. Integration into Full Reference Architecture
 */
@Component({
  standalone: true,
  selector: 'app-edge-architecture-animated',
  imports: [CommonModule],
  templateUrl: './edge-architecture-animated.component.html',
  styleUrl: './edge-architecture-animated.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EdgeArchitectureAnimatedComponent implements OnInit, OnDestroy {
  protected readonly sectionTitle = $localize`:@@edgeAnimTitle:DSP Edge Architecture (Animated)`;
  protected readonly sectionSubtitle = $localize`:@@edgeAnimSubtitle:Step-by-step view of Edge components, internal routing, and integration with Business and Shopfloor layers.`;
  
  // Diagram configuration
  protected containers: EdgeContainerConfig[] = [];
  protected connections: EdgeConnectionConfig[] = [];
  protected steps: EdgeStepConfig[] = [];
  
  // Animation state
  protected currentStepIndex = 0;
  protected isAutoPlaying = false;
  private autoPlayInterval: ReturnType<typeof setInterval> | null = null;
  private readonly autoPlayDelay = 3000; // 3 seconds per step
  
  // ViewBox dimensions
  protected readonly viewBoxWidth = EDGE_VIEWBOX_WIDTH;
  protected readonly viewBoxHeight = EDGE_VIEWBOX_HEIGHT;
  protected readonly viewBox = `0 0 ${EDGE_VIEWBOX_WIDTH} ${EDGE_VIEWBOX_HEIGHT}`;
  
  // i18n labels
  protected readonly btnPrev = $localize`:@@edgeAnimPrev:Previous`;
  protected readonly btnNext = $localize`:@@edgeAnimNext:Next`;
  protected readonly btnAutoPlay = $localize`:@@edgeAnimAutoPlay:Auto Play`;
  protected readonly btnStopPlay = $localize`:@@edgeAnimStopPlay:Stop`;
  
  constructor(private cdr: ChangeDetectorRef) {}
  
  ngOnInit(): void {
    this.containers = createEdgeContainers();
    this.connections = createEdgeConnections();
    this.steps = createEdgeSteps();
    
    // Apply first step
    this.applyStep(0);
  }
  
  ngOnDestroy(): void {
    this.stopAutoPlay();
  }
  
  /**
   * Navigate to previous step
   */
  protected prevStep(): void {
    if (this.currentStepIndex > 0) {
      this.currentStepIndex--;
      this.applyStep(this.currentStepIndex);
    }
  }
  
  /**
   * Navigate to next step
   */
  protected nextStep(): void {
    if (this.currentStepIndex < this.steps.length - 1) {
      this.currentStepIndex++;
      this.applyStep(this.currentStepIndex);
    }
  }
  
  /**
   * Navigate to specific step
   */
  protected goToStep(index: number): void {
    if (index >= 0 && index < this.steps.length) {
      this.currentStepIndex = index;
      this.applyStep(this.currentStepIndex);
    }
  }
  
  /**
   * Toggle auto-play
   */
  protected toggleAutoPlay(): void {
    if (this.isAutoPlaying) {
      this.stopAutoPlay();
    } else {
      this.startAutoPlay();
    }
  }
  
  /**
   * Start auto-play animation
   */
  private startAutoPlay(): void {
    this.isAutoPlaying = true;
    this.autoPlayInterval = setInterval(() => {
      if (this.currentStepIndex < this.steps.length - 1) {
        this.nextStep();
      } else {
        // Loop back to start
        this.currentStepIndex = 0;
        this.applyStep(0);
      }
    }, this.autoPlayDelay);
    this.cdr.markForCheck();
  }
  
  /**
   * Stop auto-play animation
   */
  private stopAutoPlay(): void {
    this.isAutoPlaying = false;
    if (this.autoPlayInterval) {
      clearInterval(this.autoPlayInterval);
      this.autoPlayInterval = null;
    }
    this.cdr.markForCheck();
  }
  
  /**
   * Apply a step to the diagram
   */
  private applyStep(stepIndex: number): void {
    const step = this.steps[stepIndex];
    if (!step) return;
    
    // Update container states
    this.containers.forEach(container => {
      if (step.visibleContainerIds.includes(container.id)) {
        if (step.highlightedContainerIds.includes(container.id)) {
          container.state = 'highlight';
        } else {
          container.state = 'normal';
        }
      } else {
        container.state = 'hidden';
      }
    });
    
    // Update connection states
    this.connections.forEach(connection => {
      if (step.visibleConnectionIds.includes(connection.id)) {
        if (step.highlightedConnectionIds.includes(connection.id)) {
          connection.state = 'highlight';
        } else {
          connection.state = 'normal';
        }
      } else {
        connection.state = 'hidden';
      }
    });
    
    this.cdr.markForCheck();
  }
  
  /**
   * Get current step configuration
   */
  protected get currentStep(): EdgeStepConfig {
    return this.steps[this.currentStepIndex];
  }
  
  /**
   * Check if we're at the first step
   */
  protected get isFirstStep(): boolean {
    return this.currentStepIndex === 0;
  }
  
  /**
   * Check if we're at the last step
   */
  protected get isLastStep(): boolean {
    return this.currentStepIndex === this.steps.length - 1;
  }
  
  /**
   * Get center point of a container
   */
  protected getContainerCenter(containerId: string): { x: number; y: number } {
    const container = this.containers.find(c => c.id === containerId);
    if (!container) return { x: 0, y: 0 };
    return {
      x: container.x + container.width / 2,
      y: container.y + container.height / 2,
    };
  }
  
  /**
   * Get connection line coordinates
   */
  protected getConnectionLine(connection: EdgeConnectionConfig): { x1: number; y1: number; x2: number; y2: number } {
    const from = this.getContainerCenter(connection.from);
    const to = this.getContainerCenter(connection.to);
    return {
      x1: from.x,
      y1: from.y,
      x2: to.x,
      y2: to.y,
    };
  }
}
