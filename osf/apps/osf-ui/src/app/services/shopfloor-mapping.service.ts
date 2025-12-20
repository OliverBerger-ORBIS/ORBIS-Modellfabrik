import { Injectable } from '@angular/core';
import type {
  ShopfloorCellConfig,
  ShopfloorLayoutConfig,
  ShopfloorModuleBySerial,
} from '../components/shopfloor-preview/shopfloor-layout.types';

export interface ModuleInfo {
  moduleType: string;
  serialId: string;
  cellId?: string;
  icon?: string;
}

@Injectable({ providedIn: 'root' })
export class ShopfloorMappingService {
  private initialized = false;
  private serialToModule = new Map<string, ModuleInfo>();
  private moduleTypeToSerials = new Map<string, Set<string>>();
  private cellById = new Map<string, ShopfloorCellConfig>();
  private intersectionIdToCellId = new Map<string, string>();
  private cellIdToIntersectionId = new Map<string, string>();

  getAllModules(): ModuleInfo[] {
    return Array.from(this.serialToModule.values());
  }

  initializeLayout(config: ShopfloorLayoutConfig): void {
    this.serialToModule.clear();
    this.moduleTypeToSerials.clear();
    this.cellById.clear();
    this.intersectionIdToCellId.clear();
    this.cellIdToIntersectionId.clear();

    // Cells
    for (const cell of config.cells) {
      this.cellById.set(cell.id, cell);
      if (cell.role === 'intersection') {
        // intersection_map contains the stable ID mapping; use it below
        continue;
      }
      if (cell.role === 'module' && cell.serial_number) {
        const moduleType = cell.name ?? cell.id;
        this.serialToModule.set(cell.serial_number, {
          moduleType,
          serialId: cell.serial_number,
          cellId: cell.id,
          icon: cell.icon,
        });
        if (!this.moduleTypeToSerials.has(moduleType)) {
          this.moduleTypeToSerials.set(moduleType, new Set());
        }
        this.moduleTypeToSerials.get(moduleType)!.add(cell.serial_number);
      }
    }

    // intersection_map
    const intersectionEntries = Object.entries(config.intersection_map ?? {});
    intersectionEntries.forEach(([intersectionId, cellId]) => {
      this.intersectionIdToCellId.set(intersectionId, cellId);
      this.cellIdToIntersectionId.set(cellId, intersectionId);
    });

    // modules_by_serial (authoritative mapping of serial -> cell_id, type)
    const modulesBySerial: Record<string, ShopfloorModuleBySerial> = config.modules_by_serial ?? {};
    Object.entries(modulesBySerial).forEach(([serial, meta]) => {
      const cell = this.cellById.get(meta.cell_id);
      const moduleType = meta.type;
      this.serialToModule.set(serial, {
        moduleType,
        serialId: serial,
        cellId: meta.cell_id,
        icon: cell?.icon,
      });
      if (!this.moduleTypeToSerials.has(moduleType)) {
        this.moduleTypeToSerials.set(moduleType, new Set());
      }
      this.moduleTypeToSerials.get(moduleType)!.add(serial);
    });

    this.initialized = true;
  }

  isInitialized(): boolean {
    return this.initialized;
  }

  getModuleBySerial(serialId: string): ModuleInfo | null {
    return this.serialToModule.get(serialId) ?? null;
  }

  getModuleTypeFromSerial(serialId: string): string | null {
    return this.serialToModule.get(serialId)?.moduleType ?? null;
  }

  getCellIdFromSerial(serialId: string): string | null {
    return this.serialToModule.get(serialId)?.cellId ?? null;
  }

  getCellBySerial(serialId: string): ShopfloorCellConfig | null {
    const cellId = this.getCellIdFromSerial(serialId);
    return cellId ? this.getCellById(cellId) : null;
  }

  getSerialFromModuleType(moduleType: string): string | null {
    const serials = this.moduleTypeToSerials.get(moduleType);
    if (!serials || serials.size === 0) {
      return null;
    }
    // Return the first available serial for this module type
    return Array.from(serials.values())[0];
  }

  getAllSerialsForModuleType(moduleType: string): string[] {
    const serials = this.moduleTypeToSerials.get(moduleType);
    return serials ? Array.from(serials.values()) : [];
  }

  getCellIdFromIntersection(intersectionId: string): string | null {
    return this.intersectionIdToCellId.get(intersectionId) ?? null;
  }

  getIntersectionIdFromCell(cellId: string): string | null {
    return this.cellIdToIntersectionId.get(cellId) ?? null;
  }

  getCellById(cellId: string): ShopfloorCellConfig | null {
    return this.cellById.get(cellId) ?? null;
  }

  getModuleIcon(serialId: string): string | null {
    const cell = this.getCellBySerial(serialId);
    return cell?.icon ?? null;
  }

  getModuleIconByType(moduleType: string): string | null {
    const serial = this.getSerialFromModuleType(moduleType);
    if (!serial) {
      return null;
    }
    return this.getModuleIcon(serial);
  }
}

