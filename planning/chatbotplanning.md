# Chatbot Planning Documentation

## Phase III: Todo AI Chatbot Architecture

Today's date is Tuesday, December 16, 2025.

This document contains comprehensive planning for the AI Chatbot implementation in Phase III of the Todo app hackathon.

## Table of Contents
1. [Phase III Overview](#phase-iii-overview)
2. [Architecture Components](#architecture-components)
3. [MCP Server and Tool Specifications](#mcp-server-and-tool-specifications)
4. [Implementation Approach](#implementation-approach)
5. [Authentication Flow](#authentication-flow)
6. [User Workflow Example](#user-workflow-example)

## Phase III Overview

Phase III focuses on creating an AI-powered chatbot interface for managing todos through natural language. Here are the key objectives and deliverables:

### Objectives:
1. Create an AI-powered chatbot interface for all Basic Level features (Add, Delete, Update, View, Mark Complete)
2. Use OpenAI Agents SDK for AI logic
3. Build an MCP (Model Context Protocol) server with Official MCP SDK that exposes task operations as tools
4. Implement a stateless chat endpoint that persists conversation state to database
5. Ensure AI agents use MCP tools to manage tasks, with tools being stateless and storing state in the database

### Technology Stack:
- Frontend: OpenAI ChatKit
- Backend: Python FastAPI
- AI Framework: OpenAI Agents SDK
- MCP Server: Official MCP SDK
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth

## Architecture Components

### System Architecture Overview:

```
┌─────────────────┐     ┌──────────────────────────────────────────────┐     ┌─────────────────┐
│                 │     │              FastAPI Server                   │     │                 │
│                 │     │  ┌────────────────────────────────────────┐  │     │    Neon DB      │
│  ChatKit UI     │────▶│  │         Chat Endpoint                  │  │     │  (PostgreSQL)   │
│  (Frontend)     │     │  │  POST /api/chat                        │  │     │                 │
│                 │     │  └───────────────┬────────────────────────┘  │     │  - tasks        │
│                 │     │                  │                           │     │  - conversations│
│                 │     │                  ▼                           │     │  - messages     │
│                 │     │  ┌────────────────────────────────────────┐  │     │                 │
│                 │     │  │      OpenAI Agents SDK                 │  │     │                 │
│                 │     │  │      (Agent + Runner)                  │  │     │                 │
│                 │     │  └───────────────┬────────────────────────┘  │     │                 │
│                 │     │                  │                           │     │                 │
│                 │     │                  ▼                           │     │                 │
│                 │     │  ┌────────────────────────────────────────┐  │────▶│                 │
│                 │     │  │         MCP Server                 │  │   │                 │
│                 │     │  │  (MCP Tools for Task Operations)       │  │◀────│                 │
│                 │     │  └────────────────────────────────────────┘  │     │                 │
└─────────────────┘     └──────────────────────────────────────────────┘     └─────────────────┘
```

### Key Components:

1. **ChatKit UI (Frontend):**
   - OpenAI's ChatKit provides the user interface for interacting with the AI
   - Handles user input and displays AI responses
   - Communicates with the backend via API endpoints

2. **FastAPI Server:**
   - Main application server handling HTTP requests
   - Stateless design - no conversation state stored in server memory
   - Handles authentication via JWT tokens from Better Auth
   - Orchestrates communication between UI and AI components

3. **OpenAI Agents SDK:**
   - Responsible for AI logic and reasoning
   - Uses natural language to understand user requests
   - Calls appropriate MCP tools based on user intent
   - Generates human-friendly responses

4. **MCP Server:**
   - Model Context Protocol server provides tools for the AI agent
   - Implements the specific task operations (add, list, complete, delete, update)
   - Stateless - relies on database for persistence
   - Standardized interface for AI to interact with application

5. **Database (Neon PostgreSQL):**
   - Stores all persistent data including tasks, conversations, and messages
   - Maintains conversation history for contextual responses
   - Supports Better Auth for user authentication
   - Three main models: Task, Conversation, and Message

## MCP Server and Tool Specifications

The Model Context Protocol (MCP) server is a critical component of Phase III that enables the AI agent to perform specific operations on the todo application. Here are the detailed specifications for the MCP tools:

### MCP Tools Overview:
The MCP server must expose five specific tools for the AI agent to use:

### 1. Tool: add_task
- **Purpose:** Create a new task
- **Parameters:**
  - `user_id` (string, required)
  - `title` (string, required)
  - `description` (string, optional)
- **Returns:** `task_id`, `status`, `title`
- **Example Input:** `{"user_id": "ziakhan", "title": "Buy groceries", "description": "Milk, eggs, bread"}`
- **Example Output:** `{"task_id": 5, "status": "created", "title": "Buy groceries"}`

### 2. Tool: list_tasks
- **Purpose:** Retrieve tasks from the list
- **Parameters:**
  - `user_id` (string, required)
  - `status` (string, optional: "all", "pending", "completed")
- **Returns:** Array of task objects
- **Example Input:** `{"user_id": "ziakhan", "status": "pending"}`
- **Example Output:** `[{"id": 1, "title": "Buy groceries", "completed": false}, ...]`

### 3. Tool: complete_task
- **Purpose:** Mark a task as complete
- **Parameters:**
  - `user_id` (string, required)
  - `task_id` (integer, required)
- **Returns:** `task_id`, `status`, `title`
- **Example Input:** `{"user_id": "ziakhan", "task_id": 3}`
- **Example Output:** `{"task_id": 3, "status": "completed", "title": "Call mom"}`

### 4. Tool: delete_task
- **Purpose:** Remove a task from the list
- **Parameters:**
  - `user_id` (string, required)
  - `task_id` (integer, required)
- **Returns:** `task_id`, `status`, `title`
- **Example Input:** `{"user_id": "ziakhan", "task_id": 2}`
- **Example Output:** `{"task_id": 2, "status": "deleted", "title": "Old task"}`

### 5. Tool: update_task
- **Purpose:** Modify task title or description
- **Parameters:**
  - `user_id` (string, required)
  - `task_id` (integer, required)
  - `title` (string, optional)
  - `description` (string, optional)
- **Returns:** `task_id`, `status`, `title`
- **Example Input:** `{"user_id": "ziakhan", "task_id": 1, "title": "Buy groceries and fruits"}`
- **Example Output:** `{"task_id": 1, "status": "updated", "title": "Buy groceries and fruits"}`

### Database Models:
- **Task:** `user_id`, `id`, `title`, `description`, `completed`, `created_at`, `updated_at`
- **Conversation:** `user_id`, `id`, `created_at`, `updated_at`
- **Message:** `user_id`, `id`, `conversation_id`, `role` (user/assistant), `content`, `created_at`

### Chat API Endpoint:
- **Endpoint:** `POST /api/{user_id}/chat`
- **Request Fields:**
  - `conversation_id` (integer, optional) - Existing conversation ID (creates new if not provided)
  - `message` (string, required) - User's natural language message
- **Response Fields:**
  - `conversation_id` (integer) - The conversation ID
  - `response` (string) - AI assistant's response
  - `tool_calls` (array) - List of MCP tools invoked

## Implementation Approach

For Phase III, the implementation will follow the Spec-Driven Development methodology using Claude Code and Spec-Kit Plus. Here's the recommended approach:

### 1. Specification Creation:
- Create comprehensive specification files in the `/specs` directory following Spec-Kit Plus conventions
- Structure the specs according to the recommended folder organization

### 2. Key Specification Files for Phase III:
- **`/specs/features/chatbot.md`** - Define the AI chatbot behavior, natural language commands, and expected responses
- **`/specs/api/mcp-tools.md`** - Detail the MCP tools specifications with parameters, return values, and examples
- **`/specs/database/schema.md`** - Specify the database models for tasks, conversations, and messages
- **`/specs/api/rest-endpoints.md`** - Document the chat API endpoint structure

### 3. Repository Structure:
- Organize the codebase in a monorepo structure with proper CLAUDE.md files

### 4. Claude Code Instructions:
- Include proper instructions in CLAUDE.md files for both backend and frontend

### 5. Implementation Workflow:
- Start with specifications, then implement based on specs
- Use Claude Code to implement features across frontend and backend

### 6. Key Implementation Steps:
1. Database Setup
2. MCP Server Implementation
3. Backend API
4. Frontend UI

## Authentication Flow

### Better Auth Flow from Frontend to MCP:

The authentication flow in this architecture works through JWT tokens that are passed from the frontend to the backend and then to the MCP tools. Here's how it works:

#### Frontend Authentication Flow:
1. **User Login:** User signs in using Better Auth on the frontend
2. **JWT Token Generation:** Better Auth generates a JWT token upon successful authentication
3. **Token Storage:** The JWT token is stored in the browser (usually in cookies or localStorage)
4. **API Requests:** When making requests to the FastAPI backend, the frontend includes the JWT token in the `Authorization: Bearer <token>` header

#### Backend Authentication Flow:
5. **Token Verification:** FastAPI receives the request with the JWT token and verifies it using the same secret key as Better Auth
6. **User Identification:** The backend decodes the token to extract user information (user ID, email, etc.)
7. **Token Forwarding:** When the backend calls MCP tools, it passes the user ID extracted from the JWT token as a parameter to each MCP tool

#### MCP Authentication:
8. **User Context:** Each MCP tool receives the `user_id` as part of its input parameters
9. **Database Operations:** MCP tools perform database operations scoped to the authenticated user's data only

### MCP Authentication with Better Auth:

The MCP server itself is stateless and doesn't maintain authentication state. Instead, each tool call includes the user ID, which is used to ensure data isolation:

- MCP tools receive user ID as a parameter from the backend
- Each tool verifies that operations are scoped to the authenticated user
- Database queries filter by user ID to prevent cross-user data access
- Error handling prevents unauthorized access

## User Workflow Example

Let's trace what happens when a user named "John Doe" asks the chatbot to add a task:

### Step 1: User Types Request in Chat UI
- John types in the ChatKit UI: "Add a task to buy groceries"
- He presses Enter or clicks the send button

### Step 2: Frontend Prepares API Request
- The frontend retrieves the JWT token from browser storage
- It prepares an API request to the FastAPI backend

### Step 3-15: Complete Request Processing Flow
- JWT verification at backend
- Conversation history retrieval
- User message storage in database
- OpenAI Agent processing
- MCP tool execution
- Database record creation
- Response generation and storage
- Response returned to frontend

### JWT Token Lifecycle:
1. **Creation:** Better Auth generates JWT upon successful authentication
2. **Storage:** JWT stored in HTTP-only cookie in the browser
3. **Transmission:** Browser automatically includes JWT in API requests
4. **Verification:** Backend verifies JWT using shared secret
5. **Usage:** User ID extracted and used to scope database operations
6. **Validation:** Token expiration and validity checked on each request
7. **Expiration:** JWT naturally expires after 7 days, requiring re-authentication

This comprehensive architecture ensures secure, authenticated communication while maintaining proper user data isolation throughout the entire system.