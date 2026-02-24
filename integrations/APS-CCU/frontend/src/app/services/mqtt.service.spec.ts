import { TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { MqttService as NgxMqttService } from 'ngx-mqtt';
import { MqttService } from './mqtt.service';

describe('MqttService', () => {
  let service: MqttService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [MockProvider(NgxMqttService)],
    });
    service = TestBed.inject(MqttService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
