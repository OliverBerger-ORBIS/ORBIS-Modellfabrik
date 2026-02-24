import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { EMPTY, NEVER } from 'rxjs';
import { MissingControllerBannerComponent } from '../../components/missing-controller-banner/missing-controller-banner.component';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { FactoryLayoutService } from '../../services/factory-layout.service';
import { SelectedControllerService } from '../../services/selected-controller.service';
import { FutureFactoryModuleListComponent } from './module-list.component';
import { TypedMqttService } from '../../services/typed-mqtt.service';

describe('FutureFactoryModuleListComponent', () => {
  let component: FutureFactoryModuleListComponent;
  let fixture: ComponentFixture<FutureFactoryModuleListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [
        FutureFactoryModuleListComponent,
        MissingControllerBannerComponent,
      ],
      providers: [
        MockProvider(TypedMqttService, {
          publish: () => true,
        }),
        MockProvider(FactoryLayoutService, {
          pairedModules$: NEVER,
          pairingState$: NEVER,
        }),
        MockProvider(SelectedControllerService, {
          availableControllers$: EMPTY,
          availableFutureFactoryControllers$: EMPTY,
        }),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(FutureFactoryModuleListComponent);
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
