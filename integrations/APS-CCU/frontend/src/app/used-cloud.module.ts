import { APP_BASE_HREF } from '@angular/common';
import { NgModule } from '@angular/core';
import {
  CameraApiMockService,
  CameraApiService,
  ChartApiMockService,
  ChartApiService,
  ControllerApiService,
  UserApiMockService,
  UserApiService,
} from '@fischertechnik/ft-api';
import { I18nService } from '@fischertechnik/ft-common-ui';
import { FT_ENVIRONMENT_TOKEN } from '@fischertechnik/ft-environment';
import {
  AlarmMqttService,
  AlarmService,
  Bme680SensorMqttService,
  Bme680SensorService,
  CameraMqttService,
  CameraService,
  CloudMqttService,
  HbwMqttService,
  HbwService,
  LdrSensorMqttService,
  LdrSensorService,
  NFCMqttService,
  NFCService,
  OrderMqttService,
  OrderService,
  PtuMqttService,
  PtuService,
  StateMqttService,
  StateService,
  StockMqttService,
  StockService,
} from '@fischertechnik/ft-mqtt';
import { FtWindowModule } from '@fischertechnik/ft-window';
import { LocalControllerService } from './services/controller.service';
import { MqttService as LocalMqttService } from './services/mqtt.service';

export function getAppBaseHref() {
  const baseTags = document.getElementsByTagName('base');
  if (baseTags.length) {
    return baseTags[0].getAttribute('href');
  }
  return '/';
}

@NgModule({
  imports: [
    FtWindowModule.configure({
      alarmService: {
        provide: AlarmService,
        useClass: AlarmMqttService,
        deps: [I18nService, CloudMqttService],
      },
      ptuService: {
        provide: PtuService,
        useClass: PtuMqttService,
        deps: [CloudMqttService],
      },
      cameraService: {
        provide: CameraService,
        useClass: CameraMqttService,
        deps: [CloudMqttService],
      },
      ldrSensorService: {
        provide: LdrSensorService,
        useClass: LdrSensorMqttService,
        deps: [CloudMqttService],
      },
      bme680SensorService: {
        provide: Bme680SensorService,
        useClass: Bme680SensorMqttService,
        deps: [CloudMqttService],
      },
      nfcService: {
        provide: NFCService,
        useClass: NFCMqttService,
        deps: [CloudMqttService],
      },
      orderService: {
        provide: OrderService,
        useClass: OrderMqttService,
        deps: [CloudMqttService],
      },
      stateService: {
        provide: StateService,
        useClass: StateMqttService,
        deps: [CloudMqttService],
      },
      stockService: {
        provide: StockService,
        useClass: StockMqttService,
        deps: [CloudMqttService],
      },
      hbwService: {
        provide: HbwService,
        useClass: HbwMqttService,
        deps: [CloudMqttService],
      },
      userApiService: { provide: UserApiService, useClass: UserApiMockService },
      chartApiService: {
        provide: ChartApiService,
        useClass: ChartApiMockService,
      },
      cameraApiService: {
        provide: CameraApiService,
        useClass: CameraApiMockService,
      },
      controllerApiService: {
        provide: ControllerApiService,
        useClass: LocalControllerService,
      },
    }),
  ],
  providers: [
    { provide: APP_BASE_HREF, useFactory: getAppBaseHref },
    { provide: FT_ENVIRONMENT_TOKEN, useValue: {} },

    // We need to provide the CloudMqttService with a local implementation
    // because the beemo libs require the CloudMqttService instead of the
    // IMqttService interface along with an injection token.
    { provide: CloudMqttService, useClass: LocalMqttService },
  ],
})
export class UsedCloudModule {}
