# Stage 1: Build stage to install dependencies
FROM python:3.11-slim as builder

# Install uv, the package manager
RUN pip install uv

WORKDIR /app

# Copy only the dependency files to leverage Docker cache
COPY pyproject.toml ./

# Install dependencies using uv
# We create a virtual environment within the builder stage
RUN uv venv && . .venv/bin/activate && uv pip install --system

# ---
# Stage 2: Final production stage
FROM python:3.11-slim as final

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv ./.venv
# Copy the application source code
COPY . .

# Activate the virtual environment for the final command
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port the app runs on
EXPOSE 8000

# The command to run the application will be provided by docker-compose
# For production, a command like:
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# would be used. The compose file overrides this with --reload for development.
