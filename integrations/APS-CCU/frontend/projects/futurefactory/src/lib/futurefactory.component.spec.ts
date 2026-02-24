import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { EMPTY } from 'rxjs';
import { LanguageSelectorComponent } from './components/language-selector/language-selector.component';
import { FutureFactoryComponent } from './futurefactory.component';
import {
  MqttClientService,
  ShowLanguageSelector,
} from './futurefactory.external.service';
import { MqttServiceMock, TypedMqttService } from './futurefactory.service';
import { FutureFactoryTestingModule } from './futurefactory.testing.module';

describe('FutureFactoryComponent', () => {
  let fixture: ComponentFixture<FutureFactoryComponent>;
  let component: FutureFactoryComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [LanguageSelectorComponent, FutureFactoryComponent],
      providers: [
        {
          provide: MqttClientService,
          useClass: MqttServiceMock,
        },
        MockProvider(TypedMqttService, {
          subscribe: () => EMPTY,
        }),
        MockProvider(ShowLanguageSelector, true),
      ],
    }).compileComponents();

    jest.useFakeTimers().setSystemTime(1699604177818);
    fixture = TestBed.createComponent(FutureFactoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should create the app', () => {
    expect(component).toBeTruthy();
  });

  it('should render the component', () => {
    expect(fixture).toMatchSnapshot();
  });
});
