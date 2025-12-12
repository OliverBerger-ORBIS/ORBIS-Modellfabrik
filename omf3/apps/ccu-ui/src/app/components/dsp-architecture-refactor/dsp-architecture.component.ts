import { CommonModule } from '@angular/common';
import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  EventEmitter,
  Input,
  OnChanges,
  OnDestroy,
  OnInit,
  Output,
  SimpleChanges,
} from '@angular/core';
import { getIconPath, type IconKey } from '../../assets/icon-registry';
import type { ContainerConfig, ConnectionConfig, StepConfig, Point, AnchorSide, ViewMode, FunctionIconConfig } from './types';
import {
  createDiagramConfig,
  VIEWBOX_WIDTH,
  VIEWBOX_HEIGHT,
} from './layout.config';
import { ModuleNameService } from '../../services/module-name.service';

/**
 * DspArchitectureRefactorComponent - Refactored animated SVG-based architecture diagram.
 *
 * Matches the existing DSP architecture component with continuous layer backgrounds,
 * grid-based positioning, multi-view mode support (Functional, Component, Deployment),
 * and animation steps for each view.
 */
@Component({
  standalone: true,
  selector: 'app-dsp-architecture-refactor',
  imports: [CommonModule],
  templateUrl: './dsp-architecture.component.html',
  styleUrl: './dsp-architecture.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspArchitectureRefactorComponent implements OnInit, OnChanges, OnDestroy {
  @Input() viewMode: ViewMode = 'functional';
  @Output() actionTriggered = new EventEmitter<{ id: string; url: string }>();

  // Diagram configuration
  protected containers: ContainerConfig[] = [];
  protected connections: ConnectionConfig[] = [];
  protected steps: StepConfig[] = [];

  // Animation state
  protected currentStepIndex = 0;
  protected isAutoPlaying = false;
  private autoPlayInterval: ReturnType<typeof setInterval> | null = null;
  protected loopToStart = true;

  // Zoom state
  protected zoom = 1;
  protected readonly minZoom = 0.6;
  protected readonly maxZoom = 1.6;
  protected readonly zoomStep = 0.1;
  protected readonly functionIconRadius = 120; // base radius for circular layout
  protected readonly functionIconScale = 1.0;
  protected readonly functionIconHighlightScale = 1.6;
  private revealedFunctionIcons = new Set<IconKey>();

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
  protected readonly labelEdge = $localize`:@@dspArchLabelEdge:Edge`;
  protected readonly labelManagementCockpit = $localize`:@@dspArchLabelManagement:Management\nCockpit`;
  protected readonly btnPrev = $localize`:@@dspArchPrev:Previous`;
  protected readonly btnNext = $localize`:@@dspArchNext:Next`;
  protected readonly btnAutoPlay = $localize`:@@dspArchAutoPlay:Auto Play`;
  protected readonly btnStopPlay = $localize`:@@dspArchStopPlay:Stop`;
  protected readonly zoomOutLabel = $localize`:@@shopfloorPreviewZoomOut:Zoom out`;
  protected readonly zoomInLabel = $localize`:@@shopfloorPreviewZoomIn:Zoom in`;
  protected readonly resetZoomLabel = $localize`:@@shopfloorPreviewResetZoom:Reset zoom`;

  // Container labels
  protected readonly containerLabels: Record<string, string> = {
    'layer-bp': this.labelBusinessProcesses,
    'layer-dsp': this.labelDsp,
    'layer-sf': this.labelShopfloor,
    'sf-systems-group': this.labelSystems,
    'sf-devices-group': this.labelDevices,
    'dsp-label-onpremise': this.labelOnPremise,
    'dsp-label-cloud': this.labelCloud,
    'dsp-ux': this.labelSmartfactoryDashboard,
    'dsp-edge': this.labelEdge,
    'dsp-mc': this.labelManagementCockpit,
    'bp-mes': $localize`:@@dspArchLabelMESApp:MES Applications`,
    'bp-erp': $localize`:@@dspArchLabelERP:ERP Applications`,
    'bp-cloud': $localize`:@@dspArchLabelCloudApps:Cloud\nApplications`,
    'bp-analytics': $localize`:@@dspArchLabelAnalytics:Analytical\nApplications`,
    'bp-data-lake': $localize`:@@dspArchLabelDataLake:Data Lake`,
    'sf-system-bp': $localize`:@@dspArchLabelMES:MES`,
    'sf-system-warehouse': $localize`:@@dspArchLabelWarehouse:Warehouse`,
    'sf-system-factory': $localize`:@@dspArchLabelFactory:Factory`,
    'sf-system-fts': $localize`:@@dspArchLabelFTS:AGV\nSystem`,
    // Device labels with manual break hints (" / ") for consistent wrapping
    'sf-device-mill': $localize`:@@deviceMILL:Fräs / station`,
    'sf-device-drill': $localize`:@@deviceDRILL:Bohr / station`,
    'sf-device-aiqs': $localize`:@@deviceAIQS:KI- / Qualitäts / station`,
    'sf-device-hbw': $localize`:@@deviceHBW:Hochregal / lager`,
    'sf-device-dps': $localize`:@@deviceDPS:Waren Ein- / und Ausgang`,
    'sf-device-chrg': $localize`:@@deviceCHRG:Lade- / station`,
    'sf-device-conveyor': $localize`:@@deviceConveyor:Förder- / station`,
    'sf-device-stone-oven': $localize`:@@deviceStoneOven:Ofen / station`,
    // DSP Edge Components
    'edge-comp-disc': $localize`:@@edgeComponentDisc:DISC`,
    'edge-comp-event-bus': $localize`:@@edgeComponentEventBus:Event Bus`,
    'edge-comp-app-server': $localize`:@@edgeComponentAppServer:App Server`,
    'edge-comp-router': $localize`:@@edgeComponentRouter:Router`,
    'edge-comp-agent': $localize`:@@edgeComponentAgent:Agent`,
    'edge-comp-log-server': $localize`:@@edgeComponentLogServer:Log Server`,
    'edge-comp-disi': $localize`:@@edgeComponentDisi:DISI`,
    'edge-comp-database': $localize`:@@edgeComponentDatabase:Database`,
  };

  constructor(
    private readonly cdr: ChangeDetectorRef,
    private readonly moduleNameService: ModuleNameService
  ) {}

  ngOnInit(): void {
    this.loadConfiguration();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['viewMode'] && !changes['viewMode'].isFirstChange()) {
      this.loadConfiguration();
    }
  }

  ngOnDestroy(): void {
    this.stopAutoPlay();
  }

  /**
   * Load diagram configuration based on current view mode
   */
  private loadConfiguration(): void {
    const config = createDiagramConfig(this.viewMode);
    this.containers = config.containers;
    this.connections = config.connections;
    this.steps = config.steps;
    this.revealedFunctionIcons = new Set<IconKey>();
    this.initializeModuleLabels();
    this.currentStepIndex = 0; // Reset to first step on configuration change
    this.applyStep(0);
    this.cdr.markForCheck();
  }

  /**
   * Replace shopfloor device labels with injected module names.
   */
  private initializeModuleLabels(): void {
    const moduleMap: Record<string, string> = {
      'sf-device-mill': 'MILL',
      'sf-device-drill': 'DRILL',
      'sf-device-aiqs': 'AIQS',
      'sf-device-hbw': 'HBW',
      'sf-device-dps': 'DPS',
      'sf-device-chrg': 'CHRG',
    };

    Object.entries(moduleMap).forEach(([id, moduleId]) => {
      const name = this.moduleNameService.getModuleFullName(moduleId);
      if (name) {
        this.containerLabels[id] = name;
      }
    });
  }

  /**
   * Check if container should be visible
   */
  protected isContainerVisible(container: ContainerConfig): boolean {
    return container.state !== 'hidden';
  }

  /**
   * Check if container should be highlighted
   */
  protected isContainerHighlighted(container: ContainerConfig): boolean {
    return container.state === 'highlight';
  }

  /**
   * Check if connection should be visible
   */
  protected isConnectionVisible(connection: ConnectionConfig): boolean {
    return connection.state !== 'hidden';
  }

  /**
   * Check if connection should be highlighted
   */
  protected isConnectionHighlighted(connection: ConnectionConfig): boolean {
    return connection.state === 'highlight';
  }

  /**
   * Detect edge-component connections (short arrows, straight lines)
   */
  protected isEcConnection(connection: ConnectionConfig): boolean {
    return connection.id.startsWith('conn-ec-');
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
    if (container.type === 'label') return 'transparent';
    if (container.type === 'pipeline' && container.backgroundColor) return container.backgroundColor;
    // Use gradient for shopfloor devices
    if (container.type === 'device' && container.id?.startsWith('sf-')) {
      return 'url(#shopfloor-gradient)';
    }
    return container.backgroundColor || '#ffffff';
  }

  /**
   * Get container stroke color
   */
  protected getContainerStroke(container: ContainerConfig): string {
    if (container.type === 'label') return 'transparent';
    if (container.type === 'pipeline') return container.borderColor || '#7f8da5';
    if (this.isContainerHighlighted(container)) {
      return '#ff9900'; // Highlight color
    }
    return container.borderColor || '#cccccc';
  }

  /**
   * Get container stroke width
   */
  protected getContainerStrokeWidth(container: ContainerConfig): number {
    if (container.type === 'label') return 0;
    if (container.type === 'pipeline') return container.state === 'highlight' ? 2.5 : 2;
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
    const fromConfig = this.containerLabels[containerId];
    if (fromConfig) return fromConfig;
    const container = this.containers.find((c) => c.id === containerId);
    return container?.label || '';
  }

  /**
   * Get multi-line label
   */
  protected getMultilineLabel(containerId: string): string[] {
    const label = this.getContainerLabel(containerId);
    if (containerId === 'layer-bp') return [this.labelBusinessProcesses];
    if (containerId === 'layer-dsp') return [this.labelDsp];
    if (containerId === 'layer-sf') return [this.labelShopfloor];
    if (containerId === 'dsp-label-onpremise') return [this.labelOnPremise];
    if (containerId === 'dsp-label-cloud') return [this.labelCloud];
    if (containerId === 'sf-devices-group') return [this.labelDevices];
    if (containerId === 'sf-systems-group') return [this.labelSystems];
    if (containerId === 'dsp-ux') return this.labelSmartfactoryDashboard.split('\n');
    if (containerId === 'dsp-edge') return [this.labelEdge];
    if (containerId === 'dsp-mc') return this.labelManagementCockpit.split('\n');
    return label.split('\n');
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
    // Special: pipeline labels centered vertically
    if (container.type === 'pipeline') {
      return container.height / 2;
    }
    // Position at bottom center for most containers
    if (container.labelPosition === 'bottom-center') {
      return container.height - 8;
    }
    if (container.labelPosition === 'top-center') {
      // For DSP containers, align with logo (at same height as 48px logo center)
      if (container.type === 'ux' || container.type === 'dsp-edge' || container.type === 'dsp-cloud') {
        return 36; // Logo is at y=12, height=48, so center is at 12+24=36
      }
      return 20;
    }
    return container.height / 2;
  }

  /**
   * Resolve secondary logos list (supports single legacy key)
   */
  protected getSecondaryLogos(container: ContainerConfig): IconKey[] {
    if (container.secondaryLogos && container.secondaryLogos.length > 0) {
      return container.secondaryLogos;
    }
    if (container.secondaryLogoIconKey) {
      return [container.secondaryLogoIconKey];
    }
    return [];
  }

  /**
   * Secondary logo size (supporting larger ORBIS top-left case)
   */
  protected getSecondaryLogoSize(container: ContainerConfig): number {
    const base = container.type === 'dsp-cloud' ? 36 : 28;
    const isTopLeft = container.secondaryLogoPosition === 'top-left';
    return isTopLeft ? base * 1.5 : base;
  }

  /**
   * Secondary logo X position (supports left placement & horizontal stacking)
   */
  protected getSecondaryLogoX(container: ContainerConfig, index: number): number {
    const size = this.getSecondaryLogoSize(container);
    const gap = 6;
    const margin = 8;
    const isTopLeft = container.secondaryLogoPosition === 'top-left';
    if (isTopLeft) {
      // stack left-to-right starting at margin
      return margin + index * (size + gap);
    }
    // right-aligned, stacking right-to-left
    return container.width - margin - size - index * (size + gap);
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
    if (!label) return [];

    // Approximate character capacity based on width and font size
    const fontSize = container.fontSize || 12;
    const maxCharsPerLine = Math.max(8, Math.floor((container.width - 12) / (fontSize * 0.58)));
    const maxLines = 3;

    // Allow manual break hints using " / " (locale-safe) and hyphen-aware splitting
    const hinted = label.split(' / ').join('\n');
    const dashExpanded: string[] = [];
    hinted.split(/\s+/).forEach((token) => {
      if (token.includes('-')) {
        const parts = token.split('-').filter(Boolean);
        parts.forEach((p, idx) => {
          dashExpanded.push(p);
          if (idx < parts.length - 1) dashExpanded.push('-');
        });
      } else if (token.includes('\n')) {
        token.split('\n').forEach((t) => dashExpanded.push(t));
      } else {
        dashExpanded.push(token);
      }
    });

    const words = dashExpanded;
    const lines: string[] = [];
    let current = '';

    for (const word of words) {
      const tentative = current ? `${current} ${word}` : word;
      if (tentative.length > maxCharsPerLine && current) {
        lines.push(current);
        current = word;
        if (lines.length >= maxLines - 1) {
          break;
        }
      } else {
        current = tentative;
      }
    }
    if (current && lines.length < maxLines) lines.push(current);

    // If still too long and only one token (no spaces), hard-wrap
    if (lines.length === 1 && lines[0].length > maxCharsPerLine) {
      const token = lines[0];
      if (token.toLowerCase().endsWith('station') && token.length > maxCharsPerLine) {
        const stem = token.slice(0, Math.max(3, token.length - 7));
        const suffix = 'station';
        lines.splice(0, 1, stem, suffix);
        return lines.slice(0, maxLines);
      }
      const hard1 = token.slice(0, maxCharsPerLine);
      const hard2 = token.slice(maxCharsPerLine, maxCharsPerLine * 2);
      const hard3 = token.slice(maxCharsPerLine * 2);
      const parts = [hard1, hard2, hard3].filter(Boolean);
      lines.splice(0, 1, ...parts);
    }

    // Limit to maxLines to keep layout stable
    return lines.slice(0, maxLines);
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

    const isEc = connection.id.startsWith('conn-ec-');
    const isInternalEc = isEc && fromContainer.id?.startsWith('edge-comp-') && toContainer.id?.startsWith('edge-comp-');

    // Use center anchors for internal edge-comp connections, otherwise side anchors
    const fromCenter = { x: fromContainer.x + fromContainer.width / 2, y: fromContainer.y + fromContainer.height / 2 };
    const toCenter = { x: toContainer.x + toContainer.width / 2, y: toContainer.y + toContainer.height / 2 };

    if (isInternalEc) {
      const from = this.getRectEdgePoint(fromCenter, toCenter, fromContainer);
      const to = this.getRectEdgePoint(toCenter, fromCenter, toContainer);
      return `M ${from.x} ${from.y} L ${to.x} ${to.y}`;
    }

    const from = this.getAnchorPoint(fromContainer, connection.fromSide || 'bottom');
    const to = this.getAnchorPoint(toContainer, connection.toSide || 'top');

    // Default L-shaped path
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
    if (this.isEcConnection(connection)) {
      classes.push('connection--ec');
    }
    return classes.join(' ');
  }

  /**
   * Device icon size helper (shrink edge-comp icons)
   */
  protected getDeviceIconSize(container: ContainerConfig): number {
    if (container.id?.startsWith('edge-comp-')) {
      return 56; // ~20% kleiner als 70
    }
    return 70;
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
      default:
        // Center fallback
        return { x: x + width / 2, y: y + height / 2 };
    }
  }

  /**
   * Get point on rectangle edge from center towards target point.
   */
  private getRectEdgePoint(fromCenter: Point, toCenter: Point, container: ContainerConfig): Point {
    const dx = toCenter.x - fromCenter.x;
    const dy = toCenter.y - fromCenter.y;
    const halfW = container.width / 2;
    const halfH = container.height / 2;

    if (dx === 0 && dy === 0) {
      return fromCenter;
    }

    const tx = dx !== 0 ? halfW / Math.abs(dx) : Number.POSITIVE_INFINITY;
    const ty = dy !== 0 ? halfH / Math.abs(dy) : Number.POSITIVE_INFINITY;
    const t = Math.min(tx, ty);

    return {
      x: fromCenter.x + dx * t,
      y: fromCenter.y + dy * t,
    };
  }

  /**
   * Build polygon points for pipeline arrow.
   */
  protected getPipelinePoints(container: ContainerConfig): string {
    const w = container.width;
    const h = container.height;
    const tip = Math.max(12, Math.min(28, w * 0.15));
    return `0,0 ${w - tip},0 ${w},${h / 2} ${w - tip},${h} 0,${h} ${tip},${h / 2}`;
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
        if (this.loopToStart) {
          this.applyStep(0);
        } else {
          this.stopAutoPlay();
        }
      }
    }, 3000);
    this.cdr.markForCheck();
  }

  protected toggleLoop(): void {
    this.loopToStart = !this.loopToStart;
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
    const step = this.steps[index];
    if (!step) {
      return;
    }

    // reset progressive reveal when we are before functional steps (steps 1-3)
    if (index < 3) {
      this.revealedFunctionIcons = new Set<IconKey>();
    }

    (step.highlightedFunctionIcons || []).forEach((key) => this.revealedFunctionIcons.add(key as IconKey));

    // Update container states for visibility/highlight
    this.containers.forEach((container) => {
      if (step.visibleContainerIds.includes(container.id)) {
        container.state = step.highlightedContainerIds.includes(container.id) ? 'highlight' : 'normal';
      } else {
        container.state = 'hidden';
      }
    });

    // Update connection states for visibility/highlight
    this.connections.forEach((connection) => {
      if (step.visibleConnectionIds.includes(connection.id)) {
        connection.state = step.highlightedConnectionIds.includes(connection.id) ? 'highlight' : 'normal';
      } else {
        connection.state = 'hidden';
      }
    });

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

  /**
   * Position function icons on a circle (start at 180° = bottom)
   */
  protected getFunctionIconPosition(
    container: ContainerConfig,
    index: number,
    icon: FunctionIconConfig
  ): { x: number; y: number } {
    const total = container.functionIcons?.length ?? 0; // keep positions stable across reveal
    if (total === 0) {
      return { x: container.width / 2, y: container.height / 2 };
    }
    const startDeg = 90; // start at 90° (clockwise)
    const step = 360 / total;
    const angleRad = ((startDeg + index * step) * Math.PI) / 180;
    const cx = container.width / 2;
    const cy = container.height / 2;
    const maxRadius = Math.max(
      0,
      Math.min(this.functionIconRadius, Math.min(container.width, container.height) / 2 - icon.size / 2 - 4)
    );
    return {
      x: cx + maxRadius * Math.cos(angleRad) - icon.size / 2,
      y: cy + maxRadius * Math.sin(angleRad) - icon.size / 2,
    };
  }

  protected getFunctionIconSize(iconKey: IconKey): number {
    const base = 48; // default size used in config (60 not needed here)
    const factor = this.isFunctionIconHighlighted(iconKey) ? this.functionIconHighlightScale : this.functionIconScale;
    return base * factor;
  }

  protected getVisibleFunctionIcons(container: ContainerConfig): FunctionIconConfig[] {
    if (!container.functionIcons || !this.shouldShowFunctionIcons()) {
      return [];
    }
    if (this.viewMode !== 'functional') {
      return container.functionIcons;
    }
    return container.functionIcons.filter((fi) => this.revealedFunctionIcons.has(fi.iconKey));
  }

  protected isFunctionIconVisible(iconKey: IconKey, container: ContainerConfig): boolean {
    if (!container.functionIcons || !this.shouldShowFunctionIcons()) return false;
    if (this.viewMode !== 'functional') return true;
    return this.revealedFunctionIcons.has(iconKey);
  }
}
