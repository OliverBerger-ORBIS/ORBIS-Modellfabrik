import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { UseCaseControlsComponent } from './use-case-controls.component';
import { NavigationBackService } from '../../../../services/navigation-back.service';
import type { UseCaseStep } from '../base-use-case.component';

describe('UseCaseControlsComponent', () => {
  let fixture: ComponentFixture<UseCaseControlsComponent>;
  let component: UseCaseControlsComponent;

  const steps: UseCaseStep[] = [
    {
      id: 'a',
      title: { en: 'One', de: 'Eins' },
      highlightIds: [],
      hideIds: [],
    },
    {
      id: 'b',
      title: { en: 'Two', de: 'Zwei' },
      highlightIds: [],
      hideIds: [],
    },
  ];

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UseCaseControlsComponent],
      providers: [{ provide: NavigationBackService, useValue: { backOrNavigate: jest.fn() } }],
    }).compileComponents();

    fixture = TestBed.createComponent(UseCaseControlsComponent);
    component = fixture.componentInstance;
    component.useCaseCode = 'UC-00';
    component.useCaseTitle = 'Interoperability';
    component.steps = steps;
    component.getStepTitle = (step) => step.title.en;
    fixture.detectChanges();
  });

  it('should create and render code + title', () => {
    expect(component).toBeTruthy();
    const text = (fixture.nativeElement as HTMLElement).textContent ?? '';
    expect(text).toContain('UC-00');
    expect(text).toContain('Interoperability');
  });

  it('should emit navigation and zoom events from controls', () => {
    const next = jest.fn();
    const zoomIn = jest.fn();
    const goTo = jest.fn();
    component.nextStep.subscribe(next);
    component.zoomIn.subscribe(zoomIn);
    component.goToStep.subscribe(goTo);

    const buttons = fixture.debugElement.queryAll(By.css('button.nav-btn-icon'));
    // prev, autoplay, loop, description, next — then zoom buttons separately
    const nextBtn = buttons.find((b) => b.attributes['title'] === component.btnNext);
    expect(nextBtn).toBeTruthy();
    nextBtn!.nativeElement.click();
    expect(next).toHaveBeenCalled();

    const zoomInBtn = fixture.debugElement.query(
      By.css(`.zoom-btn[title="${component.zoomInLabel}"]`)
    );
    expect(zoomInBtn).toBeTruthy();
    zoomInBtn!.nativeElement.click();
    expect(zoomIn).toHaveBeenCalled();

    const dots = fixture.debugElement.queryAll(By.css('button.step-dot'));
    expect(dots.length).toBe(2);
    dots[1].nativeElement.click();
    expect(goTo).toHaveBeenCalledWith(1);
  });
});
