/** @type {import('next').NextConfig} */
const nextConfig = {
  rewrites: async () => {
    const apiBase = process.env.NODE_ENV === "development"
      ? "http://127.0.0.1:8000"
      : process.env.NEXT_PUBLIC_API_BASE;

    return [
      {
        source: "/api/:path*",
        destination: `${apiBase}/api/:path*`,
      },
      {
        source: "/docs",
        destination: `${apiBase}/docs`,
      },
      {
        source: "/openapi.json",
        destination: `${apiBase}/openapi.json`,
      },
    ];
  },
};

module.exports = nextConfig;
