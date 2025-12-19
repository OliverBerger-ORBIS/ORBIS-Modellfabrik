import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CustomerSelectorPageComponent } from './customer-selector-page.component';
import { Router } from '@angular/router';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';
import { FMF_CONFIG } from '../../../components/dsp-animation/configs/fmf/fmf-config';
import { ECME_CONFIG } from '../../../components/dsp-animation/configs/ecme/ecme-config';

describe('CustomerSelectorPageComponent', () => {
  let component: CustomerSelectorPageComponent;
  let fixture: ComponentFixture<CustomerSelectorPageComponent>;
  let compiled: DebugElement;
  let router: Router & { navigate: jest.Mock; url: string };
  let navigateSpy: jest.Mock;

  beforeEach(async () => {
    navigateSpy = jest.fn();
    const routerSpy = {
      navigate: navigateSpy,
      url: '/en/dsp/customer',
    };

    await TestBed.configureTestingModule({
      imports: [CustomerSelectorPageComponent],
      providers: [
        { provide: Router, useValue: routerSpy },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(CustomerSelectorPageComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router) as Router & { navigate: jest.Mock; url: string };
    compiled = fixture.debugElement;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have available customers', () => {
    expect(component.availableCustomers).toBeDefined();
    expect(component.availableCustomers.length).toBeGreaterThan(0);
  });

  it('should include FMF and ECME customers', () => {
    const customerKeys = component.availableCustomers.map(c => c.config.customerKey);
    expect(customerKeys).toContain('fmf');
    expect(customerKeys).toContain('ecme');
  });

  it('should have correct routes for customers', () => {
    const fmfCustomer = component.availableCustomers.find(c => c.config.customerKey === 'fmf');
    expect(fmfCustomer).toBeDefined();
    expect(fmfCustomer!.route).toBe('/dsp/customer/fmf');

    const ecmeCustomer = component.availableCustomers.find(c => c.config.customerKey === 'ecme');
    expect(ecmeCustomer).toBeDefined();
    expect(ecmeCustomer!.route).toBe('/dsp/customer/ecme');
  });

  it('should initialize with empty selected customer', () => {
    expect(component.selectedCustomerKey()).toBe('');
    expect(component.selectedCustomer()).toBeNull();
  });

  it('should render header with title', () => {
    const header = compiled.query(By.css('.customer-selector-header h1'));
    expect(header).toBeTruthy();
    expect(header.nativeElement.textContent).toContain('DSP Customer Architecture');
  });

  it('should render subtitle', () => {
    const subtitle = compiled.query(By.css('.subtitle'));
    expect(subtitle).toBeTruthy();
    expect(subtitle.nativeElement.textContent).toContain('Select a customer');
  });

  it('should render customer select dropdown', () => {
    const select = compiled.query(By.css('#customer-select'));
    expect(select).toBeTruthy();
  });

  it('should have placeholder option in select', () => {
    const select = compiled.query(By.css('#customer-select'));
    const options = select.nativeElement.querySelectorAll('option');
    expect(options.length).toBeGreaterThan(0);
    expect(options[0].textContent).toContain('Please select a customer');
    expect(options[0].disabled).toBe(true);
  });

  it('should have customer options in select', () => {
    const select = compiled.query(By.css('#customer-select'));
    const options = select.nativeElement.querySelectorAll('option');
    // First option is placeholder, rest are customers
    expect(options.length).toBe(component.availableCustomers.length + 1);
    
    // Check that customer options are present
    const customerOptions = Array.from(options).slice(1) as HTMLOptionElement[];
    customerOptions.forEach((option, index) => {
      const customer = component.availableCustomers[index];
      expect(option.value).toBe(customer.config.customerKey);
      expect(option.textContent).toContain(customer.config.customerKey);
      expect(option.textContent).toContain(customer.config.customerName);
    });
  });

  it('should not show customer info initially', () => {
    const customerInfo = compiled.query(By.css('.customer-info'));
    expect(customerInfo).toBeNull();
  });

  it('should update selected customer when select changes', () => {
    const select = compiled.query(By.css('#customer-select'));
    const selectElement = select.nativeElement as HTMLSelectElement;
    
    // Select FMF customer
    selectElement.value = 'fmf';
    selectElement.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    expect(component.selectedCustomerKey()).toBe('fmf');
    expect(component.selectedCustomer()).toBeDefined();
    expect(component.selectedCustomer()!.config.customerKey).toBe('fmf');
  });

  it('should show customer info when customer is selected', () => {
    const select = compiled.query(By.css('#customer-select'));
    const selectElement = select.nativeElement as HTMLSelectElement;
    
    // Select FMF customer
    selectElement.value = 'fmf';
    selectElement.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    const customerInfo = compiled.query(By.css('.customer-info'));
    expect(customerInfo).toBeTruthy();
    
    const customerName = customerInfo.query(By.css('h3'));
    expect(customerName.nativeElement.textContent).toContain(FMF_CONFIG.customerName);
    
    const customerKey = customerInfo.query(By.css('.customer-key'));
    expect(customerKey.nativeElement.textContent).toContain('fmf');
  });

  it('should render navigate button when customer is selected', () => {
    const select = compiled.query(By.css('#customer-select'));
    const selectElement = select.nativeElement as HTMLSelectElement;
    
    // Select FMF customer
    selectElement.value = 'fmf';
    selectElement.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    const navigateButton = compiled.query(By.css('.navigate-btn'));
    expect(navigateButton).toBeTruthy();
  });

  it('should navigate to customer page when button clicked', () => {
    const select = compiled.query(By.css('#customer-select'));
    const selectElement = select.nativeElement as HTMLSelectElement;
    
    // Select FMF customer
    selectElement.value = 'fmf';
    selectElement.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    const navigateButton = compiled.query(By.css('.navigate-btn'));
    navigateButton.nativeElement.click();

    expect(navigateSpy).toHaveBeenCalledWith(['en', 'dsp', 'customer', 'fmf']);
  });

  it('should extract locale from current URL for navigation', () => {
    router.url = '/de/dsp/customer';
    
    const select = compiled.query(By.css('#customer-select'));
    const selectElement = select.nativeElement as HTMLSelectElement;
    
    // Select ECME customer
    selectElement.value = 'ecme';
    selectElement.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    const navigateButton = compiled.query(By.css('.navigate-btn'));
    navigateButton.nativeElement.click();

    expect(navigateSpy).toHaveBeenCalledWith(['de', 'dsp', 'customer', 'ecme']);
  });

  it('should default to en locale if no locale in URL', () => {
    router.url = '/dsp/customer';
    
    const select = compiled.query(By.css('#customer-select'));
    const selectElement = select.nativeElement as HTMLSelectElement;
    
    // Select FMF customer
    selectElement.value = 'fmf';
    selectElement.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    const navigateButton = compiled.query(By.css('.navigate-btn'));
    navigateButton.nativeElement.click();

    expect(navigateSpy).toHaveBeenCalledWith(['en', 'dsp', 'customer', 'fmf']);
  });

  it('should handle customer change event correctly', () => {
    const select = compiled.query(By.css('#customer-select'));
    const selectElement = select.nativeElement as HTMLSelectElement;
    
    // Initially no customer selected
    expect(component.selectedCustomerKey()).toBe('');
    
    // Select ECME
    selectElement.value = 'ecme';
    selectElement.dispatchEvent(new Event('change'));
    fixture.detectChanges();
    
    expect(component.selectedCustomerKey()).toBe('ecme');
    expect(component.selectedCustomer()!.config).toBe(ECME_CONFIG);
    
    // Change to FMF
    selectElement.value = 'fmf';
    selectElement.dispatchEvent(new Event('change'));
    fixture.detectChanges();
    
    expect(component.selectedCustomerKey()).toBe('fmf');
    expect(component.selectedCustomer()!.config).toBe(FMF_CONFIG);
  });

  it('should have correct CSS classes', () => {
    const page = compiled.query(By.css('.customer-selector-page'));
    expect(page).toBeTruthy();
    
    const header = compiled.query(By.css('.customer-selector-header'));
    expect(header).toBeTruthy();
    
    const main = compiled.query(By.css('.customer-selector-main'));
    expect(main).toBeTruthy();
    
    const card = compiled.query(By.css('.selector-card'));
    expect(card).toBeTruthy();
  });
});
