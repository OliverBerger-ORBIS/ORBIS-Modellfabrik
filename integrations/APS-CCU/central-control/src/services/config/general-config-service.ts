import { CcuTopic } from '../../../../common/protocol';
import { GeneralConfig } from '../../../../common/protocol/ccu';
import { getMqttClient } from '../../mqtt/mqtt';
import { PersistenceService } from '../persistence-service';
import config from '../../config';

const DEFAULT_CONFIG: GeneralConfig = {
  productionDurations: {
    WHITE: 80,
    BLUE: 100,
    RED: 120,
  },
  productionSettings: {
    maxParallelOrders: 2,
  },
  ftsSettings: {
    chargeThresholdPercent: config.ftsCharge.startChargeAtOrBelowPercentage,
  },
};

export class GeneralConfigService extends PersistenceService {
  private static _config: GeneralConfig | undefined;
  public static get config(): GeneralConfig {
    return this._config || DEFAULT_CONFIG;
  }

  public static async initialize(storageLocation: string) {
    console.debug('Initialize the GeneralConfigService');
    this._config = (await this.init<GeneralConfig>(storageLocation)) || DEFAULT_CONFIG;
    // in case old config is loaded, we need to add the new properties
    this._config.productionDurations = this._config.productionDurations || DEFAULT_CONFIG.productionDurations;
    this._config.productionSettings = this._config.productionSettings || DEFAULT_CONFIG.productionSettings;
    this._config.ftsSettings = this._config.ftsSettings || DEFAULT_CONFIG.ftsSettings;
    console.debug('GeneralConfigService initialized');
  }

  public static async saveConfig(config: GeneralConfig) {
    if (config) {
      this._config = config;
      await this.persist(config);
      await this.publish();
    }
  }

  public static publish() {
    return getMqttClient().publish(CcuTopic.CONFIG, JSON.stringify(this.config), { qos: 1, retain: true });
  }
}
