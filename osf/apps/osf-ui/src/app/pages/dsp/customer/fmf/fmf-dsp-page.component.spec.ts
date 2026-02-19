import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, provideRouter } from '@angular/router';
import { FmfDspPageComponent } from './fmf-dsp-page.component';
import { DspAnimationComponent } from '../../../../components/dsp-animation/dsp-animation.component';
import { DebugElement, Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { By } from '@angular/platform-browser';
import { of } from 'rxjs';
import type { CustomerDspConfig } from '../../../../components/dsp-animation/configs/types';
import type { ViewMode } from '../../../../components/dsp-animation/types';

const mockActivatedRoute = {
  snapshot: { queryParams: {} },
  queryParams: of({}),
};

// Mock DspAnimationComponent to avoid complex dependencies
@Component({
  selector: 'app-dsp-animation',
  standalone: true,
  template: '<div class="mock-dsp-animation"></div>',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
class MockDspAnimationComponent {
  @Input() viewMode?: ViewMode;
  @Input() customerConfig?: CustomerDspConfig;
  @Input() initialStep?: number;
}

describe('FmfDspPageComponent', () => {
  let component: FmfDspPageComponent;
  let fixture: ComponentFixture<FmfDspPageComponent>;
  let compiled: DebugElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FmfDspPageComponent],
      providers: [
        provideRouter([]),
        { provide: ActivatedRoute, useValue: mockActivatedRoute },
      ],
    })
      .overrideComponent(FmfDspPageComponent, {
        remove: { imports: [DspAnimationComponent] },
        add: { imports: [MockDspAnimationComponent] },
      })
      .compileComponents();

    fixture = TestBed.createComponent(FmfDspPageComponent);
    component = fixture.componentInstance;
    compiled = fixture.debugElement;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have FMF config', () => {
    expect(component.config).toBeDefined();
    expect(component.config.customerKey).toBe('fmf');
    expect(component.config.customerName).toBe('Fischertechnik Modellfabrik');
  });

  it('should initialize with functional view mode', () => {
    expect(component.currentViewMode()).toBe('functional');
  });

  it('should have three view mode options', () => {
    expect(component.viewModes).toHaveLength(3);
    expect(component.viewModes.map(m => m.value)).toEqual([
      'functional',
      'component',
      'deployment',
    ]);
  });

  it('should render customer name in header', () => {
    const header = compiled.query(By.css('h1'));
    expect(header.nativeElement.textContent).toContain('Fischertechnik Modellfabrik');
  });

  it('should render subtitle', () => {
    const subtitle = compiled.query(By.css('.subtitle'));
    expect(subtitle).toBeTruthy();
    expect(subtitle.nativeElement.textContent).toContain('Interactive demonstration');
  });

  it('should render view mode selector buttons', () => {
    const buttons = compiled.queryAll(By.css('.view-mode-btn'));
    expect(buttons).toHaveLength(3);
    expect(buttons[0].nativeElement.textContent).toContain('Functional View');
    expect(buttons[1].nativeElement.textContent).toContain('Component View');
    expect(buttons[2].nativeElement.textContent).toContain('Deployment View');
  });

  it('should have active class on functional view button by default', () => {
    const buttons = compiled.queryAll(By.css('.view-mode-btn'));
    expect(buttons[0].nativeElement.classList.contains('active')).toBe(true);
    expect(buttons[1].nativeElement.classList.contains('active')).toBe(false);
    expect(buttons[2].nativeElement.classList.contains('active')).toBe(false);
  });

  it('should switch view mode when button clicked', () => {
    const buttons = compiled.queryAll(By.css('.view-mode-btn'));
    
    // Click component view button
    buttons[1].nativeElement.click();
    fixture.detectChanges();
    
    expect(component.currentViewMode()).toBe('component');
    expect(buttons[0].nativeElement.classList.contains('active')).toBe(false);
    expect(buttons[1].nativeElement.classList.contains('active')).toBe(true);
    expect(buttons[2].nativeElement.classList.contains('active')).toBe(false);
  });

  it('should pass customer config to dsp-animation component', () => {
    const animationComponent = compiled.query(By.css('app-dsp-animation'));
    expect(animationComponent).toBeTruthy();
  });

  it('should update view mode via setViewMode method', () => {
    component.setViewMode('deployment');
    expect(component.currentViewMode()).toBe('deployment');
    
    component.setViewMode('component');
    expect(component.currentViewMode()).toBe('component');
    
    component.setViewMode('functional');
    expect(component.currentViewMode()).toBe('functional');
  });

  it('should have correct CSS classes on page container', () => {
    const container = compiled.query(By.css('.customer-dsp-page'));
    expect(container).toBeTruthy();
  });

  it('should have correct CSS classes on header', () => {
    const header = compiled.query(By.css('.customer-header'));
    expect(header).toBeTruthy();
  });

  it('should have FMF config with devices', () => {
    expect(component.config.sfDevices).toBeDefined();
    expect(component.config.sfDevices.length).toBeGreaterThan(0);
  });

  it('should have FMF config with systems', () => {
    expect(component.config.sfSystems).toBeDefined();
    expect(component.config.sfSystems.length).toBeGreaterThan(0);
  });

  it('should have FMF config with business processes', () => {
    expect(component.config.bpProcesses).toBeDefined();
    expect(component.config.bpProcesses.length).toBeGreaterThan(0);
  });
});
