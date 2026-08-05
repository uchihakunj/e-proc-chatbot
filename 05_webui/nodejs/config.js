'use strict';

/**
 * Central config — every env-var read happens here.
 * server.js and route files import from this module.
 */

// Load .env if present (dev convenience; in production set env vars directly)
try {
  require('dotenv').config({ path: require('path').resolve(__dirname, '../../.env') });
} catch (_) {
  // dotenv is optional — ignore if not installed
}

// Login/auth removed — no JWT_SECRET or user store required anymore.
const flaskPort = process.env.FLASK_PORT || '5000';
const defaultFlaskUrl = `http://127.0.0.1:${flaskPort}`;

module.exports = {
  PORT:             parseInt(process.env.PORT || '3000', 10),
  FLASK_URL:        process.env.FLASK_URL || defaultFlaskUrl,
  FLASK_TIMEOUT_MS: parseInt(process.env.FLASK_TIMEOUT_MS || '300000', 10),
  IS_PROD:          process.env.NODE_ENV  === 'production',
};
