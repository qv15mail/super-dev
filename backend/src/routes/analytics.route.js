const express = require('express');
const service = require('../services/analytics.service');
const { validateBody } = require('../middleware/validate');

const router = express.Router();

router.get('/', (_req, res, next) => {
  try {
    res.json({
      module: 'analytics',
      items: service.listAnalyticsItems(),
    });
  } catch (err) {
    next(err);
  }
});

router.post('/', validateBody(['module']), (req, res, next) => {
  try {
    const item = service.createAnalyticsItem(req.body);
    res.status(201).json(item);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
