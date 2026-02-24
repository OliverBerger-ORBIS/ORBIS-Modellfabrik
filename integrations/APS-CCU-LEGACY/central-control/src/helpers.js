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
exports.getPackageVersion = exports.readJsonFile = exports.writeJsonFile = exports.listenToTopics = exports.subscribeTopics = exports.matchTopics = void 0;
const promises_1 = require("node:fs/promises");
const packageJson = __importStar(require("../package.json"));
const generateRegexForTopicSub = (subscribedTopic) => {
    return new RegExp(`^${subscribedTopic}\$`.replaceAll('/+', '/\\w+').replace('/#', '/.+$').replaceAll('/', '\\/'));
};
const matchTopics = (subscribedTopics, topic) => {
    if (Array.isArray(subscribedTopics)) {
        return subscribedTopics.map(st => generateRegexForTopicSub(st)).some(rg => rg.test(topic));
    }
    else {
        return generateRegexForTopicSub(subscribedTopics).test(topic);
    }
};
exports.matchTopics = matchTopics;
/**
 * Subscribe to provided mqtt topics by using the provided mqtt client and subscription options.
 * @param topics the topics to subscribe to
 * @param subscriptionOptions the subscription options to use
 * @param mqtt the mqtt client to use
 */
const subscribeTopics = (topics, subscriptionOptions, mqtt) => {
    if (!mqtt) {
        throw new Error('MQTT client not provided');
    }
    mqtt
        .subscribe(topics, subscriptionOptions)
        .then(grants => console.debug('Subscriptions :', grants))
        .catch(err => {
        console.error('FATAL', err);
        process.exit(1);
    });
};
exports.subscribeTopics = subscribeTopics;
/**
 * Listen to provided mqtt topics by using the provided mqtt client and callback.
 * The message is only handled if the topic matches one of the provided topics.
 * @param mqtt The mqtt client to use
 * @param topics The topics to listen to
 * @param callback The callback to call when a message is received on a topic
 */
const listenToTopics = (mqtt, topics, callback) => {
    if (!mqtt) {
        throw new Error('MQTT client not provided');
    }
    mqtt.on('message', async (topic, payload) => {
        const payloadAsString = payload.toString();
        try {
            if ((0, exports.matchTopics)(topics, topic)) {
                await callback(payloadAsString);
            }
        }
        catch (error) {
            console.error('Error while handling message', payloadAsString, 'on topic', topic, ':', error);
        }
    });
};
exports.listenToTopics = listenToTopics;
/**
 * Writes an object as a JSON file.
 *
 * @param {string} filename - The name of the file to write.
 * @param {any} data - The object to write as JSON.
 */
async function writeJsonFile(filename, data) {
    await (0, promises_1.writeFile)(filename, JSON.stringify(data, undefined, 2), { encoding: 'utf8' });
}
exports.writeJsonFile = writeJsonFile;
/**
 * Reads a JSON file and returns the parsed object.
 *
 * @template T
 * @param {string} filename - The name of the file to read.
 * @returns {T} - The parsed JSON object.
 */
async function readJsonFile(filename) {
    const data = await (0, promises_1.readFile)(filename, { encoding: 'utf8' });
    return JSON.parse(data);
}
exports.readJsonFile = readJsonFile;
/**
 * Reads the package version from the package.json file.
 */
function getPackageVersion() {
    return packageJson?.version;
}
exports.getPackageVersion = getPackageVersion;
