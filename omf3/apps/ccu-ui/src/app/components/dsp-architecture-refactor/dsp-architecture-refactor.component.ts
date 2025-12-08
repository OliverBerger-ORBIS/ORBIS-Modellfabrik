/**
 * Refactored DSP Architecture Component
 * 
 * A new implementation of the DSP architecture visualization with:
 * - Three-layer rendering (Business, DSP, Shopfloor)
 * - Multiple view modes (Functional, Component, Deployment)
 * - Animation engine with scene-based storytelling
 * - Interactive arrows with pulse animations
 * - Zoom controls
 * - Customer-configurable layers
 */

import { CommonModule } from '@angular/common';
import {
  Component,
  Input,
  Output,
  EventEmitter,
  OnInit,
  OnDestroy,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  AfterViewInit,
  ElementRef,
  ViewChild,
} from '@angular/core';
import type {
  ViewMode,
  ArchitectureConfig,
  Layer,
  Box,
  Arrow,
  BoxBounds,
  Point,
  ComponentState,
  BoxClickEvent,
  StepChangeEvent,
  AnimationScene,
  SceneStep,
  SceneAction,
} from './types';
import { getArchitectureConfig, applyLayerOverrides } from './layout.config';
import { getAnimationScene } from './animation.config';
import { getIconForBox } from './icons.config';

