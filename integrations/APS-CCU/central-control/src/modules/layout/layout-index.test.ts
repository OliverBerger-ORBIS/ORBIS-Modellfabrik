import handleMessage from './index';
import { FactoryLayout } from '../../../../common/protocol/ccu';
import { FactoryLayoutService } from './factory-layout-service';
import { OrderManagement } from '../order/management/order-management';
import * as gateayStockSpy from '../gateway/stock';
import * as cloudStockSpy from '../production/cloud-stock';

describe('Layout update handler tests', () => {
  beforeEach(() => {
    jest.spyOn(FactoryLayoutService, 'setLayout').mockReturnValue();
    jest.spyOn(FactoryLayoutService, 'saveLayout').mockResolvedValue();
    jest.spyOn(FactoryLayoutService, 'publishLayout').mockResolvedValue();
    jest.spyOn(gateayStockSpy, 'publishWarehouses').mockResolvedValue();
    jest.spyOn(cloudStockSpy, 'publishStock').mockResolvedValue();
    jest.spyOn(OrderManagement.getInstance(), 'resumeOrders').mockResolvedValue();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should save, and publish the layout and resume orders', async () => {
    const layout: FactoryLayout = {
      modules: [],
      roads: [],
      intersections: [],
    };

    await handleMessage(JSON.stringify(layout));
    expect(FactoryLayoutService.setLayout).toHaveBeenCalled();
    expect(FactoryLayoutService.saveLayout).toHaveBeenCalled();
    expect(FactoryLayoutService.publishLayout).toHaveBeenCalled();
    expect(gateayStockSpy.publishWarehouses).toHaveBeenCalled();
    expect(cloudStockSpy.publishStock).toHaveBeenCalled();
    expect(OrderManagement.getInstance().resumeOrders).toHaveBeenCalled();
  });
});
