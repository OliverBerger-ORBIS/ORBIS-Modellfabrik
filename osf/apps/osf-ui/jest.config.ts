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
      branches: 48, // Ist 24.08.2026: 51.2%; ~3 pp Puffer
      functions: 59, // Ist: 62.8%
      lines: 64, // Ist: 67.8%
      statements: 63, // Ist: 66.7%
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
