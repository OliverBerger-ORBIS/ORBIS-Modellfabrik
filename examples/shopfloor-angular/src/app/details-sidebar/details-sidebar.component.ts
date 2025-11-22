import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IncrementalComponent } from '../incremental/incremental.component';
import { CellData } from '../services/mqtt-mock.service';

export type CellType = 'orbis' | 'dsp' | 'dynamic' | null;

@Component({
  selector: 'app-details-sidebar',
  standalone: true,
  imports: [CommonModule, IncrementalComponent],
  templateUrl: './details-sidebar.component.html',
  styleUrls: ['./details-sidebar.component.scss']
})
export class DetailsSidebarComponent {
  @Input() isOpen = false;
  @Input() cellType: CellType = null;
  @Input() cellData: CellData | null = null;
  @Output() close = new EventEmitter<void>();

  onClose(): void {
    this.close.emit();
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'running': return '#50C878';
      case 'idle': return '#FFA500';
      case 'error': return '#E74C3C';
      case 'maintenance': return '#3498DB';
      default: return '#95A5A6';
    }
  }
}
