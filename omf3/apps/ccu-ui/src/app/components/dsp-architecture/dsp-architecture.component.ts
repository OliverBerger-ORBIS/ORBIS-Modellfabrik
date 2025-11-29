import { CommonModule } from '@angular/common';
import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  EventEmitter,
  Input,
  OnDestroy,
  OnInit,
  Output,
} from '@angular/core';
import type { DspDetailView } from '../../tabs/configuration-detail.types';
import { getIconPath, type IconKey } from '../../assets/icon-registry';
import type {
  ContainerConfig,
  ConnectionConfig,
  StepConfig,
  Point,
  AnchorSide,
} from './dsp-architecture.types';
import {
  createDiagramConfig,
  VIEWBOX_WIDTH,
  VIEWBOX_HEIGHT,
} from './dsp-architecture.config';

/**
 * DspArchitectureComponent - Animated SVG-based architecture diagram.
 *
 * This component displays the DSP reference architecture with step-by-step
 * animation similar to PowerPoint slides. It can be used as a drop-in
 * replacement for DspDetailComponent.
 *
 * Features:
 * - 6-step animation sequence
 * - Navigation buttons (Prev/Next/Auto Play)
 * - Zoom controls (+/-/Reset)
 * - Responsive SVG with viewBox
 * - i18n-ready labels
 */
