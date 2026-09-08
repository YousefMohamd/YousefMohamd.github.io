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
  // This script ONLY publishes the changes that already exist in the working
  // tree. It intentionally does NOT run any asset pipeline step
  // (sync-assets / optimize / refactor / build), so nothing is regenerated,
  // overwritten, or deleted. It just commits what you changed and pushes it.

  if (!hasChanges()) {
    console.log('No local changes to publish. Nothing to do.');
    process.exit(0);
  }

  // 1. Stage and commit the existing changes.
  run('git add .');
  runAllowFail(`git commit -m "Update: $(date +'%Y-%m-%d %H:%M')"`);

  // 2. Rebase onto the latest remote (explicit remote + branch in case the
  //    local branch has no upstream tracking configured).
  run(`git pull --rebase ${REMOTE} ${BRANCH}`);

  // 3. Push the result and set upstream tracking (-u) for future pulls/pushes.
  run(`git push -u ${REMOTE} ${BRANCH}`);

  console.log('\n✅ Changes published successfully.');
} catch (err) {
  console.error('Publish failed:', err.message);
  process.exit(1);
}
