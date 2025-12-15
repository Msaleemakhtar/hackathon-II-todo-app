# PWA Screenshots (T081, FR-024)

This directory contains screenshots for the Progressive Web App installation experience.

## Required Screenshots

### Desktop Screenshots (Wide Form Factor)
- **desktop-1.png** (1280x720) - Main task dashboard view showing task list and features

### Mobile Screenshots (Narrow Form Factor)
- **mobile-1.png** (750x1334) - Mobile task list view

## Purpose

Screenshots are displayed in:
1. **Installation prompts** on supported browsers
2. **App stores** if you publish the PWA
3. **Chrome Web Store** listing if applicable

## Design Guidelines

1. **Show Real Features**: Capture actual functionality, not marketing materials
2. **Clean Data**: Use sample/demo tasks that showcase features without sensitive information
3. **High Quality**: Use high-resolution displays and export at 2x or 3x scale if possible
4. **Good Lighting**: Ensure the UI is well-lit and colors are accurate
5. **Contextual**: Show the app being used in realistic scenarios

## What to Capture

### Desktop Screenshot Should Show:
- Task list with multiple tasks
- Sidebar navigation (if present)
- Search/filter functionality
- Task creation form or modal
- Any unique features (reminders, tags, categories)

### Mobile Screenshot Should Show:
- Mobile-optimized task list
- Touch-friendly UI elements
- Key actions (add task, complete task)
- Mobile-specific features (swipe actions, pull-to-refresh)

## Taking Screenshots

1. **Prepare the App**:
   - Add sample tasks with varying priorities and statuses
   - Open relevant views/modals to show features
   - Ensure UI is in a clean, polished state

2. **Capture**:
   - **Desktop**: Use Chrome DevTools device toolbar set to 1280x720
   - **Mobile**: Use real device or emulator at 750x1334
   - Use browser's built-in screenshot tool for pixel-perfect captures

3. **Edit** (if needed):
   - Crop to exact dimensions
   - Remove any sensitive information
   - Optimize file size (PNG format, reasonable compression)

## Tools

- **Chrome DevTools** - Built-in screenshot capture
- **Firefox Developer Tools** - Screenshot command
- **Third-party**: LightShot, Greenshot, or macOS built-in screenshot tools

## Placeholder Screenshots

Until real screenshots are created, the manifest will still work but the installation UI may not display screenshots. This is acceptable for development but should be addressed before production deployment.

## Testing

After adding screenshots:
1. Open Chrome DevTools > Application > Manifest
2. Verify screenshots appear under "Screenshots" section
3. Test installation flow on supported devices
4. Check that screenshots display correctly in install prompts

## References

- [PWA Screenshots Best Practices](https://web.dev/app-like-pwas/)
- [Chrome Install Criteria](https://web.dev/install-criteria/)
