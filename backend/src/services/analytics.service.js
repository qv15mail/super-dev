const repository = require('../repositories/analytics.repository');

function listAnalyticsItems() {
  return repository.listAnalytics();
}

function createAnalyticsItem(payload) {
  return repository.createAnalytics(payload);
}

module.exports = { listAnalyticsItems, createAnalyticsItem };
