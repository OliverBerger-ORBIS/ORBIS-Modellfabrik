import { Component, OnInit } from '@angular/core';
import { ReplayToggleService } from './replay-toggle.service';
import { MqttService } from './mqtt.service';
@Component({ selector: 'app-root', template: `\n  <h3>omf3 UI (prototype)</h3>\n  <div>Mode: {{mode}}</div>\n  <button (click)="switchLive()">Live</button>\n  <button (click)="switchReplay()">Replay</button>\n  <div *ngFor="let m of messages">{{m.topic}} — {{m.payload | json}}</div>\n`, styles: [] })
export class AppComponent implements OnInit {
  messages: any[] = [];
  mode = 'idle';
  constructor(private toggle: ReplayToggleService, private mqtt: MqttService) {}
  ngOnInit() {
    this.mqtt.messages().subscribe(m => { this.messages.unshift(m); if (this.messages.length>50) this.messages.pop(); });
  }
  switchLive() {
    this.mode = 'live';
    // example ws proxy url; ops will replace with production WSS
    this.toggle.useLive('wss://broker-proxy.local:9001');
  }
  switchReplay() {
    this.mode = 'replay';
    this.toggle.useReplay('ws://localhost:18083/replay');
  }
}