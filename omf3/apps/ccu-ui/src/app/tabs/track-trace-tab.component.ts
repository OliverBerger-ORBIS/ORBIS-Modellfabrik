import { Component, ChangeDetectionStrategy, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TrackTraceComponent } from '../components/track-trace/track-trace.component';
import { EnvironmentService } from '../services/environment.service';
import { WorkpieceHistoryService } from '../services/workpiece-history.service';
import { getDashboardController } from '../mock-dashboard';
import { OrderFixtureName } from '@omf3/testing-fixtures';

/**
 * Track & Trace Tab Component
 * Displays workpiece tracking and event history
 */
@Component({
  selector: 'app-track-trace-tab',
  standalone: true,
  imports: [CommonModule, TrackTraceComponent],
  template: `
    <section class="track-trace-tab">
      <header class="track-trace-tab__toolbar">
        <div class="track-trace-tab__title">
          <img src="assets/svg/ui/heading-track-trace.svg" alt="Track & Trace" class="track-trace-tab__icon" width="32" height="32" />
          <div>
            <h1 i18n="@@trackTraceTabHeadline">Track & Trace</h1>
            <p class="track-trace-tab__subtitle" i18n="@@trackTraceTabDescription">
              Complete workpiece genealogy with real-time traceability and quality correlation.
            </p>
          </div>
        </div>

        <div class="track-trace-tab__fixtures" *ngIf="isMockMode">
          <span class="badge" i18n="@@orderTabFixtureLabel">Fixture</span>
          <div class="fixture-switch">
            <button
              type="button"
              *ngFor="let fixture of fixtureOptions"
              [class.active]="fixture === activeFixture"
              (click)="loadFixture(fixture)"
            >
              {{ fixtureLabels[fixture] }}
            </button>
          </div>
        </div>
      </header>

      <div class="track-trace-tab__content">
        <app-track-trace></app-track-trace>
      </div>
    </section>
  `,
  styleUrls: ['./track-trace-tab.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TrackTraceTabComponent implements OnInit {
  private dashboard = getDashboardController();
  private readonly workpieceHistoryService = inject(WorkpieceHistoryService);

  constructor(private readonly environmentService: EnvironmentService) {}

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  readonly fixtureOptions: OrderFixtureName[] = ['production_bwr', 'production_white', 'storage_blue'];
  readonly fixtureLabels: Partial<Record<OrderFixtureName, string>> = {
    production_bwr: $localize`:@@fixtureLabelProductionBwr:Production BWR`,
    production_white: $localize`:@@fixtureLabelProductionWhite:Production White`,
    storage_blue: $localize`:@@fixtureLabelStorageBlue:Storage Blue`,
  };
  activeFixture: OrderFixtureName | null = this.dashboard.getCurrentFixture();

  ngOnInit(): void {
    if (this.isMockMode) {
      void this.loadFixture('production_bwr');
    }
  }

  async loadFixture(fixture: OrderFixtureName): Promise<void> {
    if (!this.isMockMode) {
      return;
    }
    this.activeFixture = fixture;
    
    // Clear history before loading new fixture
    const environmentKey = this.environmentService.current.key;
    this.workpieceHistoryService.clear(environmentKey);
    
    // Map fixture name to tab preset name
    const presetMap: Partial<Record<OrderFixtureName, string>> = {
      production_bwr: 'track-trace-production-bwr',
      production_white: 'track-trace-production-white',
      storage_blue: 'track-trace-storage-blue',
    };
    
    const presetName = presetMap[fixture] || 'track-trace-default';
    
    // Load the fixture
    await this.dashboard.loadTabFixture(presetName);
    
    // Re-initialize service to process new messages
    // The TrackTraceComponent will also re-initialize, but this ensures we catch all messages
    this.workpieceHistoryService.initialize(environmentKey);
  }
}
