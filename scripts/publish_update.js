#!/usr/bin/env node
const { execSync } = require('child_process');

const BRANCH = 'main';
const REMOTE = 'origin';

// Runs a command and fails the whole script on error.
function run(command) {
  console.log(`$ ${command}`);
  execSync(command, { stdio: 'inherit', shell: '/bin/sh' });
}

// Runs a command but does NOT fail the script if it exits non-zero.
// Useful for `git commit` when there is nothing to commit.
function runAllowFail(command) {
  console.log(`$ ${command}`);
  try {
    execSync(command, { stdio: 'inherit', shell: '/bin/sh' });
    return true;
  } catch (err) {
    console.warn(`(skipped) command exited non-zero: ${command}`);
    return false;
  }
}

// Returns true if there are staged or unstaged changes in the working tree.
function hasChanges() {
  const output = execSync('git status --porcelain', { encoding: 'utf8' });
  return output.trim().length > 0;
}

try {
  // 1. Generate/refresh assets before committing.
  run('npm run sync-assets');
  run('npm run optimize');
  run('npm run refactor');
  run('SKIP_ASSET_PIPELINE=1 ELEVENTY_ENV=production npm run build');

  // 2. Commit local changes FIRST so the working tree is clean.
  //    rebase refuses to run while there are uncommitted changes.
  if (hasChanges()) {
    run('git add .');
    runAllowFail(`git commit -m "Deploy update: $(date +'%Y-%m-%d %H:%M')"`);
  } else {
    console.log('No local changes to commit.');
  }

  // 3. Rebase onto the latest remote. Specify remote + branch explicitly
  //    because the local branch may not have upstream tracking configured.
  run(`git pull --rebase ${REMOTE} ${BRANCH}`);

  // 4. Push the result and set upstream tracking (-u) so future
  //    plain `git pull` / `git push` work without extra arguments.
  run(`git push -u ${REMOTE} ${BRANCH}`);

  console.log('\n✅ Deployed successfully.');
} catch (err) {
  console.error('Deployment failed:', err.message);
  process.exit(1);
}
