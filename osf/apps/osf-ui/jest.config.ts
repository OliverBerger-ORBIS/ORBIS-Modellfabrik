export default {
  displayName: 'osf-ui',
  preset: '../../../jest.preset.js',
  setupFilesAfterEnv: ['<rootDir>/src/test-setup.ts'],
  coverageDirectory: '../../../coverage/osf-ui',
  transform: {
    '^.+\\.(ts|mjs|js|html)$': [
      'jest-preset-angular',
      {
        tsconfig: '<rootDir>/tsconfig.spec.json',
        stringifyContentPathRegex: '\\.(html|svg)$',
      },
    ],
  },
  transformIgnorePatterns: ['node_modules/(?!.*\\.mjs$)'],
  snapshotSerializers: [
    'jest-preset-angular/build/serializers/no-ng-attributes',
    'jest-preset-angular/build/serializers/ng-snapshot',
    'jest-preset-angular/build/serializers/html-comment',
  ],
  // Coverage Monitoring Configuration
  // Thresholds updated after Phase 2 service test improvements
  // Progress: +104 tests in Phase 2, incremental improvements across all metrics
  // Phase 1 + Phase 2 total: +230 tests, steady progress towards 60% target
  coverageThreshold: {
    global: {
      branches: 42, // Gemessen 2026-08-06: 48.42%; Langziel 40%+
      functions: 52, // Gemessen: 59.65%; Langziel ~60%
      lines: 58, // Gemessen: 64.65%; Langziel 60%+
      statements: 58, // Gemessen: 63.55%; Langziel ~60%
    },
  },
  collectCoverageFrom: [
    'src/app/**/*.ts',
    '!src/app/**/*.spec.ts',
    '!src/app/**/*.mock.ts',
    '!src/app/**/__tests__/**',
    '!src/app/**/*.interface.ts',
    '!src/app/**/*.type.ts',
    '!src/app/**/*.enum.ts',
    '!src/app/**/index.ts',
    '!src/app/**/test-setup.ts',
    '!src/app/**/main.ts',
  ],
};
