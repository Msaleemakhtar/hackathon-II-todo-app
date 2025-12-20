'use client';

import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useSession } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

/**
 * Chat Page - ChatKit Integration
 *
 * This page integrates OpenAI's ChatKit component with Better Auth
 * for AI-powered task management through natural conversation.
 *
 * Features:
 * - Better Auth JWT authentication
 * - ChatKit.js frontend component
 * - Backend adapter at /chatkit endpoint
 * - Conversation persistence with thread IDs
 */
export default function ChatPage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const [authToken, setAuthToken] = useState<string | null>(null);

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!isPending && !session) {
      router.push('/login');
      return;
    }

    // Extract JWT token from session
    // Better Auth stores the token in the session object
    if (session) {
      // The token might be in different places depending on Better Auth configuration
      // Common locations: session.token, session.jwt, or need to call getToken()
      const token = (session as any).token || (session as any).jwt;
      if (token) {
        setAuthToken(token);
      } else {
        // If token is not directly available, we might need to fetch it
        // For now, we'll try to get it from localStorage or cookies
        console.warn('JWT token not found in session, checking localStorage');
        const storedToken = localStorage.getItem('auth-token');
        if (storedToken) {
          setAuthToken(storedToken);
        }
      }
    }
  }, [session, isPending, router]);

  // Loading state
  if (isPending) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="text-muted-foreground">Loading chat...</p>
        </div>
      </div>
    );
  }

  // Not authenticated
  if (!session) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <h2 className="mb-2 text-2xl font-semibold">Authentication Required</h2>
          <p className="text-muted-foreground">
            Please log in to access the AI chat assistant
          </p>
        </div>
      </div>
    );
  }

  // No token available
  if (!authToken) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="max-w-md text-center">
          <h2 className="mb-2 text-2xl font-semibold text-red-600">
            Authentication Token Missing
          </h2>
          <p className="mb-4 text-muted-foreground">
            Unable to retrieve authentication token. Please try logging out and logging in again.
          </p>
          <button
            onClick={() => router.push('/login')}
            className="rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  // Initialize ChatKit control
  const control = useChatKit({
    options: {
      apiUrl: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/chatkit`,
      authToken,
    },
    handlers: {
      onError: (error) => {
        console.error('ChatKit error:', error);
        alert(`Chat error: ${error.message || 'An error occurred'}`);
      },
      onResponseEnd: (response) => {
        console.log('Response ended:', response);
      },
      onThreadChange: (thread) => {
        console.log('Thread changed:', thread);
      },
    },
  });

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <header className="border-b bg-background p-4">
        <div className="container mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">AI Task Assistant</h1>
            <p className="text-sm text-muted-foreground">
              Manage your tasks through natural conversation
            </p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              {session.user?.email || session.user?.name || 'User'}
            </span>
          </div>
        </div>
      </header>

      {/* ChatKit Component */}
      <div className="flex-1 overflow-hidden">
        <ChatKit control={control} className="h-full w-full" />
      </div>

      {/* Helper Text */}
      <div className="border-t bg-muted/50 p-3">
        <div className="container mx-auto">
          <p className="text-center text-xs text-muted-foreground">
            💡 Try: "Add task to buy milk" • "List my tasks" • "Complete task #1" •
            "Update task #2 to 'Buy groceries'"
          </p>
        </div>
      </div>
    </div>
  );
}
