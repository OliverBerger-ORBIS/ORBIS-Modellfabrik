import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { EMPTY } from 'rxjs';
import { TypedMqttService } from '../../futurefactory.service';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { ModuleInfoComponent } from './module-info.component';

describe('ModuleInfoComponent', () => {
  let component: ModuleInfoComponent;
  let fixture: ComponentFixture<ModuleInfoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [ModuleInfoComponent],
      providers: [
        MockProvider(TypedMqttService, {
          subscribe: jest.fn(() => EMPTY),
          publish: jest.fn(),
        }),
      ],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ModuleInfoComponent);
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
