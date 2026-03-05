const test = require('node:test');
const assert = require('node:assert/strict');
const service = require('../src/services/core.service');

test('core service scaffold', () => {
  const created = service.createCoreItem({ name: 'sample' });
  assert.equal(created.id > 0, true);
  const items = service.listCoreItems();
  assert.equal(Array.isArray(items), true);
});
