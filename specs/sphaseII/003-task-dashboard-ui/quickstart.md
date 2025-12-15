# Quickstart: Task Management Dashboard UI

This document provides instructions on how to set up and run the Task Management Dashboard frontend for development.

## Prerequisites

1.  **Node.js and `bun`**: Ensure you have Node.js (v18+) and `bun` installed.
2.  **Backend Server**: The backend server from the `001-foundational-backend-setup` and `002-task-tag-api` features must be running and accessible. By default, it is expected to be at `http://localhost:8000`.
3.  **Environment Variables**: A `.env` file is needed in the `frontend` directory.

## Setup

1.  **Navigate to the frontend directory**:
    ```bash
    cd /home/salim/Desktop/Hackathon-II/frontend
    ```

2.  **Install dependencies**:
    ```bash
    bun install
    ```

3.  **Create Environment File**:
    Create a `.env` file in the `/home/salim/Desktop/Hackathon-II/frontend` directory and add the following variable:
    ```env
    NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
    ```
    This URL should point to your running backend API.

## Running the Application

1.  **Start the development server**:
    ```bash
    bun run dev
    ```

2.  **Access the application**:
    Open your web browser and navigate to `http://localhost:3000`. The Task Management Dashboard should be visible, and you should be able to log in (assuming the backend is running) and interact with your tasks.

## Running Tests

To run the frontend tests, execute the following command from the `/home/salim/Desktop/Hackathon-II/frontend` directory:

```bash
bun test
```
