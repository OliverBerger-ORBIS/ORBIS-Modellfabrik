import { Injectable } from '@angular/core';
import { MqttService } from './mqtt.service';
@Injectable({ providedIn: 'root' })
export class ReplayToggleService {
  private mode: 'live' | 'replay' = 'live';
  constructor(private mqtt: MqttService) {}
  useLive(wsUrl: string, options: any = {}) {
    this.mode = 'live';
    this.mqtt.connectWebsocket(wsUrl, options);
  }
  useReplay(replayWsUrl: string) {
    this.mode = 'replay';
    // replay WS will stream messages in the same shape as MQTT messages
    this.mqtt.connectWebsocket(replayWsUrl);
  }
  currentMode() { return this.mode; }
}