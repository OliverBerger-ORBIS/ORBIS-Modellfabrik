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
    it('ModuleTab: moduleOverview$ should use dashboard.streams.moduleOverview$', () => {
      const content = readFileContent(path.join(tabsDir, 'shopfloor-tab.component.ts'));
      
      expect(content).toMatch(/this\.moduleOverview\$ = this\.dashboard\.streams\.moduleOverview\$\.pipe/);
      expect(content).toMatch(/shareReplay\(\s*\{\s*bufferSize:\s*1,\s*refCount:\s*false\s*\}\s*\)/);
    });

    it('SensorTab: cameraFrame$ should use dashboard.streams directly', () => {
      const content = readFileContent(path.join(tabsDir, 'sensor-tab.component.ts'));
      
      expect(content).toMatch(/this\.cameraFrame\$ = this\.dashboard\.streams\.cameraFrames\$\.pipe/);
      expect(content).toMatch(/shareReplay\(\s*\{\s*bufferSize:\s*1,\s*refCount:\s*false\s*\}\s*\)/);
    });
  });

  describe('Pattern 2: Streams without startWith should merge MessageMonitorService', () => {
    it('ProcessTab: flows$ should merge MessageMonitorService with dashboard.streams', () => {
      const content = readFileContent(path.join(tabsDir, 'process-tab.component.ts'));
      
      // Check MessageMonitorService.getLastMessage is called for 'ccu/state/flows'
      expect(content).toMatch(/this\.messageMonitor\.getLastMessage.*ccu\/state\/flows/);
      
      // Check merge is used
      expect(content).toMatch(/merge\(.*this\.dashboard\.streams\.flows\$/);
      
      // Check shareReplay with refCount: false
      expect(content).toMatch(/shareReplay\(\s*\{\s*bufferSize:\s*1,\s*refCount:\s*false\s*\}\s*\)/);
      
      // CRITICAL: Check that startWith comes AFTER filter and map (Pattern 2 requirement)
      const getLastMessageStart = content.indexOf('getLastMessage');
      expect(getLastMessageStart).toBeGreaterThan(-1);
      if (getLastMessageStart > -1) {
        const section = content.substring(getLastMessageStart);
        const pipeStart = section.indexOf('.pipe(');
        expect(pipeStart).toBeGreaterThan(-1);
        if (pipeStart > -1) {
          let depth = 0;
          let pipeEnd = pipeStart + 6;
          for (let i = pipeEnd; i < section.length; i++) {
            if (section[i] === '(') depth++;
            if (section[i] === ')') {
              if (depth === 0) {
                pipeEnd = i + 1;
                break;
              }
              depth--;
            }
          }
          const pipeChain = section.substring(pipeStart, pipeEnd);
          const filterIndex = pipeChain.indexOf('filter');
          const mapIndex = pipeChain.indexOf('map');
          const startWithIndex = pipeChain.indexOf('startWith');
          expect(filterIndex).toBeGreaterThan(-1);
          expect(mapIndex).toBeGreaterThan(filterIndex);
          expect(startWithIndex).toBeGreaterThan(mapIndex);
        }
      }
    });

    it('ConfigurationTab: configSnapshot$ should merge MessageMonitorService with dashboard.streams', () => {
      const content = readFileContent(path.join(tabsDir, 'configuration-tab.component.ts'));
      
      // Check MessageMonitorService.getLastMessage is called for 'ccu/state/config'
      expect(content).toMatch(/this\.messageMonitor\.getLastMessage.*ccu\/state\/config/);
      
      // Check merge is used
      expect(content).toMatch(/merge\(.*this\.dashboard\.streams\.config\$/);
      
      // Check shareReplay with refCount: false
      expect(content).toMatch(/shareReplay\(\s*\{\s*bufferSize:\s*1,\s*refCount:\s*false\s*\}\s*\)/);
      
      // CRITICAL: Check that startWith comes AFTER filter and map (Pattern 2 requirement)
      // Find the specific getLastMessage call for 'ccu/state/config'
      const getLastMessageStart = content.indexOf("getLastMessage<CcuConfigSnapshot>('ccu/state/config')");
      expect(getLastMessageStart).toBeGreaterThan(-1);
      if (getLastMessageStart > -1) {
        const section = content.substring(getLastMessageStart);
        const pipeStart = section.indexOf('.pipe(');
        expect(pipeStart).toBeGreaterThan(-1);
        if (pipeStart > -1) {
          let depth = 0;
          let pipeEnd = pipeStart + 6;
          for (let i = pipeEnd; i < section.length; i++) {
            if (section[i] === '(') depth++;
            if (section[i] === ')') {
              if (depth === 0) {
                pipeEnd = i + 1;
                break;
              }
              depth--;
            }
          }
          const pipeChain = section.substring(pipeStart, pipeEnd);
          const filterIndex = pipeChain.indexOf('filter');
          const mapIndex = pipeChain.indexOf('map');
          const startWithIndex = pipeChain.indexOf('startWith');
          expect(filterIndex).toBeGreaterThan(-1);
          expect(mapIndex).toBeGreaterThan(filterIndex);
          expect(startWithIndex).toBeGreaterThan(mapIndex);
        }
      }
    });

    it('SensorTab: sensorOverview$ should merge MessageMonitorService with dashboard.streams', () => {
      const content = readFileContent(path.join(tabsDir, 'sensor-tab.component.ts'));
      
      // Check MessageMonitorService.getLastMessage is called for sensor topics
      expect(content).toMatch(/this\.messageMonitor\.getLastMessage.*\/j1\/txt\/1\/i\/bme680/);
      expect(content).toMatch(/this\.messageMonitor\.getLastMessage.*\/j1\/txt\/1\/i\/ldr/);
      
      // Check merge is used
      expect(content).toMatch(/merge\(.*this\.dashboard\.streams\.sensorOverview\$/);
      
      // Check shareReplay with refCount: false
      expect(content).toMatch(/shareReplay\(\s*\{\s*bufferSize:\s*1,\s*refCount:\s*false\s*\}\s*\)/);
      
      // Check transformation method exists
      expect(content).toMatch(/buildSensorOverviewState/);
      
      // CRITICAL: Check that startWith is used in combineLatest and after map (Pattern 2 requirement)
      // SensorTab uses combineLatest, so we check that startWith is used in the combineLatest pipe
      const combineLatestSection = content.match(/combineLatest\s*\([^)]+\)[^}]*\.pipe\s*\([^)]+\)/);
      expect(combineLatestSection).toBeTruthy();
      if (combineLatestSection) {
        const pipeChain = combineLatestSection[0];
        const mapIndex = pipeChain.indexOf('map');
        const startWithIndex = pipeChain.indexOf('startWith');
        expect(mapIndex).toBeGreaterThan(-1);
        expect(startWithIndex).toBeGreaterThan(mapIndex);
        expect(pipeChain).toMatch(/buildSensorOverviewState/);
      }
    });
  });

  describe('Pattern Compliance: refCount: false', () => {
    it('All tab components should use refCount: false in shareReplay', () => {
      const tabFiles = [
        'order-tab.component.ts',
        'process-tab.component.ts',
        'shopfloor-tab.component.ts',
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
        { file: 'process-tab.component.ts', topic: 'ccu/state/flows' },
        { file: 'configuration-tab.component.ts', topic: 'ccu/state/config' },
        { file: 'sensor-tab.component.ts', topic: '/j1/txt/1/i/bme680' },
      ];

      pattern2Files.forEach(({ file, topic }) => {
        const content = readFileContent(path.join(tabsDir, file));
        
        // Check MessageMonitorService is imported
        expect(content).toMatch(/MessageMonitorService/);
        
        // Check getLastMessage is called with correct topic
        expect(content).toMatch(new RegExp(`getLastMessage.*${topic.replace('/', '\\/')}`));
      });
    });

    it('Pattern 2: startWith must come AFTER filter and map (critical pattern requirement)', () => {
      const pattern2Files = [
        'process-tab.component.ts',
        'configuration-tab.component.ts',
      ];

      pattern2Files.forEach((file) => {
        const content = readFileContent(path.join(tabsDir, file));
        
        // Extract the getLastMessage pipe chain (may span multiple lines)
        // For configuration-tab, find the specific 'ccu/state/config' call
        let getLastMessageStart = -1;
        if (file === 'configuration-tab.component.ts') {
          getLastMessageStart = content.indexOf("getLastMessage<CcuConfigSnapshot>('ccu/state/config')");
        } else {
          getLastMessageStart = content.indexOf('getLastMessage');
        }
        expect(getLastMessageStart).toBeGreaterThan(-1);
        if (getLastMessageStart > -1) {
          const section = content.substring(getLastMessageStart);
          const pipeStart = section.indexOf('.pipe(');
          expect(pipeStart).toBeGreaterThan(-1);
          if (pipeStart > -1) {
            let depth = 0;
            let pipeEnd = pipeStart + 6;
            for (let i = pipeEnd; i < section.length; i++) {
              if (section[i] === '(') depth++;
              if (section[i] === ')') {
                if (depth === 0) {
                  pipeEnd = i + 1;
                  break;
                }
                depth--;
              }
            }
            const pipeChain = section.substring(pipeStart, pipeEnd);
            const filterIndex = pipeChain.indexOf('filter');
            const mapIndex = pipeChain.indexOf('map');
            const startWithIndex = pipeChain.indexOf('startWith');
            expect(filterIndex).toBeGreaterThan(-1);
            expect(mapIndex).toBeGreaterThan(-1);
            expect(startWithIndex).toBeGreaterThan(-1);
            expect(startWithIndex).toBeGreaterThan(filterIndex);
            expect(startWithIndex).toBeGreaterThan(mapIndex);
          }
        }
      });
    });

    it('Streams with startWith should NOT use MessageMonitorService for their main streams', () => {
      const pattern1Files = [
        'shopfloor-tab.component.ts',
      ];

      pattern1Files.forEach((file) => {
        const content = readFileContent(path.join(tabsDir, file));
        
        // Check that getLastMessage is NOT called for main stream topics
        // (ShopfloorTab should only use dashboard.streams directly)
        const hasGetLastMessageForMainStream = 
          /getLastMessage.*module\/v1\/overview/.test(content);
        
        expect(hasGetLastMessageForMainStream).toBe(false);
      });
    });
  });
});
