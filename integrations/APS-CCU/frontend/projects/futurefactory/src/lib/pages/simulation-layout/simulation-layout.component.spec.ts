import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { EMPTY } from 'rxjs';
import { TypedMqttService } from '../../futurefactory.service';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { SelectedControllerService } from '../../services/selected-controller.service';
import { FutureFactorySimulationLayoutComponent } from './simulation-layout.component';

describe('FutureFactorySimulationLayoutComponent', () => {
  let component: FutureFactorySimulationLayoutComponent;
  let fixture: ComponentFixture<FutureFactorySimulationLayoutComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [FutureFactorySimulationLayoutComponent],
      providers: [
        MockProvider(TypedMqttService, {
          subscribe: () => EMPTY,
          publish: jest.fn(),
        }),
        MockProvider(SelectedControllerService, {
          availableFutureFactoryControllers$: EMPTY,
        }),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(FutureFactorySimulationLayoutComponent);
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
