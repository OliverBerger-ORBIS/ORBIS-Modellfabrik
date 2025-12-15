import { TestBed } from '@angular/core/testing';
import { ShopfloorMappingService } from '../shopfloor-mapping.service';
import type {
  ShopfloorCellConfig,
  ShopfloorLayoutConfig,
} from '../../components/shopfloor-preview/shopfloor-layout.types';

describe('ShopfloorMappingService', () => {
  // Helper to create minimal config for testing
  function mockConfig(partial: Partial<ShopfloorLayoutConfig>): ShopfloorLayoutConfig {
    return {
      cells: [],
      intersection_map: {},
      modules_by_serial: {},
      ...partial,
    } as unknown as ShopfloorLayoutConfig;
  }
  let service: ShopfloorMappingService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ShopfloorMappingService],
    });
    service = TestBed.inject(ShopfloorMappingService);
  });

  describe('Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });

    it('should not be initialized by default', () => {
      expect(service.isInitialized()).toBe(false);
    });

    it('should be initialized after initializeLayout', () => {
      const config = mockConfig({
        cells: [],
        intersection_map: {},
        modules_by_serial: {},
      });

      service.initializeLayout(config);
      expect(service.isInitialized()).toBe(true);
    });

    it('should clear previous data on re-initialization', () => {
      const config1 = mockConfig({
        cells: [
          {
            id: 'cell-1',
            name: 'DRILL',
            role: 'module',
            serial_number: 'SVR001',
          } as ShopfloorCellConfig,
        ],
        intersection_map: {},
        modules_by_serial: {},
      });

      service.initializeLayout(config1);
      expect(service.getModuleBySerial('SVR001')).toBeDefined();

      const config2 = mockConfig({
        cells: [],
        intersection_map: {},
        modules_by_serial: {},
      });

      service.initializeLayout(config2);
      expect(service.getModuleBySerial('SVR001')).toBeNull();
    });
  });

  describe('Module mapping from cells', () => {
    beforeEach(() => {
      const config = mockConfig({
        cells: [
          {
            id: 'cell-drill',
            name: 'DRILL',
            role: 'module',
            serial_number: 'SVR001',
            icon: 'drill',
          } as ShopfloorCellConfig,
        ],
        intersection_map: {},
        modules_by_serial: {},
      });
      service.initializeLayout(config);
    });

    it('should return module info for valid serial', () => {
      const module = service.getModuleBySerial('SVR001');
      expect(module).toEqual({
        moduleType: 'DRILL',
        serialId: 'SVR001',
        cellId: 'cell-drill',
        icon: 'drill',
      });
    });

    it('should return module type from serial', () => {
      expect(service.getModuleTypeFromSerial('SVR001')).toBe('DRILL');
    });

    it('should return cell ID from serial', () => {
      expect(service.getCellIdFromSerial('SVR001')).toBe('cell-drill');
    });
  });

  describe('Module mapping from modules_by_serial', () => {
    beforeEach(() => {
      const config = mockConfig({
        cells: [
          {
            id: 'cell-mill',
            name: 'MILL',
            role: 'module',
            icon: 'mill-icon',
          } as ShopfloorCellConfig,
        ],
        intersection_map: {},
        modules_by_serial: {
          'SVR002': {
            cell_id: 'cell-mill',
            type: 'MILL',
          },
        },
      });
      service.initializeLayout(config);
    });

    it('should return module info from modules_by_serial', () => {
      const module = service.getModuleBySerial('SVR002');
      expect(module).toBeDefined();
      expect(module?.moduleType).toBe('MILL');
      expect(module?.cellId).toBe('cell-mill');
    });

    it('should return serial from module type', () => {
      const serial = service.getSerialFromModuleType('MILL');
      expect(serial).toBe('SVR002');
    });

    it('should return all serials for module type', () => {
      const serials = service.getAllSerialsForModuleType('MILL');
      expect(serials).toEqual(['SVR002']);
    });
  });

  describe('Intersection mapping', () => {
    beforeEach(() => {
      const config = mockConfig({
        cells: [
          {
            id: 'cell-intersection-1',
            role: 'intersection',
          } as ShopfloorCellConfig,
        ],
        intersection_map: {
          'intersection-1': 'cell-intersection-1',
        },
        modules_by_serial: {},
      });
      service.initializeLayout(config);
    });

    it('should return cell ID from intersection ID', () => {
      expect(service.getCellIdFromIntersection('intersection-1')).toBe('cell-intersection-1');
    });

    it('should return intersection ID from cell ID', () => {
      expect(service.getIntersectionIdFromCell('cell-intersection-1')).toBe('intersection-1');
    });
  });

  describe('Error cases', () => {
    beforeEach(() => {
      const config = mockConfig({
        cells: [],
        intersection_map: {},
        modules_by_serial: {},
      });
      service.initializeLayout(config);
    });

    it('should return null for unknown serial', () => {
      expect(service.getModuleBySerial('UNKNOWN')).toBeNull();
      expect(service.getModuleTypeFromSerial('UNKNOWN')).toBeNull();
      expect(service.getCellIdFromSerial('UNKNOWN')).toBeNull();
    });

    it('should return null for unknown module type', () => {
      expect(service.getSerialFromModuleType('UNKNOWN')).toBeNull();
    });

    it('should return empty array for unknown module type serials', () => {
      expect(service.getAllSerialsForModuleType('UNKNOWN')).toEqual([]);
    });

    it('should return null for unknown intersection', () => {
      expect(service.getCellIdFromIntersection('unknown')).toBeNull();
    });

    it('should return null for unknown cell', () => {
      expect(service.getIntersectionIdFromCell('unknown')).toBeNull();
      expect(service.getCellById('unknown')).toBeNull();
    });
  });

  describe('getAllModules', () => {
    it('should return empty array when not initialized', () => {
      expect(service.getAllModules()).toEqual([]);
    });

    it('should return all modules', () => {
      const config = mockConfig({
        cells: [
          {
            id: 'cell-1',
            name: 'MODULE1',
            role: 'module',
            serial_number: 'SVR011',
          } as ShopfloorCellConfig,
          {
            id: 'cell-2',
            name: 'MODULE2',
            role: 'module',
            serial_number: 'SVR012',
          } as ShopfloorCellConfig,
        ],
        intersection_map: {},
        modules_by_serial: {},
      });

      service.initializeLayout(config);

      const modules = service.getAllModules();
      expect(modules.length).toBe(2);
      expect(modules.map(m => m.serialId)).toContain('SVR011');
      expect(modules.map(m => m.serialId)).toContain('SVR012');
    });
  });

  describe('Icon methods', () => {
    beforeEach(() => {
      const config = mockConfig({
        cells: [
          {
            id: 'cell-icon-test',
            name: 'ICON_TEST',
            role: 'module',
            icon: 'test-icon',
          } as ShopfloorCellConfig,
        ],
        intersection_map: {},
        modules_by_serial: {
          'SVR009': {
            cell_id: 'cell-icon-test',
            type: 'ICON_TEST',
          },
        },
      });
      service.initializeLayout(config);
    });

    it('should return icon for valid serial', () => {
      expect(service.getModuleIcon('SVR009')).toBe('test-icon');
    });

    it('should return icon for valid module type', () => {
      expect(service.getModuleIconByType('ICON_TEST')).toBe('test-icon');
    });

    it('should return null for unknown serial icon', () => {
      expect(service.getModuleIcon('UNKNOWN')).toBeNull();
    });

    it('should return null for unknown module type icon', () => {
      expect(service.getModuleIconByType('UNKNOWN')).toBeNull();
    });
  });
});
