const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const sizes = [72, 96, 128, 144, 152, 192, 384, 512];
const inputSvg = path.join(__dirname, '../public/icons/icon.svg');
const outputDir = path.join(__dirname, '../public/icons');

// Ensure output directory exists
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Generate PNG icons for each size
async function generateIcons() {
  console.log('🎨 Generating PWA icons...\n');

  for (const size of sizes) {
    const outputPath = path.join(outputDir, `icon-${size}x${size}.png`);

    try {
      await sharp(inputSvg)
        .resize(size, size)
        .png()
        .toFile(outputPath);

      console.log(`✅ Generated: icon-${size}x${size}.png`);
    } catch (error) {
      console.error(`❌ Error generating icon-${size}x${size}.png:`, error.message);
    }
  }

  // Also create apple-touch-icon.png (180x180)
  try {
    await sharp(inputSvg)
      .resize(180, 180)
      .png()
      .toFile(path.join(outputDir, 'apple-touch-icon.png'));
    console.log('✅ Generated: apple-touch-icon.png');
  } catch (error) {
    console.error('❌ Error generating apple-touch-icon.png:', error.message);
  }

  // Create favicon.ico (32x32)
  try {
    await sharp(inputSvg)
      .resize(32, 32)
      .png()
      .toFile(path.join(outputDir, 'favicon-32x32.png'));
    console.log('✅ Generated: favicon-32x32.png');
  } catch (error) {
    console.error('❌ Error generating favicon-32x32.png:', error.message);
  }

  // Create favicon.ico (16x16)
  try {
    await sharp(inputSvg)
      .resize(16, 16)
      .png()
      .toFile(path.join(outputDir, 'favicon-16x16.png'));
    console.log('✅ Generated: favicon-16x16.png');
  } catch (error) {
    console.error('❌ Error generating favicon-16x16.png:', error.message);
  }

  console.log('\n✨ Icon generation complete!');
}

generateIcons().catch(console.error);
