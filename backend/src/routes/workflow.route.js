const express = require('express');
const service = require('../services/workflow.service');

const router = express.Router();

router.get('/', (_req, res) => {
  res.json({
    module: 'workflow',
    items: service.listWorkflowItems()
  });
});

router.post('/', (req, res) => {
  const item = service.createWorkflowItem(req.body || { module: 'workflow' });
  res.status(201).json(item);
});

module.exports = router;
