import type { NextConfig } from "next";

const backendOrigin =
  process.env.NEXT_INTERNAL_API_BASE_URL ||
  (process.env.NODE_ENV === "development" ? "http://localhost:8000" : "http://backend:8000");

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [],
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendOrigin}/api/:path*`,
      },
      {
        source: "/uploads/:path*",
        destination: `${backendOrigin}/uploads/:path*`,
      },
    ];
  },
};

export default nextConfig;
