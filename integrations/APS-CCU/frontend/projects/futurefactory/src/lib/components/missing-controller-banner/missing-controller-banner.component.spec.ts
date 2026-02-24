import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ControllerResponse } from '@fischertechnik/ft-api';
import { MockProvider } from 'ng-mocks';
import { ReplaySubject } from 'rxjs';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { SelectedControllerService } from '../../services/selected-controller.service';
import { MissingControllerBannerComponent } from './missing-controller-banner.component';

describe('MissingControllerBannerComponent', () => {
  let controllerSubject$: ReplaySubject<ControllerResponse[]>;
  let fixture: ComponentFixture<MissingControllerBannerComponent>;
  let component: MissingControllerBannerComponent;

  beforeEach(async () => {
    controllerSubject$ = new ReplaySubject<ControllerResponse[]>(1);
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [MissingControllerBannerComponent],
      providers: [
        MockProvider(SelectedControllerService, {
          availableFutureFactoryControllers$: controllerSubject$,
        }),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MissingControllerBannerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create the component', () => {
    expect(component).toBeTruthy();
  });

  it('should render the component', () => {
    expect(fixture).toMatchSnapshot();
  });
});
