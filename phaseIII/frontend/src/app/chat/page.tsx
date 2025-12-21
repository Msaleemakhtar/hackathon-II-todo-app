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

// localStorage key for persisting current thread
const THREAD_STORAGE_KEY = 'chatkit_current_thread_id';

/**
 * Get the stored thread ID from localStorage
 * @returns The stored thread ID or null if not found/unavailable
 */
const getStoredThreadId = (): string | null => {
  if (typeof window === 'undefined') return null;
  try {
    const storedId = localStorage.getItem(THREAD_STORAGE_KEY);
    console.log('[DEBUG] getStoredThreadId:', storedId);
    return storedId;
  } catch (error) {
    console.error('[DEBUG] Failed to get stored thread ID:', error);
    return null;
  }
};

/**
 * Store the thread ID in localStorage
 * @param threadId - The thread ID to store, or null to clear
 */
const setStoredThreadId = (threadId: string | null): void => {
  if (typeof window === 'undefined') return;
  try {
    if (threadId) {
      localStorage.setItem(THREAD_STORAGE_KEY, threadId);
      console.log('[DEBUG] Stored thread ID:', threadId);
    } else {
      localStorage.removeItem(THREAD_STORAGE_KEY);
      console.log('[DEBUG] Cleared thread ID from localStorage');
    }
  } catch (error) {
    console.error('[DEBUG] Failed to store thread ID:', error);
  }
};

/**
 * Chat Interface Component
 * This component is only rendered when authToken is available
 *
 * Implementation based on OpenAI's official ChatKit examples:
 * https://github.com/openai/openai-chatkit-advanced-samples
 */
