import { TestBed } from '@angular/core/testing';
import { ExternalLinksService, ExternalLinksSettings } from '../external-links.service';
import { firstValueFrom } from 'rxjs';

describe('ExternalLinksService', () => {
  let service: ExternalLinksService;

  beforeEach(() => {
    localStorage.clear();

    TestBed.configureTestingModule({
      providers: [ExternalLinksService],
    });
    service = TestBed.inject(ExternalLinksService);
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });

    it('should provide default settings', () => {
      const settings = service.current;
      expect(settings).toBeDefined();
      expect(settings.grafanaDashboardUrl).toBeDefined();
      expect(settings.smartfactoryDashboardUrl).toBeDefined();
      expect(settings.dspControlUrl).toBeDefined();
      expect(settings.managementCockpitUrl).toBeDefined();
      expect(settings.erpSystemUrl).toBeDefined();
    });

    it('should emit current settings on subscription', async () => {
      const settings$ = service.settings$;
      const value = await firstValueFrom(settings$);
      expect(value).toBeDefined();
      expect(value.grafanaDashboardUrl).toBeDefined();
    });
  });

  describe('Settings Management', () => {
    it('should update settings', () => {
      const newSettings: ExternalLinksSettings = {
        grafanaDashboardUrl: 'https://test.grafana.com',
        smartfactoryDashboardUrl: '/test-dsp',
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        erpSystemUrl: 'process',
      };

      service.updateSettings(newSettings);
      const current = service.current;

      expect(current.grafanaDashboardUrl).toBe('https://test.grafana.com');
      expect(current.dspControlUrl).toBe('https://test.dsp.com');
    });

    it('should persist settings to localStorage', () => {
      const newSettings: ExternalLinksSettings = {
        grafanaDashboardUrl: 'https://test.grafana.com',
        smartfactoryDashboardUrl: '/test-dsp',
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        erpSystemUrl: 'process',
      };

      service.updateSettings(newSettings);

      const stored = localStorage.getItem('omf3.externalLinks');
      expect(stored).toBeTruthy();
      const parsed = JSON.parse(stored!);
      expect(parsed.grafanaDashboardUrl).toBe('https://test.grafana.com');
    });

    it('should load settings from localStorage', () => {
      const storedSettings: ExternalLinksSettings = {
        grafanaDashboardUrl: 'https://stored.grafana.com',
        smartfactoryDashboardUrl: '/stored-dsp',
        dspControlUrl: 'https://stored.dsp.com',
        managementCockpitUrl: 'https://stored.cockpit.com',
        erpSystemUrl: 'process',
      };

      localStorage.setItem('omf3.externalLinks', JSON.stringify(storedSettings));

      // Need to create new service instance to load from localStorage
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        providers: [ExternalLinksService],
      });
      const newService = TestBed.inject(ExternalLinksService);
      const current = newService.current;

      expect(current.grafanaDashboardUrl).toBe('https://stored.grafana.com');
    });

    it('should emit settings changes', (done) => {
      const settings$ = service.settings$;
      let callCount = 0;

      settings$.subscribe((settings) => {
        callCount++;
        if (callCount === 1) {
          // Initial value
          const newSettings: ExternalLinksSettings = {
            grafanaDashboardUrl: 'https://test.grafana.com',
            smartfactoryDashboardUrl: '/test-dsp',
            dspControlUrl: 'https://test.dsp.com',
            managementCockpitUrl: 'https://test.cockpit.com',
            erpSystemUrl: 'process',
          };
          service.updateSettings(newSettings);
        } else if (callCount === 2) {
          expect(settings.grafanaDashboardUrl).toBe('https://test.grafana.com');
          done();
        }
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle localStorage errors gracefully', () => {
      const originalSetItem = localStorage.setItem;
      localStorage.setItem = jest.fn(() => {
        throw new Error('Storage quota exceeded');
      });

      const newSettings: ExternalLinksSettings = {
        grafanaDashboardUrl: 'https://test.grafana.com',
        smartfactoryDashboardUrl: '/test-dsp',
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        erpSystemUrl: 'process',
      };

      expect(() => {
        service.updateSettings(newSettings);
      }).not.toThrow();

      // Settings should still be updated in memory
      expect(service.current.grafanaDashboardUrl).toBe('https://test.grafana.com');

      localStorage.setItem = originalSetItem;
    });

    it('should handle corrupted localStorage data', () => {
      localStorage.setItem('omf3.externalLinks', 'invalid json{{{');

      const newService = TestBed.inject(ExternalLinksService);
      const current = newService.current;

      // Should fallback to defaults
      expect(current).toBeDefined();
      expect(current.grafanaDashboardUrl).toBeDefined();
    });

    it('should handle partial settings in localStorage', () => {
      const partialSettings = {
        grafanaDashboardUrl: 'https://partial.grafana.com',
      };

      localStorage.setItem('omf3.externalLinks', JSON.stringify(partialSettings));

      // Need to create new service instance to load from localStorage
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        providers: [ExternalLinksService],
      });
      const newService = TestBed.inject(ExternalLinksService);
      const current = newService.current;

      // Should merge with defaults
      expect(current.grafanaDashboardUrl).toBe('https://partial.grafana.com');
      expect(current.dspControlUrl).toBeDefined(); // From defaults
    });

    it('should handle empty string URLs', () => {
      const emptySettings: ExternalLinksSettings = {
        grafanaDashboardUrl: '',
        smartfactoryDashboardUrl: '',
        dspControlUrl: '',
        managementCockpitUrl: '',
        erpSystemUrl: '',
      };

      service.updateSettings(emptySettings);
      const current = service.current;

      expect(current.grafanaDashboardUrl).toBe('');
      expect(current.dspControlUrl).toBe('');
    });

    it('should handle very long URLs', () => {
      const longUrl = 'https://' + 'a'.repeat(2000) + '.com';
      const longSettings: ExternalLinksSettings = {
        grafanaDashboardUrl: longUrl,
        smartfactoryDashboardUrl: '/test-dsp',
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        erpSystemUrl: 'process',
      };

      service.updateSettings(longSettings);
      const current = service.current;

      expect(current.grafanaDashboardUrl).toBe(longUrl);
    });

    it('should handle rapid settings updates', () => {
      const settings1: ExternalLinksSettings = {
        grafanaDashboardUrl: 'https://test1.grafana.com',
        smartfactoryDashboardUrl: '/test-dsp',
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        erpSystemUrl: 'process',
      };

      const settings2: ExternalLinksSettings = {
        grafanaDashboardUrl: 'https://test2.grafana.com',
        smartfactoryDashboardUrl: '/test-dsp',
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        erpSystemUrl: 'process',
      };

      service.updateSettings(settings1);
      service.updateSettings(settings2);

      expect(service.current.grafanaDashboardUrl).toBe('https://test2.grafana.com');
    });

    it('should handle special characters in URLs', () => {
      const specialSettings: ExternalLinksSettings = {
        grafanaDashboardUrl: 'https://test.com/path?param=value&other=123',
        smartfactoryDashboardUrl: '/test-dsp',
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        erpSystemUrl: 'process',
      };

      service.updateSettings(specialSettings);
      const current = service.current;

      expect(current.grafanaDashboardUrl).toBe('https://test.com/path?param=value&other=123');
    });

    it('should handle relative URLs', () => {
      const relativeSettings: ExternalLinksSettings = {
        grafanaDashboardUrl: '/grafana',
        smartfactoryDashboardUrl: '/dsp-action',
        dspControlUrl: '/dsp',
        managementCockpitUrl: '/cockpit',
        erpSystemUrl: 'process',
      };

      service.updateSettings(relativeSettings);
      const current = service.current;

      expect(current.grafanaDashboardUrl).toBe('/grafana');
    });
  });
});

