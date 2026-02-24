import { OperatorFunction } from 'rxjs';
import { map } from 'rxjs/operators';
import { MqttMessage } from '../services/typed-mqtt.service';

/**
 * This method creates an operator function that extracts the payload from a message.
 */
export function getPayload<T>(): OperatorFunction<MqttMessage<T>, T> {
  return map((mqttMessage) => mqttMessage.payload);
}
