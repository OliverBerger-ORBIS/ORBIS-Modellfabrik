import * as path from 'path';

export interface Config {
  /**
   * Mqtt credentials and initial retry configuration to connect with the broker. URL, Password and User are not defaulted
   * to any default value in order to verify that they are provided.
   * Without those values, the CCU should not start up
   */
  mqtt: {
    pass: string | undefined;
    user: string | undefined;
    url: string | undefined;
    init_retry_delay: number;
    init_retries: number;
    /** If true, additional debug info is logged to the connected broker. Defaults to false. */
    debug?: boolean;
  };
  storage: {
    layoutFile: string;
    path: string;
    flowsFile: string;
    generalConfigFile: string;
    requiredVersionsPath: string;
  };
  ftsCharge: {
    /** Battery percentage reported by the FTS at which the CCU will issue a charging command  */
    startChargeAtOrBelowPercentage: number;
    /** If disabled, no charging commands will be issued by the CCU */
    disabled: boolean;
  };
  routing: {
    /**
     * If set to true, blocked nodes will be ignored which can lead to FTS crashes.
     * This should only be disabled if:
     * 1) The user only has one FTS
     * 2) For debugging purposes
     */
    disableNodeBlocking: boolean;
  };
}

const config: Config = {
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

export default config;
