import {
  getShopfloorContainerIds,
  getShopfloorDeviceIds,
  getShopfloorConnectionIds,
  getDspContainerIds,
  getBusinessContainerIds,
  getEdgeComponentIds,
} from './layout.shared.config';

describe('Layout Shared Config Helper Functions', () => {
  describe('getShopfloorContainerIds', () => {
    it('should return all shopfloor container IDs', () => {
      const ids = getShopfloorContainerIds();

      expect(ids).toBeDefined();
      expect(Array.isArray(ids)).toBe(true);
      expect(ids.length).toBeGreaterThan(0);
    });

    it('should include layer-sf', () => {
      const ids = getShopfloorContainerIds();
      expect(ids).toContain('layer-sf');
    });

    it('should include systems group', () => {
      const ids = getShopfloorContainerIds();
      expect(ids).toContain('sf-systems-group');
    });

    it('should include devices group', () => {
      const ids = getShopfloorContainerIds();
      expect(ids).toContain('sf-devices-group');
    });

    it('should include specific systems', () => {
      const ids = getShopfloorContainerIds();
      expect(ids).toContain('sf-system-bp');
      expect(ids).toContain('sf-system-fts');
    });

    it('should include specific devices', () => {
      const ids = getShopfloorContainerIds();
      expect(ids).toContain('sf-device-mill');
      expect(ids).toContain('sf-device-drill');
      expect(ids).toContain('sf-device-aiqs');
      expect(ids).toContain('sf-device-hbw');
      expect(ids).toContain('sf-device-dps');
      expect(ids).toContain('sf-device-chrg');
    });
  });

  describe('getShopfloorDeviceIds', () => {
    it('should return only device IDs', () => {
      const ids = getShopfloorDeviceIds();

      expect(ids).toBeDefined();
      expect(Array.isArray(ids)).toBe(true);
      expect(ids.length).toBe(6);
    });

    it('should include all expected devices', () => {
      const ids = getShopfloorDeviceIds();
      expect(ids).toContain('sf-device-mill');
      expect(ids).toContain('sf-device-drill');
      expect(ids).toContain('sf-device-aiqs');
      expect(ids).toContain('sf-device-hbw');
      expect(ids).toContain('sf-device-dps');
      expect(ids).toContain('sf-device-chrg');
    });

    it('should not include layer or group IDs', () => {
      const ids = getShopfloorDeviceIds();
      expect(ids).not.toContain('layer-sf');
      expect(ids).not.toContain('sf-devices-group');
      expect(ids).not.toContain('sf-systems-group');
    });
  });

  describe('getShopfloorConnectionIds', () => {
    it('should return all shopfloor connection IDs', () => {
      const ids = getShopfloorConnectionIds();

      expect(ids).toBeDefined();
      expect(Array.isArray(ids)).toBe(true);
      expect(ids.length).toBe(8);
    });

    it('should include connections to systems', () => {
      const ids = getShopfloorConnectionIds();
      expect(ids).toContain('conn-dsp-edge-sf-system-bp');
      expect(ids).toContain('conn-dsp-edge-sf-system-fts');
    });

    it('should include connections to devices', () => {
      const ids = getShopfloorConnectionIds();
      expect(ids).toContain('conn-dsp-edge-sf-device-mill');
      expect(ids).toContain('conn-dsp-edge-sf-device-drill');
      expect(ids).toContain('conn-dsp-edge-sf-device-aiqs');
      expect(ids).toContain('conn-dsp-edge-sf-device-hbw');
      expect(ids).toContain('conn-dsp-edge-sf-device-dps');
      expect(ids).toContain('conn-dsp-edge-sf-device-chrg');
    });

    it('should return IDs in consistent format', () => {
      const ids = getShopfloorConnectionIds();
      ids.forEach((id) => {
        expect(id).toMatch(/^conn-dsp-edge-sf-(system|device)-[a-z]+$/);
      });
    });
  });

  describe('getDspContainerIds', () => {
    it('should return DSP container IDs', () => {
      const ids = getDspContainerIds();

      expect(ids).toBeDefined();
      expect(Array.isArray(ids)).toBe(true);
      expect(ids.length).toBe(4);
    });

    it('should include DSP layer and components', () => {
      const ids = getDspContainerIds();
      expect(ids).toContain('layer-dsp');
      expect(ids).toContain('dsp-ux');
      expect(ids).toContain('dsp-edge');
      expect(ids).toContain('dsp-mc');
    });

    it('should not include shopfloor or business IDs', () => {
      const ids = getDspContainerIds();
      expect(ids).not.toContain('layer-sf');
      expect(ids).not.toContain('layer-bp');
      expect(ids).not.toContain('bp-erp');
    });
  });

  describe('getBusinessContainerIds', () => {
    it('should return business container IDs', () => {
      const ids = getBusinessContainerIds();

      expect(ids).toBeDefined();
      expect(Array.isArray(ids)).toBe(true);
      expect(ids.length).toBe(6);
    });

    it('should include business layer and all business components', () => {
      const ids = getBusinessContainerIds();
      expect(ids).toContain('layer-bp');
      expect(ids).toContain('bp-erp');
      expect(ids).toContain('bp-mes');
      expect(ids).toContain('bp-cloud');
      expect(ids).toContain('bp-analytics');
      expect(ids).toContain('bp-data-lake');
    });

    it('should not include DSP or shopfloor IDs', () => {
      const ids = getBusinessContainerIds();
      expect(ids).not.toContain('layer-dsp');
      expect(ids).not.toContain('layer-sf');
      expect(ids).not.toContain('dsp-edge');
    });
  });

  describe('getEdgeComponentIds', () => {
    it('should return edge component IDs', () => {
      const ids = getEdgeComponentIds();

      expect(ids).toBeDefined();
      expect(Array.isArray(ids)).toBe(true);
      expect(ids.length).toBe(8);
    });

    it('should include all internal edge components', () => {
      const ids = getEdgeComponentIds();
      expect(ids).toContain('edge-comp-disc');
      expect(ids).toContain('edge-comp-event-bus');
      expect(ids).toContain('edge-comp-app-server');
      expect(ids).toContain('edge-comp-router');
      expect(ids).toContain('edge-comp-agent');
      expect(ids).toContain('edge-comp-log-server');
      expect(ids).toContain('edge-comp-disi');
      expect(ids).toContain('edge-comp-database');
    });

    it('should return IDs in consistent format', () => {
      const ids = getEdgeComponentIds();
      ids.forEach((id) => {
        expect(id).toMatch(/^edge-comp-[a-z-]+$/);
      });
    });

    it('should not include dsp-edge itself', () => {
      const ids = getEdgeComponentIds();
      expect(ids).not.toContain('dsp-edge');
    });
  });

  describe('Helper Function Consistency', () => {
    it('should return arrays with no duplicates', () => {
      const allHelpers = [
        getShopfloorContainerIds,
        getShopfloorDeviceIds,
        getShopfloorConnectionIds,
        getDspContainerIds,
        getBusinessContainerIds,
        getEdgeComponentIds,
      ];

      allHelpers.forEach((helper) => {
        const ids = helper();
        const uniqueIds = [...new Set(ids)];
        expect(ids.length).toBe(uniqueIds.length);
      });
    });

    it('should return the same array content on multiple calls', () => {
      const ids1 = getShopfloorContainerIds();
      const ids2 = getShopfloorContainerIds();
      expect(ids1).toEqual(ids2);
    });

    it('shopfloor devices should be a subset of shopfloor containers', () => {
      const devices = getShopfloorDeviceIds();
      const containers = getShopfloorContainerIds();

      devices.forEach((deviceId) => {
        expect(containers).toContain(deviceId);
      });
    });
  });
});
