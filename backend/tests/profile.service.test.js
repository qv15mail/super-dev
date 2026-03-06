const test = require('node:test');
const assert = require('node:assert/strict');
const service = require('../src/services/profile.service');

test('profile service scaffold', () => {
  const created = service.createProfileItem({ name: 'sample' });
  assert.equal(created.id > 0, true);
  const items = service.listProfileItems();
  assert.equal(Array.isArray(items), true);
});
