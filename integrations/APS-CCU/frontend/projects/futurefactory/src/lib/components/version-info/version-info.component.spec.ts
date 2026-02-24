import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule } from '@angular/material/dialog';
import { TypedMqttService } from '../../services/typed-mqtt.service';
import { VersionInfoComponent } from './version-info.component';
import { MockProvider } from 'ng-mocks';
import { EMPTY } from 'rxjs';

describe('VersionInfoComponent', () => {
  let fixture: ComponentFixture<VersionInfoComponent>;
  let component: VersionInfoComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatIconModule, MatDialogModule],
      declarations: [VersionInfoComponent],
      providers: [
        MockProvider(TypedMqttService, {
          subscribe: () => EMPTY,
        }),
      ],
    }).compileComponents();

    jest.useFakeTimers().setSystemTime(1699604177818);
    fixture = TestBed.createComponent(VersionInfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render the language selector', () => {
    expect(fixture).toMatchSnapshot();
  });
});
