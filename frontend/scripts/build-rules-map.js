const fs = require('fs');
const path = require('path');

const rulesDir = path.join(__dirname, '..', 'src', 'process', 'resources', 'assistant');
const outputFile = path.join(__dirname, '..', 'src', 'renderer', 'assets', 'rulesMap.json');

const rulesMap = {};

function scanRulesDir(currentPath) {
  if (!fs.existsSync(currentPath)) return;
  const entries = fs.readdirSync(currentPath, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(currentPath, entry.name);
    
    // Check if it's a markdown file
    if (entry.isFile() && entry.name.endsWith('.md')) {
      const content = fs.readFileSync(fullPath, 'utf-8');
      rulesMap[entry.name] = content;
      console.log(`Mapped rule: ${entry.name}`);
    } else if (entry.isDirectory()) {
      scanRulesDir(fullPath);
    }
  }
}

console.log(`Scanning rules in ${rulesDir}...`);
scanRulesDir(rulesDir);

fs.writeFileSync(outputFile, JSON.stringify(rulesMap, null, 2));
console.log(`Successfully wrote ${Object.keys(rulesMap).length} rules to ${outputFile}`);
