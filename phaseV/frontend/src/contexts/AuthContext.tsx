'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useSession } from '@/lib/auth';
import { BetterAuthUser } from '@/types/auth.d';

// Define UserProfile interface
interface UserProfile {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: UserProfile | null;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { data: session, isPending } = useSession();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isPending) {
      setLoading(true);
      return;
    }

    if (session && session.user) {
      // Transform the Better Auth session user to our UserProfile interface
      const userProfile: UserProfile = {
        id: session.user.id,
        email: session.user.email || '',
        name: session.user.name || session.user.email || 'User',
      };
      setUser(userProfile);
    } else {
      setUser(null);
    }

    setLoading(false);
  }, [session, isPending]);

  return (
    <AuthContext.Provider value={{ user, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
}
