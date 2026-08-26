import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter, Router } from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { DspPageComponent } from './dsp-page.component';
import { DSP_RETURN_SECTION_SESSION_KEY } from './dsp-accordion-sections';
import { DspOverviewSectionComponent } from './components/dsp-overview-section/dsp-overview-section.component';
import { DspArchitectureFunctionalSectionComponent } from './components/dsp-architecture-functional-section/dsp-architecture-functional-section.component';
import { DspArchitectureComponentSectionComponent } from './components/dsp-architecture-component-section/dsp-architecture-component-section.component';
import { DspArchitectureDeploymentSectionComponent } from './components/dsp-architecture-deployment-section/dsp-architecture-deployment-section.component';
import { DspUseCasesSectionComponent } from './components/dsp-use-cases-section/dsp-use-cases-section.component';
import { DspMethodologySectionComponent } from './components/dsp-methodology-section/dsp-methodology-section.component';
import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({ standalone: true, selector: 'app-dsp-overview-section', template: '', changeDetection: ChangeDetectionStrategy.OnPush })
class MockOverviewSectionComponent {}

@Component({ standalone: true, selector: 'app-dsp-architecture-functional-section', template: '', changeDetection: ChangeDetectionStrategy.OnPush })
class MockArchFunctionalSectionComponent {}

@Component({ standalone: true, selector: 'app-dsp-architecture-component-section', template: '', changeDetection: ChangeDetectionStrategy.OnPush })
class MockArchComponentSectionComponent {}

@Component({ standalone: true, selector: 'app-dsp-architecture-deployment-section', template: '', changeDetection: ChangeDetectionStrategy.OnPush })
class MockArchDeploymentSectionComponent {}

@Component({ standalone: true, selector: 'app-dsp-use-cases-section', template: '', changeDetection: ChangeDetectionStrategy.OnPush })
class MockUseCasesSectionComponent {}

@Component({ standalone: true, selector: 'app-dsp-methodology-section', template: '', changeDetection: ChangeDetectionStrategy.OnPush })
class MockMethodologySectionComponent {}

describe('DspPageComponent', () => {
  let fixture: ComponentFixture<DspPageComponent>;
  let component: DspPageComponent;
  let queryParamMap$: BehaviorSubject<ReturnType<typeof convertToParamMap>>;
  let router: Router;

  beforeEach(async () => {
    localStorage.removeItem('dsp-page-accordion-expanded-sections');
    sessionStorage.clear();
    queryParamMap$ = new BehaviorSubject(convertToParamMap({}));

    await TestBed.configureTestingModule({
      imports: [DspPageComponent],
      providers: [
        provideRouter([]),
        {
          provide: ActivatedRoute,
          useValue: {
            queryParamMap: queryParamMap$.asObservable(),
            snapshot: { queryParamMap: convertToParamMap({}) },
          },
        },
      ],
    })
      .overrideComponent(DspPageComponent, {
        remove: {
          imports: [
            DspOverviewSectionComponent,
            DspArchitectureFunctionalSectionComponent,
            DspArchitectureComponentSectionComponent,
            DspArchitectureDeploymentSectionComponent,
            DspUseCasesSectionComponent,
            DspMethodologySectionComponent,
          ],
        },
        add: {
          imports: [
            MockOverviewSectionComponent,
            MockArchFunctionalSectionComponent,
            MockArchComponentSectionComponent,
            MockArchDeploymentSectionComponent,
            MockUseCasesSectionComponent,
            MockMethodologySectionComponent,
          ],
        },
      })
      .compileComponents();

    fixture = TestBed.createComponent(DspPageComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    jest.spyOn(router, 'navigate').mockResolvedValue(true);
    fixture.detectChanges();
  });

  afterEach(() => {
    fixture?.destroy();
    localStorage.removeItem('dsp-page-accordion-expanded-sections');
  });

  it('should create and expand overview by default', () => {
    expect(component).toBeTruthy();
    expect((component as unknown as { isSectionExpanded: (id: string) => boolean }).isSectionExpanded('overview')).toBe(
      true
    );
  });

  it('should toggle accordion sections', () => {
    const toggle = (component as unknown as { toggleSection: (id: string) => void }).toggleSection.bind(component);
    const isExpanded = (component as unknown as { isSectionExpanded: (id: string) => boolean }).isSectionExpanded.bind(
      component
    );

    toggle('methodology');
    expect(isExpanded('methodology')).toBe(true);
    toggle('methodology');
    expect(isExpanded('methodology')).toBe(false);
  });

  it('should expand section from query param and strip param', () => {
    queryParamMap$.next(convertToParamMap({ section: 'use-cases' }));
    fixture.detectChanges();
    expect(
      (component as unknown as { isSectionExpanded: (id: string) => boolean }).isSectionExpanded('use-cases')
    ).toBe(true);
    expect(router.navigate).toHaveBeenCalled();
  });

  it('should restore accordion section from sessionStorage', () => {
    sessionStorage.setItem(DSP_RETURN_SECTION_SESSION_KEY, 'methodology');
    fixture.destroy();
    fixture = TestBed.createComponent(DspPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    expect(
      (component as unknown as { isSectionExpanded: (id: string) => boolean }).isSectionExpanded('methodology')
    ).toBe(true);
  });
});
