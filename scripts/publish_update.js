#!/usr/bin/env node
const { execSync } = require('child_process');

function run(command) {
  console.log(`$ ${command}`);
  execSync(command, { stdio: 'inherit', shell: '/bin/sh' });
}

try {
  run('git pull --rebase');
  run('npm run sync-assets');
  run('npm run optimize');
  run('npm run refactor');
  run('SKIP_ASSET_PIPELINE=1 ELEVENTY_ENV=production npm run build');
  run('git add .');
  run(`git commit -m "Deploy update: $(date +'%Y-%m-%d %H:%M')"`);
  run('git push origin main');
} catch (err) {
  console.error('Deployment failed:', err.message);
  process.exit(1);
}
