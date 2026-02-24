/** @type {import('ts-jest/dist/types').InitialOptionsTsJest} */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  collectCoverage: true,
  modulePathIgnorePatterns: [
    "<rootDir>/dist"
  ],
  reporters: [
    "default",
    ["jest-junit", { outputDirectory: "./test-results" }]
  ],
  coverageReporters: [
    "text",
    "cobertura",
    "lcov"
  ]
};
