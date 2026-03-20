const express = require('express');
const service = require('../services/experience.service');
const { validateBody } = require('../middleware/validate');

const router = express.Router();

router.get('/', (_req, res, next) => {
  try {
    res.json({
      module: 'experience',
      items: service.listExperienceItems(),
    });
  } catch (err) {
    next(err);
  }
});

router.post('/', validateBody(['module']), (req, res, next) => {
  try {
    const item = service.createExperienceItem(req.body);
    res.status(201).json(item);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
