import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ExternalLinksService, ExternalLinksSettings } from '../external-links.service';
import { firstValueFrom } from 'rxjs';

describe('ExternalLinksService', () => {
  let service: ExternalLinksService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ExternalLinksService],
    });
    service = TestBed.inject(ExternalLinksService);
    httpMock = TestBed.inject(HttpTestingController);
    // ExternalLinksService loads repo config once on construction.
    // Most tests don't care about its content; flush an empty object to avoid pending requests.
    const req = httpMock.expectOne((r) => r.url.includes('assets/config/external-links.json'));
    req.flush({});
  });

  afterEach(() => {
    httpMock.verify();
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
      expect(settings.mesSystemUrl).toBeDefined();
      expect(settings.ewmSystemUrl).toBeDefined();
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
        mesSystemUrl: '',
        ewmSystemUrl: '',
      };

      service.updateSettings(newSettings);
      const current = service.current;

      expect(current.grafanaDashboardUrl).toBe('https://test.grafana.com');
      expect(current.dspControlUrl).toBe('https://test.dsp.com');
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
            mesSystemUrl: '',
            ewmSystemUrl: '',
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
    it('should handle repo config load errors gracefully', () => {
      // Create a new service instance to simulate load failure.
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        imports: [HttpClientTestingModule],
        providers: [ExternalLinksService],
      });
      const newService = TestBed.inject(ExternalLinksService);
      const newHttpMock = TestBed.inject(HttpTestingController);
      const req = newHttpMock.expectOne((r) => r.url.includes('assets/config/external-links.json'));
      req.error(new ProgressEvent('error'));
      newHttpMock.verify();

      // Falls back to defaults
      expect(newService.current.grafanaDashboardUrl).toBeTruthy();
    });

    it('should handle empty string URLs', () => {
      const emptySettings: ExternalLinksSettings = {
        grafanaDashboardUrl: '',
        smartfactoryDashboardUrl: '',
        dspControlUrl: '',
        managementCockpitUrl: '',
        erpSystemUrl: '',
        mesSystemUrl: '',
        ewmSystemUrl: '',
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
        mesSystemUrl: '',
        ewmSystemUrl: '',
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
        mesSystemUrl: '',
        ewmSystemUrl: '',
      };

      const settings2: ExternalLinksSettings = {
        grafanaDashboardUrl: 'https://test2.grafana.com',
        smartfactoryDashboardUrl: '/test-dsp',
        dspControlUrl: 'https://test.dsp.com',
        managementCockpitUrl: 'https://test.cockpit.com',
        erpSystemUrl: 'process',
        mesSystemUrl: '',
        ewmSystemUrl: '',
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
        mesSystemUrl: '',
        ewmSystemUrl: '',
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
        mesSystemUrl: '',
        ewmSystemUrl: '',
      };

      service.updateSettings(relativeSettings);
      const current = service.current;

      expect(current.grafanaDashboardUrl).toBe('/grafana');
    });
  });
});

