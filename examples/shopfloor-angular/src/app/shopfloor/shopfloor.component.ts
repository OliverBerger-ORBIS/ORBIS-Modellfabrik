import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Subscription } from 'rxjs';
import { MqttMockService, CellData } from '../services/mqtt-mock.service';
import { DetailsSidebarComponent, CellType } from '../details-sidebar/details-sidebar.component';
import { 
  ShopfloorLayoutConfig, 
  ShopfloorCellConfig 
} from '../shopfloor-layout/shopfloor-layout.types';

interface RenderCell {
  id: string;
  name: string;
  top: number;
  left: number;
  width: number;
  height: number;
  role: 'module' | 'company' | 'software';
  background?: string;
  serial?: string;
  showLabel: boolean;
}

interface ShopfloorView {
  width: number;
  height: number;
  cells: RenderCell[];
}

@Component({
  selector: 'app-shopfloor',
  standalone: true,
  imports: [CommonModule, DetailsSidebarComponent],
  templateUrl: './shopfloor.component.html',
  styleUrls: ['./shopfloor.component.scss']
})
export class ShopfloorComponent implements OnInit, OnDestroy {
  private subscriptions = new Subscription();
  
  // Layout and view model
  viewModel: ShopfloorView | null = null;
  private layoutConfig?: ShopfloorLayoutConfig;
  
  // Cell data from MQTT service
  cellDataMap = new Map<string, CellData>();
  
  // Sidebar state
  sidebarOpen = false;
  selectedCellType: CellType = null;
  selectedCellData: CellData | null = null;
  selectedCellName = '';
  
  // Scale
  currentScale = 0.8;

  constructor(
    private http: HttpClient,
    private mqttService: MqttMockService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    // Load shopfloor layout from JSON
    this.http.get<ShopfloorLayoutConfig>('assets/shopfloor/shopfloor_layout.json').subscribe({
      next: (config) => {
        this.layoutConfig = config;
        this.updateViewModel();
        this.subscribeToModules();
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Failed to load shopfloor layout configuration:', error);
        console.error('Error details:', {
          message: error.message,
          status: error.status,
          url: error.url
        });
      }
    });
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  private subscribeToModules(): void {
    if (!this.layoutConfig) return;
    
    // Subscribe to all module cells
    this.layoutConfig.cells
      .filter(cell => cell.role === 'module' && cell.serial_number)
      .forEach(cell => {
        const serial = cell.serial_number!;
        const sub = this.mqttService.getCellData(serial).subscribe(data => {
          if (data) {
            this.cellDataMap.set(cell.id, data);
            this.cdr.markForCheck();
          }
        });
        this.subscriptions.add(sub);
      });
  }

  private updateViewModel(): void {
    if (!this.layoutConfig) return;

    const width = this.layoutConfig.metadata.canvas.width;
    const height = this.layoutConfig.metadata.canvas.height;

    const cells = this.layoutConfig.cells.map(cell => this.createRenderCell(cell));

    this.viewModel = {
      width,
      height,
      cells
    };
  }

  private createRenderCell(cell: ShopfloorCellConfig): RenderCell {
    return {
      id: cell.id,
      name: cell.name,
      top: cell.position.y,
      left: cell.position.x,
      width: cell.size.w,
      height: cell.size.h,
      role: cell.role,
      background: cell.background_color,
      serial: cell.serial_number,
      showLabel: cell.show_name !== false
    };
  }

  onCellClick(cell: RenderCell): void {
    this.selectedCellName = cell.name;
    
    if (cell.role === 'company') {
      this.selectedCellType = 'orbis';
      this.selectedCellData = null;
    } else if (cell.role === 'software') {
      this.selectedCellType = 'dsp';
      this.selectedCellData = null;
    } else if (cell.role === 'module') {
      this.selectedCellType = 'dynamic';
      this.selectedCellData = this.cellDataMap.get(cell.id) || null;
    }
    
    this.sidebarOpen = true;
  }

  onSidebarClose(): void {
    this.sidebarOpen = false;
    this.selectedCellType = null;
    this.selectedCellData = null;
  }

  getCellData(cellId: string): CellData | undefined {
    return this.cellDataMap.get(cellId);
  }

  getCellStatusClass(cell: RenderCell): string {
    if (cell.role === 'company' || cell.role === 'software') {
      return 'special';
    }
    
    const data = this.getCellData(cell.id);
    if (!data) {
      return 'idle';
    }
    
    return data.status;
  }
}