@Component({
  standalone: true,
  selector: 'app-dsp-architecture',
  imports: [CommonModule],
  templateUrl: './dsp-architecture.component.html',
  styleUrl: './dsp-architecture.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspArchitectureComponent implements OnInit, OnDestroy {
  @Input({ required: true }) view!: DspDetailView;
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
  protected readonly minZoom = 0.5;
  protected readonly maxZoom = 2;
  protected readonly zoomStep = 0.1;

  // ViewBox dimensions
  protected readonly viewBoxWidth = VIEWBOX_WIDTH;
  protected readonly viewBoxHeight = VIEWBOX_HEIGHT;

  // i18n labels
  protected readonly title = $localize`:@@dspArchTitle:DISTRIBUTED SHOP FLOOR PROCESSING (DSP)`;
  protected readonly subtitle = $localize`:@@dspArchSubtitle:Referenzarchitektur`;
  protected readonly labelBusinessProcesses = $localize`:@@dspArchLabelBusiness:Business\nProzesse`;
  protected readonly labelDsp = $localize`:@@dspArchLabelDsp:DSP`;
  protected readonly labelShopfloor = $localize`:@@dspArchLabelShopfloor:Shopfloor`;  // Changed: no "Systeme und Geräte"
  protected readonly labelOnPremise = $localize`:@@dspArchLabelOnPremise:On Premise`;
  protected readonly labelCloud = $localize`:@@dspArchLabelCloud:Cloud`;
  protected readonly labelDevices = $localize`:@@dspArchLabelDevices:Geräte`;  // Label at bottom, centered
  protected readonly labelSystems = $localize`:@@dspArchLabelSystems:Systeme`;  // Label at bottom, centered
  protected readonly labelSmartfactoryDashboard = $localize`:@@dspArchLabelUX:Smartfactory\nDashboard`;  // Two-line label
  protected readonly btnPrev = $localize`:@@dspArchPrev:Zurück`;
  protected readonly btnNext = $localize`:@@dspArchNext:Weiter`;
  protected readonly btnAutoPlay = $localize`:@@dspArchAutoPlay:Auto Play`;
  protected readonly btnStopPlay = $localize`:@@dspArchStopPlay:Stop`;

  // Step labels (8 steps)
  protected readonly stepLabels = [
    $localize`:@@dspArchStep1:Geräte`,
    $localize`:@@dspArchStep2:Shopfloor Systeme`,
    $localize`:@@dspArchStep3:DSP EDGE`,
    $localize`:@@dspArchStep4:EDGE Funktionen`,
    $localize`:@@dspArchStep5:Shopfloor Verbindungen`,
    $localize`:@@dspArchStep6:Dashboard & Cockpit`,
    $localize`:@@dspArchStep7:SAP Integration`,
    $localize`:@@dspArchStep8:Business Prozesse`,
  ];

  // Container labels from view
  protected readonly containerLabels: Record<string, string> = {};

  constructor(private readonly cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.initializeDiagram();
    this.initializeLabelsFromView();
  }

  ngOnDestroy(): void {
    this.stopAutoPlay();
  }

  /**
   * Initialize diagram configuration.
   */
  private initializeDiagram(): void {
    const config = createDiagramConfig();
    this.containers = config.containers;
    this.connections = config.connections;
    this.steps = config.steps;

    // Update step labels
    this.steps.forEach((step, index) => {
      step.label = this.stepLabels[index] || `Step ${index + 1}`;
    });

    // Apply initial step
    this.applyStepInternal(0);
  }

  /**
   * Initialize container labels from DspDetailView.
   */
  private initializeLabelsFromView(): void {
    // Map architecture layers
    this.view.architecture.forEach((layer) => {
      this.containerLabels[layer.id] = layer.title;
    });

    // Map business processes
    this.view.businessProcesses.forEach((bp) => {
      const mappedId = this.mapBusinessProcessId(bp.id);
      this.containerLabels[mappedId] = bp.label;
    });

    // Set static labels for layer backgrounds (multiline)
    this.containerLabels['layer-business'] = this.labelBusinessProcesses;
    this.containerLabels['layer-dsp'] = this.labelDsp;
    this.containerLabels['layer-shopfloor'] = this.labelShopfloor;
    this.containerLabels['dsp-label-onpremise'] = this.labelOnPremise;
    this.containerLabels['dsp-label-cloud'] = this.labelCloud;
    this.containerLabels['shopfloor-systems-group'] = this.labelSystems;  // Label at bottom
    this.containerLabels['shopfloor-devices-group'] = this.labelDevices;  // Label at bottom
    this.containerLabels['ux'] = this.labelSmartfactoryDashboard;  // Two-line label
  }

  /**
   * Map business process ID from view to container ID.
   */
  private mapBusinessProcessId(viewId: string): string {
    const mapping: Record<string, string> = {
      'shopfloor': 'bp-sap-shopfloor',
      'cloud-apps': 'bp-cloud-apps',
      'analytics': 'bp-analytics',
      'data-lake': 'bp-data-lake',
    };
    return mapping[viewId] || `bp-${viewId}`;
  }

  /**
   * Get container label.
   */
  protected getContainerLabel(containerId: string): string {
    // Get label from container config if it has one
    const container = this.containers.find(c => c.id === containerId);
    if (container?.label) {
      return container.label;
    }
    return this.containerLabels[containerId] || '';
  }

  /**
   * Get multiline label as array of lines.
   */
  protected getMultilineLabel(containerId: string): string[] {
    const label = this.containerLabels[containerId] || '';
    return label.split('\n');
  }

  /**
   * Check if a label is multiline.
   */
  protected isMultilineLabel(containerId: string): boolean {
    const label = this.containerLabels[containerId] || '';
    return label.includes('\n');
  }

  /**
   * Get label X position based on labelPosition.
   */
  protected getLabelX(container: ContainerConfig): number {
    const position = container.labelPosition || 'bottom-center';
    switch (position) {
      case 'left':
      case 'left-inside':
        return 10;
      case 'right-inside':
        return container.width - 10;
      case 'top-center':
      case 'bottom-center':
      case 'bottom':
      default:
        return container.width / 2;
    }
  }

  /**
   * Get label Y position based on labelPosition.
   */
  protected getLabelY(container: ContainerConfig): number {
    const position = container.labelPosition || 'bottom-center';
    switch (position) {
      case 'top-center':
        return container.logoIconKey && container.logoPosition === 'top-left' ? 24 : 18;
      case 'bottom':
        return container.height - 8;
      case 'bottom-center':
        return container.functionIcons?.length ? container.height - 12 : container.height - 15;
      case 'left':
      case 'left-inside':
      case 'right-inside':
        return container.height / 2;
      default:
        return container.height / 2 + 5;
    }
  }

  /**
   * Get label text-anchor based on labelPosition.
   */
  protected getLabelAnchor(container: ContainerConfig): string {
    const position = container.labelPosition || 'bottom-center';
    switch (position) {
      case 'left':
      case 'left-inside':
        return 'start';
      case 'right-inside':
        return 'end';
      case 'top-center':
      case 'bottom-center':
      case 'bottom':
      default:
        return 'middle';
    }
  }

  /**
   * Apply a specific animation step.
   */
  /**
   * Apply a specific animation step (public for template use).
   */
  protected goToStep(stepIndex: number): void {
    this.applyStepInternal(stepIndex);
    this.cdr.markForCheck();
  }

  /**
   * Apply a specific animation step (internal).
   */
  private applyStepInternal(stepIndex: number): void {
    if (stepIndex < 0 || stepIndex >= this.steps.length) {
      return;
    }

    const step = this.steps[stepIndex];

    // Update container states
    this.containers.forEach((container) => {
      if (step.visibleContainerIds.includes(container.id)) {
        container.state = step.highlightedContainerIds.includes(container.id) ? 'highlight' : 'normal';
      } else {
        container.state = 'hidden';
      }
    });

    // Update connection states
    this.connections.forEach((conn) => {
      if (step.visibleConnectionIds.includes(conn.id)) {
        conn.state = step.highlightedConnectionIds.includes(conn.id) ? 'highlight' : 'normal';
      } else {
        conn.state = 'hidden';
      }
    });

    this.currentStepIndex = stepIndex;
  }

  /**
   * Navigate to previous step.
   */
  protected prevStep(): void {
    if (this.currentStepIndex > 0) {
      this.applyStepInternal(this.currentStepIndex - 1);
      this.cdr.markForCheck();
    }
  }

  /**
   * Navigate to next step.
   */
  protected nextStep(): void {
    if (this.currentStepIndex < this.steps.length - 1) {
      this.applyStepInternal(this.currentStepIndex + 1);
      this.cdr.markForCheck();
    }
  }

  /**
   * Toggle auto play mode.
   */
  protected toggleAutoPlay(): void {
    if (this.isAutoPlaying) {
      this.stopAutoPlay();
    } else {
      this.startAutoPlay();
    }
  }

  /**
   * Start auto play.
   */
  private startAutoPlay(): void {
    this.isAutoPlaying = true;
    this.autoPlayInterval = setInterval(() => {
      if (this.currentStepIndex < this.steps.length - 1) {
        this.nextStep();
      } else {
        this.stopAutoPlay();
      }
    }, 2500);
  }

  /**
   * Stop auto play.
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
   * Zoom in.
   */
  protected zoomIn(): void {
    this.zoom = Math.min(this.maxZoom, this.zoom + this.zoomStep);
  }

  /**
   * Zoom out.
   */
  protected zoomOut(): void {
    this.zoom = Math.max(this.minZoom, this.zoom - this.zoomStep);
  }

  /**
   * Reset zoom to 100%.
   */
  protected resetZoom(): void {
    this.zoom = 1;
  }

  /**
   * Check if container is visible.
   */
  protected isContainerVisible(container: ContainerConfig): boolean {
    return container.state !== 'hidden';
  }

  /**
   * Check if connection is visible.
   */
  protected isConnectionVisible(conn: ConnectionConfig): boolean {
    return conn.state !== 'hidden';
  }

  /**
   * Get container CSS class based on state.
   */
  protected getContainerClass(container: ContainerConfig): string {
    const classes = ['container', `container--${container.type}`];

    if (container.state === 'highlight') {
      classes.push('container--highlight');
    } else if (container.state === 'dimmed') {
      classes.push('container--dimmed');
    }

    if (container.isGroup) {
      classes.push('container--group');
    }

    // Add clickable class if container has a URL
    if (container.url) {
      classes.push('container--clickable');
    }

    return classes.join(' ');
  }

  /**
   * Get connection CSS class based on state.
   */
  protected getConnectionClass(conn: ConnectionConfig): string {
    const classes = ['connection'];

    if (conn.state === 'highlight') {
      classes.push('connection--highlight');
    } else if (conn.state === 'dimmed') {
      classes.push('connection--dimmed');
    }

    return classes.join(' ');
  }

  /**
   * Get container fill color.
   */
  protected getContainerFill(container: ContainerConfig): string {
    if (container.type === 'label') {
      return 'transparent';
    }
    return container.backgroundColor || '#ffffff';
  }

  /**
   * Get container stroke color.
   */
  protected getContainerStroke(container: ContainerConfig): string {
    if (container.type === 'label') {
      return 'transparent';
    }
    if (container.state === 'highlight') {
      // Highlight color based on type
      if (container.type === 'dsp-edge') return '#009B77';
      if (container.type === 'dsp-cloud') return '#0078D4';
      if (container.type === 'business') return '#ff9900';
      return '#1f54b2';
    }
    return container.borderColor || 'rgba(31, 84, 178, 0.25)';
  }

  /**
   * Get container stroke width.
   */
  protected getContainerStrokeWidth(container: ContainerConfig): number {
    if (container.type === 'label') return 0;
    if (container.state === 'highlight') return 3;
    if (container.type === 'dsp-edge' || container.type === 'dsp-cloud') return 2;
    return 1;
  }

  /**
   * Resolve icon key to asset path using the icon registry.
   */
  protected resolveIconPath(iconKey: IconKey | undefined): string {
    return getIconPath(iconKey);
  }

  /**
   * Calculate connection path between two containers.
   */
  protected getConnectionPath(conn: ConnectionConfig): string {
    const fromContainer = this.containers.find((c) => c.id === conn.fromId);
    const toContainer = this.containers.find((c) => c.id === conn.toId);

    if (!fromContainer || !toContainer) return '';

    const fromPoint = this.getAnchorPoint(fromContainer, conn.fromSide || 'bottom');
    const toPoint = this.getAnchorPoint(toContainer, conn.toSide || 'top');

    // Create orthogonal path (dogleg)
    return this.createOrthogonalPath(fromPoint, toPoint, conn.fromSide || 'bottom', conn.toSide || 'top');
  }

  /**
   * Get anchor point for a container.
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
      default:
        return { x: x + width / 2, y: y + height };
    }
  }

  /**
   * Create orthogonal path between two points.
   */
  private createOrthogonalPath(from: Point, to: Point, fromSide: AnchorSide, toSide: AnchorSide): string {
    const midY = (from.y + to.y) / 2;
    const midX = (from.x + to.x) / 2;

    // Simple routing based on connection direction
    if (fromSide === 'bottom' && toSide === 'top') {
      // Vertical connection
      return `M ${from.x} ${from.y} L ${from.x} ${midY} L ${to.x} ${midY} L ${to.x} ${to.y}`;
    } else if (fromSide === 'right' && toSide === 'left') {
      // Horizontal connection
      return `M ${from.x} ${from.y} L ${midX} ${from.y} L ${midX} ${to.y} L ${to.x} ${to.y}`;
    } else if (fromSide === 'left' && toSide === 'right') {
      // Reverse horizontal
      return `M ${from.x} ${from.y} L ${midX} ${from.y} L ${midX} ${to.y} L ${to.x} ${to.y}`;
    }

    // Default: direct line
    return `M ${from.x} ${from.y} L ${to.x} ${to.y}`;
  }

  /**
   * Handle container click for actions/URL navigation.
   */
  protected onContainerClick(container: ContainerConfig): void {
    // Check if container has a direct URL configured
    if (container.url) {
      this.actionTriggered.emit({ id: container.id, url: container.url });
      return;
    }

    // Fall back to checking view actions for legacy support
    const layer = this.view.architecture.find((l) => l.id === container.id);
    if (layer?.actionId) {
      const action = this.view.actions.find((a) => a.id === layer.actionId);
      if (action) {
        this.actionTriggered.emit({ id: action.id, url: action.url });
      }
    }
  }

  /**
   * Handle keyboard events on containers.
   */
  protected onContainerKeydown(event: KeyboardEvent, container: ContainerConfig): void {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      this.onContainerClick(container);
    }
  }

  /**
   * TrackBy function for containers.
   */
  protected containerTrackBy(_: number, container: ContainerConfig): string {
    return container.id;
  }

  /**
   * TrackBy function for connections.
   */
  protected connectionTrackBy(_: number, conn: ConnectionConfig): string {
    return conn.id;
  }

  /**
   * TrackBy function for function icons.
   */
  protected iconTrackBy(index: number): number {
    return index;
  }
}
