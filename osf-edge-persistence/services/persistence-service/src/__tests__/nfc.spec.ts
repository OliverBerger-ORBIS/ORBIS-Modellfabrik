import { describe, expect, it } from 'vitest';
import { collectLoadNfcIds, isNfcLikeId, resolveWorkpieceId, resolveWorkpieceType } from '../nfc';

describe('nfc helpers', () => {
  it('rejects quality results that look like ids', () => {
    expect(isNfcLikeId('PASSED')).toBe(false);
    expect(isNfcLikeId('wp-1')).toBe(false);
    expect(isNfcLikeId('92e0ad91595f63')).toBe(true);
  });

  it('resolves DPS RGB_NFC result as workpiece id (Replay path)', () => {
    const id = resolveWorkpieceId({
      actionState: {
        command: 'RGB_NFC',
        state: 'FINISHED',
        result: '92e0ad91595f63',
        metadata: { type: 'WHITE' },
      },
    });
    expect(id).toBe('92e0ad91595f63');
    expect(resolveWorkpieceType({
      actionState: { metadata: { type: 'WHITE' } },
    })).toBe('WHITE');
  });

  it('does not take the first loadId of a multi-load remainder', () => {
    expect(
      resolveWorkpieceId({
        loads: [
          { loadId: '2b2c6dd469a47a', loadType: 'WHITE' },
          { loadId: '78d10489b38ed8', loadType: 'RED' },
        ],
      })
    ).toBeUndefined();
  });

  it('collects unique FTS load NFCs for fan-out', () => {
    expect(
      collectLoadNfcIds({
        load: [
          { loadId: 'nfcwhite1', loadType: 'WHITE', loadPosition: '1' },
          { loadId: 'nfcred222', loadType: 'RED', loadPosition: '2' },
        ],
      })
    ).toEqual(['nfcwhite1', 'nfcred222']);
  });

  it('reads color from module order action.metadata.type', () => {
    expect(
      resolveWorkpieceType({
        serialNumber: 'SVR4H76449',
        action: { command: 'PICK', metadata: { type: 'RED' } },
      })
    ).toBe('RED');
  });

  it('ignores FTS vehicle type as workpiece color', () => {
    expect(resolveWorkpieceType({ type: 'FTS', load: [{ loadType: 'BLUE', loadId: 'nfcblue1' }] })).toBe(
      'BLUE'
    );
  });
});
