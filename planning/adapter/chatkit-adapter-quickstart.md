# ChatKit Adapter Quick Start Guide

## Prerequisites

Before testing the ChatKit adapter, ensure:

1. ✅ Backend code has been implemented (all done!)
2. ⏳ Database migration needs to be run
3. ⏳ Backend server needs to be started
4. ⏳ Frontend ChatKit.js component needs to be configured

## Step-by-Step Setup

### Step 1: Prepare Environment

```bash
cd phaseIII/backend

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✅ Created .env file"
else
  echo "✅ .env file already exists"
fi

# Verify required environment variables
cat .env | grep -E "(DATABASE_URL|BETTER_AUTH_SECRET|OPENAI_API_KEY|GEMINI_API_KEY)"
```

### Step 2: Run Database Migration

```bash
cd phaseIII/backend

# Run the migration to add external_id field
alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade 001_initial_schema -> 002_add_external_id
```

**Troubleshooting Migration Issues:**

If you get "database_url field required" error:
```bash
# Make sure .env file exists and has DATABASE_URL
export DATABASE_URL="your-database-url-here"
alembic upgrade head
```

### Step 3: Start MCP Server

The MCP server must be running for the agent to work:

```bash
# Option 1: Using Docker
cd phaseIII
docker-compose up mcp-server

# Option 2: Running locally
cd phaseIII/backend
uvicorn app.mcp.standalone:app --port 8001
```

Verify MCP server is running:
```bash
curl http://localhost:8001/health
# Should return: {"status": "healthy"}
```

### Step 4: Start Backend Server

```bash
cd phaseIII/backend

# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

Verify backend is running with ChatKit adapter:
```bash
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "phaseiii-backend",
#   "version": "0.1.0",
#   "environment": "development",
#   "adapters": ["chatkit"]
# }
```

### Step 5: Test ChatKit Endpoint (Manual)

#### Test 1: Verify Authentication Required

```bash
curl -X POST http://localhost:8000/chatkit \
  -H "Content-Type: application/json" \
  -d '{
    "thread": {"id": "test_thread_123"},
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# Expected: 401 Unauthorized
# {"detail": "Missing Authorization header"}
```

#### Test 2: Test with Valid JWT

First, get a JWT token:
1. Start frontend and login via Better Auth
2. Open browser console
3. Run: `localStorage.getItem('auth-token')` (or check session)
4. Copy the JWT token

Then test:
```bash
# Replace YOUR_JWT_TOKEN with actual token
export JWT_TOKEN="your-jwt-token-here"

curl -N -X POST http://localhost:8000/chatkit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "thread": {"id": "test_thread_001"},
    "messages": [
      {"role": "user", "content": "Add task to test the ChatKit adapter"}
    ]
  }'

# Expected: SSE stream response
# event: thread.item.done
# data: {"item": {"id": "msg_...", "role": "assistant", "content": "I've added...", "created_at": "..."}}
```

#### Test 3: Test Conversation Continuity

```bash
# First message creates conversation
curl -N -X POST http://localhost:8000/chatkit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "thread": {"id": "test_thread_002"},
    "messages": [
      {"role": "user", "content": "Add task to buy milk"}
    ]
  }'

# Second message in same thread (should retrieve conversation)
curl -N -X POST http://localhost:8000/chatkit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "thread": {"id": "test_thread_002"},
    "messages": [
      {"role": "user", "content": "Add task to buy milk"},
      {"role": "assistant", "content": "I've added..."},
      {"role": "user", "content": "List my tasks"}
    ]
  }'
```

### Step 6: Frontend Integration

Update your ChatKit.js component:

```typescript
// phaseIII/frontend/app/chat/page.tsx
'use client';

import { ChatKit } from '@openai/chatkit-js';
import { useSession } from '@/lib/auth'; // Or your auth hook

