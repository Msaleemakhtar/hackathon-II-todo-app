### **Prompt for Specification: `001-foundational-backend`**

**Objective:**
Generate a complete feature specification (`spec.md`) for the "Foundational Backend Setup" of the Todo App. This specification will serve as the blueprint for creating the core database schema and the complete user authentication system. The specification must strictly adhere to the project constitution (`.specify/memory/constitution.md`).

**File to Create:**
`/specs/001-foundational-backend/spec.md`

**Required Specification Sections:**

1.  **Overview:**
    *   State that this specification covers the initial database schema for all Phase II entities and the complete user authentication and authorization API.

2.  **Database Schema Requirements:**
    *   Detail the full schema for the `User`, `Tag`, `Task`, and `TaskTagLink` entities.
    *   For each entity, create a markdown table specifying every `Field`, `Type`, and `Constraint` as defined in the "Data Model Specification" section of the constitution.
    *   Explicitly mention all relationships (e.g., User-Task, Task-Tag).
    *   List all required database indexes as specified in the constitution.
    *   Mandate that the implementation **MUST** use `SQLModel`.

3.  **API Endpoint Requirements: Authentication**
    *   Define the following RESTful endpoints. For each, specify the `Method`, `Path`, `Request Body`, `Success Response (Code and Body)`, and `Error Responses (Code and Body)`.

    *   **User Registration:**
        *   `POST /api/v1/auth/register`
        *   Request Body: `email`, `password`, `name` (optional).
        *   Success Response (`201 Created`): The created `User` object (excluding the hashed password).
        *   Error Response (`400 Bad Request`): If the email already exists or the password is too short.

    *   **User Login:**
        *   `POST /api/v1/auth/login`
        *   Request Body: `username` (email) and `password` (in a standard OAuth2PasswordRequestForm).
        *   Success Response (`200 OK`): An `access_token` and `token_type`. The `refresh_token` must be set in an `HttpOnly` cookie.
        *   Error Response (`401 Unauthorized`): If credentials are invalid.

    *   **Token Refresh:**
        *   `POST /api/v1/auth/refresh`
        *   Request: The endpoint should expect the `refresh_token` from its secure cookie.
        *   Success Response (`200 OK`): A new `access_token`.
        *   Error Response (`401 Unauthorized`): If the refresh token is invalid or expired.

    *   **Get Current User:**
        *   `GET /api/v1/auth/me`
        *   Request: Requires a valid `access_token`.
        *   Success Response (`200 OK`): The `User` object for the currently authenticated user.

    *   **User Logout:**
        *   `POST /api/v1/auth/logout`
        *   Action: The endpoint's primary responsibility is to clear the `refresh_token` cookie.
        *   Success Response (`200 OK`): A confirmation message.

4.  **Non-Functional & Security Requirements:**
    *   **Password Hashing:** Passwords **MUST** be hashed using `passlib[bcrypt]`. Plaintext passwords must never be stored.
    *   **JWT Specification:** The format, claims (`sub`, `exp`, `iat`, `type`), and expiration times (Access: 15 min, Refresh: 7 days) for both token types **MUST** match **Section IV** of the constitution.
    *   **Token Storage:** The specification must reiterate that `refresh_tokens` are handled via `HttpOnly` cookies.
    *   **Technology:** The implementation must use Python, FastAPI, and `python-jose` or `PyJWT` for token handling.

5.  **Acceptance Criteria:**
    *   A new, empty database can be fully initialized using the Alembic migration generated from the specified SQLModel entities.
    *   A user can successfully register, log in, and receive valid tokens.
    *   A user can access a protected endpoint (like `/auth/me`) with a valid access token.
    *   An attempt to access a protected endpoint with an expired or invalid token results in a `401 Unauthorized` error.
    *   A user can use a valid refresh token to get a new access token.
    *   All API responses and error formats match the definitions in the constitution.