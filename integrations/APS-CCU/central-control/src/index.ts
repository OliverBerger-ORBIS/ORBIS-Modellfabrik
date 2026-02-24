// Patching the console to include timestamps
import consoleStamp from 'console-stamp';
consoleStamp(console);

import path from 'path';
import config from './config';
import { matchTopics, subscribeTopics } from './helpers';
import {
  TOPICS as CALIBRATION_TOPICS,
  TOPIC_OPTIONS as CALIBRATION_TOPIC_OPTIONS,
  handleMessage as handleCalibrationMessage,
} from './modules/calibration';
import { CURRENT_ERRORS_TOPICS, CURRENT_ERRORS_TOPIC_OPTIONS, handleCurrentErrorsMessage } from './modules/current-errors';
import { handleMessage as factsheetMessage, TOPIC_OPTIONS as factsheetTopicOptions, TOPICS as factsheetTopics } from './modules/factsheets';
import { TOPIC_OPTIONS as ftsTopicOptions, TOPICS as ftsTopics, handleMessage as handleFtsMessage } from './modules/fts';
import {
  TOPICS as CHARGE_TOPICS,
  TOPIC_OPTIONS as CHARGE_TOPIC_OPTIONS,
  handleMessage as handleChargeMessage,
} from './modules/fts/charge/index';
import {
  TOPICS as GATEWAY_ORDER_TOPICS,
  TOPIC_OPTIONS as GATEWAY_ORDER_TOPIC_OPTIONS,
  handleMessage as handleGatewayMessages,
} from './modules/gateway/order';
import { TOPICS as LAYOUT_TOPICS, TOPIC_OPTIONS as LAYOUT_TOPIC_OPTIONS, handleMessage as handleLayoutMessage } from './modules/layout';
import {
  TOPICS as DEFAULT_LAYOUT_TOPICS,
  TOPIC_OPTIONS as DEFAULT_LAYOUT_TOPIC_OPTIONS,
  handleMessage as handleDefaultLayoutMessage,
} from './modules/layout/default_reset';
import { FactoryLayoutService } from './modules/layout/factory-layout-service';
import {
  TOPICS_CANCEL_ORDER,
  TOPIC_OPTIONS_CANCEL_ORDER,
  handleCancelOrders,
  handleMessage as handleOrderMessage,
  TOPIC_OPTIONS as orderTopicOptions,
  TOPICS as orderTopics,
} from './modules/order';
import { TOPICS as FLOWS_TOPICS, TOPIC_OPTIONS as FLOWS_TOPIC_OPTIONS, handleMessage as handleFlowsMessage } from './modules/order/flow';
import { OrderFlowService } from './modules/order/flow/order-flow-service';
import { OrderManagement } from './modules/order/management/order-management';
import {
  TOPIC_OPTIONS as connectionTopicOptions,
  TOPICS as connectionTopics,
  handleMessage as handleConnectionMessage,
} from './modules/pairing';
import {
  TOPIC_OPTIONS as ftsPairingTopicOptions,
  TOPICS as ftsPairingTopics,
  handleMessage as handleFtsPairingMessage,
} from './modules/pairing/pair_fts';
import {
  handleMessage as handleProductionMessage,
  TOPIC_OPTIONS as productionTopicOptions,
  TOPICS as productionTopics,
} from './modules/production';
import { updateActiveWarehouses } from './modules/production/cloud-stock';
import { TOPICS as RESET_TOPICS, TOPIC_OPTIONS as RESET_TOPIC_OPTIONS, handleMessage as handleResetMessage } from './modules/reset';
import { TOPICS as PARK_TOPICS, TOPIC_OPTIONS as PARK_TOPIC_OPTIONS, handleMessage as handleParkMessage } from './modules/park';
import {
  TOPICS as SETTINGS_TOPICS,
  TOPIC_OPTIONS as SETTINGS_TOPIC_OPTIONS,
  handleMessage as handleSettingsMessage,
} from './modules/settings';
import {
  TOPICS as VERSIONCHECKER_TOPICS,
  TOPIC_OPTIONS as VERSIONCHECKER_TOPIC_OPTIONS,
  handleMessage as handleVersionCheckerMessage,
} from './modules/version-checker';
import { AsyncMqttClient, connectMqtt } from './mqtt/mqtt';
import { TOPICS as CONFIG_TOPICS, TOPIC_OPTIONS as CONFIG_TOPIC_OPTIONS, handleMessage as handleConfigMessage } from './services/config';
import { GeneralConfigService } from './services/config/general-config-service';
import DeleteModuleService from './services/delete-module/delete-module.service';
import { CcuTopic } from '../../common/protocol';
import { VersionPlausibilityService } from './modules/version-checker/version-plausibility-service';

