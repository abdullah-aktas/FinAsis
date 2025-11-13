#!/usr/bin/env node

/**
 * TradeSim 3D - Quick Start Script
 * Automatically checks dependencies and starts dev servers
 */

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

const log = {
  info: (msg) => console.log(`${colors.blue}ℹ${colors.reset} ${msg}`),
  success: (msg) => console.log(`${colors.green}✓${colors.reset} ${msg}`),
  error: (msg) => console.log(`${colors.red}✗${colors.reset} ${msg}`),
  warning: (msg) => console.log(`${colors.yellow}⚠${colors.reset} ${msg}`),
  header: (msg) => console.log(`\n${colors.bright}${colors.cyan}${msg}${colors.reset}\n`),
};

function checkCommand(command) {
  try {
    execSync(`${command} --version`, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

function checkPort(port) {
  try {
    execSync(`netstat -ano | findstr :${port}`, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

async function main() {
  log.header('🎮 TradeSim 3D - Quick Start');

  // Check Node.js
  log.info('Checking Node.js...');
  if (!checkCommand('node')) {
    log.error('Node.js not found! Please install Node.js 18+');
    process.exit(1);
  }
  const nodeVersion = execSync('node --version').toString().trim();
  log.success(`Node.js ${nodeVersion} found`);

  // Check npm
  log.info('Checking npm...');
  if (!checkCommand('npm')) {
    log.error('npm not found!');
    process.exit(1);
  }
  const npmVersion = execSync('npm --version').toString().trim();
  log.success(`npm ${npmVersion} found`);

  // Check if node_modules exists
  log.info('Checking dependencies...');
  if (!fs.existsSync(path.join(__dirname, 'node_modules'))) {
    log.warning('Dependencies not installed. Installing...');
    try {
      execSync('npm install', { stdio: 'inherit' });
      log.success('Dependencies installed');
    } catch (error) {
      log.error('Failed to install dependencies');
      process.exit(1);
    }
  } else {
    log.success('Dependencies already installed');
  }

  // Check .env file
  log.info('Checking environment configuration...');
  if (!fs.existsSync(path.join(__dirname, '.env'))) {
    log.warning('Creating .env file...');
    const envContent = `VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
`;
    fs.writeFileSync(path.join(__dirname, '.env'), envContent);
    log.success('.env file created');
  } else {
    log.success('.env file exists');
  }

  // Check if port 3000 is available
  log.info('Checking port 3000...');
  if (checkPort(3000)) {
    log.warning('Port 3000 is already in use');
    log.info('The dev server will try to use an alternative port');
  } else {
    log.success('Port 3000 is available');
  }

  // Start dev server
  log.header('🚀 Starting Development Server');
  log.info('Starting Vite dev server...');
  log.info('Frontend will be available at: http://localhost:3000');
  log.info('Press Ctrl+C to stop');
  log.info('');

  const devServer = spawn('npm', ['run', 'dev'], {
    stdio: 'inherit',
    shell: true,
  });

  devServer.on('error', (error) => {
    log.error(`Failed to start dev server: ${error.message}`);
    process.exit(1);
  });

  devServer.on('exit', (code) => {
    if (code !== 0) {
      log.error(`Dev server exited with code ${code}`);
      process.exit(code);
    }
  });

  // Handle Ctrl+C
  process.on('SIGINT', () => {
    log.info('\nShutting down...');
    devServer.kill('SIGINT');
    process.exit(0);
  });
}

main().catch((error) => {
  log.error(`Unexpected error: ${error.message}`);
  process.exit(1);
});
