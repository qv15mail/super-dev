const express = require('express');

const app = express();
app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

app.get('/api/core', (req, res) => {
  res.json({
    module: 'core',
    status: 'todo',
    message: 'Module scaffold created by Super Dev'
  });
});

app.get('/api/auth', (req, res) => {
  res.json({
    module: 'auth',
    status: 'todo',
    message: 'Module scaffold created by Super Dev'
  });
});

app.get('/api/workflow', (req, res) => {
  res.json({
    module: 'workflow',
    status: 'todo',
    message: 'Module scaffold created by Super Dev'
  });
});

const port = process.env.PORT || 3001;
app.listen(port, () => {
  console.log(`Backend scaffold is running on http://localhost:${port}`);
});
