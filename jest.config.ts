import type { Config } from 'jest';

const config: Config = {
  testMatch: ['**/tests/node/**/*.spec.ts'],
  reporters: [
    'default',
    ['jest-junit', { outputDirectory: 'reports', outputName: 'junit-node.xml' }]
  ],
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['lcov', 'text'],
};

export default config;
