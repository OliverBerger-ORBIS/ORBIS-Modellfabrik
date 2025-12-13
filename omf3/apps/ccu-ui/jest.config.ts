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
  // Thresholds are set to current actual values and will be gradually increased
  coverageThreshold: {
    global: {
      branches: 16, // Current: 16.34%, Target: 40% (gradual increase)
      functions: 23, // Current: 23.65%, Target: 60% (gradual increase)
      lines: 29, // Current: 29.09%, Target: 60% (gradual increase)
      statements: 28, // Current: 28.39%, Target: 60% (gradual increase)
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
