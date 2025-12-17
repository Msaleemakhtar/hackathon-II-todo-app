"use client";

import { useState, useEffect, useRef } from "react";
import { sendChatMessage, type ChatResponse, type ApiError } from "@/lib/api/chat";
import { useSession } from "@/lib/auth";
import ErrorMessage from "./ErrorMessage";

interface Message {
  role: "user" | "assistant";
  content: string;
  toolCalls?: Array<{
    name: string;
    arguments: Record<string, any>;
    result: any;
  }>;
}

/**
 * ChatInterface Component (T055-T059)
 * 
 * Features:
 * - Message input field with send functionality (T056)
 * - Message display for user and assistant (T057)
 * - Loading state during AI processing (T058)
 * - Tool call visualization (T059)
 */
// T098: Conversation starter suggestions
const CONVERSATION_STARTERS = [
  "Show my tasks",
  "Add task: Buy groceries",
  "What tasks do I have pending?",
  "Complete task #1",
];

export default function ChatInterface() {
  const { data: session } = useSession();
  const user = session?.user;
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | undefined>();
  // T099: Enhanced error state with details
  const [error, setError] = useState<{
    detail: string;
    code?: string;
    suggestions?: string[];
  } | null>(null);
  const [conversationMetadata, setConversationMetadata] = useState<{
    created_at?: string;
    updated_at?: string;
    message_count: number;
  }>({ message_count: 0 });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [lastMessage, setLastMessage] = useState<string>("");  // For retry

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load conversation ID from URL and fetch history if present (T080)
  useEffect(() => {
    const loadConversationHistory = async () => {
      const params = new URLSearchParams(window.location.search);
      const convId = params.get("conversation_id");

      if (convId && user?.id) {
        const conversationIdNum = parseInt(convId, 10);
        setConversationId(conversationIdNum);

        try {
          // Import dynamically to avoid issues
          const { getConversationHistory } = await import("@/lib/api/chat");
          const history = await getConversationHistory(conversationIdNum);

          // Load messages into UI
          const loadedMessages: Message[] = history.messages.map((msg) => ({
            role: msg.role,
            content: msg.content,
            toolCalls: undefined, // Tool calls not stored in history
          }));

          setMessages(loadedMessages);

          // Update conversation metadata (T084-T086)
          setConversationMetadata({
            created_at: history.created_at,
            updated_at: history.updated_at,
            message_count: history.messages.length,
          });
        } catch (err) {
          console.error("Failed to load conversation history:", err);
          setError("Failed to load conversation history");
        }
      }
    };

    loadConversationHistory();
  }, [user]);

  const handleSendMessage = async (messageOverride?: string) => {
    const messageToSend = messageOverride || inputMessage.trim();

    if (!messageToSend || !user?.id) {
      return;
    }

    setInputMessage("");
    setError(null);
    setLastMessage(messageToSend);  // Store for retry

    // Add user message to UI immediately
    setMessages((prev) => [...prev, { role: "user", content: messageToSend }]);

    // Set loading state (T058)
    setIsLoading(true);

    try {
      // Call chat API (T062)
      const response: ChatResponse = await sendChatMessage(messageToSend, conversationId);

      // Store conversation ID for subsequent messages (T062)
      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
        // Update URL with conversation ID
        const url = new URL(window.location.href);
        url.searchParams.set("conversation_id", response.conversation_id.toString());
        window.history.pushState({}, "", url);
      }

      // Add assistant response to UI (T057)
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.response,
          toolCalls: response.tool_calls,
        },
      ]);

      // Update message count metadata (T086)
      setConversationMetadata((prev) => ({
        ...prev,
        message_count: prev.message_count + 2, // User message + assistant response
        updated_at: new Date().toISOString(),
      }));
    } catch (err) {
      const apiError = err as ApiError;
      console.error("Chat error:", err);

      // T103-T105: Enhanced error handling with detailed messages
      let errorDetails: { detail: string; code?: string; suggestions?: string[] };

      if (apiError.detail && typeof apiError.detail === "object") {
        // Backend returned structured error
        errorDetails = {
          detail: apiError.detail.detail || apiError.message || "An error occurred",
          code: apiError.detail.code,
          suggestions: apiError.detail.suggestions || [],
        };
      } else {
        // Simple error message
        errorDetails = {
          detail: apiError.message || "Failed to send message",
          code: undefined,
          suggestions: ["Please try again", "Check your connection"],
        };
      }

      // T103: Handle 403 Forbidden (unauthorized access)
      if (apiError.status === 403) {
        errorDetails = {
          detail: "You don't have permission to access this resource. Please sign in with a valid account.",
          code: "FORBIDDEN",
          suggestions: [
            "Sign out and sign in again",
            "Check that you're using the correct account",
            "Contact support if the problem persists",
          ],
        };
      }

      // T104: Handle 401 Unauthorized (session expired)
      if (apiError.status === 401) {
        errorDetails = {
          detail: "Your session has expired. Please sign in again to continue.",
          code: "UNAUTHORIZED",
          suggestions: [
            "Click 'Sign In' to re-authenticate",
            "You'll be redirected to the login page",
          ],
        };
      }

      // T105: Handle conversation access denial
      if (apiError.detail?.code === "CONVERSATION_ACCESS_DENIED") {
        errorDetails = {
          detail: "You don't have access to this conversation. It may belong to another user.",
          code: "CONVERSATION_ACCESS_DENIED",
          suggestions: [
            "Start a new conversation",
            "Check that you're viewing your own conversations",
          ],
        };
      }

      setError(errorDetails);

      // Remove the failed user message from UI
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  // T099: Retry handler
  const handleRetry = () => {
    if (lastMessage) {
      handleSendMessage(lastMessage);
    }
  };

  // T098: Starter message handler
  const handleStarterClick = (starter: string) => {
    setInputMessage(starter);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!user) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        <p>Please sign in to use the chat.</p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", maxWidth: "800px", margin: "0 auto" }}>
      {/* Header with Conversation Metadata (T084-T086) */}
      <div style={{ padding: "1rem", borderBottom: "1px solid #ccc", backgroundColor: "#f5f5f5" }}>
        <h2>AI Task Manager Chat</h2>
        <p style={{ fontSize: "0.875rem", color: "#666" }}>
          Signed in as: {user.email || user.id}
        </p>
        {conversationId && conversationMetadata.message_count > 0 && (
          <div style={{ fontSize: "0.75rem", color: "#999", marginTop: "0.5rem" }}>
            <span>Conversation #{conversationId}</span>
            {" • "}
            <span>{conversationMetadata.message_count} messages</span>
            {conversationMetadata.created_at && (
              <>
                {" • "}
                <span>Started: {new Date(conversationMetadata.created_at).toLocaleDateString()}</span>
              </>
            )}
            {conversationMetadata.updated_at && (
              <>
                {" • "}
                <span>Updated: {new Date(conversationMetadata.updated_at).toLocaleTimeString()}</span>
              </>
            )}
          </div>
        )}
      </div>

      {/* Messages Display (T057) */}
      <div style={{ flex: 1, overflowY: "auto", padding: "1rem" }}>
        {/* T098: Conversation starters */}
        {messages.length === 0 && !isLoading && (
          <div style={{ textAlign: "center", color: "#999", padding: "2rem" }}>
            <p style={{ fontSize: "1.125rem", marginBottom: "1rem" }}>
              👋 Welcome! I'm your AI task manager assistant.
            </p>
            <p style={{ fontSize: "0.875rem", marginBottom: "1.5rem" }}>
              Start by trying one of these:
            </p>
            {/* T098: Clickable starter suggestions */}
            <div style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "0.5rem",
              justifyContent: "center",
              maxWidth: "600px",
              margin: "0 auto",
            }}>
              {CONVERSATION_STARTERS.map((starter, index) => (
                <button
                  key={index}
                  onClick={() => handleStarterClick(starter)}
                  style={{
                    padding: "0.5rem 1rem",
                    backgroundColor: "#e3f2fd",
                    color: "#1976d2",
                    border: "1px solid #90caf9",
                    borderRadius: "20px",
                    fontSize: "0.875rem",
                    cursor: "pointer",
                    transition: "all 0.2s",
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.backgroundColor = "#bbdefb";
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.backgroundColor = "#e3f2fd";
                  }}
                >
                  {starter}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              marginBottom: "1rem",
              padding: "0.75rem 1rem",
              borderRadius: "8px",
              backgroundColor: msg.role === "user" ? "#e3f2fd" : "#f5f5f5",
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            <div style={{ fontWeight: "bold", marginBottom: "0.25rem", fontSize: "0.875rem" }}>
              {msg.role === "user" ? "You" : "AI Assistant"}
            </div>
            <div>{msg.content}</div>

            {/* Tool Calls Display (T059) */}
            {msg.toolCalls && msg.toolCalls.length > 0 && (
              <div style={{ marginTop: "0.5rem", fontSize: "0.75rem", color: "#666" }}>
                <details>
                  <summary style={{ cursor: "pointer" }}>
                    🔧 Tools used: {msg.toolCalls.map((t) => t.name).join(", ")}
                  </summary>
                  <div style={{ marginTop: "0.5rem", padding: "0.5rem", backgroundColor: "#fff", borderRadius: "4px" }}>
                    {msg.toolCalls.map((tool, i) => (
                      <div key={i} style={{ marginBottom: "0.5rem" }}>
                        <strong>{tool.name}</strong>: {JSON.stringify(tool.result)}
                      </div>
                    ))}
                  </div>
                </details>
              </div>
            )}
          </div>
        ))}

        {/* T102: Enhanced typing indicator during AI processing */}
        {isLoading && (
          <div style={{
            padding: "0.75rem 1rem",
            backgroundColor: "#f5f5f5",
            borderRadius: "8px",
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
          }}>
            <div>
              <div style={{ fontWeight: "bold", marginBottom: "0.25rem", fontSize: "0.875rem" }}>
                AI Assistant
              </div>
              <div style={{ color: "#666", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span>Thinking</span>
                <div style={{ display: "flex", gap: "2px" }}>
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      style={{
                        width: "6px",
                        height: "6px",
                        borderRadius: "50%",
                        backgroundColor: "#666",
                        animation: "pulse 1.4s infinite",
                        animationDelay: `${i * 0.2}s`,
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* T099, T101: Enhanced error display with retry and suggestions */}
        {error && (
          <ErrorMessage
            error={error}
            onRetry={handleRetry}
            onDismiss={() => setError(null)}
          />
        )}

        <style jsx>{`
          @keyframes pulse {
            0%, 100% { opacity: 0.3; transform: scale(0.8); }
            50% { opacity: 1; transform: scale(1); }
          }
        `}</style>

        <div ref={messagesEndRef} />
      </div>

      {/* Message Input (T056) */}
      <div style={{ padding: "1rem", borderTop: "1px solid #ccc", backgroundColor: "#f5f5f5" }}>
        {/* T100: Inline help tooltips */}
        <div style={{
          fontSize: "0.75rem",
          color: "#666",
          marginBottom: "0.5rem",
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
        }}>
          <span title="Type naturally - I understand conversational language">
            💡 Tips:
          </span>
          <span title='Try: "Show my tasks"'>📋 List</span>
          <span>•</span>
          <span title='Try: "Add task: Buy milk"'>➕ Add</span>
          <span>•</span>
          <span title='Try: "Complete task #1"'>✓ Complete</span>
          <span>•</span>
          <span title='Try: "Delete task #2"'>🗑️ Delete</span>
          <span>•</span>
          <span title="Press Enter to send, Shift+Enter for new line">⌨️ Enter to send</span>
        </div>

        <div style={{ display: "flex", gap: "0.5rem" }}>
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (e.g., 'Show my tasks')"
            disabled={isLoading}
            title="Type naturally - I understand conversational language"
            style={{
              flex: 1,
              padding: "0.75rem",
              borderRadius: "4px",
              border: "1px solid #ccc",
              fontSize: "1rem",
            }}
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={isLoading || !inputMessage.trim()}
            title={isLoading ? "Sending message..." : "Send message (or press Enter)"}
            style={{
              padding: "0.75rem 1.5rem",
              borderRadius: "4px",
              border: "none",
              backgroundColor: isLoading || !inputMessage.trim() ? "#ccc" : "#2196f3",
              color: "#fff",
              fontSize: "1rem",
              cursor: isLoading || !inputMessage.trim() ? "not-allowed" : "pointer",
            }}
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
