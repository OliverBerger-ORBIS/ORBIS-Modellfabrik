import { ModuleCommandType, ModuleType } from '../../../../../common/protocol/module';
import { OrderFlowService, ProductionDefinition } from './order-flow-service';
import * as crypt_spies from 'node:crypto';
import * as helpers_spies from '../../../helpers';
import { OrderState, ProductionFlows } from '../../../../../common/protocol/ccu';

let uuid_counter = 100000000000;
jest.mock('node:crypto');
describe('Test order flow parsing and definition generation', () => {
  beforeEach(() => {
    jest.spyOn(helpers_spies, 'writeJsonFile').mockResolvedValue();
    jest.spyOn(helpers_spies, 'readJsonFile').mockResolvedValue({});

    // mock uuids with sequential deterministic values
    jest.spyOn(crypt_spies, 'randomUUID').mockImplementation(() => {
      uuid_counter++;
      return `aabbccdd-eeee-ffff-1111-${uuid_counter}`;
    });
  });

  afterEach(() => {
    // no-explicit-any is needed here as the properties are private
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (OrderFlowService as any)['flows'] = {};
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (OrderFlowService as any)['filename'] = undefined;
    jest.restoreAllMocks();
    uuid_counter = 100000000000;
  });

  it('should convert a flow to an OrderDefinition', () => {
    const flow = { steps: [ModuleType.DRILL, ModuleType.AIQS] };

    const expectedDefinition = {
      navigationSteps: [
        {
          id: 'aabbccdd-eeee-ffff-1111-100000000001',
          source: 'START',
          state: 'ENQUEUED',
          target: 'HBW',
          type: 'NAVIGATION',
        },
        {
          dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000002',
          id: 'aabbccdd-eeee-ffff-1111-100000000003',
          source: 'HBW',
          state: 'ENQUEUED',
          target: 'DRILL',
          type: 'NAVIGATION',
        },
        {
          dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000006',
          id: 'aabbccdd-eeee-ffff-1111-100000000007',
          source: 'DRILL',
          state: 'ENQUEUED',
          target: 'AIQS',
          type: 'NAVIGATION',
        },
        {
          dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000010',
          id: 'aabbccdd-eeee-ffff-1111-100000000011',
          source: 'AIQS',
          state: 'ENQUEUED',
          target: 'DPS',
          type: 'NAVIGATION',
        },
      ],
      productionSteps: [
        {
          command: 'DROP',
          dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000001',
          id: 'aabbccdd-eeee-ffff-1111-100000000002',
          moduleType: 'HBW',
          state: 'ENQUEUED',
          type: 'MANUFACTURE',
        },
        {
          command: 'PICK',
          dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000003',
          id: 'aabbccdd-eeee-ffff-1111-100000000004',
          moduleType: 'DRILL',
          state: 'ENQUEUED',
          type: 'MANUFACTURE',
        },
        {
          command: 'DRILL',
          dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000004',
          id: 'aabbccdd-eeee-ffff-1111-100000000005',
          moduleType: 'DRILL',
          state: 'ENQUEUED',
          type: 'MANUFACTURE',
        },
        {
          command: 'DROP',
          dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000005',
          id: 'aabbccdd-eeee-ffff-1111-100000000006',
          moduleType: 'DRILL',
          state: 'ENQUEUED',
          type: 'MANUFACTURE',
        },
        {
          command: 'PICK',
          dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000007',
          id: 'aabbccdd-eeee-ffff-1111-100000000008',
          moduleType: 'AIQS',
          state: 'ENQUEUED',
          type: 'MANUFACTURE',
        },
        {
          command: 'CHECK_QUALITY',
          dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000008',
          id: 'aabbccdd-eeee-ffff-1111-100000000009',
          moduleType: 'AIQS',
          state: 'ENQUEUED',
          type: 'MANUFACTURE',
        },
        {
          command: 'DROP',
          dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000009',
          id: 'aabbccdd-eeee-ffff-1111-100000000010',
          moduleType: 'AIQS',
          state: 'ENQUEUED',
          type: 'MANUFACTURE',
        },
        {
          command: 'PICK',
          dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000011',
          id: 'aabbccdd-eeee-ffff-1111-100000000012',
          moduleType: 'DPS',
          state: 'ENQUEUED',
          type: 'MANUFACTURE',
        },
      ],
    };

    const definition = OrderFlowService.convertFlowToDefinition(flow);
    expect(definition).toEqual(expectedDefinition);
  });

  it('should create a valid storage order definition', () => {
    const expectedStorageOrder: ProductionDefinition = {
      navigationSteps: [
        {
          id: 'aabbccdd-eeee-ffff-1111-100000000001',
          source: ModuleType.START,
          state: OrderState.ENQUEUED,
          target: ModuleType.DPS,
          type: 'NAVIGATION',
        },
        {
          dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000002',
          id: 'aabbccdd-eeee-ffff-1111-100000000003',
          source: ModuleType.DPS,
          state: OrderState.ENQUEUED,
          target: ModuleType.HBW,
          type: 'NAVIGATION',
        },
      ],
      productionSteps: [
        {
          command: ModuleCommandType.DROP,
          dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000001',
          id: 'aabbccdd-eeee-ffff-1111-100000000002',
          moduleType: ModuleType.DPS,
          state: OrderState.ENQUEUED,
          type: 'MANUFACTURE',
        },
        {
          command: ModuleCommandType.PICK,
          dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000003',
          id: 'aabbccdd-eeee-ffff-1111-100000000004',
          moduleType: ModuleType.HBW,
          state: OrderState.ENQUEUED,
          type: 'MANUFACTURE',
        },
      ],
    };
    const definition = OrderFlowService.getStorageProductionDefinition();
    expect(definition).toEqual(expectedStorageOrder);
  });

  it('should use the dependentActionId for the first navigation action if given', () => {
    const flow = { steps: [ModuleType.DRILL, ModuleType.AIQS] };
    const dependentActionId = '123456-1234-1234-1234-1234678';

    const definition = OrderFlowService.convertFlowToDefinition(flow, dependentActionId);
    expect(definition).toHaveProperty('navigationSteps[0].dependentActionId', dependentActionId);
  });

  it('should reload a changed file', async () => {
    const flows: ProductionFlows = {
      RED: { steps: [ModuleType.AIQS] },
      WHITE: { steps: [ModuleType.DRILL] },
      BLUE: { steps: [ModuleType.DRILL, ModuleType.MILL] },
    };
    jest.spyOn(helpers_spies, 'readJsonFile').mockResolvedValue({});

    await OrderFlowService.initialize('/foo/test.json');
    expect(OrderFlowService.getFlows()).toEqual(OrderFlowService.getDefaultFlows());

    jest.spyOn(helpers_spies, 'readJsonFile').mockResolvedValue(flows);
    await OrderFlowService.reloadFlows();

    expect(helpers_spies.readJsonFile).toHaveBeenCalledWith('/foo/test.json');
    expect(OrderFlowService.getFlows()).toEqual(flows);
  });

  it('should allow setting the flows', () => {
    const flows: ProductionFlows = {
      RED: { steps: [ModuleType.AIQS] },
      WHITE: { steps: [ModuleType.DRILL] },
      BLUE: { steps: [ModuleType.DRILL, ModuleType.MILL] },
    };

    expect(OrderFlowService.getFlows()).toEqual({});
    OrderFlowService.setFlows(flows);
    expect(OrderFlowService.getFlows()).toEqual(flows);
  });

  it('should save the current flows', async () => {
    const flows: ProductionFlows = {
      RED: { steps: [ModuleType.AIQS] },
      WHITE: { steps: [ModuleType.DRILL] },
      BLUE: { steps: [ModuleType.DRILL, ModuleType.MILL] },
    };
    jest.spyOn(helpers_spies, 'writeJsonFile').mockResolvedValue();

    await OrderFlowService.initialize('/foo/test.json');
    OrderFlowService.setFlows(flows);

    await OrderFlowService.saveFlows();

    expect(helpers_spies.writeJsonFile).toHaveBeenCalledWith('/foo/test.json', flows);
  });
});
