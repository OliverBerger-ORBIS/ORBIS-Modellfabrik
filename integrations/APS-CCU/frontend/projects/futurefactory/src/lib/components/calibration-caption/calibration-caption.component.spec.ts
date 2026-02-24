import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ModuleType } from '../../../common/protocol/module';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { CalibrationCaptionComponent } from './calibration-caption.component';

describe('CalibrationCaptionComponent', () => {
  let fixture: ComponentFixture<CalibrationCaptionComponent>;
  let component: CalibrationCaptionComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [CalibrationCaptionComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CalibrationCaptionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render no images', () => {
    expect(fixture).toMatchSnapshot();
  });

  it('should render the images for the DPS', () => {
    component.moduleType = ModuleType.DPS;
    fixture.detectChanges();
    expect(fixture).toMatchSnapshot();
  });

  it('should render the images for the HBW', () => {
    component.moduleType = ModuleType.HBW;
    fixture.detectChanges();
    expect(fixture).toMatchSnapshot();
  });
});
