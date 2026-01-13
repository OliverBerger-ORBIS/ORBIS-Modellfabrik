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
import { ORBIS_COLORS } from '../../assets/color-palette';
import type { ContainerConfig, ConnectionConfig, StepConfig, Point, AnchorSide, ViewMode, FunctionIconConfig } from './types';
import {
  createDiagramConfig,
  VIEWBOX_WIDTH,
  VIEWBOX_HEIGHT,
} from './layout.config';
import { ModuleNameService } from '../../services/module-name.service';
import { ExternalLinksService } from '../../services/external-links.service';
import type { CustomerDspConfig } from './configs/types';

/**
 * DspAnimationComponent - Animated SVG-based architecture diagram.
 *
 * Matches the existing DSP architecture component with continuous layer backgrounds,
 * grid-based positioning, multi-view mode support (Functional, Component, Deployment),
 * and animation steps for each view.
 */
@Component({
  standalone: true,
  selector: 'app-dsp-animation',
  imports: [CommonModule],
  templateUrl: './dsp-animation.component.html',
  styleUrl: './dsp-animation.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspAnimationComponent implements OnInit, OnChanges, OnDestroy {
  @Input() viewMode: ViewMode = 'functional';
  @Input() initialStep?: number; // Optional: Start step (0-based). If undefined, starts at 0. Use -1 for last step.
  @Input() customerConfig?: CustomerDspConfig; // Optional: Customer-specific configuration for labels and icons
  @Output() actionTriggered = new EventEmitter<{ id: string; url: string }>();

  // Diagram configuration
  protected containers: ContainerConfig[] = [];
  protected connections: ConnectionConfig[] = [];
  protected steps: StepConfig[] = [];
  
  // Sorted connections for rendering (highlighted connections last)
  protected get sortedConnections(): ConnectionConfig[] {
    const currentStep = this.steps[this.currentStepIndex];
    if (!currentStep) {
      return this.connections;
    }
    
    // Sort: non-highlighted first, highlighted last (so highlighted render on top)
    return [...this.connections].sort((a, b) => {
      const aHighlighted = currentStep.highlightedConnectionIds.includes(a.id);
      const bHighlighted = currentStep.highlightedConnectionIds.includes(b.id);
      
      if (aHighlighted && !bHighlighted) return 1; // a goes after b
      if (!aHighlighted && bHighlighted) return -1; // a goes before b
      return 0; // keep original order
    });
  }

  // Animation state
  protected currentStepIndex = 0;
  protected isAutoPlaying = false;
  private autoPlayInterval: ReturnType<typeof setInterval> | null = null;
  protected loopToStart = true;

  // Zoom state
  protected zoom = 1;
  protected readonly minZoom = 0.4;
  protected readonly maxZoom = 1.8;
  
  /**
   * Fine zoom step for zoom levels < 100% (5% increments for precise control)
   */
  private readonly ZOOM_STEP_FINE = 0.05;
  
  /**
   * Coarse zoom step for zoom levels ≥ 100% (10% increments)
   */
  private readonly ZOOM_STEP_COARSE = 0.1;
  
  protected readonly functionIconRadius = 120; // base radius for circular layout
  protected readonly functionIconScale = 1.0;
  protected readonly functionIconHighlightScale = 1.92; // 1.6 * 1.2 = 20% additional enlargement for highlighted function icons
  private revealedFunctionIcons = new Set<IconKey>();

  // ViewBox dimensions
  protected readonly viewBoxWidth = VIEWBOX_WIDTH;
  protected readonly viewBoxHeight = VIEWBOX_HEIGHT;

  // i18n labels
  protected readonly baseTitle = $localize`:@@dspAnimationBaseTitle:DSP Architecture, interactive demonstration of DSP architecture visualisation with multiple views and animation`;
  protected readonly subtitle = $localize`:@@dspAnimationSubtitle:Reference Architecture`;
  
  /**
   * Get dynamic title based on view mode
   */
  protected get title(): string {
    const viewModeLabel = this.getViewModeLabel(this.viewMode);
    // Use template literal for interpolation since $localize doesn't support dynamic interpolation
    return `DSP Architecture ${viewModeLabel}`;
  }
  
  /**
   * Get view mode label for title
   */
  private getViewModeLabel(mode: ViewMode): string {
    switch (mode) {
      case 'functional':
        return $localize`:@@dspAnimationViewModeFunctional:functional view`;
      case 'component':
        return $localize`:@@dspAnimationViewModeComponent:component view`;
      case 'deployment':
        return $localize`:@@dspAnimationViewModeDeployment:deployment view`;
      default:
        return '';
    }
  }
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
    'sf-system-any': $localize`:@@dspArchLabelAnySystem:any System`,
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
    private readonly moduleNameService: ModuleNameService,
    private readonly externalLinksService: ExternalLinksService
  ) {}

  ngOnInit(): void {
    this.loadConfiguration();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if ((changes['viewMode'] && !changes['viewMode'].isFirstChange()) ||
        (changes['initialStep'] && !changes['initialStep'].isFirstChange()) ||
        (changes['customerConfig'] && !changes['customerConfig'].isFirstChange())) {
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
    const config = createDiagramConfig(this.viewMode, this.customerConfig);
    this.containers = config.containers;
    this.connections = config.connections;
    this.steps = config.steps;
    this.revealedFunctionIcons = new Set<IconKey>();
    
    // Apply customer-specific mappings if provided (this sets labels from config)
    if (this.customerConfig) {
      this.applyCustomerMappings(this.customerConfig);
    }
    
    // Initialize module labels AFTER customer mappings (only if no customer config or labels not set)
    // This ensures customer config labels take precedence
    this.initializeModuleLabels();
    
    // Update container URLs from ExternalLinksService
    this.updateContainerUrls();
    
    // Determine initial step index
    let initialStepIndex = 0;
    if (this.initialStep !== undefined) {
      if (this.initialStep === -1) {
        // -1 means last step
        initialStepIndex = this.steps.length - 1;
      } else if (this.initialStep >= 0 && this.initialStep < this.steps.length) {
        initialStepIndex = this.initialStep;
      }
    }
    
    this.currentStepIndex = initialStepIndex;
    this.applyStep(initialStepIndex);
    this.cdr.markForCheck();
  }

  /**
   * Replace shopfloor device labels with injected module names.
   * For FMF customer, maps concrete IDs to module IDs.
   * Only sets labels if they are not already set by customer config.
   */
  private initializeModuleLabels(): void {
    // Only apply module labels for FMF customer (which uses Fischertechnik modules)
    if (!this.customerConfig || this.customerConfig.customerKey !== 'fmf') {
      return;
    }

    // Map FMF's concrete device IDs to module IDs
    const moduleMap: Record<string, string> = {
      'sf-device-mill': 'MILL',
      'sf-device-drill': 'DRILL',
      'sf-device-aiqs': 'AIQS',
      'sf-device-hbw': 'HBW',
      'sf-device-dps': 'DPS',
      'sf-device-chrg': 'CHRG',
    };

    Object.entries(moduleMap).forEach(([id, moduleId]) => {
      // Only set label if it's not already set by customer config
      // Customer config labels take precedence
      if (!this.containerLabels[id]) {
        const name = this.moduleNameService.getModuleFullName(moduleId);
        if (name) {
          this.containerLabels[id] = name;
        }
      }
    });
  }

  /**
   * Apply customer-specific mappings to containers.
   * This allows different customers to have different labels and icons for the same containers.
   * Also hides containers that are not in the customer configuration.
   */
  private applyCustomerMappings(config: CustomerDspConfig): void {
    // Get IDs from customer config for filtering
    const configDeviceIds = new Set(config.sfDevices.map(d => d.id));
    const configSystemIds = new Set(config.sfSystems.map(s => s.id));
    const configBpIds = new Set(config.bpProcesses.map(bp => bp.id));

    this.containers.forEach(container => {
      // Map Shopfloor Devices
      if (container.id.startsWith('sf-device-')) {
        const mapping = config.sfDevices.find(d => d.id === container.id);
        if (mapping) {
          // Update label in containerLabels map
          this.containerLabels[container.id] = mapping.label;
          // Update icon path
          if (mapping.customIconPath) {
            container.logoIconKey = mapping.customIconPath as IconKey;
          } else if (mapping.iconKey.endsWith('-station')) {
            // New semantic key format: use directly (e.g., 'cnc-station' -> 'cnc-station')
            container.logoIconKey = mapping.iconKey as IconKey;
          } else {
            // Legacy format: add generic-device- prefix (e.g., 'cnc' -> 'generic-device-cnc')
            container.logoIconKey = `generic-device-${mapping.iconKey}` as IconKey;
          }
          // Make visible if it was hidden
          if (container.state === 'hidden') {
            container.state = 'normal';
          }
        } else {
          // Hide devices that are not in the customer config
          container.state = 'hidden';
        }
      }
      
      // Map Shopfloor Systems
      if (container.id.startsWith('sf-system-')) {
        const mapping = config.sfSystems.find(s => s.id === container.id);
        if (mapping) {
          this.containerLabels[container.id] = mapping.label;
          if (mapping.customIconPath) {
            container.logoIconKey = mapping.customIconPath as IconKey;
          } else {
            // Map iconKey to correct system icon based on label
            // Mapping by label name for clarity
            const labelLower = mapping.label.toLowerCase();
            if (labelLower.includes('agv')) {
              container.logoIconKey = 'shopfloor-fts' as IconKey; // AGV System = FTS
            } else if (labelLower.includes('any system')) {
              container.logoIconKey = 'shopfloor-systems' as IconKey; // Any System → any-system.svg
            } else if (labelLower.includes('bp system') || labelLower.includes('bp-system')) {
              container.logoIconKey = 'shopfloor-bp' as IconKey; // BP System → bp-system.svg
            } else if (labelLower.includes('warehouse')) {
              container.logoIconKey = 'shopfloor-warehouse' as IconKey; // Warehouse System → warehouse-system.svg
            } else if (mapping.iconKey === 'agv') {
              container.logoIconKey = 'shopfloor-fts' as IconKey; // Fallback: iconKey 'agv'
            } else if (mapping.iconKey.endsWith('-system')) {
              // New semantic key format: use directly (e.g., 'scada-system' -> 'scada-system')
              container.logoIconKey = mapping.iconKey as IconKey;
            } else {
              // Legacy format: add generic-system- prefix (e.g., 'scada' -> 'generic-system-scada')
              container.logoIconKey = `generic-system-${mapping.iconKey}` as IconKey;
            }
          }
          // Make visible if it was hidden
          if (container.state === 'hidden') {
            container.state = 'normal';
          }
        } else {
          // Hide systems that are not in the customer config
          container.state = 'hidden';
        }
      }
      
      // Map Business Processes
      if (container.id.startsWith('bp-')) {
        const mapping = config.bpProcesses.find(bp => bp.id === container.id);
        if (mapping) {
          this.containerLabels[container.id] = mapping.label;
          // Update primary icon
          if (mapping.customIconPath) {
            container.logoIconKey = mapping.customIconPath as IconKey;
          } else {
            container.logoIconKey = `generic-system-${mapping.iconKey}` as IconKey;
          }
          // Update brand logo
          if (mapping.customBrandLogoPath) {
            container.secondaryLogoIconKey = mapping.customBrandLogoPath as IconKey;
          } else {
            container.secondaryLogoIconKey = `generic-brand-${mapping.brandLogoKey}` as IconKey;
          }
          // Make visible if it was hidden
          if (container.state === 'hidden') {
            container.state = 'normal';
          }
        } else {
          // Hide business processes that are not in the customer config
          container.state = 'hidden';
        }
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
   * Get current step safely
   */
  protected getCurrentStep(): StepConfig | undefined {
    return this.steps[this.currentStepIndex];
  }

  /**
   * Check if current step has specific ID
   */
  protected isCurrentStep(stepId: string): boolean {
    const step = this.getCurrentStep();
    return step?.id === stepId;
  }

  /**
   * Check if function icons should be shown
   */
  protected shouldShowFunctionIcons(): boolean {
    const step = this.getCurrentStep();
    return step?.showFunctionIcons !== false;
  }

  /**
   * Check if a specific function icon is highlighted
   */
  protected isFunctionIconHighlighted(iconKey: string): boolean {
    const step = this.getCurrentStep();
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
    if (container.type === 'pipeline') return container.borderColor || ORBIS_COLORS.orbisBlue.light;
    if (this.isContainerHighlighted(container)) {
      return ORBIS_COLORS.microsoftOrange.medium;
    }
    return container.borderColor || ORBIS_COLORS.orbisGrey.light;
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

    // First check if the entire label fits in one line
    // Remove break hints " / " and any hyphens before them, join without spaces
    // Example: "Lade- / station" -> "Ladestation", "Fräs / station" -> "Frässtation"
    const fullLabel = label.replace(/-\s*\/\s*/g, '').replace(/\s*\/\s*/g, '').trim();
    if (fullLabel.length <= maxCharsPerLine) {
      // Label fits in one line, return as single line (without break hints, hyphens, and spaces)
      return [fullLabel];
    }

    // Label doesn't fit, need to wrap
    // Allow manual break hints using " / " (locale-safe)
    // Split by " / " first to preserve line breaks
    const parts = label.split(' / ');
    
    // If we have explicit break hints, use them as separate lines
    if (parts.length > 1) {
      const lines: string[] = [];
      for (let i = 0; i < parts.length; i++) {
        const part = parts[i].trim();
        if (!part) continue;
        
        // Check if this part needs a hyphen when breaking (if it doesn't already end with one)
        const needsHyphen = i < parts.length - 1 && !part.endsWith('-');
        
        // Further split long parts if needed
        if (part.length > maxCharsPerLine) {
          const words = part.split(/\s+/);
          let current = '';
          for (const word of words) {
            const tentative = current ? `${current} ${word}` : word;
            if (tentative.length > maxCharsPerLine && current) {
              // Add hyphen if breaking mid-word and not already ending with hyphen
              const lineToAdd = current.endsWith('-') ? current : `${current}-`;
              lines.push(lineToAdd);
              current = word;
              if (lines.length >= maxLines - 1) break;
            } else {
              current = tentative;
            }
          }
          if (current && lines.length < maxLines) {
            // If this is not the last part and doesn't end with hyphen, add hyphen
            if (i < parts.length - 1 && !current.endsWith('-')) {
              lines.push(`${current}-`);
            } else {
              lines.push(current);
            }
          }
        } else {
          // Part fits in one line, but if we're breaking here and it doesn't end with hyphen, add one
          if (needsHyphen) {
            lines.push(`${part}-`);
          } else {
            lines.push(part);
          }
        }
        if (lines.length >= maxLines) break;
      }
      return lines.slice(0, maxLines);
    }

    // No explicit break hints, use automatic wrapping
    const dashExpanded: string[] = [];
    label.split(/\s+/).forEach((token) => {
      if (token.includes('-')) {
        const parts = token.split('-').filter(Boolean);
        parts.forEach((p, idx) => {
          dashExpanded.push(p);
          if (idx < parts.length - 1) dashExpanded.push('-');
        });
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
   * Update container URLs from ExternalLinksService
   */
  private updateContainerUrls(): void {
    const links = this.externalLinksService.current;
    this.containers.forEach((container) => {
      switch (container.id) {
        case 'dsp-ux':
          container.url = links.smartfactoryDashboardUrl;
          break;
        case 'dsp-edge':
          container.url = links.dspControlUrl;
          break;
        case 'dsp-mc':
          container.url = links.managementCockpitUrl;
          break;
        case 'bp-analytics':
          container.url = links.grafanaDashboardUrl;
          break;
        case 'bp-erp':
          // Task 12: Use ERP URL from settings, fallback to 'process' for internal route
          container.url = links.erpSystemUrl || 'process';
          break;
      }
    });
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
  /**
   * Zoom in with dynamic step size.
   * Uses finer steps (5%) when zoom < 100%, coarser steps (10%) when zoom ≥ 100%.
   */
  protected zoomIn(): void {
    if (this.zoom < this.maxZoom) {
      // Use current zoom to determine step (before change)
      const step = this.zoom < 1.0 ? this.ZOOM_STEP_FINE : this.ZOOM_STEP_COARSE;
      this.zoom = Math.min(this.zoom + step, this.maxZoom);
      this.cdr.markForCheck();
    }
  }

  /**
   * Zoom out with dynamic step size.
   * Uses finer steps (5%) when zoom < 100%, coarser steps (10%) when zoom ≥ 100%.
   */
  protected zoomOut(): void {
    if (this.zoom > this.minZoom) {
      // Use current zoom to determine step (before change)
      const step = this.zoom < 1.0 ? this.ZOOM_STEP_FINE : this.ZOOM_STEP_COARSE;
      this.zoom = Math.max(this.zoom - step, this.minZoom);
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
    const currentStep = this.steps[this.currentStepIndex];
    const isMc = container.id === 'dsp-mc';
    // layout set: all slots to keep angles stable
    const layoutIcons = isMc
      ? (container.functionIcons ?? []).filter((fi) => {
          if (currentStep?.id === 'step-18') {
            return fi.iconKey === 'logo-edge-b'; // Only central icon in step 18
          }
          if (currentStep?.id === 'step-19') {
            return fi.iconKey.startsWith('logo-edge-'); // All three icons in step 19
          }
          return !fi.iconKey.startsWith('logo-edge-');
        })
      : container.functionIcons ?? [];
    const total = layoutIcons.length;
    if (total === 0) {
      return { x: container.width / 2, y: container.height / 2 };
    }
    // For Step 18 with only one icon, center it in the 120° segment (at 180°)
    // For Step 19 with three icons, distribute them across the 120° segment starting at 120°
    const startDeg = isMc
      ? (currentStep?.id === 'step-18' || currentStep?.id === 'step-19')
        ? (currentStep?.id === 'step-18' && total === 1) ? 180 : 120 // Center single icon in step 18, start at 120° for step 19
        : 300
      : 90;
    const spanDeg = isMc ? 120 : 360;
    const layoutIndex = layoutIcons.findIndex((fi) => fi.iconKey === icon.iconKey);
    const slotIndex = layoutIndex >= 0 ? layoutIndex : index;
    const step = isMc
      ? total > 1
        ? spanDeg / (total - 1)
        : 0 // Single icon: no step needed, position at startDeg
      : spanDeg / total; // edge: distribute evenly over full circle (9 icons -> 40°)
    const angleRad = ((startDeg + slotIndex * step) * Math.PI) / 180;
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

  protected getFunctionIconCenter(
    container: ContainerConfig,
    index: number,
    icon: FunctionIconConfig
  ): { cx: number; cy: number } {
    const pos = this.getFunctionIconPosition(container, index, icon);
    const size = icon.size ?? this.getFunctionIconSize(icon.iconKey as IconKey);
    return { cx: pos.x + size / 2, cy: pos.y + size / 2 };
  }

  protected getVisibleFunctionIcons(container: ContainerConfig): FunctionIconConfig[] {
    if (!container.functionIcons || !this.shouldShowFunctionIcons()) {
      return [];
    }
    if (this.viewMode !== 'functional') {
      return container.functionIcons;
    }
    const step = this.steps[this.currentStepIndex];
    if (container.id === 'dsp-mc') {
      if (step?.id === 'step-18') {
        // Step 18: Only show central edge icon (logo-edge-b)
        return container.functionIcons.filter((fi) => fi.iconKey === 'logo-edge-b');
      }
      if (step?.id === 'step-19') {
        // Step 19: Show all three edge icons
        return container.functionIcons.filter((fi) => fi.iconKey.startsWith('logo-edge-'));
      }
      return container.functionIcons.filter(
        (fi) => !fi.iconKey.startsWith('logo-edge-') && this.revealedFunctionIcons.has(fi.iconKey)
      );
    }
    return container.functionIcons.filter((fi) => this.revealedFunctionIcons.has(fi.iconKey));
  }

  protected isFunctionIconVisible(iconKey: IconKey, container: ContainerConfig): boolean {
    return this.getVisibleFunctionIcons(container).some((fi) => fi.iconKey === iconKey);
  }

  protected showCenterIcon(container: ContainerConfig): boolean {
    if (!container.centerIconKey) return false;
    if (container.id === 'dsp-edge' && this.viewMode !== 'functional') {
      return this.currentStepIndex === 0;
    }
    return true;
  }
}
