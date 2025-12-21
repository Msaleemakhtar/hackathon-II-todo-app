'use client';

import { useSession } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { useEffect, useState, useCallback } from 'react';
import dynamic from 'next/dynamic';

// Import ChatKit dynamically to avoid SSR issues with web components
const ChatKit = dynamic(
  () => import('@openai/chatkit-react').then((mod) => mod.ChatKit),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto"></div>
          <p className="text-sm text-muted-foreground">Loading ChatKit...</p>
        </div>
      </div>
    ),
  }
);

// Import useChatKit normally since it's just a hook
import { useChatKit } from '@openai/chatkit-react';

/**
 * Chat Interface Component
 * This component is only rendered when authToken is available
 *
 * Implementation based on OpenAI's official ChatKit examples:
 * https://github.com/openai/openai-chatkit-advanced-samples
 */
function ChatInterface({ authToken, session }: { authToken: string; session: any }) {
  const [threadId, setThreadId] = useState<string | null>(null);

  // Handle thread change events
  const handleThreadChange = useCallback(({ threadId: newThreadId }: { threadId?: string | null }) => {
    console.log('[ChatKit] 🔄 Thread changed:', {
      thread_id: newThreadId,
      timestamp: new Date().toISOString()
    });
    setThreadId(newThreadId ?? null);
  }, []);

  // Handle response completion
  const handleResponseEnd = useCallback(() => {
    console.log('[ChatKit] ✅ Response completed:', {
      thread_id: threadId,
      timestamp: new Date().toISOString()
    });
  }, [threadId]);

  // Handle errors
  const handleError = useCallback(({ error }: { error: Error }) => {
    console.error('[ChatKit] ❌ Error:', {
      message: error.message,
      name: error.name,
      stack: error.stack,
      timestamp: new Date().toISOString()
    });
  }, []);

  // Handle ready event
  const handleReady = useCallback(() => {
    console.log('[ChatKit] 🟢 ChatKit is ready', {
      thread_id: threadId,
      timestamp: new Date().toISOString()
    });
  }, [threadId]);

  // Handle incoming messages (for debugging)
  const handleMessage = useCallback((event: any) => {
    console.log('[ChatKit] 📨 Message event received:', {
      type: event?.type,
      role: event?.role,
      hasContent: !!event?.content,
      timestamp: new Date().toISOString()
    });
  }, []);

  // Handle stream events (for debugging)
  const handleStreamEvent = useCallback((event: any) => {
    console.log('[ChatKit] 🌊 Stream event received:', {
      event_type: typeof event,
      data: event,
      timestamp: new Date().toISOString()
    });
  }, []);

  // Add effect to check if web component is loaded
  useEffect(() => {
    console.log('🔍 Checking for openai-chatkit web component...');
    const checkWebComponent = () => {
      const element = document.querySelector('openai-chatkit');
      if (element) {
        console.log('✅ Found <openai-chatkit> element:', element);
        console.log('   Element properties:', Object.keys(element));
      } else {
        console.log('❌ <openai-chatkit> element NOT found in DOM');
      }
    };

    // Check immediately and after a delay
    checkWebComponent();
    const timer = setTimeout(checkWebComponent, 1000);
    return () => clearTimeout(timer);
  }, []);

  // Initialize ChatKit with full configuration following official examples
  const chatkit = useChatKit({
    api: {
      url: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/chatkit`,
      // For local development: empty string works
      // For production: set NEXT_PUBLIC_CHATKIT_DOMAIN_KEY in .env.local
      domainKey: process.env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY || '',
      // Custom fetch function to inject auth headers
      // IMPORTANT: Must return Response directly for SSE stream handling
      fetch: async (url: string, options?: RequestInit) => {
        console.log('[ChatKit] 📤 Request:', {
          method: options?.method || 'GET',
          url,
          hasToken: !!authToken,
        });

        // Return the fetch response directly without awaiting or processing
        // This preserves SSE stream handling by ChatKit
        return fetch(url, {
          ...options,
          headers: {
            ...options?.headers,
            'Authorization': `Bearer ${authToken}`,
            'Accept': 'text/event-stream',
          },
        });
      },
    },
    theme: {
      colorScheme: 'light',
      color: {
        grayscale: {
          hue: 220,
          tint: 6,
          shade: -4,
        },
        accent: {
          primary: '#0f172a',
          level: 1,
        },
      },
      radius: 'round',
    },
    startScreen: {
      greeting: 'How can I help you manage your tasks today?',
      prompts: [
        {
          label: 'Create a task',
          prompt: 'Add a new task to buy groceries',
        },
        {
          label: 'List my tasks',
          prompt: 'Show me all my tasks',
        },
        {
          label: 'Update a task',
          prompt: 'Update task #1',
        },
        {
          label: 'Complete a task',
          prompt: 'Mark task #1 as complete',
        },
      ],
    },
    composer: {
      placeholder: 'Ask me to create, update, or complete tasks...',
    },
    onResponseEnd: handleResponseEnd,
    onThreadChange: handleThreadChange,
    onError: handleError,
    onReady: handleReady,
    onMessage: handleMessage,
  });

  // Debug logging
  console.log('[ChatKit] 🎮 Control object created:', {
    type: typeof chatkit.control,
    isValid: typeof chatkit.control === 'object',
    keys: chatkit.control ? Object.keys(chatkit.control) : [],
    apiUrl: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/chatkit`,
    threadId: threadId,
    timestamp: new Date().toISOString()
  });

  // Check if control is valid
  const hasValidControl = chatkit && chatkit.control && typeof chatkit.control === 'object';

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <header className="border-b bg-background p-4">
        <div className="container mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">AI Task Assistant [NEW IMPLEMENTATION]</h1>
            <p className="text-sm text-muted-foreground">
              Manage your tasks through natural conversation
            </p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              {session.user?.email || session.user?.name || 'User'}
            </span>
            <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
              ChatKit v1.4.0
            </span>
          </div>
        </div>
      </header>

      {/* Debug Info */}
      <div className="bg-yellow-50 border-b border-yellow-200 p-2">
        <p className="text-xs text-yellow-800">
          🔧 Debug: ChatKit control type: {typeof chatkit.control} |
          Has control: {chatkit.control ? 'YES' : 'NO'} |
          Valid: {hasValidControl ? 'YES' : 'NO'} |
          Thread: {threadId || 'none'}
        </p>
      </div>

      {/* ChatKit Component - Full height container */}
      <div className="flex-1 overflow-hidden bg-white border-4 border-blue-500">
        <div className="h-full w-full bg-gray-50">
          {!hasValidControl ? (
            <div className="flex h-full items-center justify-center p-8">
              <div className="max-w-md text-center">
                <h3 className="text-lg font-semibold text-red-600 mb-2">
                  ⚠️ ChatKit Control Invalid
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  The ChatKit control object is not valid. Check browser console for errors.
                </p>
                <div className="bg-gray-100 p-4 rounded text-left">
                  <p className="text-xs font-mono">
                    Control: {JSON.stringify(chatkit.control, null, 2)}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <ChatKit control={chatkit.control} className="h-full w-full" />
          )}
        </div>
      </div>

      {/* Footer Debug */}
      <div className="bg-blue-50 border-t border-blue-200 p-2">
        <p className="text-xs text-blue-800 text-center">
          ChatKit should appear in the blue-bordered area above
        </p>
      </div>
    </div>
  );
}

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
  const [tokenLoading, setTokenLoading] = useState(true);
  const [tokenError, setTokenError] = useState<string | null>(null);

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!isPending && !session) {
      router.push('/login');
      return;
    }

    // Extract JWT token from session
    if (session) {
      // Check if JWT is available directly in session (via JWT plugin)
      if ((session as any).jwt) {
        console.log('[ChatKit] ✅ JWT found in session');
        setAuthToken((session as any).jwt);
        setTokenLoading(false);
      } else {
        // Fallback: fetch JWT from token endpoint
        console.log('[ChatKit] 🔑 Fetching JWT token from /api/auth/token');
        setTokenLoading(true);
        fetch('/api/auth/token')
          .then(res => {
            if (!res.ok) {
              console.error('[ChatKit] ❌ Token fetch failed:', res.status, res.statusText);
              throw new Error(`Token fetch failed: ${res.status}`);
            }
            return res.json();
          })
          .then(data => {
            if (data.token) {
              console.log('[ChatKit] ✅ JWT token fetched successfully');
              setAuthToken(data.token);
              setTokenError(null);
            } else {
              console.error('[ChatKit] ❌ No token in response:', data);
              throw new Error('No token in response');
            }
          })
          .catch(err => {
            console.error('Failed to fetch token:', err);
            setTokenError(err.message || 'Failed to fetch authentication token');
          })
          .finally(() => {
            setTokenLoading(false);
          });
      }
    }
  }, [session, isPending, router]);

  // Loading state - session or token
  if (isPending || tokenLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="text-muted-foreground">
            {isPending ? 'Loading chat...' : 'Fetching authentication token...'}
          </p>
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

  // Token fetch error
  if (tokenError) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="max-w-md text-center">
          <h2 className="mb-2 text-2xl font-semibold text-red-600">
            Authentication Error
          </h2>
          <p className="mb-4 text-muted-foreground">
            {tokenError}
          </p>
          <div className="flex gap-2 justify-center">
            <button
              onClick={() => window.location.reload()}
              className="rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90"
            >
              Retry
            </button>
            <button
              onClick={() => router.push('/login')}
              className="rounded-md border border-primary px-4 py-2 text-primary hover:bg-primary/10"
            >
              Go to Login
            </button>
          </div>
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

  // Render ChatInterface only when we have a valid authToken and session
  return <ChatInterface authToken={authToken} session={session} />;
}
