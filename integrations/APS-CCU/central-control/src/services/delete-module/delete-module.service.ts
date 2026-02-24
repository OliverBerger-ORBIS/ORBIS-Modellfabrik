import { AsyncMqttClient, IClientPublishOptions } from 'async-mqtt';
import { CcuTopic, ModuleTopic, getModuleTopic } from '../../../../common/protocol';
import { DeleteModuleRequest } from '../../../../common/protocol/ccu';
import { jsonIsoDateReviver } from '../../../../common/util/json.revivers';
import { matchTopics } from '../../helpers';
import { PairingStates } from '../../modules/pairing/pairing-states';

class DeleteModuleService {
  public static readonly TOPICS = [CcuTopic.DELETE_MODULE];
  private static instance: DeleteModuleService;

  private constructor(private mqtt: AsyncMqttClient) {
    this.listenToMessages();
    void this.subscribeToTopics();
  }

  public static initialize(mqtt: AsyncMqttClient): void {
    if (!DeleteModuleService.instance) {
      console.debug('Intialize the DeleteModuleService');
      DeleteModuleService.instance = new DeleteModuleService(mqtt);
      console.debug('DeleteModuleService ready');
    }
  }

  private listenToMessages(): void {
    this.mqtt.on('message', async (topic, message) => {
      if (matchTopics(DeleteModuleService.TOPICS, topic)) {
        await this.handleDeleteModuleRequest(message.toString());
      }
    });
  }

  private async subscribeToTopics(): Promise<void> {
    const subscriptions = await this.mqtt.subscribe(DeleteModuleService.TOPICS, { qos: 2 });
    console.log('DeleteModuleService:', subscriptions);
  }

  /**
   * Based on the received message, the module will be deleted from the CCU
   * and all topics will be cleared.
   * @param message The message containing the serial number of the module to delete.
   */
  private async handleDeleteModuleRequest(message: string) {
    if (!message) {
      // ignore empty message
      return;
    }
    const { serialNumber } = JSON.parse(message, jsonIsoDateReviver) as DeleteModuleRequest;
    if (!serialNumber) {
      // invalid serial number received, ignoring message
      return;
    }
    const publishOptions: IClientPublishOptions = { qos: 1, retain: true };
    const emptyMessage = Buffer.from('');
    const topicsToRemove = [
      ModuleTopic.STATE,
      ModuleTopic.ORDER,
      ModuleTopic.CONNECTION,
      ModuleTopic.FACTSHEET,
      ModuleTopic.INSTANT_ACTION,
    ];
    for (const topic of topicsToRemove) {
      await this.mqtt.publish(getModuleTopic(serialNumber, topic), emptyMessage, publishOptions);
    }
    await this.mqtt.publish(`${ModuleTopic.ROOT}/${serialNumber}`, emptyMessage, publishOptions);
    await PairingStates.getInstance().removeKnownModule(serialNumber);
  }
}

export default DeleteModuleService;
