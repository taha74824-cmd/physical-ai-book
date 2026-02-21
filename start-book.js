// Helper script: changes to book/ directory and starts Docusaurus
process.chdir(__dirname + '/book');
// Use dynamic import for ESM module
import('./book/node_modules/@docusaurus/core/bin/docusaurus.mjs');
