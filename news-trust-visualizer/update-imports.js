const fs = require('fs');
const path = require('path');

// Directory containing UI components
const uiDir = path.join(__dirname, 'src', 'components', 'ui');
const componentsDir = path.join(__dirname, 'src', 'components');
const pagesDir = path.join(__dirname, 'src', 'pages');

// Function to update imports in a file
function updateImports(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Check if the file imports from @/lib/utils
    if (content.includes('import { cn } from "@/lib/utils"') || 
        content.includes("import { cn } from '@/lib/utils'")) {
      
      // Calculate relative path to utils.js
      let relativePath;
      if (filePath.includes('components/ui/')) {
        relativePath = '../../../utils.js';
      } else if (filePath.includes('components/')) {
        relativePath = '../utils.js';
      } else if (filePath.includes('pages/')) {
        relativePath = '../utils.js';
      } else {
        relativePath = './utils.js';
      }
      
      // Replace the import statement
      content = content.replace(
        /import\s+{\s*cn\s*}\s+from\s+["']@\/lib\/utils["'];?/g, 
        `import { cn } from "${relativePath}";`
      );
      
      // Write the updated content back to the file
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`Updated imports in ${filePath}`);
    }
  } catch (error) {
    console.error(`Error updating ${filePath}:`, error);
  }
}

// Process all TypeScript and TSX files in the UI directory
function processDirectory(dir) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      processDirectory(filePath);
    } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
      updateImports(filePath);
    }
  });
}

// Process all directories
processDirectory(uiDir);
processDirectory(componentsDir);
processDirectory(pagesDir);

console.log('Import updates completed!');
