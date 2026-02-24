import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { EMPTY } from 'rxjs';
import { TypedMqttService } from '../../futurefactory.service';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { OrderStatesService } from '../../services/order-states.service';
import { OrderService } from '../../services/order.service';
import { SelectedControllerService } from '../../services/selected-controller.service';
import { FutureFactoryLayoutEditorComponent } from './layout-editor.component';

describe('FutureFactoryLayoutEditorComponent', () => {
  let component: FutureFactoryLayoutEditorComponent;
  let fixture: ComponentFixture<FutureFactoryLayoutEditorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [FutureFactoryLayoutEditorComponent],
      providers: [
        MockProvider(OrderService, {
          getActiveOrders: jest.fn(() => EMPTY),
        }),
        MockProvider(OrderStatesService, {
          orderStatus$: EMPTY,
          hasRunningOrders$: EMPTY,
        }),
        MockProvider(TypedMqttService, {
          subscribe: jest.fn(() => EMPTY),
          publish: jest.fn(),
        }),
        MockProvider(SelectedControllerService, {
          availableControllers$: EMPTY,
          availableFutureFactoryControllers$: EMPTY,
        }),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(FutureFactoryLayoutEditorComponent);
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
