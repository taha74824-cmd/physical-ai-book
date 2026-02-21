// start-book.mjs — runs from project root, starts Docusaurus from book/
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { spawn } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
// Support being called from book/ (cwd field) or project root
const projectRoot = __dirname.endsWith('book') ? dirname(__dirname) : __dirname;
const bookDir = join(projectRoot, 'book');
const docusaurusBin = join(bookDir, 'node_modules', '@docusaurus', 'core', 'bin', 'docusaurus.mjs');

const child = spawn(process.execPath, [docusaurusBin, 'start', '--host', 'localhost', '--no-open'], {
  cwd: bookDir,
  stdio: 'inherit',
  env: process.env,
});

child.on('exit', (code) => process.exit(code ?? 0));
child.on('error', (err) => { console.error(err); process.exit(1); });

