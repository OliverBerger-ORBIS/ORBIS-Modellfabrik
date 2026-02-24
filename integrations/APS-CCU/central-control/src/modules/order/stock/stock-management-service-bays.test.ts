import { StockManagementService } from './stock-management-service';
import { Factsheet, LoadType } from '../../../../../common/protocol/vda';
import { ModuleType } from '../../../../../common/protocol/module';
import { PairingStates } from '../../pairing/pairing-states';
import { Workpiece } from '../../../../../common/protocol';
import { DeviceType } from '../../../../../common/protocol/ccu';

describe('Test empty storage bay management', () => {
  const AVAILABLE_HBW_SERIAL = 'hbwSerial';

  beforeEach(() => {
    StockManagementService.reset();
    StockManagementService.setWarehouses([AVAILABLE_HBW_SERIAL]);
  });
  afterEach(() => {
    jest.restoreAllMocks();
    jest.resetModules();
  });

  it('should update the availability', () => {
    StockManagementService.setBays(AVAILABLE_HBW_SERIAL, []);

    expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeFalsy();
    expect(StockManagementService.emptyBayAvailable(Workpiece.RED)).toBeFalsy();
    expect(StockManagementService.emptyBayAvailable(Workpiece.WHITE)).toBeFalsy();

    StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [
      { loadType: LoadType.RED, setName: 'R', maxAmount: 3 },
      { loadType: LoadType.WHITE, setName: 'W', maxAmount: 3 },
      { loadType: LoadType.BLUE, setName: 'B', maxAmount: 3 },
    ]);

    expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeTruthy();
    expect(StockManagementService.emptyBayAvailable(Workpiece.RED)).toBeTruthy();
    expect(StockManagementService.emptyBayAvailable(Workpiece.WHITE)).toBeTruthy();

    StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.BLUE, setName: 'B', maxAmount: 3 }]);

    expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeTruthy();
    expect(StockManagementService.emptyBayAvailable(Workpiece.RED)).toBeFalsy();
    expect(StockManagementService.emptyBayAvailable(Workpiece.WHITE)).toBeFalsy();
  });

  it('should update the availability with available Stock', () => {
    StockManagementService.setBays(AVAILABLE_HBW_SERIAL, []);

    StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [
      { loadType: LoadType.RED, setName: 'R', maxAmount: 3 },
      { loadType: LoadType.WHITE, setName: 'W', maxAmount: 3 },
      { loadType: LoadType.BLUE, setName: 'B', maxAmount: 3 },
    ]);

    expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeTruthy();
    expect(StockManagementService.emptyBayAvailable(Workpiece.RED)).toBeTruthy();
    expect(StockManagementService.emptyBayAvailable(Workpiece.WHITE)).toBeTruthy();

    StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
      { loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' },
      { loadType: LoadType.BLUE, loadPosition: '1.1', loadId: '1' },
      { loadType: LoadType.RED, loadPosition: '2', loadId: '2' },
      { loadType: LoadType.RED, loadPosition: '2.1', loadId: '2' },
      { loadType: LoadType.RED, loadPosition: '2.2', loadId: '2' },
      { loadType: LoadType.WHITE, loadPosition: '3', loadId: '3' },
      { loadType: LoadType.WHITE, loadPosition: '3.1', loadId: '3' },
      { loadType: LoadType.WHITE, loadPosition: '3.2', loadId: '3' },
    ]);

    expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeTruthy();
    expect(StockManagementService.emptyBayAvailable(Workpiece.RED)).toBeFalsy();
    expect(StockManagementService.emptyBayAvailable(Workpiece.WHITE)).toBeFalsy();

    StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
      { loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' },
      { loadType: LoadType.BLUE, loadPosition: '1.1', loadId: '1' },
      { loadType: LoadType.BLUE, loadPosition: '1.2', loadId: '1' },
    ]);

    expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeFalsy();
    expect(StockManagementService.emptyBayAvailable(Workpiece.RED)).toBeTruthy();
    expect(StockManagementService.emptyBayAvailable(Workpiece.WHITE)).toBeTruthy();
  });

  it('should reserve an empty bay if it is available', () => {
    StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [
      { loadType: LoadType.RED, setName: 'R', maxAmount: 3 },
      { loadType: LoadType.WHITE, setName: 'W', maxAmount: 3 },
      { loadType: LoadType.BLUE, setName: 'B', maxAmount: 3 },
    ]);

    expect(StockManagementService.reserveEmptyBay('orderId1', Workpiece.RED)).toBeTruthy();
    expect(StockManagementService.reserveEmptyBay('orderId2', Workpiece.BLUE)).toBeTruthy();
    expect(StockManagementService.reserveEmptyBay('orderId3', Workpiece.BLUE)).toBeTruthy();
  });

  it('should not reserve an empty bay if it is unavailable', () => {
    StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.BLUE, setName: 'B', maxAmount: 1 }]);

    expect(StockManagementService.reserveEmptyBay('orderId', Workpiece.WHITE)).toBeFalsy();

    expect(StockManagementService.reserveEmptyBay('orderId1', Workpiece.BLUE)).toBeTruthy();
    expect(StockManagementService.reserveEmptyBay('orderId2', Workpiece.BLUE)).toBeFalsy();
  });

  it('should remove a reservation', () => {
    StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.BLUE, setName: 'B', maxAmount: 1 }]);

    expect(StockManagementService.reserveEmptyBay('orderId', Workpiece.BLUE)).toBeTruthy();
    expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeFalsy();
    StockManagementService.removeReservation('orderId');
    expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeTruthy();
  });

  it('should not remove a reservation for a different order', () => {
    StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.BLUE, setName: 'B', maxAmount: 1 }]);

    expect(StockManagementService.reserveEmptyBay('orderId1', Workpiece.BLUE)).toBeTruthy();
    expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeFalsy();
    StockManagementService.removeReservation('orderId_Missing');
    expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeFalsy();
  });

  it('should check if an order has a reservation', () => {
    StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.BLUE, setName: 'B', maxAmount: 3 }]);

    expect(StockManagementService.hasReservedEmptyBay('orderId')).toBeFalsy();
    expect(StockManagementService.reserveEmptyBay('orderId', Workpiece.BLUE)).toBeTruthy();
    expect(StockManagementService.hasReservedEmptyBay('orderId')).toBeTruthy();
  });

  it('should not show a reservation if another order has a reservation', () => {
    StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.BLUE, setName: 'B', maxAmount: 3 }]);

    expect(StockManagementService.hasReservedEmptyBay('orderId')).toBeFalsy();
    expect(StockManagementService.reserveEmptyBay('orderId1', Workpiece.BLUE)).toBeTruthy();
    expect(StockManagementService.hasReservedEmptyBay('orderId1')).toBeTruthy();
    expect(StockManagementService.hasReservedEmptyBay('orderId')).toBeFalsy();
  });

  it('should throw an error when trying to reserve two different bays for the same order', () => {
    StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [
      { loadType: LoadType.BLUE, setName: 'B', maxAmount: 3 },
      { loadType: LoadType.RED, setName: 'R', maxAmount: 2 },
    ]);

    expect(StockManagementService.reserveEmptyBay('orderId1', Workpiece.RED)).toBeTruthy();
    const errorTest = () => StockManagementService.reserveEmptyBay('orderId1', Workpiece.BLUE);
    expect(errorTest).toThrowError();
  });

  it('should update the storage bays for a storage module', () => {
    const hbwSerial = AVAILABLE_HBW_SERIAL;
    const loadSets = [
      { setName: 'R', loadType: LoadType.RED, maxAmount: 3 },
      { setName: 'B', loadType: LoadType.BLUE, maxAmount: 2 },
      { setName: 'W', loadType: LoadType.WHITE, maxAmount: 1 },
    ];
    const hbwFacts: Factsheet = {
      headerId: 0,
      timestamp: new Date(),
      version: '1',
      manufacturer: 'Test',
      serialNumber: hbwSerial,
      typeSpecification: {
        seriesName: 'series',
        moduleClass: ModuleType.HBW,
      },
      protocolFeatures: {},
      loadSpecification: {
        loadSets: loadSets,
      },
    };
    const pairingStates = PairingStates.getInstance();
    jest.spyOn(pairingStates, 'get').mockReturnValue({
      serialNumber: hbwSerial,
      type: DeviceType.MODULE,
      connected: true,
      subType: ModuleType.HBW,
    });
    jest.spyOn(pairingStates, 'getFactsheet').mockReturnValue(hbwFacts);
    jest.spyOn(StockManagementService, 'setBays').mockReturnValue();

    StockManagementService.updateBaysFromModule(hbwSerial);

    expect(pairingStates.get).toHaveBeenCalledWith(hbwSerial);
    expect(pairingStates.getFactsheet).toHaveBeenCalledWith(hbwSerial);
    expect(StockManagementService.setBays).toHaveBeenCalledWith(AVAILABLE_HBW_SERIAL, loadSets);
  });

  it('should not update the storage bays for a storage module with missing factsheet', () => {
    const hbwSerial = 'hbwserial';
    const pairingStates = PairingStates.getInstance();
    jest.spyOn(pairingStates, 'get').mockReturnValue({
      serialNumber: hbwSerial,
      type: DeviceType.MODULE,
      connected: true,
      subType: ModuleType.HBW,
    });
    jest.spyOn(pairingStates, 'getFactsheet').mockReturnValue(undefined);
    jest.spyOn(StockManagementService, 'setBays').mockReturnValue();

    StockManagementService.updateBaysFromModule(hbwSerial);

    expect(pairingStates.get).toHaveBeenCalledWith(hbwSerial);
    expect(pairingStates.getFactsheet).toHaveBeenCalledWith(hbwSerial);
    expect(StockManagementService.setBays).not.toHaveBeenCalled();
  });

  it('should not update the storage bays for a non-storage module', () => {
    const modSerial = 'serialNumber';
    const pairingStates = PairingStates.getInstance();
    jest.spyOn(pairingStates, 'get').mockReturnValue({
      serialNumber: modSerial,
      type: DeviceType.MODULE,
      connected: true,
      subType: ModuleType.DRILL,
    });
    jest.spyOn(pairingStates, 'getFactsheet').mockReturnValue(undefined);
    jest.spyOn(StockManagementService, 'setBays').mockReturnValue();

    StockManagementService.updateBaysFromModule(modSerial);

    expect(pairingStates.get).toHaveBeenCalledWith(modSerial);
    expect(pairingStates.getFactsheet).not.toHaveBeenCalled();
    expect(StockManagementService.setBays).not.toHaveBeenCalled();
  });

  describe('handle stock for multiple warehouses', () => {
    it('should update the availability with two HBWs', () => {
      const secondHbw = 'secondHbw';
      StockManagementService.setBays(AVAILABLE_HBW_SERIAL, []);
      StockManagementService.setBays(secondHbw, []);
      StockManagementService.setWarehouses([AVAILABLE_HBW_SERIAL, secondHbw]);

      expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeFalsy();
      expect(StockManagementService.emptyBayAvailable(Workpiece.RED)).toBeFalsy();
      expect(StockManagementService.emptyBayAvailable(Workpiece.WHITE)).toBeFalsy();

      StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [
        { loadType: LoadType.RED, setName: 'R', maxAmount: 3 },
        { loadType: LoadType.BLUE, setName: 'B', maxAmount: 3 },
      ]);
      StockManagementService.setBays(secondHbw, [{ loadType: LoadType.WHITE, setName: 'W', maxAmount: 3 }]);

      expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeTruthy();
      expect(StockManagementService.emptyBayAvailable(Workpiece.RED)).toBeTruthy();
      expect(StockManagementService.emptyBayAvailable(Workpiece.WHITE)).toBeTruthy();

      StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.BLUE, setName: 'B', maxAmount: 3 }]);

      expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeTruthy();
      expect(StockManagementService.emptyBayAvailable(Workpiece.RED)).toBeFalsy();
      expect(StockManagementService.emptyBayAvailable(Workpiece.WHITE)).toBeTruthy();

      StockManagementService.setBays(secondHbw, []);

      expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeTruthy();
      expect(StockManagementService.emptyBayAvailable(Workpiece.RED)).toBeFalsy();
      expect(StockManagementService.emptyBayAvailable(Workpiece.WHITE)).toBeFalsy();
    });

    it('should only use available HBWs', () => {
      const secondHbw = 'secondHbw';
      StockManagementService.setBays(AVAILABLE_HBW_SERIAL, []);
      StockManagementService.setBays(secondHbw, []);

      StockManagementService.setBays(secondHbw, [{ loadType: LoadType.WHITE, setName: 'W', maxAmount: 3 }]);

      expect(StockManagementService.emptyBayAvailable(Workpiece.BLUE)).toBeFalsy();
      expect(StockManagementService.emptyBayAvailable(Workpiece.RED)).toBeFalsy();
      expect(StockManagementService.emptyBayAvailable(Workpiece.WHITE)).toBeFalsy();
    });

    it('should return the id of the chosen warehouse', () => {
      StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.WHITE, setName: 'W', maxAmount: 3 }]);
      StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.WHITE, loadId: 'W', loadPosition: 'A2' }]);
      expect(StockManagementService.reserveWorkpiece('orderId', Workpiece.WHITE)).toEqual(AVAILABLE_HBW_SERIAL);
    });

    it('should return the id of the chosen warehouse for empty bays', () => {
      StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.WHITE, setName: 'W', maxAmount: 3 }]);
      expect(StockManagementService.reserveEmptyBay('orderId', Workpiece.WHITE)).toEqual(AVAILABLE_HBW_SERIAL);
    });

    it('should return the id of the warehosue assigned to a reservation for an empty bay', () => {
      StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.WHITE, setName: 'W', maxAmount: 3 }]);
      StockManagementService.reserveEmptyBay('orderId', Workpiece.WHITE);
      expect(StockManagementService.getReservedWarehouse('orderId')).toEqual(AVAILABLE_HBW_SERIAL);
    });

    it('should return the id of the warehosue assigned to a reservation', () => {
      StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.WHITE, setName: 'W', maxAmount: 3 }]);
      StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.WHITE, loadId: 'W', loadPosition: 'A2' }]);
      StockManagementService.reserveWorkpiece('orderId', Workpiece.WHITE);
      expect(StockManagementService.getReservedWarehouse('orderId')).toEqual(AVAILABLE_HBW_SERIAL);
    });

    it('should return undefined if no reservation exists for the order', () => {
      StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.WHITE, setName: 'W', maxAmount: 3 }]);
      StockManagementService.reserveWorkpiece('orderId2', Workpiece.WHITE);
      expect(StockManagementService.getReservedWarehouse('orderId')).toBeUndefined();
    });
  });
});
