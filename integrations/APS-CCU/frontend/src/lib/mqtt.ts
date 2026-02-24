import { connect, IPublishPacket, MqttClient } from 'mqtt-browser';
import { filter, Observable, switchMap } from 'rxjs';

export { IPublishPacket, MqttClient } from 'mqtt-browser';
import mqttMatch from "mqtt-match";

export type MqttMessage = {
  timestamp: number;
  topic: string;
  payload: Buffer;
  packet: IPublishPacket;
};

export const createAndListenForTopics = (
  url: string,
  topics: Array<string> = []
) =>
  createMqttClient(url).pipe(
    filter((client) => !!client?.connected),
    switchMap((client) => listenForTopics(client, topics))
  );

export const listenForTopics = (
  client: MqttClient,
  topics: Array<string> = []
) =>
  new Observable<MqttMessage>((subs) => {
    client.subscribe(topics);
    client.on('error', subs.error);
    client.on('close', subs.complete);
    client.on(
      'message',
      (topic: string, payload: Buffer, packet: IPublishPacket) => {
        if (topics.find(match => mqttMatch(match, topic))) {
          subs.next({ timestamp: Date.now(), topic, payload, packet });
        }
      }
    );

    return () => subs.complete();
  });

export const createMqttClient = (url: string) =>
  new Observable<MqttClient>((subs) => {
    const client = connect(url);
    client.on('close', subs.complete);
    client.on('error', subs.error);
    client.on('connect', () => subs.next(client));
    return () => subs.complete();
  });
