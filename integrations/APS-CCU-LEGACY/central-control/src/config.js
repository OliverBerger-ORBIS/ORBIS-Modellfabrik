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
const path = __importStar(require("path"));
const config = {
    mqtt: {
        url: process.env.MQTT_URL,
        user: process.env.MQTT_USER,
        pass: process.env.MQTT_PASS,
        init_retries: Number(process.env.MQTT_INIT_RETRIES) || 10,
        init_retry_delay: Number(process.env.MQTT_INIT_RETRY_DELAY) || 500,
        debug: process.env.MQTT_DEBUG === 'true' || false,
    },
    storage: {
        path: process.env.STORAGE_PATH ?? path.join(__dirname, '..', 'data'),
        layoutFile: process.env.STORAGE_FILE_LAYOUT ?? 'factory-layout.json',
        flowsFile: process.env.STORAGE_FILE_FLOWS ?? 'factory-flows.json',
        generalConfigFile: process.env.STORAGE_FILE_GENERAL_CONFIG ?? 'general-config.json',
        requiredVersionsPath: path.join(__dirname, '..', 'static-data', 'required-versions.json'),
    },
    ftsCharge: {
        startChargeAtOrBelowPercentage: Number(process.env.FTS_CHARGE_BELOW_PERCENTAGE) || 10,
        disabled: process.env.FTS_CHARGE_DISABLED === 'true' || false,
    },
    routing: {
        disableNodeBlocking: process.env.ROUTING_NODE_BLOCKING_DISABLED === 'true' || false,
    },
};
exports.default = config;
