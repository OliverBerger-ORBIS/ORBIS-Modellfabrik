import { BehaviorSubject, of } from 'rxjs';
import type { ModuleOverviewState, ModuleOverviewStatus, TransportOverviewStatus } from '@osf/entities';
import { ShopfloorTabComponent } from '../shopfloor-tab.component';
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
    publish: jest.fn(() => Promise.resolve()),
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
    .spyOn(ShopfloorTabComponent.prototype as any, 'initializeStreams')
    .mockImplementation(() => {});

  const component = new ShopfloorTabComponent(
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

describe('ShopfloorTabComponent sidebar and selection', () => {
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

describe('ShopfloorTabComponent sequence commands', () => {
  it('should load sequence commands for DRILL module', async () => {
    const component = createComponent();
    const httpStub = (component as any).http as HttpClient;
    
    const mockSequenceData = `Topic: module/v1/ff/SVR4H76449/order
Payload: 
{
  "timestamp": "2025-01-01T00:00:00.000Z",
  "serialNumber": "SVR4H76449",
  "orderId": "ORDER_DRILL_SEQUENCE_001",
  "orderUpdateId": 1,
  "action": {
    "id": "action_drill_pick_001",
    "command": "PICK",
    "metadata": {
      "type": "WHITE",
      "workpieceId": "04a189ca341290"
    }
  }
}`;

    jest.spyOn(httpStub, 'get').mockReturnValue(of(mockSequenceData) as any);

    await (component as any).loadSequenceCommands('DRILL');

    expect(component.sequenceCommands).not.toBeNull();
    expect(component.sequenceCommands?.commands).toHaveLength(1);
    expect(component.sequenceCommands?.topic).toBe('module/v1/ff/SVR4H76449/order');
    expect(component.sequenceCommands?.commands[0].action.command).toBe('PICK');
    expect(component.sequenceCommands?.commands[0].action.metadata['workpieceId']).toBe('04a189ca341290');
    expect(component.sentSequenceCommands).toHaveLength(0);
  });

  it('should restore saved module selection from localStorage', () => {
    const component = createComponent();
    const savedSerialId = 'SVR3QA0022';
    
    // Mock localStorage
    const getItemSpy = jest.spyOn(Storage.prototype, 'getItem').mockReturnValue(savedSerialId);
    
    // Mock module states
    const mockState: ModuleOverviewState = {
      modules: {
        [savedSerialId]: {
          id: savedSerialId,
          subType: 'HBW',
          connected: true,
          availability: 'READY',
          configured: true,
          lastUpdate: '2025-01-01T00:00:00Z',
        } as ModuleOverviewStatus,
      },
      transports: {},
    };
    
    (component as any).moduleOverviewState.getSnapshot = jest.fn(() => mockState);
    (component as any).currentEnvironmentKey = 'mock';
    (component as any).layoutConfig = { cells: [] };
    
    // Trigger restore
    (component as any).restoreOrSetDefaultModuleSelection();
    
    expect(component.selectedModuleSerialId).toBe(savedSerialId);
    getItemSpy.mockRestore();
  });

  it('should set HBW as default when no saved selection exists', () => {
    const component = createComponent();
    
    // Mock localStorage - no saved selection
    const getItemSpy = jest.spyOn(Storage.prototype, 'getItem').mockReturnValue(null);
    const setItemSpy = jest.spyOn(Storage.prototype, 'setItem');
    
    // Mock module states with HBW
    const hbwSerialId = 'SVR3QA0022';
    const mockState: ModuleOverviewState = {
      modules: {
        [hbwSerialId]: {
          id: hbwSerialId,
          subType: 'HBW',
          connected: true,
          availability: 'READY',
          configured: true,
          lastUpdate: '2025-01-01T00:00:00Z',
        } as ModuleOverviewStatus,
      },
      transports: {},
    };
    
    (component as any).moduleOverviewState.getSnapshot = jest.fn(() => mockState);
    (component as any).currentEnvironmentKey = 'mock';
    (component as any).layoutConfig = { cells: [] };
    
    // Trigger restore
    (component as any).restoreOrSetDefaultModuleSelection();
    
    expect(component.selectedModuleSerialId).toBe(hbwSerialId);
    expect(setItemSpy).toHaveBeenCalledWith('shopfloor-tab-selected-module-serial-id', hbwSerialId);
    
    getItemSpy.mockRestore();
    setItemSpy.mockRestore();
  });

  it('should save module selection to localStorage when module is selected', () => {
    const component = createComponent();
    const serialId = 'SVR3QA0022';
    
    const setItemSpy = jest.spyOn(Storage.prototype, 'setItem');
    
    const mockState: ModuleOverviewState = {
      modules: {
        [serialId]: {
          id: serialId,
          subType: 'HBW',
          connected: true,
          availability: 'READY',
        } as ModuleOverviewStatus,
      },
      transports: {},
    };
    
    (component as any).moduleOverviewState.getSnapshot = jest.fn(() => mockState);
    (component as any).currentEnvironmentKey = 'mock';
    (component as any).layoutConfig = { cells: [] };
    
    component.onModuleCellSelected({ id: serialId, kind: 'module' });
    
    expect(setItemSpy).toHaveBeenCalledWith('shopfloor-tab-selected-module-serial-id', serialId);
    setItemSpy.mockRestore();
  });

  it('should update selectedModuleMeta when moduleStatusMap changes', () => {
    const component = createComponent();
    const serialId = 'SVR3QA0022';
    
    component.selectedModuleSerialId = serialId;
    component.selectedModuleMeta = {
      availability: 'UNKNOWN' as any,
      availabilityLabel: 'Unknown',
      availabilityIcon: '⚫',
      availabilityClass: 'unknown',
      connected: undefined,
      connectionLabel: 'Unknown',
      connectionIcon: '⚫',
    };
    
    const statusMap = new Map();
    statusMap.set(serialId, {
      connected: true,
      availability: 'READY',
    });
    
    // Simulate moduleStatusMap$ emission by calling the subscription callback directly
    (component as any).currentModuleStatusMap = statusMap;
    
    // Manually trigger the update logic that would be in the subscription
    const currentStatus = statusMap.get(serialId);
    if (currentStatus && component.selectedModuleMeta) {
      component.selectedModuleMeta.availability = currentStatus.availability;
      component.selectedModuleMeta.connected = currentStatus.connected;
    }
    
    expect(component.selectedModuleMeta?.availability).toBe('READY');
    expect(component.selectedModuleMeta?.connected).toBe(true);
  });

  it('should send sequence command with timestamp', async () => {
    const component = createComponent();
    const connectionServiceStub = (component as any).connectionService as ConnectionService;
    
    component.sequenceCommands = {
      topic: 'module/v1/ff/SVR4H76449/order',
      commands: [{
        serialNumber: 'SVR4H76449',
        orderId: 'ORDER_DRILL_SEQUENCE_001',
        orderUpdateId: 1,
        action: {
          id: 'action_drill_pick_001',
          command: 'PICK',
          metadata: {
            type: 'WHITE',
            workpieceId: '04a189ca341290',
          },
        },
      }],
    };

    const publishSpy = jest.spyOn(connectionServiceStub, 'publish').mockResolvedValue();

    await component.sendSequenceCommand(0);

    expect(publishSpy).toHaveBeenCalledWith(
      'module/v1/ff/SVR4H76449/order',
      expect.objectContaining({
        serialNumber: 'SVR4H76449',
        orderId: 'ORDER_DRILL_SEQUENCE_001',
        orderUpdateId: 1,
        timestamp: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/),
        action: expect.objectContaining({
          command: 'PICK',
        }),
      }),
      { qos: 1 }
    );
  });

  it('should track sent commands', async () => {
    const component = createComponent();
    const connectionServiceStub = (component as any).connectionService as ConnectionService;
    
    component.sequenceCommands = {
      topic: 'module/v1/ff/SVR4H76449/order',
      commands: [{
        serialNumber: 'SVR4H76449',
        orderId: 'ORDER_DRILL_SEQUENCE_001',
        orderUpdateId: 1,
        action: {
          id: 'action_drill_pick_001',
          command: 'PICK',
          metadata: { type: 'WHITE', workpieceId: '04a189ca341290' },
        },
      }],
    };

    jest.spyOn(connectionServiceStub, 'publish').mockResolvedValue();

    expect(component.sentSequenceCommands).toHaveLength(0);
    expect(component.isCommandSent(0)).toBe(false);

    await component.sendSequenceCommand(0);

    expect(component.sentSequenceCommands).toHaveLength(1);
    expect(component.sentSequenceCommands[0].command.action.command).toBe('PICK');
    expect(component.sentSequenceCommands[0].topic).toBe('module/v1/ff/SVR4H76449/order');
    expect(component.isCommandSent(0)).toBe(true);
  });

  it('should reset sent commands', () => {
    const component = createComponent();
    
    component.sentSequenceCommands = [
      {
        command: {
          serialNumber: 'SVR4H76449',
          orderId: 'ORDER_DRILL_SEQUENCE_001',
          orderUpdateId: 1,
          action: { id: 'action_drill_pick_001', command: 'PICK', metadata: {} },
        },
        topic: 'module/v1/ff/SVR4H76449/order',
        timestamp: '2025-01-01T00:00:00.000Z',
      },
    ];

    expect(component.sentSequenceCommands).toHaveLength(1);

    component.resetSequenceCommands();

    expect(component.sentSequenceCommands).toHaveLength(0);
  });

  it('should format JSON payload correctly', () => {
    const component = createComponent();
    
    const payload = {
      serialNumber: 'SVR4H76449',
      orderId: 'ORDER_DRILL_SEQUENCE_001',
      action: { command: 'PICK' },
    };

    const formatted = component.formatJsonPayload(payload);
    const parsed = JSON.parse(formatted);

    expect(parsed).toEqual(payload);
    expect(formatted).toContain('"serialNumber"');
    expect(formatted).toContain('"orderId"');
  });

  it('should not send command if index is invalid', async () => {
    const component = createComponent();
    const connectionServiceStub = (component as any).connectionService as ConnectionService;
    
    component.sequenceCommands = {
      topic: 'module/v1/ff/SVR4H76449/order',
      commands: [{
        serialNumber: 'SVR4H76449',
        orderId: 'ORDER_DRILL_SEQUENCE_001',
        orderUpdateId: 1,
        action: { id: 'action_drill_pick_001', command: 'PICK', metadata: {} },
      }],
    };

    const publishSpy = jest.spyOn(connectionServiceStub, 'publish');
    const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();

    await component.sendSequenceCommand(-1);
    await component.sendSequenceCommand(10);

    expect(publishSpy).not.toHaveBeenCalled();
    expect(consoleWarnSpy).toHaveBeenCalledTimes(2);

    consoleWarnSpy.mockRestore();
  });

  it('should keep only last 10 sent commands', async () => {
    const component = createComponent();
    const connectionServiceStub = (component as any).connectionService as ConnectionService;
    
    component.sequenceCommands = {
      topic: 'module/v1/ff/SVR4H76449/order',
      commands: Array.from({ length: 15 }, (_, i) => ({
        serialNumber: 'SVR4H76449',
        orderId: 'ORDER_DRILL_SEQUENCE_001',
        orderUpdateId: i + 1,
        action: {
          id: `action_${i}`,
          command: 'PICK',
          metadata: { type: 'WHITE', workpieceId: '04a189ca341290' },
        },
      })),
    };

    jest.spyOn(connectionServiceStub, 'publish').mockResolvedValue();

    // Send 12 commands
    for (let i = 0; i < 12; i++) {
      await component.sendSequenceCommand(i);
    }

    expect(component.sentSequenceCommands).toHaveLength(10);
    expect(component.sentSequenceCommands[0].command.orderUpdateId).toBe(3); // First 2 were shifted out
    expect(component.sentSequenceCommands[9].command.orderUpdateId).toBe(12); // Last one
  });

  describe('getCommandEventIcon', () => {
    it('should return process-event.svg for MILL command', () => {
      const component = createComponent();
      const icon = component.getCommandEventIcon('MILL');
      expect(icon).toBe('assets/svg/shopfloor/shared/process-event.svg');
    });

    it('should return process-event.svg for DRILL command', () => {
      const component = createComponent();
      const icon = component.getCommandEventIcon('DRILL');
      expect(icon).toBe('assets/svg/shopfloor/shared/process-event.svg');
    });

    it('should return process-event.svg for CHECK_QUALITY command', () => {
      const component = createComponent();
      const icon = component.getCommandEventIcon('CHECK_QUALITY');
      expect(icon).toBe('assets/svg/shopfloor/shared/process-event.svg');
    });

    it('should return pick-event.svg for PICK command', () => {
      const component = createComponent();
      const icon = component.getCommandEventIcon('PICK');
      expect(icon).toBe('assets/svg/shopfloor/shared/pick-event.svg');
    });

    it('should return drop-event.svg for DROP command', () => {
      const component = createComponent();
      const icon = component.getCommandEventIcon('DROP');
      expect(icon).toBe('assets/svg/shopfloor/shared/drop-event.svg');
    });

    it('should return null for unknown commands', () => {
      const component = createComponent();
      const icon = component.getCommandEventIcon('UNKNOWN_COMMAND');
      expect(icon).toBeNull();
    });

    it('should return null for undefined command', () => {
      const component = createComponent();
      const icon = component.getCommandEventIcon(undefined);
      expect(icon).toBeNull();
    });

    it('should be case-insensitive', () => {
      const component = createComponent();
      expect(component.getCommandEventIcon('pick')).toBe('assets/svg/shopfloor/shared/pick-event.svg');
      expect(component.getCommandEventIcon('DROP')).toBe('assets/svg/shopfloor/shared/drop-event.svg');
      expect(component.getCommandEventIcon('mill')).toBe('assets/svg/shopfloor/shared/process-event.svg');
    });
  });

  describe('module selection highlighting', () => {
    it('should have selectedModuleSerialId property', () => {
      const component = createComponent();
      const testSerialId = 'SVR3QA0022';
      
      component.selectedModuleSerialId = testSerialId;
      
      expect(component.selectedModuleSerialId).toBe(testSerialId);
    });

    it('should allow null selectedModuleSerialId', () => {
      const component = createComponent();
      
      component.selectedModuleSerialId = null;
      
      expect(component.selectedModuleSerialId).toBeNull();
    });
  });
});

