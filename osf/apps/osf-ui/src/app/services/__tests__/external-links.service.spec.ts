import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ExternalLinksService, ExternalLinksSettings } from '../external-links.service';
import { firstValueFrom } from 'rxjs';

const fullSettings = (over: Partial<ExternalLinksSettings> = {}): ExternalLinksSettings => ({
  bpErpApplicationUrl: 'process',
  bpPlanningApplicationUrl: '',
  bpMesApplicationUrl: '',
  bpEwmApplicationUrl: '',
  bpCrmApplicationUrl: '',
  bpAnalyticsApplicationUrl: 'https://grafana.example.com',
  bpDataLakeApplicationUrl: '',
  dspSmartfactoryDashboardUrl: '/dsp-action',
  dspEdgeUrl: 'https://edge.example.com',
  dspManagementCockpitUrl: 'https://mc.example.com',
  ...over,
});

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
      expect(settings.dspSmartfactoryDashboardUrl).toBeDefined();
      expect(settings.dspEdgeUrl).toBeDefined();
      expect(settings.dspManagementCockpitUrl).toBeDefined();
      expect(settings.bpAnalyticsApplicationUrl).toBeDefined();
    });

    it('should emit current settings on subscription', async () => {
      const value = await firstValueFrom(service.settings$);
      expect(value.dspEdgeUrl).toBeDefined();
    });
  });

  describe('Settings Management', () => {
    it('should update settings', () => {
      const newSettings = fullSettings({
        dspEdgeUrl: 'https://test.dsp.com',
        bpAnalyticsApplicationUrl: 'https://test.grafana.com',
      });

      service.updateSettings(newSettings);
      const current = service.current;

      expect(current.bpAnalyticsApplicationUrl).toBe('https://test.grafana.com');
      expect(current.dspEdgeUrl).toBe('https://test.dsp.com');
    });

    it('should emit settings changes', (done) => {
      let callCount = 0;
      service.settings$.subscribe((settings) => {
        callCount++;
        if (callCount === 1) {
          service.updateSettings(
            fullSettings({ dspEdgeUrl: 'https://x.com', bpAnalyticsApplicationUrl: 'https://g.com' })
          );
        } else if (callCount === 2) {
          expect(settings.bpAnalyticsApplicationUrl).toBe('https://g.com');
          done();
        }
      });
    });
  });

  describe('resolveBpApplicationUrl', () => {
    it('returns only bp field without legacy fallback', () => {
      service.updateSettings(
        fullSettings({
          bpErpApplicationUrl: '',
          bpMesApplicationUrl: 'https://mes.example',
        })
      );
      expect(service.resolveBpApplicationUrl('bp-erp')).toBeUndefined();
      expect(service.resolveBpApplicationUrl('bp-mes')).toBe('https://mes.example');
    });
  });

  describe('Edge Cases', () => {
    it('should handle repo config load errors gracefully', () => {
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

      expect(newService.current.bpAnalyticsApplicationUrl).toBeTruthy();
    });

    it('should handle empty string URLs', () => {
      service.updateSettings(
        fullSettings({
          dspEdgeUrl: '',
          dspManagementCockpitUrl: '',
          bpAnalyticsApplicationUrl: '',
        })
      );
      const current = service.current;
      expect(current.dspEdgeUrl).toBe('');
      expect(current.bpAnalyticsApplicationUrl).toBe('');
    });

    it('should handle very long URLs', () => {
      const longUrl = 'https://' + 'a'.repeat(2000) + '.com';
      service.updateSettings(fullSettings({ bpAnalyticsApplicationUrl: longUrl }));
      expect(service.current.bpAnalyticsApplicationUrl).toBe(longUrl);
    });

    it('should handle rapid settings updates', () => {
      service.updateSettings(fullSettings({ bpAnalyticsApplicationUrl: 'https://test1.grafana.com' }));
      service.updateSettings(fullSettings({ bpAnalyticsApplicationUrl: 'https://test2.grafana.com' }));
      expect(service.current.bpAnalyticsApplicationUrl).toBe('https://test2.grafana.com');
    });

    it('should handle special characters in URLs', () => {
      const u = 'https://test.com/path?param=value&other=123';
      service.updateSettings(fullSettings({ bpAnalyticsApplicationUrl: u }));
      expect(service.current.bpAnalyticsApplicationUrl).toBe(u);
    });

    it('should handle relative URLs', () => {
      service.updateSettings(
        fullSettings({
          bpAnalyticsApplicationUrl: '/grafana',
          dspEdgeUrl: '/dsp',
          dspManagementCockpitUrl: '/cockpit',
        })
      );
      expect(service.current.bpAnalyticsApplicationUrl).toBe('/grafana');
    });
  });
});
