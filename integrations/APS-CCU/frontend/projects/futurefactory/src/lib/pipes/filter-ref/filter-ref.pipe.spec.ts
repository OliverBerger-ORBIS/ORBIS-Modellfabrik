import { ModuleType } from '../../../common/protocol/module';
import { FilterRefPipe } from './filter-ref.pipe';

describe('FilterRefPipe', () => {
  let pipe: FilterRefPipe;

  beforeEach(() => {
    pipe = new FilterRefPipe();
  });

  it('create an instance', () => {
    expect(pipe).toBeTruthy();
  });

  it('should return empty array if no positionName is given', () => {
    expect(
      pipe.transform(
        [{ referenceKey: 'ABC', referenceValue: 4711 }],
        '',
        ModuleType.HBW
      )
    ).toEqual([]);
  });

  describe(`${ModuleType.HBW}`, () => {
    it('should return no entry if positionName is not known', () => {
      expect(
        pipe.transform(
          [
            { referenceKey: 'cal__row2', referenceValue: 430 },
            { referenceKey: 'cal__colB', referenceValue: 1325 },
          ],
          'SPALTE_1',
          ModuleType.HBW
        )
      ).toEqual([]);
    });

    it('should return entry if positionName is known', () => {
      expect(
        pipe.transform(
          [
            { referenceKey: 'cal__row2', referenceValue: 430 },
            { referenceKey: 'cal__colB', referenceValue: 1325 },
          ],
          'RACK_REIHE_2_SPALTE_B',
          ModuleType.HBW
        )
      ).toEqual([
        { referenceKey: 'cal__row2', referenceValue: 430 },
        { referenceKey: 'cal__colB', referenceValue: 1325 },
      ]);
    });
  });

  describe(`${ModuleType.DPS}`, () => {
    it('should return no entry if positionName is not known', () => {
      expect(
        pipe.transform(
          [
            { referenceKey: 'RA.NFC.APPROACH.X', referenceValue: 430 },
            { referenceKey: 'RA.NFC.APPROACH.Y', referenceValue: 1325 },
            { referenceKey: 'RA.NFC.APPROACH.Z', referenceValue: 1325 },
          ],
          'NFC_TARGET',
          ModuleType.DPS
        )
      ).toEqual([]);
    });

    it('should return entry if positionName is known', () => {
      expect(
        pipe.transform(
          [
            { referenceKey: 'RA.NFC.APPROACH.X', referenceValue: 430 },
            { referenceKey: 'RA.NFC.APPROACH.Y', referenceValue: 1325 },
            { referenceKey: 'RA.NFC.APPROACH.Z', referenceValue: 1325 },
          ],
          'NFC_APPROACH',
          ModuleType.DPS
        )
      ).toEqual([
        { referenceKey: 'RA.NFC.APPROACH.X', referenceValue: 430 },
        { referenceKey: 'RA.NFC.APPROACH.Y', referenceValue: 1325 },
        { referenceKey: 'RA.NFC.APPROACH.Z', referenceValue: 1325 },
      ]);
    });
  });
});
