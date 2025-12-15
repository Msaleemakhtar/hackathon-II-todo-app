/**
 * PWA Manifest Configuration (T076, FR-024)
 *
 * Defines the Progressive Web App manifest for installation on devices.
 * This enables the app to be installed on desktop and mobile devices.
 *
 * Reference: https://nextjs.org/docs/app/api-reference/file-conventions/metadata/manifest
 */

import { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Todo App - Task Management',
    short_name: 'Todo App',
    description: 'A powerful task management application with reminders, offline support, and advanced features',
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#3b82f6',
    orientation: 'portrait-primary',
    icons: [
      {
        src: '/icons/icon-72x72.png',
        sizes: '72x72',
        type: 'image/png',
        purpose: 'maskable',
      },
      {
        src: '/icons/icon-96x96.png',
        sizes: '96x96',
        type: 'image/png',
        purpose: 'maskable',
      },
      {
        src: '/icons/icon-128x128.png',
        sizes: '128x128',
        type: 'image/png',
        purpose: 'maskable',
      },
      {
        src: '/icons/icon-144x144.png',
        sizes: '144x144',
        type: 'image/png',
        purpose: 'maskable',
      },
      {
        src: '/icons/icon-152x152.png',
        sizes: '152x152',
        type: 'image/png',
        purpose: 'maskable',
      },
      {
        src: '/icons/icon-192x192.png',
        sizes: '192x192',
        type: 'image/png',
        purpose: 'maskable',
      },
      {
        src: '/icons/icon-384x384.png',
        sizes: '384x384',
        type: 'image/png',
        purpose: 'maskable',
      },
      {
        src: '/icons/icon-512x512.png',
        sizes: '512x512',
        type: 'image/png',
        purpose: 'maskable',
      },
    ],
    screenshots: [
      {
        src: '/screenshots/desktop-1.png',
        sizes: '1280x720',
        type: 'image/png',
        form_factor: 'wide',
      },
      {
        src: '/screenshots/mobile-1.png',
        sizes: '750x1334',
        type: 'image/png',
        form_factor: 'narrow',
      },
    ],
    categories: ['productivity', 'utilities'],
    shortcuts: [
      {
        name: 'New Task',
        short_name: 'New',
        description: 'Create a new task',
        url: '/?action=new-task',
        icons: [
          {
            src: '/icons/shortcut-new-task.png',
            sizes: '96x96',
            type: 'image/png',
          },
        ],
      },
      {
        name: 'Search Tasks',
        short_name: 'Search',
        description: 'Search your tasks',
        url: '/?action=search',
        icons: [
          {
            src: '/icons/shortcut-search.png',
            sizes: '96x96',
            type: 'image/png',
          },
        ],
      },
    ],
  };
}
