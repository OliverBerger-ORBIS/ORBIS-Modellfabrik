import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OrdersViewComponent } from './orders-view.component';
import { StockViewComponent } from './stock-view.component';
import { ModuleMapComponent } from './module-map.component';
import { FtsViewComponent } from './fts-view.component';
import { createMockDashboardController } from './mock-dashboard';
import type { OrderFixtureName } from '@omf3/testing-fixtures';
import type { FtsState, ModuleState, OrderActive } from '@omf3/entities';
import type { Observable } from 'rxjs';

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
export class AppComponent implements OnInit {
  private readonly controller = createMockDashboardController();

  readonly fixtureOptions: OrderFixtureName[] = ['white', 'blue', 'red', 'mixed'];
  activeFixture: OrderFixtureName = 'white';

  orders$: Observable<OrderActive[]> = this.controller.streams.orders$;
  orderCounts$: Observable<Record<'running' | 'queued' | 'completed', number>> =
    this.controller.streams.orderCounts$;
  stockByPart$: Observable<Record<string, number>> = this.controller.streams.stockByPart$;
  moduleStates$: Observable<Record<string, ModuleState>> = this.controller.streams.moduleStates$;
  ftsStates$: Observable<Record<string, FtsState>> = this.controller.streams.ftsStates$;

  ngOnInit(): void {
    void this.loadFixture(this.activeFixture);
  }

  async loadFixture(fixture: OrderFixtureName) {
    this.activeFixture = fixture;
    try {
      const streams = await this.controller.loadFixture(fixture);
      this.orders$ = streams.orders$;
      this.orderCounts$ = streams.orderCounts$;
      this.stockByPart$ = streams.stockByPart$;
      this.moduleStates$ = streams.moduleStates$;
      this.ftsStates$ = streams.ftsStates$;
    } catch (error) {
      console.warn('Failed to load fixture', fixture, error);
    }
  }
}
