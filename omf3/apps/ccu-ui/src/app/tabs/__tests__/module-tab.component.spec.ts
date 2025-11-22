import { BehaviorSubject } from 'rxjs';
import type { ModuleOverviewState, ModuleOverviewStatus, TransportOverviewStatus } from '@omf3/entities';
import { ModuleTabComponent } from '../module-tab.component';
import type { EnvironmentService } from '../../services/environment.service';
import type { ModuleNameService } from '../../services/module-name.service';
import type { ConnectionService } from '../../services/connection.service';
import type { ModuleOverviewStateService } from '../../services/module-overview-state.service';

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

  const initSpy = jest
    .spyOn(ModuleTabComponent.prototype as any, 'initializeStreams')
    .mockImplementation(() => {});

  const component = new ModuleTabComponent(
    environmentStub,
    moduleNameServiceStub,
    connectionServiceStub,
    moduleOverviewStateStub
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

