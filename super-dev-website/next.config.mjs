/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：Next.js 构建配置
 * 作用：配置静态导出、图片优化等
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */


const isDev = process.env.NODE_ENV !== 'production';
const useCustomDomain = process.env.CUSTOM_DOMAIN === '1';
const repoName = 'super-dev';
const basePath = isDev || useCustomDomain ? '' : `/${repoName}`;

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  basePath,
  assetPrefix: isDev || useCustomDomain ? undefined : `${basePath}/`,
  images: {
    unoptimized: true,
    formats: ['image/avif', 'image/webp'],
  },
};

export default nextConfig;
