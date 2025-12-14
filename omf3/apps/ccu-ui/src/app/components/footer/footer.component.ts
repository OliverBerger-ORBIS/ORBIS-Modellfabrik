import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

let VERSION = { full: '0.3.0', build: 'dev', buildDate: new Date().toISOString() };
try {
  VERSION = require('../../../environments/version').VERSION;
} catch {}

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [CommonModule],
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
