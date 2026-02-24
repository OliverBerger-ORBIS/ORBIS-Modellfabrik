import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { EMPTY } from 'rxjs';
import { TypedMqttService } from '../../futurefactory.service';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { StateLogDetailsComponent } from './state-log-details.component';

describe('StateLogDetailsComponent', () => {
  let component: StateLogDetailsComponent;
  let fixture: ComponentFixture<StateLogDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [StateLogDetailsComponent],
      providers: [
        MockProvider(TypedMqttService, {
          subscribe: jest.fn(() => EMPTY),
          publish: jest.fn(),
        }),
      ],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(StateLogDetailsComponent);
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
