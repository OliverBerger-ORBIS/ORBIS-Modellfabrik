import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { createMockDashboardStreams } from './mock-dashboard';
import { OrdersViewComponent } from './orders-view.component';
import { StockViewComponent } from './stock-view.component';
import { ModuleMapComponent } from './module-map.component';
import { FtsViewComponent } from './fts-view.component';

@Component({
  standalone: true,
  imports: [
    CommonModule,
    OrdersViewComponent,
    StockViewComponent,
    ModuleMapComponent,
    FtsViewComponent,
  ],
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AppComponent {
  readonly streams = createMockDashboardStreams();
}
