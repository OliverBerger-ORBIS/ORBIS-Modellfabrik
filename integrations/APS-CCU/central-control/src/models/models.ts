import { DeviceType, FtsPairedModule } from '../../../common/protocol/ccu';
import { ModuleType } from '../../../common/protocol/module';
import { Path } from '../modules/fts/navigation/navigator-service';

export class ControllerNotReadyError extends Error {
  constructor(deviceType: DeviceType, moduleType?: ModuleType, customMessage?: string) {
    super(
      `Controller is not ready for deviceType ${deviceType}${moduleType ? ` and moduleType ${moduleType}` : ''}${
        customMessage ? ` message ${customMessage}` : ''
      }`,
    );
    this.name = 'ControllerNotReadyError';
  }
}

export class FTSNotReadyError extends ControllerNotReadyError {
  constructor(customMessage: string) {
    super('FTS', undefined, customMessage);
    this.name = 'FTSNotReadyError';
  }
}

export type FtsPathResult = {
  fts: FtsPairedModule;
  path: Path;
};
