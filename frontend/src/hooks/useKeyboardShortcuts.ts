import { useEffect, useCallback } from 'react';

export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  meta?: boolean;
  shift?: boolean;
  alt?: boolean;
  description: string;
  action: () => void;
}

export const useKeyboardShortcuts = (shortcuts: KeyboardShortcut[]) => {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      for (const shortcut of shortcuts) {
        const ctrlMatch = shortcut.ctrl === undefined || shortcut.ctrl === (event.ctrlKey || event.metaKey);
        const metaMatch = shortcut.meta === undefined || shortcut.meta === event.metaKey;
        const shiftMatch = shortcut.shift === undefined || shortcut.shift === event.shiftKey;
        const altMatch = shortcut.alt === undefined || shortcut.alt === event.altKey;
        const keyMatch = shortcut.key.toLowerCase() === event.key.toLowerCase();

        if (ctrlMatch && metaMatch && shiftMatch && altMatch && keyMatch) {
          event.preventDefault();
          shortcut.action();
          break;
        }
      }
    },
    [shortcuts]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);
};

// Common shortcuts for task management
export const getTaskManagementShortcuts = (handlers: {
  onSearch?: () => void;
  onNewTask?: () => void;
  onComplete?: () => void;
  onClose?: () => void;
  onDelete?: () => void;
  onHelp?: () => void;
}): KeyboardShortcut[] => {
  const shortcuts: KeyboardShortcut[] = [];

  if (handlers.onSearch) {
    shortcuts.push({
      key: 'k',
      ctrl: true,
      description: 'Search tasks',
      action: handlers.onSearch,
    });
  }

  if (handlers.onNewTask) {
    shortcuts.push({
      key: 'n',
      ctrl: true,
      description: 'Create new task',
      action: handlers.onNewTask,
    });
  }

  if (handlers.onComplete) {
    shortcuts.push({
      key: 'Enter',
      ctrl: true,
      description: 'Complete/uncomplete task',
      action: handlers.onComplete,
    });
  }

  if (handlers.onClose) {
    shortcuts.push({
      key: 'Escape',
      description: 'Close dialog/modal',
      action: handlers.onClose,
    });
  }

  if (handlers.onDelete) {
    shortcuts.push({
      key: 'Backspace',
      ctrl: true,
      shift: true,
      description: 'Delete task',
      action: handlers.onDelete,
    });
  }

  if (handlers.onHelp) {
    shortcuts.push({
      key: '?',
      shift: true,
      description: 'Show keyboard shortcuts',
      action: handlers.onHelp,
    });
  }

  return shortcuts;
};

// Format shortcut for display (e.g., "Ctrl+K" or "Cmd+K" on Mac)
export const formatShortcut = (shortcut: KeyboardShortcut): string => {
  const parts: string[] = [];
  const isMac = typeof navigator !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0;

  if (shortcut.ctrl) {
    parts.push(isMac ? 'Cmd' : 'Ctrl');
  }
  if (shortcut.meta && !shortcut.ctrl) {
    parts.push('Cmd');
  }
  if (shortcut.shift) {
    parts.push('Shift');
  }
  if (shortcut.alt) {
    parts.push('Alt');
  }

  // Format key name
  let keyName = shortcut.key;
  if (keyName === 'Escape') keyName = 'Esc';
  if (keyName === 'Backspace') keyName = 'Backspace';
  parts.push(keyName.charAt(0).toUpperCase() + keyName.slice(1));

  return parts.join('+');
};
