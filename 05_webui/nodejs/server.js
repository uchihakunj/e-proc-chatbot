'use strict';

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const morgan = require('morgan');
const path = require('path');
const net = require('net');
const { spawn } = require('child_process');

const { PORT, FLASK_URL, IS_PROD } = require('./config');
// Auth (login UI) removed — the chatbot is now open access. The proxies below
// forward straight to Flask with no JWT guard.

const FLASK_APP_DIR = path.join(__dirname, '..');
const FLASK_APP_PATH = path.join(FLASK_APP_DIR, 'app.py');
const FLASK_COMMAND = process.env.PYTHON || 'python';
let flaskProcess = null;

function parseBackendTarget(urlString) {
  try {
    const target = new URL(urlString);
    return {
      hostname: target.hostname,
      port: Number(target.port || (target.protocol === 'https:' ? 443 : 80)),
    };
  } catch (_err) {
    return { hostname: '127.0.0.1', port: 5000 };
  }
}

function isPortOpen(hostname, port) {
  return new Promise((resolve) => {
    const socket = net.createConnection({ host: hostname, port });

    socket.setTimeout(1000);
    socket.once('connect', () => {
      socket.end();
      resolve(true);
    });
    socket.once('timeout', () => {
      socket.destroy();
      resolve(false);
    });
    socket.once('error', () => {
      resolve(false);
    });
  });
}

async function ensureFlaskBackend() {
  const target = parseBackendTarget(FLASK_URL);

  if (await isPortOpen(target.hostname, target.port)) {
    if (!IS_PROD) {
      console.log(`[flask] Backend already listening on ${FLASK_URL}`);
    }
    return;
  }

  if (!require('fs').existsSync(FLASK_APP_PATH)) {
    console.warn(`[flask] app.py not found at ${FLASK_APP_PATH}; proxy will remain unavailable.`);
    return;
  }

  console.log(`[flask] Starting Flask backend from ${FLASK_APP_PATH}...`);
  flaskProcess = spawn(FLASK_COMMAND, [FLASK_APP_PATH], {
    cwd: FLASK_APP_DIR,
    env: process.env,
    stdio: 'inherit',
    windowsHide: true,
  });

  flaskProcess.on('exit', (code, signal) => {
    flaskProcess = null;
    if (code !== 0 && signal !== 'SIGTERM') {
      console.error(`[flask] Backend exited unexpectedly (code: ${code}, signal: ${signal || 'none'})`);
    }
  });
}

const app = express();

// ─── Logging ────────────────────────────────────────────────────────────────
app.use(morgan(IS_PROD ? 'combined' : 'dev'));

// ─── Security headers ───────────────────────────────────────────────────────
app.use((_req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  next();
});

// ─── Static assets ──────────────────────────────────────────────────────────
app.use(
  express.static(path.join(__dirname, 'public'), {
    maxAge: IS_PROD ? '7d' : 0,
    etag: true,
  })
);

// ─── Proxies ─────────────────────────────────────────────────────────────────
// hpm v3 strips the mount path before forwarding (e.g. /api/query → /query).
// pathRewrite as a FUNCTION (not object) re-adds the prefix.
// Object form { '^/api': '/api' } is silently ignored in hpm v3.

const apiProxy = createProxyMiddleware({
  target: FLASK_URL,
  changeOrigin: true,
  selfHandleResponse: false,
  pathRewrite: (path) => '/api' + path,   // /query → /api/query
  on: {
    error: (err, _req, res) => {
      console.error('[proxy] API error:', err.message);
      if (!res.headersSent) {
        res.status(502).json({
          success: false,
          error: 'RAG backend is unreachable. Is Flask running?',
        });
      }
    },
    proxyReq: (_proxyReq, req) => {
      if (!IS_PROD) {
        console.log(`[proxy] → ${req.method} ${FLASK_URL}${req.url}`);
      }
    },
  },
});

const pdfProxy = createProxyMiddleware({
  target: FLASK_URL,
  changeOrigin: true,
  pathRewrite: (path) => '/01_preprocessing' + path,
  on: {
    error: (err, _req, res) => {
      console.error('[proxy] PDF error:', err.message);
      if (!res.headersSent) {
        res.status(502).json({ error: 'PDF service unavailable' });
      }
    },
  },
});

// Open access — no auth guard.
app.use('/api', apiProxy);
app.use('/01_preprocessing', pdfProxy);

// ─── SPA fallback ───────────────────────────────────────────────────────────
app.get('*', (_req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ─── Start ───────────────────────────────────────────────────────────────────
async function start() {
  await ensureFlaskBackend();

  app.listen(PORT, '0.0.0.0', () => {
    console.log('');
    console.log('═══════════════════════════════════════════════════════════');
    console.log('  CHiPS-RAG  –  Express UI Server');
    console.log('═══════════════════════════════════════════════════════════');
    console.log(`  UI      →  http://0.0.0.0:${PORT}`);
    console.log(`  Flask   →  ${FLASK_URL}  (proxied, open access)`);
    console.log(`  Mode    →  ${IS_PROD ? 'production' : 'development'}`);
    console.log('═══════════════════════════════════════════════════════════');
    console.log('');
  });
}

start().catch((err) => {
  console.error('[server] Failed to start:', err);
  process.exit(1);
});

process.on('SIGINT', () => {
  if (flaskProcess) {
    flaskProcess.kill('SIGINT');
  }
  process.exit(0);
});

process.on('SIGTERM', () => {
  if (flaskProcess) {
    flaskProcess.kill('SIGTERM');
  }
  process.exit(0);
});