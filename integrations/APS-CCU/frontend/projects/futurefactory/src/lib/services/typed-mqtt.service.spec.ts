import { TestBed } from '@angular/core/testing';
// noinspection ES6PreferShortImport
import { IPublishOptions, MqttClientService, MqttPrefixRequired } from '../../lib/futurefactory.external.service';
import { MqttServiceMock, TypedMqttService } from '../futurefactory.service';
import { SelectedControllerService } from './selected-controller.service';
import { BehaviorSubject, noop } from 'rxjs';
import { ControllerResponse } from '@fischertechnik/ft-api';

describe('Typed Mqtt Service Tests', () => {
  const mqttService = new MqttServiceMock();
  const CONTROLLER_ID = 123;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [],
      declarations: [],
      providers: [
        { provide: MqttClientService, useValue: mqttService },
        { provide: SelectedControllerService, useValue: {
            selectedController$: new BehaviorSubject<ControllerResponse>({
              controllerId: CONTROLLER_ID,
            }) as ControllerResponse,
          }
        },
        TypedMqttService,
      ],
    }).compileComponents();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  })

  it('Should add a prefix with the optional injection token set to true', () => {
    TestBed.overrideProvider(MqttPrefixRequired, { useValue: true });
    const mqttSubscribeSpy = jest.spyOn(mqttService, 'subscribe');
    const testTopic = 'sample/topic';

    const service = TestBed.inject(TypedMqttService);
    service.subscribe(testTopic).subscribe(noop).unsubscribe();
    expect(mqttSubscribeSpy).toHaveBeenCalledWith(CONTROLLER_ID, `/j1/txt/${CONTROLLER_ID}/${testTopic}`);
  });

  it('Should add a prefix without the optional injection', () => {
    const mqttSubscribeSpy = jest.spyOn(mqttService, 'subscribe');
    const testTopic = 'sample/topic';

    const service = TestBed.inject(TypedMqttService);
    service.subscribe(testTopic).subscribe(noop).unsubscribe();
    expect(mqttSubscribeSpy).toHaveBeenCalledWith(CONTROLLER_ID, `/j1/txt/${CONTROLLER_ID}/${testTopic}`);
  });

  it('Should not add a prefix with the optional injection set to false', () => {
    TestBed.overrideProvider(MqttPrefixRequired, { useValue: false });
    const mqttSubscribeSpy = jest.spyOn(mqttService, 'subscribe');
    const testTopic = 'sample/topic';

    const service = TestBed.inject(TypedMqttService);
    service.subscribe(testTopic).subscribe(noop).unsubscribe();
    expect(mqttSubscribeSpy).toHaveBeenCalledWith(CONTROLLER_ID, testTopic);
  });

  it('Should publish with a prefix with the optional injection token set to true', () => {
    TestBed.overrideProvider(MqttPrefixRequired, { useValue: true });
    const mqttPublishSpy = jest.spyOn(mqttService, 'publish');
    const testTopic = 'sample/topic';
    const message = 'testmessage';
    const options  = undefined;

    const service = TestBed.inject(TypedMqttService);
    service.publish(testTopic, message, options);
    expect(mqttPublishSpy).toHaveBeenCalledWith(CONTROLLER_ID, `/j1/txt/${CONTROLLER_ID}/${testTopic}`, JSON.stringify(message), { retain: false, qos: 2 });
  });

  it('Should publish with a prefix without the optional injection', () => {
    const mqttPublishSpy = jest.spyOn(mqttService, 'publish');
    const testTopic = 'sample/topic';
    const message = 'testmessage';
    const options: IPublishOptions = { qos: 1 };

    const service = TestBed.inject(TypedMqttService);
    service.publish(testTopic, message, options);
    expect(mqttPublishSpy).toHaveBeenCalledWith(CONTROLLER_ID, `/j1/txt/${CONTROLLER_ID}/${testTopic}`, JSON.stringify(message), { retain: false, qos: 1 });
  });

  it('Should  publish without a prefix with the optional injection set to false', () => {
    TestBed.overrideProvider(MqttPrefixRequired, { useValue: false });
    const mqttPublishSpy = jest.spyOn(mqttService, 'publish');
    const testTopic = 'sample/topic';
    const message = 'testmessage';
    const options: IPublishOptions = { retain: true, qos: 0 };

    const service = TestBed.inject(TypedMqttService);
    service.publish(testTopic, message, options);
    expect(mqttPublishSpy).toHaveBeenCalledWith(CONTROLLER_ID, testTopic, JSON.stringify(message), { retain: true, qos: 0 });
  });

});
