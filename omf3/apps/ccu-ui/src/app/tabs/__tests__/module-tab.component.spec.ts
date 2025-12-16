import { BehaviorSubject, of } from 'rxjs';
import type { ModuleOverviewState, ModuleOverviewStatus, TransportOverviewStatus } from '@omf3/entities';
import { ModuleTabComponent } from '../module-tab.component';
import type { EnvironmentService } from '../../services/environment.service';
import type { ModuleNameService } from '../../services/module-name.service';
import type { ConnectionService } from '../../services/connection.service';
import type { ModuleOverviewStateService } from '../../services/module-overview-state.service';
import type { MessageMonitorService } from '../../services/message-monitor.service';
import type { HttpClient } from '@angular/common/http';
import type { ChangeDetectorRef } from '@angular/core';
import type { ShopfloorMappingService } from '../../services/shopfloor-mapping.service';
import type { ActivatedRoute, Router } from '@angular/router';

jest.mock('../../mock-dashboard', () => {
  const mockCommands = {
    calibrateModule: jest.fn(),
    setFtsCharge: jest.fn(),
    dockFts: jest.fn(),
  };

  return {
    getDashboardController: jest.fn(() => ({
      streams: {
        moduleOverview$: {
          pipe: jest.fn(() => ({
            pipe: jest.fn(),
          })),
        },
      },
      commands: mockCommands,
      loadFixture: jest.fn(),
      getCurrentFixture: jest.fn(() => 'startup'),
    })),
  };
});

const createComponent = () => {
  const environmentStub = {
    current: { key: 'mock' },
    environment$: new BehaviorSubject({ key: 'mock' }),
  } as unknown as EnvironmentService;

  const moduleNameServiceStub = {
    getModuleDisplayText: jest.fn((type: string) => `${type.toUpperCase()} (Test)`),
    getModuleDisplayName: jest.fn((type: string) => ({
      fullName: `${type.toUpperCase()} Station`,
      shortName: type.toUpperCase(),
    })),
  } as unknown as ModuleNameService;

  const connectionServiceStub = {
    state$: new BehaviorSubject<'disconnected'>('disconnected'),
  } as unknown as ConnectionService;

  const moduleOverviewStateStub = {
    getState$: jest.fn(() => new BehaviorSubject<ModuleOverviewState | null>(null)),
    getSnapshot: jest.fn(() => null),
    setState: jest.fn(),
    clear: jest.fn(),
  } as unknown as ModuleOverviewStateService;

  const messageMonitorStub = {
    getLastMessage: jest.fn(),
    getHistory: jest.fn(),
    getTopics: jest.fn(() => []),
    addMessage: jest.fn(),
  } as unknown as MessageMonitorService;

  const httpStub = {
    get: jest.fn(() => of({ cells: [] })),
  } as unknown as HttpClient;

  const cdrStub = {
    markForCheck: jest.fn(),
  } as unknown as ChangeDetectorRef;

  const mappingServiceStub = {
    initializeLayout: jest.fn(),
    getAllModules: jest.fn(() => []),
  } as unknown as ShopfloorMappingService;

  const routeStub = {
    queryParams: new BehaviorSubject({}),
  } as unknown as ActivatedRoute;

  const routerStub = {
    navigate: jest.fn(() => Promise.resolve(true)),
  } as unknown as Router;

  const initSpy = jest
    .spyOn(ModuleTabComponent.prototype as any, 'initializeStreams')
    .mockImplementation(() => {});

  const component = new ModuleTabComponent(
    environmentStub,
    moduleNameServiceStub,
    connectionServiceStub,
    moduleOverviewStateStub,
    messageMonitorStub,
    cdrStub,
    httpStub,
    mappingServiceStub,
    routeStub,
    routerStub
  );
  initSpy.mockRestore();
  return component;
};

describe('ModuleTabComponent registry metadata', () => {
  it('marks an unknown FTS transport as not registered', () => {
    const component = createComponent();
    const transport: TransportOverviewStatus = {
      id: '4711',
      connected: true,
      availability: 'READY',
      messageCount: 1,
      lastUpdate: '2025-11-10T17:48:00.000Z',
    };

    const row = (component as any).createTransportRow(transport);
    expect(row.registryActive).toBe(false);
  });

  it('marks a Hochofen module as not registered', () => {
    const component = createComponent();
    const moduleStatus: ModuleOverviewStatus = {
      id: 'HOSE0815',
      subType: 'OVEN',
      connected: true,
      availability: 'READY',
      configured: false,
      messageCount: 1,
      lastUpdate: '2025-11-10T17:48:00.000Z',
    };

    const row = (component as any).createModuleRow(moduleStatus);
    expect(row.registryActive).toBe(false);
  });
});

