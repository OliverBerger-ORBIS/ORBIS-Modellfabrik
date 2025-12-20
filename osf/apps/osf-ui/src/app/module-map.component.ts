import { CommonModule, KeyValuePipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';
import type { ModuleState } from '@osf/entities';
import type { Observable } from 'rxjs';

@Component({
  selector: 'app-module-map',
  standalone: true,
  template: `
    <section class="panel">
      <header>
        <h2 i18n="@@moduleStatusHeadline">Module Status</h2>
      </header>

      <ng-container *ngIf="moduleStates$ | async as modules">
        <ul *ngIf="(modules | keyvalue).length; else noModules">
          <li *ngFor="let entry of modules | keyvalue">
            <div class="module-id">{{ entry.key }}</div>
            <div class="state" [class]="entry.value.state">
              {{ entry.value.state }}
            </div>
            <div class="meta">
              <span *ngIf="entry.value.details as details">
                {{
                  details['orderId'] ??
                    details['step'] ??
                    details['description'] ??
                    ''
                }}
              </span>
              <span class="timestamp" *ngIf="entry.value.lastSeen">
                {{ entry.value.lastSeen | date: 'shortTime' }}
              </span>
            </div>
          </li>
        </ul>
      </ng-container>

      <ng-template #noModules>
        <p class="empty" i18n="@@moduleStatusEmptyState">Awaiting module telemetry.</p>
      </ng-template>
    </section>
  `,
  styleUrls: ['./module-map.component.scss'],
  imports: [CommonModule, KeyValuePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ModuleMapComponent {
  @Input({ required: true })
  moduleStates$!: Observable<Record<string, ModuleState>>;
}

