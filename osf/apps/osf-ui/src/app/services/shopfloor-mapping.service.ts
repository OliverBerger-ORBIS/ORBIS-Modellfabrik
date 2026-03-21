import { Injectable } from '@angular/core';
import { ORBIS_COLORS } from '../assets/color-palette';
import type {
  ShopfloorCellConfig,
  ShopfloorFtsConfig,
  ShopfloorLayoutConfig,
  ShopfloorModuleBySerial,
} from '../components/shopfloor-preview/shopfloor-layout.types';

export interface ModuleInfo {
  moduleType: string;
  serialNumber: string;
  cellId?: string;
  icon?: string;
}

/** AGV option for dropdown (serial for topics, label for display) */
export interface AgvOption {
  serial: string;
  label: string;
}

@Injectable({ providedIn: 'root' })
export class ShopfloorMappingService {
  private initialized = false;
  private serialToModule = new Map<string, ModuleInfo>();
  private moduleTypeToSerials = new Map<string, Set<string>>();
  private cellById = new Map<string, ShopfloorCellConfig>();
  private intersectionIdToCellId = new Map<string, string>();
  private cellIdToIntersectionId = new Map<string, string>();
  private ftsConfig: ShopfloorFtsConfig[] = [];

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
      if (cell.role === 'module' && cell.serial) {
        const moduleType = cell.name ?? cell.id;
        this.serialToModule.set(cell.serial, {
          moduleType,
          serialNumber: cell.serial,
          cellId: cell.id,
          icon: cell.icon,
        });
        if (!this.moduleTypeToSerials.has(moduleType)) {
          this.moduleTypeToSerials.set(moduleType, new Set());
        }
        this.moduleTypeToSerials.get(moduleType)!.add(cell.serial);
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
        serialNumber: serial,
        cellId: meta.cell_id,
        icon: cell?.icon,
      });
      if (!this.moduleTypeToSerials.has(moduleType)) {
        this.moduleTypeToSerials.set(moduleType, new Set());
      }
      this.moduleTypeToSerials.get(moduleType)!.add(serial);
    });

    // fts array (AGV/FTS with serial -> type FTS; enables AGV-1, AGV-2)
    this.ftsConfig = config.fts ?? [];
    this.ftsConfig.forEach((fts) => {
      const serial = fts.serial;
      if (serial) {
        this.serialToModule.set(serial, {
          moduleType: 'FTS',
          serialNumber: serial,
          icon: fts.icon,
        });
        if (!this.moduleTypeToSerials.has('FTS')) {
          this.moduleTypeToSerials.set('FTS', new Set());
        }
        this.moduleTypeToSerials.get('FTS')!.add(serial);
      }
    });

    this.initialized = true;
  }

  isInitialized(): boolean {
    return this.initialized;
  }

  getModuleBySerial(serialNumber: string): ModuleInfo | null {
    return this.serialToModule.get(serialNumber) ?? null;
  }

  getModuleTypeFromSerial(serialNumber: string): string | null {
    return this.serialToModule.get(serialNumber)?.moduleType ?? null;
  }

  getCellIdFromSerial(serialNumber: string): string | null {
    return this.serialToModule.get(serialNumber)?.cellId ?? null;
  }

  getCellBySerial(serialNumber: string): ShopfloorCellConfig | null {
    const cellId = this.getCellIdFromSerial(serialNumber);
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

  getModuleIcon(serialNumber: string): string | null {
    const cell = this.getCellBySerial(serialNumber);
    return cell?.icon ?? null;
  }

  getModuleIconByType(moduleType: string): string | null {
    const serial = this.getSerialFromModuleType(moduleType);
    if (!serial) {
      return null;
    }
    return this.getModuleIcon(serial);
  }

  /** AGV options for dropdown: serial (for MQTT topics) and label (e.g. AGV-1, AGV-2) */
  getAgvOptions(): AgvOption[] {
    return this.ftsConfig
      .filter((fts) => fts.serial)
      .map((fts) => ({ serial: fts.serial!, label: fts.label }));
  }

  /** Display label for AGV by serial (e.g. AGV-1, AGV-2) */
  getAgvLabel(serial: string): string | null {
    const fts = this.ftsConfig.find((f) => f.serial === serial);
    return fts?.label ?? null;
  }

  /**
   * Color for AGV by serial – unified shopfloor orange for all configured FTS (AGV-1/AGV-2).
   * Matches single-AGV display; see DR-24 amendment. Unknown serial → neutral grey.
   */
  getAgvColor(serial: string): string {
    const opts = this.getAgvOptions();
    const idx = opts.findIndex((o) => o.serial === serial);
    if (idx >= 0) {
      return ORBIS_COLORS.agv.agv1;
    }
    return ORBIS_COLORS.orbisGrey.medium;
  }
}

