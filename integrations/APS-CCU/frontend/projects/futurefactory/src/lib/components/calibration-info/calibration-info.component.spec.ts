import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { CalibrationInfoComponent } from './calibration-info.component';

describe('CalibrationInfoComponent', () => {
  let fixture: ComponentFixture<CalibrationInfoComponent>;
  let component: CalibrationInfoComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [CalibrationInfoComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CalibrationInfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render the language selector', () => {
    expect(fixture).toMatchSnapshot();
  });
});
