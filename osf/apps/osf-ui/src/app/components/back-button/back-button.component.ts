import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavigationBackService } from '../../services/navigation-back.service';

@Component({
  selector: 'app-back-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      type="button"
      class="back-btn"
      (click)="goBack()"
      [attr.aria-label]="label"
      [attr.title]="label"
    >
      ←
    </button>
  `,
  styles: [
    `
      .back-btn {
        width: 44px;
        height: 44px;
        border-radius: 999px;
        padding: 0;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(31, 54, 93, 0.25);
        background: rgba(31, 54, 93, 0.08);
        color: #1f365d;
        cursor: pointer;
        transition: transform 0.12s ease, box-shadow 0.12s ease, background 0.12s ease;
        user-select: none;
        font-size: 18px;
        line-height: 1;
      }

      .back-btn:hover {
        background: rgba(31, 54, 93, 0.12);
        box-shadow: 0 12px 24px -18px rgba(31, 54, 93, 0.45);
      }

      .back-btn:active {
        transform: translateY(1px);
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BackButtonComponent {
  /** Path without locale prefix, e.g. 'dsp'. */
  @Input() fallbackPath = 'dsp';
  @Input() label = $localize`:@@backButtonLabel:Back`;

  constructor(private readonly navBack: NavigationBackService) {}

  goBack(): void {
    this.navBack.backOrNavigate(this.fallbackPath);
  }
}

