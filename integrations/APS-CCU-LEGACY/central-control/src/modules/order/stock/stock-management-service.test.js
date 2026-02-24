"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const stock_management_service_1 = require("./stock-management-service");
const vda_1 = require("../../../../../common/protocol/vda");
const fts_pairing_states_1 = require("../../pairing/fts-pairing-states");
describe('Test stock management', () => {
    const AVAILABLE_HBW_SERIAL = 'hbwSerial';
    beforeEach(() => {
        stock_management_service_1.StockManagementService.reset();
        stock_management_service_1.StockManagementService.setWarehouses([AVAILABLE_HBW_SERIAL]);
    });
    it('should update the availability', () => {
        stock_management_service_1.StockManagementService.setStock(AVAILABLE_HBW_SERIAL, []);
        expect(stock_management_service_1.StockManagementService.stockAvailable('BLUE')).toBeFalsy();
        expect(stock_management_service_1.StockManagementService.stockAvailable('RED')).toBeFalsy();
        expect(stock_management_service_1.StockManagementService.stockAvailable('WHITE')).toBeFalsy();
        stock_management_service_1.StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' },
            { loadType: vda_1.LoadType.RED, loadPosition: '2', loadId: '2' },
            { loadType: vda_1.LoadType.WHITE, loadPosition: '3', loadId: '3' },
        ]);
        expect(stock_management_service_1.StockManagementService.stockAvailable('BLUE')).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.stockAvailable('RED')).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.stockAvailable('WHITE')).toBeTruthy();
        stock_management_service_1.StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' }]);
        expect(stock_management_service_1.StockManagementService.stockAvailable('BLUE')).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.stockAvailable('RED')).toBeFalsy();
        expect(stock_management_service_1.StockManagementService.stockAvailable('WHITE')).toBeFalsy();
    });
    it('should reserve a stock item if it is available', () => {
        stock_management_service_1.StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' },
            { loadType: vda_1.LoadType.BLUE, loadPosition: '2', loadId: '2' },
            { loadType: vda_1.LoadType.RED, loadPosition: '3', loadId: '3' },
        ]);
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId1', 'RED')).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId2', 'BLUE')).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId3', 'BLUE')).toBeTruthy();
    });
    it('should not reserve a stock item if it is unavailable', () => {
        stock_management_service_1.StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' },
            { loadType: vda_1.LoadType.RED, loadPosition: '2', loadId: '2' },
        ]);
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId', 'WHITE')).toBeFalsy();
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId1', 'BLUE')).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId2', 'BLUE')).toBeFalsy();
    });
    it('should remove a reservation', () => {
        stock_management_service_1.StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' },
            { loadType: vda_1.LoadType.RED, loadPosition: '2', loadId: '2' },
        ]);
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId', 'BLUE')).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.stockAvailable('BLUE')).toBeFalsy();
        stock_management_service_1.StockManagementService.removeReservation('orderId');
        expect(stock_management_service_1.StockManagementService.stockAvailable('BLUE')).toBeTruthy();
    });
    it('should not remove a reservation for a different order', () => {
        stock_management_service_1.StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' },
            { loadType: vda_1.LoadType.RED, loadPosition: '2', loadId: '2' },
        ]);
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId1', 'BLUE')).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.stockAvailable('BLUE')).toBeFalsy();
        stock_management_service_1.StockManagementService.removeReservation('orderId_Missing');
        expect(stock_management_service_1.StockManagementService.stockAvailable('BLUE')).toBeFalsy();
    });
    it('should check if an order has a reservation', () => {
        stock_management_service_1.StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' }]);
        expect(stock_management_service_1.StockManagementService.hasReservedWorkpiece('orderId')).toBeFalsy();
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId', 'BLUE')).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.hasReservedWorkpiece('orderId')).toBeTruthy();
    });
    it('should not show a reservation if another order has a reservation', () => {
        stock_management_service_1.StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' }]);
        expect(stock_management_service_1.StockManagementService.hasReservedWorkpiece('orderId')).toBeFalsy();
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId1', 'BLUE')).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.hasReservedWorkpiece('orderId1')).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.hasReservedWorkpiece('orderId')).toBeFalsy();
    });
    it('should throw an error when trying to reserve two different workpieces for the same order', () => {
        stock_management_service_1.StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' },
            { loadType: vda_1.LoadType.RED, loadPosition: '2', loadId: '2' },
        ]);
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId1', 'RED')).toBeTruthy();
        const errorTest = () => stock_management_service_1.StockManagementService.reserveWorkpiece('orderId1', 'BLUE');
        expect(errorTest).toThrowError();
    });
    it('should make a reservation with a different warehouse, when there are multiple FTS', () => {
        fts_pairing_states_1.FtsPairingStates.getInstance().getAll = jest.fn().mockReturnValue([1, 2, 3]);
        stock_management_service_1.StockManagementService.setWarehouses(['hbw1', 'hbw2']);
        stock_management_service_1.StockManagementService.setStock('hbw1', [
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' },
            { loadType: vda_1.LoadType.BLUE, loadPosition: '2', loadId: '2' },
        ]);
        stock_management_service_1.StockManagementService.setStock('hbw2', [
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' },
            { loadType: vda_1.LoadType.BLUE, loadPosition: '2', loadId: '2' },
        ]);
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId1', 'BLUE')).toBe('hbw1');
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId2', 'BLUE')).toBe('hbw2');
    });
    it('should make a reservation with the same warehouse, when there is only one FTS', () => {
        fts_pairing_states_1.FtsPairingStates.getInstance().getAll = jest.fn().mockReturnValue([1]);
        stock_management_service_1.StockManagementService.setWarehouses(['hbw1', 'hbw2']);
        stock_management_service_1.StockManagementService.setStock('hbw1', [
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' },
            { loadType: vda_1.LoadType.BLUE, loadPosition: '2', loadId: '2' },
        ]);
        stock_management_service_1.StockManagementService.setStock('hbw2', [
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' },
            { loadType: vda_1.LoadType.BLUE, loadPosition: '2', loadId: '2' },
        ]);
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId1', 'BLUE')).toBe('hbw1');
        expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId2', 'BLUE')).toBe('hbw1');
    });
});
