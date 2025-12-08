# Stage 1: Build Stage
FROM oven/bun:1.0 as builder

WORKDIR /app

# Copy dependency definition files
COPY package.json bun.lockb ./

# Install dependencies with bun
RUN bun install --frozen-lockfile

# Copy the rest of the application source code
COPY . .

# Build the Next.js application for production
RUN bun run build

# ---
# Stage 2: Production Stage
FROM oven/bun:1.0-slim as production

WORKDIR /app

# Copy built assets from the builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json .
COPY --from=builder /app/bun.lockb .

# Install ONLY production dependencies
RUN bun install --frozen-lockfile --production

# Expose the port the app will run on
EXPOSE 3000

# Command to start the production server
CMD ["bun", "start"]
