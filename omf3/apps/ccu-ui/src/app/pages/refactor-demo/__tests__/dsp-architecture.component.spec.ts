import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';
import { DspArchitecturePageComponent } from '../dsp-architecture.component';
import { DspArchitectureConfigService } from '../../../services/dsp-architecture-config.service';
import type { ViewMode } from '../../../components/dsp-animation/types';

describe('DspArchitecturePageComponent', () => {
  let component: DspArchitecturePageComponent;
  let fixture: ComponentFixture<DspArchitecturePageComponent>;

  beforeEach(async () => {
    const httpMock = {
      get: jest.fn(() => of({})),
    };

    const configServiceMock = {
      loadConfiguration: jest.fn(() => of({})),
    };

    await TestBed.configureTestingModule({
      imports: [DspArchitecturePageComponent],
      providers: [
        { provide: HttpClient, useValue: httpMock },
        { provide: DspArchitectureConfigService, useValue: configServiceMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(DspArchitecturePageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have default viewMode as functional', () => {
    expect(component['viewMode']).toBe('functional');
  });

  it('should have page title defined', () => {
    expect(component['pageTitle']).toBeDefined();
  });

  it('should have page description defined', () => {
    expect(component['pageDescription']).toBeDefined();
  });

  it('should have view mode labels defined', () => {
    expect(component['labelViewMode']).toBeDefined();
    expect(component['labelFunctional']).toBeDefined();
    expect(component['labelComponent']).toBeDefined();
    expect(component['labelDeployment']).toBeDefined();
  });

  it('should select view mode', () => {
    component['selectViewMode']('component');
    expect(component['viewMode']).toBe('component');
  });

  it('should handle action triggered', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
    const event = { id: 'test-id', url: 'test-url' };
    
    component['onActionTriggered'](event);
    
    expect(consoleSpy).toHaveBeenCalledWith('Action triggered:', event);
    consoleSpy.mockRestore();
  });

  it('should render DspAnimationComponent', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const dspAnimation = compiled.querySelector('app-dsp-animation');
    expect(dspAnimation).toBeTruthy();
  });
});

