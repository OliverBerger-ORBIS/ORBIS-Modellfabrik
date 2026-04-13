import { Injectable, inject } from '@angular/core';
import { Observable, filter, shareReplay } from 'rxjs';
import { ShopfloorLayoutConfig } from '../components/shopfloor-preview/shopfloor-layout.types';
import { AgvRouteService } from './agv-route.service';
import { ShopfloorMappingService } from './shopfloor-mapping.service';
import { ShopfloorLayoutService } from './shopfloor-layout.service';

export interface ModuleDisplayName {
  id: string;
  fullName: string;
}

export interface SerialToModuleInfo {
  moduleType: string;
  serialNumber: string;
}

@Injectable({ providedIn: 'root' })
export class ModuleNameService {
  private readonly ftsRouteService = inject(AgvRouteService);
  private readonly mappingService = inject(ShopfloorMappingService);
  private readonly layoutService = inject(ShopfloorLayoutService);
  private layoutConfig$?: Observable<ShopfloorLayoutConfig>;

  constructor() {
    // Ensure shopfloor layout is loaded once (shared across app) to build serial-to-module mapping.
    this.layoutConfig$ = this.layoutService.config$.pipe(
      filter((config): config is ShopfloorLayoutConfig => config !== null),
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  /**
   * Get module type from serial ID
   */
  getModuleTypeFromSerial(serialNumber: string): string | null {
    return this.mappingService.getModuleTypeFromSerial(serialNumber);
  }

  /**
   * Get full translated name for a module ID
   */
  getModuleFullName(moduleId: string): string {
    const translations: Record<string, string> = {
      HBW: $localize`:@@moduleNameHBW:High Bay Warehouse`,
      FTS: $localize`:@@moduleNameFTS:Automated Guided Vehicle`,
      MILL: $localize`:@@moduleNameMILL:Milling Station`,
      DRILL: $localize`:@@moduleNameDRILL:Drilling Station`,
      DPS: $localize`:@@moduleNameDPS:Delivery and Pickup Station`,
      AIQS: $localize`:@@moduleNameAIQS:AI Quality Station`,
      CHRG: $localize`:@@moduleNameCHRG:Charging Station`,
    };

    return translations[moduleId.toUpperCase()] ?? moduleId;
  }

  /**
   * Get display text in different formats
   */
  getModuleDisplayText(
    moduleId: string,
    format: 'id-only' | 'full-only' | 'id-full' | 'full-id' = 'id-full'
  ): string {
    const id = moduleId.toUpperCase();
    const fullName = this.getModuleFullName(id);

    switch (format) {
      case 'id-only':
        return id;
      case 'full-only':
        return fullName;
      case 'id-full':
        return `${id} (${fullName})`;
      case 'full-id':
        return `${fullName} (${id})`;
      default:
        return id;
    }
  }

  /**
   * Get location display text from serial ID or module ID
   * Returns: "MODULE_TYPE (Full Name) (Serial-ID)"
   * Handles intersections: "1" -> "1 (Intersection 1)"
   */
  getLocationDisplayText(location: string): { moduleType: string; fullName: string; serialNumber: string | null } {
    // Check if it's an intersection using AgvRouteService mapping
    const resolved = this.ftsRouteService.resolveNodeRef(location);
    if (resolved && resolved.startsWith('intersection:')) {
      // Extract intersection number from canonical form "intersection:1"
      const intersectionNumber = resolved.replace('intersection:', '');
      const intersectionNames: Record<string, string> = {
        '1': $localize`:@@intersection1:Intersection 1`,
        '2': $localize`:@@intersection2:Intersection 2`,
        '3': $localize`:@@intersection3:Intersection 3`,
        '4': $localize`:@@intersection4:Intersection 4`,
      };
      return {
        moduleType: intersectionNumber,
        fullName: intersectionNames[intersectionNumber] || `Intersection ${intersectionNumber}`,
        serialNumber: null,
      };
    }

    // Try to resolve as serial ID first
    const moduleType = this.getModuleTypeFromSerial(location);
    if (moduleType) {
      return {
        moduleType,
        fullName: this.getModuleFullName(moduleType),
        serialNumber: location,
      };
    }

    // Check if it's FTS
    if (location.toUpperCase() === 'FTS' || location.toUpperCase().includes('FTS')) {
      return {
        moduleType: 'FTS',
        fullName: this.getModuleFullName('FTS'),
        serialNumber: null,
      };
    }

    // Fallback: treat as module type
    return {
      moduleType: location.toUpperCase(),
      fullName: this.getModuleFullName(location),
      serialNumber: null,
    };
  }

  /**
   * Get module display name object
   */
  getModuleDisplayName(moduleId: string): ModuleDisplayName {
    return {
      id: moduleId.toUpperCase(),
      fullName: this.getModuleFullName(moduleId),
    };
  }
}
