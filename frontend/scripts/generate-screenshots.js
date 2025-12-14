const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const screenshotDir = path.join(__dirname, '../public/screenshots');

// Get all SVG files in the screenshots directory
const svgFiles = fs.readdirSync(screenshotDir).filter(file => file.endsWith('.svg'));

async function generateScreenshots() {
  console.log('📸 Generating PWA screenshots...\n');

  for (const svgFile of svgFiles) {
    const inputPath = path.join(screenshotDir, svgFile);
    const outputPath = path.join(screenshotDir, svgFile.replace('.svg', '.png'));

    try {
      await sharp(inputPath)
        .png()
        .toFile(outputPath);

      console.log(`✅ Generated: ${svgFile.replace('.svg', '.png')}`);
    } catch (error) {
      console.error(`❌ Error generating ${svgFile}:`, error.message);
    }
  }

  console.log('\n✨ Screenshot generation complete!');
}

generateScreenshots().catch(console.error);
