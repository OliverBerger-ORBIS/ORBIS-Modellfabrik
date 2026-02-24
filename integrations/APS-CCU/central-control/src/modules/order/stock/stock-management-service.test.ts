import { StockManagementService } from './stock-management-service';
import { LoadType } from '../../../../../common/protocol/vda';
import { FtsPairingStates } from '../../pairing/fts-pairing-states';

describe('Test stock management', () => {
  const AVAILABLE_HBW_SERIAL = 'hbwSerial';
  beforeEach(() => {
    StockManagementService.reset();
    StockManagementService.setWarehouses([AVAILABLE_HBW_SERIAL]);
  });

  it('should update the availability', () => {
    StockManagementService.setStock(AVAILABLE_HBW_SERIAL, []);

    expect(StockManagementService.stockAvailable('BLUE')).toBeFalsy();
    expect(StockManagementService.stockAvailable('RED')).toBeFalsy();
    expect(StockManagementService.stockAvailable('WHITE')).toBeFalsy();

    StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
      { loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' },
      { loadType: LoadType.RED, loadPosition: '2', loadId: '2' },
      { loadType: LoadType.WHITE, loadPosition: '3', loadId: '3' },
    ]);

    expect(StockManagementService.stockAvailable('BLUE')).toBeTruthy();
    expect(StockManagementService.stockAvailable('RED')).toBeTruthy();
    expect(StockManagementService.stockAvailable('WHITE')).toBeTruthy();

    StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' }]);

    expect(StockManagementService.stockAvailable('BLUE')).toBeTruthy();
    expect(StockManagementService.stockAvailable('RED')).toBeFalsy();
    expect(StockManagementService.stockAvailable('WHITE')).toBeFalsy();
  });

  it('should reserve a stock item if it is available', () => {
    StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
      { loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' },
      { loadType: LoadType.BLUE, loadPosition: '2', loadId: '2' },
      { loadType: LoadType.RED, loadPosition: '3', loadId: '3' },
    ]);

    expect(StockManagementService.reserveWorkpiece('orderId1', 'RED')).toBeTruthy();
    expect(StockManagementService.reserveWorkpiece('orderId2', 'BLUE')).toBeTruthy();
    expect(StockManagementService.reserveWorkpiece('orderId3', 'BLUE')).toBeTruthy();
  });

  it('should not reserve a stock item if it is unavailable', () => {
    StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
      { loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' },
      { loadType: LoadType.RED, loadPosition: '2', loadId: '2' },
    ]);

    expect(StockManagementService.reserveWorkpiece('orderId', 'WHITE')).toBeFalsy();

    expect(StockManagementService.reserveWorkpiece('orderId1', 'BLUE')).toBeTruthy();
    expect(StockManagementService.reserveWorkpiece('orderId2', 'BLUE')).toBeFalsy();
  });

  it('should remove a reservation', () => {
    StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
      { loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' },
      { loadType: LoadType.RED, loadPosition: '2', loadId: '2' },
    ]);

    expect(StockManagementService.reserveWorkpiece('orderId', 'BLUE')).toBeTruthy();
    expect(StockManagementService.stockAvailable('BLUE')).toBeFalsy();
    StockManagementService.removeReservation('orderId');
    expect(StockManagementService.stockAvailable('BLUE')).toBeTruthy();
  });

  it('should not remove a reservation for a different order', () => {
    StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
      { loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' },
      { loadType: LoadType.RED, loadPosition: '2', loadId: '2' },
    ]);

    expect(StockManagementService.reserveWorkpiece('orderId1', 'BLUE')).toBeTruthy();
    expect(StockManagementService.stockAvailable('BLUE')).toBeFalsy();
    StockManagementService.removeReservation('orderId_Missing');
    expect(StockManagementService.stockAvailable('BLUE')).toBeFalsy();
  });

  it('should check if an order has a reservation', () => {
    StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' }]);

    expect(StockManagementService.hasReservedWorkpiece('orderId')).toBeFalsy();
    expect(StockManagementService.reserveWorkpiece('orderId', 'BLUE')).toBeTruthy();
    expect(StockManagementService.hasReservedWorkpiece('orderId')).toBeTruthy();
  });

  it('should not show a reservation if another order has a reservation', () => {
    StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [{ loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' }]);

    expect(StockManagementService.hasReservedWorkpiece('orderId')).toBeFalsy();
    expect(StockManagementService.reserveWorkpiece('orderId1', 'BLUE')).toBeTruthy();
    expect(StockManagementService.hasReservedWorkpiece('orderId1')).toBeTruthy();
    expect(StockManagementService.hasReservedWorkpiece('orderId')).toBeFalsy();
  });

  it('should throw an error when trying to reserve two different workpieces for the same order', () => {
    StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
      { loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' },
      { loadType: LoadType.RED, loadPosition: '2', loadId: '2' },
    ]);

    expect(StockManagementService.reserveWorkpiece('orderId1', 'RED')).toBeTruthy();
    const errorTest = () => StockManagementService.reserveWorkpiece('orderId1', 'BLUE');
    expect(errorTest).toThrowError();
  });

  it('should make a reservation with a different warehouse, when there are multiple FTS', () => {
    FtsPairingStates.getInstance().getAll = jest.fn().mockReturnValue([1, 2, 3]);

    StockManagementService.setWarehouses(['hbw1', 'hbw2']);
    StockManagementService.setStock('hbw1', [
      { loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' },
      { loadType: LoadType.BLUE, loadPosition: '2', loadId: '2' },
    ]);
    StockManagementService.setStock('hbw2', [
      { loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' },
      { loadType: LoadType.BLUE, loadPosition: '2', loadId: '2' },
    ]);

    expect(StockManagementService.reserveWorkpiece('orderId1', 'BLUE')).toBe('hbw1');
    expect(StockManagementService.reserveWorkpiece('orderId2', 'BLUE')).toBe('hbw2');
  });

  it('should make a reservation with the same warehouse, when there is only one FTS', () => {
    FtsPairingStates.getInstance().getAll = jest.fn().mockReturnValue([1]);

    StockManagementService.setWarehouses(['hbw1', 'hbw2']);
    StockManagementService.setStock('hbw1', [
      { loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' },
      { loadType: LoadType.BLUE, loadPosition: '2', loadId: '2' },
    ]);
    StockManagementService.setStock('hbw2', [
      { loadType: LoadType.BLUE, loadPosition: '1', loadId: '1' },
      { loadType: LoadType.BLUE, loadPosition: '2', loadId: '2' },
    ]);

    expect(StockManagementService.reserveWorkpiece('orderId1', 'BLUE')).toBe('hbw1');
    expect(StockManagementService.reserveWorkpiece('orderId2', 'BLUE')).toBe('hbw1');
  });
});
