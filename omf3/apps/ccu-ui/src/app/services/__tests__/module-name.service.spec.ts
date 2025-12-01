import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ModuleNameService } from '../module-name.service';

describe('ModuleNameService', () => {
  let service: ModuleNameService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ModuleNameService],
    });
    service = TestBed.inject(ModuleNameService);
  });

  describe('Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });
  });

  describe('getModuleFullName', () => {
    it('should return full name for HBW', () => {
      const name = service.getModuleFullName('HBW');
      expect(name).toBeTruthy();
      expect(typeof name).toBe('string');
    });

    it('should return full name for FTS', () => {
      const name = service.getModuleFullName('FTS');
      expect(name).toBeTruthy();
      expect(typeof name).toBe('string');
    });

    it('should return full name for MILL', () => {
      const name = service.getModuleFullName('MILL');
      expect(name).toBeTruthy();
      expect(typeof name).toBe('string');
    });

    it('should return full name for DRILL', () => {
      const name = service.getModuleFullName('DRILL');
      expect(name).toBeTruthy();
      expect(typeof name).toBe('string');
    });

    it('should return full name for DPS', () => {
      const name = service.getModuleFullName('DPS');
      expect(name).toBeTruthy();
      expect(typeof name).toBe('string');
    });

    it('should return full name for AIQS', () => {
      const name = service.getModuleFullName('AIQS');
      expect(name).toBeTruthy();
      expect(typeof name).toBe('string');
    });

    it('should return full name for CHRG', () => {
      const name = service.getModuleFullName('CHRG');
      expect(name).toBeTruthy();
      expect(typeof name).toBe('string');
    });

    it('should handle lowercase module ID', () => {
      const name = service.getModuleFullName('hbw');
      expect(name).toBeTruthy();
      expect(typeof name).toBe('string');
    });

    it('should handle mixed case module ID', () => {
      const name = service.getModuleFullName('Hbw');
      expect(name).toBeTruthy();
      expect(typeof name).toBe('string');
    });

    it('should return module ID for unknown module', () => {
      const name = service.getModuleFullName('UNKNOWN');
      expect(name).toBe('UNKNOWN');
    });
  });

  describe('getModuleDisplayText', () => {
    it('should return id-only format', () => {
      const text = service.getModuleDisplayText('HBW', 'id-only');
      expect(text).toBe('HBW');
    });

    it('should return full-only format', () => {
      const text = service.getModuleDisplayText('HBW', 'full-only');
      expect(text).toBeTruthy();
      expect(typeof text).toBe('string');
      expect(text).not.toContain('HBW');
    });

    it('should return id-full format', () => {
      const text = service.getModuleDisplayText('HBW', 'id-full');
      expect(text).toContain('HBW');
      expect(text).toContain('(');
    });

    it('should return full-id format', () => {
      const text = service.getModuleDisplayText('HBW', 'full-id');
      expect(text).toContain('HBW');
      expect(text).toContain('(');
    });

    it('should default to id-full format', () => {
      const text = service.getModuleDisplayText('HBW');
      expect(text).toContain('HBW');
      expect(text).toContain('(');
    });

    it('should handle unknown module with id-only format', () => {
      const text = service.getModuleDisplayText('UNKNOWN', 'id-only');
      expect(text).toBe('UNKNOWN');
    });

    it('should handle unknown module with full-only format', () => {
      const text = service.getModuleDisplayText('UNKNOWN', 'full-only');
      expect(text).toBe('UNKNOWN');
    });
  });

  describe('getModuleDisplayName', () => {
    it('should return display name object', () => {
      const displayName = service.getModuleDisplayName('HBW');
      expect(displayName).toBeDefined();
      expect(displayName.id).toBe('HBW');
      expect(displayName.fullName).toBeTruthy();
      expect(typeof displayName.fullName).toBe('string');
    });

    it('should handle lowercase module ID', () => {
      const displayName = service.getModuleDisplayName('hbw');
      expect(displayName.id).toBe('HBW');
    });

    it('should handle mixed case module ID', () => {
      const displayName = service.getModuleDisplayName('Hbw');
      expect(displayName.id).toBe('HBW');
    });

    it('should return module ID as fullName for unknown module', () => {
      const displayName = service.getModuleDisplayName('UNKNOWN');
      expect(displayName.id).toBe('UNKNOWN');
      expect(displayName.fullName).toBe('UNKNOWN');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty string module ID', () => {
      const name = service.getModuleFullName('');
      expect(name).toBe('');
    });

    it('should handle very long module ID', () => {
      const longId = 'A'.repeat(1000);
      const name = service.getModuleFullName(longId);
      expect(name).toBe(longId);
    });

    it('should handle module ID with special characters', () => {
      const specialId = 'MODULE-123!@#';
      const name = service.getModuleFullName(specialId);
      expect(name).toBe(specialId);
    });

    it('should handle module ID with whitespace', () => {
      const name = service.getModuleFullName('  HBW  ');
      expect(name).toBeTruthy();
    });

    it('should handle numeric module ID', () => {
      const name = service.getModuleFullName('123');
      expect(name).toBe('123');
    });

    it('should handle all format options for unknown module', () => {
      const formats: Array<'id-only' | 'full-only' | 'id-full' | 'full-id'> = [
        'id-only',
        'full-only',
        'id-full',
        'full-id',
      ];

      formats.forEach((format) => {
        const text = service.getModuleDisplayText('UNKNOWN', format);
        expect(text).toBeTruthy();
        expect(typeof text).toBe('string');
      });
    });

    it('should handle rapid calls with different modules', () => {
      const modules = ['HBW', 'FTS', 'MILL', 'DRILL', 'DPS', 'AIQS', 'CHRG'];
      modules.forEach((module) => {
        const name = service.getModuleFullName(module);
        expect(name).toBeTruthy();
      });
    });

    it('should handle display text with all formats for all modules', () => {
      const modules = ['HBW', 'FTS', 'MILL'];
      const formats: Array<'id-only' | 'full-only' | 'id-full' | 'full-id'> = [
        'id-only',
        'full-only',
        'id-full',
        'full-id',
      ];

      modules.forEach((module) => {
        formats.forEach((format) => {
          const text = service.getModuleDisplayText(module, format);
          expect(text).toBeTruthy();
          expect(typeof text).toBe('string');
        });
      });
    });

    it('should handle getModuleDisplayName for all known modules', () => {
      const modules = ['HBW', 'FTS', 'MILL', 'DRILL', 'DPS', 'AIQS', 'CHRG'];
      modules.forEach((module) => {
        const displayName = service.getModuleDisplayName(module);
        expect(displayName.id).toBe(module);
        expect(displayName.fullName).toBeTruthy();
        expect(displayName.fullName).not.toBe(module); // Should have translation
      });
    });
  });
});

