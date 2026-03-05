const express = require('express');
const service = require('../services/operation.service');

const router = express.Router();

router.get('/', (_req, res) => {
  res.json({
    module: 'operation',
    items: service.listOperationItems()
  });
});

router.post('/', (req, res) => {
  const item = service.createOperationItem(req.body || { module: 'operation' });
  res.status(201).json(item);
});

module.exports = router;
