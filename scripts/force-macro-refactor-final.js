const fs = require('fs');
const path = require('path');

const projectsDir = path.join(__dirname, '..', 'projects');
const optimizedDir = path.join(__dirname, '..', 'img', 'optimized', 'projects');

// Create the optimized directory if it doesn't exist
if (!fs.existsSync(optimizedDir)) {
  fs.mkdirSync(optimizedDir, { recursive: true });
  console.log(`Created optimized directory: ${optimizedDir}`);
}

function processFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');

  // Replace the old macro with the new optimized-picture-macro
  content = content.replace(
    /{% from "picture-macro.njk" import renderPicture %}/g,
    '{% from "optimized-picture-macro.njk" import renderOptimizedImage %}'
  );

  // Replace all instances of renderPicture with renderOptimizedImage
  content = content.replace(
    /renderPicture\(([^)]+)\)/g,
    'renderOptimizedImage($1)'
  );

  // Update the image paths to point to the optimized directory
  content = content.replace(
    /\/img\/projects\//g,
    '/img/optimized/projects/'
  );

  // Replace .jpg and .png with .webp where appropriate
  content = content.replace(
    /(\/img\/optimized\/projects\/[^"]+)\.(jpg|png)/g,
    '$1.webp'
  );

  fs.writeFileSync(filePath, content, 'utf8');
  console.log(`Processed: ${filePath}`);
}

function processDirectory(directory) {
  if (!fs.existsSync(directory)) {
    console.log(`Directory does not exist: ${directory}`);
    return;
  }

  const files = fs.readdirSync(directory);

  files.forEach(file => {
    const filePath = path.join(directory, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      processDirectory(filePath);
    } else if (file.endsWith('.njk') || file.endsWith('.md')) {
      processFile(filePath);
    }
  });
}

// Process the projects directory
processDirectory(projectsDir);

// Process the optimized directory
processDirectory(optimizedDir);

console.log('Macro refactoring completed successfully.');
