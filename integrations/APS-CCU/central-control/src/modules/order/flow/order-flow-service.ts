import { MODULE_COMMAND_MAP, ModuleCommandType, ModuleType } from '../../../../../common/protocol/module';
import { readJsonFile, writeJsonFile } from '../../../helpers';
import { CcuTopic, Workpiece } from '../../../../../common/protocol';
import { randomUUID } from 'node:crypto';
import { OrderManufactureStep, OrderNavigationStep, OrderState, ProductionFlow, ProductionFlows } from '../../../../../common/protocol/ccu';
import { getMqttClient } from '../../../mqtt/mqtt';

/**
 * A complete representation of a production order that includes
 * all production steps and navigation steps required to handle an order to completion
 */
export type ProductionDefinition = {
  /**
   * The navigation steps are used to drive the FTS from one module to another
   */
  navigationSteps?: Array<OrderNavigationStep>;
  /**
   * The production steps are used to execute the production steps on the modules
   */
  productionSteps: Array<OrderManufactureStep>;
};

export class OrderFlowService {
  private static filename: string;
  private static flows: ProductionFlows = {};

  /**
   * Initialize the order flows with the given file used for persistence.
   * This should be called before connecting to mqtt.
   * @param filename
   */
  public static async initialize(filename: string) {
    console.debug('Initialize the Order Flows Service');
    if (this.filename) {
      return;
    }
    this.filename = filename;
    // setup default flows
    this.flows = this.getDefaultFlows();
    await this.reloadFlows();
    console.debug('Order Flows Service initialized');
  }

  /**
   * The default flows as used in the sample factory
   */
  public static getDefaultFlows(): ProductionFlows {
    return {
      BLUE: { steps: [ModuleType.MILL, ModuleType.DRILL, ModuleType.AIQS] },
      RED: { steps: [ModuleType.MILL, ModuleType.AIQS] },
      WHITE: { steps: [ModuleType.DRILL, ModuleType.AIQS] },
    };
  }

  /**
   * Converts a production flow to a complete production definition.
   * A flow consists of the production steps without fetching the workpiece and delivery
   * @param flow The module flow
   * @param depenendActionId optionally an actionid that has to be finished first
   * @private
   */
  public static convertFlowToDefinition(flow: ProductionFlow, depenendActionId?: string): ProductionDefinition {
    const definition: ProductionDefinition = {
      navigationSteps: [],
      productionSteps: [],
    };

    // start by driving to HBW and getting the workpiece
    const navigateFromStart = this.getNavigationStep(randomUUID(), ModuleType.START, ModuleType.HBW, depenendActionId);
    definition.navigationSteps?.push(navigateFromStart);
    const getWorkpieceStep = this.getOrderManufactureStep(randomUUID(), ModuleType.HBW, ModuleCommandType.DROP, navigateFromStart.id);
    definition.productionSteps.push(getWorkpieceStep);

    // add all production steps: navigate -> pick -> produce -> drop
    let prevStep = getWorkpieceStep;
    for (const mod of flow.steps) {
      const navigate = this.getNavigationStep(randomUUID(), prevStep.moduleType, mod, prevStep.id);
      definition.navigationSteps?.push(navigate);
      const pick = this.getOrderManufactureStep(randomUUID(), mod, ModuleCommandType.PICK, navigate.id);
      definition.productionSteps.push(pick);
      let produce: OrderManufactureStep | undefined;
      const action = MODULE_COMMAND_MAP[mod];
      if (action) {
        produce = this.getOrderManufactureStep(randomUUID(), mod, action, pick.id);
        definition.productionSteps.push(produce);
      }
      const drop = this.getOrderManufactureStep(randomUUID(), mod, ModuleCommandType.DROP, produce?.id ?? pick.id);
      definition.productionSteps.push(drop);

      prevStep = drop;
    }

    // end by dropping the workpiece at the DPS and staying there
    const navigateToDps = this.getNavigationStep(randomUUID(), prevStep.moduleType, ModuleType.DPS, prevStep.id);
    definition.navigationSteps?.push(navigateToDps);
    const dpsStep = this.getOrderManufactureStep(randomUUID(), ModuleType.DPS, ModuleCommandType.PICK, navigateToDps.id);
    definition.productionSteps.push(dpsStep);

    return definition;
  }

