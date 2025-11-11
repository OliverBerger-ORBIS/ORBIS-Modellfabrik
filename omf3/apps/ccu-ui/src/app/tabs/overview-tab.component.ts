import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import type { FtsState, ModuleState, OrderActive } from '@omf3/entities';
import {
  createMockDashboardController,
  type DashboardStreamSet,
} from '../mock-dashboard';
import { OrdersViewComponent } from '../orders-view.component';
import { StockViewComponent } from '../stock-view.component';
import { ModuleMapComponent } from '../module-map.component';
import { FtsViewComponent } from '../fts-view.component';
import type { OrderFixtureName } from '@omf3/testing-fixtures';
import type { Observable } from 'rxjs';

@Component({
  standalone: true,
  selector: 'app-overview-tab',
  imports: [CommonModule, OrdersViewComponent, StockViewComponent, ModuleMapComponent, FtsViewComponent],
  templateUrl: './overview-tab.component.html',
  styleUrl: './overview-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OverviewTabComponent implements OnInit {
  private dashboard = createMockDashboardController();

  readonly fixtureOptions: OrderFixtureName[] = ['white', 'blue', 'red', 'mixed'];
  activeFixture: OrderFixtureName = 'white';

  readonly fixtureLabels: Record<OrderFixtureName, string> = {
    white: $localize`:@@fixtureLabelWhite:White`,
    blue: $localize`:@@fixtureLabelBlue:Blue`,
    red: $localize`:@@fixtureLabelRed:Red`,
    mixed: $localize`:@@fixtureLabelMixed:Mixed`,
  };

  orders$: Observable<OrderActive[]> = this.dashboard.streams.orders$;
  orderCounts$: Observable<Record<'running' | 'queued' | 'completed', number>> =
    this.dashboard.streams.orderCounts$;
  stockByPart$: Observable<Record<string, number>> = this.dashboard.streams.stockByPart$;
  moduleStates$: Observable<Record<string, ModuleState>> = this.dashboard.streams.moduleStates$;
  ftsStates$: Observable<Record<string, FtsState>> = this.dashboard.streams.ftsStates$;

  ngOnInit(): void {
    void this.loadFixture(this.activeFixture);
  }

  async loadFixture(fixture: OrderFixtureName) {
    this.activeFixture = fixture;
    try {
      const streams: DashboardStreamSet = await this.dashboard.loadFixture(fixture);
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

