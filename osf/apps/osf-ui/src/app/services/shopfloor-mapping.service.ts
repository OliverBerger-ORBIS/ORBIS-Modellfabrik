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
  /** Station types first, then `fts[]` order — Shopfloor module table rows. */
  private static readonly SHOPFLOOR_TABLE_MODULE_TYPE_ORDER = [
    'DRILL',
    'HBW',
    'MILL',
    'AIQS',
    'DPS',
    'CHRG',
  ] as const;

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

  /**
   * Serials in canonical Shopfloor table order: fixed station sequence, then AGVs as in `fts[]`.
   */
  getShopfloorTableRowSerialOrder(): string[] {
    if (!this.initialized) {
      return [];
    }
    const ids: string[] = [];
    for (const t of ShopfloorMappingService.SHOPFLOOR_TABLE_MODULE_TYPE_ORDER) {
      const serials = this.getAllSerialsForModuleType(t);
      ids.push(...[...serials].sort());
    }
    for (const fts of this.ftsConfig) {
      if (fts.serial) {
        ids.push(fts.serial);
      }
    }
    return ids;
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

  /**
   * Resolve layout map key for a serial (exact match, then case-insensitive).
   * MQTT / brokers sometimes alter casing (e.g. `5iO4` vs `5IO4`).
   */
  private resolveSerialKey(serialNumber: string): string | null {
    if (!serialNumber) {
      return null;
    }
    if (this.serialToModule.has(serialNumber)) {
      return serialNumber;
    }
    const lower = serialNumber.toLowerCase();
    for (const key of this.serialToModule.keys()) {
      if (key.toLowerCase() === lower) {
        return key;
      }
    }
    return null;
  }

  getModuleBySerial(serialNumber: string): ModuleInfo | null {
    const key = this.resolveSerialKey(serialNumber);
    return key ? (this.serialToModule.get(key) ?? null) : null;
  }

  getModuleTypeFromSerial(serialNumber: string): string | null {
    return this.getModuleBySerial(serialNumber)?.moduleType ?? null;
  }

  getCellIdFromSerial(serialNumber: string): string | null {
    return this.getModuleBySerial(serialNumber)?.cellId ?? null;
  }

  /** Resolve hardware serial from layout cell id (e.g. CELL_1_3 → SVR4H73275). */
  getSerialFromCellId(cellId: string): string | null {
    for (const module of this.serialToModule.values()) {
      if (module.cellId === cellId) {
        return module.serialNumber;
      }
    }
    return null;
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
    const module = this.getModuleBySerial(serialNumber);
    if (module?.icon) {
      return module.icon;
    }
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
    const canonical = this.resolveSerialKey(serial) ?? serial;
    const fts = this.ftsConfig.find(
      (f) => f.serial === canonical || f.serial?.toLowerCase() === serial.toLowerCase()
    );
    return fts?.label ?? null;
  }

  /**
   * Color for AGV by serial – first FTS in layout = orange, second = warm yellow, rest = yellow.
   * Unknown serial → neutral grey.
   */
  getAgvColor(serial: string): string {
    const opts = this.getAgvOptions();
    const lower = serial.toLowerCase();
    const idx = opts.findIndex((o) => o.serial === serial || o.serial.toLowerCase() === lower);
    if (idx === 0) {
      return ORBIS_COLORS.agv.agv1;
    }
    if (idx === 1) {
      return ORBIS_COLORS.agv.agv2;
    }
    if (idx > 1) {
      return ORBIS_COLORS.agv.agv2;
    }
    return ORBIS_COLORS.orbisGrey.medium;
  }
}

