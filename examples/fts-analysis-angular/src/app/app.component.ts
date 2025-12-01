import { Component, ChangeDetectionStrategy, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FtsMockService } from './services/fts-mock.service';
import { FtsBatteryComponent } from './components/fts-battery/fts-battery.component';
import { FtsStatusComponent } from './components/fts-status/fts-status.component';
import { FtsLoadsComponent } from './components/fts-loads/fts-loads.component';
import { FtsRouteComponent } from './components/fts-route/fts-route.component';
import { TrackTraceComponent } from './components/track-trace/track-trace.component';
import { FtsState, FtsBatteryState, FtsLoadInfo } from './models/fts.types';
import { Observable, Subscription } from 'rxjs';

/**
 * FTS Analysis Example Application
 * 
 * Standalone Angular app demonstrating FTS/AGV data visualization
 * Based on real MQTT data from data/omf-data/fts-analysis/
 * 
 * Features:
 * - Battery Status visualization
 * - Route & Position display
 * - Action States monitoring
 * - Load Information
 * - Track & Trace for workpieces
 */
@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    FtsBatteryComponent,
    FtsStatusComponent,
    FtsLoadsComponent,
    FtsRouteComponent,
    TrackTraceComponent,
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AppComponent implements OnInit, OnDestroy {
  private ftsService = inject(FtsMockService);
  private subscription = new Subscription();
  
  title = 'FTS/AGV Analysis Dashboard';
  
  // Observable streams for components
  ftsState$: Observable<FtsState> = this.ftsService.ftsState$;
  batteryState$: Observable<FtsBatteryState> = this.ftsService.batteryState$;
  loads$: Observable<FtsLoadInfo[]> = this.ftsService.loads$;
  
  activeTab: 'dashboard' | 'track-trace' = 'dashboard';
  
  ngOnInit(): void {
    // Additional initialization if needed
  }
  
  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }
  
  setTab(tab: 'dashboard' | 'track-trace'): void {
    this.activeTab = tab;
  }
  
  resetSimulation(): void {
    this.ftsService.resetSimulation();
  }
}
