import { useAuthContext } from '@/contexts/AuthContext';

/**
 * Hook to access authentication state from centralized AuthContext
 * This replaces the previous implementation that called useSession directly,
 * eliminating multiple useSession() calls per page navigation
 */
export function useAuth() {
  return useAuthContext();
}
