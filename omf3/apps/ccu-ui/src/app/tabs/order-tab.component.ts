import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  standalone: true,
  selector: 'app-order-tab',
  template: `
    <section class="placeholder">
      <h2 i18n="@@orderTabHeadline">Order planning</h2>
      <p i18n="@@orderTabDescription">
        Detailed order information and production/storage differentiation will appear here.
      </p>
    </section>
  `,
  styles: [
    `
      .placeholder {
        display: grid;
        gap: 0.75rem;
        padding: 1.5rem;
        border-radius: 1rem;
        background: #fff;
        box-shadow: 0 12px 40px -24px rgba(20, 63, 107, 0.4);
      }

      h2 {
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrderTabComponent {}

