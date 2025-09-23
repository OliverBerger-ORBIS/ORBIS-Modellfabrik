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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getMqttClient = exports.connectMqtt = exports.AsyncMqttClient = void 0;
const config_1 = __importDefault(require("../config"));
const MQTT = __importStar(require("async-mqtt"));
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
var async_mqtt_1 = require("async-mqtt");
Object.defineProperty(exports, "AsyncMqttClient", { enumerable: true, get: function () { return async_mqtt_1.AsyncMqttClient; } });
let mqttClient;
/**
 * Connects to the configured MQTT broker
 *
 * The connection is retried a configurable amount, by default 10 times with a delay of 500ms.
 * They retry is necessary if the mqtt broker starts slower than this control unit
 */
async function connectMqtt() {
    if (mqttClient) {
        return mqttClient;
    }
    let error = null;
    for (let tries = 0; tries < config_1.default.mqtt.init_retries; tries++) {
        console.debug(`Starting MQTT on [${config_1.default.mqtt.url}] - Try ${tries + 1} of ${config_1.default.mqtt.init_retries} retries`);
        try {
            const mqtt = await MQTT.connectAsync(config_1.default.mqtt.url, {
                username: config_1.default.mqtt.user,
                password: config_1.default.mqtt.pass,
            });
            if (mqtt) {
                mqttClient = mqtt;
                return mqttClient;
            }
        }
        catch (e) {
            console.info('Attempt failed, waiting ' + config_1.default.mqtt.init_retry_delay);
            await delay(config_1.default.mqtt.init_retry_delay);
            error = e;
        }
    }
    throw error ?? new Error('Unable to connect to mqtt');
}
exports.connectMqtt = connectMqtt;
const getMqttClient = () => {
    return mqttClient;
};
exports.getMqttClient = getMqttClient;
