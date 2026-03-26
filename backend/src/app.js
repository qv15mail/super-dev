/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：Express 应用入口
 * 作用：注册路由、中间件并启动 HTTP 服务
 * 创建时间：2026-03-24
 * 最后修改：2026-03-24
 */

const express = require('express');

const app = express();
const PORT = process.env.PORT || 3001;

// 中间件
app.use(express.json());

// CORS（开发环境跨域支持）
app.use((_req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
  if (_req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

// 路由注册
app.use('/api/content', require('./routes/content.route'));
app.use('/api/profile', require('./routes/profile.route'));
app.use('/api/analytics', require('./routes/analytics.route'));
app.use('/api/workflow', require('./routes/workflow.route'));
app.use('/api/core', require('./routes/core.route'));
app.use('/api/experience', require('./routes/experience.route'));
app.use('/api/operation', require('./routes/operation.route'));

// 健康检查
app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

// 全局错误处理
app.use((err, _req, res, _next) => {
  const status = err.status || 500;
  res.status(status).json({
    error: {
      code: err.code || 'INTERNAL_ERROR',
      message: err.message || 'Internal Server Error',
    },
  });
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
}

module.exports = app;
