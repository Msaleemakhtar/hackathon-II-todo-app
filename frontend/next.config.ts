import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable Turbopack for faster builds
  turbopack: {},
  // Configure image domains if needed
  images: {
    remotePatterns: [],
  },
};

export default nextConfig;
