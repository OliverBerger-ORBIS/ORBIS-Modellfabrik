import { HttpClient, HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {
  ControllerClientService,
  FutureFactoryModule,
  MqttClientService,
  MqttPrefixRequired,
  ShowLanguageSelector,
  TranslateXlfHttpLoader,
  FUTURE_FACTORY_DASHBOARD_NO_HISTORY_CONFIG
} from '@ft/futurefactory';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { IMqttServiceOptions, MqttModule } from 'ngx-mqtt';
import { environment } from '../environments/environment';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app.routing';
import { LocalControllerService } from './services/controller.service';
import { MqttService as LocalMqttService } from './services/mqtt.service';
import { UsedCloudModule } from './used-cloud.module';
import { UsedMaterialModule } from './used-material.module';
import { DASHBOARD_CONFIG } from '@fischertechnik/ft-window';

export function createTranslateLoader(http: HttpClient) {
  return new TranslateXlfHttpLoader(http, 'assets/i18n/messages-ft.', '.xlf');
}

const MQTT_SERVICE_OPTIONS: IMqttServiceOptions = {
  hostname: environment.mqttHost || window.location.hostname,
  port: 9001,
  path: '/ws',
  username: 'default',
  password: 'default',
};

@NgModule({
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    UsedMaterialModule,
    UsedCloudModule,
    HttpClientModule,
    TranslateModule.forRoot({
      loader: {
        provide: TranslateLoader,
        useFactory: createTranslateLoader,
        deps: [HttpClient],
      },
    }),
    MqttModule.forRoot(MQTT_SERVICE_OPTIONS),
    FutureFactoryModule.configure({
      showLanguageSelector: {
        provide: ShowLanguageSelector,
        useValue: true,
      },
      mqttPrefixRequired: {
        provide: MqttPrefixRequired,
        useValue: false,
      },
      mqttService: {
        provide: MqttClientService,
        useClass: LocalMqttService,
      },
      controllerService: {
        provide: ControllerClientService,
        useClass: LocalControllerService,
      },
      dashboardConfig: {
        provide: DASHBOARD_CONFIG,
        useValue: FUTURE_FACTORY_DASHBOARD_NO_HISTORY_CONFIG
      },
    }),
  ],
  declarations: [AppComponent],
  bootstrap: [AppComponent],
})
export class AppModule {}
