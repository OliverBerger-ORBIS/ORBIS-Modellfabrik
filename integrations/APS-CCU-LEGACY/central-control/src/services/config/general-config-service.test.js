"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const general_config_service_1 = require("./general-config-service");
const config_1 = __importDefault(require("../../config"));
describe('General Config Service', () => {
    it('should initialize with ftsSettings', async () => {
        const initSpy = jest.spyOn(general_config_service_1.GeneralConfigService, 'init').mockResolvedValue(undefined);
        await general_config_service_1.GeneralConfigService.initialize('global_config');
        expect(initSpy).toHaveBeenCalledWith('global_config');
        expect(general_config_service_1.GeneralConfigService.config).toHaveProperty('ftsSettings.chargeThresholdPercent', config_1.default.ftsCharge.startChargeAtOrBelowPercentage);
    });
    it('should initialize an old config with ftsSettings', async () => {
        const initSpy = jest.spyOn(general_config_service_1.GeneralConfigService, 'init').mockResolvedValue({
            productionDurations: {
                WHITE: 10,
                BLUE: 12,
                RED: 123,
            },
        });
        await general_config_service_1.GeneralConfigService.initialize('global_config');
        expect(initSpy).toHaveBeenCalledWith('global_config');
        expect(general_config_service_1.GeneralConfigService.config).toHaveProperty('productionDurations.WHITE', 10);
        expect(general_config_service_1.GeneralConfigService.config).toHaveProperty('productionDurations.BLUE', 12);
        expect(general_config_service_1.GeneralConfigService.config).toHaveProperty('productionDurations.RED', 123);
        expect(general_config_service_1.GeneralConfigService.config).toHaveProperty('ftsSettings.chargeThresholdPercent', config_1.default.ftsCharge.startChargeAtOrBelowPercentage);
    });
    it('should load a config with ftsSettings', async () => {
        const initSpy = jest.spyOn(general_config_service_1.GeneralConfigService, 'init').mockResolvedValue({
            productionDurations: {
                WHITE: 10,
                BLUE: 12,
                RED: 123,
            },
            ftsSettings: {
                chargeThresholdPercent: 9,
            },
        });
        await general_config_service_1.GeneralConfigService.initialize('global_config');
        expect(initSpy).toHaveBeenCalledWith('global_config');
        expect(general_config_service_1.GeneralConfigService.config).toHaveProperty('productionDurations');
        expect(general_config_service_1.GeneralConfigService.config).toHaveProperty('ftsSettings.chargeThresholdPercent', 9);
    });
});
