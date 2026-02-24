import { TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { EMPTY } from 'rxjs';
import { TypedMqttService } from '../futurefactory.service';
import { StatesService } from './states.service';

const FIXED_SYSTEM_TIME = '2022-02-02T12:12:12Z';

describe('StatesService', () => {
  let service: StatesService;

  beforeEach(() => {
    jest.useFakeTimers();
    jest.setSystemTime(Date.parse(FIXED_SYSTEM_TIME));
    TestBed.configureTestingModule({
      providers: [
        MockProvider(TypedMqttService, {
          subscribe: () => EMPTY,
        }),
      ],
    });
    service = TestBed.inject(StatesService);
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
