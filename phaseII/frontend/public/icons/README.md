# PWA Icons (T079, FR-024)

This directory contains the Progressive Web App icons for various device sizes and resolutions.

## Required Icons

The following icon sizes are required for optimal PWA installation experience across devices:

### App Icons
- **icon-72x72.png** - Small mobile icon
- **icon-96x96.png** - Medium mobile icon
- **icon-128x128.png** - Large mobile icon
- **icon-144x144.png** - Windows tile icon
- **icon-152x152.png** - iOS iPad icon
- **icon-192x192.png** - Standard Android icon (maskable)
- **icon-384x384.png** - Large Android icon
- **icon-512x512.png** - Splash screen icon (maskable)

### Shortcut Icons
- **shortcut-new-task.png** (96x96) - Icon for "New Task" shortcut
- **shortcut-search.png** (96x96) - Icon for "Search Tasks" shortcut

## Design Guidelines

1. **Maskable Icons**: Icons with `purpose: "maskable any"` should have important content within the safe zone (80% of the icon size)
2. **Color Scheme**: Use the app's theme color (#3b82f6 - blue) as the primary color
3. **Background**: White or transparent background depending on the context
4. **Style**: Modern, clean, minimalist design that represents task management
5. **Content**: Consider using a checkmark, checkbox, or list icon as the primary symbol

## Creating Icons

You can use tools like:
- **Figma** or **Adobe Illustrator** for design
- **PWA Asset Generator** (https://github.com/elegantapp/pwa-asset-generator) to generate all sizes from a single SVG
- **ImageMagick** to resize a base icon to all required sizes

### Quick Generation with ImageMagick

If you have a high-resolution base icon (e.g., 1024x1024), you can generate all sizes:

```bash
# From the icons directory
for size in 72 96 128 144 152 192 384 512; do
  convert base-icon.png -resize ${size}x${size} icon-${size}x${size}.png
done
```

## Placeholder Icons

Until proper icons are created, you can use placeholder icons or the app's favicon scaled to different sizes. The manifest will still work with missing icons, but the installation experience will be degraded.

## Testing

After adding icons, test the PWA installation on:
1. **Chrome (Desktop)** - Check install prompt and app icon
2. **Chrome (Android)** - Verify home screen icon and splash screen
3. **Safari (iOS)** - Test add to home screen functionality
4. **Edge (Windows)** - Validate Windows tile appearance

## References

- [Web.dev PWA Icons Guide](https://web.dev/add-manifest/)
- [Maskable Icon Spec](https://web.dev/maskable-icon/)
- [PWA Icon Generator](https://www.pwabuilder.com/imageGenerator)
