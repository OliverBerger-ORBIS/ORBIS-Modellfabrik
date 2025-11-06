import { Injectable } from '@angular/core';
import { Subject, Observable } from 'rxjs';
import { connect, MqttClient } from 'mqtt/dist/mqtt';
@Injectable({ providedIn: 'root' })
export class MqttService {
  private client: MqttClient | null = null;
  private messages$ = new Subject<{ topic: string; payload: any; raw: any }>();
  connectionState$ = new Subject<'connected' | 'disconnected' | 'error'>();
  messages(): Observable<{ topic: string; payload: any; raw: any }> {
    return this.messages$.asObservable();
  }
  connectWebsocket(wsUrl: string, options: any = {}) {
    if (this.client) {
      try { this.client.end(true); } catch (e) {}
      this.client = null;
    }
    this.client = connect(wsUrl, options);
    this.client.on('connect', () => this.connectionState$.next('connected'));
    this.client.on('reconnect', () => this.connectionState$.next('disconnected'));
    this.client.on('error', (err: any) => this.connectionState$.next('error'));
    this.client.on('message', (topic: string, payload: Buffer) => {
      let parsed: any = null;
      try { parsed = JSON.parse(payload.toString()); } catch (e) { parsed = payload.toString(); }
      this.messages$.next({ topic, payload: parsed, raw: payload });
    });
  }
  subscribe(topic: string, qos = 0) {
    if (this.client) this.client.subscribe(topic, { qos });
  }
  publish(topic: string, payload: any, options: any = {}) {
    if (this.client) {
      this.client.publish(topic, typeof payload === 'string' ? payload : JSON.stringify(payload), options);
    }
  }
  disconnect() {
    if (this.client) {
      this.client.end(true);
      this.client = null;
      this.connectionState$.next('disconnected');
    }
  }
}