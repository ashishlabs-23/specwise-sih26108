const apiDestination = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${apiDestination}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
