import { CommonModule, KeyValuePipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';
import type { Observable } from 'rxjs';

@Component({
  selector: 'app-stock-view',
  standalone: true,
  template: `
    <section class="panel">
      <header>
        <h2>Stock Levels</h2>
      </header>

      <ng-container *ngIf="stockByPart$ | async as stock">
        <table *ngIf="(stock | keyvalue).length; else noStock">
          <thead>
            <tr>
              <th>Part</th>
              <th class="amount">Quantity</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let entry of stock | keyvalue">
              <td>{{ entry.key }}</td>
              <td class="amount">{{ entry.value }}</td>
            </tr>
          </tbody>
        </table>
      </ng-container>

      <ng-template #noStock>
        <p class="empty">No stock movements received.</p>
      </ng-template>
    </section>
  `,
  styleUrls: ['./stock-view.component.scss'],
  imports: [CommonModule, KeyValuePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class StockViewComponent {
  @Input({ required: true }) stockByPart$!: Observable<Record<string, number>>;
}

