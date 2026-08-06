import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { UseCaseSelectorPageComponent } from './use-case-selector-page.component';
import { DspUseCasesComponent } from '../dsp/components/dsp-use-cases/dsp-use-cases.component';

@Component({
  selector: 'app-dsp-use-cases',
  standalone: true,
  template: '<div class="mock-dsp-use-cases"></div>',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
class MockDspUseCasesComponent {
  @Input() enableNavigation = false;
}

describe('UseCaseSelectorPageComponent', () => {
  let fixture: ComponentFixture<UseCaseSelectorPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UseCaseSelectorPageComponent],
    })
      .overrideComponent(UseCaseSelectorPageComponent, {
        remove: { imports: [DspUseCasesComponent] },
        add: { imports: [MockDspUseCasesComponent] },
      })
      .compileComponents();

    fixture = TestBed.createComponent(UseCaseSelectorPageComponent);
    fixture.detectChanges();
  });

  it('should create and render heading with mocked use-case grid', () => {
    expect(fixture.componentInstance).toBeTruthy();
    const h1 = fixture.debugElement.query(By.css('h1'));
    expect(h1.nativeElement.textContent).toContain('DSP Use Cases');
    expect(fixture.debugElement.query(By.css('.mock-dsp-use-cases'))).toBeTruthy();
  });
});
