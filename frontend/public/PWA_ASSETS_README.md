# PWA Assets Documentation

This document describes the generated Progressive Web App (PWA) assets for the Todo App.

## Generated Assets

### Icons (`/public/icons/`)

All icon sizes have been generated from a base SVG design (`icon.svg`) featuring a clipboard with checkmarks in the app's blue theme.

#### PWA Icons
- `icon-72x72.png` - 72×72 pixels
- `icon-96x96.png` - 96×96 pixels
- `icon-128x128.png` - 128×128 pixels
- `icon-144x144.png` - 144×144 pixels
- `icon-152x152.png` - 152×152 pixels
- `icon-192x192.png` - 192×192 pixels (minimum recommended for PWA)
- `icon-384x384.png` - 384×384 pixels
- `icon-512x512.png` - 512×512 pixels (recommended for high-res displays)

#### Additional Icons
- `apple-touch-icon.png` - 180×180 pixels (for iOS home screen)
- `favicon-32x32.png` - 32×32 pixels (browser favicon)
- `favicon-16x16.png` - 16×16 pixels (browser favicon)

### Screenshots (`/public/screenshots/`)

Two app screenshots have been generated to showcase the PWA in the installation prompt:

- `screenshot-1.png` - Main task list view showing active and completed tasks
- `screenshot-2.png` - Task creation form with priority selection and tags

Both screenshots are in mobile format (1170×2532 pixels) optimized for PWA installation prompts.

## Usage in Web App Manifest

These assets are referenced in `/src/app/manifest.ts`:

```typescript
export default function manifest() {
  return {
    name: 'Todo App',
    short_name: 'Todo',
    description: 'A modern todo list application',
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#3B82F6',
    icons: [
      {
        src: '/icons/icon-192x192.png',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: '/icons/icon-512x512.png',
        sizes: '512x512',
        type: 'image/png',
      },
    ],
    screenshots: [
      {
        src: '/screenshots/screenshot-1.png',
        sizes: '1170x2532',
        type: 'image/png',
        form_factor: 'narrow',
      },
      {
        src: '/screenshots/screenshot-2.png',
        sizes: '1170x2532',
        type: 'image/png',
        form_factor: 'narrow',
      },
    ],
  }
}
```

## Regenerating Assets

If you need to regenerate the assets (e.g., after updating the base SVG design):

### Regenerate Icons Only
```bash
bun run generate:icons
```

### Regenerate Screenshots Only
```bash
bun run generate:screenshots
```

### Regenerate All PWA Assets
```bash
bun run generate:pwa-assets
```

## Customization

### Updating the Icon Design

1. Edit `/public/icons/icon.svg` with your preferred design
2. Run `bun run generate:icons` to regenerate all PNG sizes
3. The design uses a blue gradient (#3B82F6 to #2563EB) - update the gradient colors to match your brand

### Creating Real Screenshots

The current screenshots are SVG-based placeholders. For production, you should:

1. Run your app locally or in a staging environment
2. Use browser dev tools (mobile view) to capture real screenshots
3. Recommended sizes:
   - Mobile: 1170×2532 pixels (narrow form factor)
   - Desktop: 2560×1440 pixels (wide form factor)
4. Replace `screenshot-1.svg` and `screenshot-2.svg` with your captures
5. Run `bun run generate:screenshots` to convert to PNG

## Browser Support

These assets support:
- ✅ Chrome/Edge (PWA installation)
- ✅ Safari (iOS home screen icons)
- ✅ Firefox (PWA support)
- ✅ Samsung Internet (PWA support)

## File Structure

```
frontend/public/
├── icons/
│   ├── icon.svg (source file)
│   ├── icon-*.png (generated PWA icons)
│   ├── apple-touch-icon.png
│   └── favicon-*.png
├── screenshots/
│   ├── screenshot-1.svg (source file)
│   ├── screenshot-1.png (generated)
│   ├── screenshot-2.svg (source file)
│   └── screenshot-2.png (generated)
└── PWA_ASSETS_README.md (this file)
```

## Notes

- All PNG files are automatically generated from SVG sources
- Don't edit PNG files directly - they will be overwritten
- The `sharp` library is used for high-quality image conversion
- SVG sources are kept for easy regeneration and version control
