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
  EDGE_LAYOUT_SCALED,
} from './edge-architecture-animated.config';
import { DspArchitectureConfigService } from '../../../../services/dsp-architecture-config.service';

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
  
  constructor(
    private cdr: ChangeDetectorRef,
    private architectureConfigService: DspArchitectureConfigService
  ) {}
  
  ngOnInit(): void {
    // Get shared architecture configuration from service
    const sharedConfig = this.architectureConfigService.createCustomerConfiguration();
    
    this.containers = createEdgeContainers(sharedConfig);
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
   * Uses scaled positions when in full architecture view
   */
  protected getConnectionLine(connection: EdgeConnectionConfig): { x1: number; y1: number; x2: number; y2: number } {
    const fromContainer = this.containers.find(c => c.id === connection.from);
    const toContainer = this.containers.find(c => c.id === connection.to);
    
    if (!fromContainer || !toContainer) {
      return { x1: 0, y1: 0, x2: 0, y2: 0 };
    }
    
    // Get scaled positions and dimensions
    const fromX = this.getScaledX(fromContainer);
    const fromY = this.getScaledY(fromContainer);
    const fromWidth = this.getScaledWidth(fromContainer);
    const fromHeight = this.getScaledHeight(fromContainer);
    
    const toX = this.getScaledX(toContainer);
    const toY = this.getScaledY(toContainer);
    const toWidth = this.getScaledWidth(toContainer);
    const toHeight = this.getScaledHeight(toContainer);
    
    // Get centers using scaled dimensions
    const fromCenter = {
      x: fromX + fromWidth / 2,
      y: fromY + fromHeight / 2,
    };
    const toCenter = {
      x: toX + toWidth / 2,
      y: toY + toHeight / 2,
    };
    
    // Create scaled container objects for border calculation
    const scaledFromContainer = {
      ...fromContainer,
      x: fromX,
      y: fromY,
      width: fromWidth,
      height: fromHeight,
    };
    const scaledToContainer = {
      ...toContainer,
      x: toX,
      y: toY,
      width: toWidth,
      height: toHeight,
    };
    
    // Calculate border intersection points
    const fromPoint = this.getBoxBorderPoint(scaledFromContainer, fromCenter, toCenter);
    const toPoint = this.getBoxBorderPoint(scaledToContainer, toCenter, fromCenter);
    
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
  
  /**
   * Check if a container is an Edge component (not layer, zone, or architecture container)
   */
  protected isEdgeComponent(containerId: string): boolean {
    const edgeComponentIds = ['disc', 'router', 'agent', 'app-server', 'log-server', 'disi', 'db', 'event-bus'];
    return edgeComponentIds.includes(containerId);
  }
  
  /**
   * Check if a container is an architecture container (Business, Shopfloor, Cloud)
   */
  protected isArchitectureContainer(containerId: string): boolean {
    return containerId.startsWith('business-') || 
           containerId.startsWith('shopfloor-') || 
           containerId.startsWith('cloud-') && 
           containerId !== 'edge-container';
  }
  
  /**
   * Get layer background fill color
   */
  protected getLayerFill(layerId: string): string {
    switch (layerId) {
      case 'layer-business':
        return '#ffffff';
      case 'layer-dsp':
        return 'rgba(207, 230, 255, 0.5)';
      case 'layer-shopfloor':
        return 'rgba(241, 243, 247, 0.8)';
      default:
        return 'transparent';
    }
  }
  
  /**
   * Get layer border stroke color
   */
  protected getLayerStroke(layerId: string): string {
    switch (layerId) {
      case 'layer-business':
        return 'rgba(22, 65, 148, 0.1)';
      case 'layer-dsp':
        return 'rgba(22, 65, 148, 0.15)';
      case 'layer-shopfloor':
        return 'rgba(31, 54, 91, 0.12)';
      default:
        return '#ccc';
    }
  }
  
  /**
   * Get container stroke color based on type
   */
  protected getContainerStroke(containerId: string): string {
    if (containerId.startsWith('business-')) {
      return 'rgba(22, 65, 148, 0.25)';
    } else if (containerId.startsWith('cloud-')) {
      return '#009681';
    } else if (containerId.startsWith('shopfloor-')) {
      return 'rgba(31, 54, 91, 0.2)';
    }
    return '#164194';
  }
  
  /**
   * Get display name for architecture containers
   */
  protected getContainerDisplayName(containerId: string): string {
    const names: Record<string, string> = {
      'business-erp': $localize`:@@businessErp:ERP Applications`,
      'business-cloud': $localize`:@@businessCloud:Cloud Applications`,
      'business-analytics': $localize`:@@businessAnalytics:Analytics Applications`,
      'business-data-lake': $localize`:@@businessDataLake:Data Lake`,
      'business-dashboard': $localize`:@@businessDashboard:SmartFactory Dashboard`,
      'cloud-management-cockpit': $localize`:@@cloudManagementCockpit:Management Cockpit`,
      'shopfloor-systems': $localize`:@@shopfloorSystems:Shopfloor Systems`,
      'shopfloor-devices': $localize`:@@shopfloorDevices:Devices`,
    };
    return names[containerId] || containerId;
  }
  
  /**
   * Get scaled X coordinate for edge components in full architecture view (Steps 3-4)
   * Since components are now properly sized for the EDGE box, no scaling needed
   */
  protected getScaledX(container: EdgeContainerConfig): number {
    return container.x;
  }
  
  /**
   * Get scaled Y coordinate for edge components in full architecture view (Steps 3-4)
   * Since components are now properly sized for the EDGE box, no scaling needed
   */
  protected getScaledY(container: EdgeContainerConfig): number {
    return container.y;
  }
  
  /**
   * Get scaled width for edge components in full architecture view (Steps 3-4)
   * Since components are now properly sized for the EDGE box, no scaling needed
   */
  protected getScaledWidth(container: EdgeContainerConfig): number {
    return container.width;
  }
  
  /**
   * Get scaled height for edge components in full architecture view (Steps 3-4)
   * Since components are now properly sized for the EDGE box, no scaling needed
   */
  protected getScaledHeight(container: EdgeContainerConfig): number {
    return container.height;
  }
  
  /**
   * Get scaled icon size for edge components in full architecture view (Steps 3-4)
   * Use smaller icons in full architecture view for better readability
   */
  protected getScaledIconSize(container: EdgeContainerConfig): number {
    const currentStep = this.steps[this.currentStepIndex];
    if (currentStep?.showFullArchitecture && this.isEdgeComponent(container.id)) {
      return EDGE_LAYOUT_SCALED.ICON_SIZE;  // 32px for full architecture view
    }
    return 38; // Default icon size for detail view
  }
  
  /**
   * Get connection line for external connections (edge components to architecture containers)
   * These connections use horizontal/vertical routing only (no diagonals)
   */
  protected getExternalConnectionLine(fromId: string, toId: string): string {
    const fromContainer = this.containers.find(c => c.id === fromId);
    const toContainer = this.containers.find(c => c.id === toId);
    
    if (!fromContainer || !toContainer) {
      return '';
    }
    
    // Get container centers
    const fromCenterX = fromContainer.x + fromContainer.width / 2;
    const fromCenterY = fromContainer.y + fromContainer.height / 2;
    const toCenterX = toContainer.x + toContainer.width / 2;
    const toCenterY = toContainer.y + toContainer.height / 2;
    
    // For horizontal connections (App Server → Dashboard, Agent → Management Cockpit)
    // Route: horizontal from edge of source, then vertical, then horizontal to target
    if (Math.abs(fromCenterY - toCenterY) < 50) {
      // Primarily horizontal connection
      const startX = fromContainer.x + (fromCenterX < toCenterX ? fromContainer.width : 0);
      const startY = fromCenterY;
      const endX = toContainer.x + (toCenterX > fromCenterX ? 0 : toContainer.width);
      const endY = toCenterY;
      
      return `M ${startX},${startY} L ${endX},${endY}`;
    }
    
    // For vertical connections (DISC → ERP, DISI → Shopfloor, Event Bus/DB → Data Lake)
    // Route: vertical from edge of source, then horizontal, then vertical to target
    const startX = fromCenterX;
    const startY = fromContainer.y + (fromCenterY < toCenterY ? fromContainer.height : 0);
    const endX = toCenterX;
    const endY = toContainer.y + (toCenterY > fromCenterY ? 0 : toContainer.height);
    
    // Create L-shaped path: vertical then horizontal
    const midY = startY + (endY - startY) / 2;
    
    return `M ${startX},${startY} L ${startX},${midY} L ${endX},${midY} L ${endX},${endY}`;
  }
}
