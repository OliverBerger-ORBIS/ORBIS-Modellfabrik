import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { FactoryParkComponent } from './factory-park.component';
import { TypedMqttService } from '../../futurefactory.service';

describe('FactoryParkComponent', () => {
  let component: FactoryParkComponent;
  let fixture: ComponentFixture<FactoryParkComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [FactoryParkComponent],
      providers: [
        MockProvider(TypedMqttService, {
          publish: () => Promise.resolve(),
        }),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(FactoryParkComponent);
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
