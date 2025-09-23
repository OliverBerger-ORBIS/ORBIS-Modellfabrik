"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.VersionPlausibilityService = void 0;
const ccu_1 = require("../../../../common/protocol/ccu");
const mqtt_1 = require("../../mqtt/mqtt");
const protocol_1 = require("../../../../common/protocol");
const persistence_service_1 = require("../../services/persistence-service");
const helpers_1 = require("../../helpers");
const semver_1 = require("semver");
const SUFFIX_24V_TXT = '+24V+TXT';
const SUFFIX_24V = '+24V';
class VersionPlausibilityService extends persistence_service_1.PersistenceService {
    static async initialize(storageLocation) {
        const list = await this.init(storageLocation);
        if (list instanceof Object) {
            this.allowedVersionsBySeriesName = list;
        }
        this.checkedModuleVersionsBySerial.clear();
        this.checkedModuleVersionsBySerial.clear();
        await this.sendMismatchedModules();
    }
    static async sendMismatchedModules() {
        // Send the mismatched modules to the UI
        // build a mqtt json message with the timestamp and the mismatched modules. The mismatched modules should contain the serial number, the device type, the module type, the series name, the version and the allowed version
        const message = {
            timestamp: new Date(),
            ccuVersion: (0, helpers_1.getPackageVersion)(),
            mismatchedModules: [...this.mismatchedModules.values()],
        };
        // publish the message
        await (0, mqtt_1.getMqttClient)().publish(protocol_1.CcuTopic.VERSION_MISMATCH, JSON.stringify(message), { qos: 2, retain: true });
    }
    static getUniqueKey(serial, series) {
        return `${serial}-${series}`;
    }
    static isInvalidVersion(version, range) {
        return !(0, semver_1.satisfies)(version, range, { includePrerelease: true, loose: false });
    }
    static async registerModuleVersion(facts, is24VTXT = false) {
        const serial = facts.serialNumber;
        const series = this.fixupSeriesName(facts.typeSpecification.seriesName, is24VTXT);
        const uniqueKey = this.getUniqueKey(serial, series);
        console.debug('Checking module version', facts.serialNumber, series, facts.version);
        const version = facts.version;
        const allowed = this.allowedVersionsBySeriesName[series];
        let updated = false;
        // The format of the module version is one of the following:
        // "MOD-FF22+" + ModuleType + "+24V"
        // "MOD-FF22+" + ModuleType
        // "MOD-FF22+" + ModuleType + "+24V+TXT"
        // "FTS-FF22+"
        if (VersionPlausibilityService.isInvalidVersion(version, allowed)) {
            // The device type is determined by the agvClass field in the factsheet. If it is not set, it is a module
            const deviceType = facts.typeSpecification.agvClass ? ccu_1.DeviceType.FTS : ccu_1.DeviceType.MODULE;
            const is24V = facts.typeSpecification.seriesName.indexOf(SUFFIX_24V) >= 0;
            const moduleClass = this.fixupModuleClass(facts.typeSpecification.moduleClass, is24VTXT);
            const mismatchedModule = {
                serialNumber: serial,
                deviceType,
                moduleType: moduleClass,
                seriesName: series,
                seriesUnknown: !this.allowedVersionsBySeriesName.hasOwnProperty(series),
                version: facts.version,
                requiredVersion: allowed,
                isTXT: is24VTXT || !is24V,
                is24V: is24VTXT || is24V,
            };
            this.mismatchedModules.set(uniqueKey, mismatchedModule);
            if (this.checkedModuleVersionsBySerial.get(uniqueKey) !== version) {
                console.debug('Mismatched module version', serial, series, version, allowed);
                this.checkedModuleVersionsBySerial.set(uniqueKey, version);
                updated = true;
            }
        }
        else {
            if (this.checkedModuleVersionsBySerial.has(uniqueKey)) {
                this.mismatchedModules.delete(uniqueKey);
                this.checkedModuleVersionsBySerial.delete(uniqueKey);
                updated = true;
            }
        }
        if (updated) {
            // There is a change to the mismatched versions, push the new state to the UI
            await this.sendMismatchedModules();
        }
    }
    /**
     * Reset the mismatched modules cache for testing purposes
     */
    static resetMismatchedModulesCache() {
        this.mismatchedModules.clear();
        this.checkedModuleVersionsBySerial.clear();
    }
}
exports.VersionPlausibilityService = VersionPlausibilityService;
VersionPlausibilityService.allowedVersionsBySeriesName = {};
VersionPlausibilityService.checkedModuleVersionsBySerial = new Map();
VersionPlausibilityService.mismatchedModules = new Map();
VersionPlausibilityService.fixupSeriesName = (series, is24VTXT = false) => {
    if (is24VTXT) {
        if (!series.endsWith(SUFFIX_24V_TXT)) {
            // fix the series if necessary to match the 24V+TXT series, the received name might end with 24V or the model only. Handle both cases
            if (series.endsWith(SUFFIX_24V)) {
                return series.substring(0, series.length - SUFFIX_24V.length) + SUFFIX_24V_TXT;
            }
            else {
                return series + SUFFIX_24V_TXT;
            }
        }
    }
    return series;
};
VersionPlausibilityService.fixupModuleClass = (moduleClass, is24VTXT = false) => {
    if (!moduleClass) {
        return undefined;
    }
    if (is24VTXT && moduleClass.endsWith('24')) {
        // fix the moduleClass if necessary to match the standard module Class, remove trailing 24
        return moduleClass.substring(0, moduleClass.length - 2);
    }
    return moduleClass;
};
