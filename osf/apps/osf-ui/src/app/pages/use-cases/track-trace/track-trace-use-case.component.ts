import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  OnInit,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { TrackTraceGenealogyUseCaseComponent } from '../track-trace-genealogy/track-trace-genealogy-use-case.component';
import { TrackTraceTabComponent } from '../../../tabs/track-trace-tab.component';

/**
 * UC-01 shell: single DSP route with Concept (genealogy SVG) and Live Demo (Track & Trace tab).
 * DR-22: one tile in the DSP list; tabs instead of two separate routes for the same UC.
 */
@Component({
  selector: 'app-track-trace-use-case',
  standalone: true,
  imports: [CommonModule, TrackTraceGenealogyUseCaseComponent, TrackTraceTabComponent],
  templateUrl: './track-trace-use-case.component.html',
  styleUrls: ['./track-trace-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TrackTraceUseCaseComponent implements OnInit {
  activeTab: 'concept' | 'live-demo' = 'concept';

  constructor(
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.route.queryParamMap.subscribe((params) => {
      this.activeTab = params.get('tab') === 'live' ? 'live-demo' : 'concept';
      this.cdr.markForCheck();
    });
  }

  setTab(tab: 'concept' | 'live-demo'): void {
    this.activeTab = tab;
    void this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { tab: tab === 'live-demo' ? 'live' : 'concept' },
      queryParamsHandling: 'merge',
      replaceUrl: true,
    });
  }
}
