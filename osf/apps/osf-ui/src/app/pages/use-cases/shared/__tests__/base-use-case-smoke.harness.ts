import { Type } from '@angular/core';
import { TestBed, ComponentFixture } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';
import { ViewScaleService } from '../../../../services/view-scale.service';
import { LanguageService } from '../../../../services/language.service';
import { NavigationBackService } from '../../../../services/navigation-back.service';
import type { UseCaseStep } from '../base-use-case.component';

/** Public surface exercised by Tier-A use-case smoke tests. */
export interface UseCaseSmokeInstance {
  getStepsUrl(): string;
  getStepPrefix(): string;
  steps: UseCaseStep[];
  isLoading: boolean;
  svgContent: unknown;
}

export const DEFAULT_USE_CASE_STEPS: UseCaseStep[] = [
  {
    id: 's0',
    title: { de: 'Start', en: 'Start' },
    description: { de: 'D0', en: 'D0' },
    highlightIds: [],
    hideIds: [],
  },
];

export async function setupBaseUseCaseSmoke(
  componentClass: Type<UseCaseSmokeInstance>,
  extraProviders: unknown[] = []
): Promise<{ fixture: ComponentFixture<UseCaseSmokeInstance>; component: UseCaseSmokeInstance }> {
  await TestBed.configureTestingModule({
    imports: [componentClass],
    providers: [
      ViewScaleService,
      { provide: HttpClient, useValue: { get: jest.fn(() => of(DEFAULT_USE_CASE_STEPS)) } },
      { provide: LanguageService, useValue: { current: 'en' } },
      { provide: NavigationBackService, useValue: { backOrNavigate: jest.fn() } },
      ...extraProviders,
    ],
  }).compileComponents();

  const fixture = TestBed.createComponent(componentClass);
  return { fixture, component: fixture.componentInstance };
}

export function mockSvgGeneratorProvider(token: unknown): { provide: unknown; useValue: { generateSvg: jest.Mock } } {
  return {
    provide: token,
    useValue: {
      generateSvg: jest.fn(
        () =>
          '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 80"><g id="uc_root"></g></svg>'
      ),
    },
  };
}

export function mockI18nProvider(token: unknown): {
  provide: unknown;
  useValue: { loadTexts: jest.Mock };
} {
  return {
    provide: token,
    useValue: { loadTexts: jest.fn(async () => ({ 'uc.title': 'Smoke' })) },
  };
}
