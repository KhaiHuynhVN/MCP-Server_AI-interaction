import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { ScanConfig } from './types.js';
import { ProjectScanner } from './scanner.js';
import { filterOutput } from './filter.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  const args = process.argv.slice(2);

  const config: ScanConfig = {
    path: '',
    framework: 'angular',
    depth: 10,
    include: ['**/*.ts', '**/*.tsx', '**/*.js', '**/*.jsx', '**/*.mts', '**/*.mjs'],
    exclude: [],
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--path':
      case '-p':
        config.path = args[++i];
        break;
      case '--framework':
      case '-f':
        config.framework = args[++i] as 'angular' | 'react' | 'generic';
        break;
      case '--depth':
      case '-d':
        config.depth = parseInt(args[++i], 10);
        break;
      case '--include':
      case '-i':
        config.include = args[++i].split(',');
        break;
      case '--exclude':
      case '-e':
        config.exclude = args[++i].split(',');
        break;
      case '--query':
      case '-q':
        config.query = args[++i];
        break;
    }
  }

  if (!config.path) {
    console.error('Usage: npx tsx scan.ts --path <project-path> [options]');
    console.error('Options:');
    console.error('  --path, -p      Project path to scan (required)');
    console.error('  --framework, -f Framework: angular|react|generic (default: angular)');
    console.error('  --query, -q     Filter output by class/file/directory name');
    console.error('  --include, -i   File patterns to include (comma-separated)');
    console.error('  --exclude, -e   File patterns to exclude (comma-separated)');
    console.error('');
    console.error('Examples:');
    console.error('  npx tsx scan.ts --path "C:/project/src" --framework angular');
    console.error('  npx tsx scan.ts --path "C:/project/src" --query "SalonService"');
    console.error('  npx tsx scan.ts --path "C:/project/src" --query "src/app/api"');
    process.exit(1);
  }

  if (!fs.existsSync(config.path)) {
    console.error(`Path does not exist: ${config.path}`);
    process.exit(1);
  }

  console.log(`Scanning: ${config.path}`);
  console.log(`Framework: ${config.framework}`);
  if (config.query) console.log(`Query: ${config.query}`);

  const scanner = new ProjectScanner(config);
  let output = await scanner.scan();

  if (config.query) {
    output = filterOutput(output, config.query);
  }

  const outputPath = path.join(__dirname, config.query ? 'output-query.json' : 'output.json');
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
  console.log(`Output written to: ${outputPath}`);
}

main().catch(console.error);
