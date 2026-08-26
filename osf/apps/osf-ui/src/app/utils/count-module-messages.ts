/**
 * Count MQTT messages for a module/FTS serial across known topic patterns.
 * Extracted from {@link ShopfloorTabComponent} for unit testing without tab wiring.
 */
export function countModuleMessagesForSerial(
  serialNumber: string,
  allTopics: readonly string[],
  getHistoryLength: (topic: string) => number
): number {
  let count = 0;

  for (const topic of allTopics) {
    if (topic.startsWith('module/')) {
      const parts = topic.split('/');
      if (parts.length >= 5 && parts[3] === 'NodeRed' && parts[4] === serialNumber) {
        count += getHistoryLength(topic);
      } else if (parts.length >= 4 && parts[1] === 'v1' && parts[2] === 'ff' && parts[3] === serialNumber) {
        count += getHistoryLength(topic);
      } else if (parts.length >= 2 && parts[1] === serialNumber) {
        count += getHistoryLength(topic);
      }
    } else if (topic.startsWith('fts/')) {
      const parts = topic.split('/');
      if (parts.length >= 4 && parts[1] === 'v1' && parts[2] === 'ff' && parts[3] === serialNumber) {
        count += getHistoryLength(topic);
      } else if (parts.length >= 2 && parts[1] === serialNumber) {
        count += getHistoryLength(topic);
      }
    }
  }

  return count;
}
