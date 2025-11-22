import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, interval } from 'rxjs';
import { map } from 'rxjs/operators';

export interface CellData {
  id: string;
  name: string;
  status: 'idle' | 'running' | 'error' | 'maintenance';
  temperature?: number;
  cycleTime?: number;
  partsProduced?: number;
  lastUpdate?: string;
}

/**
 * Mock MQTT Service
 * 
 * This service simulates MQTT data for demonstration purposes.
 * In production, replace this with a real MQTT client like ngx-mqtt.
 * 
 * To integrate ngx-mqtt:
 * 1. Install: npm install ngx-mqtt
 * 2. Import IMqttServiceOptions, MqttModule
 * 3. Configure MQTT broker connection in app.config.ts
 * 4. Replace this service with MqttService from ngx-mqtt
 * 5. Subscribe to topics like: mqttService.observe('shopfloor/+/status')
 */
@Injectable({
  providedIn: 'root'
})
export class MqttMockService {
  private cellDataSubjects: Map<string, BehaviorSubject<CellData>> = new Map();
  
  // Initial mock data for dynamic cells (using serial numbers from layout)
  private readonly initialData: CellData[] = [
    { id: 'MILL01', name: 'Milling Machine', status: 'running', temperature: 45, cycleTime: 120, partsProduced: 234 },
    { id: 'DRILL01', name: 'Drilling Station', status: 'running', temperature: 38, cycleTime: 90, partsProduced: 189 },
    { id: 'AIQS01', name: 'AI Quality System', status: 'idle', temperature: 25, cycleTime: 0, partsProduced: 0 },
    { id: 'HBW01', name: 'High-Bay Warehouse', status: 'running', temperature: 22, cycleTime: 45, partsProduced: 567 },
    { id: 'VGR01', name: 'Vacuum Gripper Robot', status: 'running', temperature: 30, cycleTime: 15, partsProduced: 890 },
    { id: 'SLD01', name: 'Sorting Line with Camera', status: 'maintenance', temperature: 0, cycleTime: 0, partsProduced: 156 },
    { id: 'MPO01', name: 'Multi-Processing Station', status: 'running', temperature: 42, cycleTime: 105, partsProduced: 345 },
    { id: 'SSC01', name: 'Smart Sensor Cluster', status: 'running', temperature: 28, cycleTime: 5, partsProduced: 1230 },
    { id: 'DPS01', name: 'Digital Processing Station', status: 'running', temperature: 35, cycleTime: 80, partsProduced: 456 }
  ];

  constructor() {
    this.initializeCellData();
    this.startSimulation();
  }

  private initializeCellData(): void {
    this.initialData.forEach(data => {
      this.cellDataSubjects.set(data.id, new BehaviorSubject<CellData>({
        ...data,
        lastUpdate: new Date().toISOString()
      }));
    });
  }

  private startSimulation(): void {
    // Update cell data every 3 seconds
    interval(3000).subscribe(() => {
      this.cellDataSubjects.forEach((subject, cellId) => {
        const currentData = subject.value;
        const updated = this.generateUpdatedData(currentData);
        subject.next({
          ...updated,
          lastUpdate: new Date().toISOString()
        });
      });
    });
  }

  private generateUpdatedData(data: CellData): CellData {
    const statuses: Array<'idle' | 'running' | 'error' | 'maintenance'> = ['idle', 'running', 'error', 'maintenance'];
    
    // Mostly keep the same status, occasionally change
    const shouldChangeStatus = Math.random() < 0.1;
    const newStatus = shouldChangeStatus ? statuses[Math.floor(Math.random() * statuses.length)] : data.status;
    
    // Update temperature slightly
    const tempVariation = (Math.random() - 0.5) * 5;
    const newTemp = data.temperature ? Math.max(20, Math.min(60, data.temperature + tempVariation)) : undefined;
    
    // Increment parts produced if running
    const newParts = data.status === 'running' && data.partsProduced !== undefined
      ? data.partsProduced + Math.floor(Math.random() * 3)
      : data.partsProduced;
    
    return {
      ...data,
      status: newStatus,
      temperature: newTemp ? Math.round(newTemp) : undefined,
      partsProduced: newParts
    };
  }

  /**
   * Get observable for a specific cell's data
   */
  getCellData(cellId: string): Observable<CellData | undefined> {
    const subject = this.cellDataSubjects.get(cellId);
    return subject ? subject.asObservable() : new BehaviorSubject<CellData | undefined>(undefined).asObservable();
  }

  /**
   * Get all cell IDs that have data
   */
  getAllCellIds(): string[] {
    return Array.from(this.cellDataSubjects.keys());
  }

  /**
   * Get current snapshot of all cell data
   */
  getAllCellData(): Map<string, CellData> {
    const snapshot = new Map<string, CellData>();
    this.cellDataSubjects.forEach((subject, id) => {
      snapshot.set(id, subject.value);
    });
    return snapshot;
  }
}
