"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const stock_management_service_1 = require("./stock-management-service");
const vda_1 = require("../../../../../common/protocol/vda");
const module_1 = require("../../../../../common/protocol/module");
const pairing_states_1 = require("../../pairing/pairing-states");
const protocol_1 = require("../../../../../common/protocol");
const ccu_1 = require("../../../../../common/protocol/ccu");
describe('Test empty storage bay management', () => {
    const AVAILABLE_HBW_SERIAL = 'hbwSerial';
    beforeEach(() => {
        stock_management_service_1.StockManagementService.reset();
        stock_management_service_1.StockManagementService.setWarehouses([AVAILABLE_HBW_SERIAL]);
    });
    afterEach(() => {
        jest.restoreAllMocks();
        jest.resetModules();
    });
    it('should update the availability', () => {
        stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, []);
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeFalsy();
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.RED)).toBeFalsy();
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.WHITE)).toBeFalsy();
        stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [
            { loadType: vda_1.LoadType.RED, setName: 'R', maxAmount: 3 },
            { loadType: vda_1.LoadType.WHITE, setName: 'W', maxAmount: 3 },
            { loadType: vda_1.LoadType.BLUE, setName: 'B', maxAmount: 3 },
        ]);
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.RED)).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.WHITE)).toBeTruthy();
        stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.BLUE, setName: 'B', maxAmount: 3 }]);
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.RED)).toBeFalsy();
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.WHITE)).toBeFalsy();
    });
    it('should update the availability with available Stock', () => {
        stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, []);
        stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [
            { loadType: vda_1.LoadType.RED, setName: 'R', maxAmount: 3 },
            { loadType: vda_1.LoadType.WHITE, setName: 'W', maxAmount: 3 },
            { loadType: vda_1.LoadType.BLUE, setName: 'B', maxAmount: 3 },
        ]);
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.RED)).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.WHITE)).toBeTruthy();
        stock_management_service_1.StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' },
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1.1', loadId: '1' },
            { loadType: vda_1.LoadType.RED, loadPosition: '2', loadId: '2' },
            { loadType: vda_1.LoadType.RED, loadPosition: '2.1', loadId: '2' },
            { loadType: vda_1.LoadType.RED, loadPosition: '2.2', loadId: '2' },
            { loadType: vda_1.LoadType.WHITE, loadPosition: '3', loadId: '3' },
            { loadType: vda_1.LoadType.WHITE, loadPosition: '3.1', loadId: '3' },
            { loadType: vda_1.LoadType.WHITE, loadPosition: '3.2', loadId: '3' },
        ]);
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.RED)).toBeFalsy();
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.WHITE)).toBeFalsy();
        stock_management_service_1.StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1', loadId: '1' },
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1.1', loadId: '1' },
            { loadType: vda_1.LoadType.BLUE, loadPosition: '1.2', loadId: '1' },
        ]);
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeFalsy();
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.RED)).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.WHITE)).toBeTruthy();
    });
    it('should reserve an empty bay if it is available', () => {
        stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [
            { loadType: vda_1.LoadType.RED, setName: 'R', maxAmount: 3 },
            { loadType: vda_1.LoadType.WHITE, setName: 'W', maxAmount: 3 },
            { loadType: vda_1.LoadType.BLUE, setName: 'B', maxAmount: 3 },
        ]);
        expect(stock_management_service_1.StockManagementService.reserveEmptyBay('orderId1', protocol_1.Workpiece.RED)).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.reserveEmptyBay('orderId2', protocol_1.Workpiece.BLUE)).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.reserveEmptyBay('orderId3', protocol_1.Workpiece.BLUE)).toBeTruthy();
    });
    it('should not reserve an empty bay if it is unavailable', () => {
        stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.BLUE, setName: 'B', maxAmount: 1 }]);
        expect(stock_management_service_1.StockManagementService.reserveEmptyBay('orderId', protocol_1.Workpiece.WHITE)).toBeFalsy();
        expect(stock_management_service_1.StockManagementService.reserveEmptyBay('orderId1', protocol_1.Workpiece.BLUE)).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.reserveEmptyBay('orderId2', protocol_1.Workpiece.BLUE)).toBeFalsy();
    });
    it('should remove a reservation', () => {
        stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.BLUE, setName: 'B', maxAmount: 1 }]);
        expect(stock_management_service_1.StockManagementService.reserveEmptyBay('orderId', protocol_1.Workpiece.BLUE)).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeFalsy();
        stock_management_service_1.StockManagementService.removeReservation('orderId');
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeTruthy();
    });
    it('should not remove a reservation for a different order', () => {
        stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.BLUE, setName: 'B', maxAmount: 1 }]);
        expect(stock_management_service_1.StockManagementService.reserveEmptyBay('orderId1', protocol_1.Workpiece.BLUE)).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeFalsy();
        stock_management_service_1.StockManagementService.removeReservation('orderId_Missing');
        expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeFalsy();
    });
    it('should check if an order has a reservation', () => {
        stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.BLUE, setName: 'B', maxAmount: 3 }]);
        expect(stock_management_service_1.StockManagementService.hasReservedEmptyBay('orderId')).toBeFalsy();
        expect(stock_management_service_1.StockManagementService.reserveEmptyBay('orderId', protocol_1.Workpiece.BLUE)).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.hasReservedEmptyBay('orderId')).toBeTruthy();
    });
    it('should not show a reservation if another order has a reservation', () => {
        stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.BLUE, setName: 'B', maxAmount: 3 }]);
        expect(stock_management_service_1.StockManagementService.hasReservedEmptyBay('orderId')).toBeFalsy();
        expect(stock_management_service_1.StockManagementService.reserveEmptyBay('orderId1', protocol_1.Workpiece.BLUE)).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.hasReservedEmptyBay('orderId1')).toBeTruthy();
        expect(stock_management_service_1.StockManagementService.hasReservedEmptyBay('orderId')).toBeFalsy();
    });
    it('should throw an error when trying to reserve two different bays for the same order', () => {
        stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [
            { loadType: vda_1.LoadType.BLUE, setName: 'B', maxAmount: 3 },
            { loadType: vda_1.LoadType.RED, setName: 'R', maxAmount: 2 },
        ]);
        expect(stock_management_service_1.StockManagementService.reserveEmptyBay('orderId1', protocol_1.Workpiece.RED)).toBeTruthy();
        const errorTest = () => stock_management_service_1.StockManagementService.reserveEmptyBay('orderId1', protocol_1.Workpiece.BLUE);
        expect(errorTest).toThrowError();
    });
    it('should update the storage bays for a storage module', () => {
        const hbwSerial = AVAILABLE_HBW_SERIAL;
        const loadSets = [
            { setName: 'R', loadType: vda_1.LoadType.RED, maxAmount: 3 },
            { setName: 'B', loadType: vda_1.LoadType.BLUE, maxAmount: 2 },
            { setName: 'W', loadType: vda_1.LoadType.WHITE, maxAmount: 1 },
        ];
        const hbwFacts = {
            headerId: 0,
            timestamp: new Date(),
            version: '1',
            manufacturer: 'Test',
            serialNumber: hbwSerial,
            typeSpecification: {
                seriesName: 'series',
                moduleClass: module_1.ModuleType.HBW,
            },
            protocolFeatures: {},
            loadSpecification: {
                loadSets: loadSets,
            },
        };
        const pairingStates = pairing_states_1.PairingStates.getInstance();
        jest.spyOn(pairingStates, 'get').mockReturnValue({
            serialNumber: hbwSerial,
            type: ccu_1.DeviceType.MODULE,
            connected: true,
            subType: module_1.ModuleType.HBW,
        });
        jest.spyOn(pairingStates, 'getFactsheet').mockReturnValue(hbwFacts);
        jest.spyOn(stock_management_service_1.StockManagementService, 'setBays').mockReturnValue();
        stock_management_service_1.StockManagementService.updateBaysFromModule(hbwSerial);
        expect(pairingStates.get).toHaveBeenCalledWith(hbwSerial);
        expect(pairingStates.getFactsheet).toHaveBeenCalledWith(hbwSerial);
        expect(stock_management_service_1.StockManagementService.setBays).toHaveBeenCalledWith(AVAILABLE_HBW_SERIAL, loadSets);
    });
    it('should not update the storage bays for a storage module with missing factsheet', () => {
        const hbwSerial = 'hbwserial';
        const pairingStates = pairing_states_1.PairingStates.getInstance();
        jest.spyOn(pairingStates, 'get').mockReturnValue({
            serialNumber: hbwSerial,
            type: ccu_1.DeviceType.MODULE,
            connected: true,
            subType: module_1.ModuleType.HBW,
        });
        jest.spyOn(pairingStates, 'getFactsheet').mockReturnValue(undefined);
        jest.spyOn(stock_management_service_1.StockManagementService, 'setBays').mockReturnValue();
        stock_management_service_1.StockManagementService.updateBaysFromModule(hbwSerial);
        expect(pairingStates.get).toHaveBeenCalledWith(hbwSerial);
        expect(pairingStates.getFactsheet).toHaveBeenCalledWith(hbwSerial);
        expect(stock_management_service_1.StockManagementService.setBays).not.toHaveBeenCalled();
    });
    it('should not update the storage bays for a non-storage module', () => {
        const modSerial = 'serialNumber';
        const pairingStates = pairing_states_1.PairingStates.getInstance();
        jest.spyOn(pairingStates, 'get').mockReturnValue({
            serialNumber: modSerial,
            type: ccu_1.DeviceType.MODULE,
            connected: true,
            subType: module_1.ModuleType.DRILL,
        });
        jest.spyOn(pairingStates, 'getFactsheet').mockReturnValue(undefined);
        jest.spyOn(stock_management_service_1.StockManagementService, 'setBays').mockReturnValue();
        stock_management_service_1.StockManagementService.updateBaysFromModule(modSerial);
        expect(pairingStates.get).toHaveBeenCalledWith(modSerial);
        expect(pairingStates.getFactsheet).not.toHaveBeenCalled();
        expect(stock_management_service_1.StockManagementService.setBays).not.toHaveBeenCalled();
    });
    describe('handle stock for multiple warehouses', () => {
        it('should update the availability with two HBWs', () => {
            const secondHbw = 'secondHbw';
            stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, []);
            stock_management_service_1.StockManagementService.setBays(secondHbw, []);
            stock_management_service_1.StockManagementService.setWarehouses([AVAILABLE_HBW_SERIAL, secondHbw]);
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeFalsy();
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.RED)).toBeFalsy();
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.WHITE)).toBeFalsy();
            stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [
                { loadType: vda_1.LoadType.RED, setName: 'R', maxAmount: 3 },
                { loadType: vda_1.LoadType.BLUE, setName: 'B', maxAmount: 3 },
            ]);
            stock_management_service_1.StockManagementService.setBays(secondHbw, [{ loadType: vda_1.LoadType.WHITE, setName: 'W', maxAmount: 3 }]);
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeTruthy();
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.RED)).toBeTruthy();
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.WHITE)).toBeTruthy();
            stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.BLUE, setName: 'B', maxAmount: 3 }]);
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeTruthy();
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.RED)).toBeFalsy();
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.WHITE)).toBeTruthy();
            stock_management_service_1.StockManagementService.setBays(secondHbw, []);
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeTruthy();
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.RED)).toBeFalsy();
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.WHITE)).toBeFalsy();
        });
        it('should only use available HBWs', () => {
            const secondHbw = 'secondHbw';
            stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, []);
            stock_management_service_1.StockManagementService.setBays(secondHbw, []);
            stock_management_service_1.StockManagementService.setBays(secondHbw, [{ loadType: vda_1.LoadType.WHITE, setName: 'W', maxAmount: 3 }]);
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.BLUE)).toBeFalsy();
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.RED)).toBeFalsy();
            expect(stock_management_service_1.StockManagementService.emptyBayAvailable(protocol_1.Workpiece.WHITE)).toBeFalsy();
        });
        it('should return the id of the chosen warehouse', () => {
            stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.WHITE, setName: 'W', maxAmount: 3 }]);
            stock_management_service_1.StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.WHITE, loadId: 'W', loadPosition: 'A2' }]);
            expect(stock_management_service_1.StockManagementService.reserveWorkpiece('orderId', protocol_1.Workpiece.WHITE)).toEqual(AVAILABLE_HBW_SERIAL);
        });
        it('should return the id of the chosen warehouse for empty bays', () => {
            stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.WHITE, setName: 'W', maxAmount: 3 }]);
            expect(stock_management_service_1.StockManagementService.reserveEmptyBay('orderId', protocol_1.Workpiece.WHITE)).toEqual(AVAILABLE_HBW_SERIAL);
        });
        it('should return the id of the warehosue assigned to a reservation for an empty bay', () => {
            stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.WHITE, setName: 'W', maxAmount: 3 }]);
            stock_management_service_1.StockManagementService.reserveEmptyBay('orderId', protocol_1.Workpiece.WHITE);
            expect(stock_management_service_1.StockManagementService.getReservedWarehouse('orderId')).toEqual(AVAILABLE_HBW_SERIAL);
        });
        it('should return the id of the warehosue assigned to a reservation', () => {
            stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.WHITE, setName: 'W', maxAmount: 3 }]);
            stock_management_service_1.StockManagementService.setStock(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.WHITE, loadId: 'W', loadPosition: 'A2' }]);
            stock_management_service_1.StockManagementService.reserveWorkpiece('orderId', protocol_1.Workpiece.WHITE);
            expect(stock_management_service_1.StockManagementService.getReservedWarehouse('orderId')).toEqual(AVAILABLE_HBW_SERIAL);
        });
        it('should return undefined if no reservation exists for the order', () => {
            stock_management_service_1.StockManagementService.setBays(AVAILABLE_HBW_SERIAL, [{ loadType: vda_1.LoadType.WHITE, setName: 'W', maxAmount: 3 }]);
            stock_management_service_1.StockManagementService.reserveWorkpiece('orderId2', protocol_1.Workpiece.WHITE);
            expect(stock_management_service_1.StockManagementService.getReservedWarehouse('orderId')).toBeUndefined();
        });
    });
});
