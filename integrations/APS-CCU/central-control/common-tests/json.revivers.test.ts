import { jsonIsoDateReviver, SIMPLE_ISO_DATE_REGEX } from '../../common/util/json.revivers';

describe('Date matching', () => {
  it('should match valid dates', () => {
    const validDates = [
      '2022-03-07T13:00Z',
      '2022-03-07T13:00:00Z',
      '2022-03-07T13:00:00.123Z',
      '2022-03-07T13:00:00.1234Z',
      '2026-08-07T13:00:00.12345Z',
    ];

    for (const date of validDates) {
      expect(SIMPLE_ISO_DATE_REGEX.test(date)).toEqual(true);
    }
  });

  it('should not match invalid dates', () => {
    const invalidDates = [
      ' 2022-03-07T13:00Z',
      ' 2022-03-07T13:00:00Z',
      ' 2022-03-07T13:00:00.123Z',
      ' 2022-03-07T13:00:00.1234Z',
      ' 2026-08-07T13:00:00.12345Z',
      '2022-03-07T13:00Z ',
      '2022-03-07T13:00:00Z ',
      '2022-03-07T13:00:00.123Z ',
      '2022-03-07T13:00:00.1234Z ',
      '2026-08-07T13:00:00.12345Z ',
      '2022-03-07T13:00',
      '2022-03-07T13:00:00',
      '2022-03-07T13:00:00+01:00',
      '2022-03-07T13:00:00-01:00',
      '2022-03-07T13:00:00+01:00Z',
      '2022-03-07T13:00:00-01:00Z',
      '2022-03-07T13:00:00.123',
      '2022-03-07T13:00:00.1234',
      '2026-08-07T13:00:00.12345',
      '2022-03-07',
      '12022-03-07T13:00:00',
      '2022-03-07T13:00:00.123',
      '2022-03-17T13:00:00.123',
      '2022-03-07T13:00:00.1234',
      '2026-08-07T13:00:00.12345',
      'no date',
    ];

    for (const date of invalidDates) {
      expect(SIMPLE_ISO_DATE_REGEX.test(date)).toEqual(false);
    }
  });

  it('should convert a valid date to a date object', () => {
    expect(jsonIsoDateReviver('anything', '2022-03-07T13:00:00.123Z')).toEqual(new Date('2022-03-07T13:00:00.123Z'));
    expect(jsonIsoDateReviver('', '2022-03-07T13:00:00.123Z')).toEqual(new Date('2022-03-07T13:00:00.123Z'));
  });

  it('should not convert a non-date values', () => {
    expect(jsonIsoDateReviver('anything', ' 2022-03-07T13:00:00.123Z')).toEqual(' 2022-03-07T13:00:00.123Z');
    expect(jsonIsoDateReviver('', 'a string')).toBe('a string');
    expect(jsonIsoDateReviver('', true)).toBe(true);
    expect(jsonIsoDateReviver('', false)).toBe(false);
    expect(jsonIsoDateReviver('', null)).toBe(null);
    expect(jsonIsoDateReviver('', { a: 1 })).toEqual({ a: 1 });
    expect(jsonIsoDateReviver('', [12])).toEqual([12]);
  });

  it('should revive a json object with dates correctly', () => {
    // eslint-disable-next-line prettier/prettier
    const data = '{"timestamp":"2022-02-02T12:13:14.000Z","no_timestamp":"2024-02-02 12:13:14Z","something":"2024-02-02T12:13:14.000Z","text_field":"example","nested":{"ts":"2023-02-02T12:13:14.000Z","bool":true,"num":12,"text":"some text"}}';

    const expected = {
      timestamp: new Date('2022-02-02T12:13:14Z'),
      no_timestamp: '2024-02-02 12:13:14Z',
      something: new Date('2024-02-02T12:13:14Z'),
      text_field: 'example',
      nested: {
        ts: new Date('2023-02-02T12:13:14Z'),
        bool: true,
        num: 12,
        text: 'some text',
      },
    };
    expect(JSON.parse(data, jsonIsoDateReviver)).toStrictEqual(expected);
  });
});
