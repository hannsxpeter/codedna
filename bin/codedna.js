#!/usr/bin/env node
'use strict';

// Installs the codedna skill into supported coding-agent skill directories.
// Thin Node wrapper around install.sh so `npx @hxp-tools/codedna` works.

const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const INSTALLER = path.join(ROOT, 'install.sh');
const PKG = require('../package.json');

const COLORS = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  red: '\x1b[31m',
};

function c(color, text) {
  return COLORS[color] + text + COLORS.reset;
}

function usage() {
  console.log(`
${c('bold', 'codedna')} ${c('dim', 'v' + PKG.version)}
Fingerprint a codebase so AI contributions match the author.

${c('bold', 'Usage')}
  npx @hxp-tools/codedna@latest [all|claude|codex|cursor|windsurf]
  npx @hxp-tools/codedna@latest --help

${c('bold', 'Targets')}
  all        Install every registry-supported target (default)
  claude     Claude Code  (~/.claude/skills/codedna)
  codex      Codex        (~/.codex/skills/codedna)
  cursor     Cursor       (~/.cursor/skills/codedna)
  windsurf   Windsurf     (~/.codeium/windsurf/skills/codedna)

${c('bold', 'After install')}
  Restart your coding agent, then ask:
    build the codedna for this repo

${c('bold', 'Requirements')}
  Python 3.9+ on a POSIX host. Windows is not supported.
`);
}

function main(argv) {
  const args = argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    usage();
    return 0;
  }
  if (args.includes('--version') || args.includes('-v')) {
    console.log(PKG.version);
    return 0;
  }

  if (process.platform === 'win32') {
    console.error(c('red', 'codedna does not support Windows.'));
    console.error('Install from the GitHub release tarball on a POSIX host instead.');
    return 2;
  }

  if (!fs.existsSync(INSTALLER)) {
    console.error(c('red', 'install.sh missing from package.'));
    return 2;
  }

  const target = args[0] || 'all';
  console.log(c('cyan', 'codedna') + ' ' + c('dim', 'v' + PKG.version));
  console.log(c('dim', 'Installing skill into: ' + target));
  console.log('');

  const result = spawnSync('sh', [INSTALLER, target], {
    cwd: ROOT,
    stdio: 'inherit',
    env: process.env,
  });

  if (result.error) {
    console.error(c('red', String(result.error.message || result.error)));
    return 1;
  }
  if (result.status === 0) {
    console.log('');
    console.log(c('green', 'Next: restart your agent, then ask it to build the codedna.'));
    console.log(c('dim', 'Docs: ' + (PKG.homepage || 'https://github.com/hannsxpeter/codedna')));
  }
  return result.status == null ? 1 : result.status;
}

process.exitCode = main(process.argv);