const startUp = async () => {
  console.debug('Starting up the whole thing');

  console.debug(`Retrieving config values:
  - CHARGING: ${JSON.stringify(config.ftsCharge)}
  - ROUTING: ${JSON.stringify(config.routing)}
  - STORAGE: ${JSON.stringify(config.storage)}`);

  await GeneralConfigService.initialize(path.join(config.storage.path, config.storage.generalConfigFile));
  await FactoryLayoutService.initialize(path.join(config.storage.path, config.storage.layoutFile));
  await OrderFlowService.initialize(path.join(config.storage.path, config.storage.flowsFile));

  console.debug('Initialize the mqtt client');
  const mqtt: AsyncMqttClient = await connectMqtt();
  console.debug('MQTT Client ready');

  await VersionPlausibilityService.initialize(config.storage.requiredVersionsPath);

  DeleteModuleService.initialize(mqtt);

  subscribeTopics(ftsTopics, ftsTopicOptions, mqtt);
  subscribeTopics(productionTopics, productionTopicOptions, mqtt);
  subscribeTopics(orderTopics, orderTopicOptions, mqtt);
  subscribeTopics(connectionTopics, connectionTopicOptions, mqtt);
  subscribeTopics(ftsPairingTopics, ftsPairingTopicOptions, mqtt);
  subscribeTopics(factsheetTopics, factsheetTopicOptions, mqtt);
  subscribeTopics(TOPICS_CANCEL_ORDER, TOPIC_OPTIONS_CANCEL_ORDER, mqtt);
  subscribeTopics(LAYOUT_TOPICS, LAYOUT_TOPIC_OPTIONS, mqtt);
  subscribeTopics(DEFAULT_LAYOUT_TOPICS, DEFAULT_LAYOUT_TOPIC_OPTIONS, mqtt);
  subscribeTopics(GATEWAY_ORDER_TOPICS, GATEWAY_ORDER_TOPIC_OPTIONS, mqtt);
  subscribeTopics(FLOWS_TOPICS, FLOWS_TOPIC_OPTIONS, mqtt);
  subscribeTopics(SETTINGS_TOPICS, SETTINGS_TOPIC_OPTIONS, mqtt);
  subscribeTopics(CALIBRATION_TOPICS, CALIBRATION_TOPIC_OPTIONS, mqtt);
  subscribeTopics(RESET_TOPICS, RESET_TOPIC_OPTIONS, mqtt);
  subscribeTopics(PARK_TOPICS, PARK_TOPIC_OPTIONS, mqtt);
  subscribeTopics(CHARGE_TOPICS, CHARGE_TOPIC_OPTIONS, mqtt);
  subscribeTopics(CONFIG_TOPICS, CONFIG_TOPIC_OPTIONS, mqtt);
  subscribeTopics(CURRENT_ERRORS_TOPICS, CURRENT_ERRORS_TOPIC_OPTIONS, mqtt);
  subscribeTopics(VERSIONCHECKER_TOPICS, VERSIONCHECKER_TOPIC_OPTIONS, mqtt);

  // The layout can only be published after the connection has been established
  await FactoryLayoutService.publishLayout();
  await GeneralConfigService.publish();
  await OrderFlowService.publishFlows();
  await updateActiveWarehouses();
  await OrderManagement.getInstance().sendOrderListUpdate();

  mqtt.on('error', console.error); // TODO: some self repair implementation
  mqtt.on('close', console.error); // TODO: Maybe some self repair implementation
  mqtt.on('message', (topic, payload: Buffer) => {
    const payloadAsString = payload.toString();

    try {
      if (matchTopics(CURRENT_ERRORS_TOPICS, topic)) {
        void handleCurrentErrorsMessage(payloadAsString);
      }
      if (matchTopics(ftsTopics, topic)) {
        void handleFtsMessage(payloadAsString); // async by design
      } else if (matchTopics(productionTopics, topic)) {
        void handleProductionMessage(payloadAsString); // async by design
      } else if (matchTopics(orderTopics, topic)) {
        void handleOrderMessage(payloadAsString); // async by design
      } else if (matchTopics(connectionTopics, topic)) {
        void handleConnectionMessage(payloadAsString, topic); // async by design
      } else if (matchTopics(ftsPairingTopics, topic)) {
        void handleFtsPairingMessage(payloadAsString); // async by design
      } else if (matchTopics(factsheetTopics, topic)) {
        void factsheetMessage(payloadAsString, topic); // async by design
      } else if (matchTopics(TOPICS_CANCEL_ORDER, topic)) {
        void handleCancelOrders(payloadAsString); // async by design
      } else if (matchTopics(LAYOUT_TOPICS, topic)) {
        void handleLayoutMessage(payloadAsString); // async by design
      } else if (matchTopics(DEFAULT_LAYOUT_TOPICS, topic)) {
        void handleDefaultLayoutMessage(payloadAsString); // async by design
      } else if (matchTopics(GATEWAY_ORDER_TOPICS, topic)) {
        void handleGatewayMessages(payloadAsString); // async by design
      } else if (matchTopics(FLOWS_TOPICS, topic)) {
        void handleFlowsMessage(payloadAsString); // async by design
      } else if (matchTopics(SETTINGS_TOPICS, topic)) {
        void handleSettingsMessage(payloadAsString); // async by design
      } else if (matchTopics(CALIBRATION_TOPICS, topic)) {
        void handleCalibrationMessage(payloadAsString); // async by design
      } else if (matchTopics(RESET_TOPICS, topic)) {
        void handleResetMessage(payloadAsString); // async by design
      } else if (matchTopics(PARK_TOPICS, topic)) {
        void handleParkMessage(payloadAsString); // async by design
      } else if (matchTopics(CHARGE_TOPICS, topic)) {
        void handleChargeMessage(payloadAsString); // async by design
      } else if (matchTopics(CONFIG_TOPICS, topic)) {
        void handleConfigMessage(payloadAsString); // async by design
      } else if (matchTopics(VERSIONCHECKER_TOPICS, topic)) {
        void handleVersionCheckerMessage(payloadAsString); // async by design
      } else {
        // NOTE: Some messages are handled by services within the modules, so we don't need to handle them here
        // console.warn(`No handler found to process message: [${payloadAsString}] on topic: [${topic}]`);
      }
    } catch (error) {
      console.error('Error while handling message', payloadAsString, 'on topic', topic, ':', error);
      // TODO: FITEFF22-346 Did anyone think of a solution on how to inform the user that this error occurred?
    }
  });

  // send global reset 30s after startup is finished
  setTimeout(() => {
    void mqtt.publish(CcuTopic.SET_RESET, JSON.stringify({ timestamp: new Date() }), { qos: 2 });
  }, 30_000);
};

startUp()
  .then(() => {
    console.info('CCU startup successfully');
  })
  .catch(error => console.error('Error:', error));