@Component({
  selector: 'app-dsp-architecture-refactor',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dsp-architecture-refactor.component.html',
  styleUrls: ['./dsp-architecture-refactor.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspArchitectureRefactorComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('svgContainer', { static: false }) svgContainer?: ElementRef<SVGSVGElement>;

  // Inputs
  @Input() viewMode: ViewMode = 'functional';
  @Input() animationEnabled = true;
  @Input() customConfig?: Partial<ArchitectureConfig>;

  // Outputs
  @Output() boxClick = new EventEmitter<BoxClickEvent>();
  @Output() stepChange = new EventEmitter<StepChangeEvent>();

  // Component state
  protected state: ComponentState = {
    currentView: 'functional',
    currentSceneIndex: 0,
    currentStepIndex: 0,
    isPlaying: false,
    zoom: 1,
    highlightedBoxes: new Set<string>(),
    visibleArrows: new Set<string>(),
    hiddenBoxes: new Set<string>(),
    overlayText: null,
  };

  // Configuration
  protected config: ArchitectureConfig | null = null;
  protected currentScene: AnimationScene | undefined;

  // Layout calculations
  protected boxBounds: Map<string, BoxBounds> = new Map();
  protected readonly viewBoxWidth = 1200;
  protected readonly viewBoxHeight = 800;
  protected readonly padding = 40;
  protected readonly layerSpacing = 10;
  protected readonly boxSpacing = 20;

  // Animation
  private animationTimer: ReturnType<typeof setTimeout> | null = null;

  // Zoom
  protected readonly minZoom = 0.5;
  protected readonly maxZoom = 2.0;
  protected readonly zoomStep = 0.1;

  // i18n labels
  protected readonly labelZoomIn = $localize`:@@refactorZoomIn:Zoom In`;
  protected readonly labelZoomOut = $localize`:@@refactorZoomOut:Zoom Out`;
  protected readonly labelResetZoom = $localize`:@@refactorResetZoom:Reset Zoom`;
  protected readonly labelPlay = $localize`:@@refactorPlay:Play`;
  protected readonly labelPause = $localize`:@@refactorPause:Pause`;
  protected readonly labelNext = $localize`:@@refactorNext:Next`;
  protected readonly labelPrev = $localize`:@@refactorPrev:Previous`;
  protected readonly labelReset = $localize`:@@refactorReset:Reset`;

  constructor(private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.initializeConfiguration();
    this.loadAnimationScene();
    this.initializeArrowVisibility();
  }

  ngAfterViewInit(): void {
    // Calculate box bounds after view is initialized
    setTimeout(() => {
      this.calculateBoxBounds();
      this.cdr.markForCheck();
    }, 100);
  }

  ngOnDestroy(): void {
    this.stopAnimation();
  }

  /**
   * Initialize architecture configuration
   */
  private initializeConfiguration(): void {
    this.state.currentView = this.viewMode;
    const baseConfig = getArchitectureConfig(this.viewMode);
    this.config = applyLayerOverrides(baseConfig, this.customConfig);
  }

  /**
   * Load animation scene for current view mode
   */
  private loadAnimationScene(): void {
    if (this.animationEnabled) {
      this.currentScene = getAnimationScene(this.viewMode);
    }
  }

  /**
   * Initialize arrow visibility based on configuration
   */
  private initializeArrowVisibility(): void {
    if (!this.config) return;
    
    this.state.visibleArrows.clear();
    this.config.arrows
      .filter(arrow => arrow.visible !== false)
      .forEach(arrow => this.state.visibleArrows.add(arrow.id));
  }

  /**
   * Calculate bounds for all boxes for arrow rendering
   */
  private calculateBoxBounds(): void {
    if (!this.svgContainer) return;

    const svg = this.svgContainer.nativeElement;
    const boxes = svg.querySelectorAll('[data-box-id]');

    boxes.forEach((element) => {
      const boxId = element.getAttribute('data-box-id');
      if (!boxId) return;

      const rect = element.getBoundingClientRect();
      const svgRect = svg.getBoundingClientRect();
      const CTM = svg.getScreenCTM();
      if (!CTM) return;

      const bounds: BoxBounds = {
        id: boxId,
        x: (rect.left - svgRect.left) / CTM.a,
        y: (rect.top - svgRect.top) / CTM.d,
        width: rect.width / CTM.a,
        height: rect.height / CTM.d,
        centerX: 0,
        centerY: 0,
      };

      bounds.centerX = bounds.x + bounds.width / 2;
      bounds.centerY = bounds.y + bounds.height / 2;

      this.boxBounds.set(boxId, bounds);
    });
  }

  /**
   * Get layer height based on height ratio
   */
  protected getLayerHeight(layer: Layer): number {
    if (!this.config) return 0;
    
    const totalRatio = this.config.layers.reduce((sum, l) => sum + l.heightRatio, 0);
    const availableHeight = this.viewBoxHeight - this.padding * 2 - this.layerSpacing * (this.config.layers.length - 1);
    return (availableHeight * layer.heightRatio) / totalRatio;
  }

  /**
   * Get layer Y position
   */
  protected getLayerY(layerIndex: number): number {
    if (!this.config) return 0;
    
    let y = this.padding;
    for (let i = 0; i < layerIndex; i++) {
      y += this.getLayerHeight(this.config.layers[i]) + this.layerSpacing;
    }
    return y;
  }

  /**
   * Get box X position within layer
   */
  protected getBoxX(box: Box, layer: Layer): number {
    const layerWidth = this.viewBoxWidth - this.padding * 2;
    const boxesBeforeThis = layer.boxes.filter(b => (b.position || 0) < (box.position || 0));
    const widthBeforeThis = boxesBeforeThis.reduce((sum, b) => sum + b.widthRatio, 0);
    
    const x = this.padding + layerWidth * widthBeforeThis + this.boxSpacing * (box.position || 0);
    return x;
  }

  /**
   * Get box width
   */
  protected getBoxWidth(box: Box): number {
    const layerWidth = this.viewBoxWidth - this.padding * 2;
    const boxCount = this.getBoxCountInLayer(box.layer);
    const totalSpacing = this.boxSpacing * (boxCount - 1);
    return (layerWidth - totalSpacing) * box.widthRatio;
  }

  /**
   * Get number of boxes in a layer
   */
  private getBoxCountInLayer(layerType: string): number {
    if (!this.config) return 0;
    const layer = this.config.layers.find(l => l.type === layerType);
    return layer ? layer.boxes.length : 0;
  }

  /**
   * Get icon path for a box
   */
  protected getIconPath(boxId: string): string {
    return getIconForBox(boxId);
  }

  /**
   * Check if box is highlighted
   */
  protected isBoxHighlighted(boxId: string): boolean {
    return this.state.highlightedBoxes.has(boxId);
  }

  /**
   * Check if box is hidden
   */
  protected isBoxHidden(boxId: string): boolean {
    return this.state.hiddenBoxes.has(boxId);
  }

  /**
   * Check if arrow is visible
   */
  protected isArrowVisible(arrowId: string): boolean {
    return this.state.visibleArrows.has(arrowId);
  }

  /**
   * Handle box click
   */
  protected onBoxClick(box: Box): void {
    if (!box.clickable) return;

    const event: BoxClickEvent = {
      boxId: box.id,
      layer: box.layer,
      label: box.label,
    };
    this.boxClick.emit(event);
  }

  /**
   * Calculate arrow path between two boxes
   */
  protected getArrowPath(arrow: Arrow): string {
    const fromBounds = this.boxBounds.get(arrow.from);
    const toBounds = this.boxBounds.get(arrow.to);

    if (!fromBounds || !toBounds) {
      return '';
    }

    const start: Point = { x: fromBounds.centerX, y: fromBounds.y + fromBounds.height };
    const end: Point = { x: toBounds.centerX, y: toBounds.y };

    switch (arrow.type) {
      case 'straight':
        return `M ${start.x} ${start.y} L ${end.x} ${end.y}`;
      case 'l-shaped':
        return this.getLShapedPath(start, end);
      case 'curved':
        return this.getCurvedPath(start, end);
      default:
        return `M ${start.x} ${start.y} L ${end.x} ${end.y}`;
    }
  }

  /**
   * Generate L-shaped arrow path
   */
  private getLShapedPath(start: Point, end: Point): string {
    const midY = start.y + (end.y - start.y) / 2;
    return `M ${start.x} ${start.y} L ${start.x} ${midY} L ${end.x} ${midY} L ${end.x} ${end.y}`;
  }

  /**
   * Generate curved arrow path
   */
  private getCurvedPath(start: Point, end: Point): string {
    const controlY = start.y + (end.y - start.y) / 2;
    return `M ${start.x} ${start.y} Q ${start.x} ${controlY} ${end.x} ${end.y}`;
  }

  // ========== Animation Controls ==========

  /**
   * Play animation
   */
  protected playAnimation(): void {
    if (!this.currentScene) return;

    this.state.isPlaying = true;
    this.executeNextStep();
  }

  /**
   * Pause animation
   */
  protected pauseAnimation(): void {
    this.state.isPlaying = false;
    this.stopAnimationTimer();
  }

  /**
   * Execute next animation step
   */
  private executeNextStep(): void {
    if (!this.state.isPlaying || !this.currentScene) return;

    const step = this.currentScene.steps[this.state.currentStepIndex];
    if (!step) {
      // End of animation
      this.pauseAnimation();
      return;
    }

    this.executeStep(step);
    this.emitStepChange();

    // Auto-advance to next step
    this.animationTimer = setTimeout(() => {
      this.nextStep();
      if (this.state.isPlaying) {
        this.executeNextStep();
      }
    }, step.duration || 3000);
  }

  /**
   * Execute a single animation step
   */
  private executeStep(step: SceneStep): void {
    step.actions.forEach(action => this.executeAction(action));
    this.cdr.markForCheck();
  }

  /**
   * Execute a single action
   */
  private executeAction(action: SceneAction): void {
    switch (action.type) {
      case 'highlight':
        if (action.reset) {
          this.state.highlightedBoxes.clear();
        } else if (action.targets) {
          action.targets.forEach(id => this.state.highlightedBoxes.add(id));
        }
        break;
      case 'fadeothers':
        // Handled via CSS classes
        break;
      case 'connect':
        if (action.targets) {
          action.targets.forEach(id => this.state.visibleArrows.add(id));
        }
        break;
      case 'disconnect':
        if (action.targets) {
          action.targets.forEach(id => this.state.visibleArrows.delete(id));
        }
        break;
      case 'show':
        if (action.targets) {
          action.targets.forEach(id => this.state.hiddenBoxes.delete(id));
        }
        break;
      case 'hide':
        if (action.targets) {
          action.targets.forEach(id => this.state.hiddenBoxes.add(id));
        }
        break;
      case 'text':
        this.state.overlayText = action.text || null;
        break;
    }
  }

  /**
   * Go to next step
   */
  protected nextStep(): void {
    if (!this.currentScene) return;

    if (this.state.currentStepIndex < this.currentScene.steps.length - 1) {
      this.state.currentStepIndex++;
      this.emitStepChange();
      this.cdr.markForCheck();
    }
  }

  /**
   * Go to previous step
   */
  protected prevStep(): void {
    if (this.state.currentStepIndex > 0) {
      this.state.currentStepIndex--;
      this.emitStepChange();
      this.cdr.markForCheck();
    }
  }

  /**
   * Reset animation to first step
   */
  protected resetAnimation(): void {
    this.stopAnimation();
    this.state.currentStepIndex = 0;
    this.state.highlightedBoxes.clear();
    this.state.hiddenBoxes.clear();
    this.state.overlayText = null;
    this.initializeArrowVisibility();
    this.cdr.markForCheck();
  }

  /**
   * Stop animation timer
   */
  private stopAnimationTimer(): void {
    if (this.animationTimer) {
      clearTimeout(this.animationTimer);
      this.animationTimer = null;
    }
  }

  /**
   * Stop animation completely
   */
  private stopAnimation(): void {
    this.state.isPlaying = false;
    this.stopAnimationTimer();
  }

  /**
   * Emit step change event
   */
  private emitStepChange(): void {
    if (!this.currentScene) return;

    const step = this.currentScene.steps[this.state.currentStepIndex];
    if (!step) return;

    const event: StepChangeEvent = {
      sceneId: this.currentScene.id,
      stepId: step.id,
      stepIndex: this.state.currentStepIndex,
      totalSteps: this.currentScene.steps.length,
    };
    this.stepChange.emit(event);
  }

  // ========== Zoom Controls ==========

  /**
   * Zoom in
   */
  protected zoomIn(): void {
    if (this.state.zoom < this.maxZoom) {
      this.state.zoom = Math.min(this.state.zoom + this.zoomStep, this.maxZoom);
      this.cdr.markForCheck();
    }
  }

  /**
   * Zoom out
   */
  protected zoomOut(): void {
    if (this.state.zoom > this.minZoom) {
      this.state.zoom = Math.max(this.state.zoom - this.zoomStep, this.minZoom);
      this.cdr.markForCheck();
    }
  }

  /**
   * Reset zoom to default
   */
  protected resetZoom(): void {
    this.state.zoom = 1;
    this.cdr.markForCheck();
  }

  /**
   * Get viewBox adjusted for zoom
   */
  protected getViewBox(): string {
    const width = this.viewBoxWidth / this.state.zoom;
    const height = this.viewBoxHeight / this.state.zoom;
    const x = (this.viewBoxWidth - width) / 2;
    const y = (this.viewBoxHeight - height) / 2;
    return `${x} ${y} ${width} ${height}`;
  }

  /**
   * Get current step label
   */
  protected getCurrentStepLabel(): string {
    if (!this.currentScene) return '';
    const step = this.currentScene.steps[this.state.currentStepIndex];
    return step ? step.label : '';
  }

  /**
   * Check if has previous step
   */
  protected hasPrevStep(): boolean {
    return this.state.currentStepIndex > 0;
  }

  /**
   * Check if has next step
   */
  protected hasNextStep(): boolean {
    if (!this.currentScene) return false;
    return this.state.currentStepIndex < this.currentScene.steps.length - 1;
  }
}
