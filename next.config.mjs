/** @type {import('next').NextConfig} */
const apiBase = process.env.CORRELATION_API_URL || "http://localhost:5050";

const nextConfig = {
  async redirects() {
    return [
      {
        source: "/correlation-trading",
        destination: "https://correlation-trading.onrender.com",
        permanent: false,
      },
    ];
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiBase}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
