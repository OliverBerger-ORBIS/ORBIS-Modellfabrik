import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { WorkpieceHistoryService } from '../workpiece-history.service';
import { MessageMonitorService } from '../message-monitor.service';
import { ModuleNameService } from '../module-name.service';
import { EnvironmentService } from '../environment.service';
import { FtsRouteService } from '../fts-route.service';
import { MessageValidationService } from '../message-validation.service';
import { MessagePersistenceService } from '../message-persistence.service';
import { of } from 'rxjs';

describe('WorkpieceHistoryService', () => {
  let service: WorkpieceHistoryService;
  let messageMonitor: MessageMonitorService;
  let moduleNameService: ModuleNameService;
  let environmentService: EnvironmentService;
  let ftsRouteService: FtsRouteService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        WorkpieceHistoryService,
        MessageMonitorService,
        ModuleNameService,
        EnvironmentService,
        FtsRouteService,
        MessageValidationService,
        MessagePersistenceService,
      ],
    });
    service = TestBed.inject(WorkpieceHistoryService);
    messageMonitor = TestBed.inject(MessageMonitorService);
    moduleNameService = TestBed.inject(ModuleNameService);
    environmentService = TestBed.inject(EnvironmentService);
    ftsRouteService = TestBed.inject(FtsRouteService);

    // Mock necessary methods
    jest.spyOn(messageMonitor, 'getLastMessage').mockReturnValue(of(null));
  });

  afterEach(() => {
    service.ngOnDestroy();
  });

  describe('Service Creation', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });
  });

  describe('getHistory$', () => {
    it('should return observable for environment', (done) => {
      const history$ = service.getHistory$('mock');
      
      history$.subscribe((historyMap) => {
        expect(historyMap).toBeInstanceOf(Map);
        expect(historyMap.size).toBe(0);
        done();
      });
    });
  });

  describe('getSnapshot', () => {
    it('should return history snapshot', () => {
      const snapshot = service.getSnapshot('mock');
      expect(snapshot).toBeInstanceOf(Map);
      expect(snapshot.size).toBe(0);
    });
  });

  describe('getWorkpieceHistory', () => {
    it('should return observable for specific workpiece', (done) => {
      const workpiece$ = service.getWorkpieceHistory('mock', 'wp-123');
      
      workpiece$.subscribe((history) => {
        expect(history).toBeUndefined();
        done();
      });
    });
  });

  describe('clear', () => {
    it('should clear history for environment', () => {
      // Initialize first
      service.initialize('mock');
      
      // Clear
      service.clear('mock');
      
      // Verify cleared
      const snapshot = service.getSnapshot('mock');
      expect(snapshot.size).toBe(0);
    });

    it('should not throw when clearing non-initialized environment', () => {
      expect(() => service.clear('non-existent')).not.toThrow();
    });
  });

  describe('initialize', () => {
    it('should initialize tracking for environment', () => {
      service.initialize('mock');
      // Should set up subscriptions without throwing
      expect(service).toBeTruthy();
    });

    it('should not re-initialize if already initialized', () => {
      service.initialize('mock');
      const spy = jest.spyOn(messageMonitor, 'getLastMessage');
      
      // Try to initialize again
      service.initialize('mock');
      
      // Should not call getLastMessage again for the same environment
      // (First initialization already called it)
      expect(spy).not.toHaveBeenCalledTimes(2);
    });
  });

  describe('ngOnDestroy', () => {
    it('should clean up subscriptions', () => {
      service.initialize('mock');
      
      expect(() => service.ngOnDestroy()).not.toThrow();
    });

    it('should handle destroy when not initialized', () => {
      expect(() => service.ngOnDestroy()).not.toThrow();
    });
  });
});
