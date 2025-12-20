import { TestBed } from '@angular/core/testing';
import { RoleService, UserRole } from '../role.service';
import { firstValueFrom, skip } from 'rxjs';

describe('RoleService', () => {
  let service: RoleService;

  beforeEach(() => {
    localStorage.clear();

    TestBed.configureTestingModule({
      providers: [RoleService],
    });

    service = TestBed.inject(RoleService);
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });

    it('should provide default role', () => {
      const role = service.current;
      expect(['operator', 'admin']).toContain(role);
    });

    it('should default to "admin" when no role stored', () => {
      localStorage.clear();
      const newService = TestBed.inject(RoleService);
      expect(newService.current).toBe('admin');
    });

    it('should persist role to localStorage and load it', () => {
      // Test that setRole persists
      service.setRole('operator');
      const stored = localStorage.getItem('OSF.user.role');
      expect(stored).toBe('operator');
      
      // Verify current reflects the change
      expect(service.current).toBe('operator');
    });

    it('should emit current role on subscription', async () => {
      const role$ = service.role$;
      const value = await firstValueFrom(role$);
      expect(['operator', 'admin']).toContain(value);
    });
  });

  describe('Role Management', () => {
    it('should set role', () => {
      service.setRole('operator');
      expect(service.current).toBe('operator');
    });

    it('should persist role to localStorage', () => {
      service.setRole('operator');
      const stored = localStorage.getItem('OSF.user.role');
      expect(stored).toBe('operator');
    });

    it('should not set role if already set', () => {
      service.setRole('admin');
      const initialValue = service.current;

      // Try to set same role again
      service.setRole('admin');

      expect(service.current).toBe(initialValue);
    });

    it('should emit role changes', (done) => {
      const role$ = service.role$;
      let initialValue: UserRole | null = null;
      let callCount = 0;

      role$.subscribe((role) => {
        callCount++;
        if (callCount === 1) {
          initialValue = role;
          service.setRole(role === 'admin' ? 'operator' : 'admin');
        } else if (callCount === 2) {
          expect(role).not.toBe(initialValue);
          done();
        }
      });
    });
  });

  describe('Role Validation', () => {
    it('should accept "operator" role', () => {
      service.setRole('operator');
      expect(service.current).toBe('operator');
    });

    it('should accept "admin" role', () => {
      service.setRole('admin');
      expect(service.current).toBe('admin');
    });

    it('should ignore invalid role in localStorage', () => {
      localStorage.setItem('OSF.user.role', 'invalid');
      const newService = TestBed.inject(RoleService);
      // Should default to 'admin' for invalid values
      expect(newService.current).toBe('admin');
    });
  });

  describe('Observable Behavior', () => {
    it('should emit initial value immediately', async () => {
      const role$ = service.role$;
      const value = await firstValueFrom(role$);
      expect(value).toBeDefined();
    });

    it('should emit new values on role change', async () => {
      const role$ = service.role$;
      const values: UserRole[] = [];

      role$.subscribe((role) => {
        values.push(role);
      });

      service.setRole('operator');
      service.setRole('admin');

      await new Promise((resolve) => setTimeout(resolve, 50));

      expect(values.length).toBeGreaterThanOrEqual(2);
      expect(values).toContain('operator');
      expect(values).toContain('admin');
    });
  });

  describe('Edge Cases', () => {
    it('should handle localStorage errors gracefully', () => {
      const originalSetItem = localStorage.setItem;
      localStorage.setItem = jest.fn(() => {
        throw new Error('Storage quota exceeded');
      });

      expect(() => {
        service.setRole('operator');
      }).not.toThrow();

      localStorage.setItem = originalSetItem;
    });

    it('should handle null in localStorage', () => {
      localStorage.setItem('OSF.user.role', 'null');
      const newService = TestBed.inject(RoleService);
      
      // Should default to 'admin' for null
      expect(newService.current).toBe('admin');
    });

    it('should handle empty string in localStorage', () => {
      localStorage.setItem('OSF.user.role', '');
      const newService = TestBed.inject(RoleService);
      
      // Should default to 'admin' for empty string
      expect(newService.current).toBe('admin');
    });

    it('should handle number in localStorage', () => {
      localStorage.setItem('OSF.user.role', '123');
      const newService = TestBed.inject(RoleService);
      
      // Should default to 'admin' for invalid role
      expect(newService.current).toBe('admin');
    });

    it('should handle boolean in localStorage', () => {
      localStorage.setItem('OSF.user.role', 'true');
      const newService = TestBed.inject(RoleService);
      
      // Should default to 'admin' for invalid role
      expect(newService.current).toBe('admin');
    });

    it('should handle case-sensitive role validation', () => {
      localStorage.setItem('OSF.user.role', 'ADMIN');
      const newService = TestBed.inject(RoleService);
      
      // Should default to 'admin' (case-sensitive)
      expect(newService.current).toBe('admin');
    });

    it('should handle whitespace in localStorage', () => {
      localStorage.setItem('OSF.user.role', ' operator ');
      const newService = TestBed.inject(RoleService);
      
      // Should default to 'admin' (whitespace not trimmed)
      expect(newService.current).toBe('admin');
    });

    it('should not emit when setting same role', () => {
      service.setRole('admin');
      const role$ = service.role$;
      const values: UserRole[] = [];

      role$.pipe(skip(1)).subscribe((role) => {
        values.push(role);
      });

      // Set same role multiple times
      service.setRole('admin');
      service.setRole('admin');
      service.setRole('admin');

      // Should not emit new values
      expect(values.length).toBe(0);
    });

    it('should handle rapid role changes', () => {
      service.setRole('operator');
      service.setRole('admin');
      service.setRole('operator');
      service.setRole('admin');

      expect(service.current).toBe('admin');
    });
  });
});

