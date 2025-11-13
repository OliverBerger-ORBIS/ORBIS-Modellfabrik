import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ShopfloorService } from './shopfloor.service';
import { ShopfloorRenderModel } from './models';

@Component({
  selector: 'app-shopfloor-demo',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './shopfloor-demo.component.html',
  styleUrls: ['./shopfloor-demo.component.scss'],
})
export class ShopfloorDemoComponent implements OnInit {
  renderModel: ShopfloorRenderModel | null = null;
  scale = 1.0;
  minScale = 0.25;
  maxScale = 2.0;
  loading = true;
  error: string | null = null;
  selectedCellId: string | null = null;

  constructor(
    private shopfloorService: ShopfloorService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadShopfloor();
  }

  private loadShopfloor(): void {
    this.loading = true;
    this.error = null;

    this.shopfloorService.getRenderModel(this.scale).subscribe({
      next: (model) => {
        this.renderModel = model;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.error = `Failed to load shopfloor: ${err.message}`;
        this.loading = false;
        this.cdr.detectChanges();
      },
    });
  }

  onScaleChange(): void {
    if (this.scale < this.minScale) {
      this.scale = this.minScale;
    }
    if (this.scale > this.maxScale) {
      this.scale = this.maxScale;
    }
    this.loadShopfloor();
  }

  onCellClick(cellId: string): void {
    this.selectedCellId = cellId;
    console.log('Cell clicked:', cellId);
  }

  onCellDoubleClick(cellId: string): void {
    this.shopfloorService.toggleHighlight(cellId);
    this.loadShopfloor();
    console.log('Cell double-clicked (highlight toggled):', cellId);
  }

  zoomIn(): void {
    this.scale = Math.min(this.maxScale, this.scale + 0.25);
    this.loadShopfloor();
  }

  zoomOut(): void {
    this.scale = Math.max(this.minScale, this.scale - 0.25);
    this.loadShopfloor();
  }

  resetZoom(): void {
    this.scale = 1.0;
    this.loadShopfloor();
  }

  clearHighlights(): void {
    this.shopfloorService.clearHighlights();
    this.loadShopfloor();
  }

  get scaledWidth(): number {
    return this.renderModel ? this.renderModel.width * this.scale : 0;
  }

  get scaledHeight(): number {
    return this.renderModel ? this.renderModel.height * this.scale : 0;
  }

  get scalePercent(): number {
    return Math.round(this.scale * 100);
  }

  getRoadPoints(points: number[][]): string {
    return points.map((p) => p.join(',')).join(' ');
  }

  getTransform(x: number, y: number): string {
    return `translate(${x},${y})`;
  }
}
