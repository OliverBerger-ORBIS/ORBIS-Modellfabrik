const nx = require('@nx/eslint-plugin');
const baseConfig = require('../../../eslint.config.js');

module.exports = [
  ...baseConfig,
  ...nx.configs['flat/angular'],
  ...nx.configs['flat/angular-template'],
  {
    files: ['**/*.ts'],
    rules: {
      '@angular-eslint/directive-selector': [
        'error',
        {
          type: 'attribute',
          prefix: 'app',
          style: 'camelCase',
        },
      ],
      '@angular-eslint/component-selector': [
        'error',
        {
          type: 'element',
          prefix: 'app',
          style: 'kebab-case',
        },
      ],
      // Angular Best Practices
      '@angular-eslint/prefer-on-push-component-change-detection': 'error',
      // Note: TypeScript ESLint rules are configured via typescript-eslint in base config
      // Note: RxJS subscription rules require eslint-plugin-rxjs which is not compatible with ESLint 9
      // Consider manual code review for subscription management until plugin is updated
    },
  },
  {
    files: ['**/*.html'],
    // Override or add rules here
    rules: {},
  },
];
