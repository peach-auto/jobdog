/** @type {import('next').NextConfig} */
const nextConfig = {
  // 静态导出: 构建产物是纯 HTML/CSS/JS，可直接部署到 Vercel / 任意静态托管
  output: "export",
  // 生成 /job/xxx/index.html 目录结构: 本地静态服务器与线上都能直接访问
  trailingSlash: true,
  images: { unoptimized: true },
};

export default nextConfig;
