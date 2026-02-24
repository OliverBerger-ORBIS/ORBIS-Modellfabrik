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
exports.createMockMqttClient = void 0;
const localMqtt = __importStar(require("./mqtt/mqtt"));
/**
 * This function creates a mocked version of the {import('async-mqtt').AsyncMqttClient} and returns it.
 * Additionally it mocks the getMqttClient function from the mqtt module.
 * In addition, the mock includes spies on the publish and subscribe functions.
 *
 * @returns {import('async-mqtt').AsyncMqttClient}
 */
function createMockMqttClient() {
    // mock the mqtt client
    jest.mock('async-mqtt');
    const mqtt = {
        publish: jest.fn(() => Promise.resolve()),
        subscribe: jest.fn(() => Promise.resolve()),
        on: jest.fn(),
    };
    jest.spyOn(localMqtt, 'getMqttClient').mockReturnValue(mqtt);
    return mqtt;
}
exports.createMockMqttClient = createMockMqttClient;
