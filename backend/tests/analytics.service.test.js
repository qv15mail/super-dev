const test = require('node:test');
const assert = require('node:assert/strict');
const service = require('../src/services/analytics.service');

test('analytics service scaffold', () => {
  const created = service.createAnalyticsItem({ name: 'sample' });
  assert.equal(created.id > 0, true);
  const items = service.listAnalyticsItems();
  assert.equal(Array.isArray(items), true);
});
