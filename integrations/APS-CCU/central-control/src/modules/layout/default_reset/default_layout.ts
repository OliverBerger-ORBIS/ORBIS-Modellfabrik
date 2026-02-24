import { FactoryLayout, RoadDirection } from '../../../../../common/protocol/ccu';
import { ModuleType } from '../../../../../common/protocol/module';

export const DEFAULT_LAYOUT: FactoryLayout = {
  modules: [
    {
      type: ModuleType.HBW,
      serialNumber: 'HBW-MISSING',
      placeholder: true,
    },
    {
      type: ModuleType.DRILL,
      serialNumber: 'DRILL-MISSING',
      placeholder: true,
    },
    {
      type: ModuleType.MILL,
      serialNumber: 'MILL-MISSING',
      placeholder: true,
    },
    {
      type: ModuleType.DPS,
      serialNumber: 'DPS-MISSING',
      placeholder: true,
    },
    {
      type: ModuleType.AIQS,
      serialNumber: 'AIQS-MISSING',
      placeholder: true,
    },
    {
      type: ModuleType.CHRG,
      serialNumber: 'CHRG0',
    },
  ],
  intersections: [
    {
      id: '1',
    },
    {
      id: '2',
    },
    {
      id: '3',
    },
    {
      id: '4',
    },
  ],
  roads: [
    {
      length: 360,
      from: '1',
      to: '2',
      direction: RoadDirection.EAST,
    },
    {
      length: 360,
      from: '3',
      to: '1',
      direction: RoadDirection.NORTH,
    },
    {
      length: 360,
      from: '3',
      to: '4',
      direction: RoadDirection.EAST,
    },
    {
      length: 360,
      from: '4',
      to: '2',
      direction: RoadDirection.NORTH,
    },
    {
      direction: RoadDirection.EAST,
      from: 'HBW-MISSING',
      to: '1',
      length: 380,
    },
    {
      direction: RoadDirection.EAST,
      from: 'DRILL-MISSING',
      to: '3',
      length: 380,
    },
    {
      direction: RoadDirection.SOUTH,
      from: 'MILL-MISSING',
      to: '1',
      length: 380,
    },
    {
      direction: RoadDirection.WEST,
      from: 'DPS-MISSING',
      to: '2',
      length: 380,
    },
    {
      direction: RoadDirection.SOUTH,
      from: 'AIQS-MISSING',
      to: '2',
      length: 380,
    },
    {
      direction: RoadDirection.WEST,
      from: 'CHRG0',
      to: '4',
      length: 430,
    },
  ],
};
