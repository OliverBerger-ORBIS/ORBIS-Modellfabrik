import { CommonModule } from '@angular/common';
import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  EventEmitter,
  HostListener,
  Input,
  OnDestroy,
  OnInit,
  Output,
} from '@angular/core';
import type { DspDetailView, DspArchitectureLayer } from '../../tabs/configuration-detail.types';
import { getIconPath, type IconKey } from '../../assets/icon-registry';
import { ModuleNameService } from '../../services/module-name.service';
import type {
  ContainerConfig,
  ConnectionConfig,
  StepConfig,
  Point,
  AnchorSide,
} from '../dsp-animation/types';
import {
  createDiagramConfig,
  VIEWBOX_WIDTH,
  VIEWBOX_HEIGHT,
} from '../dsp-animation/layout.config';

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
  protected readonly minZoom = 0.6;
  protected readonly maxZoom = 1.6;
  protected readonly zoomStep = 0.1;
  private readonly zoomStorageKey = 'dsp-architecture-zoom';

  // Accordion state for Edge and Management Cockpit panels
  protected expandedPanels = new Set<string>();

  // ViewBox dimensions
  protected readonly viewBoxWidth = VIEWBOX_WIDTH;
  protected readonly viewBoxHeight = VIEWBOX_HEIGHT;

  // Responsive ViewBox dimensions
  protected dynamicViewBoxWidth = VIEWBOX_WIDTH;
  protected dynamicViewBoxHeight = VIEWBOX_HEIGHT;
  private readonly heroModeBreakpoint = 1000; // < 1000px = Hero-Modus
  private readonly heroModeWidth = 960; // Hero mode viewport width (960px for OBS)

  // i18n labels - English default with translation keys
  protected readonly title = $localize`:@@dspArchTitle:DISTRIBUTED SHOP FLOOR PROCESSING (DSP)`;
  protected readonly subtitle = $localize`:@@dspArchSubtitle:Reference Architecture`;
  protected readonly labelBusinessProcesses = $localize`:@@dspArchLabelBusiness:Business Processes`;
  protected readonly labelDsp = $localize`:@@dspArchLabelDsp:DSP`;
  protected readonly labelShopfloor = $localize`:@@dspArchLabelShopfloor:Shopfloor`;
  protected readonly labelOnPremise = $localize`:@@dspArchLabelOnPremise:On Premise`;
  protected readonly labelCloud = $localize`:@@dspArchLabelCloud:Cloud`;
  protected readonly labelDevices = $localize`:@@dspArchLabelDevices:Devices`;  // Label at bottom, centered
  protected readonly labelSystems = $localize`:@@dspArchLabelSystems:Systems`;  // Label at bottom, centered
  protected readonly labelSmartfactoryDashboard = $localize`:@@dspArchLabelUX:SmartFactory\nDashboard`;  // Two-line label
  protected readonly btnPrev = $localize`:@@dspArchPrev:Previous`;
  protected readonly btnNext = $localize`:@@dspArchNext:Next`;
  protected readonly btnAutoPlay = $localize`:@@dspArchAutoPlay:Auto Play`;
  protected readonly btnStopPlay = $localize`:@@dspArchStopPlay:Stop`;
  protected readonly zoomOutLabel = $localize`:@@shopfloorPreviewZoomOut:Zoom out`;
  protected readonly zoomInLabel = $localize`:@@shopfloorPreviewZoomIn:Zoom in`;
  protected readonly resetZoomLabel = $localize`:@@shopfloorPreviewResetZoom:Reset zoom`;

  // Step labels (13 steps now with buffering)
  protected readonly stepLabels = [
    $localize`:@@dspArchStep1:Shopfloor Devices`,
    $localize`:@@dspArchStep2:Shopfloor Systems`,
    $localize`:@@dspArchStep3:DSP Edge Core`,
    $localize`:@@dspArchStep4:Connectivity`,
    $localize`:@@dspArchStep5:Digital Twin`,
    $localize`:@@dspArchStep6:Process Logic`,
    $localize`:@@dspArchStep7:Edge Analytics`,
    $localize`:@@dspArchStep7a:Buffering`,
    $localize`:@@dspArchStep8:Shopfloor ↔ Edge`,
    $localize`:@@dspArchStep9:Management Cockpit`,
    $localize`:@@dspArchStep10:Business Integration`,
    $localize`:@@dspArchStep11:SmartFactory Dashboard`,
    $localize`:@@dspArchStep12:Autonomous & Adaptive Enterprise`,
    $localize`:@@dspArchStep13:Complete DSP Architecture`,
  ];

  // Container labels from view
  protected readonly containerLabels: Record<string, string> = {};

  constructor(
    private readonly cdr: ChangeDetectorRef,
    private readonly moduleNameService: ModuleNameService
  ) {}

  ngOnInit(): void {
    this.initializeDiagram();
    this.initializeLabelsFromView();
    this.initializeUrlsFromView();
    this.calculateResponsiveViewBox();
  }

  ngOnDestroy(): void {
    this.stopAutoPlay();
  }

  /**
   * Handle window resize events to recalculate responsive ViewBox.
   */
  @HostListener('window:resize', ['$event'])
  onResize(): void {
    this.calculateResponsiveViewBox();
  }

  /**
   * Calculate responsive viewBox dimensions based on viewport width.
   * Hero mode (< 1000px): Scale down to 960px width
   * Landscape mode (>= 1000px): Use full 1200px width
   */
  private calculateResponsiveViewBox(): void {
    const viewportWidth = window.innerWidth;
    
    if (viewportWidth < this.heroModeBreakpoint) {
      // Hero mode: Scale ViewBox to 960px
      const scaleFactor = this.heroModeWidth / VIEWBOX_WIDTH; // 960 / 1200 = 0.8
      this.dynamicViewBoxWidth = this.heroModeWidth;
      this.dynamicViewBoxHeight = VIEWBOX_HEIGHT * scaleFactor;
    } else {
      // Landscape mode: Use full width
      this.dynamicViewBoxWidth = VIEWBOX_WIDTH;
      this.dynamicViewBoxHeight = VIEWBOX_HEIGHT;
    }
    
    this.cdr.markForCheck();
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

    // Replace hardcoded module labels with i18n names
    this.containers.forEach((container) => {
      // Check if this is a shopfloor device container with a hardcoded module label
      if (container.id?.startsWith('shopfloor-device-') && container.label) {
        const moduleId = container.label.toUpperCase();
        // Only replace if it's a known module (DRILL, HBW, MILL, AIQS, DPS, CHRG)
        if (['DRILL', 'HBW', 'MILL', 'AIQS', 'DPS', 'CHRG'].includes(moduleId)) {
          container.label = this.moduleNameService.getModuleFullName(moduleId);
        }
      }
    });

    // Load saved zoom from localStorage
    this.loadSavedZoom();
    
    // Apply initial step (start from step 1 to show overlay immediately)
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

    // Map business processes - map IDs for configuration tab compatibility
    this.view.businessProcesses.forEach((bp) => {
      // Use ID directly for labels
      this.containerLabels[bp.id] = bp.label;
      // Also map backwards for configuration tab compatibility
      const mappedId = this.mapBusinessProcessId(bp.id);
      if (mappedId !== bp.id) {
        this.containerLabels[mappedId] = bp.label;
      }
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
   * Initialize container URLs from DspDetailView (settings-based).
   */
  private initializeUrlsFromView(): void {
    // Update container URLs from view settings
    this.containers.forEach((container) => {
      switch (container.id) {
        case 'edge':
          container.url = this.view.edgeUrl;
          break;
        case 'management':
          container.url = this.view.managementUrl;
          break;
        case 'bp-analytics':
          container.url = this.view.analyticsUrl;
          break;
        case 'ux':
          container.url = this.view.smartfactoryDashboardUrl;
          break;
      }
    });
  }

  /**
   * Map business process ID from view to container ID.
   */
  private mapBusinessProcessId(viewId: string): string {
    const mapping: Record<string, string> = {
      'shopfloor': 'erp-application',
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
   * Get wrapped label lines for device containers based on container width.
   * Automatically wraps long labels to fit within the container width.
   */
  protected getWrappedLabelLines(container: ContainerConfig): string[] {
    const label = this.containerLabels[container.id || ''] || container.label || '';
    if (!label) {
      return [];
    }

    // Only wrap for device containers
    if (container.type !== 'device') {
      return [label];
    }

    // Estimate character width (approximate: fontSize * 0.6 for average character width)
    const fontSize = container.fontSize || 10;
    const charWidth = fontSize * 0.6;
    const maxWidth = container.width - 16; // Leave some padding (8px on each side)
    const maxCharsPerLine = Math.floor(maxWidth / charWidth);

    // If label fits on one line, return as is
    if (label.length <= maxCharsPerLine) {
      return [label];
    }

    // Split label into words
    const words = label.split(/\s+/);
    const lines: string[] = [];
    let currentLine = '';

    for (const word of words) {
      const testLine = currentLine ? `${currentLine} ${word}` : word;
      
      // If adding this word would exceed the line length, start a new line
      if (testLine.length > maxCharsPerLine && currentLine) {
        lines.push(currentLine);
        currentLine = word;
      } else {
        currentLine = testLine;
      }
    }

    // Add the last line
    if (currentLine) {
      lines.push(currentLine);
    }

    // Limit to 2 lines maximum
    return lines.slice(0, 2);
  }

  /**
   * Check if a label should be wrapped (for device containers with long labels).
   */
  protected shouldWrapLabel(container: ContainerConfig): boolean {
    if (container.type !== 'device') {
      return false;
    }
    const label = this.containerLabels[container.id || ''] || container.label || '';
    if (!label) {
      return false;
    }
    const wrappedLines = this.getWrappedLabelLines(container);
    return wrappedLines.length > 1;
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
        // For device containers with wrapped labels, adjust Y position to accommodate 2 lines
        if (container.type === 'device' && this.shouldWrapLabel(container)) {
          return container.height - 20; // More space for 2 lines
        }
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

  // Layer IDs that should use larger fonts (18px vs 14px)
  protected readonly largerFontLayerIds = new Set(['layer-business', 'layer-dsp']);

  /**
   * Get font size for layer labels.
   * Business Process and DSP layers use 18px, others use 14px.
   */
  protected getLayerFontSize(containerId: string): number {
    return this.largerFontLayerIds.has(containerId) ? 18 : 18;
  }

  /**
   * Apply a specific animation step.
   */
  /**
   * Check if function icons should be shown in the current step.
   */
  protected shouldShowFunctionIcons(): boolean {
    const step = this.steps[this.currentStepIndex];
    // Default to true unless explicitly set to false
    return step?.showFunctionIcons !== false;
  }

  /**
   * Check if a specific function icon should be highlighted in the current step.
   */
  protected isFunctionIconHighlighted(iconKey: string): boolean {
    const step = this.steps[this.currentStepIndex];
    return step?.highlightedFunctionIcons?.includes(iconKey) ?? false;
  }

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
        // Loop back to step 1 when reaching the last step
        this.applyStepInternal(0);
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
    this.saveZoom();
  }

  /**
   * Zoom out.
   */
  protected zoomOut(): void {
    this.zoom = Math.max(this.minZoom, this.zoom - this.zoomStep);
    this.saveZoom();
  }

  /**
   * Reset zoom to 100%.
   */
  protected resetZoom(): void {
    this.zoom = 1;
    this.clearSavedZoom();
  }

  /**
   * Load saved zoom from localStorage.
   */
  private loadSavedZoom(): void {
    try {
      const saved = localStorage.getItem(this.zoomStorageKey);
      if (saved) {
        const zoom = parseFloat(saved);
        if (!Number.isNaN(zoom) && zoom >= this.minZoom && zoom <= this.maxZoom) {
          this.zoom = zoom;
        }
      }
    } catch (error) {
      // Ignore localStorage errors
    }
  }

  /**
   * Save current zoom to localStorage.
   */
  private saveZoom(): void {
    try {
      localStorage.setItem(this.zoomStorageKey, this.zoom.toString());
    } catch (error) {
      // Ignore localStorage errors
    }
  }

  /**
   * Clear saved zoom from localStorage.
   */
  private clearSavedZoom(): void {
    try {
      localStorage.removeItem(this.zoomStorageKey);
    } catch (error) {
      // Ignore localStorage errors
    }
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
    // Use gradient for shopfloor device containers
    if (container.type === 'device' && container.id?.startsWith('shopfloor-')) {
      return 'url(#shopfloor-gradient)';
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
      if (container.type === 'dsp-edge') return '#009681';  // Solution Petrol (keep as hex for SVG)
      if (container.type === 'dsp-cloud') return '#009681';  // Solution Petrol (keep as hex for SVG)
      if (container.type === 'ux') return '#009681';  // Solution Petrol (keep as hex for SVG)
      if (container.type === 'business') return '#ff9900';
      return '#154194'; // ORBIS Blue Strong (keep as hex for SVG)
    }
    return container.borderColor || 'rgba(22, 65, 148, 0.25)'; // ORBIS Blue Strong RGB
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
   * Handle container click for URL navigation or legacy action-based navigation.
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

  // ========== Accordion Methods ==========

  /**
   * Check if an accordion panel is expanded.
   */
  protected isExpanded(panelId: string): boolean {
    return this.expandedPanels.has(panelId);
  }

  /**
   * Toggle an accordion panel.
   */
  protected togglePanel(panelId: string): void {
    if (this.expandedPanels.has(panelId)) {
      this.expandedPanels.delete(panelId);
    } else {
      this.expandedPanels.add(panelId);
    }
    this.cdr.markForCheck();
  }

  /**
   * Get architecture layer by ID.
   */
  protected getLayerById(layerId: string): DspArchitectureLayer | undefined {
    return this.view.architecture.find((layer) => layer.id === layerId);
  }

  /**
   * Trigger an action with URL (for accordion buttons).
   */
  protected triggerAccordionAction(actionId: string, url: string): void {
    if (url) {
      this.actionTriggered.emit({ id: actionId, url });
    }
  }

  /**
   * TrackBy function for capabilities.
   */
  protected capabilityTrackBy(index: number): number {
    return index;
  }
}