function ChatInterface({ authToken, session }: { authToken: string; session: any }) {
  const [threadId, setThreadId] = useState<string | null>(() => {
    const initialThreadId = getStoredThreadId();
    console.log('[DEBUG] ChatInterface initialized with threadId:', initialThreadId);
    return initialThreadId;
  });
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Handle thread change events
  const handleThreadChange = useCallback(({ threadId: newThreadId }: { threadId?: string | null }) => {
    const normalizedThreadId = newThreadId ?? null;
    console.log('[DEBUG] handleThreadChange called with:', newThreadId, '-> normalized:', normalizedThreadId);

    // Only update if the thread ID actually changed
    // This prevents clearing the thread ID on errors
    if (normalizedThreadId !== threadId) {
      console.log('[DEBUG] Thread ID changed from', threadId, 'to', normalizedThreadId);
      setThreadId(normalizedThreadId);
      setStoredThreadId(normalizedThreadId);
    } else {
      console.log('[DEBUG] Thread ID unchanged, skipping update');
    }
  }, [threadId]);

  // Handle response completion
  const handleResponseEnd = useCallback(() => {
    // Response completed
  }, []);

  // Handle errors
  const handleError = useCallback(({ error }: { error: Error }) => {
    console.error('[ChatKit] Error:', error);
  }, []);

  // Handle ready event
  const handleReady = useCallback(() => {
    console.log('[DEBUG] ChatKit ready event fired');
  }, []);

  // Handle incoming messages
  const handleMessage = useCallback((event: any) => {
    // Message received
  }, []);

  // Handle stream events
  const handleStreamEvent = useCallback((event: any) => {
    // Stream event received
  }, []);

  // Monitor threadId changes
  useEffect(() => {
    console.log('[DEBUG] threadId state changed to:', threadId);
  }, [threadId]);

  // Log the threadId before passing to ChatKit
  console.log('[DEBUG] Initializing ChatKit with threadId:', threadId);

  // Initialize ChatKit with full configuration following official examples
  const chatkit = useChatKit({
    api: {
      url: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/chatkit`,
      domainKey: process.env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY || '',
      // Custom fetch function to inject auth headers
      // IMPORTANT: Must return Response directly for SSE stream handling
      fetch: async (input: RequestInfo | URL, init?: RequestInit) => {
        console.log('[DEBUG] ChatKit fetch called:', {
          url: input.toString(),
          method: init?.method || 'GET',
          hasAuth: !!authToken,
        });

        const response = await fetch(input, {
          ...init,
          headers: {
            ...init?.headers,
            'Authorization': `Bearer ${authToken}`,
            'Accept': 'text/event-stream',
          },
        });

        console.log('[DEBUG] ChatKit fetch response:', {
          status: response.status,
          statusText: response.statusText,
          contentType: response.headers.get('content-type'),
        });

        // Log response body for non-streaming responses
        if (!response.headers.get('content-type')?.includes('event-stream')) {
          const clonedResponse = response.clone();
          try {
            const text = await clonedResponse.text();
            console.log('[DEBUG] Response body:', text.substring(0, 500));
          } catch (e) {
            console.error('[DEBUG] Failed to read response:', e);
          }
        }

        return response;
      },
    },
    initialThread: threadId,
    history: {
      enabled: true,
      showDelete: true,
      showRename: true,
    },
    header: {
      enabled: true,
      title: {
        enabled: true,
        text: undefined,
      },
    },
    theme: {
      colorScheme: isDarkMode ? 'dark' : 'light',
      radius: 'soft',
      density: 'normal',
      typography: {
        baseSize: 16,
        fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      },
      color: {
        grayscale: {
          hue: 220,
          tint: 6,
          shade: -2,
        },
        accent: {
          primary: '#3b82f6',
          level: 2,
        },
        surface: {
          background: isDarkMode ? '#111827' : '#ffffff',
          foreground: isDarkMode ? '#f9fafb' : '#111827',
        },
      },
    },
    startScreen: {
      greeting: 'Welcome! I\'m here to help you manage your tasks efficiently. What would you like to do?',
      prompts: [
        {
          label: '📝 Create a new task',
          prompt: 'Add a new task: Buy groceries for dinner tonight',
          icon: 'plus',
        },
        {
          label: '📋 View all tasks',
          prompt: 'Show me all my pending tasks organized by priority',
          icon: 'book-open',
        },
        {
          label: '🎯 Today\'s priorities',
          prompt: 'What tasks should I focus on today?',
          icon: 'star',
        },
        {
          label: '✅ Complete a task',
          prompt: 'Mark my first task as complete',
          icon: 'check',
        },
      ],
    },
    composer: {
      placeholder: 'Type a message or describe what you need help with...',
      attachments: {
        enabled: false,
      },
    },
    threadItemActions: {
      feedback: true,
      retry: true,
    },
    disclaimer: {
      text: 'AI responses may occasionally be inaccurate. Please verify important information.',
      highContrast: false,
    },
    onResponseEnd: handleResponseEnd,
    onThreadChange: handleThreadChange,
    onError: handleError,
    onReady: handleReady,
  });

  // Handle new chat button click
  const handleNewChat = useCallback(() => {
    setThreadId(null);
    setStoredThreadId(null);
    // Refresh the page to start with a new conversation
    window.location.reload();
  }, []);

  // Check if control is valid
  const hasValidControl = chatkit && chatkit.control && typeof chatkit.control === 'object';

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <header className="border-b bg-gradient-to-r from-slate-50 to-blue-50 p-4 shadow-sm">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-xl">
              AI
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AI Task Assistant</h1>
              <p className="text-sm text-gray-600">
                Manage your tasks through natural conversation
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {/* New Chat Button */}
            <button
              onClick={handleNewChat}
              className="inline-flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
              title="Start a new conversation"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M12 5v14M5 12h14" />
              </svg>
              New Chat
            </button>

            {/* Dark Mode Toggle */}
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="rounded-md p-2 hover:bg-gray-100 transition-colors"
              title={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {isDarkMode ? '☀️' : '🌙'}
            </button>

            <span className="text-sm text-muted-foreground">
              {session.user?.email || session.user?.name || 'User'}
            </span>
            <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
              ChatKit v1.4.0
            </span>
          </div>
        </div>
      </header>

      {/* ChatKit Component - Full height container */}
      <div className="flex-1 overflow-hidden">
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
        setAuthToken((session as any).jwt);
        setTokenLoading(false);
      } else {
        // Fallback: fetch JWT from token endpoint
        setTokenLoading(true);
        fetch('/api/auth/token')
          .then(res => {
            if (!res.ok) {
              console.error('[ChatKit] Token fetch failed:', res.status, res.statusText);
              throw new Error(`Token fetch failed: ${res.status}`);
            }
            return res.json();
          })
          .then(data => {
            if (data.token) {
              setAuthToken(data.token);
              setTokenError(null);
            } else {
              console.error('[ChatKit] No token in response:', data);
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
