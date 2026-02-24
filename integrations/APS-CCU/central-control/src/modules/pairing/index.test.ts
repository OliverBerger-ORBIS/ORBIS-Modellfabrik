import { calcStatusLEDFromPairingState } from '.';
import { AvailableState, DeviceType, PairingState } from '../../../../common/protocol/ccu';
import { ModuleType } from '../../../../common/protocol/module';
import CurrentErrorsService from '../current-errors/current-errors.service';

describe('Pairing Module', () => {
  describe('calcStatusLEDFromPairingState', () => {
    it("should return green=true when there's only the dps", () => {
      const testPairing: PairingState = {
        modules: [
          {
            serialNumber: '4711-567',
            pairedSince: new Date(),
            type: DeviceType.MODULE,
            subType: ModuleType.DPS,
            available: AvailableState.READY,
          },
        ],
        transports: [],
      };

      const result = calcStatusLEDFromPairingState(testPairing, '4711-567');
      const expected = { green: true, red: false, yellow: false };
      expect(result.actions[0].metadata).toEqual(expected);
    });

    it("should return yellow=true when there's no error and a module is busy", () => {
      const testPairing: PairingState = {
        modules: [
          {
            serialNumber: '4711-567',
            pairedSince: new Date(),
            type: DeviceType.MODULE,
            subType: ModuleType.DPS,
            available: AvailableState.READY,
          },
          {
            serialNumber: '4711-123',
            pairedSince: new Date(),
            type: DeviceType.MODULE,
            subType: ModuleType.HBW,
            available: AvailableState.BUSY,
          },
        ],
        transports: [
          {
            serialNumber: '4711-789',
            pairedSince: new Date(),
            type: DeviceType.FTS,
            available: AvailableState.READY,
          },
        ],
      };
      jest.spyOn(CurrentErrorsService.getInstance(), 'getAllCurrentErrors').mockReturnValue([]);

      const result = calcStatusLEDFromPairingState(testPairing, '4711-123');
      const expected = { green: false, red: false, yellow: true };
      expect(result.actions[0].metadata).toEqual(expected);
    });

    it("should return yellow=true when there's no error and a fts is busy", () => {
      const testPairing: PairingState = {
        modules: [
          {
            serialNumber: '4711-456',
            pairedSince: new Date(),
            type: DeviceType.MODULE,
            subType: ModuleType.DPS,
            available: AvailableState.READY,
          },
          {
            serialNumber: '4711-123',
            pairedSince: new Date(),
            type: DeviceType.MODULE,
            subType: ModuleType.HBW,
            available: AvailableState.READY,
          },
        ],
        transports: [
          {
            serialNumber: '4711-789',
            pairedSince: new Date(),
            type: DeviceType.FTS,
            available: AvailableState.BUSY,
          },
        ],
      };
      jest.spyOn(CurrentErrorsService.getInstance(), 'getAllCurrentErrors').mockReturnValue([]);

      const result = calcStatusLEDFromPairingState(testPairing, '4711-567');
      const expected = { green: false, red: false, yellow: true };
      expect(result.actions[0].metadata).toEqual(expected);
    });

    it("should return red=true when there's an error and a module is blocked", () => {
      const testPairing: PairingState = {
        modules: [
          {
            serialNumber: '4711-567',
            pairedSince: new Date(),
            type: DeviceType.MODULE,
            subType: ModuleType.DPS,
            available: AvailableState.READY,
          },
          {
            serialNumber: '4711-123',
            pairedSince: new Date(),
            type: DeviceType.MODULE,
            subType: ModuleType.HBW,
            available: AvailableState.BLOCKED,
          },
        ],
        transports: [],
      };
      jest.spyOn(CurrentErrorsService.getInstance(), 'getAllCurrentErrors').mockReturnValue([
        {
          serialNumber: '4711-123',
          errors: [{ errorLevel: 'FATAL', errorType: 'ERROR', timestamp: new Date() }],
        },
      ]);

      const result = calcStatusLEDFromPairingState(testPairing, '4711-123');
      const expected = { green: false, red: true, yellow: false };
      expect(result.actions[0].metadata).toEqual(expected);
    });

    it("should return red=true when there's no error and a fts is blocked", () => {
      const testPairing: PairingState = {
        modules: [
          {
            serialNumber: '4711-456',
            pairedSince: new Date(),
            type: DeviceType.MODULE,
            subType: ModuleType.DPS,
            available: AvailableState.READY,
          },
          {
            serialNumber: '4711-123',
            pairedSince: new Date(),
            type: DeviceType.MODULE,
            subType: ModuleType.HBW,
            available: AvailableState.READY,
          },
        ],
        transports: [
          {
            serialNumber: '4711-789',
            pairedSince: new Date(),
            type: DeviceType.FTS,
            available: AvailableState.BLOCKED,
          },
        ],
      };
      jest.spyOn(CurrentErrorsService.getInstance(), 'getAllCurrentErrors').mockReturnValue([
        {
          serialNumber: '4711-789',
          errors: [{ errorLevel: 'FATAL', errorType: 'ERROR', timestamp: new Date() }],
        },
      ]);

      const result = calcStatusLEDFromPairingState(testPairing, '4711-789');
      const expected = { green: false, red: true, yellow: false };
      expect(result.actions[0].metadata).toEqual(expected);
    });

    function getTestPairingState(): PairingState {
      return {
        modules: [
          {
            serialNumber: 'SVR1E94026',
            type: 'MODULE',
            connected: true,
            available: AvailableState.READY,
            subType: ModuleType.HBW,
            pairedSince: new Date('2023-11-03T10:54:34.390Z'),
            assigned: true,
            version: '1.0.0',
            lastSeen: new Date('2023-11-03T14:34:15.815Z'),
            hasCalibration: true,
          },
          {
            serialNumber: 'SVR3QG1902',
            type: 'MODULE',
            connected: true,
            available: AvailableState.READY,
            subType: ModuleType.DPS,
            pairedSince: new Date('2023-11-03T10:54:34.391Z'),
            assigned: false,
            version: '1.0.0',
            lastSeen: new Date('2023-11-03T14:34:15.916Z'),
            hasCalibration: true,
          },
          {
            serialNumber: 'SVR1E95079',
            type: 'MODULE',
            connected: true,
            available: AvailableState.READY,
            subType: ModuleType.DRILL,
            productionDuration: 5,
            pairedSince: new Date('2023-11-03T10:54:34.391Z'),
            assigned: false,
            version: '1.0.0',
            lastSeen: new Date('2023-11-03T14:34:10.477Z'),
            hasCalibration: false,
          },
          {
            serialNumber: 'SVR1D30145',
            type: 'MODULE',
            connected: true,
            available: AvailableState.READY,
            subType: ModuleType.MILL,
            productionDuration: 5,
            pairedSince: new Date('2023-11-03T10:54:34.391Z'),
            assigned: false,
            version: '1.0.0',
            lastSeen: new Date('2023-11-03T14:34:10.353Z'),
            hasCalibration: false,
          },
          {
            serialNumber: 'SVR1D28511',
            type: 'MODULE',
            connected: true,
            available: AvailableState.READY,
            subType: ModuleType.AIQS,
            pairedSince: new Date('2023-11-03T10:54:34.391Z'),
            assigned: false,
            ip: '',
            version: '1.0.0',
            lastSeen: new Date('2023-11-03T14:34:15.590Z'),
            hasCalibration: true,
            calibrating: false,
          },
          {
            serialNumber: 'CHRG0',
            type: 'MODULE',
            connected: true,
            available: AvailableState.READY,
            subType: ModuleType.CHRG,
            pairedSince: new Date('2023-11-03T12:50:41.678Z'),
            assigned: false,
          },
        ],
        transports: [
          {
            serialNumber: '4gcx',
            type: 'FTS',
            connected: true,
            available: AvailableState.READY,
            ip: '-1',
            version: '0.2.0+git372f4be',
            lastSeen: new Date('2023-11-03T13:11:02.305Z'),
            charging: false,
            batteryVoltage: 8.7,
            batteryPercentage: 35,
            lastNodeId: 'UNKNOWN',
            lastModuleSerialNumber: 'UNKNOWN',
            lastLoadPosition: '2',
          },
          {
            serialNumber: 'BCix',
            type: 'FTS',
            connected: true,
            available: AvailableState.READY,
            ip: '-1',
            version: '0.2.0+git372f4be',
            lastSeen: new Date('2023-11-03T13:15:39.672Z'),
            charging: false,
            batteryVoltage: 8.7,
            batteryPercentage: 35,
            lastNodeId: 'SVR3QG1902',
            pairedSince: new Date('2023-11-03T13:18:39.009Z'),
            lastModuleSerialNumber: 'SVR3QG1902',
            lastLoadPosition: '2',
          },
        ],
      };
    }

    it('should evaluate driving FTS to yellow', () => {
      const testPairing: PairingState = getTestPairingState();
      testPairing.transports[1].available = AvailableState.BUSY;

      jest.spyOn(CurrentErrorsService.getInstance(), 'getAllCurrentErrors').mockReturnValue([]);

      const result = calcStatusLEDFromPairingState(testPairing, 'SVR3QG1902');
      const expected = { green: false, red: false, yellow: true };
      expect(result.actions[0].metadata).toEqual(expected);
    });

    it('should evaluate blocked charging FTS to yellow', () => {
      const testPairing: PairingState = getTestPairingState();
      testPairing.transports[1].available = AvailableState.BLOCKED;
      testPairing.transports[1].charging = true;
      testPairing.transports[1].lastNodeId = 'CHRG0';
      testPairing.transports[1].lastModuleSerialNumber = 'CHRG0';

      jest.spyOn(CurrentErrorsService.getInstance(), 'getAllCurrentErrors').mockReturnValue([]);

      const result = calcStatusLEDFromPairingState(testPairing, 'SVR3QG1902');
      const expected = { green: false, red: false, yellow: true };
      expect(result.actions[0].metadata).toEqual(expected);
    });

    it('should evaluate blocked not charging FTS with errors to red', () => {
      const testPairing: PairingState = getTestPairingState();
      testPairing.transports[1].available = AvailableState.BLOCKED;
      testPairing.transports[1].charging = false;
      testPairing.transports[1].lastNodeId = 'CHRG0';
      testPairing.transports[1].lastModuleSerialNumber = 'CHRG0';

      jest.spyOn(CurrentErrorsService.getInstance(), 'getAllCurrentErrors').mockReturnValue([
        {
          serialNumber: testPairing.transports[1].serialNumber,
          errors: [{ errorLevel: 'FATAL', errorType: 'ERROR', timestamp: new Date() }],
        },
      ]);

      const result = calcStatusLEDFromPairingState(testPairing, 'SVR3QG1902');
      const expected = { green: false, red: true, yellow: false };
      expect(result.actions[0].metadata).toEqual(expected);
    });
  });
});
