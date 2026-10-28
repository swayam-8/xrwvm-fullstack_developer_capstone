export default [
  { ignores: ['**/node_modules/**', '**/build/**', '**/static/**'] },
  {
    files: ['**/*.js', '**/*.jsx'],
    languageOptions: { ecmaVersion: 'latest', parserOptions: { ecmaFeatures: { jsx: true } } },
    rules: { 'no-dupe-args': 'error', 'no-dupe-keys': 'error', 'no-unreachable': 'error', 'no-constant-binary-expression': 'error', 'valid-typeof': 'error' },
  },
];
