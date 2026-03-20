const test = require('node:test');
const assert = require('node:assert/strict');
const service = require('../src/services/content.service');

test('content service scaffold', () => {
  const created = service.createContentItem({ name: 'sample' });
  assert.equal(created.id > 0, true);
  const items = service.listContentItems();
  assert.equal(Array.isArray(items), true);
});
