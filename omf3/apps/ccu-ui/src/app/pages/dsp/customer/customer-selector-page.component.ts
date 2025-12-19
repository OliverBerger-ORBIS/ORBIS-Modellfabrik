import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ECME_CONFIG } from '../../../components/dsp-animation/configs/ecme/ecme-config';
import { FMF_CONFIG } from '../../../components/dsp-animation/configs/fmf/fmf-config';
import type { CustomerDspConfig } from '../../../components/dsp-animation/configs/types';

interface CustomerOption {
  config: CustomerDspConfig;
  route: string;
}

/**
 * Customer Selector Page Component
 * Provides a dropdown to select and navigate to customer-specific DSP architecture pages
 */
@Component({
  standalone: true,
  selector: 'app-customer-selector-page',
  imports: [CommonModule, FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="customer-selector-page">
      <header class="customer-selector-header">
        <h1 i18n="@@customerSelectorTitle">DSP Customer Architecture</h1>
        <p class="subtitle" i18n="@@customerSelectorSubtitle">
          Select a customer to view their customized DSP architecture demonstration.
        </p>
      </header>

      <main class="customer-selector-main">
        <div class="selector-card">
          <label for="customer-select" class="selector-label">
            <span i18n="@@customerSelectorLabel">Select Customer:</span>
          </label>
          <select
            id="customer-select"
            class="customer-select"
            [value]="selectedCustomerKey()"
            (change)="onCustomerChange($event)"
          >
            <option value="" disabled i18n="@@customerSelectorPlaceholder">-- Please select a customer --</option>
            <option *ngFor="let customer of availableCustomers" [value]="customer.config.customerKey">
              {{ customer.config.customerKey }} - {{ customer.config.customerName }}
            </option>
          </select>

          <div *ngIf="selectedCustomer()" class="customer-info">
            <h3>{{ selectedCustomer()!.config.customerName }}</h3>
            <p class="customer-key">Customer ID: <strong>{{ selectedCustomer()!.config.customerKey }}</strong></p>
            <button
              type="button"
              class="navigate-btn"
              (click)="navigateToCustomer()"
            >
              <span i18n="@@customerSelectorNavigateButton">View Architecture</span>
            </button>
          </div>
        </div>
      </main>
    </div>
  `,
  styles: [
    `
      .customer-selector-page {
        min-height: 100vh;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
      }

      .customer-selector-header {
        text-align: center;
        margin-bottom: 3rem;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
      }

      .customer-selector-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 1rem;
      }

      .customer-selector-header .subtitle {
        font-size: 1.125rem;
        color: #666;
        line-height: 1.6;
      }

      .customer-selector-main {
        max-width: 600px;
        margin: 0 auto;
      }

      .selector-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      }

      .selector-label {
        display: block;
        font-size: 1rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.75rem;
      }

      .customer-select {
        width: 100%;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        border: 2px solid #ddd;
        border-radius: 8px;
        background: white;
        color: #333;
        cursor: pointer;
        transition: border-color 0.2s;
      }

      .customer-select:hover {
        border-color: #999;
      }

      .customer-select:focus {
        outline: none;
        border-color: var(--microsoft-orange-medium, #ff8c00);
        box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.1);
      }

      .customer-info {
        margin-top: 2rem;
        padding-top: 2rem;
        border-top: 2px solid #eee;
      }

      .customer-info h3 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
      }

      .customer-key {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 1.5rem;
      }

      .customer-key strong {
        color: #333;
        font-family: monospace;
        background: #f5f5f5;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
      }

      .navigate-btn {
        width: 100%;
        padding: 0.875rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        color: white;
        background: var(--microsoft-orange-medium, #ff8c00);
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.2s, transform 0.1s;
      }

      .navigate-btn:hover {
        background: var(--microsoft-orange-dark, #e67e00);
        transform: translateY(-1px);
      }

      .navigate-btn:active {
        transform: translateY(0);
      }

      .navigate-btn:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.3);
      }
    `,
  ],
})
export class CustomerSelectorPageComponent {
  /**
   * Available customer configurations
   */
  readonly availableCustomers: CustomerOption[] = [
    {
      config: FMF_CONFIG,
      route: '/dsp/customer/fmf',
    },
    {
      config: ECME_CONFIG,
      route: '/dsp/customer/ecme',
    },
  ];

  /**
   * Currently selected customer key
   */
  readonly selectedCustomerKey = signal<string>('');

  /**
   * Currently selected customer option
   */
  readonly selectedCustomer = signal<CustomerOption | null>(null);

  constructor(private readonly router: Router) {}

  /**
   * Handle customer selection change
   */
  onCustomerChange(event: Event): void {
    const selectElement = event.target as HTMLSelectElement;
    const customerKey = selectElement.value;
    this.selectedCustomerKey.set(customerKey);

    const customer = this.availableCustomers.find((c) => c.config.customerKey === customerKey);
    this.selectedCustomer.set(customer || null);
  }

  /**
   * Navigate to selected customer's DSP architecture page
   */
  navigateToCustomer(): void {
    const customer = this.selectedCustomer();
    if (customer) {
      // Get current locale from URL or default to 'en'
      const currentUrl = this.router.url;
      const localeMatch = currentUrl.match(/^\/(en|de|fr)\//);
      const locale = localeMatch ? localeMatch[1] : 'en';

      // Navigate to customer page with locale
      this.router.navigate([locale, ...customer.route.split('/').filter(Boolean)]);
    }
  }
}
