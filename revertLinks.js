const fs = require('fs');
const path = require('path');

const walkSync = function(dir, filelist) {
  const files = fs.readdirSync(dir);
  filelist = filelist || [];
  files.forEach(function(file) {
    if (fs.statSync(path.join(dir, file)).isDirectory()) {
      filelist = walkSync(path.join(dir, file), filelist);
    }
    else {
      filelist.push(path.join(dir, file));
    }
  });
  return filelist;
};

const files = walkSync('./frontend/src').filter(f => f.endsWith('.ts') || f.endsWith('.tsx'));

let changedFiles = 0;
for (const file of files) {
  let content = fs.readFileSync(file, 'utf8');
  let originalContent = content;
  
  content = content.replace(/github\.com\/iOfficeAI\/SalomoneUI/g, 'github.com/iOfficeAI/AionUi');
  content = content.replace(/skills\.salomoneui\.com/g, 'skills.aionui.com');
  content = content.replace(/api\.salomoneui\.com/g, 'api.aionui.com');
  content = content.replace(/https:\/\/www\.salomoneui\.com/g, 'https://www.aionui.com');
  content = content.replace(/'HTTP-Referer': 'https:\/\/salomoneui\.com'/g, "'HTTP-Referer': 'https://aionui.com'");
  
  if (content !== originalContent) {
    fs.writeFileSync(file, content, 'utf8');
    changedFiles++;
    console.log('Fixed:', file);
  }
}
console.log(`Reverted external links in ${changedFiles} files.`);