export default function ChatPage() {
  const { session } = useSession();

  if (!session) {
    return <div>Please login to use chat</div>;
  }

  return (
    <div className="h-screen p-4">
      <ChatKit
        baseURL="http://localhost:8000"
        auth={{
          type: "custom",
          getAuthToken: async () => {
            // Return JWT token from your session
            return session.token;
          }
        }}
        onError={(error) => {
          console.error("ChatKit error:", error);
          // Show user-friendly error message
          alert(`Chat error: ${error.message}`);
        }}
        onMessage={(message) => {
          console.log("Message received:", message);
        }}
      />
    </div>
  );
}
```

### Step 7: End-to-End Testing

1. **Start all services:**
   ```bash
   # Terminal 1: MCP Server
   cd phaseIII/backend
   uvicorn app.mcp.standalone:app --port 8001

   # Terminal 2: Backend
   cd phaseIII/backend
   uvicorn app.main:app --reload --port 8000

   # Terminal 3: Frontend
   cd phaseIII/frontend
   npm run dev
   ```

2. **Test in browser:**
   - Navigate to http://localhost:3000
   - Login via Better Auth
   - Navigate to chat page
   - Send message: "Add task to buy milk"
   - Verify assistant responds
   - Check tasks page to confirm task was created

3. **Verify in database:**
   ```sql
   -- Check conversations table has external_id
   SELECT * FROM conversations WHERE external_id IS NOT NULL;

   -- Check tasks were created
   SELECT * FROM tasks_phaseiii ORDER BY created_at DESC LIMIT 5;

   -- Check messages were stored
   SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;
   ```

## Common Issues & Solutions

### Issue: "Field required" error for database_url

**Solution:**
```bash
cd phaseIII/backend
# Ensure .env file exists and has DATABASE_URL
cat .env | grep DATABASE_URL
```

### Issue: ChatKit.js shows "Connecting..." but never responds

**Possible causes:**
1. CORS not configured correctly
2. SSE stream not being sent properly
3. Backend error not being caught

**Solution:**
- Check browser console for CORS errors
- Check browser Network tab for /chatkit request
- Check backend logs for errors
- Verify SSE format has double newlines: `\n\n`

### Issue: Tasks not being created

**Possible causes:**
1. MCP server not running
2. Agent can't connect to MCP server
3. user_id not being passed correctly

**Solution:**
```bash
# Verify MCP server is running
curl http://localhost:8001/health

# Check backend logs for MCP connection errors
# Logs should show: "Connected to MCP server with 5 tools"

# Verify user_id in JWT token
# Decode JWT at https://jwt.io and check "sub" claim
```

### Issue: Conversation history not loading

**Possible causes:**
1. Migration not run
2. external_id not being stored
3. Thread ID mismatch

**Solution:**
```bash
# Verify migration was run
cd phaseIII/backend
alembic current
# Should show: 002_add_external_id (head)

# Check database
psql $DATABASE_URL -c "SELECT * FROM conversations WHERE external_id IS NOT NULL;"
```

## Verification Checklist

Before deploying or demoing:

- [ ] Migration run successfully (`alembic current` shows 002_add_external_id)
- [ ] MCP server running and healthy (curl http://localhost:8001/health)
- [ ] Backend running and shows chatkit adapter (curl http://localhost:8000/health)
- [ ] Manual curl test with JWT succeeds
- [ ] Frontend ChatKit.js component configured with correct baseURL
- [ ] Can send message and get response
- [ ] Tasks are created in database
- [ ] Conversation continuity works (second message in same thread)
- [ ] CORS allows frontend origin
- [ ] Browser console shows no errors

## Performance Tips

1. **Use connection pooling**: Already configured in database settings
2. **Monitor SSE connections**: Use browser DevTools Network tab
3. **Check MCP server latency**: Add logging for MCP call duration
4. **Optimize token validation**: JWT validation is already cached

## Next Steps After Testing

Once the adapter is working:

1. **Add proper error handling**: User-friendly error messages
2. **Implement loading states**: Show "AI is thinking..." indicator
3. **Add conversation list**: Show previous conversations
4. **Implement rate limiting**: Protect against abuse
5. **Add metrics**: Track usage and performance
6. **Consider migration**: Evaluate official ChatKit Python SDK

## Support

If you encounter issues not covered here:

1. Check `planning/adapter-approach-detailed.md` for architecture details
2. Check `planning/chatkit-adapter-implementation-summary.md` for implementation details
3. Review backend logs: `tail -f logs/backend.log`
4. Check browser console for frontend errors
5. Review ChatKit.js documentation: https://openai.github.io/chatkit-js/

## Success! 🎉

If you can:
- ✅ Send a chat message
- ✅ Get AI response
- ✅ See task created in database
- ✅ Continue conversation in same thread

Then your ChatKit adapter is working correctly!
