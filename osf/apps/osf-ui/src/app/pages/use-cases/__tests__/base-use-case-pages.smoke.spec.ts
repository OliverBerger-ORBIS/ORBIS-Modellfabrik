import { fakeAsync, tick } from '@angular/core/testing';
import { ClosedLoopQualityUseCaseComponent } from '../closed-loop-quality/closed-loop-quality-use-case.component';
import { Uc04SvgGeneratorService } from '../closed-loop-quality/uc-04-svg-generator.service';
import { Uc04I18nService } from '../closed-loop-quality/uc-04-i18n.service';
import { AnomalyDetectionUseCaseComponent } from '../anomaly-detection/anomaly-detection-use-case.component';
import { Uc07SvgGeneratorService } from '../anomaly-detection/uc-07-svg-generator.service';
import { Uc07I18nService } from '../anomaly-detection/uc-07-i18n.service';
import { ProcessOptimizationUseCaseComponent } from '../process-optimization/process-optimization-use-case.component';
import { Uc06SvgGeneratorService } from '../process-optimization/uc-06-svg-generator.service';
import { Uc06I18nService } from '../process-optimization/uc-06-i18n.service';
import { ThreeDataPoolsUseCaseComponent } from '../three-data-pools/three-data-pools-use-case.component';
import { Uc02SvgGeneratorService } from '../three-data-pools/uc-02-svg-generator.service';
import { Uc02SvgGeneratorLanesService } from '../three-data-pools/uc-02-svg-generator-lanes.service';
import { Uc02I18nService } from '../three-data-pools/uc-02-i18n.service';
import { AiLifecycleUseCaseComponent } from '../ai-lifecycle/ai-lifecycle-use-case.component';
import { Uc03SvgGeneratorService } from '../ai-lifecycle/uc-03-svg-generator.service';
import { Uc03I18nService } from '../ai-lifecycle/uc-03-i18n.service';
import { TrackTraceGenealogyUseCaseComponent } from '../track-trace-genealogy/track-trace-genealogy-use-case.component';
import { Uc01SvgGeneratorService } from '../track-trace-genealogy/uc-01-svg-generator.service';
import { Uc01I18nService } from '../track-trace-genealogy/uc-01-i18n.service';
import {
  mockI18nProvider,
  mockSvgGeneratorProvider,
  setupBaseUseCaseSmoke,
  type UseCaseSmokeInstance,
} from '../shared/__tests__/base-use-case-smoke.harness';
import type { Type } from '@angular/core';

describe('Base use-case pages (Tier A smoke)', () => {
  const cases: ReadonlyArray<{
    name: string;
    component: Type<UseCaseSmokeInstance>;
    providers: unknown[];
    stepsUrlPart: string;
    stepPrefix: string;
  }> = [
    {
      name: 'ClosedLoopQualityUseCaseComponent',
      component: ClosedLoopQualityUseCaseComponent,
      providers: [
        mockSvgGeneratorProvider(Uc04SvgGeneratorService),
        mockI18nProvider(Uc04I18nService),
      ],
      stepsUrlPart: 'uc-04',
      stepPrefix: 'uc04',
    },
    {
      name: 'AnomalyDetectionUseCaseComponent',
      component: AnomalyDetectionUseCaseComponent,
      providers: [
        mockSvgGeneratorProvider(Uc07SvgGeneratorService),
        mockI18nProvider(Uc07I18nService),
      ],
      stepsUrlPart: 'uc-07',
      stepPrefix: 'uc07',
    },
    {
      name: 'ProcessOptimizationUseCaseComponent',
      component: ProcessOptimizationUseCaseComponent,
      providers: [
        mockSvgGeneratorProvider(Uc06SvgGeneratorService),
        mockI18nProvider(Uc06I18nService),
      ],
      stepsUrlPart: 'uc-06',
      stepPrefix: 'uc06',
    },
    {
      name: 'ThreeDataPoolsUseCaseComponent',
      component: ThreeDataPoolsUseCaseComponent,
      providers: [
        mockSvgGeneratorProvider(Uc02SvgGeneratorService),
        {
          provide: Uc02SvgGeneratorLanesService,
          useValue: {
            generateSvg: jest.fn(
              () =>
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 80"><g id="uc02_lanes"></g></svg>'
            ),
          },
        },
        mockI18nProvider(Uc02I18nService),
      ],
      stepsUrlPart: 'uc-02',
      stepPrefix: 'uc02',
    },
    {
      name: 'AiLifecycleUseCaseComponent',
      component: AiLifecycleUseCaseComponent,
      providers: [
        mockSvgGeneratorProvider(Uc03SvgGeneratorService),
        mockI18nProvider(Uc03I18nService),
      ],
      stepsUrlPart: 'uc-03',
      stepPrefix: 'uc03',
    },
    {
      name: 'TrackTraceGenealogyUseCaseComponent',
      component: TrackTraceGenealogyUseCaseComponent,
      providers: [
        mockSvgGeneratorProvider(Uc01SvgGeneratorService),
        mockI18nProvider(Uc01I18nService),
      ],
      stepsUrlPart: 'uc-01',
      stepPrefix: 'uc01',
    },
  ];

  for (const config of cases) {
    describe(config.name, () => {
      it('should create and expose step metadata', async () => {
        const { component } = await setupBaseUseCaseSmoke(config.component, [...config.providers]);
        expect(component.getStepsUrl()).toContain(config.stepsUrlPart);
        expect(component.getStepPrefix()).toBe(config.stepPrefix);
      });

      it('should load steps and SVG on init', fakeAsync(async () => {
        const { fixture, component } = await setupBaseUseCaseSmoke(config.component, [...config.providers]);
        fixture.detectChanges();
        tick(200);
        fixture.detectChanges();
        expect(component.steps.length).toBeGreaterThan(0);
        expect(component.isLoading).toBe(false);
        expect(component.svgContent).toBeTruthy();
      }));
    });
  }
});
