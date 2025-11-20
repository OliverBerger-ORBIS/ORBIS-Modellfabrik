import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { MqttMockService, CellData } from '../services/mqtt-mock.service';
import { DetailsSidebarComponent, CellType } from '../details-sidebar/details-sidebar.component';

interface ShopfloorCell {
  id: string;
  name: string;
  type: 'orbis' | 'dsp' | 'dynamic';
  row: number;
  col: number;
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
  
  // Cell data from MQTT service
  cellDataMap = new Map<string, CellData>();
  
  // Sidebar state
  sidebarOpen = false;
  selectedCellType: CellType = null;
  selectedCellData: CellData | null = null;

  // Grid layout configuration - matching the reference image
  readonly cells: ShopfloorCell[] = [
    // Row 1
    { id: 'MILL', name: 'MILL', type: 'dynamic', row: 0, col: 0 },
    { id: 'DRILL', name: 'DRILL', type: 'dynamic', row: 0, col: 1 },
    { id: 'AIQS', name: 'AIQS', type: 'dynamic', row: 0, col: 2 },
    
    // Row 2
    { id: 'HBW', name: 'HBW', type: 'dynamic', row: 1, col: 0 },
    { id: 'ORBIS', name: 'ORBIS', type: 'orbis', row: 1, col: 1 },
    { id: 'VGR', name: 'VGR', type: 'dynamic', row: 1, col: 2 },
    
    // Row 3
    { id: 'SLD', name: 'SLD', type: 'dynamic', row: 2, col: 0 },
    { id: 'DSP', name: 'DSP', type: 'dsp', row: 2, col: 1 },
    { id: 'MPO', name: 'MPO', type: 'dynamic', row: 2, col: 2 },
    
    // Row 4
    { id: 'SSC', name: 'SSC', type: 'dynamic', row: 3, col: 0 },
  ];

  constructor(private mqttService: MqttMockService) {}

  ngOnInit(): void {
    // Subscribe to all dynamic cells
    this.cells
      .filter(cell => cell.type === 'dynamic')
      .forEach(cell => {
        const sub = this.mqttService.getCellData(cell.id).subscribe(data => {
          if (data) {
            this.cellDataMap.set(cell.id, data);
          }
        });
        this.subscriptions.add(sub);
      });
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  onCellClick(cell: ShopfloorCell): void {
    this.selectedCellType = cell.type;
    
    if (cell.type === 'dynamic') {
      this.selectedCellData = this.cellDataMap.get(cell.id) || null;
    } else {
      this.selectedCellData = null;
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

  getCellStatusClass(cell: ShopfloorCell): string {
    if (cell.type === 'orbis' || cell.type === 'dsp') {
      return 'special';
    }
    
    const data = this.getCellData(cell.id);
    if (!data) {
      return 'unknown';
    }
    
    return data.status;
  }

  getGridRow(cell: ShopfloorCell): number {
    return cell.row + 1; // CSS grid is 1-indexed
  }

  getGridCol(cell: ShopfloorCell): number {
    return cell.col + 1; // CSS grid is 1-indexed
  }
}
