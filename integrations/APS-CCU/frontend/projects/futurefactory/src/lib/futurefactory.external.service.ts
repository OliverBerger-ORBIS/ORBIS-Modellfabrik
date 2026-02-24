import { InjectionToken } from '@angular/core';
import { ControllerResponse } from '@fischertechnik/ft-api';
import { IMqttMessage, IPublishOptions } from 'ngx-mqtt';
import { Observable } from 'rxjs';

export { IMqttMessage, IPublishOptions } from 'ngx-mqtt';

/**
 * This interface is used to define the methods of the MqttClientService
 * for the fischertechnik Cloud and the local running application, that
 * is hosted on the raspberry pi.
 */
export interface IMqttService {
  /**
   * This method handles the subscription to a topic for both,
   * the fischertechnik Cloud and the local running application.
   *
   * @param controllerId the id of the controller, that should receive the message
   * @param topic the topic, where the message should be published
   * @returns an observable, that emits the message, when it is received
   */
  subscribe(controllerId: number, topic: string): Observable<IMqttMessage>;

  /**
   * This method handles the publishing of a message to a topic for both,
   * the fischertechnik Cloud and the local running application.
   *
   * @param controllerId the id of the controller, that should receive the message
   * @param topic the topic, where the message should be published
   * @param message the message, that should be published
   * @param options the options for publishing the message
   */
  publish(
    controllerId: number,
    topic: string,
    message: string,
    options?: IPublishOptions
  ): void;
}

/**
 * The injection token for the MqttClientService.
 * It is required, if you want to use Interfaces instead of abstract classes to define necessary methods.
 */
export const MqttClientService = new InjectionToken<IMqttService>(
  'MqttClientService'
);
/**
 * The injection token for the mqtt topic prefix requirement.
 * It is required if you want to prevent the creation of topics with the controller prefix
 * If set to true, the controller prefix will be added, false will not add the prefix
 */
export const MqttPrefixRequired = new InjectionToken<boolean>(
  'MqttPrefixRequired'
);
/**
 * The injection token is used to control the visibility of the language selector in the navigation bar.
 * If set to true, the language selector will be visible, false will hide it.
 */
export const ShowLanguageSelector = new InjectionToken<boolean>(
  'ShowLanguageSelector'
);

export interface IControllerService {
  /**
   * This method returns the latest controller information as an observable for both,
   * the fischertechnik Cloud and the local running application.
   *
   * The observable will emil `null`, if the controller information is not loaded yet.
   * Loading the controller information can be done via `loadControllers()`.
   *
   * @returns an observable, that emits the latest controller information
   */
  onChange(): Observable<ControllerResponse[]>;

  /**
   * This method loads the controller information for both,
   * the fischertechnik Cloud and the local running application.
   *
   * The information is available via `onChange()` as an observable.
   */
  loadControllers(): void;
}

/**
 * The injection token for the ControllerClientService.
 * It is required, if you want to use Interfaces instead of abstract classes to define necessary methods.
 */
export const ControllerClientService = new InjectionToken<IControllerService>(
  'ControllerClientService'
);
