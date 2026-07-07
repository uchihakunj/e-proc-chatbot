#!/usr/bin/env node

/**
 * CHiPS Node.js Server Runner
 * Starts the Express.js web UI server with proper configuration and error handling
 * 
 * Usage:
 *   node run_server.js                    # Start with default config
 *   node run_server.js --port 3001        # Custom port
 *   node run_server.js --prod             # Production mode
 *   PORT=3001 node run_server.js          # Via environment variable
 */

'use strict';

const path = require('path');
const fs = require('fs');

// ─── Parse Arguments ────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const config = {
    port: process.env.PORT || 3001,
    flaskUrl: process.env.FLASK_URL || 'http://localhost:5001',
    isProd: process.env.NODE_ENV === 'production' || args.includes('--prod'),
    watch: !args.includes('--no-watch') && !args.includes('--prod'),
};

// Check for custom port argument
const portArgIndex = args.findIndex(arg => arg === '--port');
if (portArgIndex !== -1 && portArgIndex + 1 < args.length) {
    config.port = parseInt(args[portArgIndex + 1], 10);
}

// Check for flask URL argument
const flaskArgIndex = args.findIndex(arg => arg === '--flask-url');
if (flaskArgIndex !== -1 && flaskArgIndex + 1 < args.length) {
    config.flaskUrl = args[flaskArgIndex + 1];
}

// Show help
if (args.includes('--help') || args.includes('-h')) {
    console.log(`
CHiPS Node.js Server Runner

Usage:
  node run_server.js [options]

Options:
  --port PORT              Server port (default: 3001)
  --flask-url URL          Flask backend URL (default: http://localhost:5001)
  --prod                   Production mode
  --no-watch              Disable auto-reload
  -h, --help              Show this help message

Environment Variables:
  PORT                     Override server port
  FLASK_URL                Override Flask URL
  NODE_ENV                 Set to 'production' for prod mode

Examples:
  node run_server.js --port 3000
  PORT=8000 FLASK_URL=http://api.example.com node run_server.js
  NODE_ENV=production node run_server.js
  `);
    process.exit(0);
}

// ─── Validate Configuration ────────────────────────────────────────────────
if (isNaN(config.port) || config.port < 1 || config.port > 65535) {
    console.error(`❌ Invalid port: ${config.port}`);
    process.exit(1);
}

// ─── Check Required Files ──────────────────────────────────────────────────
const requiredFiles = [
    'server.js',
    'config.js'
];

const scriptDir = __dirname;
let missingFiles = [];

for (const file of requiredFiles) {
    const fullPath = path.join(scriptDir, file);
    if (!fs.existsSync(fullPath)) {
        missingFiles.push(file);
    }
}

if (missingFiles.length > 0) {
    console.error(`❌ Missing required files:`);
    missingFiles.forEach(f => console.error(`  - ${f}`));
    console.error(`\n   Current directory: ${scriptDir}`);
    process.exit(1);
}

// ─── Setup Environment ────────────────────────────────────────────────────
process.env.NODE_ENV = config.isProd ? 'production' : 'development';
process.env.PORT = config.port;
process.env.FLASK_URL = config.flaskUrl;
process.env.IS_PROD = config.isProd ? 'true' : 'false';

// ─── Create Logs Directory ────────────────────────────────────────────────
const logsDir = path.join(scriptDir, 'logs');
if (!fs.existsSync(logsDir)) {
    try {
        fs.mkdirSync(logsDir, { recursive: true });
    } catch (err) {
        console.warn(`⚠️  Failed to create logs directory: ${err.message}`);
    }
}

// ─── Start Server ────────────────────────────────────────────────────────
console.log('');
console.log('╔' + '═'.repeat(78) + '╗');
console.log('║' + 'CHiPS Node.js Server'.padEnd(78) + '║');
console.log('╚' + '═'.repeat(78) + '╝');
console.log('');
console.log(`⚙️  Configuration:`);
console.log(`    Port:        ${config.port}`);
console.log(`    Flask URL:   ${config.flaskUrl}`);
console.log(`    Mode:        ${config.isProd ? 'PRODUCTION' : 'DEVELOPMENT'}`);
console.log(`    Directory:   ${scriptDir}`);
console.log('');

// Load and start server
try {
    // Require server module (loads server.js)
    const { startServer } = require('./server');

    // Start the server
    startServer(config.port, config.flaskUrl)
        .then(() => {
            console.log('✅ Server started successfully');
        })
        .catch((err) => {
            console.error(`❌ Failed to start server: ${err.message}`);
            process.exit(1);
        });

} catch (err) {
    console.error(`❌ Error loading server: ${err.message}`);
    if (err.stack) {
        console.error(err.stack);
    }
    process.exit(1);
}

// ─── Graceful Shutdown ────────────────────────────────────────────────────
process.on('SIGINT', () => {
    console.log('\n⚠️  Received SIGINT, shutting down gracefully...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n⚠️  Received SIGTERM, shutting down gracefully...');
    process.exit(0);
});

// ─── Error Handlers ────────────────────────────────────────────────────
process.on('uncaughtException', (err) => {
    console.error('❌ Uncaught Exception:', err);
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});
