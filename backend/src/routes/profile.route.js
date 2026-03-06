const express = require('express');
const service = require('../services/profile.service');

const router = express.Router();

router.get('/', (_req, res) => {
  res.json({
    module: 'profile',
    items: service.listProfileItems()
  });
});

router.post('/', (req, res) => {
  const item = service.createProfileItem(req.body || { module: 'profile' });
  res.status(201).json(item);
});

module.exports = router;
