import { CommonModule, KeyValuePipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';
import type { FtsState } from '@omf3/entities';
import type { Observable } from 'rxjs';

@Component({
  selector: 'app-fts-view',
  standalone: true,
  template: `
    <section class="panel">
      <header>
        <h2>FTS Fleet</h2>
      </header>

      <ng-container *ngIf="ftsStates$ | async as fts">
        <ul *ngIf="(fts | keyvalue).length; else noFts">
          <li *ngFor="let entry of fts | keyvalue">
            <div class="fts-id">{{ entry.key }}</div>
            <div class="status" [class]="entry.value.status">
              {{ entry.value.status || 'unknown' }}
            </div>
            <div class="coords" *ngIf="entry.value.position as pos">
              ({{ pos.x }}, {{ pos.y }})
            </div>
          </li>
        </ul>
      </ng-container>

      <ng-template #noFts>
        <p class="empty">No FTS telemetry received yet.</p>
      </ng-template>
    </section>
  `,
  styleUrls: ['./fts-view.component.scss'],
  imports: [CommonModule, KeyValuePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FtsViewComponent {
  @Input({ required: true })
  ftsStates$!: Observable<Record<string, FtsState>>;
}

