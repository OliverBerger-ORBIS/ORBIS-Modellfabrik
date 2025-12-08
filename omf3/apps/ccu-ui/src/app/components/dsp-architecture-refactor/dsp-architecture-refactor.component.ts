import { CommonModule } from '@angular/common';
import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  EventEmitter,
  OnDestroy,
  OnInit,
  Output,
} from '@angular/core';
import { getIconPath, type IconKey } from '../../assets/icon-registry';
import type {
  ContainerConfig,
  ConnectionConfig,
  StepConfig,
  Point,
  AnchorSide,
} from './types';
import {
  createDiagramConfig,
  VIEWBOX_WIDTH,
  VIEWBOX_HEIGHT,
} from './layout.config';

/**
 * DspArchitectureRefactorComponent - Refactored animated SVG-based architecture diagram.
 *
 * Matches the existing DSP architecture component with continuous layer backgrounds,
 * grid-based positioning, and animation steps 1, 2, 3, 7, 10, and final.
 */
@Component({
  standalone: true,
  selector: 'app-dsp-architecture-refactor',
  imports: [CommonModule],
  templateUrl: './dsp-architecture-refactor.component.html',
  styleUrl: './dsp-architecture-refactor.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspArchitectureRefactorComponent implements OnInit, OnDestroy {
  @Output() actionTriggered = new EventEmitter<{ id: string; url: string }>();

  // Diagram configuration
  protected containers: ContainerConfig[] = [];
  protected connections: ConnectionConfig[] = [];
  protected steps: StepConfig[] = [];

  // Animation state
  protected currentStepIndex = 0;
  protected isAutoPlaying = false;
  private autoPlayInterval: ReturnType<typeof setInterval> | null = null;

  // Zoom state
  protected zoom = 1;
  protected readonly minZoom = 0.6;
  protected readonly maxZoom = 1.6;
  protected readonly zoomStep = 0.1;

  // ViewBox dimensions
  protected readonly viewBoxWidth = VIEWBOX_WIDTH;
  protected readonly viewBoxHeight = VIEWBOX_HEIGHT;

  // i18n labels
  protected readonly title = $localize`:@@dspArchRefactorTitle:DSP Architecture - Refactored`;
  protected readonly subtitle = $localize`:@@dspArchRefactorSubtitle:Reference Architecture`;
  protected readonly labelBusinessProcesses = $localize`:@@dspArchLabelBusiness:Business Processes`;
  protected readonly labelDsp = $localize`:@@dspArchLabelDsp:DSP`;
  protected readonly labelShopfloor = $localize`:@@dspArchLabelShopfloor:Shopfloor`;
  protected readonly labelOnPremise = $localize`:@@dspArchLabelOnPremise:On Premise`;
  protected readonly labelCloud = $localize`:@@dspArchLabelCloud:Cloud`;
  protected readonly labelDevices = $localize`:@@dspArchLabelDevices:Devices`;
  protected readonly labelSystems = $localize`:@@dspArchLabelSystems:Systems`;
  protected readonly labelSmartfactoryDashboard = $localize`:@@dspArchLabelUX:SmartFactory\nDashboard`;
  protected readonly labelEdge = $localize`:@@dspArchLabelEdge:EDGE`;
  protected readonly labelManagementCockpit = $localize`:@@dspArchLabelManagement:Management Cockpit`;
  protected readonly btnPrev = $localize`:@@dspArchPrev:Previous`;
  protected readonly btnNext = $localize`:@@dspArchNext:Next`;
  protected readonly btnAutoPlay = $localize`:@@dspArchAutoPlay:Auto Play`;
  protected readonly btnStopPlay = $localize`:@@dspArchStopPlay:Stop`;
  protected readonly zoomOutLabel = $localize`:@@shopfloorPreviewZoomOut:Zoom out`;
  protected readonly zoomInLabel = $localize`:@@shopfloorPreviewZoomIn:Zoom in`;
  protected readonly resetZoomLabel = $localize`:@@shopfloorPreviewResetZoom:Reset zoom`;

  // Container labels
  protected readonly containerLabels: Record<string, string> = {
    'erp-application': $localize`:@@dspArchLabelERP:ERP Applications`,
    'bp-cloud-apps': $localize`:@@dspArchLabelCloudApps:Cloud\nApplications`,
    'bp-analytics': $localize`:@@dspArchLabelAnalytics:Analytical\nApplications`,
    'bp-data-lake': $localize`:@@dspArchLabelDataLake:Data Lake`,
    'shopfloor-system-bp': $localize`:@@dspArchLabelMES:MES`,
    'shopfloor-system-fts': $localize`:@@dspArchLabelFTS:AGV\nSystem`,
    'shopfloor-device-1': $localize`:@@deviceMILL:Mill`,
    'shopfloor-device-2': $localize`:@@deviceDRILL:Drill`,
    'shopfloor-device-3': $localize`:@@deviceAIQS:AIQS`,
    'shopfloor-device-4': $localize`:@@deviceHBW:HBW`,
    'shopfloor-device-5': $localize`:@@deviceDPS:DPS`,
    'shopfloor-device-6': $localize`:@@deviceCHRG:Charger`,
  };

  constructor(private readonly cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.initializeDiagram();
    this.applyStep(0);
  }

  ngOnDestroy(): void {
    this.stopAutoPlay();
  }

  /**
   * Initialize diagram configuration
   */
  private initializeDiagram(): void {
    const config = createDiagramConfig();
    this.containers = config.containers;
    this.connections = config.connections;
    this.steps = config.steps;
  }

  /**
   * Check if container should be visible
   */
  protected isContainerVisible(container: ContainerConfig): boolean {
    const step = this.steps[this.currentStepIndex];
    if (!step) return true;
    return step.visibleContainerIds.includes(container.id);
  }

  /**
   * Check if container should be highlighted
   */
  protected isContainerHighlighted(container: ContainerConfig): boolean {
    const step = this.steps[this.currentStepIndex];
    if (!step) return false;
    return step.highlightedContainerIds.includes(container.id);
  }

  /**
   * Check if connection should be visible
   */
  protected isConnectionVisible(connection: ConnectionConfig): boolean {
    const step = this.steps[this.currentStepIndex];
    if (!step) return true;
    return step.visibleConnectionIds.includes(connection.id);
  }

  /**
   * Check if connection should be highlighted
   */
  protected isConnectionHighlighted(connection: ConnectionConfig): boolean {
    const step = this.steps[this.currentStepIndex];
    if (!step) return false;
    return step.highlightedConnectionIds.includes(connection.id);
  }

  /**
   * Check if function icons should be shown
   */
  protected shouldShowFunctionIcons(): boolean {
    const step = this.steps[this.currentStepIndex];
    return step?.showFunctionIcons !== false;
  }

  /**
   * Check if a specific function icon is highlighted
   */
  protected isFunctionIconHighlighted(iconKey: string): boolean {
    const step = this.steps[this.currentStepIndex];
    if (!step?.highlightedFunctionIcons) return false;
    return step.highlightedFunctionIcons.includes(iconKey);
  }

  /**
   * Get container fill color
   */
  protected getContainerFill(container: ContainerConfig): string {
    return container.backgroundColor || '#ffffff';
  }

  /**
   * Get container stroke color
   */
  protected getContainerStroke(container: ContainerConfig): string {
    if (this.isContainerHighlighted(container)) {
      return '#ff9900'; // Highlight color
    }
    return container.borderColor || '#cccccc';
  }

  /**
   * Get container stroke width
   */
  protected getContainerStrokeWidth(container: ContainerConfig): number {
    if (this.isContainerHighlighted(container)) {
      return 3;
    }
    return 2;
  }

  /**
   * Get container class
   */
  protected getContainerClass(container: ContainerConfig): string {
    const classes = ['container'];
    classes.push(`container--${container.type}`);
    if (this.isContainerHighlighted(container)) {
      classes.push('container--highlighted');
    }
    if (container.url) {
      classes.push('container--clickable');
    }
    return classes.join(' ');
  }

  /**
   * Get label for container
   */
  protected getContainerLabel(containerId: string): string {
    return this.containerLabels[containerId] || '';
  }

  /**
   * Get multi-line label
   */
  protected getMultilineLabel(containerId: string): string[] {
    const label = this.getContainerLabel(containerId);
    if (containerId === 'layer-business') return [this.labelBusinessProcesses];
    if (containerId === 'layer-dsp') return [this.labelDsp];
    if (containerId === 'layer-shopfloor') return [this.labelShopfloor];
    if (containerId === 'dsp-label-onpremise') return [this.labelOnPremise];
    if (containerId === 'dsp-label-cloud') return [this.labelCloud];
    if (containerId === 'shopfloor-devices-group') return [this.labelDevices];
    if (containerId === 'shopfloor-systems-group') return [this.labelSystems];
    if (containerId === 'ux') return this.labelSmartfactoryDashboard.split('\\n');
    if (containerId === 'edge') return [this.labelEdge];
    if (containerId === 'management') return [this.labelManagementCockpit];
    return label.split('\\n');
  }

  /**
   * Check if label is multiline
   */
  protected isMultilineLabel(containerId: string): boolean {
    return this.getMultilineLabel(containerId).length > 1;
  }

  /**
   * Check if label should wrap
   */
  protected shouldWrapLabel(container: ContainerConfig): boolean {
    // Device and system labels can wrap
    return container.type === 'device' || container.type === 'shopfloor';
  }

  /**
   * Get label X position
   */
  protected getLabelX(container: ContainerConfig): number {
    // Center label
    return container.width / 2;
  }

  /**
   * Get label Y position
   */
  protected getLabelY(container: ContainerConfig): number {
    // Position at bottom center for most containers
    if (container.labelPosition === 'bottom-center') {
      return container.height - 8;
    }
    if (container.labelPosition === 'top-center') {
      return 20;
    }
    return container.height / 2;
  }

  /**
   * Get label anchor
   */
  protected getLabelAnchor(container: ContainerConfig): string {
    // Most labels are centered
    return 'middle';
  }

  /**
   * Get wrapped label lines
   */
  protected getWrappedLabelLines(container: ContainerConfig): string[] {
    const label = this.getContainerLabel(container.id);
    // Simple word wrap - split on spaces if needed
    if (label.length > 15 && container.width < 100) {
      const words = label.split(' ');
      if (words.length > 1) {
        return words;
      }
    }
    return [label];
  }

  /**
   * Get layer font size
   */
  protected getLayerFontSize(containerId: string): number {
    if (containerId === 'layer-dsp') return 18;
    return 16;
  }

  /**
   * Resolve icon path
   */
  protected resolveIconPath(iconKey: IconKey | string): string {
    return getIconPath(iconKey as IconKey);
  }

  /**
   * Get connection path (alias for calculateConnectionPath)
   */
  protected getConnectionPath(connection: ConnectionConfig): string {
    return this.calculateConnectionPath(connection);
  }

  /**
   * Calculate connection path
   */
  protected calculateConnectionPath(connection: ConnectionConfig): string {
    const fromContainer = this.containers.find(c => c.id === connection.fromId);
    const toContainer = this.containers.find(c => c.id === connection.toId);
    
    if (!fromContainer || !toContainer) return '';

    const from = this.getAnchorPoint(fromContainer, connection.fromSide || 'bottom');
    const to = this.getAnchorPoint(toContainer, connection.toSide || 'top');

    // Simple L-shaped path
    const midY = (from.y + to.y) / 2;
    return `M ${from.x} ${from.y} L ${from.x} ${midY} L ${to.x} ${midY} L ${to.x} ${to.y}`;
  }

  /**
   * Get connection class
   */
  protected getConnectionClass(connection: ConnectionConfig): string {
    const classes = ['connection'];
    if (this.isConnectionHighlighted(connection)) {
      classes.push('connection--highlighted');
    }
    return classes.join(' ');
  }

  /**
   * Get anchor point for a container side
   */
  private getAnchorPoint(container: ContainerConfig, side: AnchorSide): Point {
    const { x, y, width, height } = container;
    
    switch (side) {
      case 'top':
        return { x: x + width / 2, y };
      case 'bottom':
        return { x: x + width / 2, y: y + height };
      case 'left':
        return { x, y: y + height / 2 };
      case 'right':
        return { x: x + width, y: y + height / 2 };
    }
  }

  /**
   * Handle container click
   */
  protected onContainerClick(container: ContainerConfig): void {
    if (container.url) {
      this.actionTriggered.emit({ id: container.id, url: container.url });
    }
  }

  /**
   * Handle container keydown
   */
  protected onContainerKeydown(event: KeyboardEvent, container: ContainerConfig): void {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      this.onContainerClick(container);
    }
  }

  // Navigation methods
  protected prevStep(): void {
    if (this.currentStepIndex > 0) {
      this.applyStep(this.currentStepIndex - 1);
    }
  }

  protected nextStep(): void {
    if (this.currentStepIndex < this.steps.length - 1) {
      this.applyStep(this.currentStepIndex + 1);
    }
  }

  protected goToStep(index: number): void {
    if (index >= 0 && index < this.steps.length) {
      this.applyStep(index);
    }
  }

  protected toggleAutoPlay(): void {
    if (this.isAutoPlaying) {
      this.stopAutoPlay();
    } else {
      this.startAutoPlay();
    }
  }

  private startAutoPlay(): void {
    this.isAutoPlaying = true;
    this.autoPlayInterval = setInterval(() => {
      if (this.currentStepIndex < this.steps.length - 1) {
        this.nextStep();
      } else {
        this.stopAutoPlay();
        this.applyStep(0);
      }
    }, 3000);
    this.cdr.markForCheck();
  }

  private stopAutoPlay(): void {
    this.isAutoPlaying = false;
    if (this.autoPlayInterval) {
      clearInterval(this.autoPlayInterval);
      this.autoPlayInterval = null;
    }
    this.cdr.markForCheck();
  }

  private applyStep(index: number): void {
    this.currentStepIndex = index;
    this.cdr.markForCheck();
  }

  // Zoom methods
  protected zoomIn(): void {
    if (this.zoom < this.maxZoom) {
      this.zoom = Math.min(this.zoom + this.zoomStep, this.maxZoom);
      this.cdr.markForCheck();
    }
  }

  protected zoomOut(): void {
    if (this.zoom > this.minZoom) {
      this.zoom = Math.max(this.zoom - this.zoomStep, this.minZoom);
      this.cdr.markForCheck();
    }
  }

  protected resetZoom(): void {
    this.zoom = 1;
    this.cdr.markForCheck();
  }

  // Trackby functions
  protected containerTrackBy(index: number, item: ContainerConfig): string {
    return item.id;
  }

  protected connectionTrackBy(index: number, item: ConnectionConfig): string {
    return item.id;
  }

  protected iconTrackBy(index: number, item: { iconKey: IconKey; size: number }): string {
    return item.iconKey;
  }
}
