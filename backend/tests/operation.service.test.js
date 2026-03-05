const test = require('node:test');
const assert = require('node:assert/strict');
const service = require('../src/services/operation.service');

test('operation service scaffold', () => {
  const created = service.createOperationItem({ name: 'sample' });
  assert.equal(created.id > 0, true);
  const items = service.listOperationItems();
  assert.equal(Array.isArray(items), true);
});
