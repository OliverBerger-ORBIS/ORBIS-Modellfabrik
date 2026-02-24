const nx = require('@nx/eslint-plugin');

module.exports = [
  ...nx.configs['flat/base'],
  {
    files: ['*.ts', '*.tsx', '*.js', '*.jsx'],
    rules: {},
  },
  {
    ignores: ['**/dist/**', '**/tmp/**', '**/.nx/**', 'integrations/**', 'backend/**'],
  },
];

