/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：Express 应用入口
 * 作用：配置中间件、路由和错误处理
 * 创建时间：2025-12-30
 * 最后修改：2026-03-20
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const analyticsRouter = require('./routes/analytics.route');
const coreRouter = require('./routes/core.route');
const contentRouter = require('./routes/content.route');
const experienceRouter = require('./routes/experience.route');
const operationRouter = require('./routes/operation.route');
const profileRouter = require('./routes/profile.route');
const workflowRouter = require('./routes/workflow.route');

const app = express();

// 安全头部
app.use(helmet());

// CORS 配置
const allowedOrigins = (process.env.CORS_ALLOWED_ORIGINS || 'http://localhost:5173,http://localhost:3000').split(',');
app.use(cors({
  origin: allowedOrigins.map(o => o.trim()).filter(Boolean),
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Request-ID'],
}));

// 请求体大小限制
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true, limit: '1mb' }));

// 速率限制
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 200,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: { code: 'RATE_LIMITED', message: '请求过于频繁，请稍后重试' } },
});
app.use('/api/', limiter);

// 健康检查（不受速率限制）
app.get('/health', (_req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

app.get('/ready', (_req, res) => {
  res.json({ status: 'ready' });
});

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api/analytics', analyticsRouter);
app.use('/api/core', coreRouter);
app.use('/api/content', contentRouter);
app.use('/api/experience', experienceRouter);
app.use('/api/operation', operationRouter);
app.use('/api/profile', profileRouter);
app.use('/api/workflow', workflowRouter);

// 404 处理
app.use((_req, res) => {
  res.status(404).json({
    error: { code: 'NOT_FOUND', message: '请求的资源不存在' },
  });
});

// 全局错误处理
app.use((err, _req, res, _next) => {
  const statusCode = err.statusCode || 500;
  const code = err.code || 'INTERNAL_ERROR';
  const message = statusCode === 500 ? '服务器内部错误' : err.message;

  if (statusCode >= 500) {
    console.error(`[ERROR] ${new Date().toISOString()} ${code}: ${err.message}`, err.stack);
  }

  res.status(statusCode).json({
    error: { code, message },
  });
});

const port = process.env.PORT || 3000;
if (require.main === module) {
  app.listen(port, () => {
    console.log(`Backend scaffold is running on http://localhost:${port}`);
  });
}

module.exports = app;
