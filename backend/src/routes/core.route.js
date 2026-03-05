const express = require('express');
const service = require('../services/core.service');

const router = express.Router();

router.get('/', (_req, res) => {
  res.json({
    module: 'core',
    items: service.listCoreItems()
  });
});

router.post('/', (req, res) => {
  const item = service.createCoreItem(req.body || { module: 'core' });
  res.status(201).json(item);
});

module.exports = router;
