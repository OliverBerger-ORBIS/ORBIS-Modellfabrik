import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { FactoryResetComponent } from './factory-reset.component';
import { TypedMqttService } from '../../futurefactory.service';

describe('FactoryResetComponent', () => {
  let component: FactoryResetComponent;
  let fixture: ComponentFixture<FactoryResetComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [FactoryResetComponent],
      providers: [
        MockProvider(TypedMqttService, {
          publish: () => Promise.resolve(),
        }),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(FactoryResetComponent);
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
