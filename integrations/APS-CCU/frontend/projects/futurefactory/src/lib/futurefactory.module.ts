import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import {
  Inject,
  LOCALE_ID,
  ModuleWithProviders,
  NgModule,
  Provider,
} from '@angular/core';
import { I18nService } from '@fischertechnik/ft-common-ui';
import { DASHBOARD_CONFIG } from '@fischertechnik/ft-window';
import {
  TranslateLoader,
  TranslateModule,
  TranslateService,
} from '@ngx-translate/core';
import { GridsterModule } from 'angular-gridster2';
import { FutureFactoryComponentsModule } from './components/components.module';
import { FutureFactoryComponent } from './futurefactory.component';
import { FUTURE_FACTORY_DASHBOARD } from './futurefactory.dashboard.config';
import {
  ControllerClientService,
  MqttClientService,
  MqttPrefixRequired,
  ShowLanguageSelector,
} from './futurefactory.external.service';
import { FutureFactoryRoutingModule } from './futurefactory.routing.module';
import {
  ControllerServiceMock,
  MqttServiceMock,
} from './futurefactory.service';
import { FutureFactoryPagesModule } from './pages/pages.module';
import { SelectedControllerService } from './services/selected-controller.service';
import { TypedMqttService } from './services/typed-mqtt.service';
import { TranslateXlfHttpLoader } from './translate/xlf-http-loader';
import { UsedMaterialModule } from './used-material.module';

export interface FutureFactoryModuleConfig {
  showLanguageSelector: Provider;
  mqttPrefixRequired: Provider;
  mqttService: Provider;
  controllerService: Provider;
  dashboardConfig: Provider;
}

export function createTranslateLoader(http: HttpClient) {
  return new TranslateXlfHttpLoader(http, 'assets/i18n/messages-omm.', '.xlf');
}

@NgModule({
  imports: [
    CommonModule,
    FutureFactoryRoutingModule,
    UsedMaterialModule,
    GridsterModule,
    FutureFactoryComponentsModule,
    FutureFactoryPagesModule,
    TranslateModule.forChild({
      loader: {
        provide: TranslateLoader,
        useFactory: createTranslateLoader,
        deps: [HttpClient],
      },
      extend: true,
      isolate: true,
    }),
  ],
  declarations: [FutureFactoryComponent],
  providers: [TypedMqttService, SelectedControllerService],
  exports: [],
})
export class FutureFactoryModule {
  static configure(
    config: Partial<FutureFactoryModuleConfig> = {}
  ): ModuleWithProviders<FutureFactoryModule> {
    return {
      ngModule: FutureFactoryModule,
      providers: [
        config.showLanguageSelector ?? {
          provide: ShowLanguageSelector,
          useValue: false,
        },
        config.mqttPrefixRequired ?? {
          provide: MqttPrefixRequired,
          useValue: true,
        },
        config.mqttService ?? {
          provide: MqttClientService,
          useClass: MqttServiceMock,
        },
        config.controllerService ?? {
          provide: ControllerClientService,
          useClass: ControllerServiceMock,
        },
        config.dashboardConfig ?? {
          provide: DASHBOARD_CONFIG,
          useValue: FUTURE_FACTORY_DASHBOARD,
        },
      ],
    };
  }

  constructor(
    @Inject(LOCALE_ID) private locale: string,
    private translate: TranslateService,
    private i18n: I18nService
  ) {
    this.translate.setDefaultLang('de');
    this.translate.addLangs(['de', 'en', 'es', 'fr', 'nl', 'pt', 'ru', 'ua']);
    const detectedLocale = this.locale ?? this.translate.getBrowserLang();
    console.log('Detected locale: ' + detectedLocale);
    this.translate.use(detectedLocale);
    this.i18n.use(detectedLocale);
  }
}