  /**
   * Reload flows from the persistent file.
   *
   * Flows will be merged on top of the existing flows.
   * An existing flow will be kept if the file does not contain a valid flow for that workpiece type.
   * An empty flow is valid
   */
  public static async reloadFlows() {
    try {
      const newFlows: ProductionFlows = await readJsonFile<ProductionFlows>(this.filename);
      // load new valid flows and merge them with the existing flows.
      for (const [item, flow] of Object.entries(newFlows)) {
        const wp = item as unknown as Workpiece;
        if ('steps' in flow && Array.isArray(flow.steps)) {
          this.flows[wp] = flow;
        } else {
          console.debug(`OrderFlowService: Ignoring invalid flow for ${wp}: `, flow);
        }
      }
    } catch (e) {
      console.debug(`OrderFlowService: Error reading flows from file ${this.filename}: `, e);
    }
  }

  /**
   * Save flows to the persistence file,
   */
  public static async saveFlows() {
    try {
      await writeJsonFile(this.filename, this.flows);
    } catch (e) {
      console.debug(`OrderFlowService: Error saving flows to file ${this.filename}: `, e);
    }
  }

  public static getFlows(): ProductionFlows {
    return JSON.parse(JSON.stringify(this.flows));
  }

  /**
   * Set new flows.
   * @param flows The new production flows
   */
  public static setFlows(flows: ProductionFlows) {
    for (const [item, flow] of Object.entries(flows)) {
      const wp = item as unknown as Workpiece;
      if ('steps' in flow && Array.isArray(flow.steps)) {
        this.flows[wp] = flow;
      } else {
        console.debug(`OrderFlowService: Ignoring invalid flow for ${wp}: `, flow);
      }
    }
  }

  /**
   * Publish flow information to the mqtt topic {@link CcuTopic.FLOWS} if a connection exists
   */
  public static async publishFlows(): Promise<void> {
    const mqtt = getMqttClient();
    if (mqtt) {
      return mqtt.publish(CcuTopic.FLOWS, JSON.stringify(this.flows), { qos: 1, retain: true });
    }
  }

  /**
   * Get a production definition for a workpiece type that has been defined with a flow
   * @param type
   * @param dependentActionId Optionally the id of an action that has to be finished before this production starts
   */
  public static getProductionDefinition(type: Workpiece, dependentActionId?: string): ProductionDefinition {
    const flow: ProductionFlow = this.flows[type] || { steps: [] };
    return this.convertFlowToDefinition(flow, dependentActionId);
  }

  /**
   * Returns a list of all production steps that are required to store a new workpiece
   *
   * 1) Drive the FTS to the input module
   * 2) Unload the workpiece onto the FTS
   * 3) Drive the FTS to the HighBayStorage
   * 4) Load the workpiece from the FTS into the HighBayStorage
   *
   */
  public static getStorageProductionDefinition(): ProductionDefinition {
    // Drive from starting point to the input module
    const startToDPS: OrderNavigationStep = this.getNavigationStep(randomUUID(), ModuleType.START, ModuleType.DPS);
    // load classified workpiece onto fts from input module
    const unloadWorkpieceFromDPS: OrderManufactureStep = this.getOrderManufactureStep(
      randomUUID(),
      ModuleType.DPS,
      ModuleCommandType.DROP,
      startToDPS.id,
    );
    // Drive from input module to the storage module
    const dpsToHBW: OrderNavigationStep = this.getNavigationStep(randomUUID(), ModuleType.DPS, ModuleType.HBW, unloadWorkpieceFromDPS.id);
    // load classified workpiece onto fts from input module
    const storeWorkpiece: OrderManufactureStep = this.getOrderManufactureStep(
      randomUUID(),
      ModuleType.HBW,
      ModuleCommandType.PICK,
      dpsToHBW.id,
    );
    // Stay at the last module
    return {
      navigationSteps: [startToDPS, dpsToHBW],
      productionSteps: [unloadWorkpieceFromDPS, storeWorkpiece],
    };
  }

  /**
   * Helper method to generate a navigation command in one line
   */
  public static getNavigationStep(
    actionId: string,
    source: ModuleType,
    target: ModuleType,
    dependentActionId?: string,
  ): OrderNavigationStep {
    return {
      id: actionId,
      type: 'NAVIGATION',
      state: OrderState.ENQUEUED,
      source,
      target,
      dependentActionId,
    };
  }

  /**
   * Helper method to generate a production command in one line
   */
  private static getOrderManufactureStep(
    id: string,
    moduleType: ModuleType,
    command: ModuleCommandType,
    dependentActionId?: string,
  ): OrderManufactureStep {
    return {
      id,
      type: 'MANUFACTURE',
      dependentActionId,
      state: OrderState.ENQUEUED,
      command,
      moduleType,
    };
  }
}
