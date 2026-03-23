/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：Next.js 构建配置
 * 作用：配置静态导出、图片优化等
 * 创建时间：2026-03-08
 * 最后修改：2026-03-23
 */

import fs from 'node:fs';
import path from 'node:path';

const isDev = process.env.NODE_ENV !== 'production';
const hasCustomDomainFile = fs.existsSync(path.join(process.cwd(), 'public', 'CNAME'));
const useCustomDomain = process.env.CUSTOM_DOMAIN === '1' || hasCustomDomainFile;
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
