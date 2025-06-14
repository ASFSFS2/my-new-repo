import { withSentryConfig } from '@sentry/nextjs';
import type { NextConfig } from 'next';

let nextConfig: NextConfig = {
  webpack: (config) => {
    // This rule prevents issues with pdf.js and canvas
    config.externals = [...(config.externals || []), { canvas: 'canvas' }];

    // Ensure node native modules are ignored
    config.resolve.fallback = {
      ...config.resolve.fallback,
      canvas: false,
    };

    return config;
  },
  // Allow external hosts for development
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
        ],
      },
    ];
  },
};

if (process.env.NEXT_PUBLIC_VERCEL_ENV === 'production') {
  nextConfig = withSentryConfig(nextConfig, {
    org: 'kortix-ai',
    project: 'neo-nextjs',
    silent: !process.env.CI,
    widenClientFileUpload: true,
    tunnelRoute: '/monitoring',
    disableLogger: true,
    automaticVercelMonitors: true,
  });
}

export default nextConfig;
