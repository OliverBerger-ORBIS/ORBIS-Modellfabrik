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
   * Calculates lines that stop at the border of component boxes
   */
  protected getConnectionLine(connection: EdgeConnectionConfig): { x1: number; y1: number; x2: number; y2: number } {
    const fromContainer = this.containers.find(c => c.id === connection.from);
    const toContainer = this.containers.find(c => c.id === connection.to);
    
    if (!fromContainer || !toContainer) {
      return { x1: 0, y1: 0, x2: 0, y2: 0 };
    }
    
    // Get centers
    const fromCenter = {
      x: fromContainer.x + fromContainer.width / 2,
      y: fromContainer.y + fromContainer.height / 2,
    };
    const toCenter = {
      x: toContainer.x + toContainer.width / 2,
      y: toContainer.y + toContainer.height / 2,
    };
    
    // Calculate border intersection points
    const fromPoint = this.getBoxBorderPoint(fromContainer, fromCenter, toCenter);
    const toPoint = this.getBoxBorderPoint(toContainer, toCenter, fromCenter);
    
    return {
      x1: fromPoint.x,
      y1: fromPoint.y,
      x2: toPoint.x,
      y2: toPoint.y,
    };
  }
  
  /**
   * Calculate the intersection point of a line from box center to external point
   * on the box border
   */
  private getBoxBorderPoint(
    box: EdgeContainerConfig,
    boxCenter: { x: number; y: number },
    externalPoint: { x: number; y: number }
  ): { x: number; y: number } {
    const dx = externalPoint.x - boxCenter.x;
    const dy = externalPoint.y - boxCenter.y;
    
    if (dx === 0 && dy === 0) {
      return boxCenter;
    }
    
    // Box boundaries
    const halfWidth = box.width / 2;
    const halfHeight = box.height / 2;
    
    // Normalize direction
    const angle = Math.atan2(dy, dx);
    
    // Determine which edge the line intersects
    const tanAngle = Math.abs(Math.tan(angle));
    const threshold = halfHeight / halfWidth;
    
    let borderX: number, borderY: number;
    
    if (tanAngle < threshold) {
      // Intersects left or right edge
      borderX = boxCenter.x + (dx > 0 ? halfWidth : -halfWidth);
      borderY = boxCenter.y + (borderX - boxCenter.x) * (dy / dx);
    } else {
      // Intersects top or bottom edge
      borderY = boxCenter.y + (dy > 0 ? halfHeight : -halfHeight);
      borderX = boxCenter.x + (borderY - boxCenter.y) * (dx / dy);
    }
    
    return { x: borderX, y: borderY };
  }
}
