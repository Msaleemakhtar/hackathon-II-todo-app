# Specification: Frontend Setup with Openai Chatkit & Better_Auth Integration

## Feature Overview
Implement the frontend AI-powered chat interface with OpenAI ChatKit setup, and Better Auth integration for user authentication. This feature will provide users with a conversational interface to manage their todos using natural language.

## Requirements

### Functional Requirements
1. **OpenAI ChatKit Setup**
   -  Must follow the official documentaion of Openai ChatKit and Better-Auth using context7 mcp
   - Advanced integrations with ChatKit (https://platform.openai.com/docs/guides/custom-chatkit) into the Phase III frontend
   - Configure with the required domain key from OpenAI if necessary 
   - Set up according to the Managed ChatKit Starter template as a example (https://github.com/openai/openai-chatkit-advanced-samples) it contain both frontend and backend setup with fast api
   - Handle domain allowlist configuration requirements for production deployment if necssary because we using custom chatkit

2. **Chat Interface Components**
   - Create components that can render both user and AI messages
   - Include visual differentiation for user vs assistant messages
   - Show tool call information when AI invokes MCP tools
   - Implement loading states during AI processing
   - Include proper input validation and sanitization before sending messages
   - Provide UI feedback during message sending and processing

3. **API Client Implementation**
   - Create API client for communication with the backend chat endpoint
   - Implement proper request/response handling for the `/api/{user_id}/chat` endpoint
   - Include error handling for various types of API failures (network, server, validation)
   - Ensure integration with Better Auth for authentication token attachment strictly follow the official documentation:
      -   Better_Auth official documentation (https://www.better-auth.com/)
      -   Better_Auth Github Reference (https://github.com/better-auth/better-auth)
   - Handle the conversation_id flow (create new or continue existing)
   - Implement retry mechanisms for failed requests

4. **Better Auth Integration**
   - Integrate Better Auth for user authentication and session management
   - Ensure JWT tokens are attached to API requests automatically
   - Implement user login/logout functionality
   - Secure the chat interface to authenticated users only
   - Handle token refresh automatically when needed

5. **Conversation Display and Management**
   - Display conversation history with proper message ordering
   - Show message timestamps
   - Implement conversation switching capabilities
   - Handle conversation creation when starting new chats
   - Ensure messages are properly attributed to user or assistant roles
   - Support scrolling through long conversation histories

### Non-Functional Requirements
1. **Performance**: Interface should load within 3 seconds under normal conditions
2. **Usability**: Interface should be intuitive and responsive to user interactions
3. **Security**: User data should be protected using Better Auth JWT tokens
4. **Compatibility**: Should work across modern browsers and device sizes
5. **Accessibility**: Follow accessibility standards for keyboard navigation and screen readers
6. **Maintainability**: Code should follow established patterns and include proper documentation
7. **Reliability**: Should gracefully handle network issues and API errors

## User Stories

### User Story 1: Chat Interface Access
- **As a** logged-in user
- **I want** to access the chat interface
- **So that** I can interact with the AI to manage my tasks

**Acceptance Criteria**:
- When I visit the chat page, I'm prompted to log in if not authenticated
- When I'm logged in, I see the chat interface
- When I'm logged in, my user ID is correctly passed to API calls
- When I'm logged in, I can see my existing conversation history (if any)

### User Story 2: Send and Receive Messages
- **As a** user
- **I want** to send messages to the AI and receive responses
- **So that** I can manage my tasks through conversation

**Acceptance Criteria**:
- When I type a message and send it, the message appears in the chat interface
- When I send a message, I see a loading indicator while the AI processes
- When the AI responds, the response appears in the chat interface
- When the AI uses MCP tools, I can see which tools were invoked
- When an error occurs, I receive an appropriate error message
- When I send an empty or invalid message, I get proper validation feedback

### User Story 3: Conversation Continuation
- **As a** user
- **I want** to continue previous conversations
- **So that** the AI remembers our previous interactions

**Acceptance Criteria**:
- When I return to the chat interface, I see my previous conversation history
- When I send a message in a continued conversation, it maintains context
- When I start a new conversation, it's separate from previous ones
- When I have multiple conversations, I can switch between them

### User Story 4: Error Handling
- **As a** user
- **I want** to be informed when something goes wrong
- **So that** I understand why my request failed and how to fix it

**Acceptance Criteria**:
- When network connectivity is lost, I receive a user-friendly message
- When the backend API returns an error, I understand what went wrong
- When authentication fails, I'm prompted to log in again
- When the AI service is unavailable, I receive appropriate feedback

## Technical Design

### Architecture Components
1. **ChatInterface.tsx**: Main component that orchestrates the chat experience
2. **ChatMessage.tsx**: Component for rendering individual messages with proper styling
3. **API Client**: Module for handling communication with the backend
4. **Better Auth Integration**: Components and hooks for authentication management
5. **Conversation Context**: State management for current conversation
6. **Input Validation Service**: Component/service to validate user messages before sending
7. **Error Handling Service**: Component/service to handle and display different error types

### Frontend Technology Stack
- OpenAI ChatKit components and hooks
- Better Auth for authentication
- Bun as the package manager
- Tailwind CSS for styling (consistent with existing codebase)


### Environment Variables
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`: Domain key for OpenAI ChatKit authentication
- `NEXT_PUBLIC_API_BASE_URL`: Base URL for backend API calls

### API Integration

#### Request to Backend
```
POST /api/{user_id}/chat
Headers: Authorization: Bearer <jwt_token>
{
  "message": "Add a task to buy groceries",
  "conversation_id": 123 // optional
}
```

#### Response from Backend
```
{
  "conversation_id": 123,
  "response": "I've added the task 'Buy groceries' to your list.",
  "tool_calls": [
    {
      "name": "add_task",
      "arguments": {"user_id": "user123", "title": "Buy groceries"},
      "result": {"task_id": 123, "status": "created", "title": "Buy groceries"}
    }
  ]
}
```

### Chat Structure

- Displays message history
- Contains input field for user messages
- Manages loading states and error displays
- Handles conversation context and history
- Renders a single message in the conversation
- Distinguishes between user and AI messages
- Formats tool calls when present in AI responses
- Shows timestamps for messages
- Handles message content formatting
- Supports rich text display for AI responses with tool call information

## Implementation Details

### Domain Configuration for OpenAI ChatKit
- Configure domain in OpenAI's dashboard for production deployment
- Add frontend domain to OpenAI's domain allowlist if necessary
- Obtain domain key and configure in environment variables if necessary
- Note: localhost typically works without domain allowlist for development

### Input Validation
- Prevent empty or whitespace-only messages from being sent
- Implement character limits if needed
- Sanitize input to prevent potential security issues
- Provide user feedback for invalid inputs

### Error Handling Strategy
1. **Network Errors**: Display user-friendly message and retry option
2. **Authentication Errors**: Redirect to login or refresh token as needed
3. **API Validation Errors**: Show specific validation feedback
4. **Backend Service Errors**: Display appropriate error message to user
5. **AI Service Errors**: Provide feedback that AI is temporarily unavailable

## Implementation Constraints
1. Must use OpenAI ChatKit as specified in the constitution
2. Must follow the Managed ChatKit Starter template structure
3. Must integrate with Better Auth using JWT plugin
4. Must use `/api/{user_id}/chat` endpoint format
5. Must use Bun for package management
6. Must ensure Phase III frontend is completely separate from Phase II
7. Must properly configure domain allowlist for ChatKit production deployment if necessary
8. Must implement proper error boundaries to prevent app crashes

## Security Considerations
- JWT tokens must be securely managed by Better Auth
- API requests must include proper authentication headers
- User data must be protected and only accessible to authenticated users
- Proper error handling to prevent information leakage
- Input validation and sanitization to prevent injection attacks
- Secure transmission of data over HTTPS

## Testing Requirements
- Unit tests for individual components 
- Integration tests for API client functionality
- Authentication flow tests with Better Auth
- Error handling tests for various failure scenarios
- Accessibility tests to ensure compliance with standards
- Cross-browser compatibility testing
- Performance tests to verify load time requirements

## Dependencies and Tools
- OpenAI ChatKit
- Better Auth
- MSW for API mocking in tests

## Success Criteria
- [ ] OpenAI ChatKit is properly integrated and configured
- [ ] Component renders and functions correctly , displays messages with appropriate styling
- [ ] API client successfully communicates with the backend chat endpoint
- [ ] Better Auth integration works for user authentication
- [ ] User can send messages and receive AI responses
- [ ] Conversation history is properly displayed
- [ ] Tool call information is shown when AI uses MCP tools
- [ ] Loading states are implemented during AI processing
- [ ] Error handling works for API failures
- [ ] Interface is responsive and accessible
- [ ] Security measures prevent unauthorized access
- [ ] Performance meets the 3-second load time requirement
- [ ] Domain allowlist is properly configured for production if necessary
- [ ] Input validation prevents invalid messages from being sent
- [ ] All error states are handled gracefully with user feedback
- [ ] Unit and integration tests cover critical functionality
- [ ] Cross-browser compatibility is verified
- [ ] API client implements retry mechanisms for failed requests
