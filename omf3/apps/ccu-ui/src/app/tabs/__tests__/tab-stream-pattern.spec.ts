/**
 * Tests to ensure Tab Stream Initialization Pattern is correctly implemented.
 * 
 * Pattern Rules:
 * 1. Streams with startWith in Business-Layer: Direct dashboard.streams.* with refCount: false
 * 2. Streams without startWith in Gateway-Layer: MessageMonitorService + merge with dashboard.streams.*
 * 3. All streams must use refCount: false to keep streams alive
 * 
 * See: docs/03-decision-records/11-tab-stream-initialization-pattern.md
 * 
 * Note: These tests validate the pattern by checking source code structure,
 * not by running the components (which would require full dashboard setup).
 */

import * as fs from 'fs';
import * as path from 'path';

describe('Tab Stream Initialization Pattern - Code Structure Validation', () => {
  const tabsDir = path.join(__dirname, '..');
  
  const readFileContent = (filePath: string): string => {
    return fs.readFileSync(filePath, 'utf-8');
  };

  describe('Pattern 1: Streams with startWith should use direct dashboard.streams.*', () => {
    it('OverviewTab: orders$, orderCounts$, ftsStates$ should use dashboard.streams directly', () => {
      const content = readFileContent(path.join(tabsDir, 'overview-tab.component.ts'));
      
      // Check orders$ uses dashboard.streams.orders$ with shareReplay and refCount: false
      expect(content).toMatch(/this\.orders\$ = this\.dashboard\.streams\.orders\$\.pipe/);
      expect(content).toMatch(/shareReplay\(\s*\{\s*bufferSize:\s*1,\s*refCount:\s*false\s*\}\s*\)/);
      
      // Check orderCounts$ uses dashboard.streams.orderCounts$
      expect(content).toMatch(/this\.orderCounts\$ = this\.dashboard\.streams\.orderCounts\$\.pipe/);
      
      // Check ftsStates$ uses dashboard.streams.ftsStates$
      expect(content).toMatch(/this\.ftsStates\$ = this\.dashboard\.streams\.ftsStates\$\.pipe/);
    });

    it('ModuleTab: moduleOverview$ should use dashboard.streams.moduleOverview$', () => {
      const content = readFileContent(path.join(tabsDir, 'module-tab.component.ts'));
      
      expect(content).toMatch(/this\.moduleOverview\$ = this\.dashboard\.streams\.moduleOverview\$\.pipe/);
      expect(content).toMatch(/shareReplay\(\s*\{\s*bufferSize:\s*1,\s*refCount:\s*false\s*\}\s*\)/);
    });

    it('SensorTab: sensorOverview$ and cameraFrame$ should use dashboard.streams directly', () => {
      const content = readFileContent(path.join(tabsDir, 'sensor-tab.component.ts'));
      
      expect(content).toMatch(/this\.sensorOverview\$ = this\.dashboard\.streams\.sensorOverview\$\.pipe/);
      expect(content).toMatch(/this\.cameraFrame\$ = this\.dashboard\.streams\.cameraFrames\$\.pipe/);
      expect(content).toMatch(/shareReplay\(\s*\{\s*bufferSize:\s*1,\s*refCount:\s*false\s*\}\s*\)/);
    });
  });

  describe('Pattern 2: Streams without startWith should merge MessageMonitorService', () => {
    it('OverviewTab: inventoryOverview$ should merge MessageMonitorService with dashboard.streams', () => {
      const content = readFileContent(path.join(tabsDir, 'overview-tab.component.ts'));
      
      // Check MessageMonitorService.getLastMessage is called for 'ccu/state/stock'
      expect(content).toMatch(/this\.messageMonitor\.getLastMessage.*ccu\/state\/stock/);
      
      // Check merge is used
      expect(content).toMatch(/merge\(.*this\.dashboard\.streams\.inventoryOverview\$/);
      
      // Check shareReplay with refCount: false
      expect(content).toMatch(/shareReplay\(\s*\{\s*bufferSize:\s*1,\s*refCount:\s*false\s*\}\s*\)/);
      
      // Check transformation method exists
      expect(content).toMatch(/buildInventoryOverviewFromSnapshot/);
    });

    it('ProcessTab: flows$ should merge MessageMonitorService with dashboard.streams', () => {
      const content = readFileContent(path.join(tabsDir, 'process-tab.component.ts'));
      
      // Check MessageMonitorService.getLastMessage is called for 'ccu/state/flows'
      expect(content).toMatch(/this\.messageMonitor\.getLastMessage.*ccu\/state\/flows/);
      
      // Check merge is used
      expect(content).toMatch(/merge\(.*this\.dashboard\.streams\.flows\$/);
      
      // Check shareReplay with refCount: false
      expect(content).toMatch(/shareReplay\(\s*\{\s*bufferSize:\s*1,\s*refCount:\s*false\s*\}\s*\)/);
    });

    it('ConfigurationTab: configSnapshot$ should merge MessageMonitorService with dashboard.streams', () => {
      const content = readFileContent(path.join(tabsDir, 'configuration-tab.component.ts'));
      
      // Check MessageMonitorService.getLastMessage is called for 'ccu/state/config'
      expect(content).toMatch(/this\.messageMonitor\.getLastMessage.*ccu\/state\/config/);
      
      // Check merge is used
      expect(content).toMatch(/merge\(.*this\.dashboard\.streams\.config\$/);
      
      // Check shareReplay with refCount: false
      expect(content).toMatch(/shareReplay\(\s*\{\s*bufferSize:\s*1,\s*refCount:\s*false\s*\}\s*\)/);
    });
  });

  describe('Pattern Compliance: refCount: false', () => {
    it('All tab components should use refCount: false in shareReplay', () => {
      const tabFiles = [
        'overview-tab.component.ts',
        'order-tab.component.ts',
        'process-tab.component.ts',
        'module-tab.component.ts',
        'sensor-tab.component.ts',
        'configuration-tab.component.ts',
      ];

      tabFiles.forEach((file) => {
        const content = readFileContent(path.join(tabsDir, file));
        
        // Check that shareReplay is used with refCount: false
        // This regex matches shareReplay({ bufferSize: 1, refCount: false })
        const hasRefCountFalse = /shareReplay\s*\(\s*\{\s*[^}]*refCount\s*:\s*false\s*[^}]*\}\s*\)/.test(content);
        
        // If shareReplay is used, it must have refCount: false
        if (content.includes('shareReplay')) {
          expect(hasRefCountFalse).toBe(true);
        }
      });
    });
  });

  describe('Pattern Compliance: MessageMonitorService usage', () => {
    it('Streams without startWith should import and use MessageMonitorService', () => {
      const pattern2Files = [
        { file: 'overview-tab.component.ts', topic: 'ccu/state/stock' },
        { file: 'process-tab.component.ts', topic: 'ccu/state/flows' },
        { file: 'configuration-tab.component.ts', topic: 'ccu/state/config' },
      ];

      pattern2Files.forEach(({ file, topic }) => {
        const content = readFileContent(path.join(tabsDir, file));
        
        // Check MessageMonitorService is imported
        expect(content).toMatch(/MessageMonitorService/);
        
        // Check getLastMessage is called with correct topic
        expect(content).toMatch(new RegExp(`getLastMessage.*${topic.replace('/', '\\/')}`));
      });
    });

    it('Streams with startWith should NOT use MessageMonitorService for their main streams', () => {
      const pattern1Files = [
        'module-tab.component.ts',
        'sensor-tab.component.ts',
      ];

      pattern1Files.forEach((file) => {
        const content = readFileContent(path.join(tabsDir, file));
        
        // Check that getLastMessage is NOT called for main stream topics
        // (ModuleTab and SensorTab should only use dashboard.streams directly)
        const hasGetLastMessageForMainStream = 
          /getLastMessage.*module\/v1\/overview/.test(content) ||
          /getLastMessage.*\/j1\/txt\/1\/i\/(bme680|ldr|cam)/.test(content);
        
        expect(hasGetLastMessageForMainStream).toBe(false);
      });
    });
  });
});
