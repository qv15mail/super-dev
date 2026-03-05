const express = require('express');
const service = require('../services/experience.service');

const router = express.Router();

router.get('/', (_req, res) => {
  res.json({
    module: 'experience',
    items: service.listExperienceItems()
  });
});

router.post('/', (req, res) => {
  const item = service.createExperienceItem(req.body || { module: 'experience' });
  res.status(201).json(item);
});

module.exports = router;
