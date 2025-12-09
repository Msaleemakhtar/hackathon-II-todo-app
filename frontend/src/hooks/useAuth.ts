import { useState, useEffect } from 'react';
import { UserProfile } from '@/types';

export function useAuth() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real application, you would fetch the user from an API
    // or from a token stored in localStorage/sessionStorage.
    const mockUser: UserProfile = {
      id: '1',
      email: 'user@example.com',
      name: 'Test User',
    };
    setUser(mockUser);
    setLoading(false);
  }, []);

  return { user, loading };
}
