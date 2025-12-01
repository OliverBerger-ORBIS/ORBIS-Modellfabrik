import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import type { ShopfloorPoint } from '../components/shopfloor-preview/shopfloor-layout.types';
import { FtsRouteService, type RouteSegment } from './fts-route.service';

export interface AnimationState {
  isAnimating: boolean;
  animatedPosition: ShopfloorPoint | null;
  animationPath: string[];
  activeRouteSegments: RouteSegment[];
}

export interface AnimationCallbacks {
  onSegmentComplete?: (segmentIndex: number, totalSegments: number) => void;
  onAnimationComplete?: (finalNodeId: string) => void;
}

/**
 * Service for FTS route animation
 * Handles multi-segment route animation with smooth transitions
 */
@Injectable({ providedIn: 'root' })
export class FtsAnimationService {
  private readonly animationStateSubject = new BehaviorSubject<AnimationState>({
    isAnimating: false,
    animatedPosition: null,
    animationPath: [],
    activeRouteSegments: [],
  });

  private animationInterval: number | null = null;
  private animationStartTime: number = 0;
  private currentSegmentIndex: number = 0;
  private animationPath: string[] = [];
  private callbacks: AnimationCallbacks = {};

  // Animation duration per segment (1200ms - slower than example app's 800ms)
  private readonly ANIMATION_DURATION = 1200;
  private readonly ANIMATION_FPS = 16; // ~60fps

  readonly animationState$: Observable<AnimationState> = this.animationStateSubject.asObservable().pipe(
    shareReplay({ bufferSize: 1, refCount: false })
  );

  constructor(private readonly ftsRouteService: FtsRouteService) {}

  /**
   * Get current animation state snapshot
   */
  getState(): AnimationState {
    return this.animationStateSubject.value;
  }

  /**
   * Check if animation is currently running
   */
  get isAnimating(): boolean {
    return this.animationStateSubject.value.isAnimating;
  }

  /**
   * Get current animation path
   */
  get path(): string[] {
    return [...this.animationPath];
  }

  /**
   * Start animation between two nodes
   * @param from Starting node ID
   * @param to Target node ID
   * @param callbacks Optional callbacks for animation events
   */
  animateBetweenNodes(from: string, to: string, callbacks?: AnimationCallbacks): void {
    // Don't start new animation if already animating
    if (this.isAnimating) {
      return;
    }

    this.stopAnimation();
    this.callbacks = callbacks || {};

    // Calculate full path over intersections
    const fullPath = this.ftsRouteService.findRoutePath(from, to);
    if (!fullPath || fullPath.length < 2) {
      // Fallback: direct path
      this.animationPath = [from, to];
      this.currentSegmentIndex = 0;
      this.updateActiveRouteSegmentsForFullPath();
      this.startSegmentAnimation(from, to);
      return;
    }

    // Use full path including intersections
    this.animationPath = fullPath;
    this.currentSegmentIndex = 0;

    // Show full route immediately - all segments visible from start
    this.updateActiveRouteSegmentsForFullPath();

    // Start animation from first to second node
    this.startSegmentAnimation(fullPath[0], fullPath[1]);
  }

