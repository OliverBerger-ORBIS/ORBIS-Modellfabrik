export default {
  displayName: 'ccu-ui',
  preset: '../../../jest.preset.js',
  setupFilesAfterEnv: ['<rootDir>/src/test-setup.ts'],
  coverageDirectory: '../../../coverage/ccu-ui',
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
      branches: 30, // Current: 30.68%, Phase 1: 28.73%, Target: 35% → 40%
      functions: 42, // Current: 42.29%, Phase 1: 37.66%, Target: 50% → 60%
      lines: 47, // Current: 47.18%, Phase 1: 44.61%, Target: 55% → 60%
      statements: 46, // Current: 46.08%, Phase 1: 43.56%, Target: 55% → 60%
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
