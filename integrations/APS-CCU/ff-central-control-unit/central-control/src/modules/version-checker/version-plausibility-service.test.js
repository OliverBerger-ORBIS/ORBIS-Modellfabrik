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
Object.defineProperty(exports, "__esModule", { value: true });
const version_plausibility_service_1 = require("./version-plausibility-service");
const mqttMock = __importStar(require("../../mqtt/mqtt"));
const helpersMock = __importStar(require("../../helpers"));
/* eslint-disable @typescript-eslint/no-explicit-any */
describe('VersionPlausibilityService', () => {
    let factsheet;
    let uniqueKey;
    beforeEach(() => {
        jest.spyOn(mqttMock, 'getMqttClient').mockReturnValue({
            publish: jest.fn(),
        });
        version_plausibility_service_1.VersionPlausibilityService.resetMismatchedModulesCache();
        factsheet = {
            serialNumber: 'serial',
            version: '1.0.0',
            typeSpecification: {
                seriesName: 'MOD-FF22+ModuleType',
                moduleClass: 'ModuleType',
            },
        };
        uniqueKey = version_plausibility_service_1.VersionPlausibilityService.getUniqueKey(factsheet.serialNumber, factsheet.typeSpecification.seriesName);
    });
    afterEach(() => {
        jest.restoreAllMocks();
    });
    it('matches valid and invalid version correctly', async () => {
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.0.0', '1.0.*')).toBe(false);
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.1.0', '1.1.*')).toBe(false);
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.1.7', '1.1.*')).toBe(false);
        // invalid versions
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.0.0', '2.0.*')).toBe(true);
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('2.0.0', '1.0.*')).toBe(true);
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.1.0', '1.0.*')).toBe(true);
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.1.0', '1.2.*')).toBe(true);
        // check prerelease versions
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.1.7-1', '1.1.7-1')).toBe(false);
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.1.7-1', '1.1.*')).toBe(false);
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.2.0-1', '1.2.*')).toBe(false);
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.1.7-1', '1.1.7')).toBe(true);
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.1.7-1', '1.1.7-2')).toBe(true);
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.1.7-2', '1.1.7-1')).toBe(true);
        // verify build metadata is ignored
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.1.7+git123', '1.1.7+git123')).toBe(false);
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.1.7+git123', '1.1.7+git111')).toBe(false);
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.1.7+git123', '1.1.*')).toBe(false);
        expect(version_plausibility_service_1.VersionPlausibilityService.isInvalidVersion('1.1.7+git123', '1.2.*')).toBe(true);
    });
    it('registers module version correctly when version matches allowed version', async () => {
        jest.spyOn(helpersMock, 'readJsonFile').mockResolvedValue({ 'MOD-FF22+ModuleType': '1.0.0' });
        await version_plausibility_service_1.VersionPlausibilityService.initialize('dummy');
        await version_plausibility_service_1.VersionPlausibilityService.registerModuleVersion(factsheet);
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.size).toBe(0);
    });
    it('registers module version correctly when version does not match allowed version', async () => {
        jest.spyOn(helpersMock, 'readJsonFile').mockResolvedValue({ 'MOD-FF22+ModuleType': '2.0.0' });
        await version_plausibility_service_1.VersionPlausibilityService.initialize('dummy');
        await version_plausibility_service_1.VersionPlausibilityService.registerModuleVersion(factsheet);
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.size).toBe(1);
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.get(uniqueKey).version).toBe('1.0.0');
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.get(uniqueKey).requiredVersion).toBe('2.0.0');
    });
    it('registers module version correctly when version does not match allowed version for series ending with +24V', async () => {
        factsheet.typeSpecification.seriesName = 'MOD-FF22+ModuleType+24V';
        uniqueKey = version_plausibility_service_1.VersionPlausibilityService.getUniqueKey(factsheet.serialNumber, factsheet.typeSpecification.seriesName);
        jest.spyOn(helpersMock, 'readJsonFile').mockResolvedValue({ 'MOD-FF22+ModuleType+24V': '2.0.0' });
        await version_plausibility_service_1.VersionPlausibilityService.initialize('dummy');
        await version_plausibility_service_1.VersionPlausibilityService.registerModuleVersion(factsheet);
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.size).toBe(1);
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.get(uniqueKey).version).toBe('1.0.0');
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.get(uniqueKey).requiredVersion).toBe('2.0.0');
    });
    it('registers module version correctly when series name ends with +24V, but should be +24V+TXT', async () => {
        factsheet.typeSpecification.seriesName = 'MOD-FF22+ModuleType+24V';
        uniqueKey = version_plausibility_service_1.VersionPlausibilityService.getUniqueKey(factsheet.serialNumber, 'MOD-FF22+ModuleType+24V+TXT');
        jest.spyOn(helpersMock, 'readJsonFile').mockResolvedValue({ 'MOD-FF22+ModuleType+24V+TXT': '2.0.0' });
        await version_plausibility_service_1.VersionPlausibilityService.initialize('dummy');
        await version_plausibility_service_1.VersionPlausibilityService.registerModuleVersion(factsheet, true);
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.size).toBe(1);
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.get(uniqueKey).version).toBe('1.0.0');
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.get(uniqueKey).requiredVersion).toBe('2.0.0');
    });
    it('registers module version correctly when moduleClass ends with 24 and it is a 24V module', async () => {
        factsheet.typeSpecification.moduleClass = 'ModuleType24';
        factsheet.typeSpecification.seriesName = 'MOD-FF22+ModuleType+24V';
        uniqueKey = version_plausibility_service_1.VersionPlausibilityService.getUniqueKey(factsheet.serialNumber, 'MOD-FF22+ModuleType+24V+TXT');
        jest.spyOn(helpersMock, 'readJsonFile').mockResolvedValue({ 'MOD-FF22+ModuleType+24V+TXT': '2.0.0' });
        await version_plausibility_service_1.VersionPlausibilityService.initialize('dummy');
        await version_plausibility_service_1.VersionPlausibilityService.registerModuleVersion(factsheet, true);
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.size).toBe(1);
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.get(uniqueKey).version).toBe('1.0.0');
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.get(uniqueKey).requiredVersion).toBe('2.0.0');
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.get(uniqueKey).moduleType).toBe('ModuleType');
    });
    it('resets mismatched modules cache correctly', async () => {
        jest.spyOn(helpersMock, 'readJsonFile').mockResolvedValue({ 'MOD-FF22+ModuleType': '2.0.0' });
        await version_plausibility_service_1.VersionPlausibilityService.initialize('dummy');
        await version_plausibility_service_1.VersionPlausibilityService.registerModuleVersion(factsheet);
        await version_plausibility_service_1.VersionPlausibilityService.resetMismatchedModulesCache();
        expect(version_plausibility_service_1.VersionPlausibilityService.mismatchedModules.size).toBe(0);
    });
});