  /**
   * Start animation for a single segment between two nodes
   */
  private startSegmentAnimation(from: string, to: string): void {
    // Clear any existing animation interval before starting a new segment
    if (this.animationInterval) {
      window.clearInterval(this.animationInterval);
      this.animationInterval = null;
    }

    // Resolve node references
    const fromCanonical = this.ftsRouteService.resolveNodeRef(from) ?? from;
    const toCanonical = this.ftsRouteService.resolveNodeRef(to) ?? to;

    // Get start position - use current animated position if available, otherwise use node position
    let fromPos: ShopfloorPoint;
    const currentState = this.animationStateSubject.value;
    if (currentState.animatedPosition && this.isAnimating) {
      // Continue from current animated position (smooth transition between segments)
      fromPos = currentState.animatedPosition;
    } else {
      // Start from node position
      fromPos = this.ftsRouteService.getNodePosition(fromCanonical) || this.ftsRouteService.getNodePosition(from) || { x: 0, y: 0 };
    }

    const toPos = this.ftsRouteService.getNodePosition(toCanonical) || this.ftsRouteService.getNodePosition(to);

    if (!toPos) {
      console.warn('[FtsAnimationService] Cannot start animation - missing target position:', { from, to, fromCanonical, toCanonical, toPos });
      this.stopAnimation();
      return;
    }

    // Use exact center positions for both modules and intersections
    const targetPos = toPos;

    // Keep isAnimating = true during entire multi-segment animation
    this.updateState({ isAnimating: true });
    this.animationStartTime = Date.now();

    // Store fromPos in closure to prevent it from changing during animation
    const startPos = { ...fromPos };

    // Use setInterval for consistent animation behavior
    this.animationInterval = window.setInterval(() => {
      const elapsed = Date.now() - this.animationStartTime;
      const progress = Math.min(elapsed / this.ANIMATION_DURATION, 1);

      // Ease-in-out cubic for smoother animation
      const easeProgress =
        progress < 0.5 ? 4 * progress * progress * progress : 1 - Math.pow(-2 * progress + 2, 3) / 2;

      // Calculate position from stored start position
      const animatedPosition = {
        x: startPos.x + (targetPos.x - startPos.x) * easeProgress,
        y: startPos.y + (targetPos.y - startPos.y) * easeProgress,
      };

      this.updateState({ animatedPosition });

      if (progress >= 1) {
        // Animation segment complete - set position to exact target
        this.updateState({ animatedPosition: { ...targetPos } });

        // Check if there are more segments to animate
        if (this.currentSegmentIndex < this.animationPath.length - 2) {
          // Move to next segment in path
          this.currentSegmentIndex++;
          // Keep isAnimating = true during entire multi-segment animation
          // Route remains fully visible (already shown by updateActiveRouteSegmentsForFullPath)
          const nextFrom = this.animationPath[this.currentSegmentIndex];
          const nextTo = this.animationPath[this.currentSegmentIndex + 1];
          // Start animation for next segment (smooth transition, 1200ms)
          this.startSegmentAnimation(nextFrom, nextTo);

          // Notify callback
          if (this.callbacks.onSegmentComplete) {
            this.callbacks.onSegmentComplete(this.currentSegmentIndex, this.animationPath.length - 1);
          }
        } else {
          // Animation complete - reached final destination (all segments animated)
          window.clearInterval(this.animationInterval!);
          this.animationInterval = null;
          this.updateState({
            isAnimating: false,
            animatedPosition: null,
          });

          // Clear route segments now that all segments have been animated
          this.updateState({ activeRouteSegments: [], animationPath: [] });

          this.currentSegmentIndex = 0;
          const finalNodeId = this.animationPath.length > 0 ? this.animationPath[this.animationPath.length - 1] : '';

          // Notify callback
          if (this.callbacks.onAnimationComplete && finalNodeId) {
            this.callbacks.onAnimationComplete(finalNodeId);
          }

          this.animationPath = [];
        }
      }
    }, this.ANIMATION_FPS);
  }

  /**
   * Stop animation and reset state
   */
  stopAnimation(): void {
    if (this.animationInterval) {
      window.clearInterval(this.animationInterval);
      this.animationInterval = null;
    }
    this.updateState({
      isAnimating: false,
      animationPath: [],
      animatedPosition: null,
      activeRouteSegments: [],
    });
    this.currentSegmentIndex = 0;
    this.animationPath = [];
  }

  /**
   * Update active route segments to show full path from start to destination
   */
  private updateActiveRouteSegmentsForFullPath(): void {
    if (this.animationPath.length < 2) {
      return;
    }

    const segments: RouteSegment[] = [];
    for (let i = 0; i < this.animationPath.length - 1; i++) {
      const from = this.animationPath[i];
      const to = this.animationPath[i + 1];
      
      // Resolve both nodes to canonical form to check if they're the same
      const fromCanonical = this.ftsRouteService.resolveNodeRef(from) ?? from;
      const toCanonical = this.ftsRouteService.resolveNodeRef(to) ?? to;
      
      // Skip if from and to resolve to the same node (different formats of same node)
      if (fromCanonical === toCanonical) {
        continue;
      }
      
      const road = this.ftsRouteService.findRoadBetween(from, to);
      if (road) {
        const segment = this.ftsRouteService.buildRoadSegment(road);
        if (segment) {
          segments.push(segment);
        }
      } else {
        console.warn('[FtsAnimationService] Road not found between nodes:', { from, to, fromCanonical, toCanonical, animationPath: this.animationPath });
      }
    }

    // Always set route segments, even if some segments are missing
    this.updateState({ activeRouteSegments: segments });

    console.log('[FtsAnimationService] Route segments set:', {
      pathLength: this.animationPath.length,
      segmentsCount: segments.length,
      path: this.animationPath,
    });
  }

  /**
   * Update internal state and emit to observers
   */
  private updateState(updates: Partial<AnimationState>): void {
    const currentState = this.animationStateSubject.value;
    const newState: AnimationState = {
      ...currentState,
      ...updates,
      // Ensure animationPath is always synced
      animationPath: updates.animationPath !== undefined ? updates.animationPath : this.animationPath,
    };
    this.animationStateSubject.next(newState);
  }
}


