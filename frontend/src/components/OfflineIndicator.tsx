'use client';

import { useEffect, useState } from 'react';
import { WifiOff, Cloud, CloudOff } from 'lucide-react';
import { isOnline, addOnlineListener, getPendingChangesCount, addSyncListener } from '@/lib/offline';

export const OfflineIndicator = () => {
  const [online, setOnline] = useState(true);
  const [pendingCount, setPendingCount] = useState(0);
  const [justSynced, setJustSynced] = useState(false);

  useEffect(() => {
    // Set initial online status
    setOnline(isOnline());

    // Get initial pending changes count
    getPendingChangesCount().then(setPendingCount);

    // Listen for online/offline events
    const removeOnlineListener = addOnlineListener((status) => {
      setOnline(status);

      if (status) {
        // When coming back online, update pending count
        getPendingChangesCount().then(setPendingCount);
      }
    });

    // Listen for sync completion
    const removeSyncListener = addSyncListener((data) => {
      console.log('Sync complete:', data.count, 'items synced');
      setPendingCount(0);
      setJustSynced(true);

      // Clear sync notification after 3 seconds
      setTimeout(() => {
        setJustSynced(false);
      }, 3000);
    });

    return () => {
      removeOnlineListener();
      removeSyncListener();
    };
  }, []);

  // Don't show anything if online and no pending changes
  if (online && pendingCount === 0 && !justSynced) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {!online && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg shadow-lg px-4 py-3 flex items-center gap-3 animate-in slide-in-from-bottom-4">
          <WifiOff className="h-5 w-5 text-amber-600 flex-shrink-0" />
          <div>
            <p className="text-sm font-semibold text-amber-900">You&apos;re offline</p>
            <p className="text-xs text-amber-700">
              {pendingCount > 0
                ? `${pendingCount} change${pendingCount !== 1 ? 's' : ''} will sync when online`
                : 'Changes will sync when you reconnect'}
            </p>
          </div>
        </div>
      )}

      {online && pendingCount > 0 && !justSynced && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg shadow-lg px-4 py-3 flex items-center gap-3 animate-in slide-in-from-bottom-4">
          <CloudOff className="h-5 w-5 text-blue-600 flex-shrink-0 animate-pulse" />
          <div>
            <p className="text-sm font-semibold text-blue-900">Syncing changes...</p>
            <p className="text-xs text-blue-700">
              {pendingCount} change{pendingCount !== 1 ? 's' : ''} pending
            </p>
          </div>
        </div>
      )}

      {justSynced && (
        <div className="bg-green-50 border border-green-200 rounded-lg shadow-lg px-4 py-3 flex items-center gap-3 animate-in slide-in-from-bottom-4">
          <Cloud className="h-5 w-5 text-green-600 flex-shrink-0" />
          <div>
            <p className="text-sm font-semibold text-green-900">All changes synced!</p>
            <p className="text-xs text-green-700">You&apos;re back online</p>
          </div>
        </div>
      )}
    </div>
  );
};
