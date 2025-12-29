import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs";

const nextConfig: NextConfig = {
  // Enable Turbopack for faster builds
  turbopack: {},
  // Configure image domains if needed
  images: {
    remotePatterns: [],
  },
  // Enable standalone output for Docker builds
  output: 'standalone',
};

export default withSentryConfig(nextConfig, {
  // Sentry options
  silent: false,
  org: "salim-vz",
  project: "todo-frontend",
  authToken: process.env.SENTRY_AUTH_TOKEN,
});
