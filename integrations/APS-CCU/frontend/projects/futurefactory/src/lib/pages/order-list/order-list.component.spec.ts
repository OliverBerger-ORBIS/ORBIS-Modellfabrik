import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { EMPTY } from 'rxjs';
import { TypedMqttService } from '../../futurefactory.service';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { SelectedControllerService } from '../../services/selected-controller.service';
import { FutureFactoryOrderListComponent } from './order-list.component';

describe('FutureFactoryOrderListComponent', () => {
  let component: FutureFactoryOrderListComponent;
  let fixture: ComponentFixture<FutureFactoryOrderListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [FutureFactoryOrderListComponent],
      providers: [
        MockProvider(TypedMqttService, {
          subscribe: () => EMPTY,
        }),
        MockProvider(SelectedControllerService, {
          availableFutureFactoryControllers$: EMPTY,
        }),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(FutureFactoryOrderListComponent);
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
