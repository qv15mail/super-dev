const express = require('express');

const coreRouter = require('./routes/core.route');
const experienceRouter = require('./routes/experience.route');
const operationRouter = require('./routes/operation.route');

const app = express();
app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api/core', coreRouter);
app.use('/api/experience', experienceRouter);
app.use('/api/operation', operationRouter);

const port = process.env.PORT || 3001;
app.listen(port, () => {
  console.log(`Backend scaffold is running on http://localhost:${port}`);
});
