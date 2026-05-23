const fs = require('fs');
const path = require('path');

const skillsDir = path.join(__dirname, '..', 'src', 'process', 'resources', 'skills');
const outputFile = path.join(__dirname, '..', 'src', 'renderer', 'assets', 'skillsMap.json');

const skillsMap = {};

function scanSkillsDir(currentPath, currentSkillName = null) {
  if (!fs.existsSync(currentPath)) return;
  const entries = fs.readdirSync(currentPath, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(currentPath, entry.name);
    
    // Check if it's a SKILL.md file
    if (entry.isFile() && (entry.name === 'SKILL.md' || entry.name.endsWith('.md'))) {
      const parentDirName = path.basename(currentPath);
      // Determine the skill name. If it's directly under _builtin, it might be nested
      let skillName = currentSkillName || parentDirName;
      if (entry.name === 'SKILL.md') {
        skillName = parentDirName;
      } else {
        // e.g. some-skill.md
        skillName = entry.name.replace('.md', '');
      }

      const content = fs.readFileSync(fullPath, 'utf-8');
      skillsMap[skillName] = content;
      console.log(`Mapped skill: ${skillName}`);
    } else if (entry.isDirectory()) {
      scanSkillsDir(fullPath, entry.name);
    }
  }
}

console.log(`Scanning skills in ${skillsDir}...`);
scanSkillsDir(skillsDir);

fs.writeFileSync(outputFile, JSON.stringify(skillsMap, null, 2));
console.log(`Successfully wrote ${Object.keys(skillsMap).length} skills to ${outputFile}`);
