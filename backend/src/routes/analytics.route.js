const express = require('express');
const service = require('../services/analytics.service');

const router = express.Router();

router.get('/', (_req, res) => {
  res.json({
    module: 'analytics',
    items: service.listAnalyticsItems()
  });
});

router.post('/', (req, res) => {
  const item = service.createAnalyticsItem(req.body || { module: 'analytics' });
  res.status(201).json(item);
});

module.exports = router;
