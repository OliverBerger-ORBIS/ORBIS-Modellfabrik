import { Component, OnInit, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { ShopfloorLayoutService } from './shopfloor-layout.service';
import type { ShopfloorRenderModel, CellRenderModel } from './shopfloor-layout.models';

@Component({
  standalone: true,
  selector: 'app-shopfloor-demo',
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './shopfloor-demo.component.html',
  styleUrl: './shopfloor-demo.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ShopfloorDemoComponent implements OnInit {
  renderModel: ShopfloorRenderModel | null = null;
  scale = 100; // Scale in percentage (25-200)
  selectedCellId: string | null = null;
  loading = true;
  error: string | null = null;

  readonly minScale = 25;
  readonly maxScale = 200;

  constructor(
    private layoutService: ShopfloorLayoutService,
    private cdr: ChangeDetectorRef
  ) {}

  async ngOnInit() {
    try {
      this.renderModel = await this.layoutService.loadShopfloorLayout();
      this.loading = false;
      this.cdr.markForCheck();
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Failed to load shopfloor layout';
      this.loading = false;
      this.cdr.markForCheck();
    }
  }

  /**
   * Get CSS transform for the current scale
   */
  get scaleTransform(): string {
    return `scale(${this.scale / 100})`;
  }

  /**
   * Handle cell click
   */
  onCellClick(cell: CellRenderModel) {
    console.log('Cell clicked:', cell.id, cell);
    if (this.selectedCellId === cell.id) {
      this.selectedCellId = null;
    } else {
      this.selectedCellId = cell.id;
    }
    this.cdr.markForCheck();
  }

  /**
   * Handle cell double-click
   */
  onCellDoubleClick(cell: CellRenderModel) {
    console.log('Cell double-clicked:', cell.id, cell);
    alert(`Double-clicked: ${cell.id}\nType: ${cell.type}\nRole: ${cell.role}`);
  }

  /**
   * Check if a cell is selected
   */
  isCellSelected(cell: CellRenderModel): boolean {
    return this.selectedCellId === cell.id;
  }

  /**
   * Format scale value for display
   */
  get scaleLabel(): string {
    return `${this.scale}%`;
  }

  /**
   * Update scale from slider
   */
  onScaleChange(event: Event) {
    const target = event.target as HTMLInputElement;
    this.scale = parseInt(target.value, 10);
    this.cdr.markForCheck();
  }

  /**
   * Convert route points to SVG polyline points string
   */
  getPolylinePoints(points: [number, number][]): string {
    return points.map(p => p.join(',')).join(' ');
  }
}