describe('ModuleTabComponent sidebar and selection', () => {
  it('should preserve module selection when closing sidebar', () => {
    const component = createComponent();
    
    // Set up a selected module
    const testSerialId = 'SVR3QA0022';
    const testModuleName = 'DRILL Station';
    const testIcon = 'assets/svg/shopfloor/stations/drill-station.svg';
    const testMeta = {
      availability: 'READY' as const,
      availabilityLabel: 'Available',
      availabilityIcon: '🟢',
      availabilityClass: 'availability availability--ready',
      connected: true,
      connectionIcon: '📶',
      connectionLabel: 'Connected',
    };

    component.selectedModuleSerialId = testSerialId;
    component.selectedModuleName = testModuleName;
    component.selectedModuleIcon = testIcon;
    component.selectedModuleMeta = testMeta;
    component.sidebarOpen = true;

    // Close sidebar
    component.closeSidebar();

    // Verify sidebar is closed
    expect(component.sidebarOpen).toBe(false);
    
    // Verify selection is preserved
    expect(component.selectedModuleSerialId).toBe(testSerialId);
    expect(component.selectedModuleName).toBe(testModuleName);
    expect(component.selectedModuleIcon).toBe(testIcon);
    expect(component.selectedModuleMeta).toEqual(testMeta);
  });

  it('should allow reopening sidebar without losing selection', () => {
    const component = createComponent();
    
    // Set up a selected module
    const testSerialId = 'SVR3QA0022';
    const testModuleName = 'MILL Station';
    
    component.selectedModuleSerialId = testSerialId;
    component.selectedModuleName = testModuleName;
    component.sidebarOpen = false;

    // Open sidebar
    component.openSidebarForSelected();

    // Verify sidebar is open
    expect(component.sidebarOpen).toBe(true);
    
    // Verify selection is still there
    expect(component.selectedModuleSerialId).toBe(testSerialId);
    expect(component.selectedModuleName).toBe(testModuleName);

    // Close sidebar again
    component.closeSidebar();

    // Verify sidebar is closed but selection remains
    expect(component.sidebarOpen).toBe(false);
    expect(component.selectedModuleSerialId).toBe(testSerialId);
    expect(component.selectedModuleName).toBe(testModuleName);
  });

  it('should preserve selection when sidebar is closed after double-click selection', () => {
    const component = createComponent();
    
    // Simulate module selection via double-click
    const testEvent = { id: 'SVR3QA0022', kind: 'module' as const };
    
    // Mock the layout config and module overview state
    (component as any).layoutConfig = {
      cells: [{
        id: 'SVR3QA0022',
        name: 'DRILL',
        serial_number: 'SVR3QA0022',
        position: { x: 100, y: 200 },
        size: { w: 50, h: 50 },
      }],
    };
    
    const moduleOverviewStateStub = {
      getSnapshot: jest.fn(() => ({
        modules: {
          'SVR3QA0022': {
            id: 'SVR3QA0022',
            subType: 'DRILL',
            connected: true,
            availability: 'READY',
            configured: true,
            lastUpdate: '2025-12-16T12:00:00.000Z',
          },
        },
      })),
    } as any;
    
    // Replace the moduleOverviewState with our stub
    (component as any).moduleOverviewState = moduleOverviewStateStub;
    (component as any).currentEnvironmentKey = 'mock';

    // Select module (this would normally be called by onModuleCellSelected)
    component.onModuleCellSelected(testEvent);
    
    // Verify module is selected
    expect(component.selectedModuleSerialId).toBe('SVR3QA0022');
    expect(component.selectedModuleName).toBeDefined();

    // Open sidebar (via double-click)
    component.openSidebarForSelected();
    expect(component.sidebarOpen).toBe(true);

    // Close sidebar
    component.closeSidebar();

    // Verify selection is preserved
    expect(component.sidebarOpen).toBe(false);
    expect(component.selectedModuleSerialId).toBe('SVR3QA0022');
    expect(component.selectedModuleName).toBeDefined();
    expect(component.selectedModuleIcon).toBeDefined();
    expect(component.selectedModuleMeta).toBeDefined();
  });

  it('should call markForCheck when closing sidebar', () => {
    const component = createComponent();
    const cdrStub = (component as any).cdr as ChangeDetectorRef;
    const markForCheckSpy = jest.spyOn(cdrStub, 'markForCheck');

    component.sidebarOpen = true;
    component.closeSidebar();

    expect(markForCheckSpy).toHaveBeenCalled();
  });
});

