import { GeneralConfigService } from './general-config-service';
import config from '../../config';

describe('General Config Service', () => {
  it('should initialize with ftsSettings', async () => {
    const initSpy = jest.spyOn(GeneralConfigService, 'init').mockResolvedValue(undefined);
    await GeneralConfigService.initialize('global_config');
    expect(initSpy).toHaveBeenCalledWith('global_config');
    expect(GeneralConfigService.config).toHaveProperty(
      'ftsSettings.chargeThresholdPercent',
      config.ftsCharge.startChargeAtOrBelowPercentage,
    );
  });

  it('should initialize an old config with ftsSettings', async () => {
    const initSpy = jest.spyOn(GeneralConfigService, 'init').mockResolvedValue({
      productionDurations: {
        WHITE: 10,
        BLUE: 12,
        RED: 123,
      },
    });
    await GeneralConfigService.initialize('global_config');
    expect(initSpy).toHaveBeenCalledWith('global_config');
    expect(GeneralConfigService.config).toHaveProperty('productionDurations.WHITE', 10);
    expect(GeneralConfigService.config).toHaveProperty('productionDurations.BLUE', 12);
    expect(GeneralConfigService.config).toHaveProperty('productionDurations.RED', 123);
    expect(GeneralConfigService.config).toHaveProperty(
      'ftsSettings.chargeThresholdPercent',
      config.ftsCharge.startChargeAtOrBelowPercentage,
    );
  });

  it('should load a config with ftsSettings', async () => {
    const initSpy = jest.spyOn(GeneralConfigService, 'init').mockResolvedValue({
      productionDurations: {
        WHITE: 10,
        BLUE: 12,
        RED: 123,
      },
      ftsSettings: {
        chargeThresholdPercent: 9,
      },
    });
    await GeneralConfigService.initialize('global_config');
    expect(initSpy).toHaveBeenCalledWith('global_config');
    expect(GeneralConfigService.config).toHaveProperty('productionDurations');
    expect(GeneralConfigService.config).toHaveProperty('ftsSettings.chargeThresholdPercent', 9);
  });
});
