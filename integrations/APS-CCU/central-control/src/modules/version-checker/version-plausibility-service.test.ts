import { VersionPlausibilityService } from './version-plausibility-service';
import { Factsheet } from '../../../../common/protocol/vda';
import * as mqttMock from '../../mqtt/mqtt';
import * as helpersMock from '../../helpers';
import { ModuleType } from '../../../../common/protocol/module';

/* eslint-disable @typescript-eslint/no-explicit-any */
describe('VersionPlausibilityService', () => {
  let factsheet: Factsheet;
  let uniqueKey: string;

  beforeEach(() => {
    jest.spyOn(mqttMock, 'getMqttClient').mockReturnValue({
      publish: jest.fn(),
    } as any);
    VersionPlausibilityService.resetMismatchedModulesCache();
    factsheet = {
      serialNumber: 'serial',
      version: '1.0.0',
      typeSpecification: {
        seriesName: 'MOD-FF22+ModuleType',
        moduleClass: 'ModuleType' as ModuleType,
      },
    } as Factsheet;
    uniqueKey = VersionPlausibilityService.getUniqueKey(factsheet.serialNumber, factsheet.typeSpecification.seriesName);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('matches valid and invalid version correctly', async () => {
    expect(VersionPlausibilityService.isInvalidVersion('1.0.0', '1.0.*')).toBe(false);
    expect(VersionPlausibilityService.isInvalidVersion('1.1.0', '1.1.*')).toBe(false);
    expect(VersionPlausibilityService.isInvalidVersion('1.1.7', '1.1.*')).toBe(false);

    // invalid versions
    expect(VersionPlausibilityService.isInvalidVersion('1.0.0', '2.0.*')).toBe(true);
    expect(VersionPlausibilityService.isInvalidVersion('2.0.0', '1.0.*')).toBe(true);
    expect(VersionPlausibilityService.isInvalidVersion('1.1.0', '1.0.*')).toBe(true);
    expect(VersionPlausibilityService.isInvalidVersion('1.1.0', '1.2.*')).toBe(true);

    // check prerelease versions
    expect(VersionPlausibilityService.isInvalidVersion('1.1.7-1', '1.1.7-1')).toBe(false);
    expect(VersionPlausibilityService.isInvalidVersion('1.1.7-1', '1.1.*')).toBe(false);
    expect(VersionPlausibilityService.isInvalidVersion('1.2.0-1', '1.2.*')).toBe(false);
    expect(VersionPlausibilityService.isInvalidVersion('1.1.7-1', '1.1.7')).toBe(true);
    expect(VersionPlausibilityService.isInvalidVersion('1.1.7-1', '1.1.7-2')).toBe(true);
    expect(VersionPlausibilityService.isInvalidVersion('1.1.7-2', '1.1.7-1')).toBe(true);

    // verify build metadata is ignored
    expect(VersionPlausibilityService.isInvalidVersion('1.1.7+git123', '1.1.7+git123')).toBe(false);
    expect(VersionPlausibilityService.isInvalidVersion('1.1.7+git123', '1.1.7+git111')).toBe(false);
    expect(VersionPlausibilityService.isInvalidVersion('1.1.7+git123', '1.1.*')).toBe(false);
    expect(VersionPlausibilityService.isInvalidVersion('1.1.7+git123', '1.2.*')).toBe(true);
  });

  it('registers module version correctly when version matches allowed version', async () => {
    jest.spyOn(helpersMock, 'readJsonFile').mockResolvedValue({ 'MOD-FF22+ModuleType': '1.0.0' });
    await VersionPlausibilityService.initialize('dummy');

    await VersionPlausibilityService.registerModuleVersion(factsheet);

    expect((VersionPlausibilityService as any).mismatchedModules.size).toBe(0);
  });

  it('registers module version correctly when version does not match allowed version', async () => {
    jest.spyOn(helpersMock, 'readJsonFile').mockResolvedValue({ 'MOD-FF22+ModuleType': '2.0.0' });
    await VersionPlausibilityService.initialize('dummy');

    await VersionPlausibilityService.registerModuleVersion(factsheet);

    expect((VersionPlausibilityService as any).mismatchedModules.size).toBe(1);
    expect((VersionPlausibilityService as any).mismatchedModules.get(uniqueKey).version).toBe('1.0.0');
    expect((VersionPlausibilityService as any).mismatchedModules.get(uniqueKey).requiredVersion).toBe('2.0.0');
  });

  it('registers module version correctly when version does not match allowed version for series ending with +24V', async () => {
    factsheet.typeSpecification.seriesName = 'MOD-FF22+ModuleType+24V';
    uniqueKey = VersionPlausibilityService.getUniqueKey(factsheet.serialNumber, factsheet.typeSpecification.seriesName);
    jest.spyOn(helpersMock, 'readJsonFile').mockResolvedValue({ 'MOD-FF22+ModuleType+24V': '2.0.0' });
    await VersionPlausibilityService.initialize('dummy');

    await VersionPlausibilityService.registerModuleVersion(factsheet);

    expect((VersionPlausibilityService as any).mismatchedModules.size).toBe(1);
    expect((VersionPlausibilityService as any).mismatchedModules.get(uniqueKey).version).toBe('1.0.0');
    expect((VersionPlausibilityService as any).mismatchedModules.get(uniqueKey).requiredVersion).toBe('2.0.0');
  });

  it('registers module version correctly when series name ends with +24V, but should be +24V+TXT', async () => {
    factsheet.typeSpecification.seriesName = 'MOD-FF22+ModuleType+24V';
    uniqueKey = VersionPlausibilityService.getUniqueKey(factsheet.serialNumber, 'MOD-FF22+ModuleType+24V+TXT');
    jest.spyOn(helpersMock, 'readJsonFile').mockResolvedValue({ 'MOD-FF22+ModuleType+24V+TXT': '2.0.0' });
    await VersionPlausibilityService.initialize('dummy');

    await VersionPlausibilityService.registerModuleVersion(factsheet, true);

    expect((VersionPlausibilityService as any).mismatchedModules.size).toBe(1);
    expect((VersionPlausibilityService as any).mismatchedModules.get(uniqueKey).version).toBe('1.0.0');
    expect((VersionPlausibilityService as any).mismatchedModules.get(uniqueKey).requiredVersion).toBe('2.0.0');
  });

  it('registers module version correctly when moduleClass ends with 24 and it is a 24V module', async () => {
    factsheet.typeSpecification.moduleClass = 'ModuleType24' as ModuleType;
    factsheet.typeSpecification.seriesName = 'MOD-FF22+ModuleType+24V';
    uniqueKey = VersionPlausibilityService.getUniqueKey(factsheet.serialNumber, 'MOD-FF22+ModuleType+24V+TXT');
    jest.spyOn(helpersMock, 'readJsonFile').mockResolvedValue({ 'MOD-FF22+ModuleType+24V+TXT': '2.0.0' });
    await VersionPlausibilityService.initialize('dummy');

    await VersionPlausibilityService.registerModuleVersion(factsheet, true);

    expect((VersionPlausibilityService as any).mismatchedModules.size).toBe(1);
    expect((VersionPlausibilityService as any).mismatchedModules.get(uniqueKey).version).toBe('1.0.0');
    expect((VersionPlausibilityService as any).mismatchedModules.get(uniqueKey).requiredVersion).toBe('2.0.0');
    expect((VersionPlausibilityService as any).mismatchedModules.get(uniqueKey).moduleType).toBe('ModuleType');
  });

  it('resets mismatched modules cache correctly', async () => {
    jest.spyOn(helpersMock, 'readJsonFile').mockResolvedValue({ 'MOD-FF22+ModuleType': '2.0.0' });
    await VersionPlausibilityService.initialize('dummy');

    await VersionPlausibilityService.registerModuleVersion(factsheet);
    await VersionPlausibilityService.resetMismatchedModulesCache();

    expect((VersionPlausibilityService as any).mismatchedModules.size).toBe(0);
  });
});
