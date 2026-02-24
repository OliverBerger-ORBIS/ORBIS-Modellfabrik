import { Factsheet } from '../../../../common/protocol/vda';
import { DeviceType, MismatchedModule, MismatchedVersionMessage } from '../../../../common/protocol/ccu';
import { getMqttClient } from '../../mqtt/mqtt';
import { CcuTopic } from '../../../../common/protocol';
import { PersistenceService } from '../../services/persistence-service';
import { getPackageVersion } from '../../helpers';
import { ModuleType } from '../../../../common/protocol/module';
import { satisfies as versionSatisfies } from 'semver';

const SUFFIX_24V_TXT = '+24V+TXT';
const SUFFIX_24V = '+24V';

interface SeriesVersionsList {
  [seriesName: string]: string;
}

export class VersionPlausibilityService extends PersistenceService {
  private static allowedVersionsBySeriesName: SeriesVersionsList = {};
  private static readonly checkedModuleVersionsBySerial = new Map<string, string>();
  private static readonly mismatchedModules = new Map<string, MismatchedModule>();

  static async initialize(storageLocation: string) {
    const list = await this.init<SeriesVersionsList>(storageLocation);
    if (list instanceof Object) {
      this.allowedVersionsBySeriesName = list;
    }
    this.checkedModuleVersionsBySerial.clear();
    this.checkedModuleVersionsBySerial.clear();
    await this.sendMismatchedModules();
  }

  private static fixupSeriesName = (series: string, is24VTXT = false): string => {
    if (is24VTXT) {
      if (!series.endsWith(SUFFIX_24V_TXT)) {
        // fix the series if necessary to match the 24V+TXT series, the received name might end with 24V or the model only. Handle both cases
        if (series.endsWith(SUFFIX_24V)) {
          return series.substring(0, series.length - SUFFIX_24V.length) + SUFFIX_24V_TXT;
        } else {
          return series + SUFFIX_24V_TXT;
        }
      }
    }
    return series;
  };

  private static fixupModuleClass = (moduleClass?: ModuleType, is24VTXT = false): ModuleType | undefined => {
    if (!moduleClass) {
      return undefined;
    }
    if (is24VTXT && moduleClass.endsWith('24')) {
      // fix the moduleClass if necessary to match the standard module Class, remove trailing 24
      return moduleClass.substring(0, moduleClass.length - 2) as ModuleType;
    }
    return moduleClass;
  };

  static async sendMismatchedModules() {
    // Send the mismatched modules to the UI
    // build a mqtt json message with the timestamp and the mismatched modules. The mismatched modules should contain the serial number, the device type, the module type, the series name, the version and the allowed version
    const message: MismatchedVersionMessage = {
      timestamp: new Date(),
      ccuVersion: getPackageVersion(),
      mismatchedModules: [...this.mismatchedModules.values()],
    };
    // publish the message
    await getMqttClient().publish(CcuTopic.VERSION_MISMATCH, JSON.stringify(message), { qos: 2, retain: true });
  }

  static getUniqueKey(serial: string, series: string): string {
    return `${serial}-${series}`;
  }

  static isInvalidVersion(version: string, range: string): boolean {
    return !versionSatisfies(version, range, { includePrerelease: true, loose: false });
  }

  static async registerModuleVersion(facts: Factsheet, is24VTXT = false) {
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
      const deviceType = facts.typeSpecification.agvClass ? DeviceType.FTS : DeviceType.MODULE;
      const is24V = facts.typeSpecification.seriesName.indexOf(SUFFIX_24V) >= 0;
      const moduleClass = this.fixupModuleClass(facts.typeSpecification.moduleClass, is24VTXT);
      const mismatchedModule: MismatchedModule = {
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
    } else {
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
