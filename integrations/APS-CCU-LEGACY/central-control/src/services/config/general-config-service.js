"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.GeneralConfigService = void 0;
const protocol_1 = require("../../../../common/protocol");
const mqtt_1 = require("../../mqtt/mqtt");
const persistence_service_1 = require("../persistence-service");
const config_1 = __importDefault(require("../../config"));
const DEFAULT_CONFIG = {
    productionDurations: {
        WHITE: 80,
        BLUE: 100,
        RED: 120,
    },
    productionSettings: {
        maxParallelOrders: 2,
    },
    ftsSettings: {
        chargeThresholdPercent: config_1.default.ftsCharge.startChargeAtOrBelowPercentage,
    },
};
class GeneralConfigService extends persistence_service_1.PersistenceService {
    static get config() {
        return this._config || DEFAULT_CONFIG;
    }
    static async initialize(storageLocation) {
        console.debug('Initialize the GeneralConfigService');
        this._config = (await this.init(storageLocation)) || DEFAULT_CONFIG;
        // in case old config is loaded, we need to add the new properties
        this._config.productionDurations = this._config.productionDurations || DEFAULT_CONFIG.productionDurations;
        this._config.productionSettings = this._config.productionSettings || DEFAULT_CONFIG.productionSettings;
        this._config.ftsSettings = this._config.ftsSettings || DEFAULT_CONFIG.ftsSettings;
        console.debug('GeneralConfigService initialized');
    }
    static async saveConfig(config) {
        if (config) {
            this._config = config;
            await this.persist(config);
            await this.publish();
        }
    }
    static publish() {
        return (0, mqtt_1.getMqttClient)().publish(protocol_1.CcuTopic.CONFIG, JSON.stringify(this.config), { qos: 1, retain: true });
    }
}
exports.GeneralConfigService = GeneralConfigService;
