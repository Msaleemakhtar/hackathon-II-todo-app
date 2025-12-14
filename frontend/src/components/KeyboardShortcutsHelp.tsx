'use client';

import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { KeyboardShortcut, formatShortcut } from '@/hooks/useKeyboardShortcuts';

interface KeyboardShortcutsHelpProps {
  isOpen: boolean;
  onClose: () => void;
  shortcuts: KeyboardShortcut[];
}

export const KeyboardShortcutsHelp: React.FC<KeyboardShortcutsHelpProps> = ({
  isOpen,
  onClose,
  shortcuts,
}) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl" aria-describedby="keyboard-shortcuts-description">
        <DialogHeader>
          <DialogTitle>Keyboard Shortcuts</DialogTitle>
          <DialogDescription id="keyboard-shortcuts-description">
            Use these shortcuts to manage tasks more efficiently
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="grid gap-3">
            {shortcuts.map((shortcut, index) => (
              <div
                key={index}
                className="flex items-center justify-between py-2 px-3 rounded-md hover:bg-muted/50 transition-colors"
              >
                <span className="text-sm text-muted-foreground">
                  {shortcut.description}
                </span>
                <kbd className="px-3 py-1.5 text-xs font-semibold text-foreground bg-muted border border-border rounded-md shadow-sm">
                  {formatShortcut(shortcut)}
                </kbd>
              </div>
            ))}
          </div>
          <div className="pt-4 border-t border-border">
            <p className="text-xs text-muted-foreground text-center">
              Press <kbd className="px-2 py-1 text-xs bg-muted border border-border rounded">Shift+?</kbd> to toggle this help menu
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
