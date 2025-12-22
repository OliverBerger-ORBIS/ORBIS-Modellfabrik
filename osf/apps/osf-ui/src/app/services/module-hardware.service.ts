import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map, shareReplay, of } from 'rxjs';
import type {
  ModulesHardwareConfig,
  ModuleHardwareConfig,
  OpcUaStationConfig,
  TxtControllerConfig,
} from '../components/shopfloor-preview/module-hardware.types';

@Injectable({ providedIn: 'root' })
export class ModuleHardwareService {
  private hardwareConfig$?: Observable<ModulesHardwareConfig>;
  private configCache?: ModulesHardwareConfig;

  constructor(private readonly http: HttpClient) {
    // Load module hardware configuration
    this.hardwareConfig$ = this.http
      .get<ModulesHardwareConfig>('shopfloor/modules_hardware.json')
      .pipe(
        map((config) => {
          this.configCache = config;
          return config;
        }),
        shareReplay({ bufferSize: 1, refCount: true })
      );
    // Trigger load
    this.hardwareConfig$.subscribe();
  }

  /**
   * Get hardware configuration for a module by serial number
   * @param serialNumber Module serial number (e.g., "SVR4H73275")
   * @returns Observable of module hardware config or null if not found
   */
  getModuleHardwareConfig$(serialNumber: string): Observable<ModuleHardwareConfig | null> {
    if (this.configCache) {
      return of(this.configCache.modules[serialNumber] ?? null);
    }
    return this.hardwareConfig$!.pipe(
      map((config) => config.modules[serialNumber] ?? null)
    );
  }

  /**
   * Get hardware configuration for a module by serial number (synchronous)
   * Returns null if config is not yet loaded
   * @param serialNumber Module serial number (e.g., "SVR4H73275")
   * @returns Module hardware config or null if not found/not loaded
   */
  getModuleHardwareConfig(serialNumber: string): ModuleHardwareConfig | null {
    if (!this.configCache) {
      return null;
    }
    return this.configCache.modules[serialNumber] ?? null;
  }

  /**
   * Check if module has OPC-UA server
   * @param serialNumber Module serial number
   * @returns true if module has OPC-UA server, false otherwise
   */
  hasOpcUaServer(serialNumber: string): boolean {
    const config = this.getModuleHardwareConfig(serialNumber);
    return config?.opc_ua_station !== null && config?.opc_ua_station !== undefined;
  }

  /**
   * Get OPC-UA endpoint for a module
   * @param serialNumber Module serial number
   * @returns OPC-UA endpoint URL or null if not available
   */
  getOpcUaEndpoint(serialNumber: string): string | null {
    const config = this.getModuleHardwareConfig(serialNumber);
    return config?.opc_ua_station?.endpoint ?? null;
  }

  /**
   * Get OPC-UA station configuration for a module
   * @param serialNumber Module serial number
   * @returns OPC-UA station config or null if not available
   */
  getOpcUaStation(serialNumber: string): OpcUaStationConfig | null {
    const config = this.getModuleHardwareConfig(serialNumber);
    return config?.opc_ua_station ?? null;
  }

  /**
   * Check if module has TXT controller(s)
   * @param serialNumber Module serial number
   * @returns true if module has at least one TXT controller, false otherwise
   */
  hasTxtController(serialNumber: string): boolean {
    const config = this.getModuleHardwareConfig(serialNumber);
    return (config?.txt_controllers?.length ?? 0) > 0;
  }

  /**
   * Get all TXT controllers for a module
   * @param serialNumber Module serial number
   * @returns Array of TXT controller configs (empty array if none)
   */
  getTxtControllers(serialNumber: string): TxtControllerConfig[] {
    const config = this.getModuleHardwareConfig(serialNumber);
    return config?.txt_controllers ?? [];
  }

  /**
   * Get the raw hardware configuration (for advanced use cases)
   * @returns Observable of complete hardware configuration
   */
  getHardwareConfig$(): Observable<ModulesHardwareConfig> {
    if (!this.hardwareConfig$) {
      this.hardwareConfig$ = this.http.get<ModulesHardwareConfig>('shopfloor/modules_hardware.json').pipe(
        map((config) => {
          this.configCache = config;
          return config;
        }),
        shareReplay({ bufferSize: 1, refCount: true })
      );
    }
    return this.hardwareConfig$;
  }
}

