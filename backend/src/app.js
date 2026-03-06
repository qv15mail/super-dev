const express = require('express');

const coreRouter = require('./routes/core.route');
const profileRouter = require('./routes/profile.route');
const workflowRouter = require('./routes/workflow.route');
const analyticsRouter = require('./routes/analytics.route');

const app = express();
app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api/core', coreRouter);
app.use('/api/profile', profileRouter);
app.use('/api/workflow', workflowRouter);
app.use('/api/analytics', analyticsRouter);

const port = process.env.PORT || 3001;
app.listen(port, () => {
  console.log(`Backend scaffold is running on http://localhost:${port}`);
});
