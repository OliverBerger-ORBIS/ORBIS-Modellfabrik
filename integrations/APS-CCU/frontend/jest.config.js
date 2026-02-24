module.exports = {
  preset: "jest-preset-angular",
  setupFilesAfterEnv: ["<rootDir>/setup-jest.ts"],
  globalSetup: "<rootDir>/global-setup.js",
  testPathIgnorePatterns: ["/node_modules/", "/dist/"],
  testMatch: ["<rootDir>/src/**/*(*.)@(spec|test).[jt]s?(x)"],
  moduleNameMapper: {
    "^@fischertechnik/futurefactory$": "<rootDir>/projects/futurefactory/src/public-api",
    "^@common/(.*)$": "<rootDir>/projects/futurefactory/src/common/$1",
  },
};
