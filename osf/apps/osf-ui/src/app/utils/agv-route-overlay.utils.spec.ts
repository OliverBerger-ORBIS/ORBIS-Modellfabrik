import {
  detectUnknownAgvSerialsFromTopics,
  flattenFtsOrderGraphPath,
  sameAgvRouteOverlayLayers,
  sameStyledAgvRouteSegmentList,
} from './agv-route-overlay.utils';

describe('agv-route-overlay.utils', () => {
  describe('flattenFtsOrderGraphPath', () => {
    it('concatenates BFS legs without duplicate join nodes', () => {
      const findRoutePath = (start: string, target: string): string[] | null => {
        if (start === 'A' && target === 'B') {
          return ['A', 'I1', 'B'];
        }
        if (start === 'B' && target === 'C') {
          return ['B', 'I2', 'C'];
        }
        return null;
      };
      expect(
        flattenFtsOrderGraphPath(
          { nodes: [{ id: 'A' }, { id: 'B' }, { id: 'C' }] },
          findRoutePath,
          (id) => id ?? ''
        )
      ).toEqual(['A', 'I1', 'B', 'I2', 'C']);
    });

    it('returns null for invalid orders', () => {
      expect(flattenFtsOrderGraphPath(null, () => null, () => '')).toBeNull();
      expect(flattenFtsOrderGraphPath({ nodes: [{ id: 'A' }] }, () => null, () => '')).toBeNull();
    });
  });

  describe('sameStyledAgvRouteSegmentList', () => {
    it('compares geometry and style within tolerance', () => {
      const a = [{ x1: 0, y1: 0, x2: 1, y2: 1, stroke: '#f97316', strokeDasharray: '3 14' }];
      const b = [{ x1: 0.2, y1: 0.2, x2: 1.2, y2: 1.2, stroke: '#f97316', strokeDasharray: '3 14' }];
      expect(sameStyledAgvRouteSegmentList(a, b)).toBe(true);
      expect(
        sameStyledAgvRouteSegmentList(a, [{ ...b[0], strokeDasharray: 'none' }])
      ).toBe(false);
    });
  });

  describe('sameAgvRouteOverlayLayers', () => {
    it('requires both planned and traveled lists to match', () => {
      const layer = {
        planned: [{ x1: 0, y1: 0, x2: 1, y2: 1, stroke: '#f97316' }],
        traveled: [{ x1: 0, y1: 0, x2: 0.2, y2: 0.2, stroke: '#f97316' }],
      };
      expect(sameAgvRouteOverlayLayers(layer, layer)).toBe(true);
      expect(
        sameAgvRouteOverlayLayers(layer, {
          ...layer,
          traveled: [{ x1: 5, y1: 5, x2: 6, y2: 6, stroke: '#f97316' }],
        })
      ).toBe(false);
    });
  });

  describe('detectUnknownAgvSerialsFromTopics', () => {
    it('lists FTS state topics not in layout config', () => {
      const result = detectUnknownAgvSerialsFromTopics(
        ['fts/v1/ff/5iO4/state', 'fts/v1/ff/stray/state', 'module/v1/ff/X/state'],
        new Set(['5iO4', 'leJ4'])
      );
      expect(result).toEqual([{ serial: 'stray', label: 'AGV-? (stray)' }]);
    });
  });
});
