import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute } from '@angular/router';
import { MockProvider } from 'ng-mocks';
import { EMPTY, of } from 'rxjs';
import { MissingControllerBannerComponent } from '../../components/missing-controller-banner/missing-controller-banner.component';
import { TypedMqttService } from '../../futurefactory.service';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { SelectedControllerService } from '../../services/selected-controller.service';
import { FutureFactoryModuleCalibrationComponent } from './module-calibration.component';

describe('FutureFactoryModuleCalibrationComponent', () => {
  let component: FutureFactoryModuleCalibrationComponent;
  let fixture: ComponentFixture<FutureFactoryModuleCalibrationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [
        FutureFactoryModuleCalibrationComponent,
        MissingControllerBannerComponent,
      ],
      providers: [
        MockProvider(TypedMqttService, { subscribe: () => EMPTY }),
        {
          provide: ActivatedRoute,
          useValue: {
            params: of({ moduleId: 'any' }),
            data: of({ ROUTE_TO_MODULE_ROOT: '.' }),
          },
        },
        MockProvider(SelectedControllerService, {
          availableControllers$: EMPTY,
          availableFutureFactoryControllers$: EMPTY,
        }),
      ],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FutureFactoryModuleCalibrationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render the component', () => {
    expect(fixture).toMatchSnapshot();
  });
});
