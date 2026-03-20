const express = require('express');
const service = require('../services/workflow.service');
const { validateBody } = require('../middleware/validate');

const router = express.Router();

router.get('/', (_req, res, next) => {
  try {
    res.json({
      module: 'workflow',
      items: service.listWorkflowItems(),
    });
  } catch (err) {
    next(err);
  }
});

router.post('/', validateBody(['module']), (req, res, next) => {
  try {
    const item = service.createWorkflowItem(req.body);
    res.status(201).json(item);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
