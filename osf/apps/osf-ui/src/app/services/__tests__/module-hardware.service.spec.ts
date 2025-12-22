import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { HttpClient } from '@angular/common/http';
import { ModuleHardwareService } from '../module-hardware.service';
import type {
  ModulesHardwareConfig,
  ModuleHardwareConfig,
  OpcUaStationConfig,
  TxtControllerConfig,
} from '../../components/shopfloor-preview/module-hardware.types';

describe('ModuleHardwareService', () => {
  let service: ModuleHardwareService;
  let httpMock: HttpTestingController;

  const mockConfig: ModulesHardwareConfig = {
    metadata: {
      version: '1.0.0',
      last_updated: '2025-12-22',
      description: 'Test hardware configuration',
    },
    modules: {
      SVR4H73275: {
        serial_number: 'SVR4H73275',
        module_name: 'DPS',
        module_type: 'Input/Output',
        opc_ua_station: {
          ip_address: '192.168.0.90',
          ip_range: '192.168.0.90',
          endpoint: 'opc.tcp://192.168.0.90:4840',
          description: '6-axis gripper arm with NFC scanner',
        },
        txt_controllers: [
          {
            id: 'TXT4.0-p0F4',
            name: 'TXT-DPS',
            ip_address: '192.168.0.102',
            description: 'NFC-Reader and Sensor-Station',
          },
        ],
      },
      SVR3QA0022: {
        serial_number: 'SVR3QA0022',
        module_name: 'HBW',
        module_type: 'Storage',
        opc_ua_station: {
          ip_address: '192.168.0.80',
          ip_range: '192.168.0.80-83',
          endpoint: 'opc.tcp://192.168.0.80:4840',
          description: 'Suction gripper with conveyor belt and high-bay warehouse',
        },
        txt_controllers: [],
      },
      '5iO4': {
        serial_number: '5iO4',
        module_name: 'FTS',
        module_type: 'Transport',
        opc_ua_station: null,
        txt_controllers: [
          {
            id: 'TXT4.0-5iO4',
            name: 'TXT-FTS',
            ip_address: '192.168.0.104',
            description: 'Transport Control System',
          },
        ],
      },
    },
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ModuleHardwareService],
    });
    service = TestBed.inject(ModuleHardwareService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    // Flush any remaining requests before verification
    httpMock.match('shopfloor/modules_hardware.json').forEach(req => req.flush(mockConfig));
    // Verify that no unexpected HTTP requests were made
    httpMock.verify();
  });

  describe('Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
      // Service constructor triggers HTTP request - flush it
      const reqs = httpMock.match('shopfloor/modules_hardware.json');
      expect(reqs.length).toBeGreaterThan(0);
      reqs.forEach(req => {
        expect(req.request.method).toBe('GET');
        req.flush(mockConfig);
      });
    });
  });

  describe('getModuleHardwareConfig', () => {
    beforeEach(() => {
      // Service constructor triggers HTTP request - flush it
      const reqs = httpMock.match('shopfloor/modules_hardware.json');
      reqs.forEach(req => req.flush(mockConfig));
    });

    it('should return module config for valid serial number', () => {
      const config = service.getModuleHardwareConfig('SVR4H73275');
      expect(config).toBeTruthy();
      expect(config?.module_name).toBe('DPS');
      expect(config?.module_type).toBe('Input/Output');
    });

    it('should return null for invalid serial number', () => {
      const config = service.getModuleHardwareConfig('INVALID');
      expect(config).toBeNull();
    });

    it('should return null if config not yet loaded', () => {
      // Create a new service instance that hasn't loaded yet
      const newService = new ModuleHardwareService(TestBed.inject(HttpClient));
      const config = newService.getModuleHardwareConfig('SVR4H73275');
      expect(config).toBeNull();
    });
  });

  describe('getModuleHardwareConfig$', () => {
    beforeEach(() => {
      // Service constructor triggers HTTP request - flush it
      const reqs = httpMock.match('shopfloor/modules_hardware.json');
      reqs.forEach(req => req.flush(mockConfig));
    });

    it('should return observable of module config', (done) => {
      service.getModuleHardwareConfig$('SVR4H73275').subscribe((config) => {
        expect(config).toBeTruthy();
        expect(config?.module_name).toBe('DPS');
        done();
      });
    });

    it('should return null for invalid serial number', (done) => {
      service.getModuleHardwareConfig$('INVALID').subscribe((config) => {
        expect(config).toBeNull();
        done();
      });
    });
  });

  describe('hasOpcUaServer', () => {
    beforeEach(() => {
      const reqs = httpMock.match('shopfloor/modules_hardware.json');
      reqs.forEach(req => req.flush(mockConfig));
    });

    it('should return true for module with OPC-UA server', () => {
      expect(service.hasOpcUaServer('SVR4H73275')).toBe(true);
      expect(service.hasOpcUaServer('SVR3QA0022')).toBe(true);
    });

    it('should return false for module without OPC-UA server', () => {
      expect(service.hasOpcUaServer('5iO4')).toBe(false);
    });

    it('should return false for invalid serial number', () => {
      expect(service.hasOpcUaServer('INVALID')).toBe(false);
    });
  });

  describe('getOpcUaEndpoint', () => {
    beforeEach(() => {
      const reqs = httpMock.match('shopfloor/modules_hardware.json');
      reqs.forEach(req => req.flush(mockConfig));
    });

    it('should return endpoint for module with OPC-UA server', () => {
      const endpoint = service.getOpcUaEndpoint('SVR4H73275');
      expect(endpoint).toBe('opc.tcp://192.168.0.90:4840');
    });

    it('should return null for module without OPC-UA server', () => {
      const endpoint = service.getOpcUaEndpoint('5iO4');
      expect(endpoint).toBeNull();
    });

    it('should return null for invalid serial number', () => {
      const endpoint = service.getOpcUaEndpoint('INVALID');
      expect(endpoint).toBeNull();
    });
  });

  describe('getOpcUaStation', () => {
    beforeEach(() => {
      const reqs = httpMock.match('shopfloor/modules_hardware.json');
      reqs.forEach(req => req.flush(mockConfig));
    });

    it('should return OPC-UA station config', () => {
      const station = service.getOpcUaStation('SVR4H73275');
      expect(station).toBeTruthy();
      expect(station?.ip_address).toBe('192.168.0.90');
      expect(station?.endpoint).toBe('opc.tcp://192.168.0.90:4840');
    });

    it('should return null for module without OPC-UA server', () => {
      const station = service.getOpcUaStation('5iO4');
      expect(station).toBeNull();
    });
  });

  describe('hasTxtController', () => {
    beforeEach(() => {
      const reqs = httpMock.match('shopfloor/modules_hardware.json');
      reqs.forEach(req => req.flush(mockConfig));
    });

    it('should return true for module with TXT controller', () => {
      expect(service.hasTxtController('SVR4H73275')).toBe(true);
      expect(service.hasTxtController('5iO4')).toBe(true);
    });

    it('should return false for module without TXT controller', () => {
      expect(service.hasTxtController('SVR3QA0022')).toBe(false);
    });

    it('should return false for invalid serial number', () => {
      expect(service.hasTxtController('INVALID')).toBe(false);
    });
  });

  describe('getTxtControllers', () => {
    beforeEach(() => {
      const reqs = httpMock.match('shopfloor/modules_hardware.json');
      reqs.forEach(req => req.flush(mockConfig));
    });

    it('should return TXT controllers array', () => {
      const controllers = service.getTxtControllers('SVR4H73275');
      expect(controllers).toHaveLength(1);
      expect(controllers[0].id).toBe('TXT4.0-p0F4');
      expect(controllers[0].name).toBe('TXT-DPS');
    });

    it('should return empty array for module without TXT controller', () => {
      const controllers = service.getTxtControllers('SVR3QA0022');
      expect(controllers).toEqual([]);
    });

    it('should return empty array for invalid serial number', () => {
      const controllers = service.getTxtControllers('INVALID');
      expect(controllers).toEqual([]);
    });
  });

  describe('getHardwareConfig$', () => {
    beforeEach(() => {
      const reqs = httpMock.match('shopfloor/modules_hardware.json');
      reqs.forEach(req => req.flush(mockConfig));
    });

    it('should return observable of complete config', (done) => {
      service.getHardwareConfig$().subscribe((config) => {
        expect(config).toBeTruthy();
        expect(config.modules).toBeDefined();
        expect(config.metadata).toBeDefined();
        done();
      });
    });

    it('should use cached config on subsequent calls', (done) => {
      // Second call should use cache (no new HTTP request)
      service.getHardwareConfig$().subscribe((config) => {
        expect(config).toBeTruthy();
        done();
      });

      httpMock.expectNone('shopfloor/modules_hardware.json');
    });
  });
});

