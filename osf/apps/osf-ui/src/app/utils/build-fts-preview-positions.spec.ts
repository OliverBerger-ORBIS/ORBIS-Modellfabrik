import type { FtsState } from '@osf/entities';
import { buildFtsPreviewPositionsFromStates } from './build-fts-preview-positions';

describe('buildFtsPreviewPositionsFromStates', () => {
  const baseState = (serial: string, lastNodeId: string): FtsState =>
    ({
      serialNumber: serial,
      lastNodeId,
      headerId: 1,
      timestamp: '2026-01-01T00:00:00Z',
      orderId: 'o1',
      orderUpdateId: 1,
      lastNodeSequenceId: 0,
      driving: false,
      paused: false,
      batteryState: { percentage: 80, charging: false, currentVoltage: 12, minVolt: 10, maxVolt: 14 },
      actionStates: [],
      load: [],
      nodeStates: [],
      edgeStates: [],
      errors: [],
    }) as FtsState;

  it('resolves state by serial key and builds positions from layout nodes', () => {
    const positions = buildFtsPreviewPositionsFromStates(
      { '5iO4': baseState('5iO4', 'NODE_A') },
      ['5iO4'],
      (nodeId) => (nodeId === 'NODE_A' ? { x: 10, y: 20 } : null),
      () => '#f97316'
    );
    expect(positions).toEqual([{ serial: '5iO4', x: 10, y: 20, color: '#f97316' }]);
  });

  it('resolves state when keyed by different map entry but matching serialNumber', () => {
    const positions = buildFtsPreviewPositionsFromStates(
      { alias: baseState('xkI4', 'NODE_B') },
      ['xkI4'],
      () => ({ x: 1, y: 2 }),
      (serial) => (serial === 'xkI4' ? '#eab308' : '#ccc')
    );
    expect(positions[0]?.serial).toBe('xkI4');
    expect(positions[0]?.color).toBe('#eab308');
  });

  it('falls back to state.position when layout node is missing', () => {
    const state = {
      ...baseState('5iO4', 'MISSING'),
      position: { x: 99, y: 88 },
    };
    const positions = buildFtsPreviewPositionsFromStates(
      { '5iO4': state },
      ['5iO4'],
      () => null,
      () => '#000'
    );
    expect(positions).toEqual([{ serial: '5iO4', x: 99, y: 88, color: '#000' }]);
  });

  it('skips AGVs without lastNodeId or resolvable position', () => {
    const positions = buildFtsPreviewPositionsFromStates(
      { '5iO4': baseState('5iO4', '') },
      ['5iO4', 'xkI4'],
      () => null,
      () => '#000'
    );
    expect(positions).toEqual([]);
  });

  it('preserves agvSerialsOrdered sequence', () => {
    const ftsStates = {
      '5iO4': baseState('5iO4', 'A'),
      xkI4: baseState('xkI4', 'B'),
    };
    const positions = buildFtsPreviewPositionsFromStates(
      ftsStates,
      ['xkI4', '5iO4'],
      (nodeId) => ({ x: nodeId === 'A' ? 1 : 2, y: 0 }),
      (serial) => serial
    );
    expect(positions.map((p) => p.serial)).toEqual(['xkI4', '5iO4']);
  });
});
