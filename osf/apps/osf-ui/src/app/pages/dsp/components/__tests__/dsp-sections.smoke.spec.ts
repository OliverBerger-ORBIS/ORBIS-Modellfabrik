import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { DspOverviewSectionComponent } from '../dsp-overview-section/dsp-overview-section.component';
import { DspMethodologySectionComponent } from '../dsp-methodology-section/dsp-methodology-section.component';
import { DspUseCasesSectionComponent } from '../dsp-use-cases-section/dsp-use-cases-section.component';
import { DspArchitectureFunctionalSectionComponent } from '../dsp-architecture-functional-section/dsp-architecture-functional-section.component';
import { DspArchitectureComponentSectionComponent } from '../dsp-architecture-component-section/dsp-architecture-component-section.component';
import { DspArchitectureDeploymentSectionComponent } from '../dsp-architecture-deployment-section/dsp-architecture-deployment-section.component';
import { DspAnimationComponent } from '../../../../components/dsp-animation/dsp-animation.component';
import { ExternalLinksService } from '../../../../services/external-links.service';
import { LanguageService } from '../../../../services/language.service';
import type { CustomerDspConfig } from '../../../../components/dsp-animation/configs/types';
import type { ViewMode } from '../../../../components/dsp-animation/types';

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

const wrapperCases = [
  { component: DspOverviewSectionComponent, selector: 'app-dsp-overview-section' },
  { component: DspMethodologySectionComponent, selector: 'app-dsp-methodology-section' },
  { component: DspUseCasesSectionComponent, selector: 'app-dsp-use-cases-section' },
] as const;

describe('DSP section components (Tier A smoke)', () => {
  for (const { component, selector } of wrapperCases) {
    it(`should render ${selector}`, async () => {
      await TestBed.configureTestingModule({
        imports: [component],
        providers: [
          provideRouter([]),
          { provide: LanguageService, useValue: { current: 'en' } },
        ],
      }).compileComponents();
      const fixture = TestBed.createComponent(component);
      fixture.detectChanges();
      expect(fixture.nativeElement.querySelector(selector) ?? fixture.nativeElement.tagName.toLowerCase()).toBeTruthy();
    });
  }

  describe('architecture sections with mocked animation', () => {
    let router: Router;

    beforeEach(async () => {
      await TestBed.configureTestingModule({
        imports: [
          DspArchitectureFunctionalSectionComponent,
          DspArchitectureComponentSectionComponent,
          DspArchitectureDeploymentSectionComponent,
        ],
        providers: [
          provideRouter([]),
          {
            provide: ExternalLinksService,
            useValue: { current: { bpErpApplicationUrl: 'process' } },
          },
          { provide: LanguageService, useValue: { current: 'en' } },
        ],
      })
        .overrideComponent(DspArchitectureFunctionalSectionComponent, {
          remove: { imports: [DspAnimationComponent] },
          add: { imports: [MockDspAnimationComponent] },
        })
        .overrideComponent(DspArchitectureComponentSectionComponent, {
          remove: { imports: [DspAnimationComponent] },
          add: { imports: [MockDspAnimationComponent] },
        })
        .overrideComponent(DspArchitectureDeploymentSectionComponent, {
          remove: { imports: [DspAnimationComponent] },
          add: { imports: [MockDspAnimationComponent] },
        })
        .compileComponents();

      router = TestBed.inject(Router);
      jest.spyOn(router, 'navigate').mockResolvedValue(true);
      jest.spyOn(router, 'navigateByUrl').mockResolvedValue(true);
    });

    it('should render functional architecture section', () => {
      const fixture = TestBed.createComponent(DspArchitectureFunctionalSectionComponent);
      fixture.detectChanges();
      expect(fixture.componentInstance.viewMode).toBe('functional');
      expect(fixture.nativeElement.querySelector('.mock-dsp-animation')).toBeTruthy();
    });

    it('should navigate on shopfloor device action', () => {
      const fixture = TestBed.createComponent(DspArchitectureFunctionalSectionComponent);
      fixture.componentInstance.onActionTriggered({ id: 'sf-device-mill', url: 'shopfloor' });
      expect(router.navigate).toHaveBeenCalled();
    });

    it('should render component architecture section', () => {
      const fixture = TestBed.createComponent(DspArchitectureComponentSectionComponent);
      fixture.detectChanges();
      expect(fixture.componentInstance.viewMode).toBe('component');
    });

    it('should render deployment architecture section', () => {
      const fixture = TestBed.createComponent(DspArchitectureDeploymentSectionComponent);
      fixture.detectChanges();
      expect(fixture.componentInstance.viewMode).toBe('deployment');
    });
  });
});
