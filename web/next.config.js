/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    const api = process.env.API_INTERNAL_URL || "http://localhost:20642";
    return [{ source: "/api/:path*", destination: `${api}/api/:path*` }];
  },
};

module.exports = nextConfig;
