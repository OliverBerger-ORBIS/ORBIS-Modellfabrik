"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const loadingBayCache_1 = require("./loadingBayCache");
describe('Test loading bay cache', () => {
    let underTest;
    beforeEach(() => {
        underTest = loadingBayCache_1.LoadingBayCache.getInstance();
    });
    afterEach(() => {
        underTest['loadingBayCache'].clear();
    });
    it('should return the correct loading bay', () => {
        const loadingBayMap = underTest.getLoadingBayForFTS('mocked');
        expect(loadingBayMap).toEqual({
            '1': undefined,
            '2': undefined,
            '3': undefined,
        });
    });
    it('should set the correct loading bay', () => {
        const serialNumber = 'mockedSerial';
        const loadPosition = '1';
        const orderId = 'mocked';
        underTest.setLoadingBay(serialNumber, loadPosition, orderId);
        const loadingBayMap = underTest.getLoadingBayForFTS(serialNumber);
        expect(loadingBayMap).toEqual({
            '1': orderId,
            '2': undefined,
            '3': undefined,
        });
    });
    it('should throw an error if the position is already occupied and load does not equal present load', () => {
        const loadPosition = '1';
        const orderId = 'mocked';
        const presentOrderId = 'presentId';
        underTest['loadingBayCache'].set('mocked', {
            '1': presentOrderId,
            '2': undefined,
            '3': undefined,
        });
        expect(() => underTest.setLoadingBay('mocked', loadPosition, orderId)).toThrow(loadingBayCache_1.LoadingBayOccupiedError);
    });
    it('should not throw an error if the position is already occupied but load equals present load', () => {
        const loadPosition = '1';
        const orderId = 'mocked';
        underTest['loadingBayCache'].set('mocked', {
            '1': orderId,
            '2': undefined,
            '3': undefined,
        });
        const serialNumber = 'mockedSerial';
        underTest.setLoadingBay(serialNumber, loadPosition, orderId);
        const loadingBayMap = underTest.getLoadingBayForFTS(serialNumber);
        expect(loadingBayMap).toEqual({
            '1': orderId,
            '2': undefined,
            '3': undefined,
        });
    });
    it('should clear the loading bay', () => {
        const serialNumber = 'mockedSerial';
        const orderId = 'mockedOrder';
        const orderIdToNotClear = 'orderNotToClear';
        underTest['loadingBayCache'].set(serialNumber, {
            '1': orderId,
            '2': orderIdToNotClear,
            '3': undefined,
        });
        underTest.clearLoadingBayForOrder(serialNumber, orderId);
        const loadingBayMap = underTest.getLoadingBayForFTS(serialNumber);
        expect(loadingBayMap).toEqual({
            '1': undefined,
            '2': orderIdToNotClear,
            '3': undefined,
        });
    });
    it('should reset the loading bay for a serial number', () => {
        const serialNumber = 'mockedSerial';
        underTest['loadingBayCache'].set(serialNumber, {
            '1': 'orderId1',
            '2': 'orderId2',
            '3': undefined,
        });
        underTest.resetLoadingBayForFts(serialNumber);
        expect(underTest['loadingBayCache'].get(serialNumber)).toEqual({
            '1': undefined,
            '2': undefined,
            '3': undefined,
        });
    });
});
