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
      expect(settings.orbisWebsiteUrl).toBeDefined();
      expect(settings.dspControlUrl).toBeDefined();
      expect(settings.managementCockpitUrl).toBeDefined();
      expect(settings.grafanaDashboardUrl).toBeDefined();
      expect(settings.smartfactoryDashboardUrl).toBeDefined();
    });

    it('should emit current settings on subscription', async () => {
      const settings$ = service.settings$;
      const value = await firstValueFrom(settings$);
      expect(value).toBeDefined();
      expect(value.orbisWebsiteUrl).toBeDefined();
    });
  });

  describe('Settings Management', () => {
    it('should update settings', () => {
      const newSettings: ExternalLinksSettings = {
        orbisWebsiteUrl: 'https://test.orbis.de',
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        grafanaDashboardUrl: 'https://test.grafana.com',
        smartfactoryDashboardUrl: '/test-dsp',
      };

      service.updateSettings(newSettings);
      const current = service.current;

      expect(current.orbisWebsiteUrl).toBe('https://test.orbis.de');
      expect(current.dspControlUrl).toBe('https://test.dsp.com');
    });

    it('should persist settings to localStorage', () => {
      const newSettings: ExternalLinksSettings = {
        orbisWebsiteUrl: 'https://test.orbis.de',
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        grafanaDashboardUrl: 'https://test.grafana.com',
        smartfactoryDashboardUrl: '/test-dsp',
      };

      service.updateSettings(newSettings);

      const stored = localStorage.getItem('omf3.externalLinks');
      expect(stored).toBeTruthy();
      const parsed = JSON.parse(stored!);
      expect(parsed.orbisWebsiteUrl).toBe('https://test.orbis.de');
    });

    it('should load settings from localStorage', () => {
      const storedSettings: ExternalLinksSettings = {
        orbisWebsiteUrl: 'https://stored.orbis.de',
        dspControlUrl: 'https://stored.dsp.com',
        managementCockpitUrl: 'https://stored.cockpit.com',
        grafanaDashboardUrl: 'https://stored.grafana.com',
        smartfactoryDashboardUrl: '/stored-dsp',
      };

      localStorage.setItem('omf3.externalLinks', JSON.stringify(storedSettings));

      // Need to create new service instance to load from localStorage
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        providers: [ExternalLinksService],
      });
      const newService = TestBed.inject(ExternalLinksService);
      const current = newService.current;

      expect(current.orbisWebsiteUrl).toBe('https://stored.orbis.de');
    });

    it('should emit settings changes', (done) => {
      const settings$ = service.settings$;
      let callCount = 0;

      settings$.subscribe((settings) => {
        callCount++;
        if (callCount === 1) {
          // Initial value
          const newSettings: ExternalLinksSettings = {
            orbisWebsiteUrl: 'https://test.orbis.de',
            dspControlUrl: 'https://test.dsp.com',
            managementCockpitUrl: 'https://test.cockpit.com',
            grafanaDashboardUrl: 'https://test.grafana.com',
            smartfactoryDashboardUrl: '/test-dsp',
          };
          service.updateSettings(newSettings);
        } else if (callCount === 2) {
          expect(settings.orbisWebsiteUrl).toBe('https://test.orbis.de');
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
        orbisWebsiteUrl: 'https://test.orbis.de',
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        grafanaDashboardUrl: 'https://test.grafana.com',
        smartfactoryDashboardUrl: '/test-dsp',
      };

      expect(() => {
        service.updateSettings(newSettings);
      }).not.toThrow();

      // Settings should still be updated in memory
      expect(service.current.orbisWebsiteUrl).toBe('https://test.orbis.de');

      localStorage.setItem = originalSetItem;
    });

    it('should handle corrupted localStorage data', () => {
      localStorage.setItem('omf3.externalLinks', 'invalid json{{{');

      const newService = TestBed.inject(ExternalLinksService);
      const current = newService.current;

      // Should fallback to defaults
      expect(current).toBeDefined();
      expect(current.orbisWebsiteUrl).toBeDefined();
    });

    it('should handle partial settings in localStorage', () => {
      const partialSettings = {
        orbisWebsiteUrl: 'https://partial.orbis.de',
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
      expect(current.orbisWebsiteUrl).toBe('https://partial.orbis.de');
      expect(current.dspControlUrl).toBeDefined(); // From defaults
    });

    it('should handle empty string URLs', () => {
      const emptySettings: ExternalLinksSettings = {
        orbisWebsiteUrl: '',
        dspControlUrl: '',
        managementCockpitUrl: '',
        grafanaDashboardUrl: '',
        smartfactoryDashboardUrl: '',
      };

      service.updateSettings(emptySettings);
      const current = service.current;

      expect(current.orbisWebsiteUrl).toBe('');
      expect(current.dspControlUrl).toBe('');
    });

    it('should handle very long URLs', () => {
      const longUrl = 'https://' + 'a'.repeat(2000) + '.com';
      const longSettings: ExternalLinksSettings = {
        orbisWebsiteUrl: longUrl,
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        grafanaDashboardUrl: 'https://test.grafana.com',
        smartfactoryDashboardUrl: '/test-dsp',
      };

      service.updateSettings(longSettings);
      const current = service.current;

      expect(current.orbisWebsiteUrl).toBe(longUrl);
    });

    it('should handle rapid settings updates', () => {
      const settings1: ExternalLinksSettings = {
        orbisWebsiteUrl: 'https://test1.orbis.de',
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        grafanaDashboardUrl: 'https://test.grafana.com',
        smartfactoryDashboardUrl: '/test-dsp',
      };

      const settings2: ExternalLinksSettings = {
        orbisWebsiteUrl: 'https://test2.orbis.de',
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        grafanaDashboardUrl: 'https://test.grafana.com',
        smartfactoryDashboardUrl: '/test-dsp',
      };

      service.updateSettings(settings1);
      service.updateSettings(settings2);

      expect(service.current.orbisWebsiteUrl).toBe('https://test2.orbis.de');
    });

    it('should handle special characters in URLs', () => {
      const specialSettings: ExternalLinksSettings = {
        orbisWebsiteUrl: 'https://test.com/path?param=value&other=123',
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        grafanaDashboardUrl: 'https://test.grafana.com',
        smartfactoryDashboardUrl: '/test-dsp',
      };

      service.updateSettings(specialSettings);
      const current = service.current;

      expect(current.orbisWebsiteUrl).toBe('https://test.com/path?param=value&other=123');
    });

    it('should handle relative URLs', () => {
      const relativeSettings: ExternalLinksSettings = {
        orbisWebsiteUrl: '/relative/path',
        dspControlUrl: '/dsp',
        managementCockpitUrl: '/cockpit',
        grafanaDashboardUrl: '/grafana',
        smartfactoryDashboardUrl: '/dsp-action',
      };

      service.updateSettings(relativeSettings);
      const current = service.current;

      expect(current.orbisWebsiteUrl).toBe('/relative/path');
    });
  });
});

