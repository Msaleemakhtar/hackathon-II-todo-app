/**
 * Chat Page (T060-T062)
 * 
 * - Creates chat page at /chat (T060)
 * - Integrates Better Auth session management (T061)
 * - Calls sendChatMessage API with user_id from session (T062)
 */

import ChatInterface from "@/components/chat/ChatInterface";

export default function ChatPage() {
  return (
    <main>
      <ChatInterface />
    </main>
  );
}
