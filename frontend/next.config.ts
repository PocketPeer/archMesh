import type { NextConfig } from "next";

// Always provide a dev fallback for the backend API to prevent HTML 404 responses
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/v1/projects/:path*",
        destination: `${API_BASE}/projects/:path*`,
      },
      {
        source: "/api/v1/:path*",
        destination: `${API_BASE}/:path*`,
      },
    ];
  },
};

export default nextConfig;
