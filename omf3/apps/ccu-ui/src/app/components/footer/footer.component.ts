import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

let VERSION = { full: '0.0.0-dev', build: 'dev', buildDate: new Date().toISOString() };
try {
  // Version file is generated during build (see deploy.yml workflow)
  VERSION = require('../../../environments/version').VERSION;
} catch {
  // Fallback to dev version if version file not found (development mode)
}

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <footer class="app-footer">
      <span>OMF3 Dashboard v{{ version.full }}</span>
      <span class="build-info" [title]="'Build: ' + version.build">
        {{ version.buildDate | date:'short' }}
      </span>
    </footer>
  `,
  styles: [`
    .app-footer {
      display: flex;
      justify-content: space-between;
      padding: 8px 16px;
      font-size: 12px;
      color: #6c757d;
      border-top: 1px solid #dee2e6;
      background: #f8f9fa;
    }
    .build-info {
      cursor: help;
    }
  `]
})
export class FooterComponent {
  version = VERSION;
}
