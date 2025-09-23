"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const index_1 = __importDefault(require("./index"));
const factory_layout_service_1 = require("./factory-layout-service");
const order_management_1 = require("../order/management/order-management");
const gateayStockSpy = __importStar(require("../gateway/stock"));
const cloudStockSpy = __importStar(require("../production/cloud-stock"));
describe('Layout update handler tests', () => {
    beforeEach(() => {
        jest.spyOn(factory_layout_service_1.FactoryLayoutService, 'setLayout').mockReturnValue();
        jest.spyOn(factory_layout_service_1.FactoryLayoutService, 'saveLayout').mockResolvedValue();
        jest.spyOn(factory_layout_service_1.FactoryLayoutService, 'publishLayout').mockResolvedValue();
        jest.spyOn(gateayStockSpy, 'publishWarehouses').mockResolvedValue();
        jest.spyOn(cloudStockSpy, 'publishStock').mockResolvedValue();
        jest.spyOn(order_management_1.OrderManagement.getInstance(), 'resumeOrders').mockResolvedValue();
    });
    afterEach(() => {
        jest.restoreAllMocks();
    });
    it('should save, and publish the layout and resume orders', async () => {
        const layout = {
            modules: [],
            roads: [],
            intersections: [],
        };
        await (0, index_1.default)(JSON.stringify(layout));
        expect(factory_layout_service_1.FactoryLayoutService.setLayout).toHaveBeenCalled();
        expect(factory_layout_service_1.FactoryLayoutService.saveLayout).toHaveBeenCalled();
        expect(factory_layout_service_1.FactoryLayoutService.publishLayout).toHaveBeenCalled();
        expect(gateayStockSpy.publishWarehouses).toHaveBeenCalled();
        expect(cloudStockSpy.publishStock).toHaveBeenCalled();
        expect(order_management_1.OrderManagement.getInstance().resumeOrders).toHaveBeenCalled();
    });
});
