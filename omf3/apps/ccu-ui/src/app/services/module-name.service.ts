import { Injectable } from '@angular/core';

export interface ModuleDisplayName {
  id: string;
  fullName: string;
}

@Injectable({ providedIn: 'root' })
export class ModuleNameService {
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
   * Get module display name object
   */
  getModuleDisplayName(moduleId: string): ModuleDisplayName {
    return {
      id: moduleId.toUpperCase(),
      fullName: this.getModuleFullName(moduleId),
    };
  }
}
