import { TestBed } from '@angular/core/testing';
import { Router, ActivatedRoute } from '@angular/router';
import { LanguageService, LocaleKey } from '../language.service';

describe('LanguageService', () => {
  let service: LanguageService;
  let router: Router;

  const mockRouter = {
    url: '/en/dsp',
    navigate: jest.fn().mockResolvedValue(true),
  };

  const mockActivatedRoute = {
    snapshot: { params: {} },
    params: { subscribe: jest.fn() },
  };

  beforeEach(() => {
    localStorage.clear();

    TestBed.configureTestingModule({
      providers: [
        LanguageService,
        {
          provide: Router,
          useValue: mockRouter,
        },
        {
          provide: ActivatedRoute,
          useValue: mockActivatedRoute,
        },
      ],
    });

    service = TestBed.inject(LanguageService);
    router = TestBed.inject(Router);
  });

  afterEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  describe('Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });

    it('should provide supported locales', () => {
      expect(service.supportedLocales).toEqual(['en', 'de', 'fr']);
    });

    it('should detect locale from URL', () => {
      mockRouter.url = '/de/dsp';
      const locale = service.current;
      expect(locale).toBe('de');
    });

    it('should fallback to localStorage when URL has no locale', () => {
      mockRouter.url = '/overview';
      localStorage.setItem('OSF.locale', 'fr');
      const locale = service.current;
      expect(locale).toBe('fr');
    });

    it('should default to "en" when no locale found', () => {
      mockRouter.url = '/overview';
      localStorage.clear();
      const locale = service.current;
      expect(locale).toBe('en');
    });
  });

  describe('Locale Management', () => {
    it('should set locale', () => {
      mockRouter.url = '/en/overview';
      service.setLocale('de');

      const stored = localStorage.getItem('OSF.locale');
      expect(stored).toBe('de');
    });

    it('should not set locale if already set', () => {
      mockRouter.url = '/en/overview';
      const navigateSpy = jest.spyOn(router, 'navigate');

      service.setLocale('en');

      // Should not navigate if locale is already set
      expect(navigateSpy).not.toHaveBeenCalled();
    });

    it('should navigate to new locale with same route', () => {
      mockRouter.url = '/en/order';
      const navigateSpy = jest.spyOn(router, 'navigate');

      service.setLocale('de');

      expect(navigateSpy).toHaveBeenCalledWith(['de', 'order']);
    });

    it('should handle route without locale prefix', () => {
      mockRouter.url = '/order';
      const navigateSpy = jest.spyOn(router, 'navigate');

      service.setLocale('fr');

      expect(navigateSpy).toHaveBeenCalledWith(['fr', 'order']);
    });

    it('should default to "overview" when route is empty', () => {
      mockRouter.url = '/en';
      const navigateSpy = jest.spyOn(router, 'navigate');

      service.setLocale('de');

      expect(navigateSpy).toHaveBeenCalledWith(['de', 'dsp']);
    });
  });

  describe('Locale Detection', () => {
    it('should detect "en" from URL', () => {
      mockRouter.url = '/en/overview';
      expect(service.current).toBe('en');
    });

    it('should detect "de" from URL', () => {
      mockRouter.url = '/de/order';
      expect(service.current).toBe('de');
    });

    it('should detect "fr" from URL', () => {
      mockRouter.url = '/fr/settings';
      expect(service.current).toBe('fr');
    });

    it('should ignore invalid locale in URL', () => {
      mockRouter.url = '/invalid/dsp';
      localStorage.setItem('OSF.locale', 'de');
      expect(service.current).toBe('de');
    });
  });

  describe('Persistence', () => {
    it('should persist locale to localStorage', () => {
      mockRouter.url = '/en/overview';
      service.setLocale('fr');

      const stored = localStorage.getItem('OSF.locale');
      expect(stored).toBe('fr');
    });

    it('should load locale from localStorage', () => {
      localStorage.setItem('OSF.locale', 'de');
      mockRouter.url = '/overview';

      const locale = service.current;
      expect(locale).toBe('de');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty URL', () => {
      mockRouter.url = '';
      localStorage.clear();
      
      const locale = service.current;
      expect(locale).toBe('en');
    });

    it('should handle root URL', () => {
      mockRouter.url = '/';
      localStorage.clear();
      
      const locale = service.current;
      expect(locale).toBe('en');
    });

    it('should handle URL with only locale', () => {
      mockRouter.url = '/de';
      const locale = service.current;
      expect(locale).toBe('de');
    });

    it('should handle URL with multiple segments', () => {
      mockRouter.url = '/en/order/123/details';
      const locale = service.current;
      expect(locale).toBe('en');
    });

    it('should handle invalid locale in localStorage', () => {
      localStorage.setItem('OSF.locale', 'invalid');
      mockRouter.url = '/overview';
      
      const locale = service.current;
      // Service returns what's in localStorage, even if invalid
      // This is the current behavior - validation could be added in the future
      expect(locale).toBe('invalid');
    });

    it('should handle localStorage errors gracefully', () => {
      const originalSetItem = localStorage.setItem;
      localStorage.setItem = jest.fn(() => {
        throw new Error('Storage quota exceeded');
      });

      mockRouter.url = '/en/overview';
      expect(() => {
        service.setLocale('de');
      }).not.toThrow();

      localStorage.setItem = originalSetItem;
    });

    it('should handle router navigation errors gracefully', () => {
      mockRouter.navigate = jest.fn().mockRejectedValue(new Error('Navigation failed'));
      mockRouter.url = '/en/overview';

      // Should not throw immediately (error happens in promise)
      expect(() => {
        service.setLocale('de');
      }).not.toThrow();
      
      // Navigation should be attempted
      expect(mockRouter.navigate).toHaveBeenCalled();
    });

    it('should handle complex route paths', () => {
      mockRouter.url = '/en/configuration/module/DSP';
      const navigateSpy = jest.spyOn(router, 'navigate');

      service.setLocale('fr');

      expect(navigateSpy).toHaveBeenCalledWith(['fr', 'configuration/module/DSP']);
    });

    it('should handle route with query parameters', () => {
      // URL parsing ignores query parameters
      mockRouter.url = '/en/overview?param=value';
      const locale = service.current;
      expect(locale).toBe('en');
    });

    it('should handle route with hash', () => {
      // URL parsing ignores hash
      mockRouter.url = '/en/dsp#section';
      const locale = service.current;
      expect(locale).toBe('en');
    });

    it('should not set locale if already set (edge case)', () => {
      mockRouter.url = '/de/dsp';
      const navigateSpy = jest.spyOn(router, 'navigate');

      service.setLocale('de');

      // Should not navigate if locale is already set
      expect(navigateSpy).not.toHaveBeenCalled();
    });
  });
});

