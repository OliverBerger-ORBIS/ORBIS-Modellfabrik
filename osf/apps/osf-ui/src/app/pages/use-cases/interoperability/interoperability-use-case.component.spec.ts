import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';
import { InteroperabilityUseCaseComponent } from './interoperability-use-case.component';
import { Uc00SvgGeneratorService } from './uc-00-svg-generator.service';
import { Uc00I18nService } from './uc-00-i18n.service';
import { LanguageService } from '../../../services/language.service';
import { ViewScaleService } from '../../../services/view-scale.service';
import { NavigationBackService } from '../../../services/navigation-back.service';
import type { UseCaseStep } from '../shared/base-use-case.component';

const STEPS: UseCaseStep[] = [
  {
    id: 's0',
    title: { de: 'Start', en: 'Start' },
    description: { de: 'D0', en: 'D0' },
    highlightIds: [],
    hideIds: [],
  },
  {
    id: 's1',
    title: { de: 'Weiter', en: 'Next' },
    description: { de: 'D1', en: 'D1' },
    highlightIds: ['uc00_box_a'],
    hideIds: [],
  },
];

describe('InteroperabilityUseCaseComponent', () => {
  let component: InteroperabilityUseCaseComponent;
  let fixture: ComponentFixture<InteroperabilityUseCaseComponent>;
  let viewScale: ViewScaleService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InteroperabilityUseCaseComponent],
      providers: [
        ViewScaleService,
        { provide: HttpClient, useValue: { get: jest.fn(() => of(STEPS)) } },
        {
          provide: Uc00SvgGeneratorService,
          useValue: {
            generateSvg: jest.fn(
              () =>
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 80"><g id="uc00_root"></g></svg>'
            ),
          },
        },
        {
          provide: Uc00I18nService,
          useValue: { loadTexts: jest.fn(async () => ({ 'uc00.title': 'Interop' })) },
        },
        { provide: LanguageService, useValue: { current: 'en' } },
        { provide: NavigationBackService, useValue: { backOrNavigate: jest.fn() } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(InteroperabilityUseCaseComponent);
    component = fixture.componentInstance;
    viewScale = TestBed.inject(ViewScaleService);
  }, 20000);

  afterEach(() => {
    fixture?.destroy();
  });

  it('should create and expose UC-00 step metadata', () => {
    expect(component).toBeTruthy();
    expect(component.getStepsUrl()).toContain('uc-00');
    expect(component.getStepPrefix()).toBe('uc00');
    expect(component.getConnectionIds()).toEqual([]);
  });

  it('should load steps and SVG via BaseUseCase init', fakeAsync(() => {
    fixture.detectChanges();
    tick(200);
    fixture.detectChanges();
    expect(component.steps).toHaveLength(2);
    expect(component.isLoading).toBe(false);
    expect(component.svgContent).toBeTruthy();
  }));

  it('should advance steps and sync zoom through ViewScaleService', fakeAsync(() => {
    fixture.detectChanges();
    tick(200);
    expect(component.currentStepIndex).toBe(0);
    (component as unknown as { nextStep: () => void }).nextStep();
    tick(0);
    expect(component.currentStepIndex).toBe(1);

    (component as unknown as { zoomIn: () => void }).zoomIn();
    expect(component.zoom).toBeGreaterThan(1);
    expect(viewScale.current).toBe(component.zoom);

    (component as unknown as { resetZoom: () => void }).resetZoom();
    expect(component.zoom).toBe(1);
    tick(200);
  }));
});
