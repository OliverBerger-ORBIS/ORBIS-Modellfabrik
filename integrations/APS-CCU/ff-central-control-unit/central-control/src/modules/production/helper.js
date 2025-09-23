"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.metadataForCommand = void 0;
const module_1 = require("../../../../common/protocol/module");
const getDurationMetadata = (type, command, pairedModule) => {
    const expectedCommand = module_1.MODULE_COMMAND_MAP[type];
    if (expectedCommand === command && expectedCommand !== module_1.ModuleCommandType.CHECK_QUALITY && pairedModule.productionDuration) {
        return {
            duration: pairedModule.productionDuration,
        };
    }
};
const metadataForCommand = (moduleType, command, pairedModule, workpiece, workpieceId) => {
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
exports.metadataForCommand = metadataForCommand;
