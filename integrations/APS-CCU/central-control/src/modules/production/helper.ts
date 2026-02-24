import { DurationMetadata, MODULE_COMMAND_MAP, ModuleCommandType, ModuleType, StoreMetadata } from '../../../../common/protocol/module';
import { PairedModule, Workpiece } from '../../../../common/protocol/ccu';

const getDurationMetadata = (type: ModuleType, command: ModuleCommandType, pairedModule: PairedModule) => {
  const expectedCommand = MODULE_COMMAND_MAP[type];
  if (expectedCommand === command && expectedCommand !== ModuleCommandType.CHECK_QUALITY && pairedModule.productionDuration) {
    return {
      duration: pairedModule.productionDuration,
    };
  }
};

export const metadataForCommand = (
  moduleType: ModuleType,
  command: ModuleCommandType,
  pairedModule: PairedModule,
  workpiece: Workpiece,
  workpieceId?: string,
): DurationMetadata | StoreMetadata => {
  const tempDuration = getDurationMetadata(moduleType, command, pairedModule);
  if (!tempDuration) {
    return {
      type: workpiece,
      workpieceId,
    };
  }

  return {
    ...tempDuration,
    type: workpiece,
  };
};
