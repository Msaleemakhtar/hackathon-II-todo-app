import type { NextConfig } from "next";

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

export default nextConfig;
